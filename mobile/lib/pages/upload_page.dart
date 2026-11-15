// [Sessão 31] Tela de upload de GPX/FIT.
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../services/api.dart';
import '../services/auth_service.dart';

class UploadPage extends StatefulWidget {
  final AuthService auth;
  const UploadPage({super.key, required this.auth});

  @override
  State<UploadPage> createState() => _UploadPageState();
}

class _UploadPageState extends State<UploadPage> {
  static const int _maxBytes = 20 * 1024 * 1024; // 20 MB (mesmo do web)
  static const Set<String> _allowedExt = {'gpx', 'fit'};

  final TextEditingController _titleCtrl = TextEditingController();
  final TextEditingController _descCtrl = TextEditingController();

  File? _file;
  String? _fileName;
  int? _fileSize;
  bool _submitting = false;

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    if (_submitting) return;

    // [Sessão 31 — fix] file_picker 13.x: pickFiles() é estático e retorna
    // List<PlatformFile> direto (vazio = cancelou). FilePickerResult não existe mais.
    final picked = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: _allowedExt.toList(),
    );

    if (picked.isEmpty) return; // cancelou

    final file = picked.first;
    final path = file.path;
    if (path == null) {
      _showError('Não foi possível acessar o arquivo selecionado.');
      return;
    }

    // Defesa extra: o picker já filtra por extensão, mas garantimos.
    final name = file.name;
    final dot = name.lastIndexOf('.');
    final ext = dot >= 0 ? name.substring(dot + 1).toLowerCase() : '';
    if (!_allowedExt.contains(ext)) {
      _showError('Formato não suportado. Use .gpx ou .fit.');
      return;
    }

    // [Sessão 31 — fix] PlatformFile.size virou length() (Future<int?>).
    final size = await file.length();
    if (size == null) {
      _showError('Não foi possível determinar o tamanho do arquivo.');
      return;
    }
    if (size > _maxBytes) {
      _showError(
        'Arquivo muito grande (${_formatBytes(size)}). Limite: 20 MB.',
      );
      return;
    }

    setState(() {
      _file = File(path);
      _fileName = name;
      _fileSize = size;
    });
  }

  Future<void> _submit() async {
    final file = _file;
    if (file == null || _submitting) return;

    setState(() => _submitting = true);

    try {
      final created = await widget.auth.api.uploadActivity(
        file: file,
        title: _titleCtrl.text,
        description: _descCtrl.text,
        token: widget.auth.token,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Atividade enviada: ${created.title ?? created.typeLabel}'),
          backgroundColor: Colors.green.shade700,
        ),
      );
      context.pop(true);
    } on ApiException catch (e) {
      if (!mounted) return;
      _showError(e.message);
    } catch (e) {
      if (!mounted) return;
      _showError('Falha no upload: $e');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }

  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(bytes / (1024 * 1024)).toStringAsFixed(2)} MB';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final canSubmit = _file != null && !_submitting;

    return Scaffold(
      appBar: AppBar(title: const Text('Enviar atividade')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'Selecione um arquivo .gpx ou .fit (até 20 MB).',
            style: theme.textTheme.bodyMedium,
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: _submitting ? null : _pickFile,
            icon: const Icon(Icons.attach_file),
            label: Text(_file == null ? 'Selecionar arquivo' : 'Trocar arquivo'),
          ),
          if (_fileName != null) ...[
            const SizedBox(height: 8),
            Card(
              child: ListTile(
                leading: const Icon(Icons.description_outlined),
                title: Text(
                  _fileName!,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                subtitle: _fileSize != null ? Text(_formatBytes(_fileSize!)) : null,
                trailing: _submitting
                    ? null
                    : IconButton(
                        tooltip: 'Remover',
                        icon: const Icon(Icons.close),
                        onPressed: () {
                          setState(() {
                            _file = null;
                            _fileName = null;
                            _fileSize = null;
                          });
                        },
                      ),
              ),
            ),
          ],
          const SizedBox(height: 16),
          TextField(
            controller: _titleCtrl,
            enabled: !_submitting,
            maxLength: 120,
            decoration: const InputDecoration(
              labelText: 'Título (opcional)',
              hintText: 'Ex.: Corrida no parque',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _descCtrl,
            enabled: !_submitting,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Descrição (opcional)',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: canSubmit ? _submit : null,
            icon: _submitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.upload_file),
            label: Text(_submitting ? 'Enviando...' : 'Enviar'),
          ),
          const SizedBox(height: 8),
          Text(
            'O processamento pode levar alguns segundos.',
            style: theme.textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}