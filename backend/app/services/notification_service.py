import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.notification import Notification, NotificationType


async def create_notification(
    db: AsyncSession,
    *,
    recipient_id: uuid.UUID,
    actor_id: uuid.UUID,
    type: NotificationType,
    activity_id: uuid.UUID | None = None,
    comment_id: uuid.UUID | None = None,
) -> Notification | None:
    """Cria notificação. Retorna None se for auto-ação (skip silencioso)."""
    if recipient_id == actor_id:
        return None

    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=type.value,
        activity_id=activity_id,
        comment_id=comment_id,
    )
    db.add(notification)
    # NÃO commita aqui — o caller (service de origem) já está numa transação.
    return notification


async def list_notifications(
    db: AsyncSession,
    *,
    recipient_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.recipient_id == recipient_id)
        .options(
            selectinload(Notification.actor),
            selectinload(Notification.activity),
        )
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def count_unread(db: AsyncSession, *, recipient_id: uuid.UUID) -> int:
    from sqlalchemy import func

    stmt = select(func.count()).select_from(Notification).where(
        Notification.recipient_id == recipient_id,
        Notification.is_read.is_(False),
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def mark_read(
    db: AsyncSession, *, notification_id: uuid.UUID, recipient_id: uuid.UUID
) -> bool:
    """Marca uma como lida. Retorna False se não achou ou não é do recipient."""
    stmt = (
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.recipient_id == recipient_id,
        )
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def mark_all_read(db: AsyncSession, *, recipient_id: uuid.UUID) -> int:
    stmt = (
        update(Notification)
        .where(
            Notification.recipient_id == recipient_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount