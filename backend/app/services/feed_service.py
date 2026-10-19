"""Serviço de feed (atividades de quem o usuário segue + próprias)."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.services.follow_service import following_ids_subquery


async def get_feed(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[Activity]:
    """Retorna atividades do próprio user + de quem ele segue, mais recentes primeiro."""
    stmt = (
        select(Activity)
        .where(
            or_(
                Activity.user_id == user_id,
                Activity.user_id.in_(following_ids_subquery(user_id)),
            )
        )
        .options(selectinload(Activity.user))  # carrega o autor junto
        .order_by(Activity.started_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())