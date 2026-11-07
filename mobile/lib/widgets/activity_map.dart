import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';

import '../models/activity_track.dart';

/// Mapa somente-leitura da rota de uma atividade.
///
/// - Sem API key: alterna entre OpenStreetMap (mapa) e Esri World Imagery
///   (satélite), ambos com tiles públicos.
/// - Enquadra a rota inteira via `initialCameraFit`.
/// - Marcadores de início (verde) e fim (vermelho).
/// - Botão no canto para alternar entre mapa e satélite.
class ActivityMap extends StatefulWidget {
  final ActivityTrack track;
  final double height;

  const ActivityMap({
    super.key,
    required this.track,
    this.height = 240,
  });

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

  @override
  Widget build(BuildContext context) {
    final track = widget.track;
    final points = track.points;

    // Fallback defensivo: se não houver pontos suficientes, mostra aviso
    // em vez de tentar construir um mapa inválido.
    if (points.isEmpty) {
      return _MapPlaceholder(
        height: widget.height,
        message: 'Rota sem pontos',
      );
    }

    final start = points.first;
    final end = points.last;

    // Enquadramento: se há 2+ pontos, CameraFit.bounds; senão, centro fixo.
    final MapOptions options;
    if (points.length >= 2) {
      options = MapOptions(
        initialCameraFit: CameraFit.bounds(
          bounds: LatLngBounds.fromPoints(points),
          padding: const EdgeInsets.all(24),
        ),
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.pinchZoom | InteractiveFlag.drag,
        ),
      );
    } else {
      options = MapOptions(
        initialCenter: points.first,
        initialZoom: 15,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.pinchZoom | InteractiveFlag.drag,
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
                // Atribuição obrigatória, dinâmica conforme a camada ativa.
                SimpleAttributionWidget(
                  source: Text(
                    _satelite ? _esriAttribution : _osmAttribution,
                  ),
                ),
              ],
            ),
            // Botão de alternância Mapa / Satélite.
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