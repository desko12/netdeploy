from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.database import Router, Interface, VLAN, ConfigLog, ConfigAction, ConfigStatus, RouterStatus
from app.models.schemas import InterfaceCreate, InterfaceUpdate, InterfaceResponse
from app.models.db_session import get_db
from app.services.netconf_client import NETCONFClient
from app.services.config_builder import ConfigBuilder

router = APIRouter(prefix="/api", tags=["Interfaces"])


@router.get("/routers/{router_id}/interfaces", response_model=List[InterfaceResponse])
async def list_interfaces(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Interface).where(Interface.router_id == router_id).order_by(Interface.name)
    )
    return result.scalars().all()


@router.post("/routers/{router_id}/interfaces", response_model=InterfaceResponse, status_code=status.HTTP_201_CREATED)
async def create_interface(
    router_id: int,
    interface_data: InterfaceCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    if interface_data.vlan_id:
        vlan_result = await db.execute(
            select(VLAN).where(VLAN.id == interface_data.vlan_id, VLAN.router_id == router_id)
        )
        if not vlan_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"VLAN {interface_data.vlan_id} not found on router {router_id}"
            )

    interface_obj = Interface(**interface_data.model_dump())
    db.add(interface_obj)
    await db.flush()
    await db.refresh(interface_obj)
    return interface_obj


@router.get("/interfaces/{interface_id}", response_model=InterfaceResponse)
async def get_interface(
    interface_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Interface).where(Interface.id == interface_id))
    interface_obj = result.scalar_one_or_none()
    if not interface_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found"
        )
    return interface_obj


@router.put("/interfaces/{interface_id}", response_model=InterfaceResponse)
async def update_interface(
    interface_id: int,
    interface_data: InterfaceUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Interface).where(Interface.id == interface_id))
    interface_obj = result.scalar_one_or_none()
    if not interface_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found"
        )

    update_data = interface_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(interface_obj, key, value)

    await db.flush()
    await db.refresh(interface_obj)
    return interface_obj


@router.delete("/interfaces/{interface_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interface(
    interface_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Interface).where(Interface.id == interface_id))
    interface_obj = result.scalar_one_or_none()
    if not interface_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found"
        )

    await db.delete(interface_obj)
    return None


@router.post("/interfaces/{interface_id}/apply")
async def apply_interface(
    interface_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Interface).where(Interface.id == interface_id))
    interface_obj = result.scalar_one_or_none()
    if not interface_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found"
        )

    result = await db.execute(select(Router).where(Router.id == interface_obj.router_id))
    router_obj = result.scalar_one_or_none()

    config_log = ConfigLog(
        router_id=interface_obj.router_id,
        action=ConfigAction.CREATE,
        config_type="INTERFACE",
        config_data=f"interface={interface_obj.name}",
        status=ConfigStatus.PENDING
    )
    db.add(config_log)
    await db.flush()

    try:
        client = NETCONFClient(
            host=router_obj.ip_address,
            port=router_obj.netconf_port,
            username=router_obj.username,
            password=router_obj.password,
            device_type=router_obj.device_type
        )

        success, message = client.connect()

        if not success:
            config_log.status = ConfigStatus.FAILED
            config_log.error_message = message
            router_obj.status = RouterStatus.ERROR
            await db.flush()
            return {"success": False, "message": message, "log_id": config_log.id}

        config_builder = ConfigBuilder()
        vlan_obj = None
        if interface_obj.vlan_id:
            vlan_result = await db.execute(select(VLAN).where(VLAN.id == interface_obj.vlan_id))
            vlan_obj = vlan_result.scalar_one_or_none()

        xml_config = config_builder.build_interface_create(
            interface_name=interface_obj.name,
            description=interface_obj.description,
            enabled=interface_obj.enabled,
            ip_address=interface_obj.ip_address,
            subnet_mask=interface_obj.subnet_mask,
            vlan_id=vlan_obj.vlan_id if vlan_obj else None,
            port_mode=interface_obj.port_mode.value if interface_obj.port_mode else "access"
        )

        success, response = client.edit_config(xml_config)

        if success:
            client.commit()
            config_log.status = ConfigStatus.SUCCESS
            config_log.netconf_response = response
            router_obj.status = RouterStatus.ACTIVE
        else:
            config_log.status = ConfigStatus.FAILED
            config_log.error_message = response
            config_log.netconf_response = response

        client.disconnect()
        await db.flush()

        return {
            "success": success,
            "message": response if success else response,
            "log_id": config_log.id
        }

    except Exception as e:
        config_log.status = ConfigStatus.FAILED
        config_log.error_message = str(e)
        await db.flush()
        return {"success": False, "message": str(e), "log_id": config_log.id}


@router.get("/interfaces/{interface_id}/xml-preview")
async def preview_interface_xml(
    interface_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Interface).where(Interface.id == interface_id))
    interface_obj = result.scalar_one_or_none()
    if not interface_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found"
        )

    vlan_obj = None
    if interface_obj.vlan_id:
        vlan_result = await db.execute(select(VLAN).where(VLAN.id == interface_obj.vlan_id))
        vlan_obj = vlan_result.scalar_one_or_none()

    config_builder = ConfigBuilder()
    xml_config = config_builder.build_interface_create(
        interface_name=interface_obj.name,
        description=interface_obj.description,
        enabled=interface_obj.enabled,
        ip_address=interface_obj.ip_address,
        subnet_mask=interface_obj.subnet_mask,
        vlan_id=vlan_obj.vlan_id if vlan_obj else None,
        port_mode=interface_obj.port_mode.value if interface_obj.port_mode else "access"
    )

    return {"xml": xml_config}
