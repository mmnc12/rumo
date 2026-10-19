"""Schemas de notificação."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserPublic


class ActivityPreview(BaseModel):
    """Preview mínimo da atividade pra notificação (não expõe geometria)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    activity_type: str


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    is_read: bool
    created_at: datetime
    actor: UserPublic
    activity: ActivityPreview | None = None
    comment_id: UUID | None = None


class UnreadCountResponse(BaseModel):
    count: int


class MarkAllReadResponse(BaseModel):
    updated: int