"""Endpoints de atividades (CRUD, estatísticas, curtidas)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
)
from app.schemas.like import LikeListResponse, LikeStateResponse
from app.schemas.stats import (
    StatsMonthlyResponse,
    StatsSummary,
    StatsWeeklyResponse,
)
from app.services import activity_service, like_service, stats_service
from app.services.errors import ServiceError

router = APIRouter()


# ===== Estatísticas (declaradas ANTES das rotas dinâmicas /{activity_id}) =====

@router.get("/stats/summary", response_model=StatsSummary)
async def stats_summary(
    activity_type: str | None = Query(default=None, description="Filtro opcional por tipo"),
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


# ===== CRUD =====

@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    payload: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria uma nova atividade para o usuário autenticado."""
    return await activity_service.create_activity(db, current_user.id, payload)


@router.get("", response_model=list[ActivityResponse])
async def list_activities(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista atividades do usuário autenticado (paginado)."""
    return await activity_service.list_activities(db, current_user.id, limit, offset)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna detalhes de uma atividade do usuário autenticado."""
    try:
        return await activity_service.get_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove uma atividade do usuário autenticado."""
    try:
        await activity_service.delete_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


# ===== Curtidas =====

@router.post("/{activity_id}/like", response_model=LikeStateResponse)
async def like_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Curte uma atividade (idempotente). Retorna o estado atual."""
    try:
        return await like_service.like_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{activity_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove curtida (idempotente)."""
    try:
        await like_service.unlike_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/{activity_id}/likes", response_model=LikeListResponse)
async def list_likes(
    activity_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista quem curtiu + contagem + flag do user atual."""
    try:
        return await like_service.get_likes(
            db, current_user.id, activity_id, limit, offset
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)