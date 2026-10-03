"""Service de atividades: CRUD + upload de GPX."""

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity
from app.models.activity import ActivityType
from app.schemas import ActivityCreate
from app.services.errors import NotFoundError
from app.services.gpx_service import map_gpx_type, parse_gpx


_VALID_ACTIVITY_TYPES = {t.value for t in ActivityType}


def _normalize_activity_type(value: str | None) -> str | None:
    """
    Valida/normaliza um activity_type vindo como string.

    Retorna None se for vazio ou inválido (pra usar o fallback).
    """
    if not value:
        return None
    value = value.strip().lower()
    if not value or value == "string":  # placeholder do Swagger
        return None
    if value not in _VALID_ACTIVITY_TYPES:
        return None
    return value


def points_to_linestring(track_points: list[list[float]]) -> WKTElement | None:
    """Converte lista de pontos GPS em LINESTRING WKT."""
    if not track_points or len(track_points) < 2:
        return None
    coords = ", ".join(f"{p[1]} {p[0]}" for p in track_points)
    return WKTElement(f"LINESTRING({coords})", srid=4326)


def linestring_to_points(wkt_or_geom) -> list[list[float]] | None:
    """Converte geometria LINESTRING em lista de pontos [lat, lon]."""
    if wkt_or_geom is None:
        return None
    wkt = str(wkt_or_geom)
    inner = wkt.replace("LINESTRING", "").strip().strip("()")
    points = []
    for pair in inner.split(","):
        lon, lat = pair.strip().split()
        points.append([float(lat), float(lon)])
    return points or None


async def create_activity(
    db: AsyncSession,
    user_id,
    payload: ActivityCreate,
) -> Activity:
    """Cria uma atividade no banco (a partir de JSON pré-calculado)."""
    route = points_to_linestring(payload.track_points) if payload.track_points else None

    activity = Activity(
        user_id=user_id,
        activity_type=payload.activity_type,
        title=payload.title,
        description=payload.description,
        started_at=payload.started_at,
        finished_at=payload.finished_at,
        duration_s=payload.duration_s,
        distance_m=payload.distance_m,
        elevation_gain_m=payload.elevation_gain_m,
        calories=payload.calories,
        avg_pace_s_per_km=payload.avg_pace_s_per_km,
        avg_speed_mps=payload.avg_speed_mps,
        route=route,
        raw_track_points=payload.track_points,
    )

    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def create_activity_from_gpx(
    db: AsyncSession,
    user_id,
    file_bytes: bytes,
    title: str | None = None,
    activity_type: str | None = None,
    description: str | None = None,
) -> Activity:
    """
    Cria uma atividade a partir de um arquivo GPX.

    - title: se None/vazio/"string", usa o <name> do GPX (fallback: "Atividade")
    - activity_type: se None/vazio/"string"/inválido, mapeia do <type> do GPX
    - description: opcional
    """
    parsed = parse_gpx(file_bytes)

    # Normaliza title (Swagger às vezes manda "string" como placeholder)
    clean_title = title.strip() if title else None
    if not clean_title or clean_title == "string":
        clean_title = None
    final_title = clean_title or parsed["title"] or "Atividade"

    # Normaliza activity_type
    clean_type = _normalize_activity_type(activity_type)
    final_type = clean_type or map_gpx_type(parsed["gpx_type"])

    # Normaliza description também (mesmo problema do Swagger)
    clean_description = description.strip() if description else None
    if not clean_description or clean_description == "string":
        clean_description = None

    route = points_to_linestring(parsed["track_points"])

    activity = Activity(
        user_id=user_id,
        activity_type=final_type,
        title=final_title,
        description=clean_description,
        started_at=parsed["started_at"],
        finished_at=parsed["finished_at"],
        duration_s=parsed["duration_s"],
        distance_m=parsed["distance_m"],
        elevation_gain_m=parsed["elevation_gain_m"],
        calories=None,
        avg_pace_s_per_km=(
            int(parsed["avg_pace_s_per_km"]) if parsed["avg_pace_s_per_km"] else None
        ),
        avg_speed_mps=parsed["avg_speed_mps"],
        route=route,
        raw_track_points=parsed["track_points"],
    )

    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def list_activities(
    db: AsyncSession,
    user_id,
    limit: int = 20,
    offset: int = 0,
) -> list[Activity]:
    """Lista atividades do usuário, ordenadas por started_at DESC."""
    stmt = (
        select(Activity)
        .where(Activity.user_id == user_id)
        .order_by(Activity.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_activity(
    db: AsyncSession,
    user_id,
    activity_id,
) -> Activity:
    """Retorna uma atividade do usuário (404 se não existir ou não for dele)."""
    stmt = select(Activity).where(
        Activity.id == activity_id, Activity.user_id == user_id
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()
    if activity is None:
        raise NotFoundError("Atividade não encontrada")
    return activity


async def delete_activity(
    db: AsyncSession,
    user_id,
    activity_id,
) -> None:
    """Remove uma atividade do usuário (404 se não existir ou não for dele)."""
    activity = await get_activity(db, user_id, activity_id)
    await db.delete(activity)
    await db.commit()