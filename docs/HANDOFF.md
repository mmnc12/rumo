HANDOFF — SESSÃO 51 (para a Sessão 52)
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro (S21–S51, inalterada): Você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho. Nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

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

Adições S50 (mantidas):

    S50a — Get-Content do PowerShell 5.1 NÃO tem -Skip como parâmetro nomeado. Get-Content arquivo -Skip N falha com ParameterBindingException. O comando correto é Get-Content arquivo -Encoding UTF8 | Select-Object -Skip N -First M (ou sem -First para ir até o fim). O -First N do Get-Content funciona (é parâmetro válido), mas -Skip não.

    S50b — upload_page.dart já tinha spinner no botão de upload (feito provavelmente na S31). FilledButton.icon com _submitting ? spinner : Icon, label: _submitting ? 'Enviando...' : 'Enviar', canSubmit = hasFile && !_submitting, TextField.enabled = !_submitting, IconButton de remover some durante o envio.

    S50c — ProfilePage é self-only. O perfil de terceiro é o UserProfilePage. CTA "Enviar atividade" no empty state do perfil faz sentido (não é perfil alheio). _openUpload() foi criado novo no ProfilePage (não existia).

    S50d — FeedPage já tinha RefreshIndicator (pull-to-refresh) e retry de erro. Idem ProfilePage (RefreshIndicator + _refreshAll()). Onda B (pull-to-refresh) não tem nada a fazer.

    S50e — Empty state do feed/perfil/busca: convenção adotada. Ícone 64 (feed/perfil) ou 48 (busca), onSurfaceVariant, título titleMedium, subtítulo bodyMedium, textAlign: TextAlign.center. No feed/perfil: CTA FilledButton.icon "Enviar atividade" → _openUpload(). Na busca: sem CTA. Empty state do feed/perfil fica dentro do ListView (não Center de tela cheia) para não quebrar o RefreshIndicator. Na busca, o _buildBody retorna Center.

Adições S51 (NOVAS):

    S51a — ApiClient não tinha hook global de 401. Foi adicionado um campo público mutável void Function()? onUnauthorized; e chamadas if (response.statusCode == 401) onUnauthorized?.call(); em três pontos: _send (GET/POST/PUT/DELETE), _fetchBlob (export) e uploadActivity. O login NÃO dispara — 401 de senha errada é esperado e não deve deslogar.

    S51b — AuthService agora tem construtor explícito que injeta o callback: AuthService() { _api.onUnauthorized = _handleUnauthorized; }. O corpo do construtor roda depois da inicialização dos campos, então _api já existe.

    S51c — _handleUnauthorized() tem guard if (!isLoggedIn) return; (idempotente, evita logout duplicado/loop) e chama logout(). Sem navegação no AuthService — quem navega é o refreshListenable do GoRouter.

    S51d — A peça que faltava: o GoRouter não escutava o AuthService. logout() chama notifyListeners(), mas o GoRouter só reavalia o redirect quando a rota muda ou quando um refreshListenable notifica. Foi adicionado refreshListenable: _auth, no GoRouter(...) do main.dart. Sem isso, o 401 faz logout mas não navega (usuário fica preso na tela que falhou).

    S51e — A regra discarded_futures está ativa no projeto (analysis_options.yaml). Chamar logout() (retorna Future<void>) sem await num callback void gera esse lint. Solução adotada: // ignore: discarded_futures com comentário explicando. O analyze aceitou o ignore (não deu Unnecessary ignore), confirmando que a regra está ativa.

    S51f — O refreshListenable: _auth faz o GoRouter reavaliar o redirect a cada notifyListeners() — inclusive no bootstrap() (quando loading vira false e o token é lido do storage). Isso é desejado (na inicialização, o redirect precisa saber se está logado). O redirect é puro (não tem efeito colateral), então não deve causar loop. Mas atenção ao primeiro frame: initialLocation: '/login' + bootstrap() assíncrono podem competir. Se aparecer "piscar" entre login e feed na inicialização, a correção é mostrar splash enquanto _auth.loading == true (não antecipar; testar primeiro).

SEÇÃO 1 — TL;DR para quem chega agora

Estado do repo no fim da S51: HEAD == origin/main == 9753ed9 (commit do handoff S50). Working tree tem 3 arquivos modificados NÃO commitados (a Onda B da S51):

    M mobile/lib/services/api.dart (callback onUnauthorized + 3 disparos de 401)

    M mobile/lib/services/auth_service.dart (construtor + _handleUnauthorized)

    M mobile/lib/main.dart (refreshListenable: _auth)

Os 3 arquivos passaram no flutter analyze (No issues found!), validados um por um.

O que a S51 fez: implementou a Onda B do item 10.4 (tratamento global de 401 + verificação do pull-to-refresh). O pull-to-refresh já existia (S50d confirmado: RefreshIndicator em feed_page.dart linha 191, profile_page.dart linha 549, user_profile_page.dart linha 518) — não foi tocado. O 401 global foi implementado nos 3 arquivos acima.

O que a S51 NÃO fez (fica para a S52):

    Teste manual dos 5 cenários (roteiro completo na Seção 5). O código está verde no analyze, mas não foi validado comportamentalmente. Isso é o primeiro item da S52.

    Commit dos 3 arquivos + commit deste handoff (só depois do teste manual passar).

    Itens herdados da S46: item 7 (validação no Redmi Note 8, incl. cadastro), item 8 (splash + ícone), item 10 (keystore + signingConfigs), item 13 (remover BOM de build.gradle.kts e AndroidManifest.xml).

Ação imediata da S52: executar o teste manual (Seção 5). Se passar, commitar (Seção 6). Se falhar, diagnosticar (Seção 5.7 tem os suspeitos).

Percentual consolidado: ~92% (Mobile subiu de ~98% para ~99%; MVP subiu de ~91% para ~92%; 10.4 Onda B implementada, pendente de teste/commit).
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

Git ao fim da S51 (esperado após o commit da S52):
text

<novo_hash>  (HEAD -> main, origin/main) feat(mobile): tratamento global de 401 + refreshListenable (Sessao 51, 10.4 Onda B)
9753ed9  docs: handoff da Sessao 50 (10.4 Onda A completa, licoes S50a-e)
3c534ec  feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A)
82d58de  docs: handoff da Sessao 49 (10.2 completo, licoes S49a-d)
211a713  feat(mobile): tela de cadastro + rota /register + register no ApiClient/AuthService (Sessao 49, 10.2 completo)

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 51
3.1 Verificação inicial (S48e — não confiar só no handoff)

O usuário colou git status --short --untracked-files=all (vazio) e git log --oneline -3:
text

9753ed9 (HEAD -> main, origin/main) docs: handoff da Sessao 50 (10.4 Onda A completa, licoes S50a-e)
3c534ec feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A)
82d58de docs: handoff da Sessao 49 (10.2 completo, licoes S49a-d)

Conclusão: o commit da Onda A e o handoff da S50 já estavam feitos (provavelmente no fim da S50 ou entre sessões). A "primeira ação obrigatória da S51" (commit da Onda A) já estava concluída. Working tree limpo, HEAD == origin/main.
3.2 Fase 0 — tudo verde (confirmado pelo usuário)
Verificação	Resultado
flutter analyze	No issues found! (confirmado)
npm run build	OK (confirmado)
npm run lint	0 erros (confirmado)
docker compose -f docker-compose.test.yml up -d	Running (confirmado)
pytest -q	180 passed (confirmado)
ruff check .	All checks passed! (confirmado)
Prod backend /health	OK (confirmado)
Prod frontend /	OK (confirmado)
3.3 Item 10.4 — Onda B (IMPLEMENTADA, analyze verde, teste manual pendente)

Verificação do pull-to-refresh (S50d confirmado): busca de RefreshIndicator no mobile/lib retornou:

    feed_page.dart linha 191 — RefreshIndicator(

    profile_page.dart linha 549 — RefreshIndicator( (com comentários sobre Future.wait nas linhas 14, 360, 368, 388, 626)

    user_profile_page.dart linha 518 — RefreshIndicator( (bônus)

Conclusão: pull-to-refresh já existe nos três. Nada a fazer. Item marcado como completo sem tocar.

Tratamento global de 401 — 3 arquivos alterados:
#	Arquivo	Mudança
1	lib/services/api.dart	Campo novo void Function()? onUnauthorized; (após _client). Disparo if (response.statusCode == 401) onUnauthorized?.call(); em 3 pontos: _send (antes do throw do bloco de erro), _fetchBlob (idem), uploadActivity (antes do throw do != 201). login intocado (não dispara — 401 de senha errada é esperado). Comentários novos explicando.
2	lib/services/auth_service.dart	Construtor explícito AuthService() { _api.onUnauthorized = _handleUnauthorized; }. Método novo _handleUnauthorized(): guard if (!isLoggedIn) return; + logout() (com // ignore: discarded_futures). Todo o resto idêntico (login, register, bootstrap, logout, currentUserId, decode).
3	lib/main.dart	Uma linha nova no GoRouter(...): refreshListenable: _auth,. Comentário de topo explicando a Onda B. Todo o resto idêntico.

Validação: cada arquivo passou flutter analyze imediatamente após a substituição. No issues found! nos 3 (99.3s, 42.5s, 97.8s). O // ignore: discarded_futures foi aceito (não deu Unnecessary ignore), confirmando que a regra está ativa (S51e).
3.4 Commits da S51

Nenhum. Os 3 arquivos estão no working tree, não commitados (decisão consciente: commitar só depois do teste manual passar — o analyze não pega lógica).
SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)

Nenhuma mudança de código no backend desde S39. 180 testes passando. Contratos relevantes (inalterados desde S49):

    POST /auth/register (S49d): público, @limiter.limit("3/hour"). Body = UserCreate (email, username, password, full_name?, weight_kg?, height_cm?, birth_date?). 201 → UserResponse. 409 com dois detail diferentes: "Email já cadastrado" / "Username já cadastrado". 422 validação. 429 rate limit.

    PUT /users/me aceita weight_kg?, height_cm?, full_name? (sem username/email/birth_date — S48c).

    ApiException.message já contém o detail do FastAPI. O tradutor só formata o que já existe.

Nota sobre 401: o backend retorna 401 quando o token JWT está ausente, malformado ou expirado. Não há endpoint de revogação de token — o que torna o teste "real" de token expirado difícil em prod (ver Seção 5.5).
SEÇÃO 5 — TESTE MANUAL DA ONDA B (PRIMEIRA AÇÃO DA S52)

Contexto: o código está verde no flutter analyze, mas não foi validado comportamentalmente. Os 5 passos abaixo cobrem regressão + o caso novo (401 global). Execute na ordem. Se algum falhar, ver Seção 5.7 (diagnóstico).
5.1 Passo 1 — Login normal (regressão)

    Abrir o app, logar com credenciais válidas.

    Esperado: entra no /feed, sem piscar, sem loop, sem tela cinza.

    Confirma: refreshListenable não quebrou o fluxo normal.

5.2 Passo 2 — Logout manual (regressão)

    Ainda logado, ir em Perfil → Sair.

    Esperado: vai para /login, sem travar.

    Confirma: refreshListenable não duplicou navegação nem causou loop.

5.3 Passo 3 — Senha errada no login (o caso que NÃO pode deslogar)

    Na tela de login, digitar e-mail válido + senha errada. Tocar em Entrar.

    Esperado: mensagem de erro local na LoginPage (o tradutor trata). Permanece no login. Não navega, não mostra "sessão expirada", não chama logout().

    Por que é crítico: o login do ApiClient não dispara onUnauthorized (decisão explícita). Se este passo falhar (app desloga ou mostra mensagem estranha), é bug de lógica — ver Seção 5.7.

5.4 Passo 4 — Login após logout (regressão)

    Depois do passo 2 ou 3, logar de novo com credenciais válidas.

    Esperado: entra no /feed normalmente. Confirma que _token/_cachedUserId foram limpos corretamente.

5.5 Passo 5 — 401 real (fiação) — com código temporário

Por que temporário: o backend em prod não tem revogação de token e o JWT é assinado — não dá para "expirar de fora". A forma confiável de testar a fiação callback → logout → refreshListenable → redirect é forçar um 401 temporariamente e depois reverter.

5.5.1. Alteração temporária no api.dart: abrir mobile/lib/services/api.dart, encontrar o método _send e adicionar, logo no início do método (antes de montar a URI):
dart

    // TESTE TEMPORÁRIO — REMOVER DEPOIS
    if (path.contains('/activities')) {
      onUnauthorized?.call();
      throw ApiException(401, 'Token expirado (teste)');
    }

O que isso faz: qualquer chamada a _send cujo path contenha /activities (o feed usa listActivities → get('/activities?...') → _send('GET', '/activities?...')) simula o que o _send faria num 401 real: chama o callback e lança o erro. Não testa a resposta HTTP real, mas testa a fiação inteira (callback → AuthService → logout → refreshListenable → redirect), que é o que a Onda B adiciona.

5.5.2. Rodar o teste:

    Salvar o api.dart alterado.

    cd D:\Rumo\mobile; & "C:\Users\nasci\flutter\bin\flutter.bat" analyze → deve dar No issues found! (o bloco temporário é válido).

    Rodar o app (flutter run ou hot restart).

    Fazer login (o login em si não chama /activities — deve funcionar).

    Ao entrar no /feed, o app tenta carregar atividades → _send('GET', '/activities...') → bloco temporário dispara onUnauthorized e lança 401.

    Esperado: o app desloga e cai no /login automaticamente, sem travar, sem loop, sem tela cinza.

5.5.3. Reverter (obrigatório): remover o bloco // TESTE TEMPORÁRIO — REMOVER DEPOIS do _send. Salvar. Rodar flutter analyze → No issues found!. Confirmar que o bloco sumiu (buscar TESTE TEMPORÁRIO no arquivo — não deve achar nada).

5.5.4. Após reverter: fazer login de novo → deve entrar no /feed normalmente (o feed volta a carregar). Confirma que a reversão foi limpa.
5.6 Se tudo passar

    O código da Onda B está validado (analyze + comportamento).

    Commitar (Seção 6): os 3 arquivos + este handoff.

    Seguir para o backlog (Seção 8).

5.7 Se algo falhar — diagnóstico
Passo	Sintoma	Suspeita	Correção
1, 2 ou 4	Pisca entre login e feed; loop; tela cinza	Interação refreshListenable × bootstrap() no primeiro frame (S51f)	Mostrar splash enquanto _auth.loading == true no build do _RumoAppState (ou ajustar initialLocation). Não antecipar — testar primeiro.
1, 2 ou 4	Logout manual não navega	refreshListenable ausente ou notifyListeners não chamado	Verificar refreshListenable: _auth no main.dart e notifyListeners() no logout().
5	App não desloga ao entrar no feed	(a) bloco temporário não foi inserido no lugar certo; (b) onUnauthorized não está setado (construtor do AuthService não rodou); (c) _handleUnauthorized não chama logout()	Adicionar debugPrint('401 callback') no _handleUnauthorized e ver no console. Verificar se AuthService() é o mesmo _auth do main.dart (é — _RumoAppState._auth).
5	App desloga mas não navega	refreshListenable ausente	Verificar refreshListenable: _auth no GoRouter(...).
3	App desloga com senha errada (BUG)	Alguém chamou onUnauthorized no login	Verificar login do ApiClient — não deve ter onUnauthorized?.call(). (O código entregue não tem; confirmar.)
5 (revertido)	Feed não carrega depois de reverter	Bloco temporário não removido	Buscar TESTE TEMPORÁRIO no api.dart — deve ser zero ocorrências.
SEÇÃO 6 — COMMITS PENDENTES / ESTADO DO REPO

Ação da S52 (só depois do teste manual passar — Seção 5.6):
powershell

cd D:\Rumo
# 1) Confirmar o que vai entrar (3 arquivos M + o handoff se já colado)
git status --short --untracked-files=all

# 2) Stage explícito (NÃO usar git add -A)
git add mobile/lib/services/api.dart
git add mobile/lib/services/auth_service.dart
git add mobile/lib/main.dart

# 3) Commit da Onda B
git commit -m "feat(mobile): tratamento global de 401 + refreshListenable (Sessao 51, 10.4 Onda B)"

# 4) Push
git push

Depois (commit deste handoff): quando colar este handoff em docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 51 (10.4 Onda B implementada, teste manual pendente, licoes S51a-f)"
git push

O que espero ver em git status --short antes do commit da Onda B: exatamente 3 linhas M (api.dart, auth_service.dart, main.dart) — e nenhum ??. Se aparecer ?? cls ou outro untracked, não commitar — investigar primeiro (S48: cls acidental do PowerShell). S48e: verificar sempre; o handoff é documento, não fonte de verdade.

Se o teste manual (Seção 5) falhar: NÃO commitar. Diagnosticar (Seção 5.7), corrigir, revalidar (flutter analyze + teste), só então commitar.
SEÇÃO 7 — SCRIPTS ÚTEIS

Subir o container de teste (obrigatório antes do pytest — S47c):
powershell

cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
# aguardar ~3s; depois:
.\venv\Scripts\Activate.ps1
python -m pytest -q
# Esperado: 180 passed
ruff check .
# Esperado: All checks passed!

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

Descobrir onde está algo no projeto (economiza contexto):
powershell

cd D:\Rumo\mobile\lib
Get-ChildItem -Recurse -Filter *.dart | Select-String -Pattern "termo" -CaseSensitive:$false | Select-Object Path, LineNumber, Line | Format-Table -AutoSize -Wrap

Contar linhas de um arquivo (para escolher quantas partes):
powershell

(Get-Content D:\Rumo\mobile\lib\caminho\arquivo.dart -Encoding UTF8).Count

SEÇÃO 8 — DÍVIDAS TÉCNICAS E BACKLOG DETALHADO
8.1 Fechadas na S51

    (S46) Item 10.4 — Onda B (401 global). ✅ Implementada nos 3 arquivos, analyze verde. Pendente de teste manual + commit (não é dívida de código, é validação pendente).

    (S50d) Pull-to-refresh no feed/perfil. ✅ Confirmado que já existia (RefreshIndicator em feed_page.dart:191, profile_page.dart:549, user_profile_page.dart:518). Nada foi feito — não era dívida.

8.2 Conhecidas (não-bug)

    (S41) prod@rumo.com state — estado, não bug.

    (S42k) PWA sem PNGs — não-bloqueador.

    (S43d) BOM em build.gradle.kts e AndroidManifest.xml — não-bloqueador (item 13).

    (S43e) Info.plist sem hardcode — correto.

    (S44) Dois commits de handoff S44 com a mesma mensagem — cosmético, não reescrever histórico.

8.3 Backlog para S52+ (passo a passo)
Item 7 — Validação no Redmi Note 8 (prioridade alta, ~1 sessão)

Objetivo: testar o app real no celular (Android 10, API 29, arm64) cobrindo os fluxos principais. Atenção ao rate limit do register: 3/hora por IP (S49d) — se testar muitas vezes, pode bater no limite.

Pré-requisitos:

    Redmi Note 8 conectado (flutter devices deve mostrar c767cacd).

    Backend de prod acessível (https://rumo-api-5s0b.onrender.com/health → OK).

    App buildado: cd D:\Rumo\mobile; & "C:\Users\nasci\flutter\bin\flutter.bat" run -d c767cacd (ou flutter build apk --debug e instalar).

Roteiro de teste (cobrir tudo):
#	Fluxo	O que testar	Esperado
7.1	Cadastro	Abrir /register, criar conta nova (e-mail/username únicos, senha ≥8).	201 → login automático → /feed. Cuidado: 3/hora por IP.
7.2	Login	Logar com a conta criada.	Entra no /feed.
7.3	Feed	Rolar o feed; pull-to-refresh; like; abrir detalhe.	Scroll suave; refresh funciona; like atualiza contador; detalhe abre.
7.4	Perfil	Abrir /profile; pull-to-refresh; editar perfil (/edit-profile); ver stats.	Perfil carrega; refresh funciona; edição salva; stats aparecem.
7.5	Upload	Abrir /upload; escolher arquivo GPX/FIT; preencher título; enviar.	Spinner durante envio; sucesso → volta pro feed com a atividade nova.
7.6	Comentários	Abrir detalhe; criar comentário; deletar o próprio comentário.	Comentário aparece; delete some.
7.7	Export	No detalhe, exportar CSV e GPX (unitário); exportar em lote (ZIP) no perfil.	Download/compartilhamento abre o share sheet; arquivo correto.
7.8	Busca	Abrir /search; buscar usuário e atividade (abas).	Resultados aparecem; empty state correto.
7.9	Follow	Abrir /user/:id de terceiro; seguir/deixar de seguir.	Botão alterna; lista de following atualiza.
7.10	401 global	Repetir o teste da Seção 5.5 no celular (com o bloco temporário).	Desloga e cai no /login.

Atenção especial:

    7.1 (cadastro): rate limit 3/h. Se precisar testar mais, aguardar ou usar outro IP (não recomendado). Testar uma vez e validar bem.

    7.5 (upload): testar com GPX e FIT (se tiver arquivo). O upload é multipart, o caminho File (Android) é diferente do bytes (Web) — no celular usa File.

    7.10 (401): lembrar de reverter o bloco temporário depois.

Saída esperada: todos os 10 fluxos OK. Se algum falhar, anotar qual + comportamento + mensagem (se houver) e reportar.
Item 8 — Splash + ícone no launcher (prioridade média, ~0,5 sessão)

Objetivo: ter splash screen e ícone do app no launcher Android (e iOS, se for o caso).

Passo a passo:

    Ícone: criar/preparar um PNG 1024×1024 do ícone do Rumo (não existe ainda — S42k menciona PWA sem PNGs).

    Usar flutter_launcher_icons (dev dependency) para gerar os ícones Android/iOS a partir do PNG. Configurar flutter_launcher_icons.yaml com android: true, ios: true, image_path: "assets/icon/icon.png". Rodar dart run flutter_launcher_icons.

    Splash: usar flutter_native_splash (dev dependency). Configurar flutter_native_splash.yaml com color: "#F97316" (laranja do tema) e image: assets/splash/splash.png (logo centralizado). Rodar dart run flutter_native_splash:create.

    Testar no Redmi Note 8: ícone aparece no launcher; splash aparece ao abrir.

    Commitar.

Atenção: o flutter_native_splash e o flutter_launcher_icons geram arquivos nativos (android/app/src/main/res/..., ios/Runner/Assets.xcassets/...). Não reescrever à mão — usar as ferramentas. Verificar git status depois para ver o que foi gerado.
Item 10 — Keystore + signingConfigs (prioridade média, só após item 7, ~0,5 sessão)

Objetivo: configurar assinatura de release do Android (obrigatório para publicar na Play Store).

Passo a passo:

    Gerar keystore: keytool -genkey -v -keystore D:\Rumo\mobile\android\app\rumo-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias rumo. Guardar a senha em local seguro (não commitar).

    Criar android/key.properties (não commitar — adicionar ao .gitignore):
    text

    storePassword=<senha>
    keyPassword=<senha>
    keyAlias=rumo
    storeFile=rumo-release.jks

    Editar android/app/build.gradle.kts: ler o key.properties, configurar signingConfigs { create("release") { ... } } e usar signingConfig = signingConfigs.getByName("release") no buildTypes.release.

    Adicionar key.properties e *.jks ao .gitignore.

    Testar: flutter build apk --release → APK assinado. Instalar no Redmi Note 8 e validar.

    Commitar (só o build.gradle.kts e .gitignore; nunca o .jks nem o key.properties).

Atenção: o BOM em build.gradle.kts (S43d / item 13) pode atrapalhar a edição — remover o BOM antes (item 13).
Item 13 — Remover BOM de build.gradle.kts e AndroidManifest.xml (prioridade baixa, ~0,1 sessão)

Objetivo: remover o Byte Order Mark (BOM) UTF-8 desses arquivos (S43d). O BOM pode causar problemas em ferramentas de build/edição.

Passo a passo:

    Verificar se há BOM: Get-Content D:\Rumo\mobile\android\app\build.gradle.kts -Encoding Byte -TotalCount 3 → se for 239 187 191, tem BOM.

    Remover: ler o conteúdo como UTF8, salvar de novo sem BOM. Em PowerShell:
    powershell

    $p = 'D:\Rumo\mobile\android\app\build.gradle.kts'
    $c = Get-Content $p -Encoding UTF8 -Raw
    [System.IO.File]::WriteAllText($p, $c, (New-Object System.Text.UTF8Encoding $false))

    Repetir para AndroidManifest.xml (se tiver BOM).

    Verificar: Get-Content ... -Encoding Byte -TotalCount 3 → não deve ser 239 187 191.

    flutter build apk --debug para confirmar que o build não quebrou.

    Commitar.

Ordem sugerida para a S52+

    Teste manual da Onda B (Seção 5) — primeira coisa, antes de qualquer código novo.

    Commit da Onda B + handoff (Seção 6) — se o teste passar.

    Item 7 (validação no Redmi Note 8) — cobre tudo, incl. cadastro (atenção ao rate limit 3/h).

    Item 8 (splash + ícone) — precisa de PNG do ícone (não existe; criar primeiro).

    Item 10 (keystore + signing) — só depois do item 7 completo.

    Item 13 (BOM) — pode ser feito junto com o item 10 (mesmo arquivo build.gradle.kts).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S51)

    S21–S50: acordos mantidos (código completo, handoff completo, aviso de limite, percentual, seguir recomendações).

    S51: o usuário reforçou no início da sessão os mesmos 5 pontos da S50:

        "sempre seguir suas recomendações" (mesmo que atualize só parte do código).

        "sempre colocar o código completo".

        "fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo de 70% a 80%".

        "informar o percentual de quanto nosso projeto já está pronto, isso depois de fazermos o handoff no final do chat".

        "gostaria que você avisasse se caso isso for ocorrer [o chat acabar no meio do código] — não estou falando apenas do limite do chat, mas sim o limite do site (IA)". O assistente respondeu com honestidade: o limite do site/IA não é mensurável pelo assistente. O que dá para fazer: entregar arquivo completo um por um, validar imediatamente, nunca deixar código pela metade entre duas mensagens, handoff enxuto e frequente. Isso é o máximo garantível; o resto está fora do alcance.

    S51 — decisão de fechamento: ao perceber que o contexto estava acima de 70% (após entregar os 3 arquivos da Onda B, todos verdes no analyze, mas antes do teste manual), o assistente parou e propôs o handoff. O usuário concordou e pediu handoff detalhado cobrindo tudo o que falta (não só o teste). O handoff foi entregue (este documento). O teste manual fica para a S52 (ou para o usuário executar sozinho entre sessões).

Acordos novos da S51: S51a–S51f (ver Seção 0).
SEÇÃO 10 — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 51)
Área	%	Observação
Backend	~95%	inalterado (180 testes, ruff; prod OK)
Web	~99%	inalterado (prod OK)
Mobile	~99%	subiu de ~98% (10.4 Onda B implementada: 401 global + refreshListenable; analyze verde nos 3 arquivos; teste manual pendente)
Bloqueadores não-código	~25%	inalterado (contas Google Play/Apple, keystore)
MVP consolidado	~92%	subiu de ~91% (10.4 Onda B implementada; falta teste + commit)

Variação em relação à S50: Mobile 98% → 99% (+1%); MVP 91% → 92% (+1%).

Estimativa até "pronto para submeter":

    Teste manual da Onda B + commit: ~0,2–0,5 sessão (parte de uma sessão).

    Item 7 (validação no celular, incl. cadastro): ~1 sessão.

    Item 8 (splash/ícone): ~0,5 sessão (precisa criar PNG do ícone).

    Item 10 (keystore) + item 13 (BOM): ~0,5–1 sessão.

    Total: ~2,5–3 sessões + 1 de review. ~3–4 sessões.

SEÇÃO 11 — BACKLOG DA SESSÃO 52 (planejamento)

Base: repo em 9753ed9 (working tree com 3 arquivos M da Onda B, não commitados).

    Teste manual da Onda B (Seção 5) — primeira coisa. 5 passos, incluindo o teste temporário de 401 (Seção 5.5). Reverter o bloco temporário ao fim.

    Commit da Onda B + handoff (Seção 6) — se o teste passar. 3 arquivos + docs/HANDOFF.md.

    Item 7 — validação no Redmi Note 8 (10 fluxos da Seção 8.3). Atenção ao rate limit 3/h no cadastro.

    Item 8 — splash + ícone (precisa criar PNG do ícone primeiro).

    Item 10 — keystore + signingConfigs (só após item 7).

    Item 13 — remover BOM (pode ser junto com o item 10).

Ordem sugerida: Teste manual → commit → item 7 → item 8 → item 10 + item 13.
SEÇÃO 12 — RESUMO EXECUTIVO PARA A S52

    Primeiro: executar o teste manual da Onda B (Seção 5, 5 passos, incl. o teste temporário de 401 na Seção 5.5 e reverter depois).

    Se passar: commitar os 3 arquivos + este handoff (Seção 6).

    Se falhar: diagnosticar (Seção 5.7), corrigir, revalidar, só então commitar.

    Depois: item 7 (Redmi Note 8) → item 8 (splash/ícone) → item 10 (keystore) + item 13 (BOM).

    O que NÃO fazer: reconstruir arquivo a partir de Select-String (S47a); assumir AuthService.instance (S47b); rodar pytest sem container (S47c); traduzir catch (_) silencioso/rollback/403 como erro (S48b); confiar no handoff sem git log/git status (S48e); usar ?key: value para valor opcional em map literal (S49b — é key: ?value); esquecer de incluir /register no redirect (S49c); usar Get-Content -Skip no PS 5.1 (S50a — usar | Select-Object -Skip); assumir que pull-to-refresh/spinner no upload precisam ser feitos (S50b/S50d — já existiam); commitar a Onda B antes do teste manual passar (S51 — o analyze não pega lógica); esquecer o refreshListenable (S51d — sem ele, o 401 não navega).

    Regra de ouro: não tenho acesso ao disco. Pedir Get-Content inteiro. Nunca inventar caminho. Nunca reescrever arquivo não recebido.

PERCENTUAL DE PRONTIDÃO (fim da S51)

Backend ~95% · Web ~99% · Mobile ~99% · Bloqueadores não-código ~25% · MVP consolidado ~92%