"""Parser de arquivos FIT (Garmin/ANT) e cálculo de métricas de atividade."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Any

import fitparse

from app.services.errors import BadRequestError
from app.services.gpx_service import haversine_m

_MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB — mesmo limite do GPX

# FIT armazena coordenadas em semicírculos (2^31 = 180°).
# Exemplo: 521320503 semicírculos → ~43.6°.
_SEMICIRCLES_TO_DEG = 180.0 / 2**31

# Mapeamento de sport do FIT para o ActivityType do Rumo.
# Strings vêm da mensagem `session` (não do `track`).
FIT_SPORT_MAP: dict[str, str] = {
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


def _semicircles_to_deg(value: int | None) -> float | None:
    """Converte coordenada FIT (semicírculos) para graus decimais."""
    if value is None:
        return None
    return value * _SEMICIRCLES_TO_DEG


def parse_fit(file_bytes: bytes) -> dict[str, Any]:
    """
    Lê bytes de um arquivo FIT de ATIVIDADE e devolve dict pronto para criar a Activity.

    Formato de track_points: [[lat, lon, ele, unix_ts], ...] — idêntico
    ao parse_gpx, para o activity_service tratar os dois fluxos igual.

    Rejeita arquivos que não são de atividade (sem mensagens `record`),
    como workouts e courses — o Rumo só aceita atividade.

    Levanta BadRequestError se o arquivo for inválido/vazio/sem records.
    """
    if len(file_bytes) > _MAX_FILE_SIZE_BYTES:
        raise BadRequestError(
            f"Arquivo muito grande (máx {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB)"
        )

    try:
        fit = fitparse.FitFile(BytesIO(file_bytes))
        records = list(fit.get_messages("record"))
    except Exception as exc:
        raise BadRequestError(f"FIT inválido: {exc}") from exc

    if len(records) < 2:
        raise BadRequestError(
            "FIT não contém registros de atividade suficientes "
            "(workouts e courses não são aceitos)"
        )

    # Coleta pontos com timestamp, em ordem
    points: list[dict[str, Any]] = []
    for record in records:
        data = {f.name: f.value for f in record}
        if data.get("timestamp") is None:
            continue
        points.append(data)

    if len(points) < 2:
        raise BadRequestError("FIT não contém timestamps nos registros")

    started_at = _as_utc(points[0]["timestamp"])
    finished_at = _as_utc(points[-1]["timestamp"])
    duration_s = int((finished_at - started_at).total_seconds())

    # Distância: prefere o campo `distance` acumulado do FIT (mais preciso
    # que haversine, porque o dispositivo já aplicou correções).
    # Fallback: haversine nos pontos GPS válidos.
    distance_m = 0.0
    last_distance = points[-1].get("distance")
    if last_distance is not None:
        distance_m = float(last_distance)
    else:
        valid_coords = [
            (p["position_lat"], p["position_long"])
            for p in points
            if p.get("position_lat") is not None
            and p.get("position_long") is not None
        ]
        for prev, curr in zip(valid_coords, valid_coords[1:]):
            distance_m += haversine_m(
                prev[0] * _SEMICIRCLES_TO_DEG,
                prev[1] * _SEMICIRCLES_TO_DEG,
                curr[0] * _SEMICIRCLES_TO_DEG,
                curr[1] * _SEMICIRCLES_TO_DEG,
            )

    # Elevação ganha (mesmo threshold de 1m do GPX)
    elevation_gain_m = 0.0
    elevations = [
        float(p["altitude"]) for p in points if p.get("altitude") is not None
    ]
    for prev_ele, curr_ele in zip(elevations, elevations[1:]):
        delta = curr_ele - prev_ele
        if delta >= 1.0:
            elevation_gain_m += delta

    # Métricas derivadas (mesmo cálculo do GPX)
    avg_pace_s_per_km = (
        duration_s / (distance_m / 1000.0) if distance_m > 0 else None
    )
    avg_speed_mps = distance_m / duration_s if duration_s > 0 else None

    # track_points no formato [[lat, lon, ele, unix_ts], ...]
    # Coordenadas FIT são opcionais (indoor sem GPS) — pontos sem lat/lon
    # são pulados, mas a atividade ainda é criada com distance/duration.
    track_points: list[list[float]] = []
    for p in points:
        lat = _semicircles_to_deg(p.get("position_lat"))
        lon = _semicircles_to_deg(p.get("position_long"))
        if lat is None or lon is None:
            continue
        track_points.append([
            round(lat, 7),
            round(lon, 7),
            round(float(p["altitude"]), 1) if p.get("altitude") is not None else 0.0,
            _to_unix(p["timestamp"]) or 0.0,
        ])

    # Tipo da atividade: `sport` da mensagem `session`
    # (fallback: `sport` do primeiro record, se existir — raro).
    fit_sport = None
    for session in fit.get_messages("session"):
        sport = session.get_value("sport")
        if sport:
            fit_sport = str(sport).strip().lower()
            break

    # Título: FIT não tem campo de nome de atividade padronizado.
    # O `session` pode ter `sport_profile_name` (ex: "Running"), mas não
    # é um nome de atividade. Deixamos None — o activity_service usa o
    # fallback "Atividade".
    title = None

    return {
        "title": title,
        "gpx_type": fit_sport,  # reaproveita a chave; o service mapeia com FIT_SPORT_MAP
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


def map_fit_sport(fit_sport: str | None) -> str:
    """Traduz `sport` do FIT para o ActivityType do Rumo. Default: other."""
    if not fit_sport:
        return "other"
    return FIT_SPORT_MAP.get(fit_sport.lower(), "other")