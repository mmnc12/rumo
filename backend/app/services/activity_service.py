from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity
from app.schemas import ActivityCreate


def points_to_linestring(track_points: list[list[float]]) -> WKTElement | None:
    """
    Converte lista de pontos GPS em LINESTRING WKT.

    Formato esperado de cada ponto: [lat, lon, altitude?, timestamp?]
    Retorna None se houver menos de 2 pontos.
    """
    if not track_points or len(track_points) < 2:
        return None

    # WKT usa (lon lat) — note a ordem invertida em relação ao GPS comum.
    # Pontos separados por vírgula, coordenadas do mesmo ponto por espaço.
    coords = ", ".join(f"{p[1]} {p[0]}" for p in track_points)
    return WKTElement(f"LINESTRING({coords})", srid=4326)


def linestring_to_points(wkt_or_geom) -> list[list[float]] | None:
    """
    Converte uma geometria LINESTRING em lista de pontos [lat, lon].
    Aceita string WKT ou objeto do banco (via ST_AsText).
    """
    if wkt_or_geom is None:
        return None

    wkt = str(wkt_or_geom)
    # Extrai o conteúdo entre parênteses: "LINESTRING(lon1 lat1, lon2 lat2, ...)"
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
    """Cria uma atividade no banco."""
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


async def list_user_activities(
    db: AsyncSession,
    user_id,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Activity], int]:
    """Lista atividades do usuário com paginação."""
    # Total
    count_stmt = select(func.count()).select_from(Activity).where(Activity.user_id == user_id)
    total = (await db.execute(count_stmt)).scalar_one()

    # Página atual
    stmt = (
        select(Activity)
        .where(Activity.user_id == user_id)
        .order_by(Activity.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total