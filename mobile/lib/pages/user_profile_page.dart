// [Sessão 34] Perfil público de terceiro + follow.
//
// Rota: /user/:id (fora do shell, sem bottom nav — igual /activity/:id).
//
// Diferenças em relação ao ProfilePage (self):
// - Cabeçalho vem de GET /users/{id} (UserPublic: id, username,
//   full_name, is_active). SEM email, SEM avatar_url.
// - Tem botão Follow/Unfollow (self não tem).
// - Stats e atividades podem dar 403 (backend: _ensure_can_view_stats
//   e /activities?user_id= exigem seguir). Quando 403, mostramos
//   "Siga pra ver..." em vez de erro genérico.
//
// Inferência de isFollowing: o backend NÃO tem GET /users/{id}/is-following
// (mesma limitação do web, que infere via /users/{meId}/following em
// useProfile.ts → useIsFollowing). Custa 1 request extra por perfil
// aberto. Se um dia o backend ganhar o endpoint, é só trocar a chamada
// de auth.api.isFollowing por um GET direto.
//
// Self: a rota /profile continua sendo do ProfilePage. O UserProfilePage
// é só pra terceiros. Se alguém abrir /user/{meId}, o botão Follow some
// (isSelf) e a página se comporta como leitura — decisão de UX: o
// perfil editável é o /profile, não /user/:meId.
//
// Fora de escopo (S35+):
// - onAuthorTap no ActivityCard do feed (link do autor).
// - Lista de seguidores/seguindo (o web tem abas; o mobile fica pra S35).
// - Editar perfil (requer PUT /users/me, não existe).
//
// [Sessão 37] +abas Seguidores/Seguindo (paridade com web ProfilePage.tsx):
// - GET /users/{id}/followers?limit&offset (listFollowers — novo no ApiClient).
// - GET /users/{id}/following?limit&offset (listFollowing — já existia).
// - Carrega em paralelo no initState (_loadLists), separado de _load/_loadStats.
// - Cada linha é um ListTile com avatar (inicial) + @username + full_name.
// - onTap → /user/:id (rota existe desde S34).
// - Retry por seção, sem afetar o resto da tela.
//
// [Sessão 38] +filtros de period/compare + 4 charts (weekly/monthly ×
// distance/activities) na seção de stats. Mesmo padrão do ProfilePage,
// com uma diferença: quando _statsForbidden (403 do _ensure_can_view_stats),
// os filtros ficam desabilitados e NÃO chamamos weekly/monthly (o backend
// devolveria 403 nos 4). O short-circuit é feito em _loadStats: dispara
// summary+byType primeiro, e só se byType voltar OK dispara weekly+monthly.
// Se voltar 403, marca _statsForbidden e para.
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../models/stats.dart';
import '../models/user.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../widgets/activity_card.dart';
import '../widgets/by_type_list.dart';
import '../widgets/stats_cards.dart';
// [Sessão 38] Filtros + charts do perfil de terceiro.
import '../widgets/stats_chart.dart';
import '../widgets/stats_filters.dart';

class UserProfilePage extends StatefulWidget {
  final String userId;
  final AuthService auth;
  const UserProfilePage({
    super.key,
    required this.userId,
    required this.auth,
  });

  @override
  State<UserProfilePage> createState() => _UserProfilePageState();
}

class _UserProfilePageState extends State<UserProfilePage> {
  static const int _pageSize = 20;

  // ===== Perfil + follow =====
  User? _user;
  bool? _isFollowing; // null até o primeiro load resolver
  bool _followLoading = false;
  bool _loading = true;
  String? _error;

  // ===== Atividades =====
  List<Activity> _activities = [];
  bool _activitiesForbidden = false;
  int _offset = 0;
  bool _hasMore = true;
  bool _loadingMore = false;

  // ===== Stats =====
  StatsSummary? _summary;
  StatsByTypeResponse? _byType;
  // [Sessão 38] Weekly + Monthly (para os charts).
  StatsWeeklyResponse? _weekly;
  StatsMonthlyResponse? _monthly;
  bool _statsLoading = true;
  String? _statsError;
  bool _statsForbidden = false;
  // [Sessão 38] Filtros de period/compare (default = S33: 90d/prev).
  String _statsPeriod = kStatsPeriod90d;
  String _statsCompare = kStatsComparePrev;

  // ===== [Sessão 37] Seguidores / Seguindo =====
  List<User>? _followers;
  List<User>? _following;
  bool _listsLoading = true;
  String? _listsError;
  int _listTab = 0; // 0 = Seguidores, 1 = Seguindo

  bool get _isSelf =>
      widget.auth.currentUserId != null &&
      widget.auth.currentUserId == widget.userId;

  @override
  void initState() {
    super.initState();
    _load();
    _loadStats();
    _loadLists();
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() {
      _loading = true;
      _error = null;
      _activitiesForbidden = false;
    });

    final meId = widget.auth.currentUserId;
    if (meId == null) {
      if (!mounted) return;
      setState(() {
        _error = 'Sessão sem id de usuário. Faça login novamente.';
        _loading = false;
      });
      return;
    }

    try {
      // getUser + isFollowing em paralelo com listActivities.
      // listActivities pode dar 403 (não segue) — tratamos separado.
      final userFuture = widget.auth.api.getUser(
        widget.userId,
        token: widget.auth.token,
      );
      final isFollowingFuture = widget.auth.api.isFollowing(
        meId: meId,
        targetUserId: widget.userId,
        token: widget.auth.token,
      );
      final activitiesFuture =
          widget.auth.api.listActivities(
        userId: widget.userId,
        limit: _pageSize,
        offset: 0,
        token: widget.auth.token,
      ).catchError((Object e) {
        // 403 aqui = não segue. Marcamos e devolvemos lista vazia
        // (o Future.wait não pode rejeitar inteiro por causa disso).
        if (e is ApiException && e.statusCode == 403) {
          return <Activity>[];
        }
        throw e;
      });

      final results = await Future.wait<Object?>([
        userFuture,
        isFollowingFuture,
        activitiesFuture,
      ]);
      if (!mounted) return;

      final user = results[0] as User;
      final isFollowing = results[1] as bool;
      final page = results[2] as List<Activity>;

      setState(() {
        _user = user;
        _isFollowing = isFollowing;
        _activities = page;
        _offset = page.length;
        _hasMore = page.length == _pageSize;
        _activitiesForbidden = page.isEmpty &&
            !isFollowing &&
            !_isSelf; // lista vazia + não segue + não é self = 403 engolido
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

  // [Sessão 38] Stats agregadas com short-circuit em 403.
  //
  // Diferente do ProfilePage, aqui o backend pode devolver 403 quando o
  // viewer não segue o alvo (_ensure_can_view_stats). Nesse caso, os 4
  // endpoints devolveriam 403 — não adianta tentar os 4. Estratégia:
  // 1. Dispara summary + byType em paralelo.
  // 2. Se byType voltar 403, marca _statsForbidden e PARA (não tenta
  //    weekly/monthly).
  // 3. Se byType voltar OK, dispara weekly + monthly em paralelo.
  // 4. Falha de um individual (não-403) → null, sem derrubar os outros.
  Future<void> _loadStats() async {
    if (!mounted) return;
    setState(() {
      _statsLoading = true;
      _statsError = null;
      _statsForbidden = false;
    });

    final period = _statsPeriod;
    final compare = _statsCompare;

    try {
      // Fase 1: summary + byType (paralelo, catchError individual).
      final summaryF = widget.auth.api
          .getStatsSummary(widget.userId, token: widget.auth.token)
          .then<Object?>((v) => v)
          .catchError((Object e) {
        if (e is ApiException && e.statusCode == 403) {
          // Sinaliza 403 via Future.error custom — capturado abaixo.
          throw _Stats403();
        }
        return null;
      });
      final byTypeF = widget.auth.api
          .getStatsByType(
            widget.userId,
            period: period,
            compare: compare,
            token: widget.auth.token,
          )
          .then<Object?>((v) => v)
          .catchError((Object e) {
        if (e is ApiException && e.statusCode == 403) {
          throw _Stats403();
        }
        return null;
      });

      final List<Object?> phase1;
      try {
        phase1 = await Future.wait<Object?>([summaryF, byTypeF]);
      } on _Stats403 {
        if (!mounted) return;
        setState(() {
          _statsForbidden = true;
          _statsLoading = false;
        });
        return;
      }

      if (!mounted) return;
      final summary = phase1[0] as StatsSummary?;
      final byType = phase1[1] as StatsByTypeResponse?;

      // Fase 2: weekly + monthly (só se phase1 não deu 403).
      final weeklyF = widget.auth.api
          .getStatsWeekly(widget.userId, weeks: 8, token: widget.auth.token)
          .then<Object?>((v) => v)
          .catchError((Object e) => null);
      final monthlyF = widget.auth.api
          .getStatsMonthly(widget.userId, months: 6, token: widget.auth.token)
          .then<Object?>((v) => v)
          .catchError((Object e) => null);

      final phase2 = await Future.wait<Object?>([weeklyF, monthlyF]);
      if (!mounted) return;
      final weekly = phase2[0] as StatsWeeklyResponse?;
      final monthly = phase2[1] as StatsMonthlyResponse?;

      // Falha agregada (só conta não-403).
      final failed = <String>[];
      if (summary == null) failed.add('resumo');
      if (byType == null) failed.add('por tipo');
      if (weekly == null) failed.add('semanal');
      if (monthly == null) failed.add('mensal');

      setState(() {
        _summary = summary;
        _byType = byType;
        _weekly = weekly;
        _monthly = monthly;
        _statsError = failed.isEmpty
            ? null
            : 'Falha ao carregar: ${failed.join(', ')}.';
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      if (e.statusCode == 403) {
        setState(() => _statsForbidden = true);
      } else {
        setState(() => _statsError = e.message);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _statsError = 'Erro: $e');
    } finally {
      if (mounted) setState(() => _statsLoading = false);
    }
  }

  /// [Sessão 37] Carrega seguidores + seguindo do alvo em paralelo.
  ///
  /// Separado de `_load()` e `_loadStats()` de propósito (falha aqui
  /// não derruba o resto da tela). Chamado no `initState` e no retry
  /// do widget `_SocialListsSection`.
  Future<void> _loadLists() async {
    if (!mounted) return;
    setState(() {
      _listsLoading = true;
      _listsError = null;
    });

    try {
      final results = await Future.wait([
        widget.auth.api.listFollowers(
          userId: widget.userId,
          limit: 100,
          offset: 0,
          token: widget.auth.token,
        ),
        widget.auth.api.listFollowing(
          userId: widget.userId,
          limit: 100,
          offset: 0,
          token: widget.auth.token,
        ),
      ]);
      if (!mounted) return;
      setState(() {
        _followers = results[0];
        _following = results[1];
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _listsError = e.message);
    } catch (e) {
      if (!mounted) return;
      setState(() => _listsError = 'Erro: $e');
    } finally {
      if (mounted) setState(() => _listsLoading = false);
    }
  }

  Future<void> _loadMore() async {
    if (_loadingMore || !_hasMore || _activitiesForbidden) return;
    setState(() => _loadingMore = true);
    try {
      final page = await widget.auth.api.listActivities(
        userId: widget.userId,
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

  Future<void> _toggleFollow() async {
    final current = _isFollowing;
    if (current == null || _followLoading || _isSelf) return;

    setState(() => _followLoading = true);
    try {
      if (current) {
        await widget.auth.api.unfollowUser(
          widget.userId,
          token: widget.auth.token,
        );
      } else {
        await widget.auth.api.followUser(
          widget.userId,
          token: widget.auth.token,
        );
      }
      if (!mounted) return;
      setState(() => _isFollowing = !current);

      // Follow mudou permissão → recarrega stats e lista.
      // Mantemos o _user (não muda com follow).
      _loadStats();
      // Recarrega só a lista, sem refazer getUser/isFollowing.
      await _reloadActivities();
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
      if (mounted) setState(() => _followLoading = false);
    }
  }

  Future<void> _reloadActivities() async {
    try {
      final page = await widget.auth.api.listActivities(
        userId: widget.userId,
        limit: _pageSize,
        offset: 0,
        token: widget.auth.token,
      );
      if (!mounted) return;
      setState(() {
        _activities = page;
        _offset = page.length;
        _hasMore = page.length == _pageSize;
        _activitiesForbidden = false;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      if (e.statusCode == 403) {
        setState(() {
          _activities = [];
          _offset = 0;
          _hasMore = false;
          _activitiesForbidden = true;
        });
      }
      // outros erros: mantém estado atual, sem barulho (o follow já
      // mostrou o erro dele; não empilha dois SnackBars).
    } catch (_) {
      // silencioso
    }
  }

  Future<void> _openDetail(Activity activity) async {
    await context.push('/activity/${activity.id}');
    if (!mounted) return;
    // Recarrega só esse item (mesmo padrão do ProfilePage S33).
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
      // silencioso
    }
  }

  void _replaceActivity(Activity updated) {
    setState(() {
      _activities = _activities
          .map((a) => a.id == updated.id ? updated : a)
          .toList();
    });
  }

  Future<void> _refreshAll() async {
    await Future.wait([_load(), _loadStats(), _loadLists()]);
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
                      if (_user != null)
                        _UserHeader(
                          user: _user!,
                          isSelf: _isSelf,
                          isFollowing: _isFollowing,
                          followLoading: _followLoading,
                          onToggleFollow: _toggleFollow,
                        ),
                      const SizedBox(height: 16),

                      // ===== Stats =====
                      _StatsSection(
                        summary: _summary,
                        byType: _byType,
                        weekly: _weekly,
                        monthly: _monthly,
                        isLoading: _statsLoading,
                        error: _statsError,
                        forbidden: _statsForbidden,
                        period: _statsPeriod,
                        compare: _statsCompare,
                        onFiltersChanged: (period, compare) {
                          setState(() {
                            _statsPeriod = period;
                            _statsCompare = compare;
                          });
                          _loadStats();
                        },
                        onRetry: _loadStats,
                      ),
                      const SizedBox(height: 16),

                      // ===== Atividades =====
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: Text(
                          'Atividades',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                      const SizedBox(height: 8),

                      if (_activitiesForbidden)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          child: Center(
                            child: Text(
                              'Siga @${_user?.username ?? "este usuário"} '
                              'pra ver as atividades.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color:
                                    Theme.of(context).colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ),
                        )
                      else if (_activities.isEmpty)
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 32),
                          child: Center(
                            child: Text('Nenhuma atividade registrada ainda.'),
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
                              // [Sessão 34] GET /activities não embute
                              // `user`; sem o override o card cairia em
                              // "Usuário"/"?".
                              authorUsernameOverride: _user?.username,
                            ),
                          ),
                        ),
                      if (_activities.isNotEmpty && !_activitiesForbidden) ...[
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

                      // ===== [Sessão 37] Seguidores / Seguindo =====
                      const SizedBox(height: 24),
                      _SocialListsSection(
                        followers: _followers,
                        following: _following,
                        isLoading: _listsLoading,
                        error: _listsError,
                        tab: _listTab,
                        onTabChanged: (t) => setState(() => _listTab = t),
                        onRetry: _loadLists,
                      ),
                    ],
                  ),
                ),
    );
  }
}

/// [Sessão 38] Marcador interno de 403 nos stats.
///
/// Usado só dentro do `_loadStats` para curto-circuitar a fase 1
/// (summary + byType) quando o backend devolve 403 (`_ensure_can_view_stats`).
/// Não vaza pra fora — é capturado pelo `try/on _Stats403`.
class _Stats403 implements Exception {
  const _Stats403();
}

// ===== [Sessão 37] Abas Seguidores/Seguindo =====
// Widget separado (mesmo padrão do _StatsSection) pra manter o build()
// do UserProfilePage legível. Paridade com o web ProfilePage.tsx → UserRow.
class _SocialListsSection extends StatelessWidget {
  final List<User>? followers;
  final List<User>? following;
  final bool isLoading;
  final String? error;
  final int tab;
  final ValueChanged<int> onTabChanged;
  final VoidCallback onRetry;

  const _SocialListsSection({
    required this.followers,
    required this.following,
    required this.isLoading,
    required this.error,
    required this.tab,
    required this.onTabChanged,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final list = tab == 0 ? followers : following;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Botões-aba
        Row(
          children: [
            Expanded(
              child: _TabButton(
                label: followers == null
                    ? 'Seguidores'
                    : 'Seguidores (${followers!.length})',
                active: tab == 0,
                onTap: () => onTabChanged(0),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _TabButton(
                label: following == null
                    ? 'Seguindo'
                    : 'Seguindo (${following!.length})',
                active: tab == 1,
                onTap: () => onTabChanged(1),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Conteúdo
        if (error != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Erro ao carregar a lista: $error',
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
          )
        else if (isLoading)
          const Card(
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Center(
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
          )
        else if (list == null || list.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
              child: Center(
                child: Text(
                  tab == 0
                      ? 'Ninguém segue esta pessoa ainda.'
                      : 'Esta pessoa ainda não segue ninguém.',
                  style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          )
        else
          Card(
            clipBehavior: Clip.antiAlias,
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: list.length,
              separatorBuilder: (_, _) => const Divider(height: 1),
              itemBuilder: (context, index) =>
                  _UserRow(user: list[index]),
            ),
          ),
      ],
    );
  }
}

class _TabButton extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _TabButton({
    required this.label,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: active
          ? theme.colorScheme.primary
          : theme.colorScheme.surfaceContainerHighest,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 10),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: active
                    ? theme.colorScheme.onPrimary
                    : theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Linha de usuário na lista (espelho do `UserRow` do web).
///
/// Toca → `/user/:id` (rota existe desde S34). O próprio usuário
/// aparece na lista se seguir/seguido — sem tratamento especial
/// (o web também não tem).
class _UserRow extends StatelessWidget {
  final User user;
  const _UserRow({required this.user});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListTile(
      leading: CircleAvatar(
        radius: 18,
        child: Text(
          user.initial,
          style: theme.textTheme.labelLarge,
        ),
      ),
      title: Text(
        '@${user.username}',
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: (user.fullName != null && user.fullName!.isNotEmpty)
          ? Text(user.fullName!)
          : null,
      trailing: const Icon(Icons.chevron_right, size: 18),
      onTap: () => context.push('/user/${user.id}'),
    );
  }
}

// ===== Header do perfil de terceiro =====
class _UserHeader extends StatelessWidget {
  final User user;
  final bool isSelf;
  final bool? isFollowing; // null até o load resolver
  final bool followLoading;
  final VoidCallback onToggleFollow;

  const _UserHeader({
    required this.user,
    required this.isSelf,
    required this.isFollowing,
    required this.followLoading,
    required this.onToggleFollow,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
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
                    user.initial,
                    style: theme.textTheme.titleLarge,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        user.username,
                        style: theme.textTheme.titleLarge,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (user.fullName != null && user.fullName!.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          user.fullName!,
                          style: theme.textTheme.bodyMedium,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            // Sem email (UserPublic não tem) e sem "Sair" (não é self).
            const SizedBox(height: 12),
            if (isSelf)
              Text(
                'Este é você. Use a aba Perfil pra editar.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              )
            else if (isFollowing == null)
              const SizedBox(
                height: 36,
                child: Center(
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
              )
            else
              Align(
                alignment: Alignment.centerRight,
                child: isFollowing!
                    ? OutlinedButton.icon(
                        onPressed: followLoading ? null : onToggleFollow,
                        icon: followLoading
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.person_remove, size: 18),
                        label: const Text('Deixar de seguir'),
                      )
                    : FilledButton.icon(
                        onPressed: followLoading ? null : onToggleFollow,
                        icon: followLoading
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.person_add, size: 18),
                        label: const Text('Seguir'),
                      ),
              ),
          ],
        ),
      ),
    );
  }
}

// ===== Seção de stats (self ou terceiro) =====
// Reusa StatsCards e ByTypeList do S33 (mesmos shapes de dados).
// `forbidden` é o 403 do _ensure_can_view_stats: mostra mensagem neutra
// sem botão de retry (só o Follow muda a permissão, não o retry).
//
// [Sessão 38] +StatsFilters no topo (disabled quando isLoading||forbidden)
// +4 StatsChart abaixo do ByTypeList (só quando !forbidden).
class _StatsSection extends StatelessWidget {
  final StatsSummary? summary;
  final StatsByTypeResponse? byType;
  final StatsWeeklyResponse? weekly;
  final StatsMonthlyResponse? monthly;
  final bool isLoading;
  final String? error;
  final bool forbidden;
  final String period;
  final String compare;
  final void Function(String period, String compare) onFiltersChanged;
  final VoidCallback onRetry;

  const _StatsSection({
    required this.summary,
    required this.byType,
    required this.weekly,
    required this.monthly,
    required this.isLoading,
    required this.error,
    required this.forbidden,
    required this.period,
    required this.compare,
    required this.onFiltersChanged,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (forbidden) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Estatísticas', style: theme.textTheme.titleMedium),
              const SizedBox(height: 8),
              StatsFilters(
                period: period,
                compare: compare,
                disabled: true,
                onChanged: onFiltersChanged,
              ),
              const SizedBox(height: 8),
              Text(
                'Siga pra ver as estatísticas.',
                style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Estatísticas', style: theme.textTheme.titleMedium),
        const SizedBox(height: 8),
        StatsFilters(
          period: period,
          compare: compare,
          disabled: isLoading,
          onChanged: onFiltersChanged,
        ),
        const SizedBox(height: 8),
        if (error != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
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
          )
        else ...[
          StatsCards(
            data: summary,
            isLoading: isLoading,
            isError: false,
          ),
          const SizedBox(height: 12),
          Text('Por tipo de atividade', style: theme.textTheme.titleSmall),
          const SizedBox(height: 8),
          ByTypeList(
            data: byType,
            isLoading: isLoading,
            isError: false,
          ),
          const SizedBox(height: 12),
          // [Sessão 38] 4 charts — paridade com o ProfilePage.
          StatsChart(
            period: ChartPeriod.weekly,
            metric: ChartMetric.distance,
            items: weekly?.items,
            isLoading: isLoading,
            isError: false,
          ),
          const SizedBox(height: 8),
          StatsChart(
            period: ChartPeriod.weekly,
            metric: ChartMetric.activities,
            items: weekly?.items,
            isLoading: isLoading,
            isError: false,
          ),
          const SizedBox(height: 8),
          StatsChart(
            period: ChartPeriod.monthly,
            metric: ChartMetric.distance,
            items: monthly?.items,
            isLoading: isLoading,
            isError: false,
          ),
          const SizedBox(height: 8),
          StatsChart(
            period: ChartPeriod.monthly,
            metric: ChartMetric.activities,
            items: monthly?.items,
            isLoading: isLoading,
            isError: false,
          ),
        ],
      ],
    );
  }
}