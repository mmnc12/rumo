HANDOFF — SESSÃO 49 (para a Sessão 50)
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro (S21–S49, inalterada): Você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho. Nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

Regras críticas mantidas: código sempre completo (não diff parcial); handoff completo ao chegar em 70–80% do contexto; avisar sobre limite do chat e limite do site/IA (o segundo não é mensurável pelo assistente — declarar essa limitação); percentual de prontidão ao final; seguir as recomendações do assistente como plano padrão.
Adições S47 (mantidas)

    S47a — Para arquivo não recebido inteiro, entregar apenas regra de substituição (Ctrl+F). Se essencial, pedir Get-Content inteiro antes. Se recebido inteiro (mesmo em partes), pode entregar completo — foi o caso do api.dart na S49 (recebido em 3 partes, entregue completo).

    S47b — AuthService injetado por construtor (LoginPage(auth: _auth)), não singleton. widget.auth no State.

    S47c — pytest exige container rumo_postgres_test (porta 5433). Sem ele: ConnectionRefusedError em tests/conftest.py:77.

    S47d — Docker Desktop rodando; rumo-postgres (5432), rumo-redis (6379) ativos.

    S47e — ApiException(0, ...) em timeouts de upload/export; tradutor trata statusCode == 0 como "sem conexão".

    S47f — ApiException { int statusCode; String message; }.

    S47g — AuthService extends ChangeNotifier com login, logout, bootstrap, currentUserId, token, isLoggedIn, loading, api getter.

Adições S48 (mantidas)

    S48a — >600 linhas: 3 partes na leitura (-First 400 / -Skip 400 -First 400 / -Skip 800); 250–600: 2 partes; <250: inteiro.

    S48b — friendlyErrorMessage com julgamento: não traduzir catch (_) silencioso, rollback, 403 como estado, mensagens locais.

    S48c — Verificar antes de assumir (falso positivo do 409 em edit_profile_page.dart).

    S48d — error_message.dart mapeia 409 cego → "Este e-mail já está cadastrado.". ATIVADA na S49: o register tem 409 de email e username. Solução aplicada: na RegisterPage, tratar 409 antes do tradutor e mostrar e.message direto.

    S48e — Handoff é documento, não fonte de verdade. Sempre verificar git log / git status antes de agir.

Adições S49 (NOVAS)

    S49a — Em Dart 3.9+, map literal com if (x != null) 'k': x gera lint use_null_aware_elements. Preferir ?'k': x (null-aware) ou montar o map base e adicionar opcionais com if fora do literal.

    S49b — O operador null-aware de elemento de map tem duas formas: ?key: value (chave, omite se chave null) e key: ?value (valor, omite se valor null). Para valor opcional, é key: ?value — não ?key: value. Com expressão condicional, parênteses obrigatórios: key: ?(cond ? a : null). Alternativa recomendada e à prova de lint: map base + body['k'] = v com if fora do literal.

    S49c — O redirect do main.dart precisa incluir /register como "auth page" (goingToAuthPage = matchedLocation == '/login' || matchedLocation == '/register'). Sem isso, /register cai em loop para /login. Aplicado na S49.

    S49d — POST /auth/register existe no backend (confirmado na S49): app/routers/auth.py, @limiter.limit("3/hour"), 409 com detail = "Email já cadastrado" ou "Username já cadastrado" (dois detail diferentes no mesmo 409). Schema UserCreate em app/schemas/user.py (pacote, não módulo único).

SEÇÃO 1 — TL;DR para quem chega agora

Estado do repo: HEAD == origin/main == 76e6cce (commit do handoff S48). Working tree tem 5 arquivos não commitados do 10.2:
text

 M mobile/lib/main.dart
 M mobile/lib/pages/login_page.dart
 M mobile/lib/services/api.dart
 M mobile/lib/services/auth_service.dart
?? mobile/lib/pages/register_page.dart

Ação imediata da S50: commitar o 10.2 (Seção 5, comando exato) + o handoff da S49.

S49 fez:

    Fase 0 completa verde (mobile analyze, web build/lint, backend 180 pytest + ruff).

    Item 10.2 COMPLETO — tela de cadastro, rota /register, redirect corrigido, link no login, api.register + auth.register.

    flutter analyze verde nos 5 arquivos.

    NÃO commitou o 10.2 (deixado para a S50, junto com este handoff).

S49 NÃO fez (fica para S50):

    Commit do 10.2 (5 arquivos) + commit deste handoff.

    Item 10.4 (melhorias incrementais: spinner em botões que faltam, empty states, pull-to-refresh, tratamento global de 401).

    Itens herdados da S46: item 7 (validação no Redmi Note 8), item 8 (splash + ícone), item 10 (keystore + signingConfigs), item 13 (remover BOM de build.gradle.kts e AndroidManifest.xml).

Percentual consolidado: ~90% (mobile subiu de ~95% para ~97%; 10.2 fechado).
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

    Docker Desktop: instalado e rodando. rumo-postgres (postgis/postgis:16-3.4, 5432), rumo-redis (redis:7-alpine, 6379), rumo_postgres_test (postgis/postgis:16-3.4, 5433 — sob demanda).

Git ao fim da S49 (esperado após commit da S50):
text

<novo_hash>  (HEAD -> main, origin/main) feat(mobile): tela de cadastro + rota /register + register no ApiClient/AuthService (Sessao 49, 10.2 completo)
76e6cce  docs: handoff da Sessao 48 (10.1 completo, licoes S48a-e)
c3447c2  feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo)
07a3301  docs: atualiza handoff S47 refletindo o commit 2e14673 e corrige status do commit da S47
2e14673  feat(mobile): tradutor de erros amigaveis + login usando friendlyErrorMessage (Sessao 47, 10.1 parcial)

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 49
3.1 Fase 0 — tudo verde
Verificação	Resultado
flutter analyze	No issues found! (4.0s)
npm run build	✓ built in 2.14s (826 módulos)
npm run lint	0 erros
docker compose -f docker-compose.test.yml up -d	rumo_postgres_test Running
pytest -q	180 passed in 48.54s
ruff check .	All checks passed!
Prod backend /health	não verificado na S49 (não bloqueou; nada mudou desde S48)
Prod frontend /	não verificado na S49 (idem)
3.2 Item 10.2 — Tela de Cadastro (COMPLETO, 5 arquivos verdes)
#	Arquivo	Tipo	Mudança
1	lib/services/api.dart	modificado	+método register(...) (~40 linhas) antes de // ---------- internos ----------. Usa post('/auth/register', body: ...) + UserMe.fromJson.
2	lib/services/auth_service.dart	modificado	+método register(...) (~25 linhas): chama _api.register(...) e, no sucesso, login(email, password) (login automático).
3	lib/pages/register_page.dart	novo	~280 linhas. Form com email, username, full_name (opc), password, confirmação + ExpansionTile com weight/height/birth_date (opc). Validação local espelhando UserCreate. Spinner. 409 → e.message direto (S48d). Sucesso → context.go('/feed').
4	lib/main.dart	modificado	+import register_page.dart; redirect ajustado (goingToAuthPage cobre /login e /register); +GoRoute('/register') entre /login e /upload.
5	lib/pages/login_page.dart	modificado	+TextButton "Não tem conta? Criar conta" → context.go('/register').

Validação: cada arquivo passou flutter analyze imediatamente após a substituição. O api.dart deu 2 lints use_null_aware_elements (S49a/S49b) — corrigido com map base + if fora do literal. No issues found! final (2.6s).
3.3 Commits da S49

    Nenhum. Tudo pendente (Seção 5).

SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS + 1 NOVO CONFIRMADO)

Nenhuma mudança de código no backend desde S39. 180 testes passando. Contratos relevantes:

    POST /auth/register (novo confirmado na S49, já existia): público, @limiter.limit("3/hour"). Body = UserCreate (email, username, password, full_name?, weight_kg?, height_cm?, birth_date?). 201 → UserResponse. 409 com dois detail diferentes: "Email já cadastrado" / "Username já cadastrado". 422 validação. 429 rate limit.

    PUT /users/me aceita weight_kg?, height_cm?, full_name? (sem username/email/birth_date — S48c).

    ApiException.message já contém o detail do FastAPI. O tradutor só formata o que já existe.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Ação imediata da S50 (primeira coisa):
powershell

cd D:\Rumo
# 1) Confirmar o que vai entrar (5 arquivos do 10.2 + o handoff se já colado)
git status --short --untracked-files=all

# 2) Stage explícito (NÃO usar git add -A)
git add mobile/lib/main.dart
git add mobile/lib/pages/login_page.dart
git add mobile/lib/pages/register_page.dart
git add mobile/lib/services/api.dart
git add mobile/lib/services/auth_service.dart

# 3) Commit do 10.2
git commit -m "feat(mobile): tela de cadastro + rota /register + register no ApiClient/AuthService (Sessao 49, 10.2 completo)"

# 4) Push
git push

Depois (commit deste handoff): quando você colar o handoff da S49 em docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 49 (10.2 completo, licoes S49a-d)"
git push

O que espero ver em git status --short antes do commit do 10.2: exatamente 4 linhas M + 1 linha ?? (register_page.dart). Se aparecer ?? cls ou outro untracked, não commitar — investigar primeiro (S48: cls acidental do PowerShell). S48e: verificar sempre; o handoff é documento, não fonte de verdade.
SEÇÃO 6 — SCRIPTS ÚTEIS

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

    <250 linhas: Get-Content <arquivo> -Encoding UTF8 (inteiro).

    250–600 linhas: 2 partes (-First 250 / -Skip 250).

        600 linhas: 3 partes (-First 400 / -Skip 400 -First 400 / -Skip 800).

SEÇÃO 7 — DÍVIDAS TÉCNICAS

Fechadas na S49:

    (S46) Item 10.2 — Tela de Cadastro. ✅

Conhecidas (não-bug):

    (S41) prod@rumo.com state — estado, não bug.

    (S42k) PWA sem PNGs — não-bloqueador.

    (S43d) BOM em build.gradle.kts e AndroidManifest.xml — não-bloqueador (item 13).

    (S43e) Info.plist sem hardcode — correto.

    (S44) Dois commits de handoff S44 com a mesma mensagem — cosmético, não reescrever histórico.

Oportunidades (S50+):

    (S48d) error_message.dart mapeia 409 cego → "Este e-mail já está cadastrado.". Não é problema hoje (o register trata 409 antes do tradutor; nenhum outro fluxo toca username/email). Se um fluxo futuro gerar 409 de username fora do register, ajustar (parâmetro de contexto ou preservar e.message).

    (S47) Container Docker de teste não está no README — considerar documentar.

    (S46) Item 10.4: spinner em botões que faltam, empty states, pull-to-refresh, tratamento global de 401 com redirecionamento.

    (S46) Item 7 completo: validar feed/perfil/upload/like/comentários/export + cadastro no Redmi Note 8.

    (S46) Item 8: splash + ícone no launcher.

    (S46) Item 10: keystore + signingConfigs.

    (S46) Item 13: remover BOM de build.gradle.kts e AndroidManifest.xml.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 50)

Primeira ação (obrigatória): commit do 10.2 (Seção 5).

Segunda ação (Fase 0 padrão): git log/git status, web build/lint, mobile analyze, backend pytest (com container), ruff, prod health/frontend (verificar — não foi feito na S49). (Ver Seção 6.)

Terceira ação — escolher entre (ordem recomendada):

    Item 10.4 — Melhorias incrementais (prioridade alta, ~1 sessão):

        Spinner em botões que faltam (like, upload — cadastro já tem).

        Empty states amigáveis (feed vazio, perfil sem atividades, busca sem resultados).

        Pull-to-refresh no feed/perfil.

        Tratamento global de 401 com redirecionamento (cuidado: toca navegação; testar bem).

    Item 7 completo — validação no Redmi Note 8 (prioridade alta se for submeter em breve, ~1 sessão):

        Feed, perfil, upload, like, comentários, export, cadastro (novo).

        Atenção: rate limit do register é 3/hora por IP — se testar muitas vezes, pode bater no limite.

    Item 8 — splash + ícone no launcher (~0,5 sessão).

    Item 10 — keystore + signingConfigs (só após item 7 completo, ~0,5 sessão).

Ordem sugerida: 10.4 → item 7 → item 8 → item 10.
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S49)

    S21–S48: acordos mantidos (código completo, handoff completo, aviso de limite, percentual, seguir recomendações).

    S49: o usuário reforçou: "sempre colocar o código completo" (cobrou quando eu entreguei api.dart como regra de substituição — S49 ajustou: como o arquivo foi recebido inteiro, entreguei completo, em linha com S47a). "Sempre seguir suas recomendações". "Fazer o handoff completo quando o limite estiver próximo de 70–80%". "Informar o percentual de prontidão no final". "Avisar sobre limite do chat e limite do site/IA" — com a ressalva honesta de que o limite do site/IA não é mensurável pelo assistente.

    S49 — decisão de fechamento: ao chegar em ~75–80%, o assistente entregou o último arquivo do 10.2 (login_page.dart), confirmou flutter analyze verde e parou para o handoff, sem tentar 10.4 nem item 7. Em linha com o acordo.

Acordos novos da S49: S49a–S49d (ver Seção 0).
SEÇÃO 10 — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 49)
Área	%	Observação
Backend	~95%	inalterado (180 testes, ruff; prod não verificado na S49 mas sem mudança)
Web	~99%	inalterado
Mobile	~97%	subiu de ~95% (10.2 completo: cadastro + rota + register)
Bloqueadores não-código	~25%	inalterado (contas Google Play/Apple, keystore)
MVP consolidado	~90%	subiu de ~87% (10.2 fechado)

Variação em relação à S48: Mobile 95% → 97% (+2%); MVP 87% → 90% (+3%).

Estimativa até "pronto para submeter":

    10.4 incremental: ~1 sessão.

    Item 7 (validação no celular, incl. cadastro): ~1 sessão.

    Item 8 (splash/ícone) + item 10 (keystore): ~1 sessão.

    Total: ~3–4 sessões + 1 de review. ~4–5 sessões.

SEÇÃO 11 — BACKLOG DA SESSÃO 50 (planejamento)

Base: repo em <novo_hash> (após commit do 10.2) — os 5 arquivos já commitados.

    Commit do 10.2 (obrigatório, primeira coisa). Ver Seção 5.

    Item 10.4 — Melhorias incrementais (prioridade alta). Spinner, empty states, pull-to-refresh, 401 global.

    Item 7 — validação no Redmi Note 8 (prioridade alta). Incluir cadastro; atenção ao rate limit 3/h.

    Itens herdados da S46. Item 8 (splash/ícone), item 10 (keystore), item 13 (BOM).

    Ordem sugerida para a S50: Fase 0 (com prod health/frontend) → commit do 10.2 → 10.4 → item 7 → item 8 → item 10.

RESUMO EXECUTIVO PARA A S50

    Primeiro: commit dos 5 arquivos do 10.2 (Seção 5) — feat(mobile): tela de cadastro + rota /register + register no ApiClient/AuthService (Sessao 49, 10.2 completo).

    Depois: Fase 0 completa (Seção 6), incluindo prod health/frontend (não verificado na S49).

    Em seguida: 10.4 (incremental) → item 7 (celular, incl. cadastro) → item 8 → item 10.

    O que NÃO fazer: reconstruir arquivo a partir de Select-String (S47a); assumir AuthService.instance (S47b); rodar pytest sem container (S47c); traduzir catch (_) silencioso/rollback/403 como erro (S48b); confiar no handoff sem git log/git status (S48e); usar ?key: value para valor opcional em map literal (S49b — é key: ?value); esquecer de incluir /register no redirect do main.dart (S49c).

    Regra de ouro: não tenho acesso ao disco. Pedir Get-Content inteiro. Nunca inventar caminho. Nunca reescrever arquivo não recebido.

Percentual de prontidão (fim da S49): Backend ~95% · Web ~99% · Mobile ~97% · Bloqueadores não-código ~25% · MVP consolidado ~90%