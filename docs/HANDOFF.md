HANDOFF — SESSÃO 48 (para a Sessão 49)

Instruções para quem chega agora: leia a Seção 0 primeiro. Depois a Seção 8 (próximos passos). A S48 fechou o item 10.1 completo (7 pages verdes). O repo está em 07a3301 + as edições do 10.1 ainda não commitadas (working tree). A primeira ação da S49 é commitar o 10.1 (Seção 5) — e depois o handoff da S48.
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro (S21–S48, inalterada): Você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho. Nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

Regras críticas mantidas: código sempre completo (não diff parcial); handoff completo ao chegar em 70–80% do contexto; avisar sobre limite do chat e limite do site/IA (o segundo não é mensurável pelo assistente — declarar essa limitação); percentual de prontidão ao final; seguir as recomendações do assistente como plano padrão.

Adições da S47 (mantidas, importantes):

    S47a — Para arquivo não recebido inteiro, entregar apenas regra de substituição (Ctrl+F), nunca arquivo completo. Se essencial, pedir Get-Content inteiro antes. (A S47 violou isso uma vez; não repetir.)

    S47b — Padrão de injeção do AuthService: main.dart instancia final AuthService _auth = AuthService(); e injeta por construtor em todos os pages (LoginPage(auth: _auth), FeedPage(auth: _auth), etc.). Não há Provider, não há AuthService.instance, não há context.read. Usar widget.auth no State.

    S47c — pytest exige o container Docker de teste. Sem ele: ConnectionRefusedError em tests/conftest.py:77. conftest.py aponta para postgresql+asyncpg://rumo:rumo@localhost:5433/rumo_test (porta 5433, não 5432). Container: rumo_postgres_test, definido em backend/docker-compose.test.yml. Comando: docker compose -f docker-compose.test.yml up -d.

    S47d — Docker Desktop instalado e rodando. Containers ativos: rumo-postgres (postgis/postgis:16-3.4, 5432) e rumo-redis (redis:7-alpine, 6379). Container de teste (rumo_postgres_test, 5433) sobe sob demanda. Postgres 12 nativo instalado mas parado — não usar.

    S47e — api.dart lança ApiException(0, 'Falha de rede no upload: $e') e ApiException(0, 'Falha de rede no export: $e') em timeouts de upload/export. O tradutor trata statusCode == 0 como "sem conexão".

    S47f — ApiException contrato: class ApiException implements Exception { final int statusCode; final String message; ApiException(this.statusCode, this.message); }.

    S47g — AuthService extends ChangeNotifier com login, logout, bootstrap, currentUserId, token, isLoggedIn, loading, api (getter que expõe ApiClient). Não é singleton. Toda a árvore recebe a mesma instância via construtor (S47b).

Adições da S48 (NOVAS):

    S48a — Arquivos grandes (> 600 linhas) devem ser colados/devolvidos em 3 partes (-First 400 / -Skip 400 -First 400 / -Skip 800), não 2. Funcionou bem no profile_page.dart (1035 linhas) e user_profile_page.dart (1051 linhas). Para 250–600 linhas: 2 partes. Para < 250: inteiro.

    S48b — friendlyErrorMessage deve ser aplicado com julgamento de contexto, não cegamente. Não traduzir: catch (_) silencioso, .catchError que devolve null (rollback por design), tratamento de 403 como estado (_activitiesForbidden, _statsForbidden), mensagens locais específicas (validação, "Sessão sem id de usuário", "Siga pra ver..."). Traduzir só o que exibe erro de API/rede ao usuário.

    S48c — Falso positivo registrado: em edit_profile_page.dart, o PUT /users/me só aceita weight_kg, height_cm, full_name — não há 409 de username nesse fluxo. O tradutor pode ser usado sem risco ali. (O alerta levantado antes de ler o arquivo era falso; verificar sempre antes de assumir.)

    S48d — O error_message.dart mapeia 409 → "Este e-mail já está cadastrado.". Atenção futura: se algum fluxo (ex.: 10.2 cadastro, ou edição de username) puder gerar 409 de username, o tradutor produziria mensagem errada. Nesses fluxos, preservar e.message para 409 ou ajustar o tradutor com um parâmetro de contexto. Não é problema hoje (nenhum fluxo atual de escrita toca username/email), mas registrar.

    S48e — O handoff S47 dizia "A S47 fechou sem commit", mas o commit 2e14673 já existia. Lição: o handoff é documento, não fonte de verdade do repo. Sempre verificar com git log/git status antes de agir (foi o que a S48 fez — e evitou recommitar).

SEÇÃO 1 — TL;DR para quem chega agora

Estado do repo: HEAD == origin/main == 07a3301 (commit do handoff S47). Working tree tem 8 arquivos modificados não commitados (os 7 pages do 10.1 + o edit_profile_page.dart; o feed_page.dart foi o 1º, os outros 6 vieram depois):
text

 M mobile/lib/pages/feed_page.dart
 M mobile/lib/pages/activity_detail_page.dart
 M mobile/lib/pages/upload_page.dart
 M mobile/lib/pages/profile_page.dart
 M mobile/lib/pages/user_profile_page.dart
 M mobile/lib/pages/search_page.dart
 M mobile/lib/pages/edit_profile_page.dart

(na prática, 7 arquivos — o feed_page.dart é o 1º da lista; conferir com git status --short --untracked-files=all antes do commit.)

Ação imediata da S49: commitar os 7 pages (Seção 5, comando exato).

S48 fez:

    Fase 0 completa verde (mobile analyze, web build/lint, backend 180 pytest + ruff, prod 200/200).

    Item 10.1 COMPLETO — friendlyErrorMessage aplicado nos 7 pages restantes, com julgamento de contexto (S48b). Cada arquivo validado com flutter analyze → No issues found!.

    NÃO commitou o 10.1 (deixado para a S49, junto com o handoff da S48).

S48 NÃO fez (fica para S49):

    Commit do 10.1 (7 arquivos) + commit do handoff da S48.

    Item 10.2 (tela de cadastro) — requer verificar se o backend tem POST /auth/register.

    Item 10.4 (melhorias incrementais: spinner em botões que faltam, empty states, pull-to-refresh, tratamento global de 401).

    Itens herdados da S46: item 7 (validação no Redmi Note 8), item 8 (splash + ícone), item 10 (keystore + signingConfigs), item 13 (remover BOM de build.gradle.kts e AndroidManifest.xml).

Percentual consolidado: ~87% (mobile subiu de ~94% para ~95%; os 7 pages verdes fecham o 10.1).
SEÇÃO 2 — PRODUÇÃO E AMBIENTE

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

    Docker Desktop: instalado e rodando. Containers: rumo-postgres (postgis/postgis:16-3.4, 5432), rumo-redis (redis:7-alpine, 6379), rumo_postgres_test (postgis/postgis:16-3.4, 5433 — sob demanda para pytest).

Git ao fim da S48 (esperado após commit da S49):
text

<novo_hash>  (HEAD -> main, origin/main) feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo)
07a3301  docs: atualiza handoff S47 refletindo o commit 2e14673 e corrige status do commit da S47
2e14673  feat(mobile): tradutor de erros amigaveis + login usando friendlyErrorMessage (Sessao 47, 10.1 parcial)
9d93e95  docs: adiciona backlog da Sessao 47 no handoff (erros amigaveis, cadastro, animacao de rota)
0898e5e  fix(mobile): app roda no celular real + permissao INTERNET + overflow corrigido + .gitignore Flutter (Sessao 46)
...

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 48
3.1 Fase 0 — tudo verde

    Mobile flutter analyze: No issues found! (4.0s)

    Web npm run build: ✓ built in 2.19s (826 módulos)

    Web npm run lint: 0 erros

    Backend container: rumo_postgres_test running

    Backend pytest -q: 180 passed in 46.71s

    Backend ruff check .: All checks passed!

    Prod backend /health: 200

    Prod frontend /: 200

3.2 Item 10.1 — os 7 pages (todos verdes)
#	Arquivo	Linhas	Edições (// [S48-10.1])	Não tocados (por design)
1	feed_page.dart	163	import + 2 catches (_load)	catch (_) do _openDetail (silencioso)
2	activity_detail_page.dart	625	import + 12 catches (_load, _loadComments, _loadTrack, _export, _submitComment, _deleteComment) + _showError recebe String (tradução no caller)	if (track == null) return const [] (404 silencioso)
3	upload_page.dart	215	import + 2 catches (_submit)	catches de _pickFile (validações locais) e leitura de arquivo
4	profile_page.dart	1035	import + 2 (_load) + 1 (_loadStats, ramo não-403) + 2 (_loadMore) + 2 (_exportAll)	.catchError dos stats (rollback), catch (_) do _openDetail, _logout (sem catch)
5	user_profile_page.dart	1051	import + 2 (_load) + 1 ramo não-403 (_loadStats) + 2 (_loadLists) + 2 (_loadMore) + 2 (_toggleFollow)	.catchError de 403 (_Stats403), _reloadActivities/_openDetail (silenciosos), mensagens de 403 ("Siga pra ver...")
6	search_page.dart	445	import + 2 (_UserSearchTab._runSearch) + 2 (_ActivitySearchTab._runSearch)	debounce/Timer, empty states, _clear
7	edit_profile_page.dart	351	import + 2 (_save)	validadores locais (Peso..., Altura..., Nome...), _buildBody, _NumberField

Padrão aplicado: import '../utils/error_message.dart'; + friendlyErrorMessage(e) nos catches que exibem erro de API/rede. Preservados: silenciosos, rollback, 403 como estado, mensagens locais. Construtor S47b intacto em todos.

Validação: cada um passou flutter analyze → No issues found! imediatamente após a substituição. Nenhum retrabalho.
3.3 Commits da S48

    07a3301 — docs: atualiza handoff S47 refletindo o commit 2e14673 e corrige status do commit da S47 (commit do handoff S47, feito no início da S48). Feito.

    Pendente: commit do 10.1 (7 arquivos) + commit do handoff S48. Ver Seção 5.

SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)

Nenhuma mudança desde S39. 180 testes passando. ApiException.message já contém o detail do FastAPI. O tradutor só formata o que já existe — não modifica o api.dart. Contrato relevante: PUT /users/me aceita weight_kg?, height_cm?, full_name? (exclude_unset) — sem username/email/birth_date (S48c).
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Ação imediata da S49 (primeira coisa):
powershell

cd D:\Rumo

# 1) Confirmar o que vai entrar (devem ser 7 arquivos de page + o handoff se já colado)
git status --short --untracked-files=all

# 2) Stage explícito dos 7 pages (NÃO usar git add -A)
git add mobile/lib/pages/feed_page.dart
git add mobile/lib/pages/activity_detail_page.dart
git add mobile/lib/pages/upload_page.dart
git add mobile/lib/pages/profile_page.dart
git add mobile/lib/pages/user_profile_page.dart
git add mobile/lib/pages/search_page.dart
git add mobile/lib/pages/edit_profile_page.dart

# 3) Commit do 10.1
git commit -m "feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo)"

# 4) Push
git push

Depois (commit do handoff S48): quando você colar o handoff da S48 em docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 48 (10.1 completo, licoes S48a-e)"
git push

O que espero ver em git status --short antes do commit do 10.1: exatamente 7 linhas M mobile/lib/pages/*.dart. Se aparecer ?? cls ou outro untracked, não commitar — investigar primeiro (aconteceu na S48: cls acidental do PowerShell; removido).
SEÇÃO 6 — SCRIPTS ÚTEIS (S48)

Subir o container de teste (obrigatório antes do pytest):
powershell

cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
# aguardar ~3s; depois:
.\venv\Scripts\Activate.ps1
python -m pytest -q
# Esperado: 180 passed

Rodar flutter analyze após editar arquivo mobile:
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
# Esperado: No issues found!

Verificar estado do repo antes de qualquer commit:
powershell

cd D:\Rumo
git log --oneline -5
git status --short --untracked-files=all

Para os próximos arquivos (processo S48a):

    < 250 linhas: Get-Content <arquivo> -Encoding UTF8 (inteiro).

    250–600 linhas: 2 partes (-First 250 / -Skip 250).

        600 linhas: 3 partes (-First 400 / -Skip 400 -First 400 / -Skip 800).

SEÇÃO 7 — DÍVIDAS TÉCNICAS (S48)

Fechadas na S48:

    (S47) Item 10.1 completo — friendlyErrorMessage nos 7 pages. ✅

    (S47) Handoff S47 commitado (07a3301). ✅

Conhecidas (não-bug):

    (S41) prod@rumo.com state — estado, não bug.

    (S42k) PWA sem PNGs — não-bloqueador.

    (S43d) BOM em build.gradle.kts e AndroidManifest.xml — não-bloqueador (item 13).

    (S43e) Info.plist sem hardcode — correto.

    (S44) Dois commits de handoff S44 com a mesma mensagem — cosmético, não reescrever histórico.

Oportunidades (S49+):

    (S48d) error_message.dart mapeia 409 → "Este e-mail já está cadastrado." Se algum fluxo futuro gerar 409 de username, ajustar (parâmetro de contexto ou preservar e.message). Não é problema hoje.

    (S47) Container Docker de teste não está no README — considerar documentar.

    (S46) Item 10.2: tela de cadastro (verificar POST /auth/register no backend).

    (S46) Item 10.3: animação do mapa (Polyline progressiva via AnimationController).

    (S46) Item 10.4: spinner em botões que faltam, empty states, pull-to-refresh, tratamento global de 401 com redirecionamento.

    (S46) Item 7 completo: validar feed/perfil/upload/like/comentários/export no Redmi Note 8.

    (S46) Item 8: splash + ícone no launcher.

    (S46) Item 10: keystore + signingConfigs.

    (S46) Item 13: remover BOM de build.gradle.kts e AndroidManifest.xml.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 49)

Primeira ação (obrigatória): commit do 10.1 (Seção 5).

Segunda ação (Fase 0 padrão): git log/git status, web build/lint, mobile analyze, backend pytest (com container), ruff, prod health/frontend. (Ver Seção 6.)

Terceira ação — escolher entre (ordem recomendada):

    Item 10.2 — Tela de Cadastro (prioridade alta). Pré-requisito: verificar se o backend tem POST /auth/register:
    powershell

    cd D:\Rumo\backend
    Get-ChildItem app\routers -Filter *.py | Select-String -Pattern "register|/auth" -List
    Get-Content app\routers\auth.py -Encoding UTF8 -ErrorAction SilentlyContinue

        Se existir: criar lib/pages/register_page.dart (nome completo, username, e-mail, senha, confirmação; validação local; spinner; link "Já tem conta? Entre"). Adicionar rota /register no main.dart e link na login_page.dart. Atenção S48d: 409 de username/e-mail — preservar e.message ou ajustar tradutor.

        Se não existir: criar no backend primeiro (S49 ou S50) e depois a tela.

    Item 10.4 — Melhorias incrementais (prioridade média): spinner em botões que faltam (like, upload, cadastro), empty states amigáveis (feed vazio, perfil sem atividades, busca sem resultados), pull-to-refresh no feed/perfil, tratamento global de 401 com redirecionamento (cuidado: toca navegação; testar bem).

    Item 7 completo — validação no Redmi Note 8 (prioridade alta se for submeter em breve): feed/perfil/upload/like/comentários/export.

    Item 8 — splash + ícone no launcher.

    Item 10 — keystore + signingConfigs (só após item 7 completo).

Ordem sugerida: 10.2 (se backend tiver endpoint) → 10.4 → item 7 → item 8 → item 10.
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S48)

    S21–S47: acordos mantidos (código completo, handoff completo, aviso de limite, percentual).

    S47: o usuário pediu explicitamente: "sempre seguir suas recomendações"; "sempre colocar o código completo"; "fazer o handoff completo e bem explicado quando o limite estiver próximo de 70%–80%"; "informar o percentual de quanto o projeto está pronto"; "avisar se o chat/site for acabar no meio do código — não só limite do chat, mas limite do site (IA)".

    S48: o usuário reforçou o aviso de limite ("cuidado com limite do chat para não ficar na mão sem o handoff") quando o contexto estava em ~65–70%, antes de colar o edit_profile_page.dart. O assistente avisou o ponto de risco e prometeu handoff imediatamente após o 10.1 — cumprido (este handoff).

    S48 — decisão de fechamento: ao chegar em ~70–75%, o assistente entregou o último arquivo do 10.1 e, com o flutter analyze verde, parou e fez o handoff, sem tentar 10.2/10.4. Em linha com o acordo.

Acordos novos da S48: S48a–S48e (ver Seção 0).
SEÇÃO 10 — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 48)
Área	%	Observação
Backend	~95%	inalterado (180 testes, ruff, prod 200)
Web	~99%	inalterado (build + lint, prod 200)
Mobile	~95%	subiu de ~94% (10.1 completo: 7 pages com friendlyErrorMessage)
Bloqueadores não-código	~25%	inalterado (contas Google Play/Apple, keystore)
MVP consolidado	~87%	subiu de ~86% (10.1 fechado)

Variação em relação à S47: Mobile 94% → 95% (+1%); MVP 86% → 87% (+1%).

Estimativa até "pronto para submeter":

    10.2 cadastro: ~1 sessão (se backend tiver endpoint; +1 se precisar criar endpoint).

    10.4 incremental: ~1 sessão.

    Item 7 (validação no celular): ~1 sessão.

    Item 8 (splash/ícone) + item 10 (keystore): ~1 sessão.

    Total: ~4–5 sessões + 1–2 de review. ~5–7 sessões.

SEÇÃO 11 — BACKLOG DA SESSÃO 49 (planejamento)

Base: repo em <novo_hash> (após commit do 10.1) — os 7 pages já commitados.

11.1 Commit do 10.1 (obrigatório, primeira coisa). Ver Seção 5.

11.2 Item 10.2 — Tela de Cadastro (prioridade alta). Ver Seção 8, item 1. Verificar POST /auth/register antes. Atenção S48d (409).

11.3 Item 10.4 — Melhorias incrementais (prioridade média). Spinner, empty states, pull-to-refresh, 401 global.

11.4 Itens herdados da S46 (não concluídos). Item 7, 8, 10, 13.

11.5 Ordem sugerida para a S49: Fase 0 → commit do 10.1 → 10.2 → 10.4 → item 7 → item 8 → item 10.
RESUMO EXECUTIVO PARA A S49

    Primeiro: commit dos 7 pages do 10.1 (Seção 5) — feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo).

    Depois: Fase 0 completa (Seção 6).

    Em seguida: 10.2 (cadastro — verificar endpoint primeiro), 10.4 (incremental), item 7 (celular).

    O que NÃO fazer: reconstruir arquivo a partir de Select-String (S47a); assumir AuthService.instance (S47b); rodar pytest sem container (S47c); traduzir catch (_) silencioso/rollback/403 como erro (S48b); confiar no handoff sem git log/git status (S48e).

    Regra de ouro: não tenho acesso ao disco. Pedir Get-Content inteiro. Nunca inventar caminho. Nunca reescrever arquivo não recebido.

Percentual de prontidão (fim da S48)
Área	%
Backend	~95%
Web	~99%
Mobile	~95%
Bloqueadores não-código	~25%
MVP consolidado	~87%

Sessão 48 fechada. 10.1 completo. Handoff entregue. Próxima ação da S49: commitar o 10.1 (Seção 5) e seguir para o 10.2.