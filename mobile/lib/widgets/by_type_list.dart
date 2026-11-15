// [Sessão 33] Lista de drill-down por tipo (stats/by-type) do perfil.
//
// Espelha a seção "Por tipo de atividade" do web
// (web/src/pages/ProfilePage.tsx, componentes privados PreviousDelta e
// DeltaLine no fim do arquivo) — mesma semântica, layout mobile.
//
// Paridade semântica com o web:
// - Colunas do web: Tipo | Atividades | Distância | Elevação | Tempo |
//   Pace médio | Calorias | [vs. anterior (se period!="all")].
// - No mobile (tela estreita), 8 colunas não cabem → cada tipo vira um
//   Card com header (label + N atividades), grade 2×3 de métricas
//   (Distância, Elevação, Tempo, Pace médio, Calorias) e o bloco de
//   delta embaixo, quando houver `previous`.
// - Pace médio só nos PACE_TYPES (run/walk/hike) — ciclismo/natação/outro
//   mostram "—", igual ao web. O delta de pace também só nesses tipos,
//   com `lowerIsBetter: true` (pace menor = melhor) — S30 no web.
//
// Sinal matemático do delta segue o delta cru (não inverte em
// lowerIsBetter) — só a cor inverte. Texto: "Label +abs (+pct%)" ou
// "Label −abs (−pct%)". Sinal "−" é U+2212 (mesmo do web), não hífen.
import 'package:flutter/material.dart';

import 'package:rumo_mobile/models/stats.dart';
import 'package:rumo_mobile/utils/format.dart';

/// Tipos em que pace (e delta de pace) fazem sentido.
/// Espelha PACE_TYPES do web. Ciclismo/natação/outro ficam de fora.
const Set<String> _paceTypes = {'run', 'walk', 'hike'};

/// Rótulos pt-BR dos tipos. Espelha TYPE_LABELS do web.
String _typeLabel(String type) {
  switch (type) {
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

class ByTypeList extends StatelessWidget {
  final StatsByTypeResponse? data;
  final bool isLoading;
  final bool isError;

  const ByTypeList({
    super.key,
    required this.data,
    required this.isLoading,
    required this.isError,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (isLoading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 16),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (isError || data == null) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Text(
          'Erro ao carregar tabela por tipo.',
          style: TextStyle(color: theme.colorScheme.error),
        ),
      );
    }

    if (data!.items.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Text(
          'Nenhuma atividade registrada ainda.',
          style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final item in data!.items)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _ByTypeCard(item: item),
          ),
      ],
    );
  }
}

class _ByTypeCard extends StatelessWidget {
  final StatsByTypeItem item;

  const _ByTypeCard({required this.item});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final showPace = _paceTypes.contains(item.activityType);
    final pace = computePace(
      totalDurationS: item.totalDurationS,
      totalDistanceM: item.totalDistanceM,
    );

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header: tipo + total de atividades.
            Row(
              children: [
                Expanded(
                  child: Text(
                    _typeLabel(item.activityType),
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Text(
                  '${item.totalActivities} '
                  '${item.totalActivities == 1 ? 'atividade' : 'atividades'}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // Grade 2×3 de métricas (Wrap para quebrar conforme a largura).
            Wrap(
              spacing: 16,
              runSpacing: 6,
              children: [
                _Metric(
                  label: 'Distância',
                  value: formatDistance(item.totalDistanceM),
                ),
                _Metric(
                  label: 'Elevação',
                  value: formatElevation(item.totalElevationGainM),
                ),
                _Metric(
                  label: 'Tempo',
                  value: formatDuration(item.totalDurationS),
                ),
                _Metric(
                  label: 'Pace médio',
                  value: showPace ? formatPace(pace) : '—',
                ),
                _Metric(
                  label: 'Calorias',
                  value: formatCalories(item.totalCalories),
                ),
              ],
            ),
            // Delta vs. janela anterior — só quando há comparação.
            // O web só renderiza a coluna quando period != "all"; aqui
            // o caller (ProfilePage) só passa itens com previous != null
            // quando pediu period=90d/1y. O _PreviousDelta ainda tem o
            // guard de `previous == null` por segurança.
            if (item.previous != null) ...[
              const SizedBox(height: 8),
              const Divider(height: 1),
              const SizedBox(height: 8),
              _PreviousDelta(item: item),
            ],
          ],
        ),
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  final String label;
  final String value;

  const _Metric({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SizedBox(
      width: 96,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              letterSpacing: 0.5,
              fontSize: 9,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

/// Bloco de delta vs. janela anterior. Porta o PreviousDelta do web.
///
/// 5 DeltaLines fixos (atividades, distância, elevação, tempo, calorias)
/// + Pace (lowerIsBetter) apenas nos PACE_TYPES — mesma regra do web.
/// `previous == null` → "—" cinza (tipo não existia na janela anterior).
class _PreviousDelta extends StatelessWidget {
  final StatsByTypeItem item;

  const _PreviousDelta({required this.item});

  @override
  Widget build(BuildContext context) {
    final previous = item.previous;
    if (previous == null) {
      return Text(
        '—',
        style: TextStyle(
          color: Theme.of(context).colorScheme.onSurfaceVariant,
        ),
      );
    }

    final showPace = _paceTypes.contains(item.activityType);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _DeltaLine(
          label: 'Ativ.',
          current: item.totalActivities.toDouble(),
          previous: previous.totalActivities.toDouble(),
        ),
        _DeltaLine(
          label: 'Dist.',
          current: item.totalDistanceM,
          previous: previous.totalDistanceM,
          formatter: formatDistance,
        ),
        _DeltaLine(
          label: 'Elev.',
          current: item.totalElevationGainM,
          previous: previous.totalElevationGainM,
          formatter: formatElevation,
        ),
        _DeltaLine(
          label: 'Tempo',
          current: item.totalDurationS.toDouble(),
          previous: previous.totalDurationS.toDouble(),
          formatter: formatDuration,
        ),
        _DeltaLine(
          label: 'Cal.',
          current: item.totalCalories.toDouble(),
          previous: previous.totalCalories.toDouble(),
          formatter: formatCalories,
        ),
        if (showPace)
          _DeltaLine(
            label: 'Pace',
            current: computePace(
                  totalDurationS: item.totalDurationS,
                  totalDistanceM: item.totalDistanceM,
                ) ??
                0,
            previous: computePace(
                  totalDurationS: previous.totalDurationS,
                  totalDistanceM: previous.totalDistanceM,
                ) ??
                0,
            formatter: formatPace,
            lowerIsBetter: true,
          ),
      ],
    );
  }
}

/// Uma linha de delta: "Label ±abs (±pct%)" colorida.
///
/// Porta o DeltaLine do web (S18 + S28 + S30) com a semântica exata:
/// - delta = current - previous
/// - sign = "+" se delta > 0, "−" (U+2212) se delta < 0, "" se 0
/// - pct = previous > 0 ? round(delta/previous * 100) : null
/// - isGood = lowerIsBetter ? delta < 0 : delta > 0
/// - isBad  = lowerIsBetter ? delta > 0 : delta < 0
/// - cor: verde (good), vermelho (bad), cinza (delta == 0)
///
/// `lowerIsBetter` só é usado por Pace — pace menor = mais rápido = melhor.
/// O sinal matemático (+/−) segue o delta cru; só a cor inverte.
class _DeltaLine extends StatelessWidget {
  final String label;
  final double current;
  final double previous;
  final String Function(num)? formatter;
  final bool lowerIsBetter;

  const _DeltaLine({
    required this.label,
    required this.current,
    required this.previous,
    this.formatter,
    this.lowerIsBetter = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final delta = current - previous;
    final fmt = formatter ?? (num n) => n.round().toString();
    final sign = delta > 0 ? '+' : (delta < 0 ? '−' : '');
    final abs = delta.abs();
    final pct = previous > 0
        ? ((delta / previous) * 100).round()
        : null;

    final isGood = lowerIsBetter ? delta < 0 : delta > 0;
    final isBad = lowerIsBetter ? delta > 0 : delta < 0;
    final Color color;
    if (isGood) {
      color = Colors.green.shade700;
    } else if (isBad) {
      color = Colors.red.shade700;
    } else {
      color = theme.colorScheme.onSurfaceVariant;
    }

    final pctText = pct != null ? ' ($sign${pct.abs()}%)' : '';

    return Text(
      '$label $sign${fmt(abs)}$pctText',
      style: theme.textTheme.bodySmall?.copyWith(color: color),
    );
  }
}