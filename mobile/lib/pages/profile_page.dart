// [Sessão 32] Perfil próprio + "minhas atividades".
//
// Cabeçalho vem de GET /auth/me (UserResponse — tem email, ao contrário
// do UserPublic de /users/{id}, que é minimalista: id, username,
// full_name, is_active). Lista vem de GET /activities?user_id=<me>&...
//
// Fora de escopo da S32 (por contrato):
// - Stats agregados (/users/{id}/stats/summary) — S33.
// - Perfil de terceiro + follow — S34.
// - Editar perfil (peso, altura, etc.) — S33+.
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../models/user_me.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/activity_card.dart';

class ProfilePage extends StatefulWidget {
  final AuthService auth;
  const ProfilePage({super.key, required this.auth});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  static const int _pageSize = 20;

  UserMe? _me;
  List<Activity> _activities = [];
  bool _loading = true;
  String? _error;
  int _offset = 0;
  bool _hasMore = true;
  bool _loadingMore = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() {
      _loading = true;
      _error = null;
    });

    final userId = widget.auth.currentUserId;
    if (userId == null) {
      if (!mounted) return;
      setState(() {
        _error = 'Sessão sem id de usuário. Faça login novamente.';
        _loading = false;
      });
      return;
    }

    try {
      final results = await Future.wait([
        widget.auth.api.get('/auth/me', token: widget.auth.token),
        widget.auth.api.listActivities(
          userId: userId,
          limit: _pageSize,
          offset: 0,
          token: widget.auth.token,
        ),
      ]);
      if (!mounted) return;
      final meData = results[0];
      final page = results[1] as List<Activity>;
      if (meData is! Map<String, dynamic>) {
        throw ApiException(500, 'Resposta inesperada em /auth/me');
      }
      setState(() {
        _me = UserMe.fromJson(meData);
        _activities = page;
        _offset = page.length;
        _hasMore = page.length == _pageSize;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = 'Erro: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _loadMore() async {
    if (_loadingMore || !_hasMore) return;
    final userId = widget.auth.currentUserId;
    if (userId == null) return;

    setState(() => _loadingMore = true);
    try {
      final page = await widget.auth.api.listActivities(
        userId: userId,
        limit: _pageSize,
        offset: _offset,
        token: widget.auth.token,
      );
      if (!mounted) return;
      setState(() {
        _activities = [..._activities, ...page];
        _offset += page.length;
        _hasMore = page.length == _pageSize;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message)),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: $e')),
      );
    } finally {
      if (mounted) setState(() => _loadingMore = false);
    }
  }

  Future<void> _logout() async {
    await widget.auth.logout();
    if (!mounted) return;
    context.go('/login');
  }

  Future<void> _openDetail(Activity activity) async {
    await context.push('/activity/${activity.id}');
    if (!mounted) return;
    // Recarrega só esse item para atualizar contadores (comentários etc.).
    try {
      final data = await widget.auth.api.get(
        '/activities/${activity.id}',
        token: widget.auth.token,
      );
      if (!mounted) return;
      final updated = Activity.fromJson(data as Map<String, dynamic>);
      setState(() {
        _activities = _activities
            .map((a) => a.id == updated.id ? updated : a)
            .toList();
      });
    } catch (_) {
      // silencioso: mantém o estado atual.
    }
  }

  void _replaceActivity(Activity updated) {
    setState(() {
      _activities = _activities
          .map((a) => a.id == updated.id ? updated : a)
          .toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(_error!, textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: _load,
                          child: const Text('Tentar novamente'),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.all(12),
                    children: [
                      if (_me != null) _ProfileHeader(me: _me!, onLogout: _logout),
                      const SizedBox(height: 16),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: Text(
                          'Minhas atividades',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (_activities.isEmpty)
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 32),
                          child: Center(
                            child: Text('Você ainda não enviou atividades.'),
                          ),
                        )
                      else
                        ..._activities.map(
                          (a) => Padding(
                            padding: const EdgeInsets.only(bottom: 12),
                            child: ActivityCard(
                              activity: a,
                              auth: widget.auth,
                              onTap: () => _openDetail(a),
                              onChanged: _replaceActivity,
                            ),
                          ),
                        ),
                      if (_activities.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        if (_hasMore)
                          Center(
                            child: _loadingMore
                                ? const Padding(
                                    padding: EdgeInsets.all(16),
                                    child: SizedBox(
                                      width: 24,
                                      height: 24,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    ),
                                  )
                                : FilledButton.tonal(
                                    onPressed: _loadMore,
                                    child: const Text('Carregar mais'),
                                  ),
                          )
                        else
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 16),
                            child: Center(
                              child: Text(
                                'Fim.',
                                style: TextStyle(color: Colors.grey),
                              ),
                            ),
                          ),
                      ],
                    ],
                  ),
                ),
    );
  }
}

class _ProfileHeader extends StatelessWidget {
  final UserMe me;
  final VoidCallback onLogout;

  const _ProfileHeader({required this.me, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final initial = me.username.isNotEmpty
        ? me.username.substring(0, 1).toUpperCase()
        : '?';

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  child: Text(
                    initial,
                    style: theme.textTheme.titleLarge,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        me.username,
                        style: theme.textTheme.titleLarge,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (me.fullName != null && me.fullName!.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          me.fullName!,
                          style: theme.textTheme.bodyMedium,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      const SizedBox(height: 4),
                      Text(
                        me.email,
                        style: theme.textTheme.bodySmall,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: onLogout,
                icon: const Icon(Icons.logout, size: 18),
                label: const Text('Sair'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}