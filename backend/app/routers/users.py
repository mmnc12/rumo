"""Endpoints de usuários (perfil público, follows, busca)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserPublic
from app.services import follow_service, user_service
from app.services.errors import ServiceError

router = APIRouter()


def _handle_service_error(exc: ServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/search", response_model=list[UserPublic])
async def search_users(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Busca usuários por username ou nome (case-insensitive).

    IMPORTANTE: rota estática `/search` declarada ANTES de `/{user_id}`,
    senão o FastAPI tenta parsear "search" como UUID e retorna 422.
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