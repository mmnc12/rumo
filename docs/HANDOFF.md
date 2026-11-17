Handoff — Rumo (backend + frontend + mobile) — Sessão 39
LEIA A SEÇÃO 0 INTEIRA ANTES DE QUALQUER COISA. As regras S21–S39 são o contrato de trabalho. Não são sugestões.

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚡ REGRA S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça. ⚡ Esta regra vale TAMBÉM para comandos PowerShell com here-string @' ... '@: nunca usar "COLE O CONTEÚDO AQUI" como placeholder — o conteúdo tem que ser o arquivo inteiro. (Reforçada na S36 — REGRA S36g; reincidiu na S39 — REGRA S39c.)

⚡ REGRA S21 — não adivinhar nomes de símbolos do projeto. Pedir o model/enum/schema antes de referenciar.

⚡ REGRA S21 — git status antes de qualquer git restore/git checkout. git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>.

⚡ REGRA S22 — Invoke-WebRequest com -UseBasicParsing. Elimina o prompt de segurança do PS 5.1.

⚡ REGRA S22 — validar deploy do Render antes de acusar bug no código. Depois de push, checar openapi.json para a rota nova antes de acusar 422/404/405.

⚡ REGRA S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele. Nunca procurar "ProfilePage-" direto no HTML.

⚡ REGRA S24 — Vercel às vezes demora >90 s para o primeiro deploy após push. Se o hash antigo aparecer após 90 s, rodar o teste de novo. Não presumir bug.

⚡ REGRA S25a — Select-String -SimpleMatch NÃO aceita | como alternância. Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo.

⚡ REGRA S25b — quando lines[−1] for suspeito, confirmar com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo>" antes de concluir. Não dar "OK" nem "corrompido" sem evidência.

⚡ REGRA S25c — antes de pedir git add/git commit de um arquivo que o usuário acabou de salvar, EXIGIR o output do bloco de validação e ESPERAR.

⚡ REGRA S25d — o teste definitivo de "o save pegou" é git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M <arquivo>. Se git status --short vier vazio depois de salvar, o disco é igual ao commitado. O save não pegou.

⚡ REGRA S25e — ao entregar o conteúdo de um arquivo para colar no editor, entregar SEM cerca markdown envolvendo. Entregar o arquivo inteiro como único texto da resposta, sem instruções antes/depois.

⚡ REGRA S26a — no PowerShell 5.1, Invoke-WebRequest -UseBasicParsing devolve resp.Content como STRING, não como byte[]. [System.IO.File]::WriteAllBytes(path, resp.Content) falha. Para texto UTF-8: [System.Text.Encoding]::UTF8.GetBytes(resp.Content). Para bytes crus (ZIP, imagem): resp.RawContentStream.CopyTo(fileStream). Para inspecionar GPX/XML: regex direto no Content.

⚡ REGRA S26b — validar GPX em produção por regex é mais barato que gpxpy + arquivo temporário. Contar <time> distintos com regex no Content responde "o S26 está no ar?" em 3 linhas.

⚡ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Na S39 demorou mais de 5 min (o usuário precisou aguardar). Não é bug. Se >5 min, checar dashboard do Render (Events/Logs) antes de "Manual Deploy".

⚡ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa.

⚡ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde.

⚡ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca.

⚡ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código.

⚡ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora.

⚡ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior.

⚡ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número.

⚡ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }. Declarar sem inicializar quando try/catch cobre todos os caminhos.

⚡ REGRA S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos". Usar -CaseSensitive ou regex \bTODO\b.

⚡ REGRA S30b — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos.

⚡ REGRA S30c — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo. No mobile, SEMPRE pedir Get-ChildItem + arquivos-chave antes de estimar esforço.

⚡ REGRA S31a — em ambiente Windows sem Developer Mode, flutter pub add <plugin_nativo> instala mas avisa que o build vai falhar por symlink. Vale para qualquer plugin com código nativo. flutter analyze passa sem Developer Mode; flutter run/flutter build não.

⚡ REGRA S31b — file_picker 13.x removeu FilePicker.platform, FilePickerResult, PlatformFile.size e PlatformFile.bytes. API nova: FilePicker.pickFiles() estático retorna List<PlatformFile>; PlatformFile.length()/lengthSync(); readAsBytes().

⚡ REGRA S31c — quando Select-String do disco mostrar conteúdo antigo depois do save do editor, contornar via WriteAllText no PowerShell imediatamente.

⚡ REGRA S32a — Select-String -SimpleMatch 'class X' casa PREFIXOS.

⚡ REGRA S32b — Select-String -SimpleMatch '_Simbolo' casa menções em COMENTÁRIOS também.

⚡ REGRA S32c — ao anunciar "esperado ≈ N linhas", CONTAR as linhas do arquivo entregue antes.

⚡ REGRA S32d — nos Select-String de validação, o "esperado" é sempre PISO ou FAIXA, nunca número exato.

⚡ REGRA S33a — alternância em Select-String: SEMPRE -Pattern 'a|b' (sem -SimpleMatch).

⚡ REGRA S33b — "esperado" é SEMPRE piso/faixa, nunca exato.

⚡ REGRA S34a — git rev-parse HEAD:<arquivo> exige path relativo à RAIZ DO REPO. git hash-object aceita path relativo ao CWD.

⚡ REGRA S34b — "esperado" anunciado antes de rodar pode errar mesmo sendo faixa.

⚡ REGRA S34c — ao validar tela mobile no Chrome, confirmar (a) qual usuário está logado, (b) qual URL foi colada, (c) se o flutter run foi reiniciado depois do último commit.

⚡ REGRA S35a — FECHADA na S36. /feed já devolvia autor com chave author; mobile lia user. Solução: FeedItemResponse ganhou user ao lado de author.

⚡ REGRA S36a — MatchCollection[-1] NÃO funciona no PS 5.1. Usar $times[$times.Count - 1].

⚡ REGRA S36b — em bundle minified, Select-String devolve a linha inteira. Usar [regex]::Matches.

⚡ REGRA S36c — ao validar toque no ActivityCard, confirmar PRIMEIRO qual tela está aberta pela URL.

⚡ REGRA S36d — CRÍTICA: Select-String -SimpleMatch com | é sempre erro. Usar -Pattern.

⚡ REGRA S36e — AutomaticKeepAliveClientMixin é @mustCallSuper. Solução de lint: // ignore_for_file: unnecessary_overrides na linha 1.

⚡ REGRA S36f — editor falhou em salvar → WriteAllText com o arquivo inteiro.

⚡ REGRA S36g — comandos com here-string entregam conteúdo REAL, nunca placeholder. Reincidiu na S39c (você colou <COLE O ARQUIVO INTEIRO ACIMA AQUI> como conteúdo; WriteAllText gravou; recuperado via git restore).

⚡ REGRA S37a — conflito de versão de plugin no pub get: ler o erro inteiro antes de tentar consertar. O pub sugere a versão compatível no final do output ("Try upgrading your constraint on X: Y"). Usar a sugestão em vez de adivinhar.

⚡ REGRA S37b — ao adicionar plugin nativo ao pubspec.yaml, o pub get modifica pubspec.lock + windows/flutter/generated_plugin_registrant.cc + windows/flutter/generated_plugins.cmake. Esses 3 entram no commit junto (não são "lixo").

⚡ REGRA S37c — share_plus 13.x: API nova é SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])). A antiga Share.shareXFiles foi removida.

⚡ REGRA S37d — ao testar download no Chrome, o share_plus dispara o download no browser via Share API. O arquivo aparece na barra de downloads do Chrome, não no share sheet do SO (que não existe no Chrome). É o comportamento esperado.

⚡ REGRA S37e — ao adicionar import que parece necessário mas o tipo vem por inferência (Uint8List do result.bytes), o flutter analyze acusa unused_import. Remover o import (não forçar uso).

⚡ REGRA S37f — unnecessary_underscores (Dart 3.7+): (_, __) vira (_, _) em callbacks com múltiplos parâmetros ignorados. O flutter analyze acusa info, não warning.

⚡ REGRA S38a — "esperado" de Select-String é SEMPRE piso/faixa, sem exceção — mesmo quando o arquivo entregue foi contado. O contador do entregue (comentários de cabeçalho, quebras) não bate com o número real de linhas no disco.

⚡ REGRA S38b — Select-String -SimpleMatch com | é sempre erro — reforço da S25a/S33a/S36d depois de reincidência na S38.

⚡ REGRA S38c — o ^ de continuação do PowerShell não é confiável (quebra com linhas em branco entre os ^, e o git add recebe ^ como pathspec literal, abortando). Usar backtick (`) ou — melhor — comando numa linha só.

⚡ REGRA S38d — "esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas. Chutei "~+1500/−50" na S38, o real foi +996/−112. O número que importa é o de arquivos.

⚡ REGRA S39a (NOVA) — GoRouterState no go_router 18.x NÃO tem .context (a ≤14.x expunha .context via wrapper; a 18.x removeu). O builder do GoRoute recebe (BuildContext context, GoRouterState state) — o primeiro parâmetro é o context. Quando o callback precisa do context (raro, mas acontece em fallback de deep-link), use o do builder. Regra prática: no go_router 18.x, GoRouterState só tem matchedLocation, pathParameters, queryParameters, extra, uri, fullPath — sem context, sem pageKey.

⚡ REGRA S39b (NOVA — CRÍTICA) — REGRA S21 vale para o arquivo que está sendo editado, não só pros arquivos novos. Quando o arquivo a editar é grande e tem widgets dependentes, pedir o arquivo + os widgets antes de escrever a primeira linha. Caso S39: entreguei profile_page.dart baseado em memória do handoff S38, assumi StatsMetric (não existe — é ChartMetric), StatsFilters(onPeriodChanged:, onCompareChanged:) (é onChanged(period, compare)), ByTypeList(data:) (é data:, isLoading:, isError:), StatsChart(period: String, ...) (é period: ChartPeriod enum), ActivityCard(showAuthor:) (não existe — é auth:, onTap:, onChanged:, authorUsernameOverride), context.push sem import go_router. 23 erros. Recuperação: git restore + pedir profile_page.dart real + 5 widgets (stats_filters, stats_chart, stats_cards, by_type_list, activity_card). Reentreguei alinhado, No issues found! de primeira.

⚡ REGRA S39c (NOVA) — placeholder literal no here-string do api.dart (reincidência da S36g). Você colou <COLE O ARQUIVO INTEIRO ACIMA AQUI> como conteúdo, e o WriteAllText gravou 1 linha. Recuperação: git restore (o arquivo estava no HEAD). Nota: o fallback git show HEAD:... > ... também corrompeu — no PS 5.1 o > redireciona em UTF-16 LE, e o Dart não lê. Só git restore preserva o encoding do blob. Se git restore não funcionar, o fallback correto é git show HEAD:<arquivo> | Set-Content -Encoding UTF8 <arquivo> (aceita BOM, mas o hash git hash-object difere do HEAD por causa do BOM). Preferir sempre git restore.

O que é LOCAL vs. o que é PRODUÇÃO
LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (180 passed ao fim da S39). Container de teste rumo_postgres_test na porta 5433.

⚡ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).

⚡ Após docker compose up -d, o pg_isready pode responder "no response" no primeiro segundo (container subindo). Rodar pytest ou esperar 5–10 s antes de concluir que o banco está fora.

Estrutura do repo (referência — conferir, não assumir)
text
D:\Rumo
├── .vscode/settings.json
├── backend/ (venv em backend/venv, Python 3.13.7)
│   ├── alembic/
│   ├── app/
│   │   ├── core/ models/ routers/ schemas/ services/
│   │   └── pycache/
│   ├── samples/
│   ├── scripts/
│   ├── tests/ (conftest.py + test_calories + test_comment + test_export
│   │   + test_export_bulk + test_feed + test_follow + test_like
│   │   + test_profile_update + test_stats)
│   │   — 9 arquivos, 180 testes
│   ├── _scratch/ (ignorado pelo git; s33_delta_test.gpx criado na S33)
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│   ├── lib/
│   │   ├── main.dart (StatefulShellRoute + bottom nav desde S32;
│   │   │   +rota /user/:id desde S34;
│   │   │   +rota /search desde S35, atualizada S36 para SearchPage;
│   │   │   +rota /edit-profile desde S39 ← NOVO)
│   │   ├── models/ (activity.dart, activity_track.dart, comment.dart,
│   │   │   stats.dart, user.dart ← S34, user_me.dart ← EDITADO S39
│   │   │   (+weightKg, +heightCm, +birthDate, fromJson defensivo
│   │   │   via `(json[...] as num?)?.toDouble()`))
│   │   ├── pages/ (activity_detail_page.dart ← S37,
│   │   │   edit_profile_page.dart ← NOVO S39 (384 linhas),
│   │   │   feed_page.dart, login_page.dart,
│   │   │   profile_page.dart ← EDITADO S39 (+botão "Editar perfil"
│   │   │   no _ProfileHeader + _openEditProfile via context.push<UserMe>),
│   │   │   search_page.dart ← S36, upload_page.dart ← S31,
│   │   │   user_profile_page.dart)
│   │   ├── services/ (api.dart ← EDITADO S39 (+put wrapper +
│   │   │   +updateMe + case 'PUT' no _send), auth_service.dart)
│   │   ├── utils/ (download.dart ← S37, format.dart ← S33)
│   │   └── widgets/ (activity_card.dart, activity_map.dart,
│   │       by_type_list.dart ← S33, like_button.dart,
│   │       stats_cards.dart ← S33,
│   │       stats_chart.dart ← S38 (fl_chart; enums ChartPeriod/ChartMetric),
│   │       stats_filters.dart ← S38 (onChanged(period, compare)))
│   ├── pubspec.yaml (file_picker: ^13.3.3, fl_chart: ^1.1.0 ← S38
│   │   (resolveu em 1.3.1), go_router: ^18.1.2, path_provider: ^2.1.5,
│   │   share_plus: ^13.3.1, name: rumo_mobile)
│   ├── pubspec.lock
│   └── windows/flutter/ (generated_plugin_registrant.cc,
│       generated_plugins.cmake — modificados pelo pub get S37.
│       S38 e S39 NÃO tocaram nesses — fl_chart é Dart puro.)
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md
⚡ mobile/lib/pages/user_search_page.dart NÃO EXISTE MAIS (removido na S36). Foi substituído por search_page.dart (2 abas: Usuários | Atividades).

⚡ mobile/lib/pages/edit_profile_page.dart é NOVO na S39 (384 linhas). Criado do zero.

Como rodar comandos Flutter
Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste
prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades (7 + 1 sintética da S33), 34.08 km. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min) usada pra validar o S26 e o export GPX da S37. Tem atividade sintética "Teste delta S33 (janela anterior)" (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null). Username no backend: produser. Na S39, o PUT /users/me setou weight_kg=80.0 e height_cm=null (validado via HTTP em produção) — estado atual do prod@rumo.com no backend.

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2 e Prod2 segue prod (bidirecional desde a validação manual da S37 — o handoff da S37 dizia "Prod2 seguindo: 0", desatualizado). Usado pra validar abas Seguidores/Seguindo na S37 e o short-circuit em 403 dos stats na S38.

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422 — ou 405 se a rota não existir no método).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21 à S39)
SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.

PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes.

VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo.

VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<simbolo>" antes de build/test.

NUNCA placeholder no código entregue (S21) nem em comandos com here-string (S36g). Reincidiu na S39c.

Não adivinhar nomes de símbolos (S21). Reforçada na S39b — vale pro arquivo que está sendo editado, não só pros arquivos novos.

git status + git log antes de git restore (S21).

Invoke-WebRequest sempre com -UseBasicParsing (S22).

Validar openapi.json antes de acusar bug em rota nova (S22).

Validar bundle da Vercel baixando index-*.js (S23).

Vercel pode demorar >90 s no primeiro deploy (S24).

Select-String -SimpleMatch não aceita | como alternância (S25a, reforçada S33a, S36d, S38b).

Confirmar lines[−1] suspeito com Get-Content | Select-Object -Last N (S25b).

Exigir output do bloco de validação antes de pedir commit (S25c).

Teste definitivo do save: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M (S25d).

Entregar conteúdo de arquivo para colar sem cerca markdown (S25e).

PS 5.1: resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[] (S26a).

Validar GPX em prod por regex no Content (S26b).

Render free tier pode demorar >3 min para redeployar após push (S26c). Na S39 demorou >5 min.

Commitar o handoff pendente ANTES de qualquer outra coisa na abertura (S27a).

Ordem fixa dos blocos da Fase 0: handoff → log/status → build → docker/pytest → prod back → prod front (S27b).

Antes de aceitar o escopo do handoff anterior como verdade, pedir TODOS os arquivos que o contrato toca e confirmar o gap real (S28a).

Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada, não mudança de código (S28b).

Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).

Vercel reescreve hash de chunk ao servir; sinal de "novo no ar" = hash mudou vs sessão anterior + helper no bundle (S29b).

Contar as ocorrências reais antes de anunciar "esperado Nx" num Select-String (S29c).

ESLint no-useless-assignment: declarar let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).

Select-String "TODO" casa case-insensitive — usar -CaseSensitive ou regex \bTODO\b (S30a).

Componente genérico com semântica oposta: prop booleana default-false, 4 casos (S30b).

Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + api.dart + telas (S30c).

Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink (S31a).

file_picker 13.x: API estática + length()/readAsBytes() (S31b).

Select-String do disco mostrando conteúdo antigo após save do editor → WriteAllText no PowerShell (S31c, reforçada S36f).

Select-String -SimpleMatch 'class X' casa prefixo (S32a).

Select-String -SimpleMatch '_Simbolo' casa menções em comentários (S32b).

Anunciar "esperado ≈ N linhas" só depois de CONTAR o arquivo entregue (S32c).

Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA (S32d, reforçada S33b, S34b, S38a).

Alternância em Select-String: SEMPRE -Pattern 'a|b' (S33a, S36d).

"Esperado" é SEMPRE piso/faixa (S33b).

git rev-parse HEAD:<arquivo> exige path relativo a RAIZ do repo (S34a).

"Esperado" anunciado antes de rodar pode errar mesmo sendo faixa (S34b).

Validar tela mobile no Chrome: confirmar usuário logado, URL colada e restart do flutter run (S34c).

S35a fechada: /feed agora devolve user + author (S36).

MatchCollection[-1] não funciona no PS 5.1 — usar $times[$times.Count - 1] (S36a).

Em bundle minified, Select-String devolve a linha inteira — usar [regex]::Matches (S36b).

Ao validar toque no ActivityCard, confirmar PRIMEIRO qual tela está aberta pela URL (S36c).

Select-String -SimpleMatch com | é sempre erro — usar -Pattern (S36d, CRÍTICA).

AutomaticKeepAliveClientMixin é @mustCallSuper — super.build obrigatório. Solução de lint: // ignore_for_file na linha 1, NÃO // ignore: local (S36e).

Editor falhou 2× em salvar search_page.dart — WriteAllText é a solução (S36f).

Comandos com here-string entregam conteúdo REAL, nunca placeholder (S36g). Reincidiu S39c.

Ler o erro inteiro do pub get antes de tentar consertar — o pub sugere a versão compatível no final (S37a).

Plugin nativo: pub get modifica pubspec.lock + 2 arquivos windows/flutter/generated_* — os 3 entram no commit (S37b).

share_plus 13.x: SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])) (S37c).

Download no Chrome via share_plus dispara download no browser, não share sheet do SO (S37d).

Import não usado por inferência de tipo → remover, não forçar uso (S37e).

unnecessary_underscores: (_, __) vira (_, _) (S37f).

"Esperado" de Select-String é SEMPRE piso/faixa — mesmo contando o arquivo entregue (S38a).

Select-String -SimpleMatch com | é SEMPRE erro — em dúvida, -Pattern (S38b, reforço da S25a/S33a/S36d).

^ de continuação do PowerShell não é confiável — usar backtick ou uma linha só (S38c).

"Esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas (S38d).

GoRouterState no go_router 18.x NÃO tem .context — usar o 1º parâmetro do builder (S39a).

REGRA S21 vale pro arquivo que está sendo editado, não só pros novos — pedir o arquivo + widgets dependentes antes de escrever (S39b, CRÍTICA).

Só git restore preserva o encoding do blob — git show HEAD:... > ... no PS 5.1 grava UTF-16 LE e corrompe (S39c).

Processo que o usuário elogiou na S21–S39 (para manter)
Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).

SEÇÃO 1 — TL;DR para quem chega agora
Backend: 180 testes passando LOCALMENTE, 0 warnings. S39 adicionou PUT /users/me (commit 9d52470). FeedItemResponse expõe autor em author (web) + user (mobile) desde S36. Todos os endpoints do MVP em produção.

Web: intocado desde S30. S39 não tocou no web — a paridade web do "Editar perfil" fica pra S40 (decisão travada no handoff S38 §8: "S39 = OPÇÃO 3a, só backend + mobile; web fica pra S40"). Build/lint limpos.

Mobile: flutter analyze limpo. S39 adicionou:

edit_profile_page.dart (NOVO, 384 linhas) — StatefulWidget com 3 TextFormField (peso, altura, nome completo). Prefill do UserMe current. Botão "Limpar" ao lado de cada campo numérico (manda null explícito). Validação client-side espelhando o backend (weight_kg 0–500, height_cm 0–300, full_name ≤120). _buildBody só envia campos que mudaram ou foram limpos (respeita exclude_unset do backend). Navigator.pop(updated) com o UserMe pós-update.

api.dart — +put() wrapper público, +updateMe() (PUT /users/me), +case 'PUT': no _send. Import de user_me.dart adicionado.

main.dart — +rota /edit-profile (fora do shell, antes do StatefulShellRoute), com extra: UserMe via context.push. Fallback de deep-link sem extra → context.go('/profile') via WidgetsBinding.addPostFrameCallback.

profile_page.dart — +_openEditProfile() (via context.push<UserMe>), +onEdit no _ProfileHeader, +Wrap com "Editar perfil" + "Sair".

user_me.dart (editado por você) — +weightKg, +heightCm, +birthDate com fromJson defensivo.

Endpoints relevantes para a S39 (backend novo)

text
PUT /users/me                                            — auth: Bearer JWT (self)
  body: { weight_kg?: float(0,500), height_cm?: float(0,300), full_name?: str(≤120) }
  response 200: UserResponse (mesmo shape do /auth/me)
  erros: 401 (sem token), 422 (validação Pydantic: range, max_length, extra="forbid")
  semântica: ausente → não toca; null → limpa; valor → atualiza (exclude_unset)
  proibidos: email, username, senha (extra="forbid" → 422)
  rota declarada ANTES de /{user_id} (mesma lição do /search — evita 422)
S39 — validação manual no Chrome (5/5):

Bottom nav → Perfil → _ProfileHeader com "Editar perfil" + "Sair" no rodapé: ✅

Toca "Editar perfil" → abre EditProfilePage com campos preenchidos do GET /auth/me: ✅

Preenche peso/altura/nome, Salvar → volta pro Perfil, header reflete novo nome: ✅

"Limpar" no peso → Salvar → peso some, volta pro Perfil: ✅

Cancelar → volta sem mudar nada: ✅

Validação HTTP em produção (após Render redeployar): [BE.1-retry] = OK - PUT /users/me no ar; [BE.3-retry] = OK weight_kg=80 height_cm=180; [BE.4-retry] = OK weight_kg=80 height_cm= (null). O prod@rumo.com no backend agora tem weight_kg=80.0 e height_cm=null (estado pós-validação).

Commits S39:

text
e251057 (HEAD -> main, origin/main) feat(mobile): EditProfilePage consumindo PUT /users/me (Sessao 39)
9d52470 feat(backend): PUT /users/me para editar weight_kg e height_cm (Sessao 39)
e0e71f7 docs: handoff da Sessao 38
c9543fb feat(mobile): filtros period/compare + charts weekly/monthly (Sessao 38)
d4b8c8b docs: handoff da Sessao 37
SEÇÃO 2 — PRODUÇÃO E AMBIENTE
Backend: https://rumo-api-5s0b.onrender.com

Docs Backend: https://rumo-api-5s0b.onrender.com/docs

Frontend Web: https://rumo-wheat.vercel.app

Repo local: D:\Rumo

Mobile: D:\Rumo\mobile

Web: D:\Rumo\web (scripts: dev, build, lint, preview)

Flutter: 3.47.9 / Dart 3.13.7 (em C:\Users\nasci\flutter)

Docker Desktop: 4.93.0 (engine 29.8.1, compose v5.5.1)

SO: Windows, PowerShell 5.1

Python: 3.13.7 (venv em D:\Rumo\backend\venv) — NÃO usar 3.14

Venv backend: D:\Rumo\backend\venv (ativa com .\venv\Scripts\Activate.ps1)

Deps mobile (S31/S32/S33/S34/S35/S36/S37/S38/S39): file_picker: ^13.3.3, fl_chart: ^1.1.0 (resolveu em 1.3.1), go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1. Package name: rumo_mobile.

Git (estado ao fim da Sessão 39):

text
e251057 (HEAD -> main, origin/main) feat(mobile): EditProfilePage consumindo PUT /users/me (Sessao 39)
9d52470 feat(backend): PUT /users/me para editar weight_kg e height_cm (Sessao 39)
e0e71f7 docs: handoff da Sessao 38
c9543fb feat(mobile): filtros period/compare + charts weekly/monthly (Sessao 38)
d4b8c8b docs: handoff da Sessao 37
15f7602 feat(mobile): export CSV/GPX (unitario + lote) + followers/following (Sessao 37)
b05e870 docs: handoff da Sessao 36
dba8594 refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36)
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36)
86179f2 feat(backend): expoe user no FeedItemResponse + testes de /feed (Sessao 36)
8bff66b docs: handoff da Sessao 35
199040d feat(mobile): rota /search fora do shell (Sessao 35)
d71d9fb feat(mobile): busca no feed + link do autor (Sessao 35)
25778ed feat(mobile): busca de usuarios (Sessao 35)
2b312ec docs: handoff da Sessao 34
Working tree limpo. S39 adicionou 2 commits (9d52470 backend + e251057 mobile, 5 files changed, +582/−46 no mobile; 4 files changed, +206/−3 no backend).
Pendente: docs/HANDOFF.md da S39 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 39.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 39
3.1 Fase 0 — validação de estado inicial
Não foi executada formalmente na S39. Você abriu a sessão já com o commit 9d52470 (backend PUT /users/me) feito fora do chat (na verdade, você commitou durante a sessão, provavelmente numa sessão anterior/pausa), e o handoff S38 não estava commitado (e0e71f7 é o docs: handoff da Sessao 38 que já estava lá). O git log inicial (que você não colou formalmente, mas o estado do git status mostrou) era 9d52470 no topo, origin/main em e0e71f7.

Desvio operacional: a Fase 0 (REGRA S27b) não rodou completa (build/lint, docker/pytest, prod back/front). O pytest só rodou depois do commit e251057 (180 passed, ruff limpo). Se quiser seguir o processo à risca, a S40 abre com a Fase 0 completa.

3.2 Fase 1 — descoberta
O que você tinha feito antes de me chamar:

Backend PUT /users/me (9d52470): routers/users.py (+26), schemas/user.py (+22), services/user_service.py (+50), tests/test_profile_update.py (+111) — 7 testes novos.

Mobile user_me.dart editado (working tree): +weightKg, +heightCm, +birthDate com fromJson defensivo ((json[...] as num?)?.toDouble()).

Primeiro contato — você colou um log de terminal mostrando que o api.dart tinha 1 linha (o placeholder <COLE O ARQUIVO INTEIRO ACIMA AQUI>), resultado do here-string sem substituição (S39c). flutter analyze acusava 68 issues, todos cascata do api.dart corrompido.

Recuperação da S39c:

git status --short mobile/lib/services/api.dart → M

git --no-pager log --oneline -3 -- mobile/lib/services/api.dart → topo c9543fb (S38)

git restore mobile/lib/services/api.dart → 751 linhas, hash == HEAD, status vazio

MAS você rodou o fallback git show HEAD:... > ... mesmo sem o git restore ter falhado → re-corrompeu (PS 5.1 grava > em UTF-16 LE)

git restore de novo → consertou. flutter analyze → No issues found!. Os 68 issues eram 100% cascata.

Descoberta do gap real da S39: o backend PUT /users/me estava pronto e commitado, o user_me.dart estava editado, mas o mobile não tinha EditProfilePage, api.updateMe, rota /edit-profile, nem botão no ProfilePage. A S39 mobile estava 0%.

Blocos pedidos:

A: git show --stat 9d52470 + diff completo → backend mapeado (rota, schema, service, testes)

B: Get-ChildItem -Recurse -Filter "*.dart" lib | Select-String "EditProfile|updateMe|weightKg|heightCm" → só achou o próprio user_me.dart

C: Select-String api.dart "updateMe|putMe|editMe|/users/me|PUT" → vazio (não existia)

D: git status --short + git diff user_me.dart → só user_me.dart modificado (intencional)

E: api.dart inteiro (via Get-Content -Encoding UTF8) → estrutura completa: baseUrl, _client, _send, get/post/delete, _decode, _extractMessage, _fetchBlob, _parseContentDisposition, login, listActivities, searchActivities, getStats*, getUser, followUser, unfollowUser, listFollowing, isFollowing, searchUsers, uploadActivity, listComments, createComment, deleteComment, getActivityTrack, downloadActivityExport, downloadActivityExportBulk, listFollowers

F: auth_service.dart → ChangeNotifier, _token, _cachedUserId, bootstrap/login/logout, api getter, sem cache de UserMe

H: main.dart rotas (padrão claro: fora do shell antes do StatefulShellRoute)

G: _ProfileHeader (linhas 971–1043) e _ProfilePageState (linha 69)

H.2: imports do main.dart (padrão import 'pages/...';)

W: 5 widgets (stats_filters.dart, stats_chart.dart, stats_cards.dart, by_type_list.dart, activity_card.dart) — após o tropeço S39b

P: profile_page.dart inteiro (1043 linhas) — após o tropeço S39b

ACHADOS que moldaram o plano:

#1 api.dart não tem put wrapper público (só get/post/delete) e o _send só aceita GET/POST/DELETE no switch.

#2 api.dart não tem updateMe (não consome o endpoint novo).

#3 auth_service.dart não cacheia UserMe — cada tela faz GET /auth/me local. Decisão: EditProfilePage retorna UserMe via Navigator.pop e o ProfilePage faz _load() + _loadStats().

#4 main.dart segue o padrão de rotas fora do shell antes do StatefulShellRoute — /edit-profile entra ali.

#5 _ProfileHeader é StatelessWidget com me + onLogout (sem onEdit).

#6 profile_page.dart real tem 1043 linhas (não ~1080 como o handoff S38 sugeria — REGRA S38a: piso/faixa, não exato).

#7 Os 5 widgets têm APIs específicas: StatsFilters.onChanged(period, compare) (1 callback), StatsChart.period: ChartPeriod (enum), StatsChart.metric: ChartMetric (enum), StatsCards.data:, isLoading:, isError:, ByTypeList.data:, isLoading:, isError:, ActivityCard.activity:, auth:, onTap:, onChanged:, authorUsernameOverride (não showAuthor). Tudo isso mapeado por causa do tropeço S39b.

#8 go_router 18.x: GoRouterState não tem .context (S39a).

3.3 Fase 2 — contrato travado
Decisão de escopo: S39a (só backend + mobile; web fica pra S40) — conforme handoff S38 §8.

Decisão de API:

api.dart ganha put() wrapper público + updateMe() + case 'PUT': no _send (mínima mudança, alinhada com o padrão existente). Adiciona import '../models/user_me.dart';.

updateMe({fullName?, weightKg?, heightCm?, fieldsToClear, token}) monta o body só com os campos não-nulos + fieldsToClear (map {key: bool}). Backend exclude_unset cuida da semântica ausente/null.

auth_service.dart intocado (decisão: EditProfilePage retorna UserMe via Navigator.pop).

EditProfilePage — StatefulWidget com AuthService auth + UserMe current. 3 TextFormField + "Limpar" nos numéricos. Validação client-side espelhando backend. _buildBody só envia o que mudou/foi limpo. Navigator.pop(updated).

main.dart — +GoRoute(path: '/edit-profile', builder: (context, state) { ... extra as UserMe ... }) antes do StatefulShellRoute. Fallback de deep-link sem extra → context.go('/profile') via WidgetsBinding.addPostFrameCallback.

profile_page.dart — +_openEditProfile() (via context.push<UserMe>), +onEdit no _ProfileHeader, +Wrap com "Editar perfil" + "Sair".

Ordem de entrega: api.dart → edit_profile_page.dart → main.dart → profile_page.dart.

3.4 Fase 3 — entrega incremental
mobile/lib/services/api.dart (810 linhas, +59 de [Sessão 39]). flutter analyze verde de primeira.

mobile/lib/pages/edit_profile_page.dart (NOVO, 384 linhas). flutter analyze verde.

mobile/lib/main.dart (192 linhas). 1 tropeço: state.context não existe no go_router 18.x → [V3.6] acusou 2 erros (linhas 111:27 e 111:50). Fix S39a: builder: (context, state) + context.go('/profile') + context.mounted. Reentreguei (200 linhas). flutter analyze verde.

mobile/lib/pages/profile_page.dart — TROPEÇO S39b: entreguei baseado em memória do handoff S38, assumi APIs erradas (StatsMetric, StatsFilters(onPeriodChanged:, onCompareChanged:), ByTypeList(data:), StatsChart(period: String, ...), ActivityCard(showAuthor:), context.push sem import go_router). 23 erros no [V4.6]. Recuperação: git restore (volta a 1043 linhas) + pedir 5 widgets (Bloco W) + profile_page.dart real (Bloco P) → reentreguei alinhado (1093 linhas). flutter analyze verde.

3.5 Fase 3.5 — verificar save + commit
api.dart: [V1.1] M, [V1.2] 810, [V1.3] 77b6c9c9... ≠ [V1.4] f98799cd..., [V1.5] 3 matches (put 78, updateMe 298, case 'PUT': 771), [V1.6] No issues found!. ✅

edit_profile_page.dart: [V2.1] ??, [V2.2] 384, [V2.3] e74adda2..., [V2.4] fatal: ... exists on disk, but not in 'HEAD' (esperado), [V2.5] 26 matches, [V2.6] No issues found!. ✅

main.dart: 1ª tentativa [V3.6] 2 erros (S39a). 2ª tentativa [V3.1] M, [V3.2] 200, [V3.3] ed61fe5d..., [V3.4] ebe13d60... ≠, [V3.5] 5 matches, [V3.6] No issues found!. ✅

profile_page.dart: 1ª tentativa [V4.6] 23 erros (S39b). git restore → 1043 linhas. 2ª tentativa [V4.1] M, [V4.2] 1093, [V4.3] 793c4251... ≠ [V4.4] 7f7cb40c..., [V4.5] 15 matches, [V4.6] No issues found!. ✅

pytest ([P.5]): 180 passed in 48.88s (173 + 7 da S39). [P.6] ruff: All checks passed!. ✅

git status ([C.1]): 5 arquivos (4 M + 1 ??). ✅

git diff --cached --stat ([C.5]): 5 files changed, 582 insertions(+), 46 deletions(-) + 1 create. ✅

Commit e251057: feat(mobile): EditProfilePage consumindo PUT /users/me (Sessao 39) — 5 files, +582/−46. ✅

Push ([PU.2]): e0e71f7..e251057 main -> main. ✅

[PU.3]: HEAD == origin/main == e251057de3d280f255ac70b635a4443af1faa3fe. ✅

[PU.4]: working tree limpo. ✅

3.6 Fase 4 — validação em produção
HTTP (após Render redeployar):

[BE.1] (primeira tentativa): AUSENTE — Render não redeployou ainda. Esperado (S26c: >3 min, na S39 demorou >5 min).

[BE.3] (primeira tentativa): 405 Método Não Permitido. Esperado (rota não existe no ar).

Após aguardar: [BE.1-retry] = OK - PUT /users/me no ar; [BE.3-retry] = OK weight_kg=80 height_cm=180; [BE.4-retry] = OK weight_kg=80 height_cm=null. ✅

Manual no Chrome (5/5):

Perfil → "Editar perfil" visível: ✅

Editor abre com prefill: ✅

Preenche e salva: ✅

"Limpar" no peso → salva: ✅

Cancelar: ✅

Resultado: prod@rumo.com no backend agora tem weight_kg=80.0 e height_cm=null (estado pós-validação da S39). O full_name continua "Prod User" (não mudou).

3.7 Tropeços da S39 (todos registrados como regras)
S39a (NOVA): GoRouterState no go_router 18.x não tem .context. Usar o 1º parâmetro do builder.

S39b (NOVA, CRÍTICA): profile_page.dart entregue baseado em memória, 23 erros. REGRA S21 vale pro arquivo que está sendo editado. Recuperação: git restore + pedir arquivo + 5 widgets.

S39c (NOVA): placeholder literal no here-string (reincidência S36g). git show HEAD:... > ... corrompe (PS 5.1 grava UTF-16 LE). Só git restore preserva o encoding do blob.

3.8 Resultado da suíte (S39)
pytest -q → 180 passed (+7 vs. S38).

ruff check . → All checks passed!.

npm run build / npm run lint → não rodados na S39 (web intocado desde S30).

flutter analyze → No issues found! (mobile com 1 novo + 4 editados).

Validação manual no Chrome → 5/5.

Validação HTTP em produção → PUT /users/me no ar + semântica de null validada.

3.9 Commits pushados (S39)
text
e251057 feat(mobile): EditProfilePage consumindo PUT /users/me (Sessao 39) — 5 files, +582/−46
9d52470 feat(backend): PUT /users/me para editar weight_kg e height_cm (Sessao 39) — 4 files, +206/−3
Push feito (e0e71f7..e251057). HEAD == origin/main == e251057. Working tree limpo.
Pendente: docs: handoff da Sessao 39 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES
(Contratos S1–S38 inalterados, exceto os marcados. Repetidos por completude.)

Autenticação:

POST /auth/login — application/x-www-form-urlencoded (username=email, password). 200: {access_token, token_type}. 401/422.

GET /auth/me — Bearer JWT. 200: UserResponse completo (id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at). É o "quem sou eu". /users/me não existe pra GET (405).

Perfil próprio:

PUT /users/me (S39) — Bearer JWT, body {weight_kg?: float(0,500), height_cm?: float(0,300), full_name?: str(≤120)}. Semântica exclude_unset: ausente → não toca; null → limpa; valor → atualiza. extra="forbid" (email/username/senha → 422). 200: UserResponse pós-update. 401/422. Rota declarada ANTES de /{user_id} (mesma lição do /search — evita 422).

Atividades:

GET /activities?user_id=&limit=1..100&offset=0 — Bearer JWT. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro (sem user embutido).

GET /activities/{id} — Bearer JWT, dono OU seguidor do dono. 200: ActivityResponse.

GET /activities/{id}/track — Bearer JWT, dono OU seguidor. 200: TrackResponse ({activity_id, type: "LineString", coordinates: [[lon,lat],...], bbox, n_points, simplified}). 404 se route IS NULL ("Atividade não possui rota").

GET /activities/search?q=<min 2>&limit&offset — Bearer JWT. Busca em title/description ILIKE. Visibilidade: dono OU seguido. Retorna list[FeedItemResponse] (com author + user). Rate limit 20/min.

POST /activities/upload — Bearer JWT, multipart/form-data (file, title?, activity_type?, description?). 201: ActivityResponse. 422/429/401. Rate limit 10/h.

GET /activities/{id}/export?format=csv|gpx — Bearer JWT, dono OU seguidor. csv funciona com/sem rota; gpx exige rota. Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>".

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — Bearer JWT, self-only. ZIP. 0 atividades → ZIP vazio (200). from > to → 422.

Feed:

GET /feed?limit&offset — Bearer JWT. FeedItemResponse (herda ActivityResponse + author E user — mesmo Activity.user do ORM; author = web, user = mobile desde S36).

Comentários:

GET /activities/{id}/comments — Bearer JWT. list[CommentResponse] cronológico.

POST /activities/{id}/comments — Bearer JWT, body {content}. 201: CommentResponse. 422/401.

DELETE /comments/{id} — Bearer JWT, só o autor.

Stats:

GET /activities/stats/summary?activity_type — StatsSummary.

GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse ({weeks: int, items: [StatsPeriod]}). Items crescentes em period_start.

GET /activities/stats/monthly?months=N — StatsMonthlyResponse ({months: int, items: [StatsPeriod]}).

GET /activities/stats/by-type?period=all|90d|1y&compare=prev|yoy — StatsByTypeResponse. Cada item tem 5 métricas + previous (nullable). Não inclui avg_pace (derivado no front).

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. Visibilidade: self → 200; viewer segue target → 200; não segue → 403; target não existe → 404.

StatsPeriod (item): {period_start: "YYYY-MM-DD", total_activities, total_distance_m, total_duration_s, total_calories}.

Follows:

POST /users/{user_id}/follow — 204. 400 (self) / 404.

DELETE /users/{user_id}/follow — 204. Idempotente.

GET /users/{user_id}/followers?limit&offset — list[UserPublic].

GET /users/{user_id}/following?limit&offset — list[UserPublic].

GET /users/search?q=<min 2>&limit — list[UserPublic]. Rate limit 20/min.

⚡ NÃO existe GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following e checa se o alvo está na lista.

⚡ UserPublic (/users/{id}, /users/{id}/followers, /users/{id}/following, /users/search): 4 campos apenas (id, username, full_name, is_active). Sem email, sem avatar_url. Para self, usar /auth/me.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Sessões 9–39 commitadas e pushadas. HEAD == origin/main == e251057. Working tree limpo.
Pendente: este handoff.

Primeira ação da Sessão 40 (REGRA S27a — handoff primeiro):

powershell
cd D:\Rumo
git status --short
Se aparecer M docs/HANDOFF.md, commitar:

powershell
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 39"
git push
git --no-pager log --oneline -4
git status --short
Esperado: HEAD == origin/main com docs: handoff da Sessao 39 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
powershell
# [Sessão 40 — primeira ação] Abrir PowerShell via Win+R → powershell
cd D:\Rumo
git status --short
# Se M docs/HANDOFF.md:
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 39"
git push
git --no-pager log --oneline -8
git status --short
[Sessão 40 — primeira ação] Sanidade de build:

powershell
cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
[Sessão 40 — primeira ação] Docker + pytest local:

powershell
docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
# Se o prompt já mostra (venv), PULE a linha abaixo:
.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .
Esperado: 180 passed, ruff limpo, container Up (healthy).

[Sessão 40 — detecção de versão em produção (front — Vercel)]:

powershell
$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$chunks = [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }
Esperado (S39): web inalterado desde S30 — mesmo bundle da S36/S38.

Login (produção):

powershell
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$meId = $me.id
[Sessão 40 — validação do PUT /users/me em produção]:

powershell
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
Write-Host "=== openapi ==="
$openapi = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json"
if ($openapi.paths.'/users/me'.put) { Write-Host "OK PUT /users/me" } else { Write-Host "AUSENTE" }
Write-Host "=== estado atual ==="
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
Write-Host "weight_kg=$($me.weight_kg) height_cm=$($me.height_cm) full_name=$($me.full_name)"
Esperado: OK PUT /users/me + weight_kg=80 height_cm= full_name=Prod User.

Recuperação de arquivo corrompido (lição S21 + S39c):

powershell
cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>
# Se o último commit for anterior à mudança quebrada:
git restore <arquivo>   # ← SEMPRE preferir. Preserva encoding do blob.
# Fallback SÓ se git restore não rolar (grava com BOM, hash difere):
git show HEAD:<arquivo> | Set-Content -Encoding UTF8 <arquivo>
⚡ NUNCA usar git show HEAD:... > ... no PS 5.1 — grava UTF-16 LE e corrompe (S39c).

Diagnóstico: rota nova não responde após git push (S22 + S26c):

powershell
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "users/me|stats/weekly|stats/monthly"
Se vazio: Render não redeployou. Aguardar (>3 min; S39: >5 min) ou Manual Deploy.

Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S36 + S37 + S38 + S39):

powershell
Write-Host "=== [1] termos proibidos (deve vir vazio) ==="
Select-String -Path <arquivo> -Pattern "\bTODO\b|\bFIXME\b" -CaseSensitive
Write-Host "=== [2] total de linhas ==="
(Get-Content -Encoding UTF8 <arquivo>).Count
Write-Host "=== [3] ultima linha ==="
Get-Content -Encoding UTF8 <arquivo> | Select-Object -Last 1
Write-Host "=== [4] git status (deve mostrar ' M <arquivo>') ==="
git status --short
Write-Host "=== [5] hash do disco ==="
git hash-object <arquivo>
Write-Host "=== [6] hash do HEAD (path relativo a RAIZ do repo!) ==="
git rev-parse HEAD:<path/relativo/a/raiz/do/repo>
Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou. Se [5] ≠ [6] e [4] mostra M → save pegou, pode commitar.

⚡ REGRA S34a: o git rev-parse exige path relativo à raiz do repo (mobile/lib/main.dart), não ao CWD (lib/main.dart). O git hash-object aceita CWD.
⚡ REGRA S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS". Usar -CaseSensitive ou regex \bTODO\b|\bFIXME\b.
⚡ REGRA S32a/S32b/S33a/S36d/S38b: -SimpleMatch 'class X' casa class Xxx (prefixo). -SimpleMatch '_X' casa menções em //. -SimpleMatch 'a|b' NÃO é alternância. Para contagem exata/alternância, usar -Pattern (sem -SimpleMatch).
⚡ REGRA S33b/S34b/S38a: "esperado" de qualquer Select-String é piso/faixa, nunca exato sem contagem real.

Contornar editor que não salva (S31c + S36f):

powershell
cd D:\Rumo\mobile
$content = @'
// [Sessão N] conteúdo completo do arquivo aqui (SEM PLACEHOLDER — S36g/S39c)
'@
[System.IO.File]::WriteAllText("D:\Rumo\mobile\lib\pages\arquivo.dart", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "total de linhas: $((Get-Content -Encoding UTF8 'D:\Rumo\mobile\lib\pages\arquivo.dart').Count)"
O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.

Comando git add/commit sem ^ (S38c):

powershell
# ERRADO (o ^ de continuação do PowerShell não funciona consistentemente):
# git add arquivo1 ^
#         arquivo2 ^
#         arquivo3
# CERTO (uma linha só):
git add arquivo1 arquivo2 arquivo3
# CERTO também (backtick):
git add arquivo1 `
        arquivo2 `
        arquivo3
go_router 18.x — API (S39a):

dart
GoRoute(
  path: '/edit-profile',
  builder: (context, state) {  // ← 1º parâmetro é o context (GoRouterState NÃO tem .context)
    final extra = state.extra;
    if (extra is! UserMe) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (context.mounted) context.go('/profile');
      });
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return EditProfilePage(auth: _auth, current: extra);
  },
),
Assinaturas dos widgets de stats (S38/S39 — mapeadas na S39b):

dart
// stats_filters.dart
StatsFilters({
  required String period,      // kStatsPeriodAll / kStatsPeriod90d / kStatsPeriod1y
  required String compare,     // kStatsComparePrev / kStatsCompareYoy
  required bool disabled,
  required void Function(String period, String compare) onChanged,  // 1 callback, não 2
})

// stats_chart.dart
enum ChartPeriod { weekly, monthly }
enum ChartMetric { distance, activities }
StatsChart({
  required ChartPeriod period,
  required ChartMetric metric,
  required List<StatsPeriod>? items,
  required bool isLoading,
  required bool isError,
})

// stats_cards.dart
StatsCards({required StatsSummary? data, required bool isLoading, required bool isError})

// by_type_list.dart
ByTypeList({required StatsByTypeResponse? data, required bool isLoading, required bool isError})

// activity_card.dart
ActivityCard({
  required Activity activity,
  required AuthService auth,
  required VoidCallback onTap,
  required ValueChanged<Activity> onChanged,
  String? authorUsernameOverride,
  VoidCallback? onAuthorTap,
  // ⚠ NÃO existe `showAuthor`
})
fl_chart 1.3.1 — API (S38):

dart
LineChart(LineChartData(
  lineTouchData: LineTouchData(
    touchTooltipData: LineTouchTooltipData(
      getTooltipColor: (_) => Colors.white,  // NÃO tooltipBgColor (removido)
      getTooltipItems: (spots) => spots.map((s) => LineTooltipItem(...)).toList(),
    ),
  ),
  lineBarsData: [
    LineChartBarData(
      dotData: FlDotData(
        show: true,
        getDotPainter: (spot, percent, bar, index) => FlDotCirclePainter(
          radius: 3, color: Color(0xFFF97316), strokeWidth: 0,
        ),
      ),
    ),
  ],
))
share_plus 13.x — API (S37c):

dart
await SharePlus.instance.share(
  ShareParams(
    files: [XFile.fromData(bytes, mimeType: contentType, name: filename)],
    text: shareText,
    subject: filename,
  ),
);
Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (S26a):

powershell
# ERRADO — Content é string, não byte[]:
# [System.IO.File]::WriteAllBytes($path, $resp.Content)
# CERTO (texto UTF-8):
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($resp.Content))
# CERTO (bytes crus — ZIP, imagem):
$fs = [System.IO.File]::OpenWrite($path)
$resp.RawContentStream.Position = 0
$resp.RawContentStream.CopyTo($fs)
$fs.Close()
# MELHOR para inspecionar GPX — sem arquivo, regex no Content:
$times = [regex]::Matches($resp.Content, '<time>([^<]+)</time>')
Upload de arquivo via PowerShell (S33):

powershell
# Invoke-RestMethod -Form NÃO existe no PS 5.1 (só PS 6+). Para multipart/form-data, usar curl.exe:
curl.exe -X POST "https://rumo-api-5s0b.onrender.com/activities/upload" -H "Authorization: Bearer $($login.access_token)" -F "file=@D:\caminho\arquivo.gpx" -F "title=Titulo opcional"
Validar edição de perfil no Chrome (S39):

powershell
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d chrome
Login como prod@rumo.com. Bottom nav → Perfil → "Editar perfil" no rodapé do _ProfileHeader → editor com prefill → Salvar → Perfil reflete.

⚡ REGRA S34c/S36c/S39: se a tela mostrar errado, confirmar (a) usuário logado, (b) URL, (c) flutter run reiniciado depois do último commit.

Validar PUT /users/me via curl (PS 5.1):

powershell
$body = @{ weight_kg = 80.0; height_cm = 180.0 } | ConvertTo-Json
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/me" -Method Put -Headers $h -ContentType "application/json" -Body $body
SEÇÃO 7 — DÍVIDAS TÉCNICAS
Fechadas
(S20) Duas pastas de venv — única é backend\venv.

(S20) Pylance reclamando de imports — .vscode/settings.json aponta para backend/venv.

(S25) RouteMap.tsx reutilizável — agora lazy no ActivityDetailPage.

(S26) to_gpx não emite <time> por <trkpt> — agora emite quando raw_track_points alinhado.

(S28) PreviousDelta mostrava só 3 das 5 métricas — agora renderiza as 5.

(S29) downloadActivityExportBulk retornava void — agora devolve { entryCount }.

(S30) Delta de Pace fora de escopo — DeltaLine ganhou lowerIsBetter.

(S31) Mobile não tinha upload GPX/FIT — POST /activities/upload consumido.

(S32) Mobile não tinha perfil nem "minhas atividades" — GET /activities?user_id= + ProfilePage + bottom nav.

(S32) setState() called after dispose no feed_page.dart — 4 if (!mounted) return;.

(S32) _ActivityCard e _Metric duplicados — extraídos para widgets/activity_card.dart.

(S32) GET /activities não embute user — resolvido via authorUsernameOverride.

(S33) Mobile sem stats agregadas — StatsCards + ByTypeList + delta com lowerIsBetter.

(S33) format.dart em lib/lib/ — movido para lib/utils/.

(S34) Mobile sem perfil de terceiro nem follow — UserProfilePage + rota /user/:id.

(S34) UserPublic local de activity.dart com avatarUrl que o backend não devolve — User novo nasceu sem avatarUrl.

(S35) Mobile sem busca de usuários — searchUsers + UserSearchPage (depois SearchPage).

(S35) onAuthorTap no card do feed implementado mas ninguém passava — FeedPage passa condicional.

(S36) S35a: /feed não embutia user — adicionado user ao lado de author. Mobile funcionou sem mudança. Web intacto.

(S36) Mobile sem busca de atividades — searchActivities + SearchPage (2 abas) + rota /search.

(S37) Mobile sem export (unitário + lote) — downloadActivityExport + downloadActivityExportBulk + saveAndShare + menu no ActivityDetailPage + card "Exportar tudo" no ProfilePage.

(S37) Mobile sem lista de seguidores/seguindo — listFollowers + abas no UserProfilePage.

(S38) Mobile sem filtros de period/compare na UI — StatsFilters + estado nos 2 perfis.

(S38) Mobile sem weekly/monthly charts — StatsChart + getStatsWeekly/getStatsMonthly + 3 models.

(S39) Mobile sem editor de perfil — EditProfilePage + api.updateMe + rota /edit-profile + botão no ProfilePage. Backend PUT /users/me implementado + testado (7 testes).

Conhecidas (não-bug)
(S14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.

(S17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.

(S18) WHERE mata a janela anterior antes do CASE WHEN.

(S17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.

(S17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. (Atualização S33: com a sintética de 2026-06-01, o previous de walk em 90d agora vem preenchido.)

(S20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática.

(S21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk". Testes usam activity.activity_type.value dinâmico.

(S21) apiFetchBlob não tem skipAuth. YAGNI por enquanto.

(S22) export_activities_bulk faz O(N) queries. Aceitável para export raro.

(S22) Export em lote é self-only. Decisão de privacidade.

(S23) downloadActivityExportBulk valida from > to client-side. Dupla validação proposital.

(S24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).

(S25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado desde antes.

(S26) <time> no GPX inclui microssegundos porque o gpxpy serializa datetime.isoformat(). Observação S31: em prod agora vem truncado em segundos. Contrato intacto.

(S26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Coberto por teste.

(S28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. Renomeação de referência cruzada no __vite__mapDeps (REGRA S28b).

(S29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Sentinel 0xFFFF sinaliza falha (retorna -1, fail-open).

(S29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs).

(S29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.

(S30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX.

(S30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0, resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero.

(S31) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → ApiException; o app NÃO faz logout automático.

(S31) Mobile: uploadActivity valida path == null → readAsBytes(), cobre web. No Android, path costuma vir preenchido — não testado em dispositivo físico.

(S31) Mobile: rate limit 10/h do /activities/upload não foi testado explicitamente (429).

(S31) Mobile: activity_type fora da UI do upload na S31 — o backend infere pelo arquivo.

(S31) O commit a83ed82 foi feito pelo usuário/VS Code com a versão inicial; 71a00d4 refinou upload_page.dart e api.dart. Não vale rebase/squash.

(S31) file_picker 13.3.3 trouxe 11 deps novas.

(S32) GET /activities (backend) retorna ActivityResponse[] SEM o campo user embutido. O GET /feed embute (FeedItemResponse com author + user desde S36). Resolvido no mobile via authorUsernameOverride.

(S32) UserPublic local em activity.dart tem avatarUrl que o UserPublic do backend NÃO tem. Dívida cosmética.

(S32) ProfilePage usa Future.wait([/auth/me, /activities?user_id=...]) em paralelo. Na S33, os stats foram SEPARADOS. UserProfilePage (S34) segue o mesmo padrão.

(S32) ProfilePage paginação: "Carregar mais" (botão), não scroll infinito. Regra "se voltou < limit, acabou". Conta prod tem 8 atividades — o "Carregar mais" NÃO foi exercitado.

(S32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id, /user/:id, /search e /edit-profile (S39) ficam FORA do shell (sem bottom nav). Decisão intencional.

(S32) O FAB de upload some quando o usuário está na aba Perfil. Intencional.

(S33) period/compare FIXOS no mobile (90d/prev) — FECHADO na S38 (agora têm UI).

(S33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web).

(S33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 em vez de text-green-600/red-600.

(S33) O _formatThousands é inline (sem intl).

(S33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético. Fica como dado de teste.

(S33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Usar curl.exe.

(S34) O backend NÃO tem GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following?limit=100.

(S34) O _activitiesForbidden do UserProfilePage é heurístico: se listActivities voltou vazio E isFollowing==false E não é self → assume 403.

(S34) O toggle follow/unfollow altera o backend real (não é mock). Testado nos dois sentidos e restaurado. Estado ao fim da S39: prod ↔ Prod2 bidirecional (o handoff da S37 dizia "Prod2 seguindo: 0", desatualizado).

(S34) A inferência isFollowing com limit=100 só enxerga os primeiros 100 follows.

(S35) O debounce da busca é manual (Timer de 300ms) em cada aba do SearchPage, não um Hook/utilitário reusável. Se aparecer terceira tela de busca, extrair pra utils/.

(S35) O _query do SearchPage não vai pra URL. O web usa searchParams.set('q', ...) pra deep-link; no mobile é fluxo efêmero (YAGNI).

(S35) O guard de 2 chars está DUPLICADO: client-side (ApiClient.searchUsers/searchActivities: if (len < 2) return []) e server-side (422). Dupla validação proposital.

(S35) Os 4 avisos [flutter_map] no console do Chrome são informativos (tile server público do OSM). Formalizar tile server próprio para produção.

(S36) O // ignore_for_file: unnecessary_overrides na linha 1 do search_page.dart suprime o lint no arquivo INTEIRO. Trade-off aceitável (arquivo pequeno, overrides justificados pelo mixin).

(S36) A aba Usuários do SearchPage recebe autoFocus na 1ª carga; a aba Atividades não. Decisão: evita dois teclados brigando quando o usuário troca de aba.

(S36) SearchPage usa DefaultTabController + TabBarView. Cada aba tem seu próprio estado (query, resultados, scroll) via AutomaticKeepAliveClientMixin. Trocar de aba NÃO perde estado.

(S36) O main.dart mudou só 2 linhas na S36 (import + classe na rota /search). Nada da bottom nav ou do shell foi tocado.

(S37) O _SocialListsSection no user_profile_page.dart carrega SEMPRE as duas listas (followers + following) no initState, mesmo que o usuário nunca abra as abas. É 2 requests extras por perfil aberto. No web, o ProfilePage.tsx faz o mesmo. Intencional.

(S37) O _toggleFollow do UserProfilePage NÃO recarrega as listas após follow/unfollow. Paridade com web.

(S37) O _exportInfo (feedback verde/âmbar) some em ~4s via Timer. O dispose cancela o Timer; pull-to-refresh cancela o antigo e agenda um novo. Sem vazamento.

(S37) Passo 3 da validação da S37 (GPX sem rota → erro) NÃO foi exercitado por falta de atividade sem rota na conta. A lógica é idêntica à do _fetchBlob para qualquer ApiException, e o backend já está coberto por test_export.py (S21).

(S37) share_plus 13.x removeu Share.shareXFiles — a API nova é SharePlus.instance.share(ShareParams(...)).

(S37) path_provider ^2.1.5 + share_plus ^13.3.1 conflitam com flutter_secure_storage ^11.2.0 em versões antigas. A compatível é share_plus ^13.3.1.

(S37) flutter pub get com plugin nativo modifica pubspec.lock + 2 arquivos windows/flutter/generated_*. Os 3 entram no commit. S38 e S39 NÃO tocaram nesses — fl_chart é Dart puro (não é plugin nativo).

(S38) _loadStats do ProfilePage faz 4 requests em paralelo, cada um com catchError individual. Se um falhar, os dados dos que voltaram continuam visíveis e o erro agregado lista os que falharam. Não é bug; é UX.

(S38) _loadStats do UserProfilePage faz short-circuit em 403 (classe _Stats403 interna). Fase 1 (summary + byType); se 403, marca _statsForbidden e não tenta weekly/monthly. Economiza 2 requests em perfil de terceiro não seguido.

(S38) StatsFilters usa String (não enum) para period/compare — consistência com getStatsByType. Constantes kStatsPeriod*/kStatsCompare* evitam string solta.

(S38) period == 'all' desabilita só o compare (o period continua ativo). O valor de compare persiste no estado quando volta pra 90d/1a (paridade com o web: o <select> de compare não é resetado).

(S38) StatsChart reexporta StatsPeriod (export '../models/stats.dart' show StatsPeriod;). S37e: StatsPeriod é usado de fato, então o export é legítimo.

(S38) StatsChart não reordena items — confia na ordem do backend (crescente em period_start).

(S38) StatsChart mostra só alguns labels no eixo X quando tem >6 pontos (step = labels.length / 6).

(S38) _yInterval do StatsChart: activities = passo 5; distance = adaptativo (0.25/1/5/20/yMax/5).

(S38) fl_chart 1.1.0 resolveu em 1.3.1 (o caret permite <2.0.0). getTooltipColor (não tooltipBgColor, removido), FlDotCirclePainter, LineTouchTooltipData — todos existem na 1.3.1.

(S38) Build web local vs Vercel: index-DvGu4786.js (local) vs index-CJjOEm0V.js (servido). Esperado: web intocado desde S30, nenhum push de web desde então. Não é bug (S29b).

(S38) Follow Prod2: o handoff da S37 registrava Prod2 seguindo: 0; mediu-se 1 na Fase 0 (Prod2 segue produser). Estado pós-validação manual da S37. Não é bug.

(S39) O PUT /users/me da S39 deixou o prod@rumo.com com weight_kg=80.0 e height_cm=null no backend (estado pós-validação HTTP). O full_name continua "Prod User". Fica como dado de teste. A EditProfilePage abre com esses valores pré-preenchidos (peso 80, altura vazia, nome "Prod User"). Não é bug, é estado do backend.

(S39) O extra do go_router no /edit-profile pode vir null em hot reload / deep-link (a 18.x preserva, mas não é garantido). O builder protege (redireciona pra /profile se não for UserMe), mas o hot reload da EditProfilePage perde o estado. Se virar problema, S40 troca por GET /auth/me dentro da própria EditProfilePage.

(S39) birth_date fora do escopo da S39 (backend UserUpdate não aceita). O model UserMe já tem birthDate: String? (cru do backend). S40 pode editar (mudando pra DateTime? e adicionando ao UserUpdate).

(S39) email/username fora do escopo (rotas próprias, chave única). S40+.

(S39) O ActivityCard no profile_page.dart NÃO passa onAuthorTap — no perfil self não faz sentido (o usuário já é o autor). Comportamento herdado da S34, intocado.

(S39) edit_profile_page.dart não tem "Desfazer" global — só por campo ("Limpar" / "Desfazer" no peso e altura). O nome completo não tem "Limpar" (apagar o texto + salvar manda null). Decisão de UX: consistente com a semântica exclude_unset.

Oportunidades
(S18–39) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.

(S19–39) Stats públicas só quando viewer segue o alvo.

(S22–37) Export em lote no mobile — FECHADO S37.

(S30) Testes unitários do DeltaLine no web e no mobile (puro, testável).

(S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.

(S31) Testar upload em Android físico/emulador.

(S31) UI dedicada para 429 (rate limit) com cooldown visual.

(S31) activity_type como dropdown opcional na UploadPage.

(S33) Filtros de period/compare na UI do perfil — FECHADO S38.

(S33) Weekly/monthly charts no perfil — FECHADO S38.

(S33) Filtros de activity_type na UI do perfil — S40+.

(S34) Lista de seguidores/seguindo no UserProfilePage — FECHADO S37.

(S34) Export no mobile (unitário + lote) — FECHADO S37.

(S34) Editar perfil (peso, altura, etc.) — FECHADO S39 no mobile (backend + mobile). Falta a paridade no web (S40).

(S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S40+.

(S34) Endpoint GET /users/{id}/is-following no backend — S40+.

(S36) Deep-link ?q= na busca mobile (se aparecer necessidade).

(S36) Extrair o debounce manual (Timer 300ms) para um helper utils/debounce.dart se aparecer terceira tela de busca.

(S36) Testar busca de atividades com termo vazio/1 char (guard client-side + 422 backend).

(S36) Tile server próprio do OSM (formalizar para produção).

(S37) Incluir botão de export unitário no web/src/pages/ActivityDetailPage.tsx para paridade com o mobile (hoje só o ProfilePage.tsx tem).

(S37) Mostrar o _exportInfo como SnackBar (em vez de texto inline) no mobile, se a UX pedir.

(S37) Testar export em Android/iOS físico (hoje só Chrome/web).

(S37) Criar atividade sintética sem rota para exercitar o passo 3 da validação da S37 (GPX → 404 "Atividade não possui rota").

(S38) Filtros de activity_type na UI do perfil (o backend aceita em todos os 4 endpoints de stats).

(S38) Testar StatsChart em Android/iOS físico (hoje só Chrome/web).

(S38) Extrair o padrão _loadStats de 4 requests em paralelo para um helper se aparecer terceira tela de stats (improvável).

(S39) Paridade web do "Editar perfil" — o ProfilePage.tsx do web não tem a UI. Decisão travada no handoff S38 §8: S39 = OPÇÃO 3a (só backend + mobile); web fica pra S40.

(S39) Editar birth_date — backend UserUpdate não aceita. S40+ (mudar schema + UserMe.birthDate pra DateTime?).

(S39) Editar email/username — rotas próprias (chave única). S40+.

(S39) Trocar extra do /edit-profile por GET /auth/me dentro da EditProfilePage se o hot reload perder estado de forma recorrente.

(S39) Testar EditProfilePage em Android/iOS físico (hoje só Chrome/web). O TextInputType.numberWithOptions(decimal: true) + inputFormatters podem se comportar diferente em teclado nativo.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 40 e além)
Sessão 39 fechada. PUT /users/me (backend + 7 testes) e EditProfilePage (mobile) entregues. Backend com 180 testes, web intocado desde S30, mobile com 1 arquivo novo + 4 editados. Mobile subiu de ~90% para ~93% de cobertura.

Primeira ação obrigatória da Sessão 40 (REGRA S27a)
Abrir PowerShell via Win+R → powershell.

Rodar o bloco "[Sessão 40 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 39, push, confirmar HEAD == origin/main.

Fase 0 completa (REGRA S27b) — a S39 não rodou a Fase 0 completa (pytest só rodou depois do commit mobile). A S40 abre com:

Handoff pendente (git status).

Log/status (git log -8, git status).

Build/lint/analyze (npm run build, npm run lint, flutter analyze).

Docker + pytest + ruff (docker ps -a, pytest -q → 180 passed, ruff check .).

Prod backend (/auth/me, /feed, PUT /users/me no openapi).

Prod frontend (index-*.js da Vercel).

Rota travada para a Sessão 40
S40 = OPÇÃO 3b (paridade web do "Editar perfil") + OPÇÃO 4 (release prep).

Parte A — Paridade web (S40a):

O web/src/pages/ProfilePage.tsx do web não tem UI de edição de perfil. Precisa ganhar:

Botão "Editar perfil" no cabeçalho.

Modal ou página de edição (peso, altura, nome completo).

Consome PUT /users/me via api do web.

Não foi confirmado nesta sessão se o ProfilePage.tsx do web já tem algum esboço. S40 abre pedindo web/src/pages/ProfilePage.tsx, web/src/api/*.ts, web/src/hooks/useProfile.ts (se existir) e web/src/types/*.ts pra mapear o padrão.

Decisão de UX: seguir o padrão do ProfilePage.tsx (componentes existentes) + react-hook-form (se já for usado) ou useState local (como o mobile).

Testes: sem teste E2E no web; validação manual no browser.

Parte B — Release prep (S40b) — bloqueadores não-código:

Ícone do app (mobile + web favicon).

Identidade visual (logo, splash screen).

Política de privacidade (obrigatória pra loja).

Build assinado (Android keystore + iOS provisioning profile — precisa de conta de dev).

Tile server próprio do OSM (formalizar; hoje usa tile público, não recomendado pra produção).

Publicação nas lojas (Google Play + App Store — precisa de contas de dev, ~$25 + $99/ano).

Ordem de entrega da S40 (proposta):

Fase 0 completa (a que faltou na S39).

Fase 1 — descoberta: pedir web/src/pages/ProfilePage.tsx, web/src/api/*.ts, web/src/hooks/useProfile.ts (se existir), web/src/types/*.ts, mobile/lib/models/user_me.dart (o estado real), mobile/lib/pages/edit_profile_page.dart (pra referência).

Fase 2 — contrato: PUT /users/me no web (mesma API, mesmo shape). Componente de edição (modal vs página — decidir pelo padrão do web). Validação client-side espelhando backend.

Fase 3 — entrega incremental (web primeiro, depois release prep).

Fase 3.5 — verificar save + commit.

Fase 4 — validação (build + lint + validação manual no browser + Vercel).

Fase 5 — handoff + percentual.

Alternativas (se a S40 quiser reduzir escopo)
OPÇÃO 4 só (release prep): não tocar no web, focar em ícone + identidade + política de privacidade + build assinado. Não fecha a paridade web, mas avança o lançamento.

OPÇÃO 3b reduzida: só o botão "Editar perfil" no web abrindo um modal simples (peso + altura). Nome completo fica pra S41.

OPÇÃO 5 (features extras): notificações, feed de "quem você segue", comentários aninhados, etc. Fora do MVP.

Recomendação final: S40 = OPÇÃO 3b (paridade web do "Editar perfil") + começo da OPÇÃO 4 (ícone + identidade visual). A paridade web fecha o ciclo da S39 (backend + mobile + web) e a identidade visual é o próximo bloqueador não-código. A S41 fica pra release prep pesado (política de privacidade + build assinado + lojas).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT
O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordadas, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25–S38: reforçou os mesmos acordos. Tolerou tropeços (S21–S38: 1 a 8 tropeços por sessão). A S38 fechou com 4 tropeços (S38a–S38d), todos registrados.

Na S39: tolerou 3 tropeços (S39a–S39c):

S39a: GoRouterState no go_router 18.x não tem .context. 2 erros, fix imediato.

S39b: profile_page.dart entregue baseado em memória do handoff S38. 23 erros. Recuperação: git restore + pedir arquivo + 5 widgets.

S39c: placeholder literal no here-string do api.dart (reincidência S36g). git restore recuperou; git show HEAD:... > ... re-corrompeu (PS 5.1 grava UTF-16 LE).

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Acordo novo na S32: manter o processo da S21–S31. Concretamente:

Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar. REGRA S39b: vale pro arquivo que está sendo editado, não só pros arquivos novos.

Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> (com path relativo à RAIZ do repo — REGRA S34a) + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b + S34b + S38a: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c). git add com todos os paths numa linha só (REGRA S38c).

Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render — na S39 demorou >5 min) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local. REGRA S34c: no mobile, confirmar login/URL/restart antes de declarar bug de tela.

Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S39 (Seção 0, itens 64–66): S39a (GoRouterState 18.x não tem .context), S39b (REGRA S21 vale pro arquivo que está sendo editado — pedir arquivo + widgets dependentes antes de escrever), S39c (só git restore preserva o encoding do blob — git show HEAD:... > ... corrompe).

O que funcionou nas S21–S39 (manter):

Ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão).

Disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33, S34, S35, S36, S37, S38, S39).

Consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor, sessão do localStorage, tela errada, placeholder em here-string, conflito de versão de plugin, import não usado, ^ de continuação, hash git diff --cached --stat, go_router 18.x sem .context, API errada por memória, git show > corrompendo encoding) na hora e corrigir/registrar, sem contornar.

A S39 acrescentou: a REGRA S21 vale pro arquivo que está sendo editado, não só pros novos (S39b — a mais valiosa da sessão); só git restore preserva encoding (S39c); GoRouterState 18.x não tem .context (S39a); a paridade web fica pra próxima sessão (S39 = backend + mobile apenas, decisão travada no handoff S38 §8).

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 39)
Quebrado por camada
Backend — ~95%
Item	%	Status
Auth (login, me)	100%	✅
Perfil próprio (GET /auth/me, PUT /users/me)	100%	✅ (S39)
Atividades (CRUD, list, detail, search, track)	100%	✅
Feed (com author + user)	100%	✅
Comentários	100%	✅
Upload GPX/FIT	100%	✅
Stats (summary, by-type, weekly, monthly)	100%	✅
Follows (follow, unfollow, followers, following, search)	100%	✅
Export (unitário + lote)	100%	✅
Testes (180 passed)	100%	✅
Ruff (0 warnings)	100%	✅
Faltando pro MVP: editar email/username (rotas próprias), editar birth_date (S40+), GET /users/{id}/is-following (opcional), notificações (pós-MVP)	—	⏳
Consolidado backend: ~95%. O que falta é opcional pro MVP.

Web — ~92%
Item	%	Status
Feed	100%	✅
Perfil próprio (com stats + filtros + 4 charts + export em lote)	100%	✅
Perfil de terceiro (com follow + abas Seguidores/Seguindo)	100%	✅
Detalhe de atividade (com mapa, comentários, like)	100%	✅
Upload (se houver — não confirmado nesta sessão)	?	❓
Busca (atividades + usuários)	100%	✅
Editar perfil (peso, altura, nome)	0%	❌ S40
Tile server próprio do OSM	0%	❌ S40
Consolidado web: ~92%. O gap real é a paridade web do "Editar perfil" (S40).

Mobile — ~93%
Item	%	Status
Feed	100%	✅
Perfil próprio (com stats + filtros + 4 charts + export em lote)	100%	✅
Perfil de terceiro (com follow + abas Seguidores/Seguindo)	100%	✅
Detalhe de atividade (com mapa, comentários, like, export unitário)	100%	✅
Upload GPX/FIT	100%	✅
Busca (2 abas: Usuários | Atividades)	100%	✅
Editar perfil (peso, altura, nome)	100%	✅ (S39)
Export (unitário + lote)	100%	✅
Testes em dispositivo físico (Android/iOS)	0%	❌ S40
Paridade visual exata com o web	~90%	🟡
Refresh token / logout automático em 401	0%	❌ S40+
Consolidado mobile: ~93%. O gap real é testes em dispositivo físico + paridade visual exata + refresh token.

Bloqueadores não-código — 0%
Item	%	Status
Ícone do app (mobile + favicon web)	0%	❌ S40
Identidade visual (logo, splash)	0%	❌ S40
Política de privacidade	0%	❌ S41
Build assinado (Android keystore + iOS provisioning)	0%	❌ S41
Conta Google Play Developer ($25)	0%	❌ S41
Conta Apple Developer ($99/ano)	0%	❌ S41
Publicação nas lojas	0%	❌ S42
Tile server próprio do OSM	0%	❌ S40
Screenshots / descrição da loja	0%	❌ S42
Consolidado bloqueadores: 0%. É o maior gap pro lançamento. Nada disso é código, mas é obrigatório pra publicar.

Consolidado
Camada	%	Peso estimado	Contribuição
Backend	~95%	35%	33.3%
Web	~92%	20%	18.4%
Mobile	~93%	30%	27.9%
Bloqueadores não-código	0%	15%	0%
MVP consolidado	~79.6%	100%	~79.6%
Interpretação: o código está em ~93% (backend+web+mobile), mas os bloqueadores não-código (ícone, política, build assinado, lojas) estão em 0% e pesam 15% do MVP. Sem eles, não há lançamento. Por isso o consolidado é ~80%, não ~93%.

Estimativa de sessões restantes
Sessão	Foco	Estimativa
S40	Paridade web do "Editar perfil" + começo da identidade visual (ícone + splash)	1 sessão
S41	Release prep pesado (política de privacidade + build assinado + contas de dev + tile server próprio)	1–2 sessões
S42	Screenshots + descrição da loja + submissão Google Play (review ~1–3 dias)	1 sessão + review
S43	Submissão App Store (review ~1–7 dias) + correções de review	1 sessão + review
S44+	Pós-MVP (notificações, editar email/username, refresh token, paridade visual exata)	contínuo
Estimativa: ~3–4 sessões pra chegar em "pronto pra submeter" (S40–S42), +1–2 sessões de review das lojas (S43+). Total: ~5–6 sessões até o app estar publicado.