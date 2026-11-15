// [Sessão 33] Cards de resumo (stats/summary) do perfil.
//
// Espelha web/src/components/StatsCards.tsx 1:1 em conteúdo:
// 5 cards, mesma ordem, mesmos labels, mesmos formatadores:
//   Atividades | Distância | Tempo | Elevação | Calorias
//
// Ignora avg_pace_s_per_km e avg_speed_mps do StatsSummary — o web
// também ignora (esses campos existem no model, mas não são exibidos
// no resumo agregado; pace médio agregado é ambíguo entre tipos, e
// o pace por tipo já aparece no ByTypeList).
//
// Usa Wrap (não GridView) — evita shrinkWrap/NeverScrollable dentro
// do ListView do ProfilePage; Wrap mede os filhos e quebra linha sem
// precisar de altura fixa.
//
// [Sessão 33 — fix] Imports como package: (regra avoid_relative_lib_imports
// do flutter_lints). O format.dart foi movido para lib/utils/ no commit
// e15bedd; o import agora é package:rumo_mobile/utils/format.dart.
import 'package:flutter/material.dart';

import 'package:rumo_mobile/models/stats.dart';
import 'package:rumo_mobile/utils/format.dart';

class StatsCards extends StatelessWidget {
  final StatsSummary? data;
  final bool isLoading;
  final bool isError;

  const StatsCards({
    super.key,
    required this.data,
    required this.isLoading,
    required this.isError,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Wrap(
        spacing: 8,
        runSpacing: 8,
        children: List.generate(
          5,
          (_) => const _SkeletonCard(),
        ),
      );
    }

    if (isError || data == null) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Text(
          'Erro ao carregar estatísticas.',
          style: TextStyle(
            color: Theme.of(context).colorScheme.error,
          ),
        ),
      );
    }

    final d = data!;
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _StatCard(
          label: 'Atividades',
          value: d.totalActivities.toString(),
        ),
        _StatCard(
          label: 'Distância',
          value: formatDistance(d.totalDistanceM),
        ),
        _StatCard(
          label: 'Tempo',
          value: formatDuration(d.totalDurationS),
        ),
        _StatCard(
          label: 'Elevação',
          value: formatElevation(d.totalElevationGainM),
        ),
        _StatCard(
          label: 'Calorias',
          value: formatCalories(d.totalCalories),
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;

  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: 160,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _SkeletonCard extends StatelessWidget {
  const _SkeletonCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 160,
      height: 68,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
      ),
    );
  }
}