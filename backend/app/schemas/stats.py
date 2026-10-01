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