// [Sessão 33] Models das estatísticas agregadas (stats/summary + stats/by-type).
//
// Espelho 1:1 de web/src/types/api.ts (que bate com backend/app/schemas/stats.py):
// - StatsSummary: 7 campos (5 "totais" + avg_pace_s_per_km + avg_speed_mps nullable).
// - StatsByTypePrevious: 5 campos (mesmo shape do item, sem activity_type).
// - StatsByTypeItem: 6 campos + previous nullable.
// - StatsByTypeResponse: envelope { items }.
//
// Casts seguem o schema Python:
// - total_activities / total_duration_s / total_calories são int.
// - total_distance_m / total_elevation_gain_m / avg_pace_s_per_km / avg_speed_mps
//   são float (backend pode mandar int quando o valor é inteiro) → (num).toDouble().
//
// [Sessão 38] +StatsPeriod, StatsWeeklyResponse, StatsMonthlyResponse.
// Paridade com web/src/types/api.ts (S13/S14) e com o backend real
// (validado por GET /users/{id}/stats/weekly e /monthly em produção):
// - StatsPeriod tem 5 campos (period_start, total_activities,
//   total_distance_m, total_duration_s, total_calories). O StatsChart
//   só usa 3 (period_start, total_activities, total_distance_m) — os
//   outros 2 ficam no model pra S39+ (chart de duração/calorias).
// - StatsWeeklyResponse: { weeks: int, items: [StatsPeriod] }.
// - StatsMonthlyResponse: { months: int, items: [StatsPeriod] }.
// Backend devolve items em ordem crescente de period_start — o mobile
// NÃO reordena (paridade com PeriodChart.tsx do web).

class StatsSummary {
  final int totalActivities;
  final double totalDistanceM;
  final int totalDurationS;
  final double totalElevationGainM;
  final int totalCalories;
  final double? avgPaceSPerKm;
  final double? avgSpeedMps;

  StatsSummary({
    required this.totalActivities,
    required this.totalDistanceM,
    required this.totalDurationS,
    required this.totalElevationGainM,
    required this.totalCalories,
    this.avgPaceSPerKm,
    this.avgSpeedMps,
  });

  factory StatsSummary.fromJson(Map<String, dynamic> json) {
    return StatsSummary(
      totalActivities: json['total_activities'] as int,
      totalDistanceM: (json['total_distance_m'] as num).toDouble(),
      totalDurationS: json['total_duration_s'] as int,
      totalElevationGainM:
          (json['total_elevation_gain_m'] as num).toDouble(),
      totalCalories: json['total_calories'] as int,
      avgPaceSPerKm: (json['avg_pace_s_per_km'] as num?)?.toDouble(),
      avgSpeedMps: (json['avg_speed_mps'] as num?)?.toDouble(),
    );
  }
}

class StatsByTypePrevious {
  final int totalActivities;
  final double totalDistanceM;
  final int totalDurationS;
  final double totalElevationGainM;
  final int totalCalories;

  StatsByTypePrevious({
    required this.totalActivities,
    required this.totalDistanceM,
    required this.totalDurationS,
    required this.totalElevationGainM,
    required this.totalCalories,
  });

  factory StatsByTypePrevious.fromJson(Map<String, dynamic> json) {
    return StatsByTypePrevious(
      totalActivities: json['total_activities'] as int,
      totalDistanceM: (json['total_distance_m'] as num).toDouble(),
      totalDurationS: json['total_duration_s'] as int,
      totalElevationGainM:
          (json['total_elevation_gain_m'] as num).toDouble(),
      totalCalories: json['total_calories'] as int,
    );
  }
}

class StatsByTypeItem {
  final String activityType;
  final int totalActivities;
  final double totalDistanceM;
  final int totalDurationS;
  final double totalElevationGainM;
  final int totalCalories;
  final StatsByTypePrevious? previous;

  StatsByTypeItem({
    required this.activityType,
    required this.totalActivities,
    required this.totalDistanceM,
    required this.totalDurationS,
    required this.totalElevationGainM,
    required this.totalCalories,
    this.previous,
  });

  factory StatsByTypeItem.fromJson(Map<String, dynamic> json) {
    return StatsByTypeItem(
      activityType: json['activity_type'] as String,
      totalActivities: json['total_activities'] as int,
      totalDistanceM: (json['total_distance_m'] as num).toDouble(),
      totalDurationS: json['total_duration_s'] as int,
      totalElevationGainM:
          (json['total_elevation_gain_m'] as num).toDouble(),
      totalCalories: json['total_calories'] as int,
      previous: json['previous'] != null
          ? StatsByTypePrevious.fromJson(
              json['previous'] as Map<String, dynamic>,
            )
          : null,
    );
  }
}

class StatsByTypeResponse {
  final List<StatsByTypeItem> items;

  StatsByTypeResponse({required this.items});

  factory StatsByTypeResponse.fromJson(Map<String, dynamic> json) {
    final raw = json['items'];
    if (raw is! List) {
      throw FormatException('stats/by-type: items não é List');
    }
    return StatsByTypeResponse(
      items: raw
          .map((e) => StatsByTypeItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

// ===== [Sessão 38] Weekly / Monthly =====

/// Item de um período (semana ou mês).
///
/// Espelho 1:1 de web/src/types/api.ts → StatsPeriod. O backend sempre
/// devolve 5 campos; o StatsChart usa 3 (period_start, total_activities,
/// total_distance_m), mas os outros 2 ficam no model pra reuso.
///
/// `periodStart` é ISO `YYYY-MM-DD`. Backend devolve o primeiro dia do
/// período: segunda-feira da semana (weekly) ou dia 01 do mês (monthly).
class StatsPeriod {
  final String periodStart;
  final int totalActivities;
  final double totalDistanceM;
  final int totalDurationS;
  final int totalCalories;

  StatsPeriod({
    required this.periodStart,
    required this.totalActivities,
    required this.totalDistanceM,
    required this.totalDurationS,
    required this.totalCalories,
  });

  factory StatsPeriod.fromJson(Map<String, dynamic> json) {
    return StatsPeriod(
      periodStart: json['period_start'] as String,
      totalActivities: json['total_activities'] as int,
      totalDistanceM: (json['total_distance_m'] as num).toDouble(),
      totalDurationS: json['total_duration_s'] as int,
      totalCalories: json['total_calories'] as int,
    );
  }
}

/// `GET /users/{id}/stats/weekly?weeks=N` — resposta do backend.
///
/// Shape confirmado em produção (S38): `{ weeks: int, items: [StatsPeriod] }`.
/// `items` vem em ordem crescente de `period_start` (o mobile não reordena —
/// paridade com PeriodChart.tsx do web).
class StatsWeeklyResponse {
  final int weeks;
  final List<StatsPeriod> items;

  StatsWeeklyResponse({required this.weeks, required this.items});

  factory StatsWeeklyResponse.fromJson(Map<String, dynamic> json) {
    final raw = json['items'];
    if (raw is! List) {
      throw FormatException('stats/weekly: items não é List');
    }
    return StatsWeeklyResponse(
      weeks: json['weeks'] as int,
      items: raw
          .map((e) => StatsPeriod.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// `GET /users/{id}/stats/monthly?months=N` — resposta do backend.
///
/// Shape confirmado em produção (S38): `{ months: int, items: [StatsPeriod] }`.
/// Mesma semântica do weekly (só muda a janela de agregação).
class StatsMonthlyResponse {
  final int months;
  final List<StatsPeriod> items;

  StatsMonthlyResponse({required this.months, required this.items});

  factory StatsMonthlyResponse.fromJson(Map<String, dynamic> json) {
    final raw = json['items'];
    if (raw is! List) {
      throw FormatException('stats/monthly: items não é List');
    }
    return StatsMonthlyResponse(
      months: json['months'] as int,
      items: raw
          .map((e) => StatsPeriod.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}