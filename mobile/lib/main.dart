// [Sessão 32] Bottom nav (Feed / Perfil) via StatefulShellRoute.indexedStack.
//
// - /feed e /profile são branches do shell; cada uma preserva estado
//   (scroll do feed mantido ao trocar de aba, etc.).
// - /login, /upload, /activity/:id e /user/:id ficam FORA do shell
//   (são fluxos, não áreas) — não têm bottom nav.
// - O FAB de upload continua no FeedPage (não no shell): upload é ação
//   do feed, não uma área.
//
// [Sessão 34] +rota /user/:id (perfil público de terceiro + follow).
// Fora do shell — é fluxo.
//
// [Sessão 35] +rota /search (busca de usuários). Fora do shell — fluxo.
//
// [Sessão 36] SearchPage com 2 abas (Usuários | Atividades) substitui a
// UserSearchPage. Mesma rota (/search), mesmo fora do shell, mesma
// decisão de UX. A rota continua sendo "abre, busca, toca no resultado,
// fecha" — a busca de atividades é só uma segunda aba dentro do mesmo
// fluxo. Apaga o user_search_page.dart.
//
// [Sessão 39] +rota /edit-profile (edição do próprio perfil). Fora do
// shell — é fluxo. Recebe o UserMe atual via `extra` (state.extra do
// go_router); se `extra` não for UserMe (deep-link sem extra), redireciona
// pro /profile. O pop retorna o UserMe pós-update pro caller (ProfilePage
// faz setState). Consome PUT /users/me (commit 9d52470).
//
// [Sessão 39 — fix] builder usa (context, state), não (_, state) — o
// GoRouterState 18.x NÃO tem `.context` (removido). O context do builder
// é o que serve pro `context.go('/profile')` no fallback do deep-link.
//
// [Sessão 49 — item 10.2] +rota /register (tela de cadastro). Fora do
// shell — é fluxo. O redirect global foi ajustado: /register é uma
// "auth page" (como /login) e passa sem login. Sem esse ajuste, o
// redirect mandaria /register para /login em loop.
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'models/user_me.dart'; // [Sessão 39] extra do /edit-profile
import 'pages/activity_detail_page.dart';
import 'pages/edit_profile_page.dart'; // [Sessão 39] rota /edit-profile
import 'pages/feed_page.dart';
import 'pages/login_page.dart';
import 'pages/profile_page.dart'; // [Sessão 32] rota /profile
import 'pages/register_page.dart'; // [Sessão 49] rota /register
import 'pages/search_page.dart'; // [Sessão 36] rota /search (era user_search_page.dart)
import 'pages/upload_page.dart'; // [Sessão 31] rota /upload
import 'pages/user_profile_page.dart'; // [Sessão 34] rota /user/:id
import 'services/auth_service.dart';

void main() {
  runApp(RumoApp());
}

class RumoApp extends StatefulWidget {
  const RumoApp({super.key});

  @override
  State<RumoApp> createState() => _RumoAppState();
}

class _RumoAppState extends State<RumoApp> {
  final AuthService _auth = AuthService();
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _auth.bootstrap();

    _router = GoRouter(
      initialLocation: '/login',
      // [Sessão 32] Redirect global: sem login → /login. Com login em
      // /login → /feed. As rotas do shell (/feed, /profile) exigem auth.
      //
      // [Sessão 49 — item 10.2] /register também é "auth page": passa
      // sem login (é onde o usuário cria a conta). Sem isso, o redirect
      // mandaria /register → /login em loop.
      redirect: (context, state) {
        final loggedIn = _auth.isLoggedIn;
        final goingToAuthPage = state.matchedLocation == '/login' ||
            state.matchedLocation == '/register';
        if (!loggedIn && !goingToAuthPage) return '/login';
        if (loggedIn && goingToAuthPage) return '/feed';
        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (_, _) => LoginPage(auth: _auth),
        ),
        // [Sessão 49 — item 10.2] Tela de cadastro. Pública (sem auth).
        // O AuthService.register() faz login automático após o 201, e o
        // redirect leva para /feed (loggedIn == true, /register é auth
        // page).
        GoRoute(
          path: '/register',
          builder: (_, _) => RegisterPage(auth: _auth),
        ),
        GoRoute(
          path: '/upload',
          builder: (_, _) => UploadPage(auth: _auth),
        ),
        GoRoute(
          path: '/activity/:id',
          builder: (_, state) => ActivityDetailPage(
            auth: _auth,
            activityId: state.pathParameters['id']!,
          ),
        ),
        GoRoute(
          path: '/user/:id',
          builder: (_, state) => UserProfilePage(
            auth: _auth,
            userId: state.pathParameters['id']!,
          ),
        ),
        GoRoute(
          path: '/search',
          builder: (_, _) => SearchPage(auth: _auth),
        ),
        // [Sessão 39] Edição do próprio perfil. `extra` carrega o UserMe
        // atual (o ProfilePage passa via context.push<UserMe>(...)).
        // Sem extra (deep-link), redireciona pro /profile — evita crash
        // com `null as UserMe`.
        //
        // [Sessão 39 — fix] builder usa `(context, state)` — o GoRouterState
        // 18.x NÃO tem `.context` (a 18.x removeu). O `context` do builder
        // é o que serve pro `context.go('/profile')` no fallback.
        GoRoute(
          path: '/edit-profile',
          builder: (context, state) {
            final extra = state.extra;
            if (extra is! UserMe) {
              // Fallback defensivo: deep-link sem extra → volta pro perfil.
              // WidgetsBinding.addPostFrameCallback evita "setState during build"
              // do go_router (não dá pra chamar context.go dentro do builder).
              WidgetsBinding.instance.addPostFrameCallback((_) {
                if (context.mounted) context.go('/profile');
              });
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            }
            return EditProfilePage(auth: _auth, current: extra);
          },
        ),
        StatefulShellRoute.indexedStack(
          builder: (context, state, navigationShell) {
            return _ShellScaffold(auth: _auth, navigationShell: navigationShell);
          },
          branches: [
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/feed',
                  builder: (_, _) => FeedPage(auth: _auth),
                ),
              ],
            ),
            StatefulShellBranch(
              routes: [
                GoRoute(
                  path: '/profile',
                  builder: (_, _) => ProfilePage(auth: _auth),
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Rumo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFF97316)),
        useMaterial3: true,
      ),
      routerConfig: _router,
    );
  }
}

/// [Sessão 32] Scaffold do shell com bottom nav (Feed / Perfil).
class _ShellScaffold extends StatelessWidget {
  final AuthService auth;
  final StatefulNavigationShell navigationShell;

  const _ShellScaffold({required this.auth, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (i) => navigationShell.goBranch(
          i,
          initialLocation: i == navigationShell.currentIndex,
        ),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Feed',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}