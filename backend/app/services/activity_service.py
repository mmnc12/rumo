"""Service de atividades: CRUD + upload de GPX/FIT + track + busca."""

import asyncio
import json

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Activity, User
from app.models.activity import ActivityType
from app.schemas import ActivityCreate
from app.schemas.activity import TrackResponse
from app.services import follow_service
from app.services.errors import NotFoundError
from app.services.fit_service import map_fit_sport, parse_fit
from app.services.follow_service import following_ids_subquery
from app.services.gpx_service import map_gpx_type, parse_gpx


_VALID_ACTIVITY_TYPES = {t.value for t in ActivityType}


# ---------------------------------------------------------------------------
# CÃ¡lculo de calorias
# ---------------------------------------------------------------------------
#
# FÃ³rmula: kcal = MET x peso_kg x duraÃ§Ã£o_horas
#
# MET = "Metabolic Equivalent of Task" â€” quantas vezes o gasto energÃ©tico
# da atividade supera o basal em repouso (1 MET ~= 1 kcal/kg/h).
#
# Valores tirados do Compendium of Physical Activities (Ainsworth et al.),
# arredondados para 1 casa. SÃ£o aproximaÃ§Ãµes â€” Strava/Garmin usam modelos
# mais finos (FC, VO2max, potÃªncia), mas para o Rumo a estimativa por MET
# Ã© suficiente e barata. Ajustar aqui se aparecer reclamaÃ§Ã£o de precisÃ£o.
#
# Chaves sÃ£o os valores do enum ActivityType. Cobre TODOS os tipos vÃ¡lidos;
# se um tipo novo entrar no enum e faltar aqui, o fallback Ã© _MET_DEFAULT.

_MET_BY_TYPE: dict[str, float] = {
    "run": 9.8,        # corrida ~10 km/h
    "walk": 3.5,       # caminhada ~5 km/h
    "cycle": 7.5,      # pedalada lazer ~16 km/h
    "hike": 6.0,       # trilha
    "swim": 8.0,       # nataÃ§Ã£o moderada
    "other": 5.0,      # default conservador
}
_MET_DEFAULT = 5.0

# Peso de fallback quando o usuÃ¡rio nÃ£o preencheu weight_kg.
# 70 kg Ã© a mÃ©dia adulta global aproximada (usada em vÃ¡rias calculadoras
# pÃºblicas). NÃ£o Ã© ideal â€” o certo Ã© o usuÃ¡rio preencher o perfil â€” mas
# evita calories=NULL e mantÃ©m /stats/summary Ãºtil.
_DEFAULT_WEIGHT_KG = 70.0


def _estimate_calories(
    activity_type: str | None,
    duration_s: int | None,
    weight_kg: float | None,
) -> int | None:
    """
    Estima calorias queimadas por MET x peso x duraÃ§Ã£o.

    - Retorna None se a duraÃ§Ã£o for ausente/zero (nÃ£o hÃ¡ o que estimar).
    - Peso ausente usa _DEFAULT_WEIGHT_KG (ver comentÃ¡rio acima).
    - Tipo desconhecido usa _MET_DEFAULT (5.0).
    - Sempre retorna int >= 0 (CHECK do banco exige nÃ£o-negativo).
    """
    if not duration_s or duration_s <= 0:
        return None

    met = _MET_BY_TYPE.get(activity_type or "", _MET_DEFAULT)
    kg = weight_kg if weight_kg and weight_kg > 0 else _DEFAULT_WEIGHT_KG

    duration_hours = duration_s / 3600.0
    kcal = met * kg * duration_hours

    # Defensivo: MET positivo x kg positivo x duraÃ§Ã£o positiva nunca dÃ¡
    # negativo, mas o CheckConstraint do banco exige >= 0. Clampa por seguranÃ§a.
    return max(0, int(round(kcal)))


async def _get_user_weight_kg(db: AsyncSession, user_id) -> float:
    """
    Busca o weight_kg do usuÃ¡rio para o cÃ¡lculo de calorias.

    Custa 1 query extra por upload â€” aceitÃ¡vel: upload Ã© raro (10/h de rate
    limit) e o peso nÃ£o vem no JWT. NÃ£o otimizar sem medir: a alternativa
    (mudar a assinatura de create_activity_from_* pra receber o User) quebra
    o contrato do service e mexe no router por ~1 query.
    """
    stmt = select(User.weight_kg).where(User.id == user_id)
    result = await db.execute(stmt)
    weight = result.scalar_one_or_none()
    return float(weight) if weight is not None else _DEFAULT_WEIGHT_KG


# ---------------------------------------------------------------------------
# NormalizaÃ§Ã£o de campos de upload
# ---------------------------------------------------------------------------

def _normalize_activity_type(value: str | None) -> str | None:
    """
    Valida/normaliza um activity_type vindo como string.

    Retorna None se for vazio ou invÃ¡lido (pra usar o fallback).
    """
    if not value:
        return None
    value = value.strip().lower()
    if not value or value == "string":  # placeholder do Swagger
        return None
    if value not in _VALID_ACTIVITY_TYPES:
        return None
    return value


def _normalize_upload_fields(
    title: str | None,
    activity_type: str | None,
    description: str | None,
    parsed_title: str | None,
    parsed_type: str | None,
    type_mapper,
) -> tuple[str, str, str | None]:
    """
    Normaliza os campos comuns a GPX e FIT.

    - title: None/vazio/"string" â†’ parsed_title â†’ "Atividade"
    - activity_type: None/vazio/"string"/invÃ¡lido â†’ type_mapper(parsed_type)
    - description: None/vazio/"string" â†’ None

    `type_mapper` Ã© `map_gpx_type` ou `map_fit_sport` â€” cada parser tem
    seu prÃ³prio vocabulÃ¡rio de tipo, mas o fallback e a validaÃ§Ã£o sÃ£o iguais.
    """
    clean_title = title.strip() if title else None
    if not clean_title or clean_title == "string":
        clean_title = None
    final_title = clean_title or parsed_title or "Atividade"

    clean_type = _normalize_activity_type(activity_type)
    final_type = clean_type or type_mapper(parsed_type)

    clean_description = description.strip() if description else None
    if not clean_description or clean_description == "string":
        clean_description = None

    return final_title, final_type, clean_description


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CriaÃ§Ã£o
# ---------------------------------------------------------------------------

async def create_activity(
    db: AsyncSession,
    user_id,
    payload: ActivityCreate,
) -> Activity:
    """
    Cria uma atividade no banco (a partir de JSON prÃ©-calculado).

    Calorias: se o payload trouxer `calories` explÃ­cito, o valor do usuÃ¡rio
    prevalece. SÃ³ calcula quando vier None â€” mesma regra do GPX/FIT.
    """
    route = points_to_linestring(payload.track_points) if payload.track_points else None

    calories = payload.calories
    if calories is None:
        weight_kg = await _get_user_weight_kg(db, user_id)
        calories = _estimate_calories(
            payload.activity_type, payload.duration_s, weight_kg
        )

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
        calories=calories,
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
    - activity_type: se None/vazio/"string"/invÃ¡lido, mapeia do <type> do GPX
    - description: opcional
    - calories: se o GPX trouxer (raro), usa; senÃ£o estima por MET x peso x hora

    Parse roda em thread separada (`asyncio.to_thread`) para nÃ£o bloquear
    o event loop â€” o parser Ã© sÃ­ncrono e pesa 1â€“3s por arquivo.
    """
    parsed = await asyncio.to_thread(parse_gpx, file_bytes)

    final_title, final_type, clean_description = _normalize_upload_fields(
        title, activity_type, description,
        parsed["title"], parsed["gpx_type"], map_gpx_type,
    )

    calories = parsed.get("calories")
    if calories is None:
        weight_kg = await _get_user_weight_kg(db, user_id)
        calories = _estimate_calories(
            final_type, parsed["duration_s"], weight_kg
        )

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
        calories=calories,
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


async def create_activity_from_fit(
    db: AsyncSession,
    user_id,
    file_bytes: bytes,
    title: str | None = None,
    activity_type: str | None = None,
    description: str | None = None,
) -> Activity:
    """
    Cria uma atividade a partir de um arquivo FIT (Garmin/ANT).

    Espelha create_activity_from_gpx, mas usa `map_fit_sport` no fallback
    de tipo (o FIT usa `sport` da sessÃ£o, nÃ£o `type` do track).

    - title: se None/vazio/"string", FIT nÃ£o tem nome de atividade â†’ "Atividade"
    - activity_type: se None/vazio/"string"/invÃ¡lido, mapeia do sport do FIT
    - description: opcional
    - calories: se o FIT trouxer (session.total_calories), usa; senÃ£o estima
      por MET x peso x hora. O parse_fit atual NÃƒO extrai total_calories â€”
      fica como dÃvida futura; hoje sempre cai no estimate.

    Parse roda em thread separada (`asyncio.to_thread`) para nÃ£o bloquear
    o event loop â€” o parser Ã© sÃ­ncrono e pesa 1â€“3s por arquivo.
    """
    parsed = await asyncio.to_thread(parse_fit, file_bytes)

    final_title, final_type, clean_description = _normalize_upload_fields(
        title, activity_type, description,
        parsed["title"], parsed["gpx_type"], map_fit_sport,
    )

    calories = parsed.get("calories")
    if calories is None:
        weight_kg = await _get_user_weight_kg(db, user_id)
        calories = _estimate_calories(
            final_type, parsed["duration_s"], weight_kg
        )

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
        calories=calories,
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


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------

async def list_activities(
    db: AsyncSession,
    user_id,
    limit: int = 20,
    offset: int = 0,
) -> list[Activity]:
    """Lista atividades do usuÃ¡rio, ordenadas por started_at DESC."""
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

    Regra de visibilidade: dono OU seguido â€” mesma do feed. Usa o helper
    `following_ids_subquery` pra nÃ£o duplicar SQL (fonte de verdade Ãºnica).

    `ILIKE %q%` NÃƒO usa Ã­ndice B-tree â€” full scan Ã© o que roda hoje.
    AceitÃ¡vel atÃ© ~5k atividades; criar Ã­ndice GIN gin_trgm_ops quando crescer
    (dÃvida jÃ¡ registrada no handoff).

    Carrega `user` com selectinload porque o router serializa com
    FeedItemResponse (author aninhado) â€” async quebra lazy load.
    """
    clean_q = q.strip()
    if not clean_q:
        # Defensivo: se o router deixar passar, nÃ£o varre o banco Ã  toa.
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

    - allow_following=False: sÃ³ o dono (comportamento original).
    - allow_following=True: dono OU quem segue o dono.

    Levanta NotFoundError em ambos os casos (nÃ£o vaza existÃªncia).

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
        raise NotFoundError("Atividade nÃ£o encontrada")

    if activity.user_id == user_id:
        return activity

    if allow_following:
        following = await follow_service.is_following(
            db, user_id, activity.user_id
        )
        if following:
            return activity

    raise NotFoundError("Atividade nÃ£o encontrada")


async def get_activity_track(
    db: AsyncSession,
    user_id,
    activity_id,
) -> TrackResponse:
    """
    Retorna a geometria da rota de uma atividade em formato GeoJSON-like.

    - Dono OU seguidor do dono acessa (404 caso contrÃ¡rio â€” nÃ£o vaza existÃªncia).
    - Usa ST_AsGeoJSON + ST_XMin/YMin/XMax/YMax do PostGIS: uma Ãºnica query.
    - NÃ£o expÃµe raw_track_points â€” sÃ³ geometria (decisÃ£o do 13a.0).
    """
    activity = await get_activity(
        db, user_id, activity_id, allow_following=True
    )

    if activity.route is None:
        raise NotFoundError("Atividade nÃ£o possui rota")

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

    geojson = json.loads(row.geojson)
    coordinates = geojson["coordinates"]

    return TrackResponse(
        activity_id=activity_id,
        type="LineString",
        coordinates=coordinates,
        bbox=[row.min_lon, row.min_lat, row.max_lon, row.max_lat],
        n_points=row.n_points,
        simplified=False,
    )


# ---------------------------------------------------------------------------
# ExclusÃ£o
# ---------------------------------------------------------------------------

async def delete_activity(
    db: AsyncSession,
    user_id,
    activity_id,
) -> None:
    """
    Remove uma atividade do usuÃ¡rio.

    SÃ³ o dono apaga (404 se nÃ£o existir ou nÃ£o for dele).
    NÃƒO usa allow_following â€” segue a regra original de escrita.
    """
    activity = await get_activity(db, user_id, activity_id)
    await db.delete(activity)
    await db.commit()