// [Sessão 38] Filtros de period/compare da seção de estatísticas.
//
// Paridade com o web (ProfilePage.tsx → selects de period/compare, S17/S20):
// - period: "all" (todos os tempos) | "90d" (últimos 90 dias) | "1y" (365 dias).
// - compare: "prev" (janela imediatamente anterior) | "yoy" (ano anterior).
// - period == "all" → compare é IGNORADO pelo backend (previous sempre null);
//   na UI, o SegmentedButton de compare fica desabilitado nesse caso.
//
// Semântica de "disabled":
// - `disabled: true` (stats 403 ou loading inicial) → os dois SegmentedButton
//   ficam desabilitados, sem toque.
// - `period == "all"` → só o compare fica desabilitado (period continua ativo).
//
// O caller (ProfilePage/UserProfilePage) guarda o estado (_statsPeriod,
// _statsCompare) e refaz o _loadStats() quando onChanged dispara.
import 'package:flutter/material.dart';

/// Janela temporal dos stats. Espelha `StatsPeriod` do web/backend.
/// String (não enum) por paridade com `getStatsByType(period: String)`.
const String kStatsPeriodAll = 'all';
const String kStatsPeriod90d = '90d';
const String kStatsPeriod1y = '1y';

/// Janela de comparação. Espelha `StatsCompare` do web/backend.
const String kStatsComparePrev = 'prev';
const String kStatsCompareYoy = 'yoy';

class StatsFilters extends StatelessWidget {
  final String period;
  final String compare;
  final bool disabled;
  final void Function(String period, String compare) onChanged;

  const StatsFilters({
    super.key,
    required this.period,
    required this.compare,
    required this.disabled,
    required this.onChanged,
  });

  bool get _compareDisabled => disabled || period == kStatsPeriodAll;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Janela', style: theme.textTheme.labelLarge),
            const SizedBox(height: 6),
            SizedBox(
              width: double.infinity,
              child: SegmentedButton<String>(
                segments: const [
                  ButtonSegment(
                    value: kStatsPeriodAll,
                    label: Text('Todas'),
                  ),
                  ButtonSegment(
                    value: kStatsPeriod90d,
                    label: Text('90d'),
                  ),
                  ButtonSegment(
                    value: kStatsPeriod1y,
                    label: Text('1a'),
                  ),
                ],
                selected: <String>{period},
                onSelectionChanged: disabled
                    ? null
                    : (s) {
                        if (s.isEmpty) return;
                        final newPeriod = s.first;
                        // Se virou "all", o compare não tem efeito — mas
                        // mantemos o valor atual no estado (paridade com o
                        // web: o select de compare não é resetado ao trocar
                        // period; só fica desabilitado visualmente).
                        onChanged(newPeriod, compare);
                      },
              ),
            ),
            const SizedBox(height: 12),
            Text('Comparar com', style: theme.textTheme.labelLarge),
            const SizedBox(height: 6),
            SizedBox(
              width: double.infinity,
              child: SegmentedButton<String>(
                segments: const [
                  ButtonSegment(
                    value: kStatsComparePrev,
                    label: Text('Período anterior'),
                  ),
                  ButtonSegment(
                    value: kStatsCompareYoy,
                    label: Text('Ano anterior'),
                  ),
                ],
                selected: <String>{compare},
                onSelectionChanged: _compareDisabled
                    ? null
                    : (s) {
                        if (s.isEmpty) return;
                        onChanged(period, s.first);
                      },
              ),
            ),
          ],
        ),
      ),
    );
  }
}