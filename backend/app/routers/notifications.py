"""Endpoints de notificações in-app."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.notification import (
    MarkAllReadResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    notifications = await notification_service.list_notifications(
        db, recipient_id=current_user.id, limit=limit, offset=offset
    )
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnreadCountResponse:
    count = await notification_service.count_unread(
        db, recipient_id=current_user.id
    )
    return UnreadCountResponse(count=count)


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    ok = await notification_service.mark_read(
        db, notification_id=notification_id, recipient_id=current_user.id
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )


@router.post("/read-all", response_model=MarkAllReadResponse)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarkAllReadResponse:
    updated = await notification_service.mark_all_read(
        db, recipient_id=current_user.id
    )
    return MarkAllReadResponse(updated=updated)