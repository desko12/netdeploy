from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import os

from app.models.database import Router, VLAN, Interface, BGPConfig, OSPFConfig, ConfigLog
from app.models.db_session import get_db
from app.models.schemas import RouterCreate, RouterUpdate, VLANCreate, InterfaceCreate, BGPConfigCreate, OSPFConfigCreate

templates = Jinja2Templates(directory="app/templates")

web = APIRouter(tags=["Web UI"])


@web.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    routers_result = await db.execute(select(Router))
    routers = routers_result.scalars().all()

    logs_result = await db.execute(
        select(ConfigLog).order_by(ConfigLog.created_at.desc()).limit(10)
    )
    logs = logs_result.scalars().all()

    total_routers = len(routers)
    active_routers = len([r for r in routers if r.status == "active"])

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": {
            "total_routers": total_routers,
            "active_routers": active_routers,
            "successful_configs": 0,
            "failed_configs": 0
        },
        "recent_routers": routers[:5],
        "recent_logs": logs
    })


@web.get("/routers", response_class=HTMLResponse)
async def list_routers_page(request: Request, db: AsyncSession = Depends(get_db)):
    routers_result = await db.execute(select(Router).order_by(Router.name))
    routers = routers_result.scalars().all()
    return templates.TemplateResponse("routers/list.html", {
        "request": request,
        "routers": routers
    })


@web.get("/routers/add", response_class=HTMLResponse)
async def add_router_page(request: Request):
    return templates.TemplateResponse("routers/add.html", {
        "request": request,
        "router": None
    })


@web.get("/routers/{router_id}", response_class=HTMLResponse)
async def router_detail_page(router_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Router)
        .options(
            selectinload(Router.vlans),
            selectinload(Router.interfaces),
            selectinload(Router.bgp_configs),
            selectinload(Router.ospf_configs),
            selectinload(Router.config_logs)
        )
        .where(Router.id == router_id)
    )
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return templates.TemplateResponse("routers/detail.html", {
        "request": request,
        "router": router
    })


@web.get("/routers/{router_id}/edit", response_class=HTMLResponse)
async def edit_router_page(router_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return templates.TemplateResponse("routers/add.html", {
        "request": request,
        "router": router
    })


@web.get("/routers/{router_id}/vlans/add", response_class=HTMLResponse)
async def add_vlan_page(router_id: int, request: Request):
    return templates.TemplateResponse("vlans/add.html", {
        "request": request,
        "router_id": router_id,
        "vlan": None
    })


@web.get("/vlans", response_class=HTMLResponse)
async def list_vlans_page(request: Request, db: AsyncSession = Depends(get_db)):
    vlans_result = await db.execute(
        select(VLAN).order_by(VLAN.vlan_id)
    )
    vlans = vlans_result.scalars().all()
    return templates.TemplateResponse("vlans/list.html", {
        "request": request,
        "vlans": vlans
    })


@web.get("/routers/{router_id}/interfaces/add", response_class=HTMLResponse)
async def add_interface_page(router_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    vlans_result = await db.execute(select(VLAN).where(VLAN.router_id == router_id))
    vlans = vlans_result.scalars().all()
    
    return templates.TemplateResponse("interfaces/add.html", {
        "request": request,
        "router": router,
        "router_id": router_id,
        "vlans": vlans,
        "interface": None
    })


@web.get("/routers/{router_id}/bgp/add", response_class=HTMLResponse)
async def add_bgp_page(router_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    return templates.TemplateResponse("routing/bgp.html", {
        "request": request,
        "router": router,
        "router_id": router_id,
        "bgp": None
    })


@web.get("/routers/{router_id}/ospf/add", response_class=HTMLResponse)
async def add_ospf_page(router_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    return templates.TemplateResponse("routing/ospf.html", {
        "request": request,
        "router": router,
        "router_id": router_id,
        "ospf": None
    })


@web.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, db: AsyncSession = Depends(get_db)):
    logs_result = await db.execute(
        select(ConfigLog)
        .order_by(ConfigLog.created_at.desc())
        .limit(100)
    )
    logs = logs_result.scalars().all()
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs
    })


@web.get("/lab/deploy", response_class=HTMLResponse)
async def lab_deploy_page(request: Request):
    example_xml = """<lab>
  <router name="R1">
    <vlans>
      <vlan vlan_id="10" name="VLAN10" />
      <vlan vlan_id="20" name="VLAN20" />
    </vlans>
    <interfaces>
      <!-- Ports physiques (access) vers les VLAN -->
      <interface name="GigabitEthernet0/1" enabled="true" port_mode="access" vlan_id="10" description="LAN VLAN10" />
      <interface name="GigabitEthernet0/2" enabled="true" port_mode="access" vlan_id="20" description="LAN VLAN20" />

      <!-- SVIs pour le routage inter-VLAN -->
      <interface name="Vlan10" svi="true" enabled="true" ip_address="10.10.10.1" subnet_mask="255.255.255.0" />
      <interface name="Vlan20" svi="true" enabled="true" ip_address="10.10.20.1" subnet_mask="255.255.255.0" />
    </interfaces>
    <routing>
      <inter_vlan enabled="true" />
    </routing>

    <!-- Routage dynamique (BGP) -->
    <bgp local_as="65001" router_id_address="10.0.0.1">
      <neighbor neighbor_ip="192.168.1.2" remote_as="65002" enabled="true" description="Peer R2" />
    </bgp>

    <!-- Routage dynamique (OSPF) -->
    <ospf>
      <process process_id="1" router_id_address="10.0.0.1" area_id="0"
               network="10.10.0.0" wildcard="0.0.255.255"
               enabled="true" />
    </ospf>
  </router>

  <pings>
    <ping to="10.10.10.1" />
    <ping to="10.10.20.1" />
  </pings>
</lab>
"""
    return templates.TemplateResponse("lab/deploy.html", {"request": request, "example_xml": example_xml})


@web.get("/routers/{router_id}/ping", response_class=HTMLResponse)
async def ping_page(router_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return templates.TemplateResponse("routers/ping.html", {
        "request": request,
        "router": router
    })


@web.post("/routers")
async def create_router_api(router_data: RouterCreate, db: AsyncSession = Depends(get_db)):
    router = Router(**router_data.model_dump())
    db.add(router)
    await db.flush()
    await db.refresh(router)
    return {"id": router.id, "name": router.name}


@web.put("/routers/{router_id}")
async def update_router_api(
    router_id: int,
    router_data: RouterUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router = result.scalar_one_or_none()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")

    update_data = router_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(router, key, value)

    await db.flush()
    return {"id": router.id, "name": router.name}


@web.post("/routers/{router_id}/vlans")
async def create_vlan_api(
    router_id: int,
    vlan_data: VLANCreate,
    db: AsyncSession = Depends(get_db)
):
    vlan_data.router_id = router_id
    vlan = VLAN(**vlan_data.model_dump())
    db.add(vlan)
    await db.flush()
    await db.refresh(vlan)
    return {"id": vlan.id, "vlan_id": vlan.vlan_id, "name": vlan.name}


@web.post("/routers/{router_id}/interfaces")
async def create_interface_api(
    router_id: int,
    interface_data: InterfaceCreate,
    db: AsyncSession = Depends(get_db)
):
    interface_data.router_id = router_id
    interface = Interface(**interface_data.model_dump())
    db.add(interface)
    await db.flush()
    await db.refresh(interface)
    return {"id": interface.id, "name": interface.name}


@web.post("/routers/{router_id}/bgp")
async def create_bgp_api(
    router_id: int,
    bgp_data: BGPConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    bgp_data.router_id = router_id
    bgp = BGPConfig(**bgp_data.model_dump())
    db.add(bgp)
    await db.flush()
    await db.refresh(bgp)
    return {"id": bgp.id, "neighbor_ip": bgp.neighbor_ip}


@web.post("/routers/{router_id}/ospf")
async def create_ospf_api(
    router_id: int,
    ospf_data: OSPFConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    ospf_data.router_id = router_id
    ospf = OSPFConfig(**ospf_data.model_dump())
    db.add(ospf)
    await db.flush()
    await db.refresh(ospf)
    return {"id": ospf.id, "process_id": ospf.process_id}
