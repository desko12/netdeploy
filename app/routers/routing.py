from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.database import Router, BGPConfig, OSPFConfig, ConfigLog, ConfigAction, ConfigStatus, RouterStatus
from app.models.schemas import (
    BGPConfigCreate, BGPConfigUpdate, BGPConfigResponse,
    OSPFConfigCreate, OSPFConfigUpdate, OSPFConfigResponse
)
from app.models.db_session import get_db
from app.services.netconf_client import NETCONFClient
from app.services.config_builder import ConfigBuilder

router = APIRouter(prefix="/api", tags=["Routing"])


@router.get("/routers/{router_id}/bgp", response_model=List[BGPConfigResponse])
async def list_bgp_configs(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BGPConfig).where(BGPConfig.router_id == router_id)
    )
    return result.scalars().all()


@router.post("/routers/{router_id}/bgp", response_model=BGPConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_bgp_config(
    router_id: int,
    bgp_data: BGPConfigCreate,
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
        select(BGPConfig).where(
            BGPConfig.router_id == router_id,
            BGPConfig.neighbor_ip == bgp_data.neighbor_ip
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"BGP neighbor {bgp_data.neighbor_ip} already configured"
        )

    bgp_obj = BGPConfig(**bgp_data.model_dump())
    db.add(bgp_obj)
    await db.flush()
    await db.refresh(bgp_obj)
    return bgp_obj


@router.get("/bgp/{bgp_id}", response_model=BGPConfigResponse)
async def get_bgp_config(
    bgp_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BGPConfig).where(BGPConfig.id == bgp_id))
    bgp_obj = result.scalar_one_or_none()
    if not bgp_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BGP config {bgp_id} not found"
        )
    return bgp_obj


@router.put("/bgp/{bgp_id}", response_model=BGPConfigResponse)
async def update_bgp_config(
    bgp_id: int,
    bgp_data: BGPConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BGPConfig).where(BGPConfig.id == bgp_id))
    bgp_obj = result.scalar_one_or_none()
    if not bgp_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BGP config {bgp_id} not found"
        )

    update_data = bgp_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bgp_obj, key, value)

    await db.flush()
    await db.refresh(bgp_obj)
    return bgp_obj


@router.delete("/bgp/{bgp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bgp_config(
    bgp_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BGPConfig).where(BGPConfig.id == bgp_id))
    bgp_obj = result.scalar_one_or_none()
    if not bgp_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BGP config {bgp_id} not found"
        )

    await db.delete(bgp_obj)
    return None


@router.post("/bgp/{bgp_id}/apply")
async def apply_bgp_config(
    bgp_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BGPConfig).where(BGPConfig.id == bgp_id))
    bgp_obj = result.scalar_one_or_none()
    if not bgp_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BGP config {bgp_id} not found"
        )

    result = await db.execute(select(Router).where(Router.id == bgp_obj.router_id))
    router_obj = result.scalar_one_or_none()

    config_log = ConfigLog(
        router_id=bgp_obj.router_id,
        action=ConfigAction.CREATE,
        config_type="BGP",
        config_data=f"neighbor={bgp_obj.neighbor_ip},as={bgp_obj.neighbor_as}",
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

        xml_router = config_builder.build_bgp_router(
            local_as=bgp_obj.local_as,
            router_id=bgp_obj.router_id_address
        )
        success, response = client.edit_config(xml_router)

        if not success:
            config_log.status = ConfigStatus.FAILED
            config_log.error_message = response
            client.disconnect()
            await db.flush()
            return {"success": False, "message": response, "log_id": config_log.id}

        xml_neighbor = config_builder.build_bgp_neighbor(
            local_as=bgp_obj.local_as,
            neighbor_ip=bgp_obj.neighbor_ip,
            remote_as=bgp_obj.neighbor_as,
            description=bgp_obj.description,
            enabled=bgp_obj.enabled
        )
        success, response = client.edit_config(xml_neighbor)

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


@router.get("/routers/{router_id}/ospf", response_model=List[OSPFConfigResponse])
async def list_ospf_configs(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(OSPFConfig).where(OSPFConfig.router_id == router_id)
    )
    return result.scalars().all()


@router.post("/routers/{router_id}/ospf", response_model=OSPFConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_ospf_config(
    router_id: int,
    ospf_data: OSPFConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    ospf_obj = OSPFConfig(**ospf_data.model_dump())
    db.add(ospf_obj)
    await db.flush()
    await db.refresh(ospf_obj)
    return ospf_obj


@router.get("/ospf/{ospf_id}", response_model=OSPFConfigResponse)
async def get_ospf_config(
    ospf_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(OSPFConfig).where(OSPFConfig.id == ospf_id))
    ospf_obj = result.scalar_one_or_none()
    if not ospf_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSPF config {ospf_id} not found"
        )
    return ospf_obj


@router.put("/ospf/{ospf_id}", response_model=OSPFConfigResponse)
async def update_ospf_config(
    ospf_id: int,
    ospf_data: OSPFConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(OSPFConfig).where(OSPFConfig.id == ospf_id))
    ospf_obj = result.scalar_one_or_none()
    if not ospf_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSPF config {ospf_id} not found"
        )

    update_data = ospf_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ospf_obj, key, value)

    await db.flush()
    await db.refresh(ospf_obj)
    return ospf_obj


@router.delete("/ospf/{ospf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ospf_config(
    ospf_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(OSPFConfig).where(OSPFConfig.id == ospf_id))
    ospf_obj = result.scalar_one_or_none()
    if not ospf_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSPF config {ospf_id} not found"
        )

    await db.delete(ospf_obj)
    return None


@router.post("/ospf/{ospf_id}/apply")
async def apply_ospf_config(
    ospf_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(OSPFConfig).where(OSPFConfig.id == ospf_id))
    ospf_obj = result.scalar_one_or_none()
    if not ospf_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSPF config {ospf_id} not found"
        )

    result = await db.execute(select(Router).where(Router.id == ospf_obj.router_id))
    router_obj = result.scalar_one_or_none()

    config_log = ConfigLog(
        router_id=ospf_obj.router_id,
        action=ConfigAction.CREATE,
        config_type="OSPF",
        config_data=f"process={ospf_obj.process_id},network={ospf_obj.network}",
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
        xml_config = config_builder.build_ospf_process(
            process_id=ospf_obj.process_id,
            router_id=ospf_obj.router_id_address,
            area_id=ospf_obj.area_id,
            network=ospf_obj.network,
            wildcard=ospf_obj.wildcard
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
