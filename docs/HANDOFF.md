HANDOFF — SESSÃO 47 (para a Sessão 48)

    Instruções para quem chega agora: leia a Seção 0 primeiro. Ela tem o contexto operacional e as regras que não mudam. Depois leia a Seção 8 (próximos passos) antes de tocar em qualquer arquivo. A S47 fechou sem commit — a primeira ação da S48 é commitar o que está pronto (Seção 5).

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro (S21–S47, inalterada)

Você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho. Nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.
Regras críticas S21–S46 mantidas integralmente

    Código sempre completo (não diff parcial).

    Handoff completo ao chegar em 70–80% do contexto.

    Avisar sobre limite do chat e limite do site/IA (o segundo não é mensurável pelo assistente; declarar essa limitação).

    Percentual de prontidão ao final de cada sessão.

    Seguir as recomendações do assistente como plano padrão.

Adições da S47 (NOVAS — importantes)

S47a (NOVA — lição aprendida, violação da regra de ouro). Na S47, o assistente reconstruiu o login_page.dart a partir de um Select-String (trechos), assumindo AuthService.instance. Errado: o projeto injeta AuthService por construtor (LoginPage({required this.auth}), widget.auth.login(...)). O erro gerou retrabalho. Regra nova, obrigatória: para qualquer arquivo que não foi recebido inteiro, entregar apenas a regra de substituição (com Ctrl+F), nunca o arquivo completo. Se o arquivo for essencial, pedir Get-Content inteiro antes.

S47b (NOVA — padrão de injeção do AuthService). O main.dart instancia final AuthService _auth = AuthService(); no _RumoAppState e injeta em todos os pages por construtor:
dart

GoRoute(path: '/login', builder: (_, _) => LoginPage(auth: _auth)),
GoRoute(path: '/feed',  builder: (_, _) => FeedPage(auth: _auth)),
// ... todos os pages recebem auth: _auth

Não há Provider, não há AuthService.instance, não há context.read. Se algum código novo precisar do auth, usar widget.auth no State ou receber por construtor. Isso não estava documentado no handoff S46 — agora está.

S47c (NOVA — Docker de teste obrigatório para pytest). O pytest local exige o container Docker de teste. Sem ele, todos os testes falham com ConnectionRefusedError em tests/conftest.py:77. O conftest.py aponta para postgresql+asyncpg://rumo:rumo@localhost:5433/rumo_test (porta 5433, não 5432). O container é rumo_postgres_test, definido em backend/docker-compose.test.yml. Comando: docker compose -f docker-compose.test.yml up -d. O handoff S46 não mencionava isso — agora está.

S47d (NOVA — ambiente Docker confirmado). Docker Desktop está instalado e rodando na máquina. Containers ativos: rumo-postgres (postgis/postgis:16-3.4, porta 5432) e rumo-redis (redis:7-alpine, porta 6379). O container de teste (rumo_postgres_test, porta 5433) sobe sob demanda. Postgres 12 nativo instalado mas parado — não usar.

S47e (NOVA — erro de rede interno do ApiClient usa statusCode == 0). O api.dart já lança ApiException(0, 'Falha de rede no upload: $e') e ApiException(0, 'Falha de rede no export: $e') em timeouts de upload/export. O tradutor de erros deve tratar statusCode == 0 como "sem conexão" (já trata — ver error_message.dart).

S47f (NOVA — ApiException contrato confirmado). lib/services/api.dart define:
dart

class ApiException implements Exception {
  final int statusCode;   // int (não String, não nullable)
  final String message;   // .detail do FastAPI já extraído, ou fallback
  ApiException(this.statusCode, this.message);  // construtor posicional
}

S47g (NOVA — AuthService extends ChangeNotifier). O AuthService é um ChangeNotifier com login, logout, bootstrap, currentUserId, token, isLoggedIn, loading, api (getter que expõe ApiClient). Não é singleton. Toda a árvore recebe a mesma instância via construtor (S47b).
SEÇÃO 1 — TL;DR para quem chega agora

Estado do repo ao fim da S47: HEAD == origin/main == 9d93e95 — a S47 NÃO commitou. Os arquivos alterados estão no working tree:
text

?? mobile/lib/utils/error_message.dart       (novo, criado na S47)
 M mobile/lib/pages/login_page.dart          (modificado na S47)

Ação imediata da S48: commitar esses 2 arquivos (ver Seção 5, comando exato).

S47 fez:

    Criou lib/utils/error_message.dart — tradutor central de erros (SocketException, TimeoutException, ApiException por statusCode: 0, 401, 403, 404, 409, 422, 429, 5xx; FormatException; fallback). Valida com flutter analyze.

    Corrigiu e atualizou lib/pages/login_page.dart — usa friendlyErrorMessage(e) nos dois catch. O erro original (AuthService.instance) foi corrigido para widget.auth (padrão correto do projeto). Valida com flutter analyze.

S47 NÃO fez (fica para S48):

    Item 10.1 nos 7 pages restantes: feed_page.dart, activity_detail_page.dart, upload_page.dart, profile_page.dart, user_profile_page.dart, search_page.dart, edit_profile_page.dart.

    Commit do que foi feito (deixado para a S48 para evitar ambiguidade de hash no handoff).

    Item 10.2 (tela de cadastro), 10.3 (animação do mapa), 10.4 (outras melhorias), itens 7, 8, 10, 13 herdados do S46.

Fase 0 da S47 (verificações):

    Web build ✅ (✓ built in 6.12s)

    Web lint ✅ (0 erros)

    Mobile analyze ✅ (No issues found!)

    Backend pytest ✅ (180 passed in 46.96s após subir o container de teste)

    Backend ruff ✅ (All checks passed!)

    Backend prod /health ✅ (200), /docs ✅ (200)

    Frontend prod / ✅ (200)

Percentual consolidado: ~86% (mobile subiu de ~93% para ~94% porque o 10.1 começou; backend/web inalterados).
SEÇÃO 2 — PRODUÇÃO E AMBIENTE (atualizado S47)

    Backend: https://rumo-api-5s0b.onrender.com

    Frontend Web: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

    Flutter: 3.47.9 / Dart 3.13.7 (C:\Users\nasci\flutter)

    SO: Windows 11 (26H2), PowerShell 5.1

    Python: 3.13.7 (venv em D:\Rumo\backend\venv)

    Android SDK: C:\Users\nasci\AppData\Local\Android\Sdk (SDK 36.0.0, NDK 27.0)

    Android Studio: C:\Program Files\Android\Android Studio\bin\studio64.exe

    Celular de teste: Redmi Note 8 (Android 10, API 29, arm64) — c767cacd no flutter devices

    Emulador: emulador1 — NÃO usar (S45g)

    Docker Desktop: instalado e rodando (S47d). Containers:

        rumo-postgres (postgis/postgis:16-3.4, 5432) — produção local

        rumo-redis (redis:7-alpine, 6379)

        rumo_postgres_test (postgis/postgis:16-3.4, 5433) — deve ser iniciado para rodar pytest

Git ao fim da S47 (esperado após commit da S48):
text

<novo_hash> (HEAD -> main, origin/main) feat(mobile): tradutor de erros amigaveis + login usando friendlyErrorMessage (Sessao 47, 10.1 parcial)
9d93e95 docs: adiciona backlog da Sessao 47 no handoff (erros amigaveis, cadastro, animacao de rota)
0898e5e fix(mobile): app roda no celular real + permissao INTERNET + overflow corrigido + .gitignore Flutter (Sessao 46)
74ecb32 docs: handoff da Sessao 44 (build Android bloqueado)
b893f98 docs: handoff da Sessao 44
...

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 47
3.1 Fase 0 — todas as verificações passaram

Listado na Seção 1. Nada a fazer.
3.2 lib/utils/error_message.dart (novo)

Propósito: centralizar a tradução de exceções para mensagens amigáveis em português.

Função pública: String friendlyErrorMessage(Object e)

Cobertura:
Tipo	Mensagem
SocketException / http.ClientException	"Não foi possível conectar. Verifique sua internet e tente novamente."
TimeoutException	"O servidor demorou para responder. Tente novamente."
ApiException(statusCode == 0)	(mesma de rede)
ApiException(401)	"E-mail ou senha incorretos."
ApiException(403)	"Você não tem permissão para acessar este conteúdo."
ApiException(404)	"Conteúdo não encontrado."
ApiException(409)	"Este e-mail já está cadastrado."
ApiException(422)	"Verifique os campos e tente novamente."
ApiException(429)	"Muitas tentativas. Aguarde um momento e tente novamente."
ApiException(5xx)	"Erro no servidor. Tente novamente em instantes."
FormatException	"Resposta inválida do servidor. Tente novamente."
Outros 4xx com message não vazia	a própria e.message
Fallback	"Algo deu errado. Tente novamente."

Detalhes de design:

    Em kDebugMode, faz debugPrint do erro cru ([friendlyErrorMessage] <Type>: <e>) — preserva depuração sem expor lixo em release.

    Não importa flutter/material.dart — só dart:async, dart:io, package:flutter/foundation.dart, package:http/http.dart, ../services/api.dart. Utilitário puro, testável.

    5xx nunca expõe e.message (pode conter SQL/traceback).

    401 é tratado como "credenciais inválidas" — a detecção de sessão expirada com redirecionamento fica para 10.4 (toca navegação).

Caminho: mobile/lib/utils/error_message.dart (novo).
3.3 lib/pages/login_page.dart (modificado)

Mudanças S47:

    Import novo: import '../utils/error_message.dart';

    on ApiException catch (e) { setState(() => _error = friendlyErrorMessage(e)); }

    catch (e) { setState(() => _error = friendlyErrorMessage(e)); }

    Correção crítica (S47a/S47b): LoginPage agora recebe final AuthService auth no construtor; _submit usa widget.auth.login(...) em vez de AuthService.instance.login(...).

Contrato correto (referência para os 7 pages restantes):
dart

class LoginPage extends StatefulWidget {
  final AuthService auth;
  const LoginPage({super.key, required this.auth});
  ...
}
// No State:
await widget.auth.login(...);

Caminho: mobile/lib/pages/login_page.dart (modificado).

Validação: flutter analyze → No issues found!
SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)

Nenhuma mudança desde S39. 180 testes passando (confirmado na S47 após subir o container rumo_postgres_test na porta 5433). Nada a fazer no backend para a S48.

Contrato relevante para o 10.1 (erros): o backend FastAPI devolve {"detail": "..."} para erros. O ApiClient._extractMessage já extrai esse detail. O ApiException.message já contém esse valor. O tradutor só formata o que já existe — não modifica o api.dart.
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Ação imediata na S48 (primeira coisa):
powershell

cd D:\Rumo

# Confirmar o que vai entrar (devem ser 2 arquivos)
git status --short --untracked-files=all

# Stage explícito
git add mobile/lib/utils/error_message.dart
git add mobile/lib/pages/login_page.dart

# Commit
git commit -m "feat(mobile): tradutor de erros amigaveis + login usando friendlyErrorMessage (Sessao 47, 10.1 parcial)"

# Push
git push

Mensagem sugerida do commit (se quiser mais detalhe):
text

feat(mobile): tradutor de erros amigaveis + login usando friendlyErrorMessage (Sessao 47, 10.1 parcial)

- lib/utils/error_message.dart (novo): friendlyErrorMessage(Object e) traduz
  SocketException, ClientException, TimeoutException, ApiException (por
  statusCode: 0, 401, 403, 404, 409, 422, 429, 5xx), FormatException e
  fallback. Em kDebugMode, debugPrint do erro cru. Nao importa material.dart
  (utilitario puro).
- lib/pages/login_page.dart: os dois catch usam friendlyErrorMessage(e).
  Corrige tambem o contrato do AuthService: LoginPage recebe `final AuthService
  auth` por construtor (padrao do main.dart) e usa `widget.auth.login(...)`,
  nao `AuthService.instance`.

Backend intocado. Flutter analyze verde.

Pendente para a Sessao 48: aplicar o mesmo padrao nos 7 pages restantes
(feed, activity_detail, upload, profile, user_profile, search, edit_profile).

O que espero ver em git status --short antes do commit: exatamente 2 linhas:
text

?? mobile/lib/utils/error_message.dart
 M mobile/lib/pages/login_page.dart

Se aparecer mais alguma coisa (ex.: algum build/), remover do stage antes do commit.
SEÇÃO 6 — SCRIPTS ÚTEIS (S47)
Subir o container de teste do backend (obrigatório antes do pytest)
powershell

cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
# aguardar ~3s; depois:
.\venv\Scripts\Activate.ps1
python -m pytest -q
# Esperado: 180 passed

Sem isso, o pytest falha com ConnectionRefusedError em tests/conftest.py:77. O conftest.py aponta para localhost:5433 (não 5432). O Postgres 12 nativo não serve.
Rodar flutter analyze após editar arquivo mobile
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
# Esperado: No issues found!

Verificar estado do repo antes de qualquer commit
powershell

cd D:\Rumo
git log --oneline -5
git status --short --untracked-files=all

Para os 7 pages restantes do 10.1 (novo processo S47a)

Para cada arquivo:
powershell

cd D:\Rumo\mobile
Get-Content lib\pages\<arquivo>.dart -Encoding UTF8

Colar a saída inteira para o assistente. Nunca pedir para o assistente reconstruir a partir de Select-String.
SEÇÃO 7 — DÍVIDAS TÉCNICAS (S47)
Fechadas na S47

    (S46) Erros técnicos crus para o usuário — error_message.dart criado; login já usa. Os 7 pages restantes ficam para S48.

    (S46) Falta de documentação do padrão AuthService — agora documentado (S47b).

Conhecidas (não-bug)

    (S41) prod@rumo.com state — estado, não bug.

    (S42k) PWA sem PNGs — não-bloqueador.

    (S43d) BOM em build.gradle.kts e AndroidManifest.xml — não-bloqueador.

    (S43e) Info.plist sem hardcode — correto.

    (S44) Dois commits de handoff S44 com a mesma mensagem (b893f98, 74ecb32) — cosmético, não reescrever histórico.

Oportunidades (S48+)

    (S47) Aplicar friendlyErrorMessage nos 7 pages restantes (10.1 completo).

    (S47) O handoff S46 não mencionava o container Docker de teste — agora está na Seção 6. Considerar adicionar docker compose up -d ao README ou docs/.

    (S46) Item 10.2: tela de cadastro (requer verificar se o backend tem POST /auth/register).

    (S46) Item 10.3: animação do mapa (Polyline progressiva via AnimationController).

    (S46) Item 10.4: spinner em botões que faltam, empty states, pull-to-refresh, tratamento global de 401 com redirecionamento.

    (S46) Item 7 completo: validar feed/perfil/upload/like/comentários/export no Redmi Note 8.

    (S46) Item 8: splash + ícone no launcher.

    (S46) Item 10: keystore + signingConfigs.

    (S46) Item 13: remover BOM de build.gradle.kts e AndroidManifest.xml.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 48)
Primeira ação (obrigatória): commitar a S47

Ver Seção 5. Fazer o git add dos 2 arquivos, commit, push. Confirmar hash novo.
Segunda ação (Fase 0 padrão): verificações
powershell

cd D:\Rumo
git log --oneline -5
git status --short --untracked-files=all

# Web
cd D:\Rumo\web
npm run build
npm run lint

# Mobile
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# Backend (subir container de teste primeiro!)
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .

# Produção
curl.exe -s -o NUL -w "backend health: %{http_code}`n" https://rumo-api-5s0b.onrender.com/health
curl.exe -s -o NUL -w "frontend home:  %{http_code}`n" https://rumo-wheat.webfrontend.app/

Terceira ação: completar 10.1 nos 7 pages restantes (novo processo S47a)

Para cada arquivo, em ordem (do maior/mais crítico para o menor):

    feed_page.dart — maior, mais catch. Onde o erro de hoje teria doído mais.

    activity_detail_page.dart — S46 mexeu (overflow). Conferir se a correção Wrap + ClipRRect está intacta.

    upload_page.dart — usa ApiException(0, ...) do api.dart; o tradutor já cobre.

    profile_page.dart

    user_profile_page.dart

    search_page.dart

    edit_profile_page.dart

Processo por arquivo:

    Usuário roda Get-Content lib\pages\<arquivo>.dart -Encoding UTF8 e cola a saída.

    Assistente devolve o arquivo completo com edições marcadas // [S47-10.1].

    Usuário substitui, roda flutter analyze.

    Se verde, próximo arquivo.

Regra de substituição para cada page (o padrão que o login seguiu):

    Adicionar import '../utils/error_message.dart';

    Todo catch (e) { _error = e.message; } → catch (e) { _error = friendlyErrorMessage(e); }

    Todo catch (e) { _error = 'Erro: $e'; } → catch (e) { _error = friendlyErrorMessage(e); }

    Todo SnackBar(content: Text('$e')) → SnackBar(content: Text(friendlyErrorMessage(e)))

    Preservar o padrão de exibição de cada tela (inline vermelho vs SnackBar). Não misturar.

    Não tocar em validators, navegação, lógica de like/comentário/upload.

Quando os 7 estiverem verdes: commit final do 10.1 completo:
text

feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo)

Quarta ação (se sobrar tempo): escolher entre

    10.2 — tela de cadastro (verificar se backend tem POST /auth/register; se não, criar endpoint no backend primeiro).

    10.4 — melhorias incrementais (spinner em botões que faltam, empty states, pull-to-refresh).

    Item 7 — validação no Redmi Note 8 (feed/perfil/upload/like/comentários/export).

    Item 8 — splash + ícone no launcher.

    Item 10 — keystore + signingConfigs (só após item 7 completo).

Ordem recomendada: terminar 10.1 primeiro (é o que está em andamento), depois 10.2, depois item 7 completo, depois item 10.
Observação importante sobre o AuthService nos pages restantes

Os 7 pages recebem AuthService por construtor (padrão S47b). Ao colar cada arquivo, o assistente deve verificar o construtor antes de assumir widget.auth. Se algum page não receber auth, o assistente para e pergunta antes de entregar — não reconstrói.
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S47)

S21–S46: acordos mantidos (código completo, handoff completo, aviso de limite, percentual).

S46: o usuário confirmou que o app funcionou no celular real após as correções do S46.

S47: o usuário pediu explicitamente:

    "vamos deixar algumas coisas acordada, sempre seguir suas recomendações" — o assistente deve apresentar recomendações como plano padrão.

    "sempre colocar o código completo" — mesmo em alteração de 3 linhas.

    "fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%" — aviso proativo + handoff.

    "me informasse o percentual de quanto nosso projeto já está pronto" — tabela de percentual ao final.

    "avisasse se caso isso for ocorrer" (referindo-se ao chat acabar no meio do código) — não só limite do chat, mas limite do site/IA. O assistente deve avisar que o limite do site não é mensurável e sinalizar antes de respostas longas.

S47 — decisão de fechamento: ao chegar em ~65%, o assistente recomendou a Opção 3 (commitar o que está pronto + handoff), em vez de tentar mais um arquivo e arriscar corte. O usuário concordou. Isso está em linha com o acordo. A S48 retoma com o commit e os 7 pages restantes.

Acordos novos da S47: S47a–S47g.
SEÇÃO 10 — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 47)
Área	%	Observação
Backend	~95%	inalterado (180 testes passando, ruff verde, prod 200)
Web	~99%	inalterado (build + lint verdes, prod 200)
Mobile	~94%	subiu de ~93% (error_message + login corrigido; falta aplicar nos 7 pages restantes)
Bloqueadores não-código	~25%	inalterado (contas Google Play/Apple, keystore)
MVP consolidado	~86%	subiu de ~85% (10.1 iniciado com sucesso)
Variação em relação à S46

    Mobile: 93% → 94% (+1% — error_message + login)

    MVP: 85% → 86% (+1%)

Estimativa

    10.1 completo (7 pages): ~1 sessão curta (se o processo S47a for seguido à risca, ~2–3 h de trabalho).

    10.2 cadastro (verificar backend + tela): ~1 sessão.

    Item 7 completo (validação no celular): ~1 sessão.

    Item 10 keystore + Item 8 splash/ícone: ~1 sessão.

    Total até "pronto para submeter": ~3–4 sessões. +1–2 de review. Total ~4–6 sessões.

SEÇÃO 11 — BACKLOG DA SESSÃO 48 (planejamento)

Base: repo no commit <novo_hash> (S47 commitada). error_message.dart + login_page.dart commitados.
11.1 Item 10.1 — aplicar nos 7 pages restantes (prioridade alta)

Ver Seção 8, Terceira ação. Ordem:

    feed_page.dart

    activity_detail_page.dart

    upload_page.dart

    profile_page.dart

    user_profile_page.dart

    search_page.dart

    edit_profile_page.dart

Processo: colar inteiro → assistente devolve completo → flutter analyze → próximo.

Quando os 7 verdes: commit feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo).
11.2 Item 10.2 — Tela de Cadastro (prioridade alta)

Pré-requisito: verificar se o backend tem POST /auth/register:
powershell

cd D:\Rumo\backend
Get-ChildItem app\routers -Filter *.py | Select-String -Pattern "register|/auth" -List
Get-Content app\routers\auth.py -Encoding UTF8 -ErrorAction SilentlyContinue

    Se existir: criar lib/pages/register_page.dart (nome completo, username, e-mail, senha, confirmação; validação local; spinner; link "Já tem conta? Entre"). Adicionar rota /register no main.dart e link na login_page.dart.

    Se não existir: criar no backend primeiro (S48 ou S49) e depois a tela.

11.3 Item 10.4 — Melhorias incrementais (prioridade média)

    Spinner em botões que faltam (like, upload, cadastro).

    Empty states amigáveis (feed vazio, perfil sem atividades, busca sem resultados).

    Pull-to-refresh no feed e no perfil.

    Tratamento global de 401 com redirecionamento para login (cuidado: toca navegação; testar bem).

11.4 Itens herdados da S46 (não concluídos)

    Item 7 completo: validar feed/perfil/upload/like/comentários/export no Redmi Note 8.

    Item 8: splash + ícone no launcher.

    Item 10: keystore + signingConfigs (só após item 7 completo).

    Item 13: higiene (remover BOM de build.gradle.kts e AndroidManifest.xml, remover comentário com.example se existir).

11.5 Ordem sugerida para a S48

    Fase 0 (obrigatória): git log/status, web build/lint, mobile analyze, backend pytest/ruff (com container), prod backend/frontend.

    Commit da S47 (Seção 5) — se ainda não foi feito.

    Item 10.1 nos 7 pages (processo S47a).

    Commit do 10.1 completo.

    Item 10.2 (cadastro) — se o backend tiver endpoint; senão, avaliar criar.

    Item 10.4 (incremental) — conforme tempo.

    Item 7 completo (validação no celular) — se sobrar tempo.

RESUMO EXECUTIVO PARA A S48

    O que fazer primeiro: commit dos 2 arquivos pendentes (error_message.dart + login_page.dart) — Seção 5.

    O que fazer depois: Fase 0 completa (Seção 8, Segunda ação).

    O que fazer em seguida: aplicar friendlyErrorMessage nos 7 pages restantes, um por vez, colando o arquivo inteiro e devolvendo completo (Seção 8, Terceira ação).

    O que NÃO fazer: reconstruir arquivo a partir de Select-String (S47a). Assumir AuthService.instance (S47b). Rodar pytest sem subir o container de teste (S47c).

    Regra de ouro: não tenho acesso ao disco. Pedir Get-Content inteiro. Nunca inventar caminho. Nunca reescrever arquivo não recebido.