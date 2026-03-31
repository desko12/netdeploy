from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.database import Router, VLAN, ConfigLog, ConfigAction, ConfigStatus, RouterStatus
from app.models.schemas import VLANCreate, VLANUpdate, VLANResponse
from app.models.db_session import get_db
from app.services.netconf_client import NETCONFClient
from app.services.config_builder import ConfigBuilder

router = APIRouter(prefix="/api", tags=["VLANs"])


@router.get("/routers/{router_id}/vlans", response_model=List[VLANResponse])
async def list_vlans(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(VLAN).where(VLAN.router_id == router_id).order_by(VLAN.vlan_id)
    )
    return result.scalars().all()


@router.post("/routers/{router_id}/vlans", response_model=VLANResponse, status_code=status.HTTP_201_CREATED)
async def create_vlan(
    router_id: int,
    vlan_data: VLANCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    existing = await db.execute(
        select(VLAN).where(VLAN.router_id == router_id, VLAN.vlan_id == vlan_data.vlan_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"VLAN {vlan_data.vlan_id} already exists on router {router_id}"
        )

    vlan_obj = VLAN(**vlan_data.model_dump())
    db.add(vlan_obj)
    await db.flush()
    await db.refresh(vlan_obj)
    return vlan_obj


@router.get("/vlans/{vlan_id}", response_model=VLANResponse)
async def get_vlan(
    vlan_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(VLAN).where(VLAN.id == vlan_id))
    vlan_obj = result.scalar_one_or_none()
    if not vlan_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN {vlan_id} not found"
        )
    return vlan_obj


@router.put("/vlans/{vlan_id}", response_model=VLANResponse)
async def update_vlan(
    vlan_id: int,
    vlan_data: VLANUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(VLAN).where(VLAN.id == vlan_id))
    vlan_obj = result.scalar_one_or_none()
    if not vlan_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN {vlan_id} not found"
        )

    update_data = vlan_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vlan_obj, key, value)

    await db.flush()
    await db.refresh(vlan_obj)
    return vlan_obj


@router.delete("/vlans/{vlan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vlan(
    vlan_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(VLAN).where(VLAN.id == vlan_id))
    vlan_obj = result.scalar_one_or_none()
    if not vlan_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN {vlan_id} not found"
        )

    await db.delete(vlan_obj)
    return None


@router.post("/vlans/{vlan_id}/apply")
async def apply_vlan(
    vlan_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(VLAN).where(VLAN.id == vlan_id))
    vlan_obj = result.scalar_one_or_none()
    if not vlan_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN {vlan_id} not found"
        )

    result = await db.execute(select(Router).where(Router.id == vlan_obj.router_id))
    router_obj = result.scalar_one_or_none()

    config_log = ConfigLog(
        router_id=vlan_obj.router_id,
        action=ConfigAction.CREATE,
        config_type="VLAN",
        config_data=f"vlan_id={vlan_obj.vlan_id},name={vlan_obj.name}",
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
        xml_config = config_builder.build_vlan_create(
            vlan_id=vlan_obj.vlan_id,
            name=vlan_obj.name,
            description=vlan_obj.description
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
