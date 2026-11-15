// [Sessão 32] Resposta de GET /auth/me (UserResponse do backend).
//
// Schema do backend (UserResponse): { id, email, username, full_name,
// weight_kg, height_cm, birth_date, is_active, created_at }.
//
// O perfil só consome { id, email, username, full_name, is_active }.
// Os campos de peso/altura/nascimento ficam de fora até existir editor
// de perfil — incluir agora seria modelar algo sem uso, e o `fromJson`
// lançaria se um dia o backend devolvesse tipos diferentes (ex.: weight
// como number, não int). YAGNI.
class UserMe {
  final String id;
  final String email;
  final String username;
  final String? fullName;
  final bool isActive;

  UserMe({
    required this.id,
    required this.email,
    required this.username,
    required this.fullName,
    required this.isActive,
  });

  factory UserMe.fromJson(Map<String, dynamic> json) => UserMe(
        id: json['id'] as String,
        email: json['email'] as String,
        username: json['username'] as String,
        fullName: json['full_name'] as String?,
        isActive: json['is_active'] as bool,
      );
}