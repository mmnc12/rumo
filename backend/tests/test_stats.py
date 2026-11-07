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
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from app.models.activity import Activity, ActivityType
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