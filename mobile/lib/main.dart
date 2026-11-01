import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'pages/activity_detail_page.dart';
import 'pages/feed_page.dart';
import 'pages/login_page.dart';
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
          builder: (_, __) => LoginPage(auth: _auth),
        ),
        GoRoute(
          path: '/feed',
          builder: (_, __) => FeedPage(auth: _auth),
        ),
        GoRoute(
          path: '/activity/:id',
          builder: (_, state) => ActivityDetailPage(
            activityId: state.pathParameters['id']!,
            auth: _auth,
          ),
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