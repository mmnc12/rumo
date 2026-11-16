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
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'pages/activity_detail_page.dart';
import 'pages/feed_page.dart';
import 'pages/login_page.dart';
import 'pages/profile_page.dart'; // [Sessão 32] rota /profile
import 'pages/search_page.dart'; // [Sessão 36] rota /search (era user_search_page.dart)
import 'pages/upload_page.dart'; // [Sessão 31] rota /upload
import 'pages/user_profile_page.dart'; // [Sessão 34] rota /user/:id
import 'services/auth_service.dart';

void main() {
  runApp(const RumoApp());
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
      initialLocation: '/feed',
      refreshListenable: _auth,
      redirect: (context, state) {
        if (_auth.loading) return null;
        final loggingIn = state.matchedLocation == '/login';
        if (!_auth.isLoggedIn) {
          return loggingIn ? null : '/login';
        }
        if (loggingIn) return '/feed';
        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (_, _) => LoginPage(auth: _auth),
        ),
        // [Sessão 31] Tela de upload de GPX/FIT.
        GoRoute(
          path: '/upload',
          builder: (_, _) => UploadPage(auth: _auth),
        ),
        GoRoute(
          path: '/activity/:id',
          builder: (_, state) => ActivityDetailPage(
            activityId: state.pathParameters['id']!,
            auth: _auth,
          ),
        ),
        // [Sessão 34] Perfil público de terceiro + follow.
        GoRoute(
          path: '/user/:id',
          builder: (_, state) => UserProfilePage(
            userId: state.pathParameters['id']!,
            auth: _auth,
          ),
        ),
        // [Sessão 36] Busca unificada (Usuários | Atividades).
        // Fora do shell, mesma decisão de /user/:id e /activity/:id.
        GoRoute(
          path: '/search',
          builder: (_, _) => SearchPage(auth: _auth),
        ),
        // [Sessão 32] Bottom nav: Feed / Perfil.
        StatefulShellRoute.indexedStack(
          builder: (context, state, navigationShell) {
            return _ScaffoldWithNavBar(navigationShell: navigationShell);
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
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.green,
      ),
      routerConfig: _router,
    );
  }
}

/// [Sessão 32] Casca do bottom nav. Cada página da branch mantém seu
/// próprio Scaffold/AppBar; este Scaffold só fornece o NavigationBar.
class _ScaffoldWithNavBar extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const _ScaffoldWithNavBar({required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (index) {
          navigationShell.goBranch(
            index,
            initialLocation: index == navigationShell.currentIndex,
          );
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dynamic_feed_outlined),
            selectedIcon: Icon(Icons.dynamic_feed),
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