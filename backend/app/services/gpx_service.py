"""Parser de arquivos GPX e cálculo de métricas de atividade."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from io import BytesIO
from typing import TYPE_CHECKING, Any

import gpxpy
import gpxpy.gpx

from app.services.errors import BadRequestError

if TYPE_CHECKING:
    from app.models.activity import Activity

_EARTH_RADIUS_M = 6_371_000.0
_ELEVATION_THRESHOLD_M = 1.0
_MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em metros entre dois pontos (fórmula de Haversine).

    Público (sem underscore) porque o fit_service reusa como fallback
    quando o FIT não traz `distance` acumulada.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a))


def _as_utc(dt: datetime | None) -> datetime | None:
    """Garante datetime UTC aware."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_unix(dt: datetime | None) -> float | None:
    """Converte datetime para unix timestamp (float)."""
    if dt is None:
        return None
    return _as_utc(dt).timestamp()


def parse_gpx(file_bytes: bytes) -> dict[str, Any]:
    """
    Lê bytes de um GPX e devolve dict pronto para criar a Activity.

    Formato de track_points: [[lat, lon, ele, unix_ts], ...] — idêntico
    ao que o POST /activities já aceita.

    Levanta BadRequestError se o arquivo for inválido/vazio.
    """
    if len(file_bytes) > _MAX_FILE_SIZE_BYTES:
        raise BadRequestError(
            f"Arquivo muito grande (máx {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB)"
        )

    try:
        gpx = gpxpy.parse(BytesIO(file_bytes))
    except Exception as exc:
        raise BadRequestError(f"GPX inválido: {exc}") from exc

    # Coleta todos os pontos de todos os segmentos, em ordem
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            points.extend(segment.points)

    valid_points = [
        p for p in points if p.latitude is not None and p.longitude is not None
    ]
    if len(valid_points) < 2:
        raise BadRequestError("GPX não contém pontos GPS suficientes")

    # Timestamps
    times = [_as_utc(p.time) for p in valid_points if p.time is not None]
    if not times:
        raise BadRequestError("GPX não contém timestamps nos pontos")

    started_at = times[0]
    finished_at = times[-1]
    duration_s = int((finished_at - started_at).total_seconds())

    # Distância
    distance_m = 0.0
    for prev, curr in zip(valid_points, valid_points[1:]):
        distance_m += haversine_m(
            prev.latitude, prev.longitude, curr.latitude, curr.longitude
        )

    # Elevação ganha (só subidas acima do threshold)
    elevation_gain_m = 0.0
    elevations = [p.elevation for p in valid_points if p.elevation is not None]
    for prev_ele, curr_ele in zip(elevations, elevations[1:]):
        delta = curr_ele - prev_ele
        if delta >= _ELEVATION_THRESHOLD_M:
            elevation_gain_m += delta

    # Métricas derivadas
    avg_pace_s_per_km = (
        duration_s / (distance_m / 1000.0) if distance_m > 0 else None
    )
    avg_speed_mps = distance_m / duration_s if duration_s > 0 else None

    # track_points no formato [[lat, lon, ele, unix_ts], ...]
    track_points: list[list[float]] = []
    for p in valid_points:
        track_points.append([
            round(p.latitude, 7),
            round(p.longitude, 7),
            round(p.elevation, 1) if p.elevation is not None else 0.0,
            _to_unix(p.time) or 0.0,
        ])

    # Nome e tipo default do GPX
    title = None
    if gpx.tracks and gpx.tracks[0].name:
        title = gpx.tracks[0].name.strip() or None

    gpx_type = None
    if gpx.tracks and gpx.tracks[0].type:
        gpx_type = gpx.tracks[0].type.strip().lower() or None

    return {
        "title": title,
        "gpx_type": gpx_type,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_s": duration_s,
        "distance_m": round(distance_m, 2),
        "elevation_gain_m": round(elevation_gain_m, 2),
        "avg_pace_s_per_km": (
            round(avg_pace_s_per_km, 2) if avg_pace_s_per_km else None
        ),
        "avg_speed_mps": round(avg_speed_mps, 4) if avg_speed_mps else None,
        "track_points": track_points,
    }


# Mapeamento de tipos do GPX para o enum ActivityType
GPX_TYPE_MAP: dict[str, str] = {
    "running": "run",
    "run": "run",
    "walking": "walk",
    "walk": "walk",
    "hiking": "hike",
    "hike": "hike",
    "cycling": "cycle",
    "biking": "cycle",
    "bike": "cycle",
    "swimming": "swim",
    "swim": "swim",
}


def map_gpx_type(gpx_type: str | None) -> str:
    """Traduz <type> do GPX para o ActivityType do Rumo. Default: other."""
    if not gpx_type:
        return "other"
    return GPX_TYPE_MAP.get(gpx_type.lower(), "other")


# ===== Geração de GPX (export) — [Sessão 21] =====
# [Sessão 26] to_gpx passa a emitir <time> por <trkpt> quando
# raw_track_points tem timestamps reais. Fallback preserva o
# comportamento da S25 (started_at em todos os pontos) quando os
# dados brutos não estão disponíveis ou não batem com a geometria.


def _trkpt_time(
    index: int,
    raw_track_points: list[list[float]] | None,
    n_coordinates: int,
    started_at: datetime | None,
) -> datetime | None:
    """Resolve o <time> de um <trkpt> (S26).

    Regra:
    1. Se `raw_track_points` existe, tem o MESMO comprimento de
       `coordinates`, o item `index` tem >= 4 posições e o timestamp
       (posição 3, unix epoch) é > 0 → usa o timestamp real do ponto.
    2. Caso contrário → fallback: `started_at` da atividade (comportamento
       da S25, inalterado). Isso cobre atividades antigas (JSON sem
       raw_track_points) e qualquer divergência de comprimento.

    Timestamps `0.0` são tratados como "sem tempo" (o parse_gpx grava 0.0
    quando o GPX não trouxe `<time>` por ponto). Para não emitir `<time>`
    errado, o fallback usa `started_at` — a mesma âncora que o GPX
    exportado usava antes da S26.
    """
    if (
        raw_track_points is not None
        and len(raw_track_points) == n_coordinates
        and 0 <= index < len(raw_track_points)
    ):
        point = raw_track_points[index]
        if len(point) >= 4:
            ts = point[3]
            if isinstance(ts, (int, float)) and ts > 0:
                return datetime.fromtimestamp(float(ts), tz=timezone.utc)
    return started_at


def to_gpx(
    activity: "Activity",
    coordinates: list[list[float]],
    raw_track_points: list[list[float]] | None = None,
) -> str:
    """Serializa uma atividade como GPX 1.1 (string XML).

    `coordinates` vem do `get_activity_track` em ordem GeoJSON `[lon, lat]`.
    Aqui invertemos para `lat`/`lon` no atributo do `<trkpt>` — é o
    contrário do `parse_gpx`, que lê `[lat, lon]` do GPX e devolve
    `[lat, lon]`. Manter essa inversão documentada evita bugs de eixo.

    [Sessão 26] Timestamps por ponto: quando `raw_track_points` está
    disponível e alinhado com `coordinates`, cada `<trkpt>` recebe o
    `<time>` real do ponto (unix epoch → ISO 8601 UTC). Caso contrário,
    cai no fallback da S25: `<time>` com `started_at` em todos os pontos.
    Strava/Garmin aceitam ambos; ter `<time>` distintos é o que permite
    cálculo de velocidade/pace por segmento do lado do consumidor.

    `raw_track_points` é opcional (default None) para não quebrar callers
    antigos — mas os 2 call sites em activity_service.py passam
    `activity.raw_track_points` explicitamente.
    """
    gpx = gpxpy.gpx.GPX()
    gpx.creator = "Rumo"

    track = gpxpy.gpx.GPXTrack()
    if activity.title:
        track.name = activity.title
    track.type = (
        activity.activity_type.value
        if hasattr(activity.activity_type, "value")
        else str(activity.activity_type)
    )
    gpx.tracks.append(track)

    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    started_at = _as_utc(activity.started_at)
    n_coordinates = len(coordinates)
    for index, point in enumerate(coordinates):
        # point é [lon, lat] (GeoJSON) — inverter aqui.
        lon, lat = point[0], point[1]
        trkpt = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon)
        trkpt.time = _trkpt_time(
            index, raw_track_points, n_coordinates, started_at
        )
        segment.points.append(trkpt)

    return gpx.to_xml()