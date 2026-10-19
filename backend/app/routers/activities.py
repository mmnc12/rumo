"""Endpoints de atividades (CRUD, estatísticas, curtidas, upload, track)."""

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.user import User
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
    TrackResponse,
)
from app.schemas.like import LikeListResponse, LikeStateResponse
from app.schemas.stats import (
    StatsMonthlyResponse,
    StatsSummary,
    StatsWeeklyResponse,
)
from app.services import activity_service, like_service, stats_service
from app.services.errors import ServiceError
from app.services.follow_service import is_following

router = APIRouter()


# ===== Estatísticas (declaradas ANTES das rotas dinâmicas /{activity_id}) =====

@router.get("/stats/summary", response_model=StatsSummary)
async def stats_summary(
    activity_type: str | None = Query(default=None, description="Filtro opcional por tipo"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Totais gerais das atividades do usuário."""
    return await stats_service.get_summary(db, current_user.id, activity_type)


@router.get("/stats/weekly", response_model=StatsWeeklyResponse)
async def stats_weekly(
    weeks: int = Query(default=8, ge=1, le=52, description="Número de semanas"),
    activity_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo das últimas N semanas."""
    items = await stats_service.get_period_stats(
        db, current_user.id, "week", weeks, activity_type
    )
    return {"weeks": weeks, "items": items}


@router.get("/stats/monthly", response_model=StatsMonthlyResponse)
async def stats_monthly(
    months: int = Query(default=6, ge=1, le=24, description="Número de meses"),
    activity_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resumo dos últimos N meses."""
    items = await stats_service.get_period_stats(
        db, current_user.id, "month", months, activity_type
    )
    return {"months": months, "items": items}


# ===== CRUD =====

@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def create_activity(
    request: Request,
    payload: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria uma nova atividade (JSON pré-calculado, com track_points opcional).

    Rate limit: 10/hora por IP — escrita pesada no Neon free tier
    (insert de atividade + possível insert em lote de track_points).
    """
    return await activity_service.create_activity(db, current_user.id, payload)


@router.post(
    "/upload",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/hour")
async def upload_activity(
    request: Request,
    file: UploadFile = File(..., description="Arquivo .gpx"),
    title: str | None = Form(None, max_length=120),
    activity_type: str | None = Form(None),
    description: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cria uma atividade a partir de um arquivo GPX.

    O backend parseia o arquivo, calcula distância, pace, elevação
    e preenche rota (PostGIS) + raw_track_points automaticamente.

    Rate limit: 10/hora por IP — parse de GPX é síncrono e bloqueia o
    event loop; 10/hora cobre uso legítimo (algumas atividades por dia)
    e barra loop de upload que derrubaria o Render free tier.
    """
    if not file.filename or not file.filename.lower().endswith(".gpx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado. Envie um arquivo .gpx",
        )

    file_bytes = await file.read()

    try:
        return await activity_service.create_activity_from_gpx(
            db=db,
            user_id=current_user.id,
            file_bytes=file_bytes,
            title=title,
            activity_type=activity_type,
            description=description,
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("", response_model=list[ActivityResponse])
async def list_activities(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: UUID | None = Query(
        default=None,
        description="Filtra atividades de outro usuário (requer seguir)",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista atividades (paginado).

    - Sem `user_id`: lista as do usuário autenticado.
    - Com `user_id` igual ao próprio: lista as do usuário autenticado.
    - Com `user_id` de outro: só se o autenticado seguir esse usuário (senão 403).
    """
    target_id = user_id or current_user.id

    if target_id != current_user.id:
        allowed = await is_following(db, current_user.id, target_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você precisa seguir este usuário pra ver as atividades dele",
            )

    return await activity_service.list_activities(db, target_id, limit, offset)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna detalhes de uma atividade.

    Acessível pelo dono OU por quem segue o dono (mesma regra do feed).
    Quem não é dono nem seguidor recebe 404 (não vaza existência).
    """
    try:
        return await activity_service.get_activity(
            db, current_user.id, activity_id, allow_following=True
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/{activity_id}/track", response_model=TrackResponse)
async def get_activity_track(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna a geometria da rota (GeoJSON-like) da atividade.

    Acessível pelo dono OU por quem segue o dono.
    Não inclui raw_track_points — apenas a geometria da rota pro mapa.
    """
    try:
        return await activity_service.get_activity_track(
            db, current_user.id, activity_id
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove uma atividade do usuário autenticado (só o dono)."""
    try:
        await activity_service.delete_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


# ===== Curtidas =====

@router.post("/{activity_id}/like", response_model=LikeStateResponse)
async def like_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Curte uma atividade (idempotente). Retorna o estado atual."""
    try:
        return await like_service.like_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{activity_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove curtida (idempotente)."""
    try:
        await like_service.unlike_activity(db, current_user.id, activity_id)
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/{activity_id}/likes", response_model=LikeListResponse)
async def list_likes(
    activity_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista quem curtiu + contagem + flag do user atual."""
    try:
        return await like_service.get_likes(
            db, current_user.id, activity_id, limit, offset
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)