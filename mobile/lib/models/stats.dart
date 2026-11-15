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