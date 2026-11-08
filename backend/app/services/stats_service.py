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
    janela de comparação, e o recorte da janela atual precisa ser feito
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


# [Sessão 20] Janela "mesmo período do ano anterior" (year-over-year).
# Simétrica à _previous_window_expr, mas deslocada 365 dias para trás.
#
# Semântica por period:
# - `all`: None (year-over-year não faz sentido sem janela).
# - `90d`: [now-455d, now-365d) — os 90 dias terminando "um ano atrás".
# - `1y`:  [now-730d, now-365d) — coincide exatamente com _previous_window_expr
#          de period="1y". Isso NÃO é bug: a janela imediatamente anterior
#          a 1 ano é o mesmo período do ano anterior. Documentado em teste.
def _yoy_window_expr(period: Literal["all", "90d", "1y"]):
    """Condição SQL da janela do mesmo período do ano anterior (Sessão 20)."""
    days = _period_window_days(period)
    if days is None:
        return None
    end_yoy = func.now() - timedelta(days=365)
    start_yoy = func.now() - timedelta(days=days + 365)
    return and_(Activity.started_at >= start_yoy, Activity.started_at < end_yoy)


# [Sessão 20] Retorna a condição de comparação conforme o modo.
def _comparison_window_expr(
    period: Literal["all", "90d", "1y"],
    compare: Literal["prev", "yoy"],
):
    """Despacha para _previous_window_expr ou _yoy_window_expr."""
    if compare == "yoy":
        return _yoy_window_expr(period)
    return _previous_window_expr(period)


# [Sessão 20] Limite inferior do WHERE quando há janela de comparação.
#
# - `prev`: now - 2N (janela atual + anterior adjacentes).
# - `yoy`:  now - (N + 365) (janela atual + yoy, deslocada 1 ano atrás).
def _where_floor_days(
    period: Literal["all", "90d", "1y"],
    compare: Literal["prev", "yoy"],
) -> int | None:
    days = _period_window_days(period)
    if days is None:
        return None
    if compare == "yoy":
        return days + 365
    return 2 * days


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
# [Sessão 20] Adicionado param `compare` (prev|yoy) — janela de comparação.
async def get_by_type(
    db: AsyncSession,
    user_id: UUID,
    period: Literal["all", "90d", "1y"] = "all",
    compare: Literal["prev", "yoy"] = "prev",
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
    mesmas 5 métricas, calculadas sobre uma janela de comparação:
    - `compare="prev"` (default): janela *imediatamente anterior*.
        - `90d`: [now-180d, now-90d)
        - `1y`:  [now-730d, now-365d)
    - `compare="yoy"` [Sessão 20]: mesmo período do ano anterior.
        - `90d`: [now-455d, now-365d)
        - `1y`:  [now-730d, now-365d) — idêntico a prev (coincidência
                 matemática: a janela imediatamente anterior a 1 ano é
                 o mesmo período do ano anterior).
    `previous` é `null` quando `period="all"` ou quando o tipo não tem
    nenhuma atividade na janela de comparação (todas as métricas zero).

    [Sessão 18 — fix] Quando `period != "all"`, o `WHERE` do SELECT
    cobre a união (janela de comparação + atual) e cada métrica faz seu
    próprio recorte via `CASE WHEN`. Sem isso, as linhas da janela de
    comparação eram descartadas antes do `CASE WHEN` e `previous` vinha
    sempre `null`.
    [Sessão 20 — fix] O limite inferior do WHERE depende de `compare`:
    para `prev` é `now - 2N` (janelas adjacentes); para `yoy` é
    `now - (N + 365)` (janela deslocada 1 ano atrás). `_where_floor_days`
    encapsula essa diferença.

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
    # [Sessão 20] Janela de comparação depende de `compare`.
    cmp_cond = _comparison_window_expr(period, compare)

    # [Sessão 18 — fix] Quando há janela de comparação, cada métrica do
    # item atual precisa ignorar as linhas dessa janela que entram no
    # SELECT (o WHERE foi ampliado). Para `period="all"`, mantém o
    # comportamento original (somas diretas, sem CASE).
    def _curr_metric(col, agg):
        """SUM/CASE da janela atual sobre `col` (ou contagem, se col=None)."""
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

    # [Sessão 18/20] Métricas da janela de comparação.
    if cmp_cond is not None:
        columns += [
            func.coalesce(
                func.sum(case((cmp_cond, 1), else_=0)), 0
            ).label("prev_total_activities"),
            func.coalesce(
                func.sum(case((cmp_cond, Activity.distance_m), else_=0)), 0
            ).label("prev_total_distance_m"),
            func.coalesce(
                func.sum(case((cmp_cond, Activity.duration_s), else_=0)), 0
            ).label("prev_total_duration_s"),
            func.coalesce(
                func.sum(case((cmp_cond, Activity.elevation_gain_m), else_=0)), 0
            ).label("prev_total_elevation_gain_m"),
            func.coalesce(
                func.sum(case((cmp_cond, Activity.calories), else_=0)), 0
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
        # [Sessão 18/20] WHERE ampliado para cobrir janela atual + janela
        # de comparação. `_where_floor_days` decide o limite inferior:
        # prev → 2N (adjacentes); yoy → N + 365 (deslocada 1 ano atrás).
        floor_days = _where_floor_days(period, compare)
        stmt = stmt.where(Activity.started_at >= func.now() - timedelta(days=floor_days))

    rows = (await db.execute(stmt)).all()

    items = []
    for row in rows:
        # [Sessão 18 — fix] Só tipos com >= 1 atividade na janela atual
        # aparecem (o WHERE ampliado traz também tipos que só existem
        # na janela de comparação; esses são filtrados aqui).
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

        # [Sessão 18/20] Preenche `previous` só quando há dado na janela
        # de comparação.
        if cmp_cond is not None:
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