from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.database import ConfigLog, Router, ConfigStatus
from app.models.schemas import ConfigLogResponse
from app.models.db_session import get_db

router = APIRouter(prefix="/api", tags=["Logs"])


@router.get("/logs", response_model=List[ConfigLogResponse])
async def list_logs(
    skip: int = 0,
    limit: int = 50,
    config_type: Optional[str] = None,
    status: Optional[ConfigStatus] = None,
    router_id: Optional[int] = None,
    days: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ConfigLog)

    if router_id:
        query = query.where(ConfigLog.router_id == router_id)
    if config_type:
        query = query.where(ConfigLog.config_type == config_type)
    if status:
        query = query.where(ConfigLog.status == status)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.where(ConfigLog.created_at >= cutoff)

    query = query.order_by(ConfigLog.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/routers/{router_id}/logs", response_model=List[ConfigLogResponse])
async def list_router_logs(
    router_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ConfigLog)
        .where(ConfigLog.router_id == router_id)
        .order_by(ConfigLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/logs/{log_id}", response_model=ConfigLogResponse)
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ConfigLog).where(ConfigLog.id == log_id))
    log_obj = result.scalar_one_or_none()
    if not log_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log {log_id} not found"
        )
    return log_obj


@router.get("/stats/summary")
async def get_stats_summary(
    db: AsyncSession = Depends(get_db)
):
    total_routers_result = await db.execute(select(Router))
    total_routers = len(total_routers_result.scalars().all())

    active_routers_result = await db.execute(
        select(Router).where(Router.status == "active")
    )
    active_routers = len(active_routers_result.scalars().all())

    recent_logs_result = await db.execute(
        select(ConfigLog).where(
            ConfigLog.created_at >= datetime.utcnow() - timedelta(days=7)
        )
    )
    recent_logs = recent_logs_result.scalars().all()

    success_logs = [log for log in recent_logs if log.status == ConfigStatus.SUCCESS]
    failed_logs = [log for log in recent_logs if log.status == ConfigStatus.FAILED]

    return {
        "total_routers": total_routers,
        "active_routers": active_routers,
        "inactive_routers": total_routers - active_routers,
        "recent_configs": len(recent_logs),
        "successful_configs": len(success_logs),
        "failed_configs": len(failed_logs),
        "period_days": 7
    }
