"""Service de comentários."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.comment import Comment
from app.services.errors import ForbiddenError, NotFoundError


async def _ensure_activity_exists(db: AsyncSession, activity_id: UUID) -> None:
    result = await db.execute(
        select(Activity.id).where(Activity.id == activity_id)
    )
    if result.scalar_one_or_none() is None:
        raise NotFoundError("Atividade não encontrada")


async def create_comment(
    db: AsyncSession, user_id: UUID, activity_id: UUID, content: str
) -> Comment:
    await _ensure_activity_exists(db, activity_id)

    comment = Comment(user_id=user_id, activity_id=activity_id, content=content)
    db.add(comment)
    await db.commit()

    # recarrega com o user carregado (evita MissingGreenlet no schema)
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment.id)
    )
    return result.scalar_one()


async def list_comments(
    db: AsyncSession, activity_id: UUID, limit: int, offset: int
) -> list[Comment]:
    await _ensure_activity_exists(db, activity_id)

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.activity_id == activity_id)
        .order_by(Comment.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_comment(
    db: AsyncSession, user_id: UUID, comment_id: UUID
) -> None:
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise NotFoundError("Comentário não encontrado")

    if comment.user_id != user_id:
        raise ForbiddenError("Você só pode deletar seus próprios comentários")

    await db.delete(comment)
    await db.commit()