HANDOFF — SESSÃO 50 (para a Sessão 51)
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro (S21–S50, inalterada): Você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho. Nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

Regras críticas mantidas: código sempre completo (não diff parcial); handoff completo ao chegar em 70–80% do contexto; avisar sobre limite do chat e limite do site/IA (o segundo não é mensurável pelo assistente — declarar essa limitação); percentual de prontidão ao final; seguir as recomendações do assistente como plano padrão.

Adições S47 (mantidas):

    S47a — Arquivo não recebido inteiro → entregar só regra de substituição (Ctrl+F). Se essencial, pedir Get-Content inteiro antes. Se recebido inteiro (mesmo em partes), pode entregar completo.

    S47b — AuthService injetado por construtor (LoginPage(auth: _auth)), não singleton. widget.auth no State.

    S47c — pytest exige container rumo_postgres_test (porta 5433). Sem ele: ConnectionRefusedError em tests/conftest.py:77.

    S47d — Docker Desktop rodando; rumo-postgres (5432), rumo-redis (6379) ativos.

    S47e — ApiException(0, ...) em timeouts de upload/export; tradutor trata statusCode == 0 como "sem conexão".

    S47f — ApiException { int statusCode; String message; }.

    S47g — AuthService extends ChangeNotifier com login, logout, bootstrap, currentUserId, token, isLoggedIn, loading, api getter.

Adições S48 (mantidas):

    S48a — >600 linhas: 3 partes na leitura; 250–600: 2 partes; <250: inteiro.

    S48b — friendlyErrorMessage com julgamento: não traduzir catch (_) silencioso, rollback, 403 como estado, mensagens locais.

    S48c — Verificar antes de assumir (falso positivo do 409 em edit_profile_page.dart).

    S48d — error_message.dart mapeia 409 cego → "Este e-mail já está cadastrado.". Na RegisterPage, tratar 409 antes do tradutor e mostrar e.message direto.

    S48e — Handoff é documento, não fonte de verdade. Sempre verificar git log / git status antes de agir.

Adições S49 (mantidas):

    S49a — Em Dart 3.9+, map literal com if (x != null) 'k': x gera lint use_null_aware_elements. Preferir ?'k': x (null-aware) ou montar o map base e adicionar opcionais com if fora do literal.

    S49b — Operador null-aware de elemento de map tem duas formas: ?key: value (chave, omite se chave null) e key: ?value (valor, omite se valor null). Para valor opcional, é key: ?value — não ?key: value. Com expressão condicional, parênteses obrigatórios: key: ?(cond ? a : null). Alternativa recomendada e à prova de lint: map base + body['k'] = v com if fora do literal.

    S49c — O redirect do main.dart precisa incluir /register como "auth page" (goingToAuthPage = matchedLocation == '/login' || matchedLocation == '/register'). Sem isso, /register cai em loop para /login.

    S49d — POST /auth/register existe no backend: app/routers/auth.py, @limiter.limit("3/hour"), 409 com detail = "Email já cadastrado" ou "Username já cadastrado" (dois detail diferentes no mesmo 409). Schema UserCreate em app/schemas/user.py (pacote, não módulo único).

Adições S50 (NOVAS):

    S50a — Get-Content do PowerShell 5.1 NÃO tem -Skip como parâmetro nomeado. Get-Content arquivo -Skip N falha com ParameterBindingException. O comando correto é Get-Content arquivo -Encoding UTF8 | Select-Object -Skip N -First M (ou sem -First para ir até o fim). O -First N do Get-Content funciona (é parâmetro válido), mas -Skip não. Corrigir no handoff S48a: a intenção (3 partes) está certa, mas o comando concreto precisa ser com | Select-Object.

    S50b — upload_page.dart já tinha spinner no botão de upload (feito provavelmente na S31). O item "spinner no upload" do 10.4 estava completo antes da S50. Não foi tocado. FilledButton.icon com _submitting ? spinner : Icon, label: _submitting ? 'Enviando...' : 'Enviar', canSubmit = hasFile && !_submitting, TextField.enabled = !_submitting, IconButton de remover some durante o envio.

    S50c — ProfilePage é self-only. O comentário na seção de export confirma: "a tela ProfilePage é sempre self; o perfil de terceiro é o UserProfilePage, arquivo 6". CTA "Enviar atividade" no empty state do perfil faz sentido (não é perfil alheio). _openUpload() foi criado novo no ProfilePage (não existia).

    S50d — FeedPage já tinha RefreshIndicator (pull-to-refresh) e retry de erro. O item 10.4 "pull-to-refresh no feed" estava completo antes da S50. Idem ProfilePage (RefreshIndicator + _refreshAll()). Onda B (pull-to-refresh) provavelmente não tem nada a fazer — verificar antes de assumir.

    S50e — Empty state do feed/perfil/busca: convenção adotada. Ícone 64 (feed/perfil) ou 48 (busca), onSurfaceVariant, título titleMedium, subtítulo bodyMedium, textAlign: TextAlign.center. No feed/perfil: CTA FilledButton.icon "Enviar atividade" → _openUpload(). Na busca: sem CTA (busca vazia não tem ação óbvia). Empty state do feed/perfil fica dentro do ListView (não Center de tela cheia) para não quebrar o RefreshIndicator. Na busca, o _buildBody retorna Center (não tem RefreshIndicator).

SEÇÃO 1 — TL;DR para quem chega agora

Estado do repo: HEAD == origin/main == 82d58de (handoff S49). Working tree tem 4 arquivos modificados (do 10.4 Onda A), não commitados:

    M mobile/lib/pages/feed_page.dart

    M mobile/lib/pages/profile_page.dart

    M mobile/lib/pages/search_page.dart

    M mobile/lib/widgets/like_button.dart

(upload_page.dart não foi tocado — já estava pronto. A lista acima é o que deve aparecer em git status antes do commit da S50. Verificar — S48e.)

Ação imediata da S51: commitar os 4 arquivos da Onda A (Seção 5, comando exato) + o handoff da S50.

S50 fez:

    Fase 0 completa verde (mobile analyze, web build/lint, backend 180 pytest + ruff, prod health/frontend — o usuário confirmou "tudo verde" sem colar output, por economia de contexto).

    Onda A do item 10.4 COMPLETA — 5 sub-itens, mas 2 já estavam prontos:

        Spinner no like (like_button.dart) — feito na S50 (spinner 20×20 strokeWidth: 2 no lugar do ícone enquanto _inFlight).

        Spinner no upload (upload_page.dart) — já existia (S50b). Não tocado.

        Empty state do feed (feed_page.dart) — feito na S50 (ícone + título + subtítulo + CTA "Enviar atividade").

        Empty state do perfil (profile_page.dart) — feito na S50 (idem, + método novo _openUpload()).

        Empty state da busca (search_page.dart) — feito na S50 (2 abas, ícones person_search / search_off, sem CTA).

    flutter analyze verde nos 4 arquivos, validado um por um.

    NÃO commitou os 4 arquivos (deixado para a S51, junto com este handoff).

S50 NÃO fez (fica para S51):

    Commit da Onda A (4 arquivos) + commit deste handoff.

    Onda B do 10.4 — pull-to-refresh (provavelmente já existe, verificar — S50d) + tratamento global de 401 (o item de maior risco; toca navegação; testar bem).

    Itens herdados da S46: item 7 (validação no Redmi Note 8, incl. cadastro), item 8 (splash + ícone), item 10 (keystore + signingConfigs), item 13 (remover BOM de build.gradle.kts e AndroidManifest.xml).

Percentual consolidado: ~91% (mobile subiu de ~97% para ~98%; MVP subiu de ~90% para ~91%; 10.4 Onda A fechada, Onda B pendente).
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

Git ao fim da S50 (esperado após commit da S51):
text

<novo_hash>  (HEAD -> main, origin/main) feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A)
82d58de  docs: handoff da Sessao 49 (10.2 completo, licoes S49a-d)
211a713  feat(mobile): tela de cadastro + rota /register + register no ApiClient/AuthService (Sessao 49, 10.2 completo)
76e6cce  docs: handoff da Sessao 48 (10.1 completo, licoes S48a-e)
c3447c2  feat(mobile): aplica friendlyErrorMessage em todos os pages (Sessao 48, 10.1 completo)

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 50
3.1 Fase 0 — tudo verde (confirmado pelo usuário)
Verificação	Resultado
flutter analyze	No issues found! (confirmado)
npm run build	OK (confirmado)
npm run lint	0 erros (confirmado)
docker compose -f docker-compose.test.yml up -d	Running (confirmado)
pytest -q	180 passed (confirmado)
ruff check .	All checks passed! (confirmado)
Prod backend /health	OK (confirmado — verificado na S50, não estava na S49)
Prod frontend /	OK (confirmado — verificado na S50)
3.2 Item 10.4 — Onda A (COMPLETA, 4 arquivos verdes)
#	Arquivo	Tipo	Mudança
1	lib/widgets/like_button.dart	modificado	build agora é condicional: _inFlight → CircularProgressIndicator 20×20 strokeWidth: 2 com a cor do ícone; senão, Icon normal. Largura idêntica (20), contador não pula. _toggle, rollback, SnackBar intactos.
2	lib/pages/upload_page.dart	não tocado	Já tinha spinner completo (FilledButton.icon com _submitting ? spinner : Icon, label "Enviando...", canSubmit = hasFile && !_submitting, TextField.enabled = !_submitting). S50b.
3	lib/pages/feed_page.dart	modificado	Ramo _activities.isEmpty saiu de Text cru para Padding + Column (ícone directions_run 64 + título + subtítulo + FilledButton.icon "Enviar atividade" → _openUpload). Fica dentro do ListView (não quebra RefreshIndicator).
4	lib/pages/profile_page.dart	modificado	Método novo _openUpload() (context.push<bool>('/upload'), se true → _refreshAll()). Ramo _activities.isEmpty idem ao feed (ícone + título + subtítulo + CTA "Enviar atividade"). Fica dentro do ListView.
5	lib/pages/search_page.dart	modificado	Os dois ramos if (_hasSearched && _results.isEmpty) (abas Usuários e Atividades) saíram de Text cru para Padding + Column (ícone person_search / search_off 48 + título + subtítulo com a query). Sem CTA (busca vazia não tem ação óbvia).

Validação: cada arquivo passou flutter analyze imediatamente após a substituição. No issues found! nos 4 (2.7s–5.2s). O upload_page.dart não precisou de mudança.
3.3 Commits da S50

Nenhum. Tudo pendente (Seção 5).
SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)

Nenhuma mudança de código no backend desde S39. 180 testes passando. Contratos relevantes (inalterados desde S49):

    POST /auth/register (S49d): público, @limiter.limit("3/hour"). Body = UserCreate (email, username, password, full_name?, weight_kg?, height_cm?, birth_date?). 201 → UserResponse. 409 com dois detail diferentes: "Email já cadastrado" / "Username já cadastrado". 422 validação. 429 rate limit.

    PUT /users/me aceita weight_kg?, height_cm?, full_name? (sem username/email/birth_date — S48c).

    ApiException.message já contém o detail do FastAPI. O tradutor só formata o que já existe.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Ação imediata da S51 (primeira coisa):
powershell

cd D:\Rumo
# 1) Confirmar o que vai entrar (4 arquivos da Onda A + o handoff se já colado)
git status --short --untracked-files=all

# 2) Stage explícito (NÃO usar git add -A)
git add mobile/lib/pages/feed_page.dart
git add mobile/lib/pages/profile_page.dart
git add mobile/lib/pages/search_page.dart
git add mobile/lib/widgets/like_button.dart

# 3) Commit da Onda A
git commit -m "feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A)"

# 4) Push
git push

Depois (commit deste handoff): quando você colar o handoff da S50 em docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 50 (10.4 Onda A completa, licoes S50a-e)"
git push

O que espero ver em git status --short antes do commit da Onda A: exatamente 4 linhas M (feed, profile, search, like_button) — e nenhum ??. Se aparecer ?? cls ou outro untracked, não commitar — investigar primeiro (S48: cls acidental do PowerShell). S48e: verificar sempre; o handoff é documento, não fonte de verdade.
SEÇÃO 6 — SCRIPTS ÚTEIS

Subir o container de teste (obrigatório antes do pytest — S47c):
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

Para os próximos arquivos (processo S48a + correção S50a):

    <250 linhas: Get-Content <arquivo> -Encoding UTF8 (inteiro).

    250–600 linhas: 2 partes:
    powershell

    Get-Content <arquivo> -Encoding UTF8 | Select-Object -First 250
    Get-Content <arquivo> -Encoding UTF8 | Select-Object -Skip 250

    >600 linhas: 3 partes:
    powershell

    Get-Content <arquivo> -Encoding UTF8 | Select-Object -First 400
    Get-Content <arquivo> -Encoding UTF8 | Select-Object -Skip 400 -First 400
    Get-Content <arquivo> -Encoding UTF8 | Select-Object -Skip 800

    NUNCA usar Get-Content arquivo -Skip N — não existe no PS 5.1 (S50a).

Descobrir onde está algo no projeto (economiza contexto, S50):
powershell

cd D:\Rumo\mobile\lib
Get-ChildItem -Recurse -Filter *.dart | Select-String -Pattern "termo" -CaseSensitive:$false | Select-Object Path, LineNumber, Line | Format-Table -AutoSize -Wrap

SEÇÃO 7 — DÍVIDAS TÉCNICAS

Fechadas na S50:

    (S46) Item 10.4 — Onda A (spinner no like, empty states do feed/perfil/busca). ✅

    (S50b/S50d) Spinner no upload e pull-to-refresh no feed/perfil já existiam — não eram dívida, eram itens do 10.4 já prontos. ✅

Conhecidas (não-bug):

    (S41) prod@rumo.com state — estado, não bug.

    (S42k) PWA sem PNGs — não-bloqueador.

    (S43d) BOM em build.gradle.kts e AndroidManifest.xml — não-bloqueador (item 13).

    (S43e) Info.plist sem hardcode — correto.

    (S44) Dois commits de handoff S44 com a mesma mensagem — cosmético, não reescrever histórico.

Oportunidades (S51+):

    (S50) Item 10.4 — Onda B: pull-to-refresh (provavelmente já existe no feed/perfil — verificar antes de assumir, S50d) + tratamento global de 401 com redirecionamento. O 401 global é o item de maior risco do 10.4: toca navegação (go_router), pode causar loop de redirect se mal feito. Testar bem: login com token expirado, logout em uma tela, refresh em outra. Recomendação: implementar em AuthService (um listener/ChangeNotifier que, ao detectar ApiException(401), faz logout() + context.go('/login')), não em cada página. Verificar se ApiClient já tem hook global antes de criar um.

    (S48d) error_message.dart mapeia 409 cego → "Este e-mail já está cadastrado.". Não é problema hoje (o register trata 409 antes do tradutor; nenhum outro fluxo toca username/email). Se um fluxo futuro gerar 409 de username fora do register, ajustar (parâmetro de contexto ou preservar e.message).

    (S47) Container Docker de teste não está no README — considerar documentar.

    (S46) Item 7 completo: validar feed/perfil/upload/like/comentários/export + cadastro no Redmi Note 8. Atenção ao rate limit do register: 3/hora por IP (S49d) — se testar muitas vezes, pode bater no limite.

    (S46) Item 8: splash + ícone no launcher.

    (S46) Item 10: keystore + signingConfigs.

    (S46) Item 13: remover BOM de build.gradle.kts e AndroidManifest.xml.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 51)

Primeira ação (obrigatória): commit da Onda A (4 arquivos, Seção 5).

Segunda ação (Fase 0 padrão): git log/git status, web build/lint, mobile analyze, backend pytest (com container), ruff, prod health/frontend. (Ver Seção 6.)

Terceira ação — escolher entre (ordem recomendada):

    Item 10.4 — Onda B (prioridade alta, ~0,5–1 sessão):

        Pull-to-refresh: verificar feed/perfil antes de assumir (S50d diz que já existe; confirmar e, se já estiver, marcar como feito sem tocar).

        Tratamento global de 401: implementar em AuthService (não em cada página). Antes de criar, verificar se ApiClient já tem hook global. Cuidado com loop de redirect. Testar: login com token expirado, logout em uma tela, refresh em outra.

    Item 7 — validação no Redmi Note 8 (prioridade alta se for submeter em breve, ~1 sessão): feed, perfil, upload, like, comentários, export, cadastro. Atenção ao rate limit do register (3/h).

    Item 8 — splash + ícone no launcher (~0,5 sessão).

    Item 10 — keystore + signingConfigs (só após item 7 completo, ~0,5 sessão).

Ordem sugerida: 10.4 Onda B → item 7 → item 8 → item 10.
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S50)

    S21–S49: acordos mantidos (código completo, handoff completo, aviso de limite, percentual, seguir recomendações).

    S50: o usuário reforçou no início da sessão:

        "sempre seguir suas recomendações" (mesmo que atualize só parte do código).

        "sempre colocar o código completo".

        "fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%".

        "informar o percentual de quanto nosso projeto já está pronto, isso depois de fazermos o handoff no final do chat".

        "gostaria que você avisasse se caso isso for ocorrer [o chat acabar no meio do código] — não estou falando apenas do limite do chat, mas sim o limite do site (IA)". O assistente respondeu com honestidade: o limite do site/IA não é mensurável pelo assistente. O que dá para fazer: entregar arquivo completo um por um, validar imediatamente (flutter analyze/pytest), nunca deixar código pela metade entre duas mensagens, handoff enxuto e frequente. Isso é o máximo que o assistente pode garantir; o resto está fora do alcance.

    S50 — decisão de fechamento: ao chegar em ~70% do contexto, o assistente parou antes de começar a Onda B (o 401 global é o item mais delicado) e fez o handoff completo, em linha com o acordo. O usuário confirmou o flutter analyze verde do search_page.dart e o handoff foi entregue.

Acordos novos da S50: S50a–S50e (ver Seção 0).
SEÇÃO 10 — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 50)
Área	%	Observação
Backend	~95%	inalterado (180 testes, ruff; prod verificado na S50 — OK)
Web	~99%	inalterado (prod verificado na S50 — OK)
Mobile	~98%	subiu de ~97% (10.4 Onda A completa: empty states + spinner no like)
Bloqueadores não-código	~25%	inalterado (contas Google Play/Apple, keystore)
MVP consolidado	~91%	subiu de ~90% (10.4 Onda A fechada, Onda B pendente)

Variação em relação à S49: Mobile 97% → 98% (+1%); MVP 90% → 91% (+1%).

Estimativa até "pronto para submeter":

    10.4 Onda B (401 global + verificar pull-to-refresh): ~0,5–1 sessão.

    Item 7 (validação no celular, incl. cadastro): ~1 sessão.

    Item 8 (splash/ícone) + item 10 (keystore): ~1 sessão.

    Total: ~2,5–3 sessões + 1 de review. ~3–4 sessões.

SEÇÃO 11 — BACKLOG DA SESSÃO 51 (planejamento)

Base: repo em <novo_hash> (após commit da Onda A) — os 4 arquivos já commitados.

    Commit da Onda A (obrigatório, primeira coisa). Ver Seção 5.

    Item 10.4 — Onda B (prioridade alta). Verificar pull-to-refresh (provavelmente já existe — S50d) + tratamento global de 401 (maior risco; implementar em AuthService, não em cada página; verificar se ApiClient já tem hook global antes).

    Item 7 — validação no Redmi Note 8 (prioridade alta). Incluir cadastro; atenção ao rate limit 3/h.

    Itens herdados da S46. Item 8 (splash/ícone), item 10 (keystore), item 13 (BOM).

    Ordem sugerida para a S51: Fase 0 → commit da Onda A → 10.4 Onda B → item 7 → item 8 → item 10.

RESUMO EXECUTIVO PARA A S51

    Primeiro: commit dos 4 arquivos da Onda A (Seção 5) — feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A).

    Depois: Fase 0 completa (Seção 6).

    Em seguida: 10.4 Onda B (401 global + verificar pull-to-refresh) → item 7 (celular, incl. cadastro) → item 8 → item 10.

    O que NÃO fazer: reconstruir arquivo a partir de Select-String (S47a); assumir AuthService.instance (S47b); rodar pytest sem container (S47c); traduzir catch (_) silencioso/rollback/403 como erro (S48b); confiar no handoff sem git log/git status (S48e); usar ?key: value para valor opcional em map literal (S49b — é key: ?value); esquecer de incluir /register no redirect do main.dart (S49c); usar Get-Content -Skip no PS 5.1 (S50a — não existe; usar | Select-Object -Skip); assumir que pull-to-refresh/spinner no upload precisam ser feitos (S50b/S50d — já existiam).

    Regra de ouro: não tenho acesso ao disco. Pedir Get-Content inteiro. Nunca inventar caminho. Nunca reescrever arquivo não recebido.

Percentual de prontidão (fim da S50): Backend ~95% · Web ~99% · Mobile ~98% · Bloqueadores não-código ~25% · MVP consolidado ~91%