"""Schemas de curtidas em atividades."""

from pydantic import BaseModel

from app.schemas.user import UserPublic


class LikeStateResponse(BaseModel):
    """Estado atual de curtidas de uma atividade."""

    count: int
    liked_by_me: bool


class LikeListResponse(BaseModel):
    """Lista paginada de quem curtiu."""

    count: int
    liked_by_me: bool
    users: list[UserPublic]