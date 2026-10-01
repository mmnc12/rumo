"""Endpoint de feed (atividades próprias + de quem o usuário segue)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.activity import FeedItemResponse
from app.services import feed_service

router = APIRouter()


@router.get("", response_model=list[FeedItemResponse])
async def get_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Feed do usuário: atividades próprias + de quem ele segue."""
    return await feed_service.get_feed(db, current_user.id, limit, offset)