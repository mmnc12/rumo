"""Serviço de relações de seguidores (follow/unfollow)."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follow
from app.models.user import User
from app.services.errors import BadRequestError, ConflictError, NotFoundError


async def _get_user_or_404(db: AsyncSession, user_id: UUID) -> User:
    """Busca usuário por id ou levanta NotFoundError."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("User not found")
    return user


async def follow_user(
    db: AsyncSession, follower_id: UUID, following_id: UUID
) -> None:
    """Cria relação de follow. Levanta ServiceError em caso de conflito."""
    if follower_id == following_id:
        raise BadRequestError("Cannot follow yourself")

    await _get_user_or_404(db, following_id)

    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictError("Already following this user")


async def unfollow_user(
    db: AsyncSession, follower_id: UUID, following_id: UUID
) -> None:
    """Remove relação de follow. Levanta NotFoundError se não existia."""
    stmt = delete(Follow).where(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id,
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise NotFoundError("Not following this user")


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