// [Sessão 11] construtor fromBbox + modo estático para miniatura no feed.
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../models/activity_track.dart';

/// Mapa somente-leitura da rota de uma atividade.
///
/// Dois modos:
/// - **Track** (`ActivityMap(track: ...)`): desenha polyline + pinos de
///   início/fim, interativo, com toggle Mapa/Satélite. Usado no detalhe.
/// - **Bbox** (`ActivityMap.fromBbox(...)`): enquadra o bounding box,
///   sem polyline e sem pinos. Ideal para miniatura no feed. Interativo
///   por padrão, mas o feed passa `interactive: false` + `showLayerToggle: false`.
///
/// Sem API key: alterna entre OpenStreetMap (mapa) e Esri World Imagery
/// (satélite), ambos com tiles públicos.
class ActivityMap extends StatefulWidget {
  // Modo track (completo).
  final ActivityTrack? track;
  // Modo bbox (miniatura).
  final List<double>? bbox;

  final double height;
  final bool interactive;
  final bool showLayerToggle;

  const ActivityMap({
    super.key,
    required ActivityTrack this.track,
    this.height = 240,
    this.interactive = true,
    this.showLayerToggle = true,
  }) : bbox = null;

  /// Construtor para miniatura de mapa a partir de um bounding box GeoJSON
  /// `[minLon, minLat, maxLon, maxLat]`. Sem polyline, sem pinos.
  const ActivityMap.fromBbox({
    super.key,
    required List<double> this.bbox,
    this.height = 120,
    this.interactive = false,
    this.showLayerToggle = false,
  }) : track = null;

  @override
  State<ActivityMap> createState() => _ActivityMapState();
}

class _ActivityMapState extends State<ActivityMap> {
  bool _satelite = false;

  // Ordem dos placeholders é diferente entre os dois provedores:
  //   OSM:   {z}/{x}/{y}
  //   Esri:  {z}/{y}/{x}
  static const String _osmUrl =
      'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  static const String _esriUrl =
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';

  static const String _osmAttribution = 'OpenStreetMap contributors';
  static const String _esriAttribution =
      'Esri, Maxar, Earthstar Geographics, and the GIS User Community';

  void _toggleLayer() {
    setState(() => _satelite = !_satelite);
  }

  /// Traduz `bbox` GeoJSON `[minLon, minLat, maxLon, maxLat]` em LatLngBounds.
  /// Retorna `null` se malformado (menos de 4 elementos).
  LatLngBounds? _boundsFromBbox() {
    final b = widget.bbox;
    if (b == null || b.length < 4) return null;
    // GeoJSON: [minLon, minLat, maxLon, maxLat] -> LatLng é (lat, lon).
    return LatLngBounds(
      LatLng(b[1], b[0]), // south-west (minLat, minLon)
      LatLng(b[3], b[2]), // north-east (maxLat, maxLon)
    );
  }

  @override
  Widget build(BuildContext context) {
    // ---------- Modo bbox (miniatura) ----------
    if (widget.track == null) {
      final bounds = _boundsFromBbox();
      if (bounds == null) {
        return _MapPlaceholder(
          height: widget.height,
          message: 'Rota sem coordenadas',
        );
      }

      return ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: SizedBox(
          height: widget.height,
          child: FlutterMap(
            options: MapOptions(
              initialCameraFit: CameraFit.bounds(
                bounds: bounds,
                padding: const EdgeInsets.all(8),
              ),
              interactionOptions: InteractionOptions(
                flags: widget.interactive
                    ? InteractiveFlag.pinchZoom | InteractiveFlag.drag
                    : InteractiveFlag.none,
              ),
            ),
            children: [
              TileLayer(
                urlTemplate: _satelite ? _esriUrl : _osmUrl,
                userAgentPackageName: 'com.rumo.mobile',
              ),
              SimpleAttributionWidget(
                source: Text(_satelite ? _esriAttribution : _osmAttribution),
              ),
            ],
          ),
        ),
      );
    }

    // ---------- Modo track (detalhe) ----------
    final track = widget.track!;
    final points = track.points;

    if (points.isEmpty) {
      return _MapPlaceholder(
        height: widget.height,
        message: 'Rota sem pontos',
      );
    }

    final start = points.first;
    final end = points.last;

    final MapOptions options;
    if (points.length >= 2) {
      options = MapOptions(
        initialCameraFit: CameraFit.bounds(
          bounds: LatLngBounds.fromPoints(points),
          padding: const EdgeInsets.all(24),
        ),
        interactionOptions: InteractionOptions(
          flags: widget.interactive
              ? InteractiveFlag.pinchZoom | InteractiveFlag.drag
              : InteractiveFlag.none,
        ),
      );
    } else {
      options = MapOptions(
        initialCenter: points.first,
        initialZoom: 15,
        interactionOptions: InteractionOptions(
          flags: widget.interactive
              ? InteractiveFlag.pinchZoom | InteractiveFlag.drag
              : InteractiveFlag.none,
        ),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: SizedBox(
        height: widget.height,
        child: Stack(
          children: [
            FlutterMap(
              options: options,
              children: [
                TileLayer(
                  urlTemplate: _satelite ? _esriUrl : _osmUrl,
                  userAgentPackageName: 'com.rumo.mobile',
                ),
                if (track.hasPolyline)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: points,
                        strokeWidth: 4,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ],
                  ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: start,
                      width: 28,
                      height: 28,
                      child:
                          const _Pin(color: Colors.green, icon: Icons.play_arrow),
                    ),
                    if (points.length >= 2)
                      Marker(
                        point: end,
                        width: 28,
                        height: 28,
                        child: const _Pin(color: Colors.red, icon: Icons.flag),
                      ),
                  ],
                ),
                SimpleAttributionWidget(
                  source: Text(
                    _satelite ? _esriAttribution : _osmAttribution,
                  ),
                ),
              ],
            ),
            if (widget.showLayerToggle)
              Positioned(
                top: 8,
                right: 8,
                child: Material(
                  color: Colors.white,
                  elevation: 2,
                  shape: const CircleBorder(),
                  child: IconButton(
                    onPressed: _toggleLayer,
                    icon: Icon(
                      _satelite ? Icons.map : Icons.satellite_alt,
                      color: Colors.black87,
                    ),
                    tooltip: _satelite ? 'Ver mapa' : 'Ver satélite',
                    iconSize: 20,
                    visualDensity: VisualDensity.compact,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _Pin extends StatelessWidget {
  final Color color;
  final IconData icon;

  const _Pin({required this.color, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white, width: 2),
      ),
      child: Icon(icon, size: 16, color: Colors.white),
    );
  }
}

class _MapPlaceholder extends StatelessWidget {
  final double height;
  final String message;

  const _MapPlaceholder({required this.height, required this.message});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Text(message, style: theme.textTheme.bodySmall),
      ),
    );
  }
}