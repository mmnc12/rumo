// [Sessão 34] Model do perfil público de terceiro.
//
// Espelha o UserPublic do backend (app/schemas/user.py): só id, username,
// full_name, is_active. NÃO tem email (UserResponse/auth/me tem; UserPublic
// não expõe) e NÃO tem avatar_url (o backend não devolve — o UserPublic
// local de activity.dart carrega avatarUrl como dívida cosmética, mas
// nunca vem preenchido; aqui não repetimos o erro).
//
// Por que arquivo separado e não reaproveitar o UserPublic de activity.dart:
// - UserPublic (activity.dart) é acoplado ao Activity.fromJson e carrega
//   avatarUrl (não existe no backend). É o modelo "de feed".
// - User (este arquivo) é o modelo "de perfil público" — mesmos 4 campos
//   reais do backend, sem campo morto.
// - O UserProfilePage (S34) usa este; o ActivityCard continua usando
//   UserPublic via activity.user (opcional, tolerante a null).
//
// Schema real (GET /users/{id}):
// { "id": "uuid", "username": "string", "full_name": "string|null",
//   "is_active": true }
class User {
  final String id;
  final String username;
  final String? fullName;
  final bool isActive;

  User({
    required this.id,
    required this.username,
    required this.fullName,
    required this.isActive,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        username: json['username'] as String,
        fullName: json['full_name'] as String?,
        isActive: json['is_active'] as bool,
      );

  /// Inicial do username pra CircleAvatar. "?" quando username vazio
  /// (não deveria acontecer — o backend valida —, mas evita crash).
  String get initial =>
      username.isNotEmpty ? username.substring(0, 1).toUpperCase() : '?';
}