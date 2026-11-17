// [Sessão 39] EditProfilePage — edição do próprio perfil.
//
// Consome PUT /users/me (backend S39, commit 9d52470):
//   body: { weight_kg?: float(0,500), height_cm?: float(0,300), full_name?: str(≤120) }
//   response: UserResponse (mesmo shape do /auth/me) → parseado por UserMe.fromJson
//
// Semântica de "não mandou" vs "mandou null" (backend usa exclude_unset):
// - campo AUSENTE do body → não toca no banco
// - campo = null          → limpa o campo
// - campo com valor       → atualiza
//
// Esta tela só envia os campos que o usuário MUDOU ou LIMPOU. Campo
// intocado (valor atual == valor do controller) NÃO vai no body. Campo
// que o usuário tocou em "Limpar" vai como `null` explícito. Isso evita
// PUT redundante e respeita exclude_unset.
//
// Validação client-side espelha o backend (S39): weight_kg in (0, 500),
// height_cm in (0, 300), full_name ≤ 120. Botão Salvar desabilitado se
// algum campo estiver inválido OU se nada mudou.
//
// Retorno: Navigator.pop(UserMe) com o user pós-update (o ProfilePage
// faz setState + _load()). Se o usuário cancelar, pop(null).
//
// birth_date FICA FORA do escopo da S39 (UserUpdate do backend não
// aceita). email/username também (rotas próprias, chave única).
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/user_me.dart';
import '../services/api.dart';
import '../services/auth_service.dart';

class EditProfilePage extends StatefulWidget {
  final AuthService auth;
  final UserMe current;

  const EditProfilePage({
    super.key,
    required this.auth,
    required this.current,
  });

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  // Controllers criados no initState pra pré-preencher com o estado atual.
  late final TextEditingController _weightCtrl;
  late final TextEditingController _heightCtrl;
  late final TextEditingController _fullNameCtrl;

  // Valores iniciais guardados pra detectar "mudou?" no submit.
  // Se o controller final == inicial E não foi limpo → campo ausente.
  late final String _initialWeight;
  late final String _initialHeight;
  late final String _initialFullName;

  // "Limpar" foi acionado? Se sim, manda `null` explícito no body,
  // independente do que estiver no controller.
  bool _clearWeight = false;
  bool _clearHeight = false;

  // Loading do submit (desabilita botões, mostra spinner).
  bool _saving = false;

  // Form key pra validação client-side (TextFormField validator).
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _initialWeight = _formatNumber(widget.current.weightKg);
    _initialHeight = _formatNumber(widget.current.heightCm);
    _initialFullName = widget.current.fullName ?? '';

    _weightCtrl = TextEditingController(text: _initialWeight);
    _heightCtrl = TextEditingController(text: _initialHeight);
    _fullNameCtrl = TextEditingController(text: _initialFullName);
  }

  @override
  void dispose() {
    _weightCtrl.dispose();
    _heightCtrl.dispose();
    _fullNameCtrl.dispose();
    super.dispose();
  }

  /// Formata double pra string "limpa": 80.0 → "80", 80.5 → "80.5".
  /// Retorna '' quando null (campo vazio).
  static String _formatNumber(double? value) {
    if (value == null) return '';
    if (value == value.roundToDouble()) {
      return value.toInt().toString();
    }
    return value.toString();
  }

  /// Parser tolerante: aceita "80", "80.5", "80,5" (PT-BR). Retorna
  /// null se vazio ou inválido — o validator decide se é erro.
  static double? _parseNumber(String raw) {
    final trimmed = raw.trim().replaceAll(',', '.');
    if (trimmed.isEmpty) return null;
    return double.tryParse(trimmed);
  }

  /// Valida peso (>0, <500) — espelha backend UserUpdate.weight_kg.
  String? _validateWeight(String? raw) {
    if (_clearWeight) return null; // limpar é válido
    final v = _parseNumber(raw ?? '');
    if (v == null) return null; // vazio = não toca (ausente)
    if (v <= 0 || v >= 500) return 'Peso deve estar entre 0 e 500 kg';
    return null;
  }

  /// Valida altura (>0, <300) — espelha backend UserUpdate.height_cm.
  String? _validateHeight(String? raw) {
    if (_clearHeight) return null;
    final v = _parseNumber(raw ?? '');
    if (v == null) return null;
    if (v <= 0 || v >= 300) return 'Altura deve estar entre 0 e 300 cm';
    return null;
  }

  /// Valida nome (≤120) — espelha backend UserUpdate.full_name.
  String? _validateFullName(String? raw) {
    final v = (raw ?? '').trim();
    if (v.length > 120) return 'Nome deve ter no máximo 120 caracteres';
    return null;
  }

  /// Monta o body só com o que mudou. Regras:
  /// - _clearWeight true  → weight_kg: null
  /// - _clearWeight false E controller != inicial → weight_kg: valor
  /// - _clearWeight false E controller == inicial → ausente
  /// Idem pra altura. FullName: se != inicial → full_name: valor (ou null
  /// se o usuário apagou tudo e o inicial era preenchido).
  Map<String, dynamic> _buildBody() {
    final body = <String, dynamic>{};

    if (_clearWeight) {
      body['weight_kg'] = null;
    } else {
      final raw = _weightCtrl.text;
      if (raw.trim() != _initialWeight) {
        final v = _parseNumber(raw);
        if (v != null) body['weight_kg'] = v;
      }
    }

    if (_clearHeight) {
      body['height_cm'] = null;
    } else {
      final raw = _heightCtrl.text;
      if (raw.trim() != _initialHeight) {
        final v = _parseNumber(raw);
        if (v != null) body['height_cm'] = v;
      }
    }

    final fullName = _fullNameCtrl.text.trim();
    if (fullName != _initialFullName) {
      // Se o usuário apagou tudo, manda null (limpa). Se preencheu, manda string.
      body['full_name'] = fullName.isEmpty ? null : fullName;
    }

    return body;
  }

  Future<void> _save() async {
    // Validação client-side via Form (weight/height/fullName).
    if (!_formKey.currentState!.validate()) return;

    final body = _buildBody();
    if (body.isEmpty) {
      // Nada mudou — só fecha devolvendo o user atual (idempotente).
      Navigator.of(context).pop(widget.current);
      return;
    }

    setState(() => _saving = true);
    try {
      final updated = await widget.auth.api.updateMe(
        fullName: body.containsKey('full_name')
            ? (body['full_name'] as String?)
            : null,
        weightKg: body.containsKey('weight_kg')
            ? (body['weight_kg'] as double?)
            : null,
        heightCm: body.containsKey('height_cm')
            ? (body['height_cm'] as double?)
            : null,
        fieldsToClear: {
          if (body.containsKey('weight_kg') && body['weight_kg'] == null)
            'weight_kg': true,
          if (body.containsKey('height_cm') && body['height_cm'] == null)
            'height_cm': true,
          if (body.containsKey('full_name') && body['full_name'] == null)
            'full_name': true,
        },
        token: widget.auth.token,
      );
      if (!mounted) return;
      Navigator.of(context).pop(updated);
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message)),
      );
      setState(() => _saving = false);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro inesperado: $e')),
      );
      setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Editar perfil'),
        leading: TextButton(
          onPressed: _saving ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        leadingWidth: 96,
        actions: [
          if (_saving)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Center(
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            TextButton(
              onPressed: _save,
              child: const Text('Salvar'),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              'Atualize seus dados. Campos vazios não são alterados.',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 24),

            // ===== Peso =====
            _NumberField(
              controller: _weightCtrl,
              label: 'Peso (kg)',
              hint: 'Ex.: 75.5',
              validator: _validateWeight,
              enabled: !_saving && !_clearWeight,
              suffix: _clearWeight
                  ? TextButton(
                      onPressed: () => setState(() {
                        _clearWeight = false;
                        _weightCtrl.text = _initialWeight;
                      }),
                      child: const Text('Desfazer'),
                    )
                  : (widget.current.weightKg != null
                      ? IconButton(
                          tooltip: 'Limpar peso',
                          icon: const Icon(Icons.clear, size: 20),
                          onPressed: () => setState(() {
                            _clearWeight = true;
                            _weightCtrl.clear();
                          }),
                        )
                      : null),
            ),
            const SizedBox(height: 16),

            // ===== Altura =====
            _NumberField(
              controller: _heightCtrl,
              label: 'Altura (cm)',
              hint: 'Ex.: 180',
              validator: _validateHeight,
              enabled: !_saving && !_clearHeight,
              suffix: _clearHeight
                  ? TextButton(
                      onPressed: () => setState(() {
                        _clearHeight = false;
                        _heightCtrl.text = _initialHeight;
                      }),
                      child: const Text('Desfazer'),
                    )
                  : (widget.current.heightCm != null
                      ? IconButton(
                          tooltip: 'Limpar altura',
                          icon: const Icon(Icons.clear, size: 20),
                          onPressed: () => setState(() {
                            _clearHeight = true;
                            _heightCtrl.clear();
                          }),
                        )
                      : null),
            ),
            const SizedBox(height: 16),

            // ===== Nome completo =====
            TextFormField(
              controller: _fullNameCtrl,
              enabled: !_saving,
              maxLength: 120,
              validator: _validateFullName,
              decoration: const InputDecoration(
                labelText: 'Nome completo',
                hintText: 'Como você quer aparecer',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),

            Text(
              'E-mail e username não são editáveis por aqui — '
              'têm fluxos próprios.',
              style: theme.textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

/// Campo numérico reutilizável (peso/altura) com:
/// - `keyboardType: numberWithOptions(decimal: true)`
/// - `inputFormatters` restringindo a dígitos + 1 separador (. ou ,)
/// - `suffix` opcional (botão Limpar/Desfazer)
class _NumberField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final String? Function(String?) validator;
  final bool enabled;
  final Widget? suffix;

  const _NumberField({
    required this.controller,
    required this.label,
    required this.hint,
    required this.validator,
    required this.enabled,
    this.suffix,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      enabled: enabled,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      inputFormatters: [
        // Só dígitos + 1 separador decimal (aceita . e ,).
        FilteringTextInputFormatter.allow(RegExp(r'[\d.,]')),
      ],
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: const OutlineInputBorder(),
        suffixIcon: suffix,
      ),
    );
  }
}