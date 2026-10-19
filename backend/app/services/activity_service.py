"""Service de atividades: CRUD + upload de GPX + track (geometria) + busca."""

import json

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Activity
from app.models.activity import ActivityType
from app.schemas import ActivityCreate
from app.schemas.activity import TrackResponse
from app.services import follow_service
from app.services.errors import NotFoundError
from app.services.follow_service import following_ids_subquery
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


async def search_activities(
    db: AsyncSession,
    user_id,
    q: str,
    limit: int = 20,
    offset: int = 0,
) -> list[Activity]:
    """
    Busca atividades por texto em title/description, filtrando por visibilidade.

    Regra de visibilidade: dono OU seguido — mesma do feed. Usa o helper
    `following_ids_subquery` pra não duplicar SQL (fonte de verdade única).

    `ILIKE %q%` NÃO usa índice B-tree — full scan é o que roda hoje.
    Aceitável até ~5k atividades; criar índice GIN gin_trgm_ops quando crescer
    (dívida já registrada no handoff).

    Carrega `user` com selectinload porque o router serializa com
    FeedItemResponse (author aninhado) — async quebra lazy load.
    """
    clean_q = q.strip()
    if not clean_q:
        # Defensivo: se o router deixar passar, não varre o banco à toa.
        return []

    pattern = f"%{clean_q}%"

    stmt = (
        select(Activity)
        .where(
            or_(
                Activity.title.ilike(pattern),
                Activity.description.ilike(pattern),
            )
        )
        .where(
            or_(
                Activity.user_id == user_id,
                Activity.user_id.in_(following_ids_subquery(user_id)),
            )
        )
        .options(selectinload(Activity.user))
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
    *,
    allow_following: bool = False,
) -> Activity:
    """
    Retorna uma atividade.

    - allow_following=False: só o dono (comportamento original).
    - allow_following=True: dono OU quem segue o dono.

    Levanta NotFoundError em ambos os casos (não vaza existência).

    Carrega `user` com selectinload para que ActivityDetailResponse
    consiga serializar `author` sem lazy load (async quebra lazy load).
    """
    stmt = (
        select(Activity)
        .options(selectinload(Activity.user))
        .where(Activity.id == activity_id)
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()

    if activity is None:
        raise NotFoundError("Atividade não encontrada")

    if activity.user_id == user_id:
        return activity

    if allow_following:
        following = await follow_service.is_following(
            db, user_id, activity.user_id
        )
        if following:
            return activity

    raise NotFoundError("Atividade não encontrada")


async def get_activity_track(
    db: AsyncSession,
    user_id,
    activity_id,
) -> TrackResponse:
    """
    Retorna a geometria da rota de uma atividade em formato GeoJSON-like.

    - Dono OU seguidor do dono acessa (404 caso contrário — não vaza existência).
    - Usa ST_AsGeoJSON + ST_XMin/YMin/XMax/YMax do PostGIS: uma única query.
    - Não expõe raw_track_points — só geometria (decisão do 13a.0).
    """
    # 1) Confirma que a atividade existe e o usuário pode vê-la
    #    (reusa get_activity com allow_following=True -> 404 caso contrário)
    activity = await get_activity(
        db, user_id, activity_id, allow_following=True
    )

    if activity.route is None:
        raise NotFoundError("Atividade não possui rota")

    # 2) Extrai GeoJSON + bbox + n_points direto do PostGIS
    stmt = select(
        func.ST_AsGeoJSON(Activity.route).label("geojson"),
        func.ST_NPoints(Activity.route).label("n_points"),
        func.ST_XMin(Activity.route).label("min_lon"),
        func.ST_YMin(Activity.route).label("min_lat"),
        func.ST_XMax(Activity.route).label("max_lon"),
        func.ST_YMax(Activity.route).label("max_lat"),
    ).where(Activity.id == activity_id)

    result = await db.execute(stmt)
    row = result.one()

    # ST_AsGeoJSON retorna uma string JSON — parsear
    geojson = json.loads(row.geojson)
    coordinates = geojson["coordinates"]  # [[lon, lat], ...]

    return TrackResponse(
        activity_id=activity_id,
        type="LineString",
        coordinates=coordinates,
        bbox=[row.min_lon, row.min_lat, row.max_lon, row.max_lat],
        n_points=row.n_points,
        simplified=False,
    )


async def delete_activity(
    db: AsyncSession,
    user_id,
    activity_id,
) -> None:
    """
    Remove uma atividade do usuário.

    Só o dono apaga (404 se não existir ou não for dele).
    NÃO usa allow_following — segue a regra original de escrita.
    """
    activity = await get_activity(db, user_id, activity_id)
    await db.delete(activity)
    await db.commit()