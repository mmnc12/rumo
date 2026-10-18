from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.photo import ActivityPhotoResponse
from app.services import photo_service

router = APIRouter(tags=["photos"])


@router.post(
    "/activities/{activity_id}/photos",
    response_model=ActivityPhotoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    activity_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await photo_service.upload_photo(db, activity_id, file, current_user)


@router.get(
    "/activities/{activity_id}/photos",
    response_model=list[ActivityPhotoResponse],
)
async def list_photos(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await photo_service.list_photos(db, activity_id)


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await photo_service.delete_photo(db, photo_id, current_user)
    return None