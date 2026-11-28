HANDOFF — SESSÃO 51/52 (para a Sessão 53)
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro (S21–S52, inalterada): Você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho. Nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

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

Adições S51 (mantidas):

    S51a — ApiClient não tinha hook global de 401. Foi adicionado um campo público mutável void Function()? onUnauthorized; e chamadas if (response.statusCode == 401) onUnauthorized?.call(); em três pontos: _send (GET/POST/PUT/DELETE), _fetchBlob (export) e uploadActivity. O login NÃO dispara — 401 de senha errada é esperado e não deve deslogar.

    S51b — AuthService agora tem construtor explícito que injeta o callback: AuthService() { _api.onUnauthorized = _handleUnauthorized; }. O corpo do construtor roda depois da inicialização dos campos, então _api já existe.

    S51c — _handleUnauthorized() tem guard if (!isLoggedIn) return; (idempotente, evita logout duplicado/loop) e chama logout(). Sem navegação no AuthService — quem navega é o refreshListenable do GoRouter.

    S51d — A peça que faltava: o GoRouter não escutava o AuthService. logout() chama notifyListeners(), mas o GoRouter só reavalia o redirect quando a rota muda ou quando um refreshListenable notifica. Foi adicionado refreshListenable: _auth, no GoRouter(...) do main.dart. Sem isso, o 401 faz logout mas não navega (usuário fica preso na tela que falhou).

    S51e — A regra discarded_futures está ativa no projeto (analysis_options.yaml). Chamar logout() (retorna Future<void>) sem await num callback void gera esse lint. Solução adotada: // ignore: discarded_futures com comentário explicando. O analyze aceitou o ignore (não deu Unnecessary ignore), confirmando que a regra está ativa.

    S51f — O refreshListenable: _auth faz o GoRouter reavaliar o redirect a cada notifyListeners() — inclusive no bootstrap() (quando loading vira false e o token é lido do storage). Isso é desejado (na inicialização, o redirect precisa saber se está logado). O redirect é puro (não tem efeito colateral), então não deve causar loop. Mas atenção ao primeiro frame: initialLocation: '/login' + bootstrap() assíncrono podem competir. Se aparecer "piscar" entre login e feed na inicialização, a correção é mostrar splash enquanto _auth.loading == true (não antecipar; testar primeiro).

Adições S52 (NOVAS — esta sessão):

    S52a — O commit da Onda B JÁ FOI FEITO entre a S51 e a S52 (hash 49b4275, mensagem feat(mobile): tratamento global de 401 + refreshListenable (Sessao 51, 10.4 Onda B)). O handoff da S51 também foi commitado (docs/HANDOFF.md). Working tree limpo. A Onda B está commitada mas NÃO foi validada comportamentalmente — o teste manual da Seção 5 do handoff S51 (5 passos, incl. 7.10/401) ainda não foi executado com sucesso/registro. Isso é o que falta para fechar a Onda B de verdade.

    S52b — O usuário gerou e instalou o APK debug no Redmi Note 8 e está testando manualmente. O APK é flutter build apk --debug, que mostra o banner "DEBUG" no canto superior direito — esperado e correto em debug (some no release, que só sai depois do Item 10/keystore). Não é bug.

    S52c — O usuário inseriu o bloco temporário de teste do 401 no _send do api.dart (Seção 5.5.1 do handoff S51), entre a linha 820 (}) async {) e a 821 (final uri = Uri.parse(...)), com a estrutura exata: // TESTE TEMPORÁRIO — REMOVER DEPOIS (Sessao 51, Secao 5.5) + if (path.contains('/activities')) { onUnauthorized?.call(); throw ApiException(401, 'Token expirado (teste)'); }. Esse bloco PRECISA ser revertido ao final dos testes (Seção 5.5.3) — senão o app desloga toda vez que abrir o feed. Status na S52: inserido, NÃO revertido ainda (o teste 7.10 provavelmente foi feito com o bloco, mas o resultado não foi registrado antes da cota acabar).

    S52d — O usuário confirmou 1 validação de comportamento: o tratamento de erro amigável no feed funciona — se o servidor demora, aparece "servidor demorando, tente novamente" em vez da mensagem crua ("antes aparecia uma mensagem feia"). Isso valida o friendlyErrorMessage (S48b) + ApiException(0, ...) (S47e) no caminho de timeout — não é o 401 global (7.10), é outro caminho. Sinal positivo, mas não fecha a Onda B.

    S52e — Diagnóstico do mapa (faixa amarela/preta "POWERED BY 69 PIXELS"): NÃO é bug. O activity_map.dart usa tile.openstreetmap.org (linha 58) e tem SimpleAttributionWidget configurado (linhas 115–116 e 204–206, alternando _esriAttribution/_osmAttribution conforme _satelite). A faixa amarela/preta é placeholder/overlay padrão do flutter_map enquanto os tiles carregam (ou overlay de atribuição do próprio pacote em versões recentes). É cosmético. Não vale a pena mexer agora. Na S53, confirmar com uma pergunta simples: "a faixa some depois que o mapa carrega?" — se sim, cosmético, ignorar; se fica permanente, investigar SimpleAttributionWidget (alignment/backgroundColor padrão que precisa ser customizado). O mapa em si funciona (ruas visíveis, traçado da rota desenhado na screenshot).

    S52f — O usuário mencionou "a barra de baixo está estranha, já tinha relatado e consertado, só que voltou" — NÃO CONFIRMADO o que exatamente está estranho. Pode ser: (a) FAB (botão laranja de upload) cobrindo o último card do feed (visível na screenshot); (b) espaçamento/insets da NavigationBar; (c) cor/label errada; (d) outra coisa. Não assumir (S48e). Na S53, pedir descrição do usuário + o trecho do feed_page.dart/profile_page.dart relevante antes de corrigir. Pode ser falso positivo ("voltou" pode ser que nunca foi exatamente esse ponto, ou era outra tela).

    S52g — Cota apertada: o usuário avisou que restam ~37% da cota diária do site/IA. Decisão: handoff imediato (este documento) antes de esgotar. Limite do site/IA não é mensurável pelo assistente — o usuário é quem informa. Isso confirma a limitação declarada na S51: o assistente não consegue prever o corte do site, só o usuário consegue avisar.

SEÇÃO 1 — TL;DR para quem chega agora

Estado do repo no fim da S52: HEAD == origin/main == 49b4275 (commit da Onda B S51) + commit do handoff S51 em cima (docs/HANDOFF.md). Working tree limpo no repo. Porém, o api.dart no disco do usuário tem o bloco temporário de teste do 401 inserido (S52c) e NÃO revertido — ou seja, o git status provavelmente vai mostrar M mobile/lib/services/api.dart agora. Primeira ação da S53: verificar git status e reverter o bloco temporário antes de qualquer outra coisa (S52c / Seção 5.5.3 do handoff S51).

O que a S52 fez: commit do handoff S51 (docs), geração do APK debug, instalação no Redmi Note 8, início do teste manual do Item 7. Validações confirmadas: erro amigável no timeout funciona (S52d). Diagnóstico do mapa feito (S52e — cosmético, não bug). Diagnóstico da "barra de baixo" NÃO confirmado (S52f — precisa de descrição do usuário).

O que a S52 NÃO fez (fica para a S53):

    Reverter o bloco temporário do api.dart (S52c) — obrigatório antes de qualquer commit futuro.

    Registrar o resultado do 7.10 (401 global no celular) — foi provavelmente testado, mas o resultado não foi reportado antes da cota acabar. Se o app deslogou ao entrar no feed, a Onda B está validada; se não, diagnosticar (Seção 5.7 do handoff S51).

    Completar os fluxos 7.3–7.9 do Item 7 (feed, perfil, upload, comentários, export, busca, follow) — status de cada um não registrado.

    Resolver a "barra de baixo estranha" (S52f) — precisa de descrição do usuário primeiro.

    Commitar o resultado do teste (se tudo passar) ou corrigir (se falhar).

    Itens herdados: Item 8 (splash/ícone), Item 10 (keystore), Item 13 (BOM).

Ação imediata da S53:

    cd D:\Rumo; git status --short --untracked-files=all → esperado: M mobile/lib/services/api.dart (bloco temporário) + possivelmente outros.

    Reverter o bloco temporário (Seção 5.5.3 do handoff S51): remover as 5 linhas do // TESTE TEMPORÁRIO e confirmar com Select-String "TESTE TEMPORÁRIO" → zero ocorrências.

    Perguntar ao usuário o resultado do 7.10 (deslogou? caiu no /login? travou? loop? tela cinza?).

    Perguntar a descrição da "barra de baixo estranha".

    Continuar o teste do Item 7 (7.3–7.9).

Percentual consolidado (fim da S52): ~92% (inalterado em relação à S51 — a Onda B está commitada mas não validada; a validação comportamental pendente é o que falta para o Mobile subir de ~99% para ~99,5% e o MVP de ~92% para ~92,5%).
SEÇÃO 2 — PRODUÇÃO E AMBIENTE

    Backend: https://rumo-api-5s0b.onrender.com

    Frontend Web: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

    Flutter: 3.47.9 / Dart 3.13.7 (C:\Users\nasci\flutter)

    SO: Windows 11 (26H2), PowerShell 5.1

    Python: 3.13.7 (venv em D:\Rumo\backend\venv)

    Android SDK: C:\Users\nasci\AppData\Local\Android\Sdk (SDK 36.0.0, NDK 27.0)

    Android Studio: C:\Program Files\Android\Android Studio\bin\studio64.exe

    Celular de teste: Redmi Note 8 (Android 10, API 29, arm64) — c767cacd no flutter devices. APK debug instalado na S52 (banner "DEBUG" visível — esperado em debug).

    Emulador: emulador1 — NÃO usar (S45g)

    Docker Desktop: instalado e rodando. rumo-postgres (postgis/postgis:16-3.4, 5432), rumo-redis (redis:7-alpine, 6379), rumo_postgres_test (postgis/postgis:16-3.4, 5433 — sob demanda).

Git ao fim da S52 (esperado após reverter o bloco temporário):
text

49b4275  (HEAD -> main, origin/main) feat(mobile): tratamento global de 401 + refreshListenable (Sessao 51, 10.4 Onda B)
<novo_hash>  docs: handoff da Sessao 51 (10.4 Onda B implementada, teste manual pendente, licoes S51a-f)
9753ed9  docs: handoff da Sessao 50 (10.4 Onda A completa, licoes S50a-e)
3c534ec  feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A)
82d58de  docs: handoff da Sessao 49 (10.2 completo, licoes S49a-d)
211a713  feat(mobile): tela de cadastro + rota /register + register no ApiClient/AuthService (Sessao 49, 10.2 completo)

⚠️ Atenção: o git status no início da S53 deve mostrar M mobile/lib/services/api.dart (bloco temporário do teste 7.10, S52c). Reverter antes de commitar qualquer coisa.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 52
3.1 Verificação inicial (S48e)

O usuário rodou git log --oneline -3 e git status --short --untracked-files=all:
text

49b4275 (HEAD -> main, origin/main) feat(mobile): tratamento global de 401 + refreshListenable (Sessao 51, 10.4 Onda B)
9753ed9 docs: handoff da Sessao 50 (10.4 Onda A completa, licoes S50a-e)
3c534ec feat(mobile): empty states amigáveis + spinner no like (Sessao 50, 10.4 Onda A)
 M docs/HANDOFF.md

Conclusão: a Onda B já estava commitada (49b4275) desde antes da S52. Faltava só commitar o handoff S51 (docs/HANDOFF.md).
3.2 Commit do handoff S51

O usuário executou git add docs/HANDOFF.md; git commit -m "docs: handoff da Sessao 51 (...)"; git push. Working tree ficou limpo. Repo em estado consistente: código da Onda B + docs, ambos commitados e pushados.
3.3 Geração do APK debug e instalação no Redmi

Decisão: testar no celular via APK (mais prático que cabo/emulador). flutter build apk --debug gerou D:\Rumo\mobile\build\app\outputs\flutter-apk\app-debug.apk. Usuário instalou no Redmi Note 8. Banner "DEBUG" no canto superior direito é esperado (build debug).
3.4 Bloco temporário do 401 no api.dart

Para testar o 7.10 (fiação 401 → logout → redirect), o usuário inseriu o bloco temporário no _send do api.dart, entre as linhas 820 e 821 (antes da montagem da URI). O bloco é:
dart

    // TESTE TEMPORÁRIO — REMOVER DEPOIS (Sessao 51, Secao 5.5)
    if (path.contains('/activities')) {
      onUnauthorized?.call();
      throw ApiException(401, 'Token expirado (teste)');
    }

Status: inserido, não revertido. Precisa ser removido na S53 (Seção 5.5.3 do handoff S51).
3.5 Validações confirmadas na S52

    Erro amigável no timeout: o usuário viu "servidor demorando, tente novamente" em vez da mensagem crua. Confirma friendlyErrorMessage + ApiException(0, ...) no caminho de timeout. (Não é o 401 global.)

    Feed funcional: a screenshot mostra atividades reais carregando (produser, "Teste mapa - rota sintetica", "Caminhada vespertina"), com mapa, distância, tempo, kcal, data, contador de like/comentário. O feed está renderizando corretamente.

    Mapa funcional: ruas, traçado da rota, tiles do OSM carregando. A faixa amarela/preta é cosmética (S52e).

3.6 Diagnóstico do mapa (S52e)

activity_map.dart:

    Linha 3: import 'package:flutter_map/flutter_map.dart';

    Linhas 17, 58, 62, 63: comentário + _osmTileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png' + _osmAttribution = 'OpenStreetMap contributors' + _esriAttribution = ...

    Linhas 111, 172: TileLayer(...) (dois: um para o mapa normal, um para satélite)

    Linhas 115–116, 204–206: SimpleAttributionWidget(source: Text(_satelite ? _esriAttribution : _osmAttribution))

A faixa amarela/preta é placeholder/overlay padrão do flutter_map. Não é bug. Confirmar na S53 se some ao carregar (cosmético) ou fica (investigar SimpleAttributionWidget). Não vale a pena mexer agora.
3.7 "Barra de baixo estranha" (S52f — NÃO CONFIRMADO)

O usuário mencionou que "já tinha relatado e consertado, só que voltou". Não foi possível diagnosticar (cota acabou antes). Hipóteses: (a) FAB cobrindo o último card do feed (visível na screenshot); (b) insets/altura da NavigationBar; (c) cor/label; (d) outra coisa. Não assumir. Na S53, pedir descrição + trecho do feed_page.dart/profile_page.dart relevante.
3.8 Commits da S52

Um commit: o handoff S51 (docs/HANDOFF.md). Nenhum commit de código na S52 (a Onda B já estava commitada; o bloco temporário é de teste e não deve ser commitado).
SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)

Nenhuma mudança de código no backend desde S39. 180 testes passando. Contratos relevantes (inalterados desde S49):

    POST /auth/register (S49d): público, @limiter.limit("3/hour"). Body = UserCreate (email, username, password, full_name?, weight_kg?, height_cm?, birth_date?). 201 → UserResponse. 409 com dois detail diferentes: "Email já cadastrado" / "Username já cadastrado". 422 validação. 429 rate limit.

    PUT /users/me aceita weight_kg?, height_cm?, full_name? (sem username/email/birth_date — S48c).

    ApiException.message já contém o detail do FastAPI. O tradutor só formata o que já existe.

Nota sobre 401: o backend retorna 401 quando o token JWT está ausente, malformado ou expirado. Não há endpoint de revogação de token — o que torna o teste "real" de token expirado difícil em prod (por isso o bloco temporário no _send).
SEÇÃO 5 — TESTE MANUAL — STATUS NA S52 (o que falta na S53)

O teste manual do Item 7 (10 fluxos) foi parcialmente executado. Status registrado:
#	Fluxo	Status S52	Observação
7.1	Cadastro	Não registrado	Atenção: rate limit 3/h por IP
7.2	Login	Implicitamente OK	O app está logado (produser)
7.3	Feed	Parcialmente OK	Feed carrega (screenshot), mas rolar/pull-to-refresh/like/abrir detalhe não registrados
7.4	Perfil	Não registrado	
7.5	Upload	Não registrado	
7.6	Comentários	Não registrado	
7.7	Export	Não registrado	
7.8	Busca	Não registrado	
7.9	Follow	Não registrado	
7.10	401 global	NÃO REGISTRADO	Bloco temporário inserido, mas resultado não reportado. Prioridade máxima na S53.
5.1 Roteiro do 7.10 (prioridade máxima na S53)

Com o bloco temporário no api.dart (ainda presente no disco do usuário — S52c):

    Abrir o app no Redmi (está logado).

    Sair do feed e voltar (ou puxar para atualizar, ou trocar de aba e voltar). O app tenta GET /activities → bloco temporário dispara onUnauthorized?.call() → AuthService.logout() → refreshListenable → redirect.

    Esperado: o app desloga sozinho e cai no /login, sem travar, sem loop, sem tela cinza.

    Se acontecer: Onda B validada. 🎉

    Se não acontecer: diagnosticar com a Seção 5.7 do handoff S51:

        App não desloga: (a) bloco no lugar errado; (b) onUnauthorized não setado; (c) _handleUnauthorized não chama logout().

        App desloga mas não navega: refreshListenable: _auth ausente no main.dart.

        App desloga com senha errada: alguém chamou onUnauthorized no login (verificar api.dart).

5.2 Reversão obrigatória (S52c)

Após o 7.10 (passando ou falhando):
powershell

# 1) Remover o bloco temporário do api.dart (editor)
# 2) Confirmar que sumiu:
cd D:\Rumo\mobile\lib\services
Get-Content api.dart -Encoding UTF8 | Select-String -Pattern "TESTE TEMPORÁRIO"
# Esperado: zero ocorrências
# 3) Rebuild limpo (opcional, para APK final sem o bloco):
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" build apk --debug

Se esquecer de reverter: o app desloga toda vez que abrir o feed. Não commitar o api.dart com o bloco.
SEÇÃO 6 — COMMITS PENDENTES / ESTADO DO REPO

Estado esperado no início da S53:
powershell

cd D:\Rumo
git log --oneline -3
git status --short --untracked-files=all

Esperado:

    HEAD == origin/main == commit do handoff S51 (docs), com 49b4275 logo abaixo.

    git status deve mostrar M mobile/lib/services/api.dart (bloco temporário do 7.10, S52c) — reverter antes de commitar.

Após reverter o bloco temporário: working tree limpo. Nenhum commit pendente de código. O próximo commit será o que resultar do teste do Item 7 (se houver correção) ou o commit deste handoff S52.

Commit deste handoff (quando colar em docs/HANDOFF.md):
powershell

cd D:\Rumo
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 52 (teste manual parcial no Redmi, diagnostico do mapa, licoes S52a-g)"
git push

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

Build do APK debug:
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" build apk --debug
# Saída: D:\Rumo\mobile\build\app\outputs\flutter-apk\app-debug.apk

Instalar no Redmi (adb):
powershell

adb install -r D:\Rumo\mobile\build\app\outputs\flutter-apk\app-debug.apk

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

        600 linhas: 3 partes:

    powershell

    Get-Content <arquivo> -Encoding UTF8 | Select-Object -First 400
    Get-Content <arquivo> -Encoding UTF8 | Select-Object -Skip 400 -First 400
    Get-Content <arquivo> -Encoding UTF8 | Select-Object -Skip 800

    NUNCA usar Get-Content arquivo -Skip N — não existe no PS 5.1 (S50a).

Descobrir onde está algo no projeto:
powershell

cd D:\Rumo\mobile\lib
Get-ChildItem -Recurse -Filter *.dart | Select-String -Pattern "termo" -CaseSensitive:$false | Select-Object Path, LineNumber, Line | Format-Table -AutoSize -Wrap

Contar linhas de um arquivo (para escolher quantas partes):
powershell

(Get-Content D:\Rumo\mobile\lib\caminho\arquivo.dart -Encoding UTF8).Count

SEÇÃO 8 — DÍVIDAS TÉCNICAS E BACKLOG DETALHADO
8.1 Fechadas na S52

    Commit do handoff S51 (docs/HANDOFF.md). ✅

    Diagnóstico do mapa (faixa amarela/preta "POWERED BY 69 PIXELS"). ✅ Cosmético, não bug (S52e).

    Validação do erro amigável no timeout (S52d). ✅ friendlyErrorMessage + ApiException(0, ...) funcionam.

8.2 Abertas / pendentes (S53)

    Reverter bloco temporário do api.dart (S52c) — obrigatório antes de qualquer commit futuro.

    Registrar resultado do 7.10 (401 global no celular). Prioridade máxima.

    Completar fluxos 7.3–7.9 do Item 7.

    Diagnosticar "barra de baixo estranha" (S52f) — precisa de descrição do usuário primeiro.

    Commitar resultado do teste (se passar) ou corrigir (se falhar).

8.3 Backlog para S53+ (passo a passo)

Item 7 — Validação no Redmi Note 8 (prioridade alta, ~1 sessão)

    Status: parcialmente feito na S52. Faltam 7.3–7.9 + registro do 7.10.

    Roteiro completo na Seção 8.3 do handoff S51 (inalterado).

    Atenção: 7.1 (cadastro) tem rate limit 3/h — testar uma vez e validar bem.

Item 8 — Splash + ícone no launcher (prioridade média, ~0,5 sessão)

    Bloqueio: precisa de um PNG 1024×1024 do ícone do Rumo (não existe — S42k).

    Usar flutter_launcher_icons e flutter_native_splash (dev dependencies).

    Detalhes na Seção 8.3 do handoff S51.

Item 10 — Keystore + signingConfigs (prioridade média, só após item 7, ~0,5 sessão)

    Detalhes na Seção 8.3 do handoff S51.

    Atenção: o BOM em build.gradle.kts (S43d / item 13) pode atrapalhar — remover antes.

Item 13 — Remover BOM de build.gradle.kts e AndroidManifest.xml (prioridade baixa, ~0,1 sessão)

    Detalhes na Seção 8.3 do handoff S51.

    Pode ser feito junto com o item 10 (mesmo arquivo).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S52)

    S21–S51: acordos mantidos (código completo, handoff completo, aviso de limite, percentual, seguir recomendações).

    S52: o usuário reforçou os mesmos 5 pontos no início da sessão:

        "sempre seguir suas recomendações" (mesmo que atualize só parte do código).

        "sempre colocar o código completo".

        "fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo de 70% a 80%".

        "informar o percentual de quanto nosso projeto já está pronto, isso depois de fazermos o handoff no final do chat".

        "gostaria que você avisasse se caso isso for ocorrer [o chat acabar no meio do código] — não estou falando apenas do limite do chat, mas sim o limite do site (IA)". O assistente respondeu com honestidade: o limite do site/IA não é mensurável pelo assistente. O que dá para fazer: entregar arquivo completo um por um, validar imediatamente, nunca deixar código pela metade entre duas mensagens, handoff enxuto e frequente. Isso é o máximo garantível; o resto está fora do alcance. A S52 confirmou isso na prática: o usuário avisou "resta 37% da cota" — o assistente não teria como prever esse número; só o usuário consegue.

    S52 — decisão de fechamento: ao ser avisado da cota em 37%, o assistente parou imediatamente e propôs o handoff, sem tentar "espremer" mais um diagnóstico. O usuário concordou. Este handoff foi entregue.

Acordos novos da S52: S52a–S52g (ver Seção 0).
SEÇÃO 10 — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 52)
Área	%	Observação
Backend	~95%	inalterado (180 testes, ruff; prod OK)
Web	~99%	inalterado (prod OK)
Mobile	~99%	inalterado em relação à S51 (Onda B commitada, mas validação comportamental ainda pendente — 7.10 não registrado)
Bloqueadores não-código	~25%	inalterado (contas Google Play/Apple, keystore)
MVP consolidado	~92%	inalterado em relação à S51 (a validação pendente é o que falta para subir)

Variação em relação à S51: nenhuma (0%). A S52 foi de verificação/teste/diagnóstico, não de implementação nova. O Mobile e o MVP só sobem quando o 7.10 for validado (Mobile → ~99,5%, MVP → ~92,5%).

Estimativa até "pronto para submeter":

    Registrar 7.10 + completar 7.3–7.9 + reverter bloco: ~0,5–1 sessão.

    Item 8 (splash/ícone): ~0,5 sessão (precisa criar PNG do ícone).

    Item 10 (keystore) + item 13 (BOM): ~0,5–1 sessão.

    Total: ~1,5–2,5 sessões + 1 de review. ~2,5–3,5 sessões.

SEÇÃO 11 — BACKLOG DA SESSÃO 53 (planejamento)

Base: repo em 49b4275 + commit do handoff S51. Working tree deve ter M mobile/lib/services/api.dart (bloco temporário do 7.10, S52c).

    Verificar git status (S48e). Esperado: M mobile/lib/services/api.dart.

    Perguntar ao usuário:

        Resultado do 7.10: o app deslogou e caiu no /login ao entrar no feed? Travou? Loop? Tela cinza?

        Descrição da "barra de baixo estranha" (S52f): o que exatamente está estranho?

    Reverter o bloco temporário do api.dart (Seção 5.2 deste handoff / Seção 5.5.3 do handoff S51). Confirmar com Select-String "TESTE TEMPORÁRIO" → zero ocorrências.

    Se o 7.10 passou: Onda B validada. Commit do handoff S52. Seguir para 7.3–7.9.

    Se o 7.10 falhou: diagnosticar (Seção 5.7 do handoff S51), corrigir, revalidar, só então commitar.

    Se a "barra de baixo" for o FAB cobrindo o card: pedir o trecho do feed_page.dart (e profile_page.dart, se aplicável), corrigir com padding no fim do ListView/SliverPadding.

    Continuar o Item 7 (7.3–7.9).

    Depois: Item 8 (splash/ícone — precisa criar PNG) → Item 10 (keystore) + Item 13 (BOM).

Ordem sugerida: verificar status → reverter bloco → registrar 7.10 → diagnosticar "barra de baixo" → completar 7.3–7.9 → commit do handoff S52 → Item 8 → Item 10 + Item 13.
SEÇÃO 12 — RESUMO EXECUTIVO PARA A S53

    Primeiro: git status (S48e). Esperado: M mobile/lib/services/api.dart (bloco temporário do 7.10).

    Perguntar ao usuário: (a) resultado do 7.10 (deslogou/não deslogou, travou/loop/tela cinza); (b) descrição da "barra de baixo estranha".

    Reverter o bloco temporário do api.dart (obrigatório — Seção 5.2 deste handoff). Confirmar com Select-String "TESTE TEMPORÁRIO" → zero ocorrências.

    Se o 7.10 passou: Onda B validada. Commitar o handoff S52. Seguir para 7.3–7.9.

    Se o 7.10 falhou: diagnosticar (Seção 5.7 do handoff S51), corrigir, revalidar, só então commitar.

    Depois: completar Item 7 (7.3–7.9) → Item 8 (splash/ícone) → Item 10 (keystore) + Item 13 (BOM).

    O que NÃO fazer: reconstruir arquivo a partir de Select-String (S47a); assumir AuthService.instance (S47b); rodar pytest sem container (S47c); traduzir catch (_) silencioso/rollback/403 como erro (S48b); confiar no handoff sem git log/git status (S48e); usar ?key: value para valor opcional em map literal (S49b — é key: ?value); esquecer de incluir /register no redirect (S49c); usar Get-Content -Skip no PS 5.1 (S50a — usar | Select-Object -Skip); assumir que pull-to-refresh/spinner no upload precisam ser feitos (S50b/S50d — já existiam); esquecer de reverter o bloco temporário do api.dart (S52c — senão o app desloga toda vez que abrir o feed); assumir que a faixa amarela/preta do mapa é bug (S52e — é cosmética do flutter_map); assumir o que é a "barra de baixo estranha" sem perguntar (S52f — pedir descrição primeiro).

    Regra de ouro: não tenho acesso ao disco. Pedir Get-Content inteiro. Nunca inventar caminho. Nunca reescrever arquivo não recebido.

PERCENTUAL DE PRONTIDÃO (fim da S52)

Backend ~95% · Web ~99% · Mobile ~99% · Bloqueadores não-código ~25% · MVP consolidado ~92%

Variação em relação à S51: nenhuma. A S52 foi de verificação/teste/diagnóstico. O Mobile e o MVP só sobem quando o 7.10 for validado (Mobile → ~99,5%, MVP → ~92,5%).