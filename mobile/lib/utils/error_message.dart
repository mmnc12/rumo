// lib/utils/error_message.dart
//
// Tradutor central de erros -> mensagem amigável para o usuário.
//
// [Sessão 47 — item 10.1] Antes disso, cada tela exibia o erro cru:
//   - `ClientException with SocketException: Failed host lookup: '...'`
//   - `ApiException(401): Invalid credentials`
//   - `TimeoutException after 0:00:30.000000`
// Isso confundia o usuário e expunha detalhes técnicos. Agora todas as
// telas chamam `friendlyErrorMessage(e)` e recebem uma string curta,
// em português, com orientação de próximo passo.
//
// Contrato com `ApiException` (lib/services/api.dart):
//   class ApiException implements Exception {
//     final int statusCode;  // 0 = falha de rede (upload/export)
//     final String message;  // já é o .detail do FastAPI, quando houver
//   }
//
// Cobertura:
//   - SocketException / ClientException (http) -> sem conexão / DNS
//   - TimeoutException                        -> servidor demorou
//   - ApiException por statusCode             -> 401, 403, 404, 409, 422, 429, 5xx
//   - FormatException                         -> resposta inválida
//   - Fallback                                -> "Algo deu errado..."
//
// NÃO importa flutter/material.dart (é utilitário puro; testável).

import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../services/api.dart';

/// Converte qualquer exceção em uma mensagem amigável para o usuário final.
///
/// A string retornada NUNCA contém stack trace, nome de host, caminho de
/// arquivo ou detalhe técnico. É segura para exibir em `Text`, `SnackBar`
/// ou `showDialog`.
///
/// Em `kDebugMode`, imprime o erro cru com `debugPrint` para preservar a
/// depuração sem expor lixo ao usuário em produção.
String friendlyErrorMessage(Object e) {
  // Log de debug (não aparece em release).
  if (kDebugMode) {
    debugPrint('[friendlyErrorMessage] ${e.runtimeType}: $e');
  }

  // 1) ApiException — prioridade máxima, tem statusCode.
  if (e is ApiException) {
    return _messageForApiException(e);
  }

  // 2) Falha de rede (SocketException é de dart:io; ClientException é do
  //    package:http e pode embrulhar SocketException em plataformas web).
  if (e is SocketException) {
    return _noConnectionMessage;
  }
  if (e is http.ClientException) {
    // "Failed host lookup: '...'" ou "Connection refused" -> sem rede/DNS.
    return _noConnectionMessage;
  }

  // 3) Timeout.
  if (e is TimeoutException) {
    return 'O servidor demorou para responder. Tente novamente.';
  }

  // 4) JSON inválido / resposta inesperada.
  if (e is FormatException) {
    return 'Resposta inválida do servidor. Tente novamente.';
  }

  // 5) Fallback.
  return 'Algo deu errado. Tente novamente.';
}

const String _noConnectionMessage =
    'Não foi possível conectar. Verifique sua internet e tente novamente.';

/// Mapeia ApiException(statusCode, message) -> mensagem amigável.
String _messageForApiException(ApiException e) {
  final int code = e.statusCode;

  // 0 = falha de rede interna do ApiClient (upload/export).
  if (code == 0) {
    return _noConnectionMessage;
  }

  // 401 — credenciais inválidas OU token expirado.
  // O backend usa 401 para "Invalid credentials" no login e para
  // "Not authenticated" em rotas protegidas. Na dúvida, o texto de
  // credenciais é o mais útil para o usuário final (sessão expirada
  // global fica para 10.4, que vai detectar e redirecionar).
  if (code == 401) {
    return 'E-mail ou senha incorretos.';
  }

  // 403 — sem permissão para ver o recurso (ex.: não segue o autor).
  if (code == 403) {
    return 'Você não tem permissão para acessar este conteúdo.';
  }

  // 404 — recurso não encontrado.
  if (code == 404) {
    return 'Conteúdo não encontrado.';
  }

  // 409 — conflito (ex.: e-mail já cadastrado; follow duplicado).
  if (code == 409) {
    return 'Este e-mail já está cadastrado.';
  }

  // 422 — validação de formulário do backend.
  // O backend manda um .detail estruturado; a mensagem crua é feia.
  // Mensagem genérica é melhor que expor JSON.
  if (code == 422) {
    return 'Verifique os campos e tente novamente.';
  }

  // 429 — rate limit.
  if (code == 429) {
    return 'Muitas tentativas. Aguarde um momento e tente novamente.';
  }

  // 5xx — erro do servidor. NUNCA expor e.message (pode conter SQL,
  // traceback, path). Mensagem genérica + log em debug já feito acima.
  if (code >= 500 && code <= 599) {
    return 'Erro no servidor. Tente novamente em instantes.';
  }

  // Outros 4xx — usa a mensagem do backend se não for vazia.
  final String raw = e.message.trim();
  if (raw.isNotEmpty) return raw;

  return 'Algo deu errado. Tente novamente.';
}