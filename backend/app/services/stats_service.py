"""Serviço de agregações/estatísticas de atividades."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


def _apply_type_filter(stmt, activity_type: str | None):
    """Aplica filtro opcional por tipo de atividade."""
    if activity_type:
        stmt = stmt.where(Activity.activity_type == activity_type)
    return stmt


async def get_summary(
    db: AsyncSession,
    user_id: UUID,
    activity_type: str | None = None,
) -> dict:
    """Retorna totais gerais do usuário."""
    stmt = select(
        func.count(Activity.id).label("total_activities"),
        func.coalesce(func.sum(Activity.distance_m), 0).label("total_distance_m"),
        func.coalesce(func.sum(Activity.duration_s), 0).label("total_duration_s"),
        func.coalesce(func.sum(Activity.elevation_gain_m), 0).label("total_elevation_gain_m"),
        func.coalesce(func.sum(Activity.calories), 0).label("total_calories"),
    ).where(Activity.user_id == user_id)
    stmt = _apply_type_filter(stmt, activity_type)

    row = (await db.execute(stmt)).one()

    total_distance = float(row.total_distance_m or 0)
    total_duration = int(row.total_duration_s or 0)

    avg_pace = (total_duration / (total_distance / 1000.0)) if total_distance > 0 else None
    avg_speed = (total_distance / total_duration) if total_duration > 0 else None

    return {
        "total_activities": int(row.total_activities or 0),
        "total_distance_m": total_distance,
        "total_duration_s": total_duration,
        "total_elevation_gain_m": float(row.total_elevation_gain_m or 0),
        "total_calories": int(row.total_calories or 0),
        "avg_pace_s_per_km": avg_pace,
        "avg_speed_mps": avg_speed,
    }


async def get_period_stats(
    db: AsyncSession,
    user_id: UUID,
    trunc_unit: str,  # "week" ou "month"
    limit_periods: int,
    activity_type: str | None = None,
) -> list[dict]:
    """Retorna resumos agrupados por semana ou mês."""
    period_col = func.date_trunc(trunc_unit, Activity.started_at).label("period_start")

    stmt = (
        select(
            period_col,
            func.count(Activity.id).label("total_activities"),
            func.coalesce(func.sum(Activity.distance_m), 0).label("total_distance_m"),
            func.coalesce(func.sum(Activity.duration_s), 0).label("total_duration_s"),
            func.coalesce(func.sum(Activity.calories), 0).label("total_calories"),
        )
        .where(Activity.user_id == user_id)
        .group_by(period_col)
        .order_by(period_col.desc())
        .limit(limit_periods)
    )
    stmt = _apply_type_filter(stmt, activity_type)

    rows = (await db.execute(stmt)).all()

    return [
        {
            "period_start": row.period_start.date() if hasattr(row.period_start, "date") else row.period_start,
            "total_activities": int(row.total_activities or 0),
            "total_distance_m": float(row.total_distance_m or 0),
            "total_duration_s": int(row.total_duration_s or 0),
            "total_calories": int(row.total_calories or 0),
        }
        for row in rows
    ]


# [Sessão 14 — B1] Drill-down por tipo de atividade.
async def get_by_type(
    db: AsyncSession,
    user_id: UUID,
) -> list[dict]:
    """Agrega as atividades do usuário por tipo.

    Ordenação: total_activities DESC, activity_type ASC (desempate
    determinístico). Só tipos com >= 1 atividade aparecem (GROUP BY
    natural, sem "zero rows").

    [Sessão 14 — fix] O desempate por tipo é feito em Python, não no
    ORDER BY do SQL. Motivo: `Activity.activity_type` é um Enum nativo
    do Postgres (`native_enum=True`), e ORDER BY em coluna Enum ordena
    pela *ordem de declaração* do tipo — não pela string. Isso é
    surpreendente e frágil (adicionar "e-bike" antes de "walk" mudaria
    a ordem). Como o universo é no máximo 6 linhas, ordenar em Python
    é trivial, previsível e desacopla a UI do enum.
    """
    type_col = Activity.activity_type.label("activity_type")

    stmt = (
        select(
            type_col,
            func.count(Activity.id).label("total_activities"),
            func.coalesce(func.sum(Activity.distance_m), 0).label("total_distance_m"),
            func.coalesce(func.sum(Activity.duration_s), 0).label("total_duration_s"),
            func.coalesce(func.sum(Activity.elevation_gain_m), 0).label("total_elevation_gain_m"),
            func.coalesce(func.sum(Activity.calories), 0).label("total_calories"),
        )
        .where(Activity.user_id == user_id)
        .group_by(type_col)
        # Sem tie-break no SQL: total_activities DESC basta para a UI.
        # O desempate é aplicado no `sorted()` abaixo.
        .order_by(func.count(Activity.id).desc())
    )

    rows = (await db.execute(stmt)).all()

    items = [
        {
            # activity_type é Enum no model; .value garante a string.
            "activity_type": row.activity_type.value
            if hasattr(row.activity_type, "value")
            else str(row.activity_type),
            "total_activities": int(row.total_activities or 0),
            "total_distance_m": float(row.total_distance_m or 0),
            "total_duration_s": int(row.total_duration_s or 0),
            "total_elevation_gain_m": float(row.total_elevation_gain_m or 0),
            "total_calories": int(row.total_calories or 0),
        }
        for row in rows
    ]

    # Desempate determinístico: atividades DESC, tipo ASC (string).
    items.sort(key=lambda r: (-r["total_activities"], r["activity_type"]))
    return items