"""Service de fotos de atividades (Cloudinary + denormalizados na Activity)."""

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.activity_photo import ActivityPhoto
from app.models.user import User
from app.services import activity_service

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
FOLDER = "rumo/activities"


async def _get_owned_activity(
    db: AsyncSession, activity_id, current_user: User
) -> Activity:
    """Busca a atividade e exige que o usuário seja o DONO (escrita).

    Usado só em upload/delete — operações de escrita. Diferente da
    listagem, que usa a regra social (dono OU seguidor) via
    `activity_service.get_activity(..., allow_following=True)`.

    Mantém 403 aqui (semântica de escrita: "existe, você não é o dono").
    A listagem usa 404 pra não vazar existência — ver `list_photos`.
    """
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada")
    if activity.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sem permissão")
    return activity


async def _recalc_cover_and_count(
    db: AsyncSession, activity: Activity
) -> None:
    """
    Recalcula cover_photo_url e photo_count a partir da tabela activity_photos.

    Fonte da verdade é a tabela; os campos denormalizados só espelham.
    Usado no delete (quando a capa pode mudar) e como fallback de segurança.
    """
    result = await db.execute(
        select(ActivityPhoto)
        .where(ActivityPhoto.activity_id == activity.id)
        .order_by(ActivityPhoto.created_at)
    )
    photos = list(result.scalars().all())
    activity.photo_count = len(photos)
    activity.cover_photo_url = photos[0].url if photos else None


async def upload_photo(
    db: AsyncSession,
    activity_id,
    file: UploadFile,
    current_user: User,
) -> ActivityPhoto:
    activity = await _get_owned_activity(db, activity_id, current_user)

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

    # Sincroniza denormalizados. Se é a primeira foto, vira capa.
    if activity.photo_count == 0 or activity.cover_photo_url is None:
        activity.cover_photo_url = photo.url
    activity.photo_count = (activity.photo_count or 0) + 1

    await db.commit()
    await db.refresh(photo)
    return photo


async def list_photos(
    db: AsyncSession,
    activity_id,
    user_id,
) -> list[ActivityPhoto]:
    """
    Lista as fotos de uma atividade.

    Regra de visibilidade: dono OU seguidor do dono — mesma regra do
    feed e do GET /activities/{id} (fonte de verdade: `following_ids_subquery`
    via `activity_service.get_activity`).

    Reusa `get_activity(..., allow_following=True)` em vez de duplicar a
    checagem: garante uma regra só no app e devolve `NotFoundError` (404)
    quando não autorizado — mesmo padrão do detalhe/track, não vaza
    existência da atividade pra quem não é dono nem seguidor.

    Custo: 1 SELECT extra na `activities` (indexada por id) + o join
    do selectinload. Desprezível — não otimizar prematuramente.
    """
    # Confirma existência + permissão. Levanta NotFoundError (404 no router)
    # tanto pra "não existe" quanto pra "existe mas você não pode ver".
    await activity_service.get_activity(
        db, user_id, activity_id, allow_following=True
    )

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
    await db.flush()  # aplica o DELETE antes de recalcular

    # Recalcula a partir da tabela (fonte da verdade).
    # Custo: 1 SELECT na tabela de fotos da atividade — aceitável.
    await _recalc_cover_and_count(db, activity)

    await db.commit()