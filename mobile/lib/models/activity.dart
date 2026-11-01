class UserPublic {
  final String id;
  final String username;
  final String? fullName;
  final String? avatarUrl;

  UserPublic({
    required this.id,
    required this.username,
    this.fullName,
    this.avatarUrl,
  });

  factory UserPublic.fromJson(Map<String, dynamic> json) {
    return UserPublic(
      id: json['id'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
    );
  }
}

class Activity {
  final String id;
  final String activityType;
  final String? title;
  final String? description;
  final DateTime startedAt;
  final DateTime? finishedAt;
  final int? durationS;
  final double? distanceM;
  final double? elevationGainM;
  final int? calories;
  final double? avgPaceSPerKm;
  final double? avgSpeedMps;
  final String? coverPhotoUrl;
  final UserPublic? user;

  Activity({
    required this.id,
    required this.activityType,
    required this.startedAt,
    this.title,
    this.description,
    this.finishedAt,
    this.durationS,
    this.distanceM,
    this.elevationGainM,
    this.calories,
    this.avgPaceSPerKm,
    this.avgSpeedMps,
    this.coverPhotoUrl,
    this.user,
  });

  factory Activity.fromJson(Map<String, dynamic> json) {
    return Activity(
      id: json['id'] as String,
      activityType: json['activity_type'] as String,
      startedAt: DateTime.parse(json['started_at'] as String),
      title: json['title'] as String?,
      description: json['description'] as String?,
      finishedAt: json['finished_at'] != null
          ? DateTime.parse(json['finished_at'] as String)
          : null,
      durationS: json['duration_s'] as int?,
      distanceM: (json['distance_m'] as num?)?.toDouble(),
      elevationGainM: (json['elevation_gain_m'] as num?)?.toDouble(),
      calories: json['calories'] as int?,
      avgPaceSPerKm: (json['avg_pace_s_per_km'] as num?)?.toDouble(),
      avgSpeedMps: (json['avg_speed_mps'] as num?)?.toDouble(),
      coverPhotoUrl: json['cover_photo_url'] as String?,
      user: json['user'] != null
          ? UserPublic.fromJson(json['user'] as Map<String, dynamic>)
          : null,
    );
  }

  // ---------- Helpers de formatação ----------

  String get typeLabel {
    switch (activityType) {
      case 'run':
        return 'Corrida';
      case 'walk':
        return 'Caminhada';
      case 'cycle':
        return 'Pedal';
      case 'hike':
        return 'Trilha';
      case 'swim':
        return 'Natação';
      default:
        return 'Outro';
    }
  }

  String? get distanceLabel {
    if (distanceM == null) return null;
    final km = distanceM! / 1000;
    return '${km.toStringAsFixed(2)} km';
  }

  String? get durationLabel {
    if (durationS == null) return null;
    final h = durationS! ~/ 3600;
    final m = (durationS! % 3600) ~/ 60;
    final s = durationS! % 60;
    if (h > 0) {
      return '${h}h ${m.toString().padLeft(2, '0')}min';
    }
    return '${m}min ${s.toString().padLeft(2, '0')}s';
  }

  String? get caloriesLabel {
    if (calories == null) return null;
    return '$calories kcal';
  }

  String? get paceLabel {
    if (avgPaceSPerKm == null || avgPaceSPerKm! <= 0) return null;
    final total = avgPaceSPerKm!.round();
    final min = total ~/ 60;
    final sec = total % 60;
    return '$min:${sec.toString().padLeft(2, '0')} /km';
  }

  String get startedAtLabel {
    final local = startedAt.toLocal();
    return '${local.day.toString().padLeft(2, '0')}/'
        '${local.month.toString().padLeft(2, '0')}/${local.year} '
        '${local.hour.toString().padLeft(2, '0')}:'
        '${local.minute.toString().padLeft(2, '0')}';
  }
}