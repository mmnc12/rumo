"""Endpoints de fotos de atividades (upload, listagem, delete)."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.user import User
from app.schemas.photo import ActivityPhotoResponse
from app.services import photo_service
from app.services.errors import ServiceError

router = APIRouter(tags=["photos"])


@router.post(
    "/activities/{activity_id}/photos",
    response_model=ActivityPhotoResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/hour")
async def upload_photo(
    request: Request,
    activity_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sobe uma foto para uma atividade (só o dono).

    Rate limit: 20/hora por IP — o upload é síncrono (bloqueia o event
    loop ~1–3s) e o Cloudinary free tier tem 25 créditos/mês. 20/hora
    permite subir um álbum de uma atividade sem bloqueio e barra
    automação que esgotaria os créditos em minutos.
    """
    return await photo_service.upload_photo(db, activity_id, file, current_user)


@router.get(
    "/activities/{activity_id}/photos",
    response_model=list[ActivityPhotoResponse],
)
async def list_photos(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista as fotos de uma atividade.

    Visibilidade: dono OU seguidor do dono — mesma regra do feed e do
    GET /activities/{id}. Quem não é dono nem seguidor recebe 404
    (não vaza existência da atividade), consistente com o detalhe/track.
    """
    try:
        return await photo_service.list_photos(db, activity_id, current_user.id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove uma foto (só o dono da atividade)."""
    await photo_service.delete_photo(db, photo_id, current_user)
    return None