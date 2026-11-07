"""Schemas de estatísticas agregadas de atividades."""

from datetime import date

from pydantic import BaseModel


class StatsSummary(BaseModel):
    """Totais gerais do usuário (com filtro opcional por tipo)."""

    total_activities: int
    total_distance_m: float
    total_duration_s: int
    total_elevation_gain_m: float
    total_calories: int
    avg_pace_s_per_km: float | None
    avg_speed_mps: float | None


class StatsPeriod(BaseModel):
    """Resumo de um período (semana ou mês)."""

    period_start: date
    total_activities: int
    total_distance_m: float
    total_duration_s: int
    total_calories: int


class StatsWeeklyResponse(BaseModel):
    """Lista de resumos semanais."""

    weeks: int
    items: list[StatsPeriod]


class StatsMonthlyResponse(BaseModel):
    """Lista de resumos mensais."""

    months: int
    items: list[StatsPeriod]


# [Sessão 14 — B1] Drill-down por tipo de atividade.
# [Sessão 18] Adicionado `previous` (comparação vs. janela imediatamente anterior).

class StatsByTypePreviousItem(BaseModel):
    """Agregado do tipo na janela *imediatamente anterior* à atual.

    Só aparece quando `period != "all"` e o tipo teve >= 1 atividade
    nessa janela. As 5 métricas são as mesmas do item atual; o
    `activity_type` não se repete (é o mesmo do item pai).
    """

    total_activities: int
    total_distance_m: float
    total_duration_s: int
    total_elevation_gain_m: float
    total_calories: int


class StatsByTypeItem(BaseModel):
    """Agregado de um único tipo de atividade (ex.: run, cycle)."""

    activity_type: str
    total_activities: int
    total_distance_m: float
    total_duration_s: int
    total_elevation_gain_m: float
    total_calories: int
    # [Sessão 18] None quando period="all" ou sem atividade na janela anterior.
    previous: StatsByTypePreviousItem | None = None


class StatsByTypeResponse(BaseModel):
    """Lista de agregados por tipo, ordenada por total_activities DESC."""

    items: list[StatsByTypeItem]