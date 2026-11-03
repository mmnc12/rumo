import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/like_button.dart';

class FeedPage extends StatefulWidget {
  final AuthService auth;
  const FeedPage({super.key, required this.auth});

  @override
  State<FeedPage> createState() => _FeedPageState();
}

class _FeedPageState extends State<FeedPage> {
  List<Activity> _activities = [];
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
        '/feed?limit=20&offset=0',
        token: widget.auth.token,
      );
      final list = (data as List)
          .map((e) => Activity.fromJson(e as Map<String, dynamic>))
          .toList();
      setState(() => _activities = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Erro: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  /// Substitui um item da lista pelo `updated` (mesmo id).
  /// Chamado pelo LikeButton com o estado otimista e, em erro, com o original
  /// (rollback). Como o LikeButton faz o merge, aqui só trocamos o item.
  void _replaceActivity(Activity updated) {
    setState(() {
      _activities = _activities
          .map((a) => a.id == updated.id ? updated : a)
          .toList();
    });
  }

  /// Abre o detalhe e, ao voltar, recarrega o item para refletir
  /// contagens de comentários/crudes feitas lá.
  Future<void> _openDetail(Activity activity) async {
    await context.push('/activity/${activity.id}');
    if (!mounted) return;
    // Recarrega apenas esse item do detalhe para atualizar commentsCount.
    try {
      final data = await widget.auth.api.get(
        '/activities/${activity.id}',
        token: widget.auth.token,
      );
      final updated = Activity.fromJson(data as Map<String, dynamic>);
      _replaceActivity(updated);
    } catch (_) {
      // silencioso: se falhar, mantém o estado atual do feed.
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Feed'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sair',
            onPressed: () async {
              await widget.auth.logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
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
              : _activities.isEmpty
                  ? const Center(child: Text('Nenhuma atividade ainda.'))
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.separated(
                        padding: const EdgeInsets.all(12),
                        itemCount: _activities.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 12),
                        itemBuilder: (context, index) {
                          final a = _activities[index];
                          return _ActivityCard(
                            activity: a,
                            auth: widget.auth,
                            onTap: () => _openDetail(a),
                            onChanged: _replaceActivity,
                          );
                        },
                      ),
                    ),
    );
  }
}

class _ActivityCard extends StatelessWidget {
  final Activity activity;
  final AuthService auth;
  final VoidCallback onTap;
  final ValueChanged<Activity> onChanged;

  const _ActivityCard({
    required this.activity,
    required this.auth,
    required this.onTap,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Cabeçalho: avatar + username + tipo
              Row(
                children: [
                  CircleAvatar(
                    radius: 16,
                    backgroundImage: activity.user?.avatarUrl != null
                        ? NetworkImage(activity.user!.avatarUrl!)
                        : null,
                    child: activity.user?.avatarUrl == null
                        ? Text(
                            (activity.user?.username ?? '?')
                                .substring(0, 1)
                                .toUpperCase(),
                          )
                        : null,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      activity.user?.username ?? 'Usuário',
                      style: theme.textTheme.titleSmall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Text(
                    activity.typeLabel,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Título
              Text(
                activity.title ?? activity.typeLabel,
                style: theme.textTheme.titleMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),

              // Métricas
              Wrap(
                spacing: 12,
                runSpacing: 4,
                children: [
                  if (activity.distanceLabel != null)
                    _Metric(
                      icon: Icons.straighten,
                      text: activity.distanceLabel!,
                    ),
                  if (activity.durationLabel != null)
                    _Metric(
                      icon: Icons.timer_outlined,
                      text: activity.durationLabel!,
                    ),
                  if (activity.caloriesLabel != null)
                    _Metric(
                      icon: Icons.local_fire_department,
                      text: activity.caloriesLabel!,
                    ),
                ],
              ),
              const SizedBox(height: 8),

              // Rodapé: data + curtidas + comentários
              Row(
                children: [
                  Expanded(
                    child: Text(
                      activity.startedAtLabel,
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                  LikeButton(
                    activity: activity,
                    auth: auth,
                    onChanged: onChanged,
                  ),
                  const SizedBox(width: 4),
                  // Botão de comentários com contador; navega para o detalhe.
                  TextButton.icon(
                    onPressed: onTap,
                    icon: const Icon(Icons.chat_bubble_outline, size: 18),
                    label: Text('${activity.commentsCount}'),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      minimumSize: const Size(0, 36),
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  final IconData icon;
  final String text;
  const _Metric({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16),
        const SizedBox(width: 4),
        Text(text),
      ],
    );
  }
}