import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Router,
    VLAN,
    Interface,
    ConfigLog,
    ConfigAction,
    ConfigStatus,
    RouterStatus,
    PortMode,
    BGPConfig,
    OSPFConfig,
)
from app.models.db_session import get_db
from app.services.config_builder import ConfigBuilder
from app.services.netconf_client import NETCONFClient
from app.routers.routers import ping_host


router = APIRouter(prefix="/api", tags=["Lab Deploy"])


class LabDeployRequest(BaseModel):
    lab_xml: str = Field(..., min_length=1, description="Fichier XML déclaratif du lab")
    dry_run: bool = Field(default=False, description="Valider sans appliquer sur les équipements")
    ping_targets: Optional[List[str]] = Field(
        default=None,
        description="IP(s) à ping après déploiement (optionnel)",
    )


class PingResult(BaseModel):
    ip_address: str
    success: bool
    reachable: bool = True
    packet_loss: str | None = None
    rtt: str | None = None
    error: Optional[str] = None


class RouterDeployResult(BaseModel):
    router_name: str
    router_id: int
    success: bool
    applied: int
    log_id: int | None = None
    error: Optional[str] = None


class LabDeployResponse(BaseModel):
    success: bool
    message: str
    routers: List[RouterDeployResult]
    pings: Optional[List[PingResult]] = None


def _bool_from_text(v: Optional[str], default: bool = False) -> bool:
    if v is None:
        return default
    s = v.strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _first_attr(el: ET.Element, names: List[str]) -> Optional[str]:
    for n in names:
        v = el.get(n)
        if v is not None:
            return v
    return None


def _first_child_text(el: ET.Element, names: List[str]) -> Optional[str]:
    for n in names:
        child = el.find(n)
        if child is not None and child.text:
            return child.text.strip()
    return None


@dataclass
class VlanPlan:
    vlan_id: int
    name: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None


@dataclass
class InterfacePlan:
    name: str
    enabled: bool = True
    description: Optional[str] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    vlan_id: Optional[int] = None  # vlan_id "métier" (pas l'id DB)
    port_mode: str = "access"
    is_svi: bool = False


@dataclass
class RouterPlan:
    name: str
    vlans: List[VlanPlan]
    interfaces: List[InterfacePlan]
    inter_vlan: bool
    bgp_configs: List["BGPPlan"]
    ospf_configs: List["OSPFPlan"]


@dataclass
class BGPNeighborPlan:
    neighbor_ip: str
    remote_as: int
    description: Optional[str] = None
    enabled: bool = True


@dataclass
class BGPPlan:
    local_as: int
    router_id_address: Optional[str] = None
    neighbors: List[BGPNeighborPlan] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.neighbors is None:
            self.neighbors = []


@dataclass
class OSPFProcessPlan:
    process_id: int
    router_id_address: Optional[str] = None
    area_id: int = 0
    network: Optional[str] = None
    wildcard: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True


@dataclass
class OSPFPlan:
    processes: List[OSPFProcessPlan] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.processes is None:
            self.processes = []


def _parse_ip_mask_pair(ip_el: Optional[ET.Element]) -> tuple[Optional[str], Optional[str]]:
    if ip_el is None:
        return None, None
    ip_address = ip_el.get("address") or ip_el.get("ip_address") or ip_el.get("ip")
    subnet_mask = ip_el.get("mask") or ip_el.get("subnet_mask")
    return (ip_address.strip() if ip_address else None, subnet_mask.strip() if subnet_mask else None)


def parse_lab_xml(lab_xml: str) -> tuple[List[RouterPlan], List[str]]:
    root = ET.fromstring(lab_xml)

    router_plans: List[RouterPlan] = []
    ping_targets: List[str] = []

    # Supporte plusieurs styles : <lab><router .../></lab> et <routers><router .../></routers>
    router_elements = root.findall(".//router")

    for router_el in router_elements:
        router_name = _first_attr(router_el, ["name"]) or _first_child_text(router_el, ["name"])
        if not router_name:
            continue

        vlans: List[VlanPlan] = []
        for vlan_el in router_el.findall(".//vlans/vlan"):
            vlan_id_raw = _first_attr(vlan_el, ["vlan_id", "id", "vid"]) or _first_child_text(
                vlan_el, ["vlan_id", "id"]
            )
            name = _first_attr(vlan_el, ["name"]) or _first_child_text(vlan_el, ["name"]) or ""
            if not vlan_id_raw:
                continue

            vlan_id = int(vlan_id_raw)

            vlan_desc = _first_attr(vlan_el, ["description"]) or _first_child_text(vlan_el, ["description"])
            # Optionnel : VLAN avec IP (pas indispensable pour inter-VLAN routing via SVIs)
            ip_address, subnet_mask = _parse_ip_mask_pair(vlan_el.find("./ip"))

            if not name:
                name = f"VLAN{vlan_id}"

            vlans.append(
                VlanPlan(
                    vlan_id=vlan_id,
                    name=name,
                    description=vlan_desc,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                )
            )

        interfaces: List[InterfacePlan] = []
        for intf_el in router_el.findall(".//interfaces/interface"):
            intf_name = _first_attr(intf_el, ["name"]) or _first_child_text(intf_el, ["name"])
            if not intf_name:
                continue

            enabled = _bool_from_text(_first_attr(intf_el, ["enabled"]), default=True)
            description = _first_attr(intf_el, ["description"]) or _first_child_text(
                intf_el, ["description"]
            )

            vlan_id_raw = _first_attr(intf_el, ["vlan_id", "vlan"])
            vlan_id = int(vlan_id_raw) if vlan_id_raw else None

            port_mode = _first_attr(intf_el, ["port_mode", "portMode"]) or "access"
            if isinstance(port_mode, str):
                port_mode = port_mode.lower()

            ip_address, subnet_mask = _parse_ip_mask_pair(intf_el.find("./ip"))
            ip_address = ip_address or intf_el.get("ip_address")
            subnet_mask = subnet_mask or intf_el.get("subnet_mask")

            is_svi = _bool_from_text(_first_attr(intf_el, ["svi"]), default=False) or intf_name.lower().startswith(
                "vlan"
            )

            interfaces.append(
                InterfacePlan(
                    name=intf_name,
                    enabled=enabled,
                    description=description,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    vlan_id=vlan_id if not is_svi else None,  # une SVI ne s'attache pas à un switchport
                    port_mode=port_mode if not is_svi else "access",
                    is_svi=is_svi,
                )
            )

        inter_vlan_el = router_el.find(".//routing/inter_vlan") or router_el.find(".//inter_vlan")
        inter_vlan_enabled = _bool_from_text(
            inter_vlan_el.get("enabled") if inter_vlan_el is not None else None, default=inter_vlan_el is not None
        )

        bgp_configs: List[BGPPlan] = []
        bgp_root = router_el.find(".//bgp")
        if bgp_root is not None:
            local_as_raw = _first_attr(bgp_root, ["local_as", "localAs", "as_local", "localAS"])
            local_as = int(local_as_raw) if local_as_raw else None

            router_id_address = _first_attr(
                bgp_root,
                ["router_id_address", "router-id-address", "router_id", "router-id", "router_id_address"],
            )

            if local_as is not None:
                neighbor_plans: List[BGPNeighborPlan] = []
                for n_el in bgp_root.findall(".//neighbor"):
                    neighbor_ip = _first_attr(n_el, ["neighbor_ip", "ip", "id", "neighborIp"]) or _first_child_text(
                        n_el, ["neighbor_ip", "ip", "id"]
                    )
                    remote_as_raw = _first_attr(n_el, ["remote_as", "remoteAs", "as_remote", "remoteAS", "remote_as_id"])
                    if not neighbor_ip or not remote_as_raw:
                        continue

                    neighbor_plans.append(
                        BGPNeighborPlan(
                            neighbor_ip=neighbor_ip,
                            remote_as=int(remote_as_raw),
                            description=_first_attr(n_el, ["description"]) or _first_child_text(n_el, ["description"]),
                            enabled=_bool_from_text(_first_attr(n_el, ["enabled"]), default=True),
                        )
                    )

                bgp_configs.append(
                    BGPPlan(
                        local_as=local_as,
                        router_id_address=router_id_address,
                        neighbors=neighbor_plans,
                    )
                )

        ospf_configs: List[OSPFPlan] = []
        ospf_root = router_el.find(".//ospf")
        if ospf_root is not None:
            process_plans: List[OSPFProcessPlan] = []
            for p_el in ospf_root.findall(".//process"):
                process_id_raw = _first_attr(p_el, ["process_id", "id", "processId"]) or _first_child_text(p_el, ["process_id", "id"])
                if not process_id_raw:
                    continue

                router_id_address = _first_attr(p_el, ["router_id_address", "router-id-address", "router_id", "router-id"])
                area_id_raw = _first_attr(p_el, ["area_id", "area", "areaId"]) or "0"
                area_id = int(area_id_raw)

                network = _first_attr(p_el, ["network"])
                wildcard = _first_attr(p_el, ["wildcard"])

                # Certains labs peuvent fournir network/wildcard dans des sous-tags
                if not network:
                    network = _first_child_text(p_el, ["network"])
                if not wildcard:
                    wildcard = _first_child_text(p_el, ["wildcard"])

                process_plans.append(
                    OSPFProcessPlan(
                        process_id=int(process_id_raw),
                        router_id_address=router_id_address,
                        area_id=area_id,
                        network=network,
                        wildcard=wildcard,
                        description=_first_attr(p_el, ["description"]) or _first_child_text(p_el, ["description"]),
                        enabled=_bool_from_text(_first_attr(p_el, ["enabled"]), default=True),
                    )
                )

            if process_plans:
                ospf_configs.append(OSPFPlan(processes=process_plans))

        router_plans.append(
            RouterPlan(
                name=router_name,
                vlans=vlans,
                interfaces=interfaces,
                inter_vlan=inter_vlan_enabled,
                bgp_configs=bgp_configs,
                ospf_configs=ospf_configs,
            )
        )

    # Pings au niveau global du lab
    for ping_el in root.findall(".//ping"):
        ip = ping_el.get("to") or ping_el.get("target") or ping_el.get("ip_address")
        if ip:
            ping_targets.append(ip.strip())

    if ping_targets and len(set(ping_targets)) != len(ping_targets):
        # On évite les doublons simples
        ping_targets = list(dict.fromkeys(ping_targets))

    return router_plans, ping_targets


async def upsert_vlan(db: AsyncSession, router_id: int, vlan: VlanPlan) -> VLAN:
    result = await db.execute(
        select(VLAN).where(VLAN.router_id == router_id, VLAN.vlan_id == vlan.vlan_id)
    )
    vlan_obj = result.scalar_one_or_none()
    if vlan_obj:
        vlan_obj.name = vlan.name or vlan_obj.name
        vlan_obj.description = vlan.description
        if vlan.ip_address:
            vlan_obj.ip_address = vlan.ip_address
        if vlan.subnet_mask:
            vlan_obj.subnet_mask = vlan.subnet_mask
        await db.flush()
        return vlan_obj

    vlan_obj = VLAN(
        router_id=router_id,
        vlan_id=vlan.vlan_id,
        name=vlan.name,
        description=vlan.description,
        ip_address=vlan.ip_address,
        subnet_mask=vlan.subnet_mask,
    )
    db.add(vlan_obj)
    await db.flush()
    await db.refresh(vlan_obj)
    return vlan_obj


async def upsert_interface(
    db: AsyncSession,
    router_id: int,
    interface: InterfacePlan,
    vlan_objs_by_vlan_id: dict[int, VLAN],
) -> Interface:
    result = await db.execute(select(Interface).where(Interface.router_id == router_id, Interface.name == interface.name))
    interface_obj = result.scalar_one_or_none()
    if interface_obj:
        interface_obj.enabled = interface.enabled
        interface_obj.description = interface.description
        interface_obj.ip_address = interface.ip_address
        interface_obj.subnet_mask = interface.subnet_mask
        interface_obj.port_mode = PortMode(interface.port_mode) if interface.port_mode else PortMode.ACCESS
        interface_obj.vlan_id = (
            vlan_objs_by_vlan_id[interface.vlan_id].id
            if interface.vlan_id is not None
            else None
        )
        await db.flush()
        return interface_obj

    interface_obj = Interface(
        router_id=router_id,
        name=interface.name,
        description=interface.description,
        enabled=interface.enabled,
        ip_address=interface.ip_address,
        subnet_mask=interface.subnet_mask,
        vlan_id=vlan_objs_by_vlan_id[interface.vlan_id].id if interface.vlan_id is not None else None,
        port_mode=PortMode(interface.port_mode) if interface.port_mode else PortMode.ACCESS,
    )
    db.add(interface_obj)
    await db.flush()
    await db.refresh(interface_obj)
    return interface_obj


async def upsert_bgp_config(
    db: AsyncSession,
    router_id: int,
    local_as: int,
    router_id_address: Optional[str],
    neighbor_ip: str,
    remote_as: int,
    description: Optional[str],
    enabled: bool,
) -> BGPConfig:
    # Uniqueness "métier" : un voisin (neighbor_ip) par routeur.
    result = await db.execute(
        select(BGPConfig).where(BGPConfig.router_id == router_id, BGPConfig.neighbor_ip == neighbor_ip)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.local_as = local_as
        existing.router_id_address = router_id_address
        existing.neighbor_as = remote_as
        existing.description = description
        existing.enabled = enabled
        await db.flush()
        return existing

    obj = BGPConfig(
        router_id=router_id,
        local_as=local_as,
        router_id_address=router_id_address,
        neighbor_ip=neighbor_ip,
        neighbor_as=remote_as,
        description=description,
        enabled=enabled,
    )
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def upsert_ospf_config(
    db: AsyncSession,
    router_id: int,
    process_id: int,
    router_id_address: Optional[str],
    area_id: int,
    network: str,
    wildcard: str,
    description: Optional[str],
    enabled: bool,
) -> OSPFConfig:
    result = await db.execute(
        select(OSPFConfig).where(OSPFConfig.router_id == router_id, OSPFConfig.process_id == process_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.router_id_address = router_id_address
        existing.area_id = area_id
        existing.network = network
        existing.wildcard = wildcard
        existing.description = description
        existing.enabled = enabled
        await db.flush()
        return existing

    obj = OSPFConfig(
        router_id=router_id,
        process_id=process_id,
        router_id_address=router_id_address,
        area_id=area_id,
        network=network,
        wildcard=wildcard,
        description=description,
        enabled=enabled,
    )
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.post("/lab/deploy", response_model=LabDeployResponse)
async def deploy_lab(payload: LabDeployRequest, db: AsyncSession = Depends(get_db)) -> LabDeployResponse:
    try:
        router_plans, ping_targets_from_xml = parse_lab_xml(payload.lab_xml)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"XML invalide: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur parsing XML: {str(e)}")

    if not router_plans:
        raise HTTPException(status_code=400, detail="Aucun <router> trouvé dans le XML")

    ping_targets = payload.ping_targets or ping_targets_from_xml

    if payload.dry_run:
        # Validation minimale: on vérifie que les routeurs référencés existent.
        routers_result: List[RouterDeployResult] = []
        for rp in router_plans:
            result = await db.execute(select(Router).where(Router.name == rp.name))
            router_obj = result.scalar_one_or_none()
            if not router_obj:
                routers_result.append(
                    RouterDeployResult(
                        router_name=rp.name,
                        router_id=-1,
                        success=False,
                        applied=0,
                        log_id=None,
                        error="Router introuvable dans la base (crée-le d'abord via l'UI).",
                    )
                )
                continue
            routers_result.append(
                RouterDeployResult(
                    router_name=rp.name,
                    router_id=router_obj.id,
                    success=True,
                    applied=(
                        len(rp.vlans)
                        + len(rp.interfaces)
                        + (1 if rp.inter_vlan else 0)
                        + sum(len(b.neighbors) for b in rp.bgp_configs)
                        + sum(len(p.processes) for p in rp.ospf_configs)
                    ),
                    log_id=None,
                    error=None,
                )
            )

        return LabDeployResponse(
            success=all(r.success for r in routers_result),
            message="Dry-run terminé" if all(r.success for r in routers_result) else "Dry-run avec erreurs",
            routers=routers_result,
            pings=None,
        )

    routers_result: List[RouterDeployResult] = []
    overall_success = True

    for rp in router_plans:
        result = await db.execute(select(Router).where(Router.name == rp.name))
        router_obj = result.scalar_one_or_none()
        if not router_obj:
            overall_success = False
            routers_result.append(
                RouterDeployResult(
                    router_name=rp.name,
                    router_id=-1,
                    success=False,
                    applied=0,
                    log_id=None,
                    error="Router introuvable dans la base.",
                )
            )
            continue

        # On applique les objets côté DB avant de pousser la config NETCONF.
        vlan_objs_by_vlan_id: dict[int, VLAN] = {}
        for vlan in rp.vlans:
            vlan_obj = await upsert_vlan(db=db, router_id=router_obj.id, vlan=vlan)
            vlan_objs_by_vlan_id[vlan.vlan_id] = vlan_obj

        interface_objs_count = 0
        for intf in rp.interfaces:
            # Pour les interfaces physiques: il faut que la VLAN existe soit dans le DB soit dans le plan.
            if intf.vlan_id is not None and intf.vlan_id not in vlan_objs_by_vlan_id:
                overall_success = False
                routers_result.append(
                    RouterDeployResult(
                        router_name=rp.name,
                        router_id=router_obj.id,
                        success=False,
                        applied=0,
                        log_id=None,
                        error=f"Interface {intf.name} référence VLAN {intf.vlan_id} qui n'existe pas dans le plan/DB.",
                    )
                )
                interface_objs_count = -1
                break
            await upsert_interface(
                db=db,
                router_id=router_obj.id,
                interface=intf,
                vlan_objs_by_vlan_id=vlan_objs_by_vlan_id,
            )
            interface_objs_count += 1

        if interface_objs_count == -1:
            continue

        # Routage / protocols (BGP, OSPF) stockés côté DB
        for bgp_plan in rp.bgp_configs:
            for n in bgp_plan.neighbors:
                if not bgp_plan.local_as:
                    raise RuntimeError("BGP: local_as manquant")
                await upsert_bgp_config(
                    db=db,
                    router_id=router_obj.id,
                    local_as=bgp_plan.local_as,
                    router_id_address=bgp_plan.router_id_address,
                    neighbor_ip=n.neighbor_ip,
                    remote_as=n.remote_as,
                    description=n.description,
                    enabled=n.enabled,
                )

        for ospf_plan in rp.ospf_configs:
            for p in ospf_plan.processes:
                if not p.enabled and (not p.network or not p.wildcard):
                    # Si désactivé, pas besoin des paramètres réseau.
                    await upsert_ospf_config(
                        db=db,
                        router_id=router_obj.id,
                        process_id=p.process_id,
                        router_id_address=p.router_id_address,
                        area_id=p.area_id,
                        network=p.network or "0.0.0.0",
                        wildcard=p.wildcard or "0.0.0.0",
                        description=p.description,
                        enabled=p.enabled,
                    )
                    continue

                if not p.network or not p.wildcard:
                    raise RuntimeError(f"OSPF: network/wildcard manquants pour process {p.process_id}")

                await upsert_ospf_config(
                    db=db,
                    router_id=router_obj.id,
                    process_id=p.process_id,
                    router_id_address=p.router_id_address,
                    area_id=p.area_id,
                    network=p.network,
                    wildcard=p.wildcard,
                    description=p.description,
                    enabled=p.enabled,
                )

        config_log = ConfigLog(
            router_id=router_obj.id,
            action=ConfigAction.UPDATE,
            config_type="LAB_DEPLOY",
            config_data=(
                f"routers={rp.name};"
                f"vlans={len(rp.vlans)};"
                f"interfaces={len(rp.interfaces)};"
                f"inter_vlan={rp.inter_vlan};"
                f"bgp={sum(len(b.neighbors) for b in rp.bgp_configs)};"
                f"ospf={sum(len(p.processes) for p in rp.ospf_configs)}"
            ),
            status=ConfigStatus.PENDING,
        )
        db.add(config_log)
        await db.flush()

        client = NETCONFClient(
            host=router_obj.ip_address,
            port=router_obj.netconf_port,
            username=router_obj.username,
            password=router_obj.password,
            device_type=router_obj.device_type,
        )

        success, message = client.connect()
        if not success:
            overall_success = False
            config_log.status = ConfigStatus.FAILED
            config_log.error_message = message
            router_obj.status = RouterStatus.ERROR
            await db.flush()
            routers_result.append(
                RouterDeployResult(
                    router_name=rp.name,
                    router_id=router_obj.id,
                    success=False,
                    applied=(
                        len(rp.vlans)
                        + len(rp.interfaces)
                        + (1 if rp.inter_vlan else 0)
                        + sum(len(b.neighbors) for b in rp.bgp_configs)
                        + sum(len(p.processes) for p in rp.ospf_configs)
                    ),
                    log_id=config_log.id,
                    error=message,
                )
            )
            continue

        config_builder = ConfigBuilder()
        applied_steps = 0
        last_response: Optional[str] = None
        router_success = True

        try:
            # VLANs
            for vlan in rp.vlans:
                xml_config = config_builder.build_vlan_create(
                    vlan_id=vlan.vlan_id,
                    name=vlan.name,
                    description=vlan.description,
                )
                ok, response = client.edit_config(xml_config)
                last_response = response
                if not ok:
                    router_success = False
                    raise RuntimeError(response)
                applied_steps += 1

            # Interfaces (physiques + SVIs)
            for intf in rp.interfaces:
                vlan_id_fk = None
                if intf.vlan_id is not None:
                    vlan_id_fk = vlan_objs_by_vlan_id[intf.vlan_id].vlan_id

                xml_config = config_builder.build_interface_create(
                    interface_name=intf.name,
                    description=intf.description,
                    enabled=intf.enabled,
                    ip_address=intf.ip_address,
                    subnet_mask=intf.subnet_mask,
                    vlan_id=vlan_id_fk,
                    port_mode=intf.port_mode if intf.vlan_id is not None else "access",
                )
                ok, response = client.edit_config(xml_config)
                last_response = response
                if not ok:
                    router_success = False
                    raise RuntimeError(response)
                applied_steps += 1

            # Inter-VLAN routing via SVIs
            if rp.inter_vlan:
                xml_config = config_builder.build_ip_routing_enable()
                ok, response = client.edit_config(xml_config)
                last_response = response
                if not ok:
                    router_success = False
                    raise RuntimeError(response)
                applied_steps += 1

            # BGP
            for bgp_plan in rp.bgp_configs:
                # On pousse d'abord le "router bgp" (avec éventuellement router-id),
                # puis on applique les voisins un par un.
                xml_router = config_builder.build_bgp_router(
                    local_as=bgp_plan.local_as,
                    router_id=bgp_plan.router_id_address,
                )
                ok, response = client.edit_config(xml_router)
                last_response = response
                if not ok:
                    router_success = False
                    raise RuntimeError(response)
                applied_steps += 1

                for n in bgp_plan.neighbors:
                    if n.enabled:
                        xml_neighbor = config_builder.build_bgp_neighbor(
                            local_as=bgp_plan.local_as,
                            neighbor_ip=n.neighbor_ip,
                            remote_as=n.remote_as,
                            description=n.description,
                            enabled=n.enabled,
                        )
                    else:
                        xml_neighbor = config_builder.build_bgp_neighbor_delete(
                            local_as=bgp_plan.local_as,
                            neighbor_ip=n.neighbor_ip,
                        )
                    ok, response = client.edit_config(xml_neighbor)
                    last_response = response
                    if not ok:
                        router_success = False
                        raise RuntimeError(response)
                    applied_steps += 1

            # OSPF
            for ospf_plan in rp.ospf_configs:
                for p in ospf_plan.processes:
                    if p.enabled:
                        if not p.network or not p.wildcard:
                            raise RuntimeError(f"OSPF: network/wildcard manquants pour process {p.process_id}")
                        xml_config = config_builder.build_ospf_process(
                            process_id=p.process_id,
                            router_id=p.router_id_address,
                            area_id=p.area_id,
                            network=p.network,
                            wildcard=p.wildcard,
                        )
                    else:
                        xml_config = config_builder.build_ospf_delete(process_id=p.process_id)

                    ok, response = client.edit_config(xml_config)
                    last_response = response
                    if not ok:
                        router_success = False
                        raise RuntimeError(response)
                    applied_steps += 1

            if router_success:
                client.commit()
                config_log.status = ConfigStatus.SUCCESS
                config_log.netconf_response = last_response
                router_obj.status = RouterStatus.ACTIVE
            else:
                config_log.status = ConfigStatus.FAILED
                config_log.netconf_response = last_response

        except Exception as e:
            overall_success = False
            router_success = False
            config_log.status = ConfigStatus.FAILED
            config_log.error_message = str(e)
            config_log.netconf_response = last_response
            router_obj.status = RouterStatus.ERROR
            await db.flush()
        finally:
            client.disconnect()
            await db.flush()

        routers_result.append(
            RouterDeployResult(
                router_name=rp.name,
                router_id=router_obj.id,
                success=router_success,
                applied=applied_steps,
                log_id=config_log.id,
                error=None if router_success else (config_log.error_message or "Echec déploiement"),
            )
        )

    ping_results: Optional[List[PingResult]] = None
    if ping_targets:
        ping_results = []
        for target in ping_targets:
            pr = await ping_host(target)
            ping_results.append(
                PingResult(
                    ip_address=target,
                    success=pr.get("success", False),
                    reachable=pr.get("reachable", False),
                    packet_loss=pr.get("packet_loss"),
                    rtt=pr.get("rtt"),
                    error=pr.get("error"),
                )
            )

    return LabDeployResponse(
        success=overall_success,
        message="Lab déployé avec succès" if overall_success else "Lab déployé avec erreurs",
        routers=routers_result,
        pings=ping_results,
    )

