"""Endpoints de usuários (perfil público, follows, busca, stats públicas)."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.user import User
from app.schemas.stats import (
    StatsByTypeResponse,
    StatsMonthlyResponse,
    StatsSummary,
    StatsWeeklyResponse,
)
from app.schemas.user import UserPublic
from app.services import follow_service, stats_service, user_service
from app.services.errors import ServiceError

router = APIRouter()


def _handle_service_error(exc: ServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


# [Sessão 19] Regra de visibilidade das stats de terceiros.
# Mesma regra do /activities/{id}/track e do feed: dono OU seguidor do dono.
# O próprio usuário sempre pode ver as próprias stats (sem consulta extra).
async def _ensure_can_view_stats(
    db: AsyncSession, viewer_id: UUID, target_id: UUID
) -> None:
    """Levanta 404 (target inexistente) ou 403 (viewer não segue target)."""
    if viewer_id == target_id:
        return

    # 404 para target inexistente — não vaza existência vs. permissão.
    target = await db.get(User, target_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    allowed = await follow_service.is_following(db, viewer_id, target_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você precisa seguir este usuário pra ver as estatísticas dele",
        )


@router.get("/search", response_model=list[UserPublic])
@limiter.limit("20/minute")
async def search_users(
    request: Request,
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Busca usuários por username ou nome (case-insensitive).

    IMPORTANTE: rota estática `/search` declarada ANTES de `/{user_id}`,
    senão o FastAPI tenta parsear "search" como UUID e retorna 422.

    Rate limit: 20/minuto por IP — a busca faz full scan ILIKE em
    username + full_name (sem índice pg_trgm ainda), então um scraper
    derruba o Neon free tier. 20/min cobre uso legítimo do SearchPage
    (debounce 300ms + staleTime 30s) e barra varredura em massa.
    """
    try:
        return await user_service.search_users(db, q, current_user.id, limit)
    except ServiceError as exc:
        raise _handle_service_error(exc)


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Segue um usuário."""
    try:
        await follow_service.follow_user(db, current_user.id, user_id)
    except ServiceError as exc:
        raise _handle_service_error(exc)


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deixa de seguir um usuário."""
    try:
        await follow_service.unfollow_user(db, current_user.id, user_id)
    except ServiceError as exc:
        raise _handle_service_error(exc)


@router.get("/{user_id}/followers", response_model=list[UserPublic])
async def list_followers(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista seguidores de um usuário."""
    try:
        return await follow_service.get_followers(db, user_id, limit, offset)
    except ServiceError as exc:
        raise _handle_service_error(exc)


@router.get("/{user_id}/following", response_model=list[UserPublic])
async def list_following(
    user_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista usuários que um usuário segue."""
    try:
        return await follow_service.get_following(db, user_id, limit, offset)
    except ServiceError as exc:
        raise _handle_service_error(exc)


# ===== Stats públicas [Sessão 19] =====
# Espelham /activities/stats/*, mas aceitam `user_id` de terceiros.
# Visibilidade: dono OU seguidor do dono (mesma regra do /track).
# Declaradas ANTES de @router.get("/{user_id}") — senão o FastAPI tenta
# parsear "stats" como UUID e retorna 422.
#
# O service é o MESMO de /activities/stats/* (recebe user_id como 1º
# param depois de `db`). Nenhuma assinatura muda, zero duplicação de SQL.


@router.get("/{user_id}/stats/summary", response_model=StatsSummary)
async def get_user_stats_summary(
    user_id: UUID,
    activity_type: str | None = Query(default=None, description="Filtro opcional por tipo"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Totais gerais das atividades de um usuário (dono ou seguido)."""
    await _ensure_can_view_stats(db, current_user.id, user_id)
    return await stats_service.get_summary(db, user_id, activity_type)


@router.get("/{user_id}/stats/weekly", response_model=StatsWeeklyResponse)
async def get_user_stats_weekly(
    user_id: UUID,
    weeks: int = Query(default=8, ge=1, le=52, description="Número de semanas"),
    activity_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo das últimas N semanas de um usuário (dono ou seguido)."""
    await _ensure_can_view_stats(db, current_user.id, user_id)
    items = await stats_service.get_period_stats(db, user_id, "week", weeks, activity_type)
    return {"weeks": weeks, "items": items}


@router.get("/{user_id}/stats/monthly", response_model=StatsMonthlyResponse)
async def get_user_stats_monthly(
    user_id: UUID,
    months: int = Query(default=6, ge=1, le=24, description="Número de meses"),
    activity_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo dos últimos N meses de um usuário (dono ou seguido)."""
    await _ensure_can_view_stats(db, current_user.id, user_id)
    items = await stats_service.get_period_stats(db, user_id, "month", months, activity_type)
    return {"months": months, "items": items}


# [Sessão 20] Adicionado param `compare` (prev|yoy) — janela de comparação.
@router.get("/{user_id}/stats/by-type", response_model=StatsByTypeResponse)
async def get_user_stats_by_type(
    user_id: UUID,
    period: Literal["all", "90d", "1y"] = Query(
        default="all",
        description="Janela temporal: 'all' (todos os tempos), '90d' (últimos 90 dias) ou '1y' (últimos 365 dias)",
    ),
    compare: Literal["prev", "yoy"] = Query(
        default="prev",
        description=(
            "Janela de comparação para `previous`: 'prev' (imediatamente "
            "anterior, default) ou 'yoy' (mesmo período do ano anterior). "
            "Só tem efeito quando period != 'all'."
        ),
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Drill-down por tipo de um usuário (dono ou seguido).

    Mesma semântica de /activities/stats/by-type: `previous` (comparação
    com a janela imediatamente anterior) vem preenchido para 90d/1y e
    `null` para all.

    [Sessão 20] `compare` escolhe a janela de comparação:
    - `prev` (default): janela imediatamente anterior (S18).
    - `yoy`: mesmo período do ano anterior.
    """
    await _ensure_can_view_stats(db, current_user.id, user_id)
    items = await stats_service.get_by_type(db, user_id, period, compare)
    return {"items": items}


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retorna o perfil público de qualquer usuário autenticado."""
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    return user