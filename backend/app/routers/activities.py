"""Endpoints de atividades (CRUD, estatísticas, curtidas, upload, track, busca)."""

from typing import Literal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
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
    ActivityDetailResponse,
    ActivityResponse,
    FeedItemResponse,
    TrackResponse,
)
from app.schemas.like import LikeListResponse, LikeStateResponse
from app.schemas.stats import (
    StatsByTypeResponse,
    StatsMonthlyResponse,
    StatsSummary,
    StatsWeeklyResponse,
)
from app.services import activity_service, like_service, stats_service
from app.services.errors import ServiceError
from app.services.follow_service import is_following

router = APIRouter()

_ALLOWED_UPLOAD_EXTENSIONS = (".gpx", ".fit")


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


# [Sessão 14 — B1] Drill-down por tipo de atividade.
# [Sessão 17] Adicionado param `period` (all|90d|1y) para janela temporal.
# [Sessão 20] Adicionado param `compare` (prev|yoy) — janela de comparação.
@router.get("/stats/by-type", response_model=StatsByTypeResponse)
async def stats_by_type(
    period: Literal["all", "90d", "1y"] = Query(
        default="all",
        description="Janela temporal: 'all' (todos os tempos), '90d' (últimos 90 dias) ou '1y' (últimos 365 dias)",
    ),
    compare: Literal["prev", "yoy"] = Query(
        default="prev",
        description=(
            "Janela de comparação para `previous`: 'prev' (imediatamente "
            "anterior, default) ou 'yoy' (mesmo período do ano anterior). "
            "Só tem efeito quando period != 'all'."
        ),
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Agrega as atividades do usuário por tipo (run/cycle/walk/...).

    Sem filtro por tipo: o objetivo é ver TODOS os tipos praticados lado a lado.
    Ordenação no backend: atividades DESC, tipo ASC.

    `period` filtra por `start_time` (retroativo a partir de agora):
    - `all` (default): todos os tempos — comportamento original.
    - `90d`: últimas 90 dias corridos.
    - `1y`: últimos 365 dias corridos.

    `compare` escolhe a janela de comparação usada em `previous`:
    - `prev` (default): janela imediatamente anterior (comportamento S18).
    - `yoy`: mesmo período do ano anterior (Sessão 20).
    """
    items = await stats_service.get_by_type(db, current_user.id, period, compare)
    return {"items": items}


# ===== Busca (estática — precisa vir ANTES de /{activity_id}) =====

@router.get("/search", response_model=list[FeedItemResponse])
@limiter.limit("20/minute")
async def search_activities(
    request: Request,
    q: str = Query(..., min_length=2, max_length=100, description="Texto a buscar em title/description"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Busca atividades por texto em title/description.

    Visibilidade: dono + seguidos (mesma regra do feed). Retorna
    `FeedItemResponse` (com author aninhado) pra o frontend renderizar
    o ActivityCard sem request extra.

    Rate limit: 20/min por IP — mesmo padrão do /users/search (busca
    textual é full scan, não pode virar vetor de DoS acidental).
    """
    return await activity_service.search_activities(
        db, current_user.id, q, limit, offset
    )


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
    file: UploadFile = File(..., description="Arquivo .gpx ou .fit"),
    title: str | None = Form(None, max_length=120),
    activity_type: str | None = Form(None),
    description: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cria uma atividade a partir de um arquivo GPX ou FIT.

    O backend detecta o formato pela extensão e parseia o arquivo,
    calculando distância, pace, elevação e preenchendo rota (PostGIS)
    + raw_track_points automaticamente.

    Rate limit: 10/hora por IP — parse é síncrono e bloqueia o event
    loop (GPX e FIT têm o mesmo custo ~1–3s); 10/hora cobre uso
    legítimo (algumas atividades por dia) e barra loop de upload que
    derrubaria o Render free tier.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo sem nome. Envie um arquivo .gpx ou .fit",
        )

    filename_lower = file.filename.lower()
    is_gpx = filename_lower.endswith(".gpx")
    is_fit = filename_lower.endswith(".fit")

    if not (is_gpx or is_fit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado. Envie um arquivo .gpx ou .fit",
        )

    file_bytes = await file.read()

    try:
        if is_gpx:
            return await activity_service.create_activity_from_gpx(
                db=db,
                user_id=current_user.id,
                file_bytes=file_bytes,
                title=title,
                activity_type=activity_type,
                description=description,
            )
        # is_fit
        return await activity_service.create_activity_from_fit(
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


@router.get("/{activity_id}", response_model=ActivityDetailResponse)
async def get_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna detalhes de uma atividade (com autor aninhado).

    Acessível pelo dono OU por quem segue o dono (mesma regra do feed).
    Quem não é dono nem seguidor recebe 404 (não vaza existência).

    `author` vem aninhado — o frontend não precisa de um segundo request
    pra buscar o perfil do dono.
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


# [Sessão 21] Export CSV/GPX — metadados (CSV) e geometria (GPX).
# Auth: mesma de /track (dono ou seguidor; 404 caso contrário).
# 404 se format=gpx e route IS NULL ("Atividade não possui rota").
# Response cru (bytes) — não é JSON, então não usa response_model.
@router.get("/{activity_id}/export")
async def export_activity(
    activity_id: UUID,
    format: Literal["csv", "gpx"] = Query(
        default="csv",
        description="Formato do arquivo: 'csv' (metadados) ou 'gpx' (geometria da rota).",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Baixa a atividade como CSV (metadados) ou GPX (geometria completa).

    - CSV: 1 linha de cabeçalho + 1 linha de dados. Funciona com ou sem rota.
    - GPX: exige rota (404 "Atividade não possui rota" se não houver).

    Retorna `Response` com `Content-Disposition: attachment` — o browser
    baixa em vez de exibir.
    """
    try:
        body, content_type, filename = await activity_service.export_activity(
            db, current_user.id, activity_id, format
        )
    except ServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return Response(
        content=body,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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