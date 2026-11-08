"""Testes do export em lote CSV/GPX em ZIP (Sessão 22).

Cobertura:
- CSV em lote: ZIP com N arquivos .csv, cada um com header + 1 linha.
  Inclui atividades sem rota (bbox_* vazios).
- GPX em lote: ZIP com N arquivos .gpx, apenas atividades COM rota
  (as sem rota são omitidas). Prova a inversão [lon,lat]→lat/lon
  comparando com raw_track_points.
- Escopo self-only: atividades de outro usuário NÃO entram no ZIP.
- Filtros from/to: inclusivos nas pontas, em UTC. from > to → 422.
- Casos de borda: usuário sem atividades → 200 + ZIP vazio (0 entries).
- Validação: format inválido → 422; format omitido → csv (default).
- Header: Content-Type application/zip; Content-Disposition com
  rumo_export_<YYYYMMDD-HHMMSS>.zip.

Estratégia de auth: mesmo helper `_client_as(user, test_engine)` da S21
em test_export.py. Sobrescreve get_db (session nova por request usando
test_engine) e get_current_user (user do cenário). Sem sobrescrever
get_db, usaria a engine de produção.

Datas fixas no passado (2024) para o filtro ser determinístico — não
depende de now(). Evita flakiness se a suíte rodar perto da meia-noite.

ATENÇÃO — tipo de atividade:
`sample_run.gpx` não tem <type>running</type>; o <type> interno traduz
para "walk" via map_gpx_type. Por isso os asserts de filename usam
activity.activity_type.value em vez de hardcodar "run".
"""

import io
import zipfile
from datetime import datetime, timezone

import gpxpy
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from uuid6 import uuid7

from app.core.dependencies import get_current_user
from app.database import get_db
from app.main import app
from app.models.activity import Activity, ActivityType
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.services import activity_service


# ===== Helpers =====

def _make_other_user(username: str) -> User:
    """User não commitado, para cenários de escopo (self-only)."""
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


async def _create_activity_with_date(
    db_session: AsyncSession,
    user_id,
    *,
    started_at: datetime,
    title: str,
    activity_type: ActivityType = ActivityType.RUN,
    with_track_points: list[list[float]] | None = None,
    distance_m: float = 5000.0,
    duration_s: int = 1800,
) -> Activity:
    """Cria uma Activity com started_at controlado.

    Se with_track_points vier, o points_to_linestring do service monta a
    route PostGIS — usado para o cenário de GPX em lote. Caso contrário,
    route IS NULL (CSV funciona, GPX omite).
    """
    payload = ActivityCreate(
        activity_type=activity_type,
        title=title,
        started_at=started_at,
        duration_s=duration_s,
        distance_m=distance_m,
        elevation_gain_m=100.0,
        track_points=with_track_points,
    )
    created = await activity_service.create_activity(db_session, user_id, payload)
    return await activity_service.get_activity(db_session, user_id, created.id)


def _read_zip_entries(content: bytes) -> dict[str, bytes]:
    """Abre o ZIP em memória e devolve {nome_do_arquivo: bytes}."""
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        return {name: zf.read(name) for name in zf.namelist()}


# ===== CSV em lote =====

@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_csv_owner_ok(
    db_session: AsyncSession, test_user: User, test_engine
):
    """2 atividades → ZIP com 2 .csv, cada um header + 1 linha, valores batem."""
    a1 = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 1, 10, 10, 0, tzinfo=timezone.utc),
        title="Primeira",
        activity_type=ActivityType.RUN,
    )
    a2 = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 1, 20, 10, 0, tzinfo=timezone.utc),
        title="Segunda",
        activity_type=ActivityType.WALK,
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=csv")

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    disp = res.headers["content-disposition"]
    assert "attachment" in disp
    assert "rumo_export_" in disp and ".zip" in disp

    entries = _read_zip_entries(res.content)
    assert len(entries) == 2

    t1 = a1.activity_type.value
    t2 = a2.activity_type.value
    name1 = f"rumo_{a1.id}_{t1}.csv"
    name2 = f"rumo_{a2.id}_{t2}.csv"
    assert name1 in entries
    assert name2 in entries

    # Cada CSV tem header + 1 linha.
    for name, expected_title in ((name1, "Primeira"), (name2, "Segunda")):
        text = entries[name].decode("utf-8")
        lines = [ln for ln in text.split("\n") if ln]
        assert len(lines) == 2
        header = lines[0].split(",")
        row = lines[1].split(",")
        assert header[0] == "id"
        assert "activity_type" in header
        assert "bbox_min_lon" in header
        assert row[0] == str(a1.id) if name == name1 else row[0] == str(a2.id)
        assert row[2] == expected_title


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_csv_includes_no_route(
    db_session: AsyncSession, test_user: User, test_engine
):
    """Atividade SEM rota entra no CSV em lote (bbox_* vazios)."""
    no_route = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 2, 1, 10, 0, tzinfo=timezone.utc),
        title="Sem rota",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=csv")

    entries = _read_zip_entries(res.content)
    name = f"rumo_{no_route.id}_{no_route.activity_type.value}.csv"
    assert name in entries

    text = entries[name].decode("utf-8")
    lines = [ln for ln in text.split("\n") if ln]
    header = lines[0].split(",")
    row = lines[1].split(",")
    for col in (
        "bbox_min_lon", "bbox_min_lat", "bbox_max_lon", "bbox_max_lat"
    ):
        assert row[header.index(col)] == ""


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_csv_only_own_activities(
    db_session: AsyncSession, test_user: User, test_engine
):
    """Atividades de outro usuário NÃO entram no ZIP (self-only)."""
    other = _make_other_user("otherbulk")
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)

    own = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 3, 1, 10, 0, tzinfo=timezone.utc),
        title="Minha",
    )
    await _create_activity_with_date(
        db_session, other.id,
        started_at=datetime(2024, 3, 2, 10, 0, tzinfo=timezone.utc),
        title="Do outro",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=csv")

    entries = _read_zip_entries(res.content)
    assert len(entries) == 1
    expected = f"rumo_{own.id}_{own.activity_type.value}.csv"
    assert expected in entries


# ===== GPX em lote =====

@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_gpx_skips_no_route(
    db_session: AsyncSession, test_user: User, test_engine
):
    """1 com rota + 1 sem → ZIP só com o .gpx da com rota."""
    # Rota sintética: 3 pontos [lat, lon, ele, ts].
    track_points = [
        [-23.5505, -46.6333, 700.0, 1700000000.0],
        [-23.5510, -46.6340, 705.0, 1700000060.0],
        [-23.5515, -46.6345, 710.0, 1700000120.0],
    ]
    with_route = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 4, 1, 10, 0, tzinfo=timezone.utc),
        title="Com rota",
        activity_type=ActivityType.CYCLE,
        with_track_points=track_points,
    )
    await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 4, 2, 10, 0, tzinfo=timezone.utc),
        title="Sem rota",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=gpx")

    entries = _read_zip_entries(res.content)
    assert len(entries) == 1
    name = f"rumo_{with_route.id}_{with_route.activity_type.value}.gpx"
    assert name in entries

    # Prova a inversão [lon,lat]→lat/lon comparando com raw_track_points.
    gpx = gpxpy.parse(io.BytesIO(entries[name]))
    points = gpx.tracks[0].segments[0].points
    raw = with_route.raw_track_points
    for idx in (0, -1):
        assert points[idx].latitude == pytest.approx(raw[idx][0], abs=1e-6)
        assert points[idx].longitude == pytest.approx(raw[idx][1], abs=1e-6)


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_gpx_all_no_route_empty_zip(
    db_session: AsyncSession, test_user: User, test_engine
):
    """Só atividades sem rota + format=gpx → ZIP vazio (0 entries), 200."""
    await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 5, 1, 10, 0, tzinfo=timezone.utc),
        title="Sem rota 1",
    )
    await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 5, 2, 10, 0, tzinfo=timezone.utc),
        title="Sem rota 2",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=gpx")

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    entries = _read_zip_entries(res.content)
    assert entries == {}


# ===== Casos de borda =====

@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_empty_user_ok(test_user: User, test_engine):
    """Usuário sem atividades → 200 + ZIP vazio (0 entries)."""
    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=csv")

    assert res.status_code == 200
    entries = _read_zip_entries(res.content)
    assert entries == {}


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_date_from_filter(
    db_session: AsyncSession, test_user: User, test_engine
):
    """from=2024-02-01 corta as atividades anteriores."""
    old = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
        title="Antiga",
    )
    new = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 2, 15, 10, 0, tzinfo=timezone.utc),
        title="Nova",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=csv&from=2024-02-01")

    entries = _read_zip_entries(res.content)
    assert len(entries) == 1
    expected = f"rumo_{new.id}_{new.activity_type.value}.csv"
    assert expected in entries
    assert f"rumo_{old.id}_{old.activity_type.value}.csv" not in entries


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_date_to_filter(
    db_session: AsyncSession, test_user: User, test_engine
):
    """to=2024-02-29 inclui o dia inteiro (inclusivo nas pontas)."""
    before = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 2, 29, 23, 59, tzinfo=timezone.utc),
        title="Antes da meia-noite",
    )
    after = await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 3, 1, 0, 1, tzinfo=timezone.utc),
        title="Depois da meia-noite",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=csv&to=2024-02-29")

    entries = _read_zip_entries(res.content)
    assert len(entries) == 1
    assert f"rumo_{before.id}_{before.activity_type.value}.csv" in entries
    assert f"rumo_{after.id}_{after.activity_type.value}.csv" not in entries


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_from_after_to_422(
    db_session: AsyncSession, test_user: User, test_engine
):
    """from > to → 422 com detail claro."""
    await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
        title="Qualquer",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get(
            "/activities/export?format=csv&from=2024-06-10&to=2024-06-01"
        )

    assert res.status_code == 422
    assert "from" in res.json()["detail"].lower()


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_invalid_format_422(
    db_session: AsyncSession, test_user: User, test_engine
):
    """format=xpto → 422 (Literal do Pydantic)."""
    await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 7, 1, 10, 0, tzinfo=timezone.utc),
        title="Qualquer",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export?format=xpto")

    assert res.status_code == 422


@pytest.mark.asyncio(loop_scope="function")
async def test_export_bulk_default_format_is_csv(
    db_session: AsyncSession, test_user: User, test_engine
):
    """Sem ?format → default 'csv' (ZIP de .csv)."""
    await _create_activity_with_date(
        db_session, test_user.id,
        started_at=datetime(2024, 8, 1, 10, 0, tzinfo=timezone.utc),
        title="Default",
    )

    async with _client_as(test_user, test_engine) as client:
        res = await client.get("/activities/export")

    assert res.status_code == 200
    entries = _read_zip_entries(res.content)
    assert len(entries) == 1
    (name,) = entries.keys()
    assert name.endswith(".csv")