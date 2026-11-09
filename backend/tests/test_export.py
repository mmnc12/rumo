"""Testes do export CSV/GPX (Sessão 21).

Cobertura:
- CSV: shape (header + 1 linha), valores, Content-Type/Disposition,
  funciona com e sem rota, 404 (inexistente / não-seguidor),
  200 (dono / seguidor).
- GPX: shape (<trk>/<trkseg>/<trkpt>), inversão [lon,lat]→lat/lon
  comprovada por comparação com raw_track_points (o upload guarda
  [[lat, lon, ele, ts], ...]; o export lê de route PostGIS via GeoJSON
  e devolve lat/lon; os eixos precisam bater).
- Validação: format inválido → 422; format omitido → csv (default).
- [Sessão 26] GPX com <time> por <trkpt>: usa raw_track_points quando
  disponível (timestamps reais, distintos e crescentes); cai no fallback
  S25 (started_at) quando raw_track_points é None.

Estratégia de auth: helper `_client_as(user, test_engine)` constrói um
AsyncClient espelhando o `client` do conftest (sobrescreve get_db com
session nova por request, usando o `test_engine` do escopo session) e
sobrescreve get_current_user com o user do cenário. Sem sobrescrever
get_db, `_client_as` usaria o get_db real (engine de produção).

ATENÇÃO — tipo de atividade:
`sample_run.gpx` NÃO tem `<type>running</type>`; o arquivo se chama
"run" mas o `<type>` interno traduz para "walk" via `map_gpx_type`.
Por isso os asserts de filename usam `activity.activity_type.value`
em vez de hardcodar "run". Se um dia trocar o sample, o teste continua
passando sem manutenção.
"""

import io
from datetime import datetime, timedelta, timezone

import gpxpy
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from uuid6 import uuid7

from app.core.dependencies import get_current_user
from app.database import get_db
from app.main import app
from app.models.activity import Activity, ActivityType
from app.models.follow import Follow
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.services import activity_service
from app.services.gpx_service import to_gpx


# ===== Helpers =====

def _make_other_user(username: str) -> User:
    """User não commitado, para cenários de permissão."""
    return User(
        id=uuid7(),
        email=f"{username}@rumo.com",
        username=username,
        hashed_password="x",
        full_name=username.title(),
        is_active=True,
    )


def _client_as(user: User, test_engine) -> AsyncClient:
    """AsyncClient com get_db e get_current_user sobrescritos.

    Espelha o `client` do conftest (que sempre autentica como test_user),
    mas permite trocar a identidade. `test_engine` vem da fixture de
    escopo session do conftest — reusar evita recriar engine por teste.
    """

    async def _override_get_db():
        session_factory = async_sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        async with session_factory() as session:
            yield session

    async def _override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ===== Fixtures de cenário =====

@pytest.fixture
async def activity_with_route(
    db_session: AsyncSession, test_user: User, sample_gpx_bytes: bytes
) -> Activity:
    """Activity do test_user COM rota (route PostGIS + bbox + raw_track_points)."""
    created = await activity_service.create_activity_from_gpx(
        db=db_session,
        user_id=test_user.id,
        file_bytes=sample_gpx_bytes,
        title="Corrida de teste",
    )
    # Recarrega para trazer bbox/raw_track_points (atributos calculados
    # no SELECT do get_activity via _attach_counts).
    return await activity_service.get_activity(
        db_session, test_user.id, created.id
    )


@pytest.fixture
async def activity_no_route(
    db_session: AsyncSession, test_user: User
) -> Activity:
    """Activity do test_user SEM rota (route IS NULL, bbox None)."""
    payload = ActivityCreate(
        activity_type=ActivityType.RUN,
        title="Sem rota",
        started_at=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        duration_s=1800,
        distance_m=5000.0,
        elevation_gain_m=100.0,
    )
    created = await activity_service.create_activity(
        db_session, test_user.id, payload
    )
    return await activity_service.get_activity(
        db_session, test_user.id, created.id
    )


# ===== CSV =====

@pytest.mark.asyncio(loop_scope="function")
async def test_export_csv_owner_ok(
    activity_with_route: Activity, test_user: User, test_engine
):
    type_str = activity_with_route.activity_type.value

    async with _client_as(test_user, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_with_route.id}/export?format=csv"
        )

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    disp = res.headers["content-disposition"]
    assert "attachment" in disp
    assert f"rumo_{activity_with_route.id}_{type_str}.csv" in disp

    lines = [ln for ln in res.text.split("\n") if ln]
    assert len(lines) == 2

    header = lines[0].split(",")
    assert header[0] == "id"
    assert "activity_type" in header
    assert "bbox_min_lon" in header
    assert "bbox_max_lat" in header

    row = lines[1].split(",")
    assert row[0] == str(activity_with_route.id)
    assert row[1] == type_str
    assert row[2] == "Corrida de teste"


@pytest.mark.asyncio(loop_scope="function")
async def test_export_csv_no_route_owner_ok(
    activity_no_route: Activity, test_user: User, test_engine
):
    async with _client_as(test_user, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_no_route.id}/export?format=csv"
        )

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")

    lines = [ln for ln in res.text.split("\n") if ln]
    assert len(lines) == 2

    # Sem rota → bbox_* vazios (4 últimos campos do CSV).
    header = lines[0].split(",")
    row = lines[1].split(",")
    bbox_indices = [
        header.index(c)
        for c in (
            "bbox_min_lon",
            "bbox_min_lat",
            "bbox_max_lon",
            "bbox_max_lat",
        )
    ]
    for idx in bbox_indices:
        assert row[idx] == ""


@pytest.mark.asyncio(loop_scope="function")
async def test_export_csv_nonexistent_activity_404(test_user: User, test_engine):
    fake_id = uuid7()
    async with _client_as(test_user, test_engine) as client:
        res = await client.get(f"/activities/{fake_id}/export?format=csv")
    assert res.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_export_csv_not_follower_404(
    activity_with_route: Activity,
    db_session: AsyncSession,
    test_engine,
):
    other = _make_other_user("otheruser")
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)

    async with _client_as(other, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_with_route.id}/export?format=csv"
        )
    assert res.status_code == 404


@pytest.mark.asyncio(loop_scope="function")
async def test_export_csv_follower_ok(
    activity_with_route: Activity,
    db_session: AsyncSession,
    test_user: User,
    test_engine,
):
    follower = _make_other_user("follower")
    db_session.add(follower)
    await db_session.commit()
    await db_session.refresh(follower)

    # Follow usa following_id (não followed_id). Ref: app/models/follow.py.
    db_session.add(
        Follow(follower_id=follower.id, following_id=test_user.id)
    )
    await db_session.commit()

    async with _client_as(follower, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_with_route.id}/export?format=csv"
        )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")


# ===== GPX =====

@pytest.mark.asyncio(loop_scope="function")
async def test_export_gpx_owner_ok(
    activity_with_route: Activity, test_user: User, test_engine
):
    type_str = activity_with_route.activity_type.value

    async with _client_as(test_user, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_with_route.id}/export?format=gpx"
        )

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/gpx+xml")
    disp = res.headers["content-disposition"]
    assert f"rumo_{activity_with_route.id}_{type_str}.gpx" in disp

    gpx = gpxpy.parse(io.BytesIO(res.content))
    assert len(gpx.tracks) == 1
    assert len(gpx.tracks[0].segments) == 1
    points = gpx.tracks[0].segments[0].points
    assert len(points) >= 2

    # Prova a inversão: raw_track_points tem [[lat, lon, ele, ts], ...]
    # (ordem do upload GPX). O export recebe route em GeoJSON [lon, lat],
    # inverte para lat/lon no <trkpt>. Se os eixos estivessem trocados,
    # latitude do GPX seria ~ -50 (longitude do RS) e o teste falharia
    # grosseiramente.
    raw = activity_with_route.raw_track_points
    assert raw is not None and len(raw) >= 2

    # Compara primeiro e último ponto (bordas). Tolerância 1e-6 cobre o
    # round-trip float→WKT→PostGIS→GeoJSON→float; se estiver trocado,
    # o erro seria ~graus, não ~micro.
    for idx in (0, -1):
        assert points[idx].latitude == pytest.approx(raw[idx][0], abs=1e-6)
        assert points[idx].longitude == pytest.approx(raw[idx][1], abs=1e-6)


@pytest.mark.asyncio(loop_scope="function")
async def test_export_gpx_no_route_404(
    activity_no_route: Activity, test_user: User, test_engine
):
    async with _client_as(test_user, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_no_route.id}/export?format=gpx"
        )
    assert res.status_code == 404
    assert "rota" in res.json()["detail"].lower()


@pytest.mark.asyncio(loop_scope="function")
async def test_export_gpx_not_follower_404(
    activity_with_route: Activity,
    db_session: AsyncSession,
    test_engine,
):
    other = _make_other_user("notfollower")
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)

    async with _client_as(other, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_with_route.id}/export?format=gpx"
        )
    assert res.status_code == 404


# ===== GPX com <time> por <trkpt> — [Sessão 26] =====
#
# A S26 passou a emitir <time> por ponto quando raw_track_points está
# disponível e alinhado com coordinates. Os 2 testes abaixo cobrem:
# 1. Caminho feliz: raw_track_points com 3 timestamps distintos e
#    crescentes → 3 <trkpt> com <time> distintos e crescentes, primeiro
#    igual a started_at. Exercita to_gpx DIRETAMENTE (sem HTTP) porque o
#    que queremos validar é a regra da função, não o contrato da rota
#    (que os testes acima já cobrem).
# 2. Fallback: raw_track_points=None (atividade antiga/JSON) → GPX
#    continua válido; cada <trkpt> recebe <time> == started_at
#    (comportamento S25 preservado).

@pytest.mark.asyncio(loop_scope="function")
async def test_to_gpx_emits_time_per_point_when_raw_track_points_available(
    activity_with_route: Activity,
):
    """to_gpx emite <time> real por ponto quando raw_track_points existe.

    Atividade tem raw_track_points populado pelo upload GPX. Vamos
    substituí-lo por 3 pontos sintéticos com ts distintos (T, T+60,
    T+120) para checar a regra sem depender do sample_run.gpx (que
    tem N pontos — legível, mas dificulta asserts pontuais).
    """
    # Base: primeiro ponto real (para lat/lon válidos). Timestamps
    # sintéticos, distintos e crescentes.
    base_lat = activity_with_route.raw_track_points[0][0]
    base_lon = activity_with_route.raw_track_points[0][1]
    t0 = 1_700_000_000.0  # 2023-11-14T22:13:20Z (UTC)
    synthetic_raw = [
        [base_lat, base_lon, 0.0, t0],
        [base_lat + 0.001, base_lon + 0.001, 0.0, t0 + 60.0],
        [base_lat + 0.002, base_lon + 0.002, 0.0, t0 + 120.0],
    ]
    # coordinates em GeoJSON [lon, lat] — derivadas dos mesmos pontos.
    synthetic_coordinates = [
        [p[1], p[0]] for p in synthetic_raw
    ]

    xml = to_gpx(activity_with_route, synthetic_coordinates, synthetic_raw)
    gpx = gpxpy.parse(io.BytesIO(xml.encode("utf-8")))
    points = gpx.tracks[0].segments[0].points
    assert len(points) == 3

    times = [p.time for p in points]
    assert all(t is not None for t in times)

    # Distintos e crescentes — o ponto principal da S26.
    assert times[0] < times[1] < times[2]

    # Primeiro igual a started_at da atividade (âncora temporal).
    expected_t0 = datetime.fromtimestamp(t0, tz=timezone.utc)
    assert times[0] == expected_t0

    # Passo de 60s entre pontos consecutivos (raw foi construído assim).
    for i in range(1, 3):
        assert times[i] - times[i - 1] == timedelta(seconds=60)


@pytest.mark.asyncio(loop_scope="function")
async def test_to_gpx_falls_back_to_started_at_when_raw_track_points_is_none(
    activity_with_route: Activity,
):
    """Sem raw_track_points, to_gpx usa started_at em todos os <trkpt>.

    Preserva o comportamento da S25 (fallback). Atividades antigas (criadas
    por POST /activities sem track_points) e qualquer divergência de
    comprimento caem aqui — o GPX continua válido e parseável.
    """
    raw = activity_with_route.raw_track_points
    coordinates = [[p[1], p[0]] for p in raw]

    # Passa None explicitamente para simular atividade sem track_points.
    xml = to_gpx(activity_with_route, coordinates, None)
    gpx = gpxpy.parse(io.BytesIO(xml.encode("utf-8")))
    points = gpx.tracks[0].segments[0].points
    assert len(points) == len(coordinates)

    started_at_utc = activity_with_route.started_at
    if started_at_utc.tzinfo is None:
        started_at_utc = started_at_utc.replace(tzinfo=timezone.utc)

    # Todos os <time> iguais a started_at (S25).
    for p in points:
        assert p.time is not None
        assert p.time == started_at_utc


# ===== Validação =====

@pytest.mark.asyncio(loop_scope="function")
async def test_export_invalid_format_422(
    activity_with_route: Activity, test_user: User, test_engine
):
    async with _client_as(test_user, test_engine) as client:
        res = await client.get(
            f"/activities/{activity_with_route.id}/export?format=xpto"
        )
    assert res.status_code == 422


@pytest.mark.asyncio(loop_scope="function")
async def test_export_default_format_is_csv(
    activity_with_route: Activity, test_user: User, test_engine
):
    """Sem ?format → default 'csv' (contrato do front)."""
    async with _client_as(test_user, test_engine) as client:
        res = await client.get(f"/activities/{activity_with_route.id}/export")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")