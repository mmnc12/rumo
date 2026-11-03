import 'package:flutter/material.dart';

import '../models/activity.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/like_button.dart';

class ActivityDetailPage extends StatefulWidget {
  final String activityId;
  final AuthService auth;

  const ActivityDetailPage({
    super.key,
    required this.activityId,
    required this.auth,
  });

  @override
  State<ActivityDetailPage> createState() => _ActivityDetailPageState();
}

class _ActivityDetailPageState extends State<ActivityDetailPage> {
  Activity? _activity;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await widget.auth.api.get(
        '/activities/${widget.activityId}',
        token: widget.auth.token,
      );
      setState(() {
        _activity = Activity.fromJson(data as Map<String, dynamic>);
      });
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Erro: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  /// Atualiza o estado local quando a curtida muda (otimista ou rollback).
  void _onLikeChanged(Activity updated) {
    setState(() {
      _activity = updated;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Detalhe')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _load,
                        child: const Text('Tentar novamente'),
                      ),
                    ],
                  ),
                )
              : _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    final a = _activity!;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          a.title ?? a.typeLabel,
          style: theme.textTheme.headlineSmall,
        ),
        const SizedBox(height: 4),
        Text(
          '${a.typeLabel} • ${a.startedAtLabel}',
          style: theme.textTheme.bodySmall,
        ),
        
        // Autor e Botão de Curtir
        if (a.user != null) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundImage: a.user!.avatarUrl != null
                    ? NetworkImage(a.user!.avatarUrl!)
                    : null,
                child: a.user!.avatarUrl == null
                    ? Text(a.user!.username.substring(0, 1).toUpperCase())
                    : null,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  a.user!.fullName ?? a.user!.username,
                  style: theme.textTheme.titleMedium,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // Botão de curtir integrado
              LikeButton(
                activity: a,
                auth: widget.auth,
                onChanged: _onLikeChanged,
              ),
            ],
          ),
        ],
        
        const SizedBox(height: 24),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 2.2,
          children: [
            if (a.distanceLabel != null)
              _StatCard(label: 'Distância', value: a.distanceLabel!, icon: Icons.straighten),
            if (a.durationLabel != null)
              _StatCard(label: 'Duração', value: a.durationLabel!, icon: Icons.timer_outlined),
            if (a.paceLabel != null)
              _StatCard(label: 'Ritmo', value: a.paceLabel!, icon: Icons.speed),
            if (a.caloriesLabel != null)
              _StatCard(label: 'Calorias', value: a.caloriesLabel!, icon: Icons.local_fire_department),
            if (a.elevationGainM != null)
              _StatCard(
                label: 'Elevação',
                value: '${a.elevationGainM!.round()} m',
                icon: Icons.terrain,
              ),
            if (a.avgSpeedMps != null)
              _StatCard(
                label: 'Vel. média',
                value: '${(a.avgSpeedMps! * 3.6).toStringAsFixed(1)} km/h',
                icon: Icons.speed,
              ),
          ],
        ),
        if (a.description != null && a.description!.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text('Descrição', style: theme.textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(a.description!),
        ],
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: theme.colorScheme.primary),
                const SizedBox(width: 4),
                Text(label, style: theme.textTheme.labelSmall),
              ],
            ),
            const SizedBox(height: 4),
            Text(value, style: theme.textTheme.titleMedium),
          ],
        ),
      ),
    );
  }
}