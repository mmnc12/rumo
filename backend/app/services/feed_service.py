"""Serviço de feed (atividades de quem o usuário segue + próprias)."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.services.activity_service import (
    _attach_counts,
    _bbox_columns,
    _bbox_from_row,
    _count_comments_subq,
    _count_likes_subq,
    _liked_by_me_subq,
)
from app.services.follow_service import following_ids_subquery


async def get_feed(
    db: AsyncSession, user_id: UUID, limit: int, offset: int
) -> list[Activity]:
    """Retorna atividades do próprio user + de quem ele segue, mais recentes primeiro.

    Embute likes_count / comments_count / liked_by_me e bbox via subqueries
    correlacionadas e funções PostGIS — evita N+1 no cliente (o app mobile
    não precisa fazer requests extras por card, e o card do feed consegue
    desenhar a miniatura do mapa só com o bbox).

    [Sessão 10] Reutiliza os helpers do activity_service para que a regra
    de "quais colunas compõem um ActivityResponse" fique em UM lugar só.
    """
    likes_sq = _count_likes_subq().label("likes_count")
    comments_sq = _count_comments_subq().label("comments_count")
    liked_sq = _liked_by_me_subq(user_id).label("liked_by_me_raw")
    bbox_cols = _bbox_columns()

    stmt = (
        select(Activity, likes_sq, comments_sq, liked_sq, *bbox_cols)
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
    for activity, likes, comments, liked, *bbox_raw in result.all():
        bbox = _bbox_from_row(*bbox_raw)
        activities.append(_attach_counts(activity, likes, comments, liked, bbox))
    return activities