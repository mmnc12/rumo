import 'package:latlong2/latlong.dart';

/// Geometria da rota de uma atividade, já convertida para `LatLng`.
///
/// O backend (`TrackResponse`) devolve `coordinates` em ordem GeoJSON
/// `[[lon, lat], ...]`. A conversão para `LatLng(lat, lon)` é feita
/// AQUI, uma única vez, para que nenhum widget precise lembrar da inversão.
class ActivityTrack {
  final String activityId;
  final List<LatLng> points;
  final List<double> bbox; // [minLon, minLat, maxLon, maxLat]
  final int nPoints;
  final bool simplified;

  const ActivityTrack({
    required this.activityId,
    required this.points,
    required this.bbox,
    required this.nPoints,
    required this.simplified,
  });

  factory ActivityTrack.fromJson(Map<String, dynamic> json) {
    final rawCoords = (json['coordinates'] as List<dynamic>)
        .map((e) => (e as List<dynamic>).cast<num>())
        .toList();

    // GeoJSON: [lon, lat] -> LatLng(lat, lon)
    final points = rawCoords
        .map((pair) => LatLng(pair[1].toDouble(), pair[0].toDouble()))
        .toList(growable: false);

    final rawBbox = (json['bbox'] as List<dynamic>)
        .map((e) => (e as num).toDouble())
        .toList(growable: false);

    return ActivityTrack(
      activityId: json['activity_id'] as String,
      points: points,
      bbox: rawBbox,
      nPoints: (json['n_points'] as num).toInt(),
      simplified: json['simplified'] as bool? ?? false,
    );
  }

  /// Há pelo menos 2 pontos para desenhar uma polyline?
  bool get hasPolyline => points.length >= 2;
}