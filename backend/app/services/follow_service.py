"""Serviço de relações de seguidores (follow/unfollow)."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follow
from app.models.user import User


class FollowError(Exception):
    """Erro de negócio em operações de follow."""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def _get_user_or_404(db: AsyncSession, user_id: UUID) -> User:
    """Busca usuário por id ou levanta FollowError 404."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise FollowError("User not found", status_code=404)
    return user


async def follow_user(
    db: AsyncSession, follower_id: UUID, following_id: UUID
) -> None:
    """Cria relação de follow. Levanta FollowError em caso de conflito."""
    if follower_id == following_id:
        raise FollowError("Cannot follow yourself", status_code=400)

    await _get_user_or_404(db, following_id)

    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise FollowError("Already following this user", status_code=409)


async def unfollow_user(
    db: AsyncSession, follower_id: UUID, following_id: UUID
) -> None:
    """Remove relação de follow. Levanta FollowError 404 se não existia."""
    stmt = delete(Follow).where(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id,
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise FollowError("Not following this user", status_code=404)


async def get_followers(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[User]:
    """Lista usuários que seguem `user_id`."""
    await _get_user_or_404(db, user_id)

    stmt = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .order_by(Follow.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_following(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[User]:
    """Lista usuários que `user_id` segue."""
    await _get_user_or_404(db, user_id)

    stmt = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .order_by(Follow.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())