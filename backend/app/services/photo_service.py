import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.activity_photo import ActivityPhoto
from app.models.user import User

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
FOLDER = "rumo/activities"


async def _get_owned_activity(
    db: AsyncSession, activity_id, current_user: User
) -> Activity:
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada")
    if activity.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sem permissão")
    return activity


async def upload_photo(
    db: AsyncSession,
    activity_id,
    file: UploadFile,
    current_user: User,
) -> ActivityPhoto:
    await _get_owned_activity(db, activity_id, current_user)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Tipo de arquivo inválido. Use JPEG, PNG ou WebP.",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Arquivo maior que 10 MB.",
        )
    if not contents:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Arquivo vazio.")

    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=f"{FOLDER}/{activity_id}",
            resource_type="image",
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Falha no upload para o Cloudinary: {exc}",
        ) from exc

    photo = ActivityPhoto(
        activity_id=activity_id,
        url=result["secure_url"],
        public_id=result["public_id"],
        width=result.get("width"),
        height=result.get("height"),
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def list_photos(db: AsyncSession, activity_id) -> list[ActivityPhoto]:
    result = await db.execute(
        select(ActivityPhoto)
        .where(ActivityPhoto.activity_id == activity_id)
        .order_by(ActivityPhoto.created_at)
    )
    return list(result.scalars().all())


async def delete_photo(
    db: AsyncSession, photo_id, current_user: User
) -> None:
    result = await db.execute(
        select(ActivityPhoto).where(ActivityPhoto.id == photo_id)
    )
    photo = result.scalar_one_or_none()
    if photo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto não encontrada")

    activity_result = await db.execute(
        select(Activity).where(Activity.id == photo.activity_id)
    )
    activity = activity_result.scalar_one()
    if activity.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sem permissão")

    try:
        cloudinary.uploader.destroy(photo.public_id)
    except Exception:  # noqa: BLE001
        pass  # se falhar no Cloudinary, ainda removemos do banco

    await db.delete(photo)
    await db.commit()