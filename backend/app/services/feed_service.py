"""Serviço de feed (atividades de quem o usuário segue + próprias)."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.comment import Comment
from app.models.like import Like
from app.services.follow_service import following_ids_subquery


async def get_feed(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[Activity]:
    """Retorna atividades do próprio user + de quem ele segue, mais recentes primeiro.

    Embutе likes_count / comments_count / liked_by_me via subqueries
    correlacionadas — evita N+1 no cliente (o app mobile não precisa
    fazer 3 requests por card).
    """
    likes_sq = (
        select(func.count(Like.id))
        .where(Like.activity_id == Activity.id)
        .correlate(Activity)
        .scalar_subquery()
        .label("likes_count")
    )
    comments_sq = (
        select(func.count(Comment.id))
        .where(Comment.activity_id == Activity.id)
        .correlate(Activity)
        .scalar_subquery()
        .label("comments_count")
    )
    liked_sq = (
        select(func.count(Like.id))
        .where(
            Like.activity_id == Activity.id,
            Like.user_id == user_id,
        )
        .correlate(Activity)
        .scalar_subquery()
        .label("liked_by_me_raw")
    )

    stmt = (
        select(Activity, likes_sq, comments_sq, liked_sq)
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

    activities: list[Activity] = []
    for activity, likes, comments, liked in result.all():
        activity.likes_count = int(likes or 0)
        activity.comments_count = int(comments or 0)
        activity.liked_by_me = bool(liked and int(liked) > 0)
        activities.append(activity)
    return activities