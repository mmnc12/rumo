import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.activity import ActivityType
from app.schemas.user import UserPublic



# ===== Schemas de entrada =====

class ActivityCreate(BaseModel):
    """Dados para criar uma nova atividade."""

    activity_type: ActivityType
    title: str | None = Field(None, max_length=120)
    description: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    duration_s: int | None = Field(None, ge=0)
    distance_m: float | None = Field(None, ge=0)
    elevation_gain_m: float | None = Field(None, ge=0)
    calories: int | None = Field(None, ge=0)
    avg_pace_s_per_km: int | None = Field(None, ge=0)
    avg_speed_mps: float | None = Field(None, ge=0)

    # Lista de pontos GPS: [[lat, lon, altitude, timestamp], ...]
    track_points: list[list[float]] | None = Field(
        None,
        description="Lista de pontos GPS no formato [lat, lon, altitude, timestamp_unix]",
    )


# ===== Schemas de saída =====

class ActivityResponse(BaseModel):
    """Dados públicos de uma atividade."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    activity_type: ActivityType
    title: str | None
    description: str | None
    started_at: datetime
    finished_at: datetime | None
    duration_s: int | None
    distance_m: float | None
    elevation_gain_m: float | None
    calories: int | None
    avg_pace_s_per_km: int | None
    avg_speed_mps: float | None
    cover_photo_url: str | None
    photo_count: int
    created_at: datetime


class ActivityDetailResponse(ActivityResponse):
    """Detalhe de uma atividade, com autor aninhado.

    Usado APENAS no GET /activities/{id} — evita um segundo request
    do frontend pra buscar o autor. A listagem usa ActivityResponse
    (sem author) pra não inflar o payload do feed/lista.
    """

    author: UserPublic = Field(validation_alias="user")


class ActivityListResponse(BaseModel):
    """Lista paginada de atividades."""

    items: list[ActivityResponse]
    total: int
    limit: int
    offset: int


class FeedItemResponse(ActivityResponse):
    """Atividade no feed, com dados do autor."""

    author: UserPublic = Field(validation_alias="user")


# ===== Track (geometria pro mapa) =====

class TrackResponse(BaseModel):
    """Geometria da rota de uma atividade, em formato GeoJSON-like.

    Decisão: expor APENAS a geometria (não raw_track_points) pra não pesar
    a resposta. Cliente desenha o mapa; streams (elevação/tempo por ponto)
    ficam pra um endpoint dedicado no futuro.
    """

    activity_id: uuid.UUID
    type: str = "LineString"
    # [[lon, lat], ...] — ordem GeoJSON (lon primeiro!)
    coordinates: list[list[float]]
    # [minLon, minLat, maxLon, maxLat]
    bbox: list[float]
    n_points: int
    simplified: bool = False