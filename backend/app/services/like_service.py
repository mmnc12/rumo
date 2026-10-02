"""Serviço de curtidas em atividades."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.like import Like
from app.models.user import User
from app.services.errors import NotFoundError


async def _ensure_activity_exists(db: AsyncSession, activity_id: UUID) -> None:
    """Levanta NotFoundError se a atividade não existe."""
    result = await db.execute(select(Activity.id).where(Activity.id == activity_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundError("Activity not found")


async def _get_like_count(db: AsyncSession, activity_id: UUID) -> int:
    """Conta curtidas de uma atividade."""
    stmt = select(func.count(Like.id)).where(Like.activity_id == activity_id)
    result = await db.execute(stmt)
    return int(result.scalar_one() or 0)


async def _has_liked(db: AsyncSession, user_id: UUID, activity_id: UUID) -> bool:
    """Verifica se o usuário já curtiu a atividade."""
    stmt = select(Like.id).where(
        Like.user_id == user_id, Like.activity_id == activity_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def like_activity(
    db: AsyncSession, user_id: UUID, activity_id: UUID
) -> dict:
    """Curte uma atividade (idempotente). Retorna estado atual."""
    await _ensure_activity_exists(db, activity_id)

    like = Like(user_id=user_id, activity_id=activity_id)
    db.add(like)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()  # já curtia — segue, é idempotente

    return {
        "count": await _get_like_count(db, activity_id),
        "liked_by_me": True,
    }


async def unlike_activity(
    db: AsyncSession, user_id: UUID, activity_id: UUID
) -> None:
    """Remove curtida (idempotente)."""
    await _ensure_activity_exists(db, activity_id)

    stmt = delete(Like).where(
        Like.user_id == user_id, Like.activity_id == activity_id
    )
    await db.execute(stmt)
    await db.commit()


async def get_likes(
    db: AsyncSession, user_id: UUID, activity_id: UUID, limit: int, offset: int
) -> dict:
    """Lista quem curtiu + contagem + flag do user atual."""
    await _ensure_activity_exists(db, activity_id)

    count = await _get_like_count(db, activity_id)
    liked = await _has_liked(db, user_id, activity_id)

    stmt = (
        select(User)
        .join(Like, Like.user_id == User.id)
        .where(Like.activity_id == activity_id)
        .order_by(Like.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    users = list(result.scalars().all())

    return {"count": count, "liked_by_me": liked, "users": users}