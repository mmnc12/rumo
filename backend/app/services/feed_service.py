"""Serviço de feed (atividades de quem o usuário segue + próprias)."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.follow import Follow


async def get_feed(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[Activity]:
    """Retorna atividades do próprio user + de quem ele segue, mais recentes primeiro."""
    # Subquery: ids de quem eu sigo
    following_subq = (
        select(Follow.following_id).where(Follow.follower_id == user_id).scalar_subquery()
    )

    stmt = (
        select(Activity)
        .where(
            or_(
                Activity.user_id == user_id,
                Activity.user_id.in_(following_subq),
            )
        )
        .options(selectinload(Activity.user))  # carrega o autor junto
        .order_by(Activity.started_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())