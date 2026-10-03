"""Router de comentários."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import comment_service
from app.services.errors import ServiceError

router = APIRouter()


def _to_http(exc: ServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post(
    "/activities/{activity_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    activity_id: UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await comment_service.create_comment(
            db, current_user.id, activity_id, payload.content
        )
    except ServiceError as exc:
        raise _to_http(exc)


@router.get(
    "/activities/{activity_id}/comments",
    response_model=list[CommentResponse],
)
async def list_comments(
    activity_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await comment_service.list_comments(db, activity_id, limit, offset)
    except ServiceError as exc:
        raise _to_http(exc)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await comment_service.delete_comment(db, current_user.id, comment_id)
    except ServiceError as exc:
        raise _to_http(exc)