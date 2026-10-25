"""Testes de stats_service: get_summary e get_period_stats.

Cobertura:
- Service puro (db_session): somas, filtros, tratamento de None, isolamento
  entre usuários, períodos semana/mês com datas fixas (sem now()).
- Rota HTTP (client): shape de resposta, filtro por tipo, limites de
  validação (weeks/months) e integração service → schema.

Filosofia: datas determinísticas (nada de datetime.now()) para eliminar
flakiness de fuso/relógio. Todos os inserts usam o ORM com ActivityType
enum nativo, e os filtros usam string (o que o router de fato recebe).

Paths de rota: o router `activities.py` é incluído no main.py com
`prefix="/activities"`. Como as rotas de stats já declaram `/stats/...`
no próprio router, o path final é `/activities/stats/summary`, etc.
"""

from datetime import datetime, timezone

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