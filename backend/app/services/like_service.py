"""Serviço de curtidas em atividades."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.like import Like
from app.models.notification import NotificationType
from app.models.user import User
from app.services import notification_service
from app.services.errors import NotFoundError


async def _get_activity_owner(db: AsyncSession, activity_id: UUID) -> UUID:
    """Retorna o user_id do dono da atividade. Levanta NotFoundError se não existe."""
    result = await db.execute(
        select(Activity.user_id).where(Activity.id == activity_id)
    )
    owner_id = result.scalar_one_or_none()
    if owner_id is None:
        raise NotFoundError("Activity not found")
    return owner_id


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
    """Curte uma atividade (idempotente). Retorna estado atual.

    Cria notificação só no primeiro like (não no replay idempotente).
    """
    owner_id = await _get_activity_owner(db, activity_id)

    like = Like(user_id=user_id, activity_id=activity_id)
    db.add(like)

    try:
        # flush força o INSERT — se for duplicado, estoura IntegrityError aqui
        # antes de criarmos a notificação. Commit único preserva atomicidade.
        await db.flush()
    except IntegrityError:
        await db.rollback()  # já curtia — idempotente, sem notificação
        return {
            "count": await _get_like_count(db, activity_id),
            "liked_by_me": True,
        }

    await notification_service.create_notification(
        db,
        recipient_id=owner_id,
        actor_id=user_id,
        type=NotificationType.LIKE,
        activity_id=activity_id,
    )
    await db.commit()

    return {
        "count": await _get_like_count(db, activity_id),
        "liked_by_me": True,
    }


async def unlike_activity(
    db: AsyncSession, user_id: UUID, activity_id: UUID
) -> None:
    """Remove curtida (idempotente)."""
    await _get_activity_owner(db, activity_id)  # só valida existência

    stmt = delete(Like).where(
        Like.user_id == user_id, Like.activity_id == activity_id
    )
    await db.execute(stmt)
    await db.commit()


async def get_likes(
    db: AsyncSession, user_id: UUID, activity_id: UUID, limit: int, offset: int
) -> dict:
    """Lista quem curtiu + contagem + flag do user atual."""
    await _get_activity_owner(db, activity_id)

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