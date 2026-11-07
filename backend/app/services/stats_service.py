"""Serviço de agregações/estatísticas de atividades."""

from datetime import timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


def _apply_type_filter(stmt, activity_type: str | None):
    """Aplica filtro opcional por tipo de atividade."""
    if activity_type:
        stmt = stmt.where(Activity.activity_type == activity_type)
    return stmt


# [Sessão 17] Filtro opcional por janela temporal (all|90d|1y).
def _apply_period_filter(stmt, period: Literal["all", "90d", "1y"]):
    """Aplica filtro de janela temporal em `Activity.started_at`.

    - `all`: sem filtro (todos os tempos).
    - `90d`: atividades iniciadas nos últimos 90 dias corridos.
    - `1y`:  atividades iniciadas nos últimos 365 dias corridos.

    Usa `now() - INTERVAL` via `func.now() - timedelta`, que o
    SQLAlchemy serializa como `now() - INTERVAL 'N days'` — sem SQL cru,
    sem função específica de Postgres no Python. Se um dia o suporte a
    outro banco entrar na pauta, essa expressão continua válida.
    """
    if period == "90d":
        stmt = stmt.where(Activity.started_at >= func.now() - timedelta(days=90))
    elif period == "1y":
        stmt = stmt.where(Activity.started_at >= func.now() - timedelta(days=365))
    # period == "all": nenhum filtro (comportamento original).
    return stmt


# [Sessão 18] Helpers para a comparação "este período vs. anterior".
def _period_window_days(period: Literal["all", "90d", "1y"]) -> int | None:
    """Retorna o tamanho da janela em dias para 90d/1y; None para all."""
    if period == "90d":
        return 90
    if period == "1y":
        return 365
    return None


def _current_window_expr(period: Literal["all", "90d", "1y"]):
    """Condição SQL da janela *atual* (started_at >= now - N).

    Usada dentro de `CASE WHEN` quando `period != "all"` — porque nesse
    caso o `WHERE` do get_by_type foi ampliado para cobrir também a
    janela anterior, e o recorte da janela atual precisa ser feito
    dentro de cada métrica.
    """
    days = _period_window_days(period)
    if days is None:
        return None
    return Activity.started_at >= func.now() - timedelta(days=days)


def _previous_window_expr(period: Literal["all", "90d", "1y"]):
    """Retorna a condição SQL da janela imediatamente anterior.

    - `90d`: [now-180d, now-90d)
    - `1y`:  [now-730d, now-365d)
    - `all`: None (sem comparação)

    `started_at < now - N` é o limite superior **exclusivo** (garante que
    uma atividade no exato "now - N" não caia nas duas janelas).
    """
    days = _period_window_days(period)
    if days is None:
        return None
    end_prev = func.now() - timedelta(days=days)
    start_prev = func.now() - timedelta(days=2 * days)
    return and_(Activity.started_at >= start_prev, Activity.started_at < end_prev)


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
# [Sessão 17] Adicionado param `period` (all|90d|1y) para janela temporal.
# [Sessão 18] Adicionado `previous` por item (comparação vs. janela anterior).
async def get_by_type(
    db: AsyncSession,
    user_id: UUID,
    period: Literal["all", "90d", "1y"] = "all",
) -> list[dict]:
    """Agrega as atividades do usuário por tipo.

    Ordenação: total_activities DESC, activity_type ASC (desempate
    determinístico). Só tipos com >= 1 atividade na janela *atual*
    aparecem (GROUP BY natural, sem "zero rows").

    `period` filtra por `started_at` (retroativo a partir de now()):
    - `all` (default): todos os tempos — comportamento original.
    - `90d`: últimas 90 dias corridos.
    - `1y`:  últimos 365 dias corridos.

    [Sessão 18] Para `90d`/`1y`, cada item ganha `previous` com as
    mesmas 5 métricas, calculadas sobre a janela *imediatamente
    anterior* (sem sobreposição):
    - `90d`: [now-180d, now-90d)
    - `1y`:  [now-730d, now-365d)
    `previous` é `null` quando `period="all"` ou quando o tipo não tem
    nenhuma atividade na janela anterior (todas as métricas zero).

    [Sessão 18 — fix] Quando `period != "all"`, o `WHERE` do SELECT
    cobre `started_at >= now - 2N dias` (janela anterior + atual) e
    cada métrica faz seu próprio recorte via `CASE WHEN`. Antes, o
    `WHERE` recortava só a janela atual e as linhas da janela anterior
    eram descartadas antes do `CASE WHEN` — `previous` vinha sempre
    `null`. As 5 métricas "atuais" também passaram a ser
    `SUM(CASE WHEN <janela_atual> ...)` para ignorar as linhas da
    janela anterior que agora entram no SELECT.

    [Sessão 14 — fix] O desempate por tipo é feito em Python, não no
    ORDER BY do SQL. Motivo: `Activity.activity_type` é um Enum nativo
    do Postgres (`native_enum=True`), e ORDER BY em coluna Enum ordena
    pela *ordem de declaração* do tipo — não pela string. Isso é
    surpreendente e frágil (adicionar "e-bike" antes de "walk" mudaria
    a ordem). Como o universo é no máximo 6 linhas, ordenar em Python
    é trivial, previsível e desacopla a UI do enum.
    """
    type_col = Activity.activity_type.label("activity_type")
    curr_cond = _current_window_expr(period)
    prev_cond = _previous_window_expr(period)

    # [Sessão 18 — fix] Quando há janela anterior, cada métrica do item
    # atual precisa ignorar as linhas da janela anterior que entram no
    # SELECT (o WHERE foi ampliado). Para `period="all"`, mantém o
    # comportamento original (somas diretas, sem CASE).
    def _curr_metric(col, agg):
        """SUM/CASE da janela atual sobre `col` (ou contagem, se col=1)."""
        if curr_cond is None:
            return agg(col) if col is not None else func.count(Activity.id)
        if col is None:
            return func.coalesce(func.sum(case((curr_cond, 1), else_=0)), 0)
        return func.coalesce(func.sum(case((curr_cond, col), else_=0)), 0)

    if curr_cond is None:
        # period == "all": comportamento original, sem CASE.
        columns = [
            type_col,
            func.count(Activity.id).label("total_activities"),
            func.coalesce(func.sum(Activity.distance_m), 0).label("total_distance_m"),
            func.coalesce(func.sum(Activity.duration_s), 0).label("total_duration_s"),
            func.coalesce(func.sum(Activity.elevation_gain_m), 0).label("total_elevation_gain_m"),
            func.coalesce(func.sum(Activity.calories), 0).label("total_calories"),
        ]
    else:
        # period != "all": WHERE cobre as duas janelas e cada métrica
        # recorta a janela atual via CASE WHEN.
        columns = [
            type_col,
            _curr_metric(None, None).label("total_activities"),
            _curr_metric(Activity.distance_m, func.sum).label("total_distance_m"),
            _curr_metric(Activity.duration_s, func.sum).label("total_duration_s"),
            _curr_metric(Activity.elevation_gain_m, func.sum).label("total_elevation_gain_m"),
            _curr_metric(Activity.calories, func.sum).label("total_calories"),
        ]

    # [Sessão 18] Métricas da janela anterior (só para 90d/1y).
    if prev_cond is not None:
        columns += [
            func.coalesce(
                func.sum(case((prev_cond, 1), else_=0)), 0
            ).label("prev_total_activities"),
            func.coalesce(
                func.sum(case((prev_cond, Activity.distance_m), else_=0)), 0
            ).label("prev_total_distance_m"),
            func.coalesce(
                func.sum(case((prev_cond, Activity.duration_s), else_=0)), 0
            ).label("prev_total_duration_s"),
            func.coalesce(
                func.sum(case((prev_cond, Activity.elevation_gain_m), else_=0)), 0
            ).label("prev_total_elevation_gain_m"),
            func.coalesce(
                func.sum(case((prev_cond, Activity.calories), else_=0)), 0
            ).label("prev_total_calories"),
        ]

    stmt = (
        select(*columns)
        .where(Activity.user_id == user_id)
        .group_by(type_col)
        # Sem tie-break no SQL: total_activities DESC basta para a UI.
        # O desempate é aplicado no `sorted()` abaixo.
        .order_by(func.count(Activity.id).desc())
    )

    if period == "all":
        # [Sessão 17] Filtro de janela temporal (no-op para "all").
        stmt = _apply_period_filter(stmt, period)
    else:
        # [Sessão 18 — fix] WHERE ampliado para [now-2N, now): cobre
        # janela anterior + atual. O recorte de cada janela é feito
        # pelos CASE WHEN das métricas acima.
        days = _period_window_days(period)
        stmt = stmt.where(Activity.started_at >= func.now() - timedelta(days=2 * days))

    rows = (await db.execute(stmt)).all()

    items = []
    for row in rows:
        # [Sessão 18 — fix] Só tipos com >= 1 atividade na janela atual
        # aparecem (o WHERE ampliado traz também tipos que só existem
        # na janela anterior; esses são filtrados aqui).
        curr_activities = int(row.total_activities or 0)
        if curr_activities == 0:
            continue

        item = {
            # activity_type é Enum no model; .value garante a string.
            "activity_type": row.activity_type.value
            if hasattr(row.activity_type, "value")
            else str(row.activity_type),
            "total_activities": curr_activities,
            "total_distance_m": float(row.total_distance_m or 0),
            "total_duration_s": int(row.total_duration_s or 0),
            "total_elevation_gain_m": float(row.total_elevation_gain_m or 0),
            "total_calories": int(row.total_calories or 0),
            "previous": None,
        }

        # [Sessão 18] Preenche `previous` só quando há dado na janela anterior.
        if prev_cond is not None:
            prev_activities = int(row.prev_total_activities or 0)
            if prev_activities > 0:
                item["previous"] = {
                    "total_activities": prev_activities,
                    "total_distance_m": float(row.prev_total_distance_m or 0),
                    "total_duration_s": int(row.prev_total_duration_s or 0),
                    "total_elevation_gain_m": float(row.prev_total_elevation_gain_m or 0),
                    "total_calories": int(row.prev_total_calories or 0),
                }

        items.append(item)

    # Desempate determinístico: atividades DESC, tipo ASC (string).
    items.sort(key=lambda r: (-r["total_activities"], r["activity_type"]))
    return items