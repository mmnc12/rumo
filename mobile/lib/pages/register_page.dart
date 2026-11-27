// lib/pages/register_page.dart
//
// [Sessão 49 — item 10.2] Tela de Cadastro.
//
// Fluxo:
// - Form: username, e-mail, nome completo (opcional), senha, confirmação
//   de senha + campos opcionais (peso, altura, data de nascimento)
//   colapsados por padrão (ExpansionTile) — o MVP só exige o essencial.
// - Validação local espelha o backend (`UserCreate` em app/schemas/user.py):
//   * email: formato (o backend usa EmailStr)
//   * username: min 3, max 50, pattern ^[a-zA-Z0-9_]+$
//   * password: min 8, max 128
//   * full_name: opcional, max 120
//   * weight_kg: opcional, 0 < x < 500
//   * height_cm: opcional, 0 < x < 300
//   * birth_date: opcional (YYYY-MM-DD, calendário)
// - Ao submeter: `widget.auth.register(...)`. Em sucesso, o AuthService
//   já faz login automático e notifica; o redirect do main.dart leva
//   para /feed.
// - Erros:
//   * 409 → MOSTRAR `e.message` DIRETO (S48d): "Email já cadastrado" ou
//     "Username já cadastrado". NÃO usar friendlyErrorMessage no 409
//     (o tradutor mapeia 409 cego → "Este e-mail já está cadastrado.").
//   * outros → friendlyErrorMessage(e).
//
// S47b: AuthService via construtor (`widget.auth`), não singleton.
// S48b: `catch (_)` silencioso NÃO existe aqui — todo catch exibe erro.

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/api.dart';
import '../services/auth_service.dart';
import '../utils/error_message.dart';

class RegisterPage extends StatefulWidget {
  final AuthService auth;

  const RegisterPage({super.key, required this.auth});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();

  final _emailCtrl = TextEditingController();
  final _usernameCtrl = TextEditingController();
  final _fullNameCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _passwordConfirmCtrl = TextEditingController();

  // Campos opcionais (ExpansionTile). Controladores separados para
  // conseguirmos distinguir "não preencheu" (null) de "preencheu".
  final _weightCtrl = TextEditingController();
  final _heightCtrl = TextEditingController();
  final _birthDateCtrl = TextEditingController();
  DateTime? _birthDate;

  bool _loading = false;
  bool _obscurePassword = true;
  bool _obscureConfirm = true;
  String? _error;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _usernameCtrl.dispose();
    _fullNameCtrl.dispose();
    _passwordCtrl.dispose();
    _passwordConfirmCtrl.dispose();
    _weightCtrl.dispose();
    _heightCtrl.dispose();
    _birthDateCtrl.dispose();
    super.dispose();
  }

  // ---------- validação local (espelha UserCreate) ----------

  String? _validateEmail(String? v) {
    final t = v?.trim() ?? '';
    if (t.isEmpty) return 'Informe o e-mail';
    // EmailStr do backend rejeita formatos óbvios; no client, regex simples.
    final re = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!re.hasMatch(t)) return 'E-mail inválido';
    return null;
  }

  String? _validateUsername(String? v) {
    final t = v?.trim() ?? '';
    if (t.isEmpty) return 'Informe o username';
    if (t.length < 3) return 'Mínimo 3 caracteres';
    if (t.length > 50) return 'Máximo 50 caracteres';
    final re = RegExp(r'^[a-zA-Z0-9_]+$');
    if (!re.hasMatch(t)) {
      return 'Use apenas letras, números e _';
    }
    return null;
  }

  String? _validateFullName(String? v) {
    final t = v?.trim() ?? '';
    if (t.isEmpty) return null; // opcional
    if (t.length > 120) return 'Máximo 120 caracteres';
    return null;
  }

  String? _validatePassword(String? v) {
    final t = v ?? '';
    if (t.isEmpty) return 'Informe a senha';
    if (t.length < 8) return 'Mínimo 8 caracteres';
    if (t.length > 128) return 'Máximo 128 caracteres';
    return null;
  }

  String? _validatePasswordConfirm(String? v) {
    final t = v ?? '';
    if (t.isEmpty) return 'Confirme a senha';
    if (t != _passwordCtrl.text) return 'As senhas não coincidem';
    return null;
  }

  String? _validateWeight(String? v) {
    final t = v?.trim() ?? '';
    if (t.isEmpty) return null; // opcional
    final parsed = double.tryParse(t.replaceAll(',', '.'));
    if (parsed == null) return 'Valor inválido';
    if (parsed <= 0 || parsed >= 500) return 'Entre 0 e 500 kg';
    return null;
  }

  String? _validateHeight(String? v) {
    final t = v?.trim() ?? '';
    if (t.isEmpty) return null; // opcional
    final parsed = double.tryParse(t.replaceAll(',', '.'));
    if (parsed == null) return 'Valor inválido';
    if (parsed <= 0 || parsed >= 300) return 'Entre 0 e 300 cm';
    return null;
  }

  // ---------- submit ----------

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final double? weight = _weightCtrl.text.trim().isEmpty
          ? null
          : double.tryParse(_weightCtrl.text.trim().replaceAll(',', '.'));
      final double? height = _heightCtrl.text.trim().isEmpty
          ? null
          : double.tryParse(_heightCtrl.text.trim().replaceAll(',', '.'));

      String? birthDateIso;
      if (_birthDate != null) {
        final y = _birthDate!.year.toString().padLeft(4, '0');
        final m = _birthDate!.month.toString().padLeft(2, '0');
        final d = _birthDate!.day.toString().padLeft(2, '0');
        birthDateIso = '$y-$m-$d';
      }

      await widget.auth.register(
        email: _emailCtrl.text.trim(),
        username: _usernameCtrl.text.trim(),
        password: _passwordCtrl.text,
        fullName: _fullNameCtrl.text.trim().isEmpty
            ? null
            : _fullNameCtrl.text.trim(),
        weightKg: weight,
        heightCm: height,
        birthDate: birthDateIso,
      );

      // Sucesso: o AuthService já fez login automático. O redirect do
      // main.dart leva pra /feed (isLoggedIn == true e /register é auth
      // page). Usamos context.go direto pra garantir ida imediata.
      if (mounted) context.go('/feed');
    } on ApiException catch (e) {
      // S48d: 409 tem `detail` específico (email OU username) — NÃO passar
      // pelo tradutor (que mapeia 409 cego → "Este e-mail já está cadastrado.").
      if (e.statusCode == 409) {
        setState(() => _error = e.message);
      } else {
        setState(() => _error = friendlyErrorMessage(e));
      }
    } catch (e) {
      setState(() => _error = friendlyErrorMessage(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _pickBirthDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _birthDate ?? DateTime(now.year - 25),
      firstDate: DateTime(1900),
      lastDate: now,
      helpText: 'Data de nascimento',
      cancelText: 'Cancelar',
      confirmText: 'OK',
    );
    if (picked != null) {
      setState(() {
        _birthDate = picked;
        final y = picked.year.toString().padLeft(4, '0');
        final m = picked.month.toString().padLeft(2, '0');
        final d = picked.day.toString().padLeft(2, '0');
        _birthDateCtrl.text = '$d/$m/$y';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Criar conta')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 400),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Icon(
                      Icons.directions_run,
                      size: 48,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Junte-se ao Rumo',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                    const SizedBox(height: 24),

                    // ---------- obrigatórios ----------
                    TextFormField(
                      controller: _emailCtrl,
                      keyboardType: TextInputType.emailAddress,
                      autocorrect: false,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'E-mail',
                        prefixIcon: Icon(Icons.mail_outline),
                        border: OutlineInputBorder(),
                      ),
                      validator: _validateEmail,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _usernameCtrl,
                      autocorrect: false,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Username',
                        hintText: 'ex.: joao_corredor',
                        helperText: 'Letras, números e _ (mín. 3)',
                        prefixIcon: Icon(Icons.alternate_email),
                        border: OutlineInputBorder(),
                      ),
                      validator: _validateUsername,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _fullNameCtrl,
                      textCapitalization: TextCapitalization.words,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Nome completo (opcional)',
                        prefixIcon: Icon(Icons.person_outline),
                        border: OutlineInputBorder(),
                      ),
                      validator: _validateFullName,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordCtrl,
                      obscureText: _obscurePassword,
                      textInputAction: TextInputAction.next,
                      decoration: InputDecoration(
                        labelText: 'Senha',
                        helperText: 'Mínimo 8 caracteres',
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          icon: Icon(_obscurePassword
                              ? Icons.visibility_outlined
                              : Icons.visibility_off_outlined),
                          onPressed: () => setState(
                            () => _obscurePassword = !_obscurePassword,
                          ),
                        ),
                        border: const OutlineInputBorder(),
                      ),
                      validator: _validatePassword,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordConfirmCtrl,
                      obscureText: _obscureConfirm,
                      textInputAction: TextInputAction.done,
                      onFieldSubmitted: (_) => _loading ? null : _submit(),
                      decoration: InputDecoration(
                        labelText: 'Confirmar senha',
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          icon: Icon(_obscureConfirm
                              ? Icons.visibility_outlined
                              : Icons.visibility_off_outlined),
                          onPressed: () => setState(
                            () => _obscureConfirm = !_obscureConfirm,
                          ),
                        ),
                        border: const OutlineInputBorder(),
                      ),
                      validator: _validatePasswordConfirm,
                    ),

                    // ---------- opcionais (colapsados) ----------
                    const SizedBox(height: 16),
                    ExpansionTile(
                      tilePadding: EdgeInsets.zero,
                      title: const Text('Dados opcionais'),
                      subtitle: const Text('Peso, altura e data de nascimento'),
                      childrenPadding:
                          const EdgeInsets.only(top: 8, bottom: 8),
                      children: [
                        TextFormField(
                          controller: _weightCtrl,
                          keyboardType: const TextInputType.numberWithOptions(
                            decimal: true,
                          ),
                          decoration: const InputDecoration(
                            labelText: 'Peso (kg)',
                            prefixIcon: Icon(Icons.monitor_weight_outlined),
                            border: OutlineInputBorder(),
                          ),
                          validator: _validateWeight,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _heightCtrl,
                          keyboardType: const TextInputType.numberWithOptions(
                            decimal: true,
                          ),
                          decoration: const InputDecoration(
                            labelText: 'Altura (cm)',
                            prefixIcon: Icon(Icons.height),
                            border: OutlineInputBorder(),
                          ),
                          validator: _validateHeight,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _birthDateCtrl,
                          readOnly: true,
                          onTap: _pickBirthDate,
                          decoration: const InputDecoration(
                            labelText: 'Data de nascimento (opcional)',
                            prefixIcon: Icon(Icons.cake_outlined),
                            suffixIcon: Icon(Icons.calendar_today),
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ],
                    ),

                    if (_error != null) ...[
                      const SizedBox(height: 16),
                      Text(
                        _error!,
                        style: TextStyle(color: theme.colorScheme.error),
                      ),
                    ],
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: _loading ? null : _submit,
                      child: _loading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Criar conta'),
                    ),
                    const SizedBox(height: 12),
                    TextButton(
                      onPressed: _loading ? null : () => context.go('/login'),
                      child: const Text('Já tem conta? Entre'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}