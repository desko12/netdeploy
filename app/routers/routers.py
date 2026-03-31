from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import asyncio
import socket

from app.models.database import Router, RouterStatus
from app.models.schemas import (
    RouterCreate, RouterUpdate, RouterResponse, RouterDetail,
    NETCONFTestRequest, NETCONFTestResponse
)
from app.models.db_session import get_db
from app.services.netconf_client import NETCONFClient

router = APIRouter(prefix="/api/routers", tags=["Routers"])


@router.get("", response_model=List[RouterResponse])
async def list_routers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Router).offset(skip).limit(limit).order_by(Router.name)
    )
    return result.scalars().all()


@router.get("/{router_id}", response_model=RouterDetail)
async def get_router(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Router)
        .options(
            selectinload(Router.vlans),
            selectinload(Router.interfaces),
            selectinload(Router.bgp_configs),
            selectinload(Router.ospf_configs)
        )
        .where(Router.id == router_id)
    )
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )
    return router_obj


@router.post("", response_model=RouterResponse, status_code=status.HTTP_201_CREATED)
async def create_router(
    router_data: RouterCreate,
    db: AsyncSession = Depends(get_db)
):
    router_obj = Router(**router_data.model_dump())
    db.add(router_obj)
    await db.flush()
    await db.refresh(router_obj)
    return router_obj


@router.put("/{router_id}", response_model=RouterResponse)
async def update_router(
    router_id: int,
    router_data: RouterUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    update_data = router_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(router_obj, key, value)

    await db.flush()
    await db.refresh(router_obj)
    return router_obj


@router.delete("/{router_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_router(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    await db.delete(router_obj)
    return None


@router.post("/{router_id}/test", response_model=NETCONFTestResponse)
async def test_router_connection(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    client = NETCONFClient(
        host=router_obj.ip_address,
        port=router_obj.netconf_port,
        username=router_obj.username,
        password=router_obj.password,
        device_type=router_obj.device_type
    )

    success, message = client.connect()

    if success:
        success_info, device_info = client.get_device_info()
        client.disconnect()
        if router_obj.status != RouterStatus.ACTIVE:
            router_obj.status = RouterStatus.ACTIVE
            await db.flush()
    else:
        router_obj.status = RouterStatus.ERROR
        await db.flush()
        device_info = None

    return NETCONFTestResponse(
        success=success,
        message=message,
        device_info=device_info
    )


@router.post("/test-connection", response_model=NETCONFTestResponse)
async def test_connection(
    test_data: NETCONFTestRequest
):
    client = NETCONFClient(
        host=test_data.ip_address,
        port=test_data.port,
        username=test_data.username,
        password=test_data.password
    )

    success, message = client.connect()

    if success:
        success_info, device_info = client.get_device_info()
        client.disconnect()
    else:
        device_info = None

    return NETCONFTestResponse(
        success=success,
        message=message,
        device_info=device_info
    )


@router.post("/{router_id}/ping")
async def ping_router(
    router_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()
    if not router_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Router {router_id} not found"
        )

    return await ping_host(router_obj.ip_address)


@router.post("/ping")
async def ping_host_endpoint(
    ip_address: str = Query(..., description="IP address to ping")
):
    return await ping_host(ip_address)


async def ping_host(ip_address: str):
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping", "-c", "4", "-W", "2", ip_address,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        output = stdout.decode()
        error = stderr.decode()

        if proc.returncode == 0:
            stats_line = [l for l in output.split('\n') if 'packet loss' in l]
            rtt_line = [l for l in output.split('\n') if 'rtt' in l or 'round-trip' in l]
            return {
                "success": True,
                "ip_address": ip_address,
                "output": output,
                "packet_loss": stats_line[0] if stats_line else "0% packet loss",
                "rtt": rtt_line[0] if rtt_line else "N/A",
                "reachable": True
            }
        else:
            return {
                "success": False,
                "ip_address": ip_address,
                "output": output,
                "error": error or "Host unreachable",
                "reachable": False
            }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "ip_address": ip_address,
            "error": "Ping timeout",
            "reachable": False
        }
    except Exception as e:
        return {
            "success": False,
            "ip_address": ip_address,
            "error": str(e),
            "reachable": False
        }
