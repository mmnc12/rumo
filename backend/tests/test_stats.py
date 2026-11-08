"""Testes de stats_service: get_summary, get_period_stats e get_by_type.

Cobertura:
- Service puro (db_session): somas, filtros, tratamento de None, isolamento
  entre usuários, períodos semana/mês com datas fixas (sem now()).
- Rota HTTP (client): shape de resposta, filtro por tipo, limites de
  validação (weeks/months) e integração service → schema.

Filosofia: datas determinísticas (nada de datetime.now()) para eliminar
flakiness de fuso/relógio. Todos os inserts usam o ORM com ActivityType
enum nativo, e os filtros usam string (o que o router de fato recebe).

Exceção [Sessão 17]: os testes de `period` (all|90d|1y) usam
`datetime.now(timezone.utc) - timedelta(days=N)` porque o filtro
depende de `now()` do banco. Para evitar flakiness, as margens entre
"dentro" e "fora" da janela são ≥10 dias — folga absurdamente maior que
qualquer desvio de relógio entre o processo de teste e o Postgres.

Exceção [Sessão 18]: os testes de `previous` (janela anterior) seguem a
mesma regra — usam `_dt_ago(days)` e a atividade "de referência" fica
bem no meio da janela (ex.: 45d para 90d, 200d para 1y), longe das
bordas `now-90d`/`now-180d`/`now-365d`/`now-730d`, para não flakar por
relógio.

Paths de rota: o router `activities.py` é incluído no main.py com
`prefix="/activities"`. Como as rotas de stats já declaram `/stats/...`
no próprio router, o path final é `/activities/stats/summary`, etc.

[Sessão 14 — B1] Adicionados testes de get_by_type (drill-down por tipo)
e da rota /activities/stats/by-type.

[Sessão 17] Adicionados testes de `period` (all|90d|1y) — service e rota.

[Sessão 18] Adicionados testes de `previous` — janela imediatamente
anterior (90d→[now-180d, now-90d); 1y→[now-730d, now-365d)). `all` →
`previous is None`. Testa service e rota.

[Sessão 19] Adicionados testes das stats públicas em perfis de terceiros
(/users/{user_id}/stats/*). Regra: dono OU seguidor do dono. Viewer não
seguidor → 403; user_id inexistente → 404. Helper `client_as(user)`
sobrescreve get_current_user localmente, sem tocar no conftest.

[Sessão 20] Adicionados testes de `compare=prev|yoy` no get_by_type —
janela de comparação configurável. `prev` (default) = janela imediatamente
anterior (S18); `yoy` = mesmo período do ano anterior (90d→[now-455d,
now-365d); 1y→[now-730d, now-365d) — idêntico a prev, coincidência
matemática documentada). Testa service e rota.
"""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from app.core.dependencies import get_current_user
from app.database import get_db
from app.main import app
from app.models.activity import Activity, ActivityType
from app.models.follow import Follow
from app.models.user import User
from app.services import stats_service


# ===== Helpers =====

def _dt(year: int, month: int, day: int, hour: int = 10) -> datetime:
    """Datetime UTC determinístico — nunca usa now()."""
    return datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc)


def _dt_ago(days: int, hour: int = 10) -> datetime:
    """[Sessão 17] Datetime UTC relativo a now() — só para testes de `period`.

    Usado exclusivamente porque o filtro `period` (all|90d|1y) é aplicado
    em SQL via `now() - INTERVAL`. Fora dele, `_dt` (fixo) continua sendo
    o padrão. Margem mínima de 10 dias entre "dentro" e "fora" da janela
    elimina qualquer flakiness de relógio Python vs. Postgres.

    [Sessão 18] Também usado pelos testes de `previous` (janela anterior).
    [Sessão 20] Também usado pelos testes de `compare=yoy`.
    """
    return datetime.now(timezone.utc) - timedelta(days=days)


async def _make_activity(
    db: AsyncSession,
    user: User,
    *,
    activity_type: ActivityType = ActivityType.RUN,
    started_at: datetime | None = None,
    distance_m: float | None = 5000.0,
    duration_s: int | None = 1800,
    elevation_gain_m: float | None = 100.0,
    calories: int | None = 300,
) -> Activity:
    """Insere uma Activity com valores explícitos. Sem create_activity
    (que recalcularia calories a partir do MET/peso — aqui queremos
    controlar tudo)."""
    activity = Activity(
        id=uuid7(),
        user_id=user.id,
        activity_type=activity_type,
        started_at=started_at or _dt(2026, 1, 5),
        distance_m=distance_m,
        duration_s=duration_s,
        elevation_gain_m=elevation_gain_m,
        calories=calories,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def _make_other_user(db: AsyncSession, username: str = "otheruser") -> User:
    """Segundo usuário pra testes de isolamento."""
    user = User(
        id=uuid7(),
        email=f"{username}@rumo.com",
        username=username,
        hashed_password="x",
        full_name="Other User",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# [Sessão 19] Cria relação de follow direto no banco (sem notification).
async def _make_follow(
    db: AsyncSession, follower: User, following: User
) -> Follow:
    follow = Follow(follower_id=follower.id, following_id=following.id)
    db.add(follow)
    await db.commit()
    await db.refresh(follow)
    return follow


# [Sessão 19] AsyncClient "logado como outro usuário".
# O `client` do conftest sobrescreve get_current_user para `test_user`
# fixo. Para testar permissão (viewer != dono), precisamos de um client
# cujo current_user seja outro usuário. Não tocamos no conftest:
# montamos o override aqui, reaproveitando o `test_engine` (session-scoped)
# para o mesmo banco de teste.
def _client_as(user: User, test_engine):
    async def _override_get_db():
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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

    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ===== get_summary — service =====


@pytest.mark.asyncio
async def test_get_summary_empty_returns_zeros(db_session, test_user):
    result = await stats_service.get_summary(db_session, test_user.id)

    assert result["total_activities"] == 0
    assert result["total_distance_m"] == 0.0
    assert result["total_duration_s"] == 0
    assert result["total_elevation_gain_m"] == 0.0
    assert result["total_calories"] == 0
    assert result["avg_pace_s_per_km"] is None
    assert result["avg_speed_mps"] is None


@pytest.mark.asyncio
async def test_get_summary_sums_all_fields(db_session, test_user):
    await _make_activity(
        db_session, test_user,
        distance_m=5000.0, duration_s=1800,
        elevation_gain_m=100.0, calories=300,
    )
    await _make_activity(
        db_session, test_user,
        distance_m=3000.0, duration_s=1200,
        elevation_gain_m=50.0, calories=200,
    )

    result = await stats_service.get_summary(db_session, test_user.id)

    assert result["total_activities"] == 2
    assert result["total_distance_m"] == pytest.approx(8000.0)
    assert result["total_duration_s"] == 3000
    assert result["total_elevation_gain_m"] == pytest.approx(150.0)
    assert result["total_calories"] == 500
    # pace = 3000s / (8000m / 1000) = 375 s/km
    assert result["avg_pace_s_per_km"] == pytest.approx(375.0)
    # speed = 8000m / 3000s ≈ 2.6667 m/s
    assert result["avg_speed_mps"] == pytest.approx(8000.0 / 3000.0)


@pytest.mark.asyncio
async def test_get_summary_none_calories_treated_as_zero(db_session, test_user):
    await _make_activity(db_session, test_user, calories=400)
    await _make_activity(db_session, test_user, calories=None)

    result = await stats_service.get_summary(db_session, test_user.id)

    assert result["total_activities"] == 2
    assert result["total_calories"] == 400


@pytest.mark.asyncio
async def test_get_summary_zero_distance_pace_is_none(db_session, test_user):
    await _make_activity(
        db_session, test_user,
        distance_m=0.0, duration_s=600, calories=50,
    )

    result = await stats_service.get_summary(db_session, test_user.id)

    assert result["avg_pace_s_per_km"] is None
    # speed = 0 / 600 = 0.0 (não None — duration > 0)
    assert result["avg_speed_mps"] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_get_summary_zero_duration_speed_is_none(db_session, test_user):
    await _make_activity(
        db_session, test_user,
        distance_m=1000.0, duration_s=0, calories=10,
    )

    result = await stats_service.get_summary(db_session, test_user.id)

    # pace = 0 / (1000/1000) = 0.0 (não None — distance > 0)
    assert result["avg_pace_s_per_km"] == pytest.approx(0.0)
    assert result["avg_speed_mps"] is None


@pytest.mark.asyncio
async def test_get_summary_filters_by_type(db_session, test_user):
    await _make_activity(db_session, test_user, activity_type=ActivityType.RUN,
                         distance_m=5000.0, calories=300)
    await _make_activity(db_session, test_user, activity_type=ActivityType.CYCLE,
                         distance_m=20000.0, calories=800)

    run_only = await stats_service.get_summary(
        db_session, test_user.id, activity_type="run"
    )
    assert run_only["total_activities"] == 1
    assert run_only["total_distance_m"] == pytest.approx(5000.0)
    assert run_only["total_calories"] == 300

    cycle_only = await stats_service.get_summary(
        db_session, test_user.id, activity_type="cycle"
    )
    assert cycle_only["total_activities"] == 1
    assert cycle_only["total_distance_m"] == pytest.approx(20000.0)

    no_filter = await stats_service.get_summary(db_session, test_user.id)
    assert no_filter["total_activities"] == 2
    assert no_filter["total_distance_m"] == pytest.approx(25000.0)


@pytest.mark.asyncio
async def test_get_summary_ignores_other_users(db_session, test_user):
    other = await _make_other_user(db_session)

    await _make_activity(db_session, test_user, distance_m=1000.0, calories=100)
    await _make_activity(db_session, other, distance_m=9999.0, calories=999)

    result = await stats_service.get_summary(db_session, test_user.id)
    assert result["total_activities"] == 1
    assert result["total_distance_m"] == pytest.approx(1000.0)
    assert result["total_calories"] == 100


# ===== get_period_stats — service =====


@pytest.mark.asyncio
async def test_get_period_stats_empty_returns_empty_list(db_session, test_user):
    result = await stats_service.get_period_stats(
        db_session, test_user.id, "week", limit_periods=8
    )
    assert result == []


@pytest.mark.asyncio
async def test_get_period_stats_groups_by_week(db_session, test_user):
    # 2026-01-05 (seg) e 2026-01-06 (ter) → mesma semana
    # 2026-01-12 (seg) → semana seguinte
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 5), distance_m=1000.0, calories=100)
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 6), distance_m=2000.0, calories=200)
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 12), distance_m=3000.0, calories=300)

    result = await stats_service.get_period_stats(
        db_session, test_user.id, "week", limit_periods=8
    )

    assert len(result) == 2
    # Ordem desc: semana de 12/01 primeiro
    first = result[0]
    assert first["period_start"] == _dt(2026, 1, 12).date()
    assert first["total_activities"] == 1
    assert first["total_distance_m"] == pytest.approx(3000.0)
    assert first["total_calories"] == 300

    second = result[1]
    assert second["period_start"] == _dt(2026, 1, 5).date()  # date_trunc → segunda
    assert second["total_activities"] == 2
    assert second["total_distance_m"] == pytest.approx(3000.0)
    assert second["total_calories"] == 300


@pytest.mark.asyncio
async def test_get_period_stats_groups_by_month(db_session, test_user):
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 5), distance_m=1000.0, calories=100)
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 20), distance_m=2000.0, calories=200)
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 2, 3), distance_m=3000.0, calories=300)

    result = await stats_service.get_period_stats(
        db_session, test_user.id, "month", limit_periods=6
    )

    assert len(result) == 2
    assert result[0]["period_start"] == _dt(2026, 2, 1).date()
    assert result[0]["total_activities"] == 1
    assert result[0]["total_distance_m"] == pytest.approx(3000.0)

    assert result[1]["period_start"] == _dt(2026, 1, 1).date()
    assert result[1]["total_activities"] == 2
    assert result[1]["total_distance_m"] == pytest.approx(3000.0)
    assert result[1]["total_calories"] == 300


@pytest.mark.asyncio
async def test_get_period_stats_respects_limit(db_session, test_user):
    await _make_activity(db_session, test_user, started_at=_dt(2026, 1, 5))
    await _make_activity(db_session, test_user, started_at=_dt(2026, 1, 12))
    await _make_activity(db_session, test_user, started_at=_dt(2026, 1, 19))

    result = await stats_service.get_period_stats(
        db_session, test_user.id, "week", limit_periods=2
    )

    assert len(result) == 2
    # Só as 2 semanas mais recentes
    assert result[0]["period_start"] == _dt(2026, 1, 19).date()
    assert result[1]["period_start"] == _dt(2026, 1, 12).date()


@pytest.mark.asyncio
async def test_get_period_stats_sums_calories_with_none(
    db_session, test_user
):
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 5), calories=100)
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 6), calories=None)

    result = await stats_service.get_period_stats(
        db_session, test_user.id, "week", limit_periods=8
    )

    assert len(result) == 1
    assert result[0]["total_activities"] == 2
    assert result[0]["total_calories"] == 100


@pytest.mark.asyncio
async def test_get_period_stats_filters_by_type(db_session, test_user):
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt(2026, 1, 5), calories=100)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt(2026, 1, 5), calories=500)

    result = await stats_service.get_period_stats(
        db_session, test_user.id, "week", limit_periods=8, activity_type="run"
    )

    assert len(result) == 1
    assert result[0]["total_activities"] == 1
    assert result[0]["total_calories"] == 100


@pytest.mark.asyncio
async def test_get_period_stats_ignores_other_users(db_session, test_user):
    other = await _make_other_user(db_session)
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 5), calories=100)
    await _make_activity(db_session, other,
                         started_at=_dt(2026, 1, 5), calories=999)

    result = await stats_service.get_period_stats(
        db_session, test_user.id, "week", limit_periods=8
    )

    assert len(result) == 1
    assert result[0]["total_activities"] == 1
    assert result[0]["total_calories"] == 100


# ===== Rotas HTTP — integração service → schema → response =====
# Paths reais: /activities/stats/* (main.py inclui activities.router com
# prefix="/activities", e as rotas já declaram "/stats/..." no router).


@pytest.mark.asyncio
async def test_route_summary_empty(client, db_session, test_user):
    response = await client.get("/activities/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 0
    assert data["total_distance_m"] == 0.0
    assert data["avg_pace_s_per_km"] is None
    assert data["avg_speed_mps"] is None


@pytest.mark.asyncio
async def test_route_summary_with_data(client, db_session, test_user):
    await _make_activity(db_session, test_user,
                         distance_m=5000.0, duration_s=1800,
                         elevation_gain_m=100.0, calories=300)

    response = await client.get("/activities/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 1
    assert data["total_distance_m"] == pytest.approx(5000.0)
    assert data["total_duration_s"] == 1800
    assert data["total_elevation_gain_m"] == pytest.approx(100.0)
    assert data["total_calories"] == 300


@pytest.mark.asyncio
async def test_route_summary_filter_by_type(client, db_session, test_user):
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE, calories=800)

    response = await client.get(
        "/activities/stats/summary", params={"activity_type": "run"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 1
    assert data["total_calories"] == 300


@pytest.mark.asyncio
async def test_route_weekly_shape(client, db_session, test_user):
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 1, 5), calories=100)

    response = await client.get("/activities/stats/weekly", params={"weeks": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["weeks"] == 2
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["period_start"] == "2026-01-05"
    assert item["total_activities"] == 1
    assert item["total_calories"] == 100


@pytest.mark.asyncio
async def test_route_monthly_shape(client, db_session, test_user):
    await _make_activity(db_session, test_user,
                         started_at=_dt(2026, 2, 3), calories=300)

    response = await client.get("/activities/stats/monthly", params={"months": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["months"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["period_start"] == "2026-02-01"
    assert data["items"][0]["total_calories"] == 300


@pytest.mark.asyncio
async def test_route_weekly_weeks_lower_bound(client, db_session, test_user):
    response = await client.get("/activities/stats/weekly", params={"weeks": 0})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_route_weekly_weeks_upper_bound(client, db_session, test_user):
    response = await client.get("/activities/stats/weekly", params={"weeks": 53})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_route_monthly_months_upper_bound(client, db_session, test_user):
    response = await client.get("/activities/stats/monthly", params={"months": 25})
    assert response.status_code == 422


# ===== get_by_type — service [Sessão 14 — B1] =====


@pytest.mark.asyncio
async def test_get_by_type_empty_returns_empty_list(db_session, test_user):
    result = await stats_service.get_by_type(db_session, test_user.id)
    assert result == []


@pytest.mark.asyncio
async def test_get_by_type_groups_and_orders(db_session, test_user):
    # 2 runs + 1 cycle → run primeiro (mais atividades), depois cycle.
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         distance_m=5000.0, duration_s=1800,
                         elevation_gain_m=100.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         distance_m=3000.0, duration_s=1200,
                         elevation_gain_m=50.0, calories=200)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         distance_m=20000.0, duration_s=3600,
                         elevation_gain_m=400.0, calories=800)

    result = await stats_service.get_by_type(db_session, test_user.id)

    assert len(result) == 2
    run = result[0]
    assert run["activity_type"] == "run"
    assert run["total_activities"] == 2
    assert run["total_distance_m"] == pytest.approx(8000.0)
    assert run["total_duration_s"] == 3000
    assert run["total_elevation_gain_m"] == pytest.approx(150.0)
    assert run["total_calories"] == 500

    cycle = result[1]
    assert cycle["activity_type"] == "cycle"
    assert cycle["total_activities"] == 1
    assert cycle["total_distance_m"] == pytest.approx(20000.0)
    assert cycle["total_calories"] == 800


@pytest.mark.asyncio
async def test_get_by_type_tie_breaks_by_type_asc(db_session, test_user):
    # 1 run + 1 cycle → empate em total_activities; desempate alfabético:
    # "cycle" < "run", então cycle vem primeiro.
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN, calories=100)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE, calories=500)

    result = await stats_service.get_by_type(db_session, test_user.id)

    assert len(result) == 2
    assert result[0]["activity_type"] == "cycle"
    assert result[1]["activity_type"] == "run"


@pytest.mark.asyncio
async def test_get_by_type_handles_none_calories(db_session, test_user):
    await _make_activity(db_session, test_user, calories=100)
    await _make_activity(db_session, test_user, calories=None)

    result = await stats_service.get_by_type(db_session, test_user.id)

    assert len(result) == 1
    assert result[0]["activity_type"] == "run"
    assert result[0]["total_activities"] == 2
    assert result[0]["total_calories"] == 100


@pytest.mark.asyncio
async def test_get_by_type_ignores_other_users(db_session, test_user):
    other = await _make_other_user(db_session)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN, calories=100)
    await _make_activity(db_session, other,
                         activity_type=ActivityType.CYCLE, calories=999)

    result = await stats_service.get_by_type(db_session, test_user.id)

    assert len(result) == 1
    assert result[0]["activity_type"] == "run"
    assert result[0]["total_activities"] == 1


# ===== Rota /activities/stats/by-type [Sessão 14 — B1] =====


@pytest.mark.asyncio
async def test_route_by_type_empty(client, db_session, test_user):
    response = await client.get("/activities/stats/by-type")
    assert response.status_code == 200
    data = response.json()
    assert data == {"items": []}


@pytest.mark.asyncio
async def test_route_by_type_shape(client, db_session, test_user):
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         distance_m=5000.0, duration_s=1800,
                         elevation_gain_m=100.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         distance_m=20000.0, duration_s=3600,
                         elevation_gain_m=400.0, calories=800)

    response = await client.get("/activities/stats/by-type")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    # run e cycle têm 1 atividade cada; desempate "cycle" < "run"
    assert data["items"][0]["activity_type"] == "cycle"
    assert data["items"][0]["total_activities"] == 1
    assert data["items"][0]["total_distance_m"] == pytest.approx(20000.0)
    assert data["items"][1]["activity_type"] == "run"


# ===== get_by_type com period — service [Sessão 17] =====


@pytest.mark.asyncio
async def test_get_by_type_period_all_is_baseline(db_session, test_user):
    """`period="all"` (default) preserva o comportamento original: inclui
    atividades antigas e recentes, sem filtrar por data."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(100), calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt_ago(30), calories=800)

    result = await stats_service.get_by_type(db_session, test_user.id, period="all")

    assert len(result) == 2
    types = {r["activity_type"] for r in result}
    assert types == {"run", "cycle"}


@pytest.mark.asyncio
async def test_get_by_type_period_90d_excludes_old(db_session, test_user):
    """`period="90d"` inclui atividade de 30 dias atrás e exclui a de 100
    dias atrás (fora da janela)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(100), calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt_ago(30), calories=800)

    result = await stats_service.get_by_type(db_session, test_user.id, period="90d")

    assert len(result) == 1
    assert result[0]["activity_type"] == "cycle"
    assert result[0]["total_activities"] == 1
    assert result[0]["total_calories"] == 800


@pytest.mark.asyncio
async def test_get_by_type_period_1y_excludes_older_than_365d(
    db_session, test_user
):
    """`period="1y"` inclui atividade de 300 dias atrás e exclui a de 400
    dias atrás (fora da janela de 365 dias)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(400), calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt_ago(300), calories=800)

    result = await stats_service.get_by_type(db_session, test_user.id, period="1y")

    assert len(result) == 1
    assert result[0]["activity_type"] == "cycle"
    assert result[0]["total_activities"] == 1
    assert result[0]["total_calories"] == 800


@pytest.mark.asyncio
async def test_get_by_type_period_1y_is_superset_of_90d(db_session, test_user):
    """30d e 200d aparecem em `1y`, só 30d aparece em `90d`."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(30), calories=100)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt_ago(200), calories=500)

    one_year = await stats_service.get_by_type(
        db_session, test_user.id, period="1y"
    )
    ninety_days = await stats_service.get_by_type(
        db_session, test_user.id, period="90d"
    )

    assert {r["activity_type"] for r in one_year} == {"run", "cycle"}
    assert {r["activity_type"] for r in ninety_days} == {"run"}


# ===== Rota /activities/stats/by-type com period [Sessão 17] =====


@pytest.mark.asyncio
async def test_route_by_type_period_param(client, db_session, test_user):
    """?period=90d filtra na rota — mesma semântica do service."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(100), calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt_ago(30), calories=800)

    response = await client.get(
        "/activities/stats/by-type", params={"period": "90d"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["activity_type"] == "cycle"
    assert data["items"][0]["total_calories"] == 800


@pytest.mark.asyncio
async def test_route_by_type_invalid_period_returns_422(
    client, db_session, test_user
):
    """Valor fora de {all, 90d, 1y} → 422 (Literal do FastAPI)."""
    response = await client.get(
        "/activities/stats/by-type", params={"period": "30d"}
    )
    assert response.status_code == 422


# ===== get_by_type com previous — service [Sessão 18] =====
# Regra de janela: "anterior" = janela imediatamente anterior, sem
# sobreposição. 90d → [now-180d, now-90d); 1y → [now-730d, now-365d).
# Margens: toda atividade "de referência" fica bem no meio da janela
# (45d para 90d; 200d para 1y), longe das bordas, para não flakar.


@pytest.mark.asyncio
async def test_get_by_type_previous_90d(db_session, test_user):
    """Atividade dentro dos 90d atuais + atividade entre 90d e 180d
    atrás → item atual reflete só a recente; `previous` reflete só a
    antiga."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(45),
                         distance_m=5000.0, duration_s=1800,
                         elevation_gain_m=100.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(120),
                         distance_m=3000.0, duration_s=1200,
                         elevation_gain_m=50.0, calories=200)

    result = await stats_service.get_by_type(
        db_session, test_user.id, period="90d"
    )

    assert len(result) == 1
    run = result[0]
    assert run["activity_type"] == "run"
    # Janela atual (45d): só a primeira.
    assert run["total_activities"] == 1
    assert run["total_distance_m"] == pytest.approx(5000.0)
    assert run["total_duration_s"] == 1800
    assert run["total_elevation_gain_m"] == pytest.approx(100.0)
    assert run["total_calories"] == 300
    # Janela anterior (120d): só a segunda.
    prev = run["previous"]
    assert prev is not None
    assert prev["total_activities"] == 1
    assert prev["total_distance_m"] == pytest.approx(3000.0)
    assert prev["total_duration_s"] == 1200
    assert prev["total_elevation_gain_m"] == pytest.approx(50.0)
    assert prev["total_calories"] == 200


@pytest.mark.asyncio
async def test_get_by_type_previous_1y(db_session, test_user):
    """`period="1y"`: atual = 200d (dentro de 365d); anterior = 500d
    (entre 365d e 730d)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(200),
                         distance_m=4000.0, calories=250)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(500),
                         distance_m=6000.0, calories=350)

    result = await stats_service.get_by_type(
        db_session, test_user.id, period="1y"
    )

    assert len(result) == 1
    run = result[0]
    assert run["total_activities"] == 1
    assert run["total_distance_m"] == pytest.approx(4000.0)
    assert run["total_calories"] == 250

    prev = run["previous"]
    assert prev is not None
    assert prev["total_activities"] == 1
    assert prev["total_distance_m"] == pytest.approx(6000.0)
    assert prev["total_calories"] == 350


@pytest.mark.asyncio
async def test_get_by_type_previous_all_is_none(db_session, test_user):
    """`period="all"` → sem comparação: `previous is None` em todo item."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(30), calories=100)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.CYCLE,
                         started_at=_dt_ago(200), calories=500)

    result = await stats_service.get_by_type(db_session, test_user.id, period="all")

    assert len(result) == 2
    for item in result:
        assert item["previous"] is None


@pytest.mark.asyncio
async def test_get_by_type_previous_none_when_type_absent_in_window(
    db_session, test_user
):
    """Tipo com atividade só na janela atual (nada na anterior) → item
    existe com `previous is None`. Garante que o `null` não mascara o
    item: o tipo aparece, mas sem comparação."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(30), calories=100)

    result = await stats_service.get_by_type(
        db_session, test_user.id, period="90d"
    )

    assert len(result) == 1
    run = result[0]
    assert run["activity_type"] == "run"
    assert run["total_activities"] == 1
    assert run["previous"] is None


# ===== Rota /activities/stats/by-type com previous [Sessão 18] =====


@pytest.mark.asyncio
async def test_route_by_type_previous_shape(client, db_session, test_user):
    """Shape do `previous` na rota, para period=90d e period=all."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(45),
                         distance_m=5000.0, duration_s=1800,
                         elevation_gain_m=100.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(120),
                         distance_m=3000.0, duration_s=1200,
                         elevation_gain_m=50.0, calories=200)

    # period=90d: previous preenchido com as 5 métricas.
    response = await client.get(
        "/activities/stats/by-type", params={"period": "90d"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["activity_type"] == "run"
    assert item["total_activities"] == 1
    prev = item["previous"]
    assert prev is not None
    assert set(prev.keys()) == {
        "total_activities",
        "total_distance_m",
        "total_duration_s",
        "total_elevation_gain_m",
        "total_calories",
    }
    assert prev["total_activities"] == 1
    assert prev["total_distance_m"] == pytest.approx(3000.0)
    assert prev["total_calories"] == 200

    # period=all: previous é null em todos os itens.
    response_all = await client.get(
        "/activities/stats/by-type", params={"period": "all"}
    )
    assert response_all.status_code == 200
    for it in response_all.json()["items"]:
        assert it["previous"] is None


# ===== Stats públicas em perfis de terceiros [Sessão 19] =====
# Regra: dono OU seguidor do dono (mesma do /activities/{id}/track).
# Viewer não seguidor → 403. user_id inexistente → 404 (não vaza existência).
#
# O `client` padrão do conftest é "logado" como test_user. Para simular
# um viewer diferente, usamos _client_as(viewer, test_engine) — que monta
# override local de get_current_user sem tocar no conftest.
#
# Convenção dos testes abaixo:
# - `owner` = dono das atividades (test_user, o "viewer padrão" é ele mesmo
#   no teste de regressão self).
# - `viewer` = outro usuário (sem follow, ou com follow, conforme o teste).


@pytest.mark.asyncio
async def test_user_stats_summary_self_ok(client, db_session, test_user):
    """Regressão: /users/{meu_id}/stats/summary funciona igual ao antigo
    /activities/stats/summary (self sempre permitido, sem exigir follow)."""
    await _make_activity(
        db_session, test_user,
        distance_m=5000.0, duration_s=1800, calories=300,
    )

    response = await client.get(f"/users/{test_user.id}/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 1
    assert data["total_distance_m"] == pytest.approx(5000.0)
    assert data["total_calories"] == 300


@pytest.mark.asyncio
async def test_user_stats_summary_forbidden_when_not_following(
    db_session, test_user, test_engine
):
    """Viewer que NÃO segue o dono → 403 (mesma regra do /track)."""
    owner = test_user
    viewer = await _make_other_user(db_session, username="viewer1")
    await _make_activity(db_session, owner, distance_m=5000.0, calories=300)

    async with _client_as(viewer, test_engine) as ac:
        response = await ac.get(f"/users/{owner.id}/stats/summary")

    assert response.status_code == 403
    # Mensagem consistente com list_activities.
    assert "seguir" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_stats_summary_allowed_when_following(
    db_session, test_user, test_engine
):
    """Viewer que segue o dono → 200, e os dados são do DONO (não do viewer).
    Prova que o target_id é respeitado (não cai no current_user.id por engano)."""
    owner = test_user
    viewer = await _make_other_user(db_session, username="viewer2")
    await _make_follow(db_session, follower=viewer, following=owner)

    # Atividades distintas: owner tem 2, viewer tem 1 (não deve aparecer).
    await _make_activity(db_session, owner, distance_m=5000.0, calories=300)
    await _make_activity(db_session, owner, distance_m=3000.0, calories=200)
    await _make_activity(db_session, viewer, distance_m=9999.0, calories=999)

    async with _client_as(viewer, test_engine) as ac:
        response = await ac.get(f"/users/{owner.id}/stats/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 2
    assert data["total_distance_m"] == pytest.approx(8000.0)
    assert data["total_calories"] == 500


@pytest.mark.asyncio
async def test_user_stats_weekly_allowed_when_following(
    db_session, test_user, test_engine
):
    """Rota weekly responde no mesmo shape do /activities/stats/weekly."""
    owner = test_user
    viewer = await _make_other_user(db_session, username="viewer3")
    await _make_follow(db_session, follower=viewer, following=owner)
    await _make_activity(db_session, owner,
                         started_at=_dt(2026, 1, 5), calories=100)

    async with _client_as(viewer, test_engine) as ac:
        response = await ac.get(
            f"/users/{owner.id}/stats/weekly", params={"weeks": 2}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["weeks"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["period_start"] == "2026-01-05"
    assert data["items"][0]["total_calories"] == 100


@pytest.mark.asyncio
async def test_user_stats_monthly_forbidden_when_not_following(
    db_session, test_user, test_engine
):
    """Monthly também respeita a regra de follow (403)."""
    owner = test_user
    viewer = await _make_other_user(db_session, username="viewer4")

    async with _client_as(viewer, test_engine) as ac:
        response = await ac.get(f"/users/{owner.id}/stats/monthly")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_stats_by_type_previous_when_following(
    db_session, test_user, test_engine
):
    """by-type de terceiros mantém `previous` (mesma semântica da S18)."""
    owner = test_user
    viewer = await _make_other_user(db_session, username="viewer5")
    await _make_follow(db_session, follower=viewer, following=owner)

    # 45d atrás (janela atual 90d) e 120d atrás (janela anterior).
    await _make_activity(
        db_session, owner, activity_type=ActivityType.RUN,
        started_at=_dt_ago(45), distance_m=5000.0, calories=300,
    )
    await _make_activity(
        db_session, owner, activity_type=ActivityType.RUN,
        started_at=_dt_ago(120), distance_m=3000.0, calories=200,
    )

    async with _client_as(viewer, test_engine) as ac:
        response = await ac.get(
            f"/users/{owner.id}/stats/by-type", params={"period": "90d"}
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    run = data["items"][0]
    assert run["activity_type"] == "run"
    assert run["total_activities"] == 1
    assert run["total_distance_m"] == pytest.approx(5000.0)
    prev = run["previous"]
    assert prev is not None
    assert prev["total_activities"] == 1
    assert prev["total_distance_m"] == pytest.approx(3000.0)
    assert prev["total_calories"] == 200


@pytest.mark.asyncio
async def test_user_stats_unknown_user_404(
    client, db_session, test_user
):
    """user_id que não existe → 404 (não 403; não vaza existência)."""
    # UUID válido (formato), mas não existe no banco.
    missing = uuid7()
    response = await client.get(f"/users/{missing}/stats/summary")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


# ===== compare=prev|yoy — janela de comparação configurável [Sessão 20] =====
# Semântica (service):
# - compare="prev" (default): comportamento S18 — janela imediatamente
#   anterior. 90d → [now-180d, now-90d); 1y → [now-730d, now-365d).
# - compare="yoy": mesmo período do ano anterior. 90d → [now-455d,
#   now-365d); 1y → [now-730d, now-365d) (coincide com prev — matemática).
# - period="all": previous sempre None, independente de compare.
#
# Estratégia de datas (90d):
# - _dt_ago(45)  → dentro da janela ATUAL [now-90, now).
# - _dt_ago(120) → dentro da janela PREV [now-180, now-90).
# - _dt_ago(400) → dentro da janela YOY [now-455, now-365).
# Cada modo pega uma atividade distinta:
# - compare=prev → previous = 120d (3000m).
# - compare=yoy  → previous = 400d (7000m).
# Margem mínima de 30 dias das bordas → zero flakiness.


@pytest.mark.asyncio
async def test_get_by_type_compare_yoy_90d_uses_year_ago_window(
    db_session, test_user
):
    """`compare="yoy"` + `90d`: previous reflete _dt_ago(400) (janela yoy),
    não _dt_ago(120) (janela prev)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(45),
                         distance_m=5000.0, calories=300)
    # Referência prev: dentro de [now-180, now-90).
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(120),
                         distance_m=3000.0, calories=200)
    # Referência yoy: dentro de [now-455, now-365).
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(400),
                         distance_m=7000.0, calories=400)

    prev_result = await stats_service.get_by_type(
        db_session, test_user.id, period="90d", compare="prev"
    )
    yoy_result = await stats_service.get_by_type(
        db_session, test_user.id, period="90d", compare="yoy"
    )

    # Item atual idêntico nos dois modos: só a atividade de 45d.
    assert len(prev_result) == 1 and len(yoy_result) == 1
    prev_item = prev_result[0]
    yoy_item = yoy_result[0]
    assert prev_item["total_activities"] == 1
    assert yoy_item["total_activities"] == 1
    assert prev_item["total_distance_m"] == pytest.approx(5000.0)
    assert yoy_item["total_distance_m"] == pytest.approx(5000.0)

    # prev → pega a referência de 120d.
    assert prev_item["previous"] is not None
    assert prev_item["previous"]["total_distance_m"] == pytest.approx(3000.0)
    assert prev_item["previous"]["total_calories"] == 200

    # yoy → pega a referência de 400d, ignora a de 120d.
    assert yoy_item["previous"] is not None
    assert yoy_item["previous"]["total_distance_m"] == pytest.approx(7000.0)
    assert yoy_item["previous"]["total_calories"] == 400


@pytest.mark.asyncio
async def test_get_by_type_compare_yoy_90d_null_when_no_data_in_yoy_window(
    db_session, test_user
):
    """Se só há atividade na janela PREV (não na yoy), `compare=yoy` →
    previous None (mesmo com `compare=prev` trazendo dados)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(45),
                         distance_m=5000.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(120),
                         distance_m=3000.0, calories=200)

    yoy_result = await stats_service.get_by_type(
        db_session, test_user.id, period="90d", compare="yoy"
    )

    assert len(yoy_result) == 1
    assert yoy_result[0]["total_activities"] == 1
    assert yoy_result[0]["previous"] is None


@pytest.mark.asyncio
async def test_get_by_type_compare_yoy_1y_equals_prev(db_session, test_user):
    """Para period="1y", compare="yoy" e compare="prev" coincidem: a janela
    imediatamente anterior a 1 ano é o mesmo período do ano anterior."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(200),
                         distance_m=4000.0, calories=250)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(500),
                         distance_m=6000.0, calories=350)

    prev_result = await stats_service.get_by_type(
        db_session, test_user.id, period="1y", compare="prev"
    )
    yoy_result = await stats_service.get_by_type(
        db_session, test_user.id, period="1y", compare="yoy"
    )

    assert prev_result == yoy_result
    assert prev_result[0]["previous"] is not None
    assert prev_result[0]["previous"]["total_distance_m"] == pytest.approx(6000.0)


@pytest.mark.asyncio
async def test_get_by_type_compare_yoy_all_is_none(db_session, test_user):
    """period="all" ignora compare: previous sempre None."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(30), calories=100)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(400), calories=400)

    result = await stats_service.get_by_type(
        db_session, test_user.id, period="all", compare="yoy"
    )

    assert len(result) == 1
    assert result[0]["previous"] is None


@pytest.mark.asyncio
async def test_route_by_type_compare_yoy_param(client, db_session, test_user):
    """Rota aceita ?compare=yoy e propaga ao service (mesmo cenário do
    teste de service, agora via HTTP)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(45),
                         distance_m=5000.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(120),
                         distance_m=3000.0, calories=200)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(400),
                         distance_m=7000.0, calories=400)

    response = await client.get(
        "/activities/stats/by-type",
        params={"period": "90d", "compare": "yoy"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    run = data["items"][0]
    assert run["total_activities"] == 1
    prev = run["previous"]
    assert prev is not None
    assert prev["total_distance_m"] == pytest.approx(7000.0)
    assert prev["total_calories"] == 400


@pytest.mark.asyncio
async def test_route_by_type_compare_invalid_returns_422(
    client, db_session, test_user
):
    """compare fora de {prev, yoy} → 422 (Literal do FastAPI)."""
    response = await client.get(
        "/activities/stats/by-type", params={"compare": "xpto"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_route_by_type_compare_default_is_prev(client, db_session, test_user):
    """Sem passar ?compare=, comportamento S18 preservado (default prev)."""
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(45),
                         distance_m=5000.0, calories=300)
    await _make_activity(db_session, test_user,
                         activity_type=ActivityType.RUN,
                         started_at=_dt_ago(120),
                         distance_m=3000.0, calories=200)

    response = await client.get(
        "/activities/stats/by-type", params={"period": "90d"}
    )
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["previous"] is not None
    # 120d está na prev de 90d → 3000m.
    assert item["previous"]["total_distance_m"] == pytest.approx(3000.0)