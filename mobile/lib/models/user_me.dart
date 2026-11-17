// [Sessão 32] Resposta de GET /auth/me (UserResponse do backend).
//
// Schema do backend (UserResponse): { id, email, username, full_name,
// weight_kg, height_cm, birth_date, is_active, created_at }.
//
// [Sessão 39] O editor de perfil (EditProfilePage) passa a consumir
// weight_kg e height_cm. birth_date entra no model por completude do
// schema (o backend devolve), mas o editor da S39 NÃO edita data de
// nascimento — fica como String? (YYYY-MM-DD cru do backend) pra evitar
// DateTime.parse desnecessário. Se a S40 editar birth_date, aí sim vira
// DateTime? e ganha parse.
//
// fromJson é DEFENSIVO nos numéricos: o backend devolve weight_kg/height_cm
// como float (ex.: 80.0), mas o JSON pode trazer int quando o valor é
// inteiro (ex.: 80). `(json[...] as num?)?.toDouble()` cobre os dois casos
// e evita cast exception.
class UserMe {
  final String id;
  final String email;
  final String username;
  final String? fullName;
  final double? weightKg;
  final double? heightCm;
  final String? birthDate;
  final bool isActive;

  UserMe({
    required this.id,
    required this.email,
    required this.username,
    required this.fullName,
    required this.weightKg,
    required this.heightCm,
    required this.birthDate,
    required this.isActive,
  });

  factory UserMe.fromJson(Map<String, dynamic> json) => UserMe(
        id: json['id'] as String,
        email: json['email'] as String,
        username: json['username'] as String,
        fullName: json['full_name'] as String?,
        weightKg: (json['weight_kg'] as num?)?.toDouble(),
        heightCm: (json['height_cm'] as num?)?.toDouble(),
        birthDate: json['birth_date'] as String?,
        isActive: json['is_active'] as bool,
      );
}