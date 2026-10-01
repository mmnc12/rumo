import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import Activity, User
from app.schemas import ActivityCreate, ActivityListResponse, ActivityResponse
from app.services import activity_service
from app.schemas.stats import (
    StatsSummary,
    StatsWeeklyResponse,
    StatsMonthlyResponse,
)
from app.services import stats_service

router = APIRouter(prefix="/activities", tags=["Atividades"])


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra uma nova atividade",
)
async def create(
    payload: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria uma atividade para o usuário autenticado."""
    activity = await activity_service.create_activity(db, current_user.id, payload)
    return activity


@router.get(
    "",
    response_model=ActivityListResponse,
    summary="Lista atividades do usuário autenticado (paginado)",
)
async def list_mine(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna as atividades do usuário logado, mais recentes primeiro."""
    items, total = await activity_service.list_user_activities(
        db, current_user.id, limit=limit, offset=offset
    )
    return ActivityListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/stats/summary", response_model=StatsSummary)
async def stats_summary(
    activity_type: str | None = Query(
        default=None, description="Filtro opcional por tipo"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Totais gerais das atividades do usuário."""
    return await stats_service.get_summary(db, current_user.id, activity_type)


@router.get("/stats/weekly", response_model=StatsWeeklyResponse)
async def stats_weekly(
    weeks: int = Query(default=8, ge=1, le=52, description="Número de semanas"),
    activity_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo das últimas N semanas."""
    items = await stats_service.get_period_stats(
        db, current_user.id, "week", weeks, activity_type
    )
    return {"weeks": weeks, "items": items}


@router.get("/stats/monthly", response_model=StatsMonthlyResponse)
async def stats_monthly(
    months: int = Query(default=6, ge=1, le=24, description="Número de meses"),
    activity_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo dos últimos N meses."""
    items = await stats_service.get_period_stats(
        db, current_user.id, "month", months, activity_type
    )
    return {"months": months, "items": items}


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Detalhes de uma atividade",
)
async def get_one(
    activity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna os detalhes de uma atividade do usuário autenticado."""
    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == current_user.id,
        )
    )
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada",
        )
    return activity


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma atividade",
)
async def delete(
    activity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove uma atividade do usuário autenticado."""
    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == current_user.id,
        )
    )
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada",
        )

    await db.delete(activity)
    await db.commit()
    return None
