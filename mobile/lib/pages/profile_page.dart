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
//
// [Sessão 37] +seção "Exportar tudo" (self-only, paridade com web S23+S29):
// - GET /activities/export?format=&from=&to= (backend S22) → ZIP.
// - Download via share_plus (utils/download.dart → saveAndShare).
// - Feedback inline âmbar (ZIP vazio) / verde (N atividades) / vermelho (erro).
// - Validação client-side de from > to antes de chamar o backend.
import 'dart:async'; // [Sessão 37] Timer do feedback transitório

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/activity.dart';
import '../models/stats.dart';
import '../models/user_me.dart';
import '../services/api.dart';
import '../services/auth_service.dart';
import '../utils/download.dart'; // [Sessão 37] saveAndShare
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

  // ===== Export em lote (S37) =====
  _BulkExportFormat _exportFormat = _BulkExportFormat.csv;
  DateTime? _exportFrom;
  DateTime? _exportTo;
  bool _exporting = false;
  String? _exportError;
  _ExportInfo? _exportInfo;
  Timer? _exportInfoTimer;

  @override
  void initState() {
    super.initState();
    // Carrega em paralelo — cada _load* tem seu próprio try/catch,
    // então uma falha não impede a outra de completar.
    _load();
    _loadStats();
  }

  @override
  void dispose() {
    _exportInfoTimer?.cancel();
    super.dispose();
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

  // ===== [Sessão 37] Export em lote =====

  /// Abre o date picker e atualiza `_exportFrom` ou `_exportTo`.
  Future<void> _pickDate({required bool isFrom}) async {
    final initial = isFrom
        ? (_exportFrom ?? DateTime.now())
        : (_exportTo ?? DateTime.now());
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2000),
      lastDate: DateTime.now().add(const Duration(days: 1)),
      helpText: isFrom ? 'Data inicial' : 'Data final',
    );
    if (picked == null || !mounted) return;
    setState(() {
      if (isFrom) {
        _exportFrom = picked;
      } else {
        _exportTo = picked;
      }
      _exportError = null;
    });
  }

  /// Formata `DateTime` no padrão do backend: `YYYY-MM-DD` (UTC).
  ///
  /// O `showDatePicker` devolve meia-noite local. Como o backend trata
  /// as datas como UTC inclusivo, e o fuso do usuário é Brasil (UTC-3),
  /// a conversão direta `toIso8601String().substring(0,10)` mantém o
  /// dia escolhido. Não convertemos pra UTC porque o usuário está
  /// escolhendo "o dia 15", não "o instante 00:00 UTC do dia 15".
  String _formatDate(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-'
      '${d.month.toString().padLeft(2, '0')}-'
      '${d.day.toString().padLeft(2, '0')}';

  /// Limpa o feedback transitório (timer de ~4s, paridade web S24).
  void _scheduleClearExportInfo() {
    _exportInfoTimer?.cancel();
    _exportInfoTimer = Timer(const Duration(seconds: 4), () {
      if (!mounted) return;
      setState(() => _exportInfo = null);
    });
  }

  /// [Sessão 37] "Exportar tudo" — paridade com web S23+S29.
  ///
  /// Fluxo:
  /// 1. Valida client-side `from > to` (evita ida perdida ao backend — 422).
  /// 2. `downloadActivityExportBulk` → devolve `{bytes, filename, contentType, entryCount}`.
  /// 3. `saveAndShare` (web: download no browser; nativo: share sheet).
  /// 4. Feedback:
  ///    - `entryCount == 0` → "Nenhuma atividade no período — ZIP vazio." (âmbar).
  ///    - `entryCount == 1` → "Download iniciado (1 atividade)." (verde).
  ///    - `entryCount >= 2` → "Download iniciado (N atividades)." (verde).
  ///    - `entryCount == -1` → "Download iniciado." (verde, fail-open).
  /// 5. Erro → mensagem em vermelho (`_exportError`).
  Future<void> _exportAll() async {
    // Validação client-side (o backend devolve 422 se from > to).
    if (_exportFrom != null &&
        _exportTo != null &&
        _exportFrom!.isAfter(_exportTo!)) {
      setState(() {
        _exportError = 'A data inicial não pode ser maior que a final.';
        _exportInfo = null;
      });
      return;
    }

    setState(() {
      _exportError = null;
      _exportInfo = null;
      _exporting = true;
    });

    try {
      final result = await widget.auth.api.downloadActivityExportBulk(
        format: _exportFormat.name,
        from: _exportFrom == null ? null : _formatDate(_exportFrom!),
        to: _exportTo == null ? null : _formatDate(_exportTo!),
        token: widget.auth.token,
      );

      await saveAndShare(
        bytes: result.bytes,
        filename: result.filename,
        contentType: result.contentType,
        shareText: 'Exportação em lote — Rumo',
      );

      if (!mounted) return;
      // Decide o feedback conforme entryCount (EOCD do client).
      final _ExportInfo info;
      if (result.entryCount == 0) {
        info = const _ExportInfo(
          text: 'Nenhuma atividade no período — ZIP vazio.',
          kind: _ExportInfoKind.empty,
        );
      } else if (result.entryCount == 1) {
        info = const _ExportInfo(
          text: 'Download iniciado (1 atividade).',
          kind: _ExportInfoKind.success,
        );
      } else if (result.entryCount >= 2) {
        info = _ExportInfo(
          text: 'Download iniciado (${result.entryCount} atividades).',
          kind: _ExportInfoKind.success,
        );
      } else {
        // entryCount == -1 (EOCD falhou, fail-open).
        info = const _ExportInfo(
          text: 'Download iniciado.',
          kind: _ExportInfoKind.success,
        );
      }
      setState(() => _exportInfo = info);
      _scheduleClearExportInfo();
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _exportError = e.message);
    } catch (e) {
      if (!mounted) return;
      setState(() => _exportError = 'Falha ao exportar: $e');
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
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

                      // ===== [Sessão 37] Export em lote =====
                      // Só no perfil self (a tela ProfilePage é sempre self;
                      // o perfil de terceiro é o UserProfilePage, arquivo 6).
                      _ExportSection(
                        format: _exportFormat,
                        from: _exportFrom,
                        to: _exportTo,
                        exporting: _exporting,
                        error: _exportError,
                        info: _exportInfo,
                        onFormatChanged: (f) {
                          setState(() {
                            _exportFormat = f;
                            _exportError = null;
                          });
                        },
                        onPickFrom: () => _pickDate(isFrom: true),
                        onPickTo: () => _pickDate(isFrom: false),
                        onClearFrom: () => setState(() {
                          _exportFrom = null;
                          _exportError = null;
                        }),
                        onClearTo: () => setState(() {
                          _exportTo = null;
                          _exportError = null;
                        }),
                        onExport: _exportAll,
                      ),
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

// ===== [Sessão 37] Seção "Exportar tudo" =====
// Paridade com a seção homônima do web (ProfilePage.tsx, S23+S29).
// Widget separado pra manter o build() do ProfilePage legível.
enum _BulkExportFormat { csv, gpx }

enum _ExportInfoKind { success, empty }

class _ExportInfo {
  final String text;
  final _ExportInfoKind kind;
  const _ExportInfo({required this.text, required this.kind});
}

class _ExportSection extends StatelessWidget {
  final _BulkExportFormat format;
  final DateTime? from;
  final DateTime? to;
  final bool exporting;
  final String? error;
  final _ExportInfo? info;
  final ValueChanged<_BulkExportFormat> onFormatChanged;
  final VoidCallback onPickFrom;
  final VoidCallback onPickTo;
  final VoidCallback onClearFrom;
  final VoidCallback onClearTo;
  final VoidCallback onExport;

  const _ExportSection({
    required this.format,
    required this.from,
    required this.to,
    required this.exporting,
    required this.error,
    required this.info,
    required this.onFormatChanged,
    required this.onPickFrom,
    required this.onPickTo,
    required this.onClearFrom,
    required this.onClearTo,
    required this.onExport,
  });

  String _fmt(DateTime? d) {
    if (d == null) return 'Sem limite';
    return '${d.year.toString().padLeft(4, '0')}-'
        '${d.month.toString().padLeft(2, '0')}-'
        '${d.day.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Exportar tudo', style: theme.textTheme.titleMedium),
            const SizedBox(height: 4),
            Text(
              'Baixa todas as suas atividades do período como um ZIP, '
              'com um arquivo por atividade. Se nenhuma atividade casar '
              'com o período, o ZIP virá vazio.',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            // Formato
            DropdownButtonFormField<_BulkExportFormat>(
              initialValue: format,
              decoration: const InputDecoration(
                labelText: 'Formato',
                border: OutlineInputBorder(),
                isDense: true,
              ),
              items: const [
                DropdownMenuItem(
                  value: _BulkExportFormat.csv,
                  child: Text('CSV'),
                ),
                DropdownMenuItem(
                  value: _BulkExportFormat.gpx,
                  child: Text('GPX (só com rota)'),
                ),
              ],
              onChanged: exporting
                  ? null
                  : (v) {
                      if (v != null) onFormatChanged(v);
                    },
            ),
            const SizedBox(height: 12),
            // Datas
            Row(
              children: [
                Expanded(
                  child: _DateField(
                    label: 'De (opcional)',
                    value: _fmt(from),
                    isEmpty: from == null,
                    onPick: exporting ? null : onPickFrom,
                    onClear: from == null ? null : onClearFrom,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _DateField(
                    label: 'Até (opcional)',
                    value: _fmt(to),
                    isEmpty: to == null,
                    onPick: exporting ? null : onPickTo,
                    onClear: to == null ? null : onClearTo,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Botão
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: exporting ? null : onExport,
                icon: exporting
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.archive_outlined),
                label: Text(exporting ? 'Preparando…' : 'Exportar tudo'),
              ),
            ),
            // Feedback
            if (error != null) ...[
              const SizedBox(height: 8),
              Text(
                error!,
                style: TextStyle(color: theme.colorScheme.error),
              ),
            ],
            if (info != null && error == null) ...[
              const SizedBox(height: 8),
              Text(
                info!.text,
                style: TextStyle(
                  color: info!.kind == _ExportInfoKind.empty
                      ? Colors.amber.shade800
                      : Colors.green.shade700,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Campo de data read-only que abre `showDatePicker` ao tocar.
///
/// Tem um botão "X" para limpar quando há valor (paridade com o web,
/// onde apagar o `<input type="date">` remove o filtro).
class _DateField extends StatelessWidget {
  final String label;
  final String value;
  final bool isEmpty;
  final VoidCallback? onPick;
  final VoidCallback? onClear;

  const _DateField({
    required this.label,
    required this.value,
    required this.isEmpty,
    required this.onPick,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onPick,
      borderRadius: BorderRadius.circular(4),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
          isDense: true,
          suffixIcon: isEmpty
              ? const Icon(Icons.calendar_today, size: 18)
              : IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: onClear,
                  tooltip: 'Limpar',
                ),
        ),
        child: Text(
          value,
          style: TextStyle(
            color: isEmpty ? Colors.grey : null,
          ),
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