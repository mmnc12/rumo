// [Sessão 32] Perfil próprio + "minhas atividades".
//
// Cabeçalho vem de GET /auth/me (UserResponse — tem email, ao contrário
// do UserPublic de /users/{id}, que é minimalista: id, username,
// full_name, is_active). Lista vem de GET /activities?user_id=<me>&...
//
// [Sessão 33] +seção de stats agregadas (self-only):
// - GET /users/{me.id}/stats/summary  → StatsCards (5 cards)
// - GET /users/{me.id}/stats/by-type  → ByTypeList (cards por tipo + delta)
//
// Decisões da S33:
// - _load() (perfil + lista) e _loadStats() (stats) são SEPARADOS, com
//   try/catch próprios. Falha de stats não derruba a lista, e vice-versa.
//   O RefreshIndicator chama os dois em paralelo (Future.wait) — se um
//   falhar, o outro continua (cada _load* tem seu próprio catch).
// - Stats usam period=90d&compare=prev (default do contrato S33). O web
//   usa period=all (sem delta); o mobile prioriza mostrar o delta desde
//   a primeira renderização. Filtros de period/compare ficam pra S34.
// - ActivityCard recebe authorUsernameOverride: _me?.username — o
//   GET /activities não embute `user`, e sem o override o card cairia
//   em "Usuário"/"?" no perfil. O feed não muda (GET /feed embute `user`).
//
// Fora de escopo da S33 (por contrato):
// - Filtros de period/compare na UI — S34.
// - Weekly/monthly charts — S34.
// - Perfil de terceiro + follow — S34.
// - Editar perfil — S34+.
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../models/stats.dart';
import '../models/user_me.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/activity_card.dart';
import '../widgets/by_type_list.dart';
import '../widgets/stats_cards.dart';

class ProfilePage extends StatefulWidget {
  final AuthService auth;
  const ProfilePage({super.key, required this.auth});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  static const int _pageSize = 20;

  // ===== Perfil + atividades (S32) =====
  UserMe? _me;
  List<Activity> _activities = [];
  bool _loading = true;
  String? _error;
  int _offset = 0;
  bool _hasMore = true;
  bool _loadingMore = false;

  // ===== Stats agregadas (S33) =====
  StatsSummary? _summary;
  StatsByTypeResponse? _byType;
  bool _statsLoading = true;
  String? _statsError;

  @override
  void initState() {
    super.initState();
    // Carrega em paralelo — cada _load* tem seu próprio try/catch,
    // então uma falha não impede a outra de completar.
    _load();
    _loadStats();
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

  // [Sessão 33] Stats agregadas — separado de _load() de propósito.
  // Roda em paralelo no initState; falha aqui NÃO derruba a lista de
  // atividades (e vice-versa). period=90d&compare=prev é o default do
  // contrato S33 (o web usa "all", mas "all" não tem delta — o delta é
  // o valor da seção de by-type).
  Future<void> _loadStats() async {
    if (!mounted) return;
    setState(() {
      _statsLoading = true;
      _statsError = null;
    });

    final userId = widget.auth.currentUserId;
    if (userId == null) {
      if (!mounted) return;
      setState(() {
        _statsError = 'Sessão sem id de usuário.';
        _statsLoading = false;
      });
      return;
    }

    try {
      final results = await Future.wait([
        widget.auth.api.getStatsSummary(userId, token: widget.auth.token),
        widget.auth.api.getStatsByType(
          userId,
          period: '90d',
          compare: 'prev',
          token: widget.auth.token,
        ),
      ]);
      if (!mounted) return;
      setState(() {
        _summary = results[0] as StatsSummary;
        _byType = results[1] as StatsByTypeResponse;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _statsError = e.message);
    } catch (e) {
      if (!mounted) return;
      setState(() => _statsError = 'Erro: $e');
    } finally {
      if (mounted) setState(() => _statsLoading = false);
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

  // [Sessão 33] Pull-to-refresh recarrega tudo: perfil+lista e stats,
  // em paralelo. Cada um tem seu try/catch — se um falhar, o outro
  // completa (o RefreshIndicator só espera os dois terminarem).
  Future<void> _refreshAll() async {
    await Future.wait([_load(), _loadStats()]);
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
                  onRefresh: _refreshAll,
                  child: ListView(
                    padding: const EdgeInsets.all(12),
                    children: [
                      if (_me != null)
                        _ProfileHeader(me: _me!, onLogout: _logout),
                      const SizedBox(height: 16),

                      // ===== [Sessão 33] Stats agregadas =====
                      // Seção própria: se falhar, mostra erro + "Tentar
                      // novamente" SÓ nos stats, sem afetar a lista abaixo.
                      _StatsSection(
                        summary: _summary,
                        byType: _byType,
                        isLoading: _statsLoading,
                        error: _statsError,
                        onRetry: _loadStats,
                      ),
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
                              // [Sessão 33] GET /activities não embute
                              // `user`; sem o override o card cairia em
                              // "Usuário"/"?". O feed não passa (GET /feed
                              // já traz `user`).
                              authorUsernameOverride: _me?.username,
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

// ===== [Sessão 33] Seção de stats agregadas =====
// Extraída como widget separado pra manter o build() do ProfilePage
// legível e deixar a lógica de loading/erro dos stats autocontida.
class _StatsSection extends StatelessWidget {
  final StatsSummary? summary;
  final StatsByTypeResponse? byType;
  final bool isLoading;
  final String? error;
  final VoidCallback onRetry;

  const _StatsSection({
    required this.summary,
    required this.byType,
    required this.isLoading,
    required this.error,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Erro: mostra mensagem + botão "Tentar novamente" SÓ nos stats.
    // A lista de atividades abaixo continua funcionando (a S33 separa
    // os dois carregamentos de propósito).
    if (error != null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Estatísticas',
                style: theme.textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Erro ao carregar estatísticas: $error',
                style: TextStyle(color: theme.colorScheme.error),
              ),
              const SizedBox(height: 8),
              FilledButton.tonal(
                onPressed: onRetry,
                child: const Text('Tentar novamente'),
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Estatísticas',
          style: theme.textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        StatsCards(
          data: summary,
          isLoading: isLoading,
          isError: false, // erro já tratado acima (error != null)
        ),
        const SizedBox(height: 12),
        Text(
          'Por tipo de atividade',
          style: theme.textTheme.titleSmall,
        ),
        const SizedBox(height: 8),
        ByTypeList(
          data: byType,
          isLoading: isLoading,
          isError: false, // erro já tratado acima
        ),
      ],
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