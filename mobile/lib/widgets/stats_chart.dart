// [Sessão 38] Chart de linha weekly/monthly do perfil.
//
// Paridade 1:1 com web/src/components/PeriodChart.tsx (S14):
// - 4 combinações: (weekly|monthly) × (distance|activities).
// - metric="distance": eixo Y em km, tooltip "X.X km".
// - metric="activities": eixo Y contagem inteira, domain [0, yMax] com
//   yMax >= 5 arredondado pra cima em múltiplos de 5.
// - period="weekly": label X "DD/MM", tooltip "Semana de DD/MM".
// - period="monthly": label X "MM/YYYY", tooltip "Mês de MM/YYYY".
// - Título e estados (loading/erro/vazio) idênticos ao web.
//
// Implementação: fl_chart (Dart puro, MIT, sem código nativo).
// No fl_chart o eixo X é numérico (index 0..N-1); os labels vêm de
// getTitlesWidget mapeando index → label — o resultado visual é o
// mesmo do web.
//
// Cor da linha: #f97316 (laranja do web).
// Altura: 256px (16rem do web).
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../models/stats.dart';

export '../models/stats.dart' show StatsPeriod;

/// Período do chart. Espelha `ChartPeriod` do web.
enum ChartPeriod { weekly, monthly }

/// Métrica do chart. Espelha `ChartMetric` do web.
enum ChartMetric { distance, activities }

class StatsChart extends StatelessWidget {
  final ChartPeriod period;
  final ChartMetric metric;
  final List<StatsPeriod>? items;
  final bool isLoading;
  final bool isError;

  const StatsChart({
    super.key,
    required this.period,
    required this.metric,
    required this.items,
    required this.isLoading,
    required this.isError,
  });

  String get _title {
    if (metric == ChartMetric.distance) {
      return period == ChartPeriod.weekly
          ? 'Distância por semana (km)'
          : 'Distância por mês (km)';
    }
    return period == ChartPeriod.weekly
        ? 'Atividades por semana'
        : 'Atividades por mês';
  }

  String get _tooltipLabel =>
      period == ChartPeriod.weekly ? 'Semana de' : 'Mês de';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _title,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              height: 256,
              child: _buildBody(context, theme),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody(BuildContext context, ThemeData theme) {
    if (isLoading) {
      return Container(
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(8),
        ),
      );
    }

    if (isError || items == null) {
      return Center(
        child: Text(
          'Erro ao carregar gráfico.',
          style: TextStyle(color: theme.colorScheme.error),
        ),
      );
    }

    if (items!.isEmpty) {
      return Center(
        child: Text(
          period == ChartPeriod.weekly
              ? 'Sem dados nas últimas semanas.'
              : 'Sem dados nos últimos meses.',
          style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
        ),
      );
    }

    return _buildChart(context, theme);
  }

  Widget _buildChart(BuildContext context, ThemeData theme) {
    final data = items!;
    // x = index 0..N-1 (ordem do backend é crescente em period_start).
    final spots = <FlSpot>[];
    for (var i = 0; i < data.length; i++) {
      final v = metric == ChartMetric.distance
          ? data[i].totalDistanceM / 1000.0 // km
          : data[i].totalActivities.toDouble();
      spots.add(FlSpot(i.toDouble(), v));
    }

    // yMax: só pra activities (contagem inteira), paridade com o web.
    double? yMax;
    if (metric == ChartMetric.activities) {
      double maxVal = 0;
      for (final s in spots) {
        if (s.y > maxVal) maxVal = s.y;
      }
      yMax = maxVal < 5 ? 5 : ((maxVal + 1) / 5).ceil() * 5.0;
    }

    // Y max "solto" pra distance: só um pouco de folga pro topo.
    if (yMax == null) {
      double maxVal = 0;
      for (final s in spots) {
        if (s.y > maxVal) maxVal = s.y;
      }
      yMax = maxVal <= 0 ? 1 : maxVal * 1.15;
    }

    // Labels X por index.
    final labels = data.map((p) => _formatLabel(p.periodStart)).toList();

    return LineChart(
      LineChartData(
        minX: 0,
        maxX: (data.length - 1).toDouble(),
        minY: 0,
        maxY: yMax,
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          getDrawingHorizontalLine: (v) => FlLine(
            color: const Color(0xFFE5E7EB),
            strokeWidth: 1,
            dashArray: [3, 3],
          ),
        ),
        borderData: FlBorderData(show: false),
        titlesData: FlTitlesData(
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              interval: _yInterval(yMax),
              getTitlesWidget: (value, meta) => Text(
                _formatY(value),
                style: const TextStyle(
                  fontSize: 11,
                  color: Color(0xFF6B7280),
                ),
              ),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 28,
              interval: 1,
              getTitlesWidget: (value, meta) {
                final i = value.round();
                if (i < 0 || i >= labels.length) {
                  return const SizedBox.shrink();
                }
                // Mostra só alguns labels pra não lotar (paridade: o
                // web deixa o recharts decidir; aqui é 1 a cada N).
                final step = labels.length <= 6 ? 1 : (labels.length / 6).ceil();
                if (i % step != 0 && i != labels.length - 1) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(
                    labels[i],
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF6B7280),
                    ),
                  ),
                );
              },
            ),
          ),
        ),
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipColor: (_) => Colors.white,
            getTooltipItems: (touchedSpots) => touchedSpots.map((s) {
              final i = s.x.round();
              final label = (i >= 0 && i < labels.length) ? labels[i] : '';
              final valueText = _formatTooltipValue(s.y);
              return LineTooltipItem(
                '$_tooltipLabel $label\n$valueText',
                const TextStyle(
                  color: Color(0xFF111827),
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              );
            }).toList(),
          ),
        ),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: false,
            color: const Color(0xFFF97316),
            barWidth: 2,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, percent, bar, index) =>
                  FlDotCirclePainter(
                radius: 3,
                color: const Color(0xFFF97316),
                strokeWidth: 0,
              ),
            ),
            belowBarData: BarAreaData(show: false),
          ),
        ],
      ),
    );
  }

  /// "2026-10-13" → "13/10" (weekly). "2026-11-01" → "11/2026" (monthly).
  String _formatLabel(String iso) {
    final parts = iso.split('-');
    if (parts.length != 3) return iso;
    final year = parts[0];
    final month = parts[1];
    final day = parts[2];
    if (period == ChartPeriod.weekly) {
      return '$day/$month';
    }
    return '$month/$year';
  }

  /// Y do eixo (só no eixo, não no tooltip): inteiro para activities,
  /// 1 casa decimal para distance.
  String _formatY(double v) {
    if (metric == ChartMetric.activities) {
      return v.round().toString();
    }
    return v.toStringAsFixed(1);
  }

  /// Texto do tooltip: "1.0 km" ou "N atividade(s)".
  String _formatTooltipValue(double v) {
    if (metric == ChartMetric.distance) {
      return '${v.toStringAsFixed(1)} km';
    }
    final n = v.round();
    return n == 1 ? '1 atividade' : '$n atividades';
  }

  /// Intervalo do eixo Y. Activities: passo 5 (paridade com yMax múltiplo
  /// de 5). Distance: passo adaptativo pro número de ticks ficar ~5.
  double _yInterval(double yMax) {
    if (metric == ChartMetric.activities) return 5;
    if (yMax <= 1) return 0.25;
    if (yMax <= 5) return 1;
    if (yMax <= 20) return 5;
    if (yMax <= 100) return 20;
    return (yMax / 5).ceilToDouble();
  }
}