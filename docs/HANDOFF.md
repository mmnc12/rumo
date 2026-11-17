HANDOFF — Rumo (backend + frontend + mobile) — Sessão 38
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚡ REGRA S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça. ⚡ Esta regra vale TAMBÉM para comandos PowerShell com here-string @' ... '@: nunca usar "COLE O CONTEÚDO AQUI" como placeholder — o conteúdo tem que ser o arquivo inteiro. (Reforçada na S36 — REGRA S36g.)

⚡ REGRA S21 — não adivinhar nomes de símbolos do projeto. Pedir o model/enum/schema antes de referenciar.

⚡ REGRA S21 — git status antes de qualquer git restore/git checkout. git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>.

⚡ REGRA S22 — Invoke-WebRequest com -UseBasicParsing. Elimina o prompt de segurança do PS 5.1.

⚡ REGRA S22 — validar deploy do Render antes de acusar bug no código. Depois de push, checar openapi.json para a rota nova antes de acusar 422/404.

⚡ REGRA S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele. Nunca procurar "ProfilePage-" direto no HTML.

⚡ REGRA S24 — Vercel às vezes demora >90 s para o primeiro deploy após push. Se o hash antigo aparecer após 90 s, rodar o teste de novo. Não presumir bug.

⚡ REGRA S25a — Select-String -SimpleMatch NÃO aceita | como alternância. Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo.

⚡ REGRA S25b — quando lines[−1] for suspeito, confirmar com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo>" antes de concluir. Não dar "OK" nem "corrompido" sem evidência.

⚡ REGRA S25c — antes de pedir git add/git commit de um arquivo que o usuário acabou de salvar, EXIGIR o output do bloco de validação e ESPERAR.

⚡ REGRA S25d — o teste definitivo de "o save pegou" é git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M <arquivo>. Se git status --short vier vazio depois de salvar, o disco é igual ao commitado. O save não pegou.

⚡ REGRA S25e — ao entregar o conteúdo de um arquivo para colar no editor, entregar SEM cerca markdown envolvendo. Entregar o arquivo inteiro como único texto da resposta, sem instruções antes/depois.

⚡ REGRA S26a — no PowerShell 5.1, Invoke-WebRequest -UseBasicParsing devolve resp.Content como STRING, não como byte[]. [System.IO.File]::WriteAllBytes(path, resp.Content) falha. Para texto UTF-8: [System.Text.Encoding]::UTF8.GetBytes(resp.Content). Para bytes crus (ZIP, imagem): resp.RawContentStream.CopyTo(fileStream). Para inspecionar GPX/XML: regex direto no Content.

⚡ REGRA S26b — validar GPX em produção por regex é mais barato que gpxpy + arquivo temporário. Contar <time> distintos com regex no Content responde "o S26 está no ar?" em 3 linhas.

⚡ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Não é bug.

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

⚡ REGRA S36g — comandos com here-string entregam conteúdo REAL, nunca placeholder.

⚡ REGRA S37a — conflito de versão de plugin no pub get: ler o erro inteiro antes de tentar consertar. O pub sugere a versão compatível no final do output ("Try upgrading your constraint on X: Y"). Usar a sugestão em vez de adivinhar. Caso da S37: share_plus ^12.0.1 + flutter_secure_storage ^11.2.0 brigavam por win32 (6.x vs 5.x). Solução: share_plus ^13.3.1.

⚡ REGRA S37b — ao adicionar plugin nativo ao pubspec.yaml, o pub get modifica pubspec.lock + windows/flutter/generated_plugin_registrant.cc + windows/flutter/generated_plugins.cmake. Esses 3 entram no commit junto (não são "lixo").

⚡ REGRA S37c — share_plus 13.x: API nova é SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])). A antiga Share.shareXFiles foi removida (mesma família de mudança do file_picker 13.x da S31b).

⚡ REGRA S37d — ao testar download no Chrome, o share_plus dispara o download no browser via Share API. O arquivo aparece na barra de downloads do Chrome, não no share sheet do SO (que não existe no Chrome). É o comportamento esperado.

⚡ REGRA S37e — ao adicionar import que parece necessário mas o tipo vem por inferência (Uint8List do result.bytes), o flutter analyze acusa unused_import. Remover o import (não forçar uso). Caso da S37: dart:typed_data no activity_detail_page.dart.

⚡ REGRA S37f — unnecessary_underscores (Dart 3.7+): (_, __) vira (_, _) em callbacks com múltiplos parâmetros ignorados. O flutter analyze acusa info, não warning.

⚡ REGRA S38a (NOVA) — "esperado" de Select-String é SEMPRE piso/faixa, sem exceção — mesmo quando o arquivo entregue foi contado. O contador do entregue (comentários de cabeçalho, quebras) não bate com o número real de linhas no disco. Caso S38: anunciei "≥ 260" para o stats.dart e vieram 224; anunciei "≥ 124" para o stats_filters.dart e vieram 116. O arquivo estava correto nos dois casos.

⚡ REGRA S38b (NOVA) — Select-String -SimpleMatch com | é sempre erro — reforço da S25a/S33a/S36d depois de reincidência na S38. Na validação do profile_page.dart da S38, usei -SimpleMatch com | de novo e o resultado veio vazio (0 matches). A prova de que o arquivo estava correto veio do flutter analyze verde, não do Select-String. Regra prática: -SimpleMatch nunca, exceto quando o padrão é um único termo literal sem |, sem _Prefixo (que casa comentário — S32b), sem class X (que casa prefixo — S32a). Em dúvida, -Pattern.

⚡ REGRA S38c (NOVA) — o ^ de continuação de linha do PowerShell não é confiável (quebra com linhas em branco entre os ^, e o git add recebe ^ como pathspec literal, abortando). Usar backtick (`) ou — melhor — comando numa linha só. Caso S38: o git add com ^ falhou (fatal: pathspec '^' did not match any files), nada foi staged, o git commit falhou, o git push disse "Everything up-to-date". Recuperado com git add numa linha só.

⚡ REGRA S38d (NOVA) — "esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas. Chutei "~+1500/−50" na S38, o real foi +996/−112. O número que importa é o de arquivos (8, e esse bateu).
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (173 passed ao fim da S38). Container de teste rumo_postgres_test na porta 5433.

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
│   │   + test_export_bulk + test_feed + test_follow + test_like + test_stats)
│   │   — 8 arquivos, 173 testes
│   ├── _scratch/ (ignorado pelo git; s33_delta_test.gpx criado na S33)
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│   ├── lib/
│   │   ├── main.dart (StatefulShellRoute + bottom nav desde S32;
│   │   │   +rota /user/:id desde S34;
│   │   │   +rota /search desde S35, atualizada S36 para SearchPage)
│   │   ├── models/ (activity.dart, activity_track.dart, comment.dart,
│   │   │   stats.dart ← EDITADO S38 (+StatsPeriod, StatsWeeklyResponse,
│   │   │   StatsMonthlyResponse), user.dart ← S34, user_me.dart ← S32)
│   │   ├── pages/ (activity_detail_page.dart ← S37,
│   │   │   feed_page.dart, login_page.dart,
│   │   │   profile_page.dart ← EDITADO S38 (filtros + 4 charts),
│   │   │   search_page.dart ← S36, upload_page.dart ← S31,
│   │   │   user_profile_page.dart ← EDITADO S38 (filtros + 4 charts
│   │   │   + short-circuit em 403 via _Stats403))
│   │   ├── services/ (api.dart ← EDITADO S38 (+getStatsWeekly,
│   │   │   +getStatsMonthly), auth_service.dart)
│   │   ├── utils/ (download.dart ← S37, format.dart ← S33)
│   │   └── widgets/ (activity_card.dart ← S34, activity_map.dart,
│   │       by_type_list.dart ← S33, like_button.dart,
│   │       stats_cards.dart ← S33,
│   │       stats_chart.dart ← NOVO S38 (fl_chart),
│   │       stats_filters.dart ← NOVO S38 (SegmentedButton))
│   ├── pubspec.yaml (file_picker: ^13.3.3, fl_chart: ^1.1.0 ← S38
│   │   (resolveu em 1.3.1), go_router: ^18.1.2,
│   │   path_provider: ^2.1.5 ← S37, share_plus: ^13.3.1 ← S37,
│   │   name: rumo_mobile)
│   ├── pubspec.lock
│   └── windows/flutter/ (generated_plugin_registrant.cc,
│       generated_plugins.cmake — modificados pelo pub get S37.
│       S38 NÃO tocou nesses — fl_chart é Dart puro.)
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

⚡ mobile/lib/pages/user_search_page.dart NÃO EXISTE MAIS (removido na S36). Foi substituído por search_page.dart (2 abas: Usuários | Atividades).
Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades (7 + 1 sintética da S33), 34.08 km. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min) usada pra validar o S26 e o export GPX da S37. Tem atividade sintética "Teste delta S33 (janela anterior)" (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null). Username no backend: produser (confirmado na S36 via /feed).

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2 e Prod2 segue prod (confirmado na S38 — o handoff da S37 registrava "Prod2 seguindo: 0", desatualizado; não é bug, é estado de follow pós-validação manual da S37). Usado pra validar abas Seguidores/Seguindo na S37 e o short-circuit em 403 dos stats na S38.

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).
Acordos de trabalho (válidos em todas as sessões — reforçados na S21 à S38)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

    UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

    HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.

    PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes.

    VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo.

    VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<simbolo>" antes de build/test.

    NUNCA placeholder no código entregue (S21) nem em comandos com here-string (S36g).

    Não adivinhar nomes de símbolos (S21).

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

    Render free tier pode demorar >3 min para redeployar após push (S26c).

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

    git rev-parse HEAD:<arquivo> exige path relativo à RAIZ do repo (S34a).

    "Esperado" anunciado antes de rodar pode errar mesmo sendo faixa (S34b).

    Validar tela mobile no Chrome: confirmar usuário logado, URL colada e restart do flutter run (S34c).

    S35a fechada: /feed agora devolve user + author (S36).

    MatchCollection[-1] não funciona no PS 5.1 — usar $times[$times.Count - 1] (S36a).

    Em bundle minified, Select-String devolve a linha inteira — usar [regex]::Matches (S36b).

    Ao validar toque no ActivityCard, confirmar PRIMEIRO qual tela está aberta pela URL (S36c).

    Select-String -SimpleMatch com | é sempre erro — usar -Pattern (S36d, CRÍTICA).

    AutomaticKeepAliveClientMixin é @mustCallSuper — super.build obrigatório. Solução de lint: // ignore_for_file na linha 1, NÃO // ignore: local (S36e).

    Editor falhou 2× em salvar search_page.dart — WriteAllText é a solução (S36f).

    Comandos com here-string entregam conteúdo REAL, nunca placeholder (S36g).

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

Processo que o usuário elogiou na S21–S38 (para manter)

Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).
SEÇÃO 1 — TL;DR para quem chega agora

Backend: 173 testes passando LOCALMENTE, 0 warnings. Sem mudança na S38. FeedItemResponse expõe autor em author (web) + user (mobile) desde S36. Todos os endpoints do MVP em produção.

Web: intocado desde S30. ActivityDetailPage.tsx não tem botão de export unitário (só o ProfilePage.tsx tem "Exportar tudo") — o mobile ganhou o botão no detalhe como adição de paridade, não espelho. Build/lint limpos. S38 não tocou no web.

Mobile: flutter analyze limpo. S38 adicionou:

    Filtros de period/compare na seção de estatísticas (ProfilePage + UserProfilePage). StatsFilters (novo widget) com 2 SegmentedButton M3: Janela (Todas/90d/1a) e Comparar com (Período anterior/Ano anterior). compare desabilitado quando period == 'all' (regra do backend).

    4 charts weekly/monthly (StatsChart, novo widget, fl_chart): weekly×distance, weekly×activities, monthly×distance, monthly×activities. Paridade visual 1:1 com PeriodChart.tsx do web (cor #f97316, eixo Y adaptativo, tooltip formatado).

    2 métodos novos no ApiClient: getStatsWeekly (?weeks=8) e getStatsMonthly (?months=6).

    3 models novos no stats.dart: StatsPeriod (5 campos), StatsWeeklyResponse {weeks, items}, StatsMonthlyResponse {months, items}.

    1 dependência nova: fl_chart ^1.1.0 (resolveu em 1.3.1, Dart puro, sem código nativo).

    Short-circuit em 403 no UserProfilePage: se by-type volta 403 (viewer não segue o alvo), _loadStats não tenta weekly/monthly. Filtros ficam desabilitados.

Endpoints relevantes para stats (S38 — consumidos pelo mobile)
text

GET /users/{id}/stats/summary                          — auth dono OU seguidor
GET /users/{id}/stats/by-type?period=&compare=         — auth dono OU seguidor
GET /users/{id}/stats/weekly?weeks=N                   — auth dono OU seguidor
GET /users/{id}/stats/monthly?months=N                 — auth dono OU seguidor

O stats/weekly e stats/monthly devolvem { weeks|months: int, items: [StatsPeriod] } com items em ordem crescente de period_start. O StatsChart não reordena (paridade com PeriodChart.tsx do web).

S38 — validação manual no Chrome (7/7):

    Passo 1 (filtros no topo, 90d/prev default): ✅

    Passo 2 (4 charts na ordem, com linha laranja e labels): ✅

    Passo 3 (trocar para 1a recarrega ByTypeList; charts weekly/monthly fixos): ✅

    Passo 4 ("Todas" desabilita "Comparar com" e some com o delta): ✅

    Passo 5 ("Ano anterior" com 90d muda os deltas): ✅

    Passo 6 (perfil de terceiro: follow ativo → stats; unfollow → 403 short-circuit, filtros desabilitados, "Siga pra ver..."; follow de volta → restaura): ✅

    Passo 7 (console limpo): ✅

Commits S38:
text

c9543fb (HEAD -> main, origin/main) feat(mobile): filtros period/compare + charts weekly/monthly (Sessao 38)
d4b8c8b docs: handoff da Sessao 37
15f7602 feat(mobile): export CSV/GPX (unitario + lote) + followers/following (Sessao 37)
b05e870 docs: handoff da Sessao 36
dba8594 refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36)
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36)

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

    Deps mobile (S31/S32/S33/S34/S35/S36/S37/S38): file_picker: ^13.3.3, fl_chart: ^1.1.0 (resolveu em 1.3.1), go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1. Package name: rumo_mobile.

Git (estado ao fim da Sessão 38):
text

c9543fb (HEAD -> main, origin/main) feat(mobile): filtros period/compare + charts weekly/monthly (Sessao 38)
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

Working tree limpo. S38 adicionou 1 commit (c9543fb, 8 files changed, +996/−112).
Pendente: docs/HANDOFF.md da S38 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 38.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 38
3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short mostrou working tree limpo (d4b8c8b já commitado fora do chat). Sem M docs/HANDOFF.md.

    Log/status. HEAD == origin/main == d4b8c8b. Working tree limpo.

    Build/lint/analyze. npm run build: 824 modules, 3.84s, index-DvGu4786.js (hash novo vs index-CJjOEm0V.js servido pela Vercel — mas web intocado desde S30, então é só variação de build local). npm run lint: limpo. flutter analyze: No issues found! (7.7s).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. Container rumo_postgres_test já Up 42 minutes (healthy) na porta 5433. pg_isready → accepting connections de primeira. pytest -q: 173 passed in 50.17s. ruff check .: All checks passed!.

    Prod backend. /auth/me OK (produser, id 01a12c83…). /feed 3 itens com author == user (mesmo id, produser) nos 3. Export unitário GPX: Content-Disposition: attachment; filename="rumo_01a1b36a-…_walk.gpx", application/gpx+xml; charset=utf-8, 60 <time> distintos, último 2026-11-06T21:40:23Z. Export em lote CSV: attachment; filename="rumo_export_20261117-000909.zip", application/zip. Followers do Prod2: 1 (produser). Following do Prod2: 1, esperado era 0 — desvio de expectativa, não bug (ver 3.7).

    Prod frontend. index-CJjOEm0V.js + 7 chunks batendo 1:1 com S36. Web intocado desde S30. Divergência servido != local é esperada: a Vercel está servindo o build da S36 (não houve push de web desde S30), e o build local da S38 gerou hash novo por variação do ambiente de build, não por mudança de código. Não é bug (REGRA S29b).

3.2 Fase 1 — descoberta

Pedidos e recebidos: web/src/components/StatsCards.tsx, web/src/components/PeriodChart.tsx, mobile/lib/models/stats.dart, mobile/lib/widgets/stats_cards.dart, mobile/lib/widgets/by_type_list.dart, mobile/lib/services/api.dart, mobile/pubspec.yaml. Depois: web/src/hooks/useStats.ts, mobile/lib/pages/profile_page.dart, mobile/lib/pages/user_profile_page.dart, e a saída real de GET /users/{id}/stats/weekly?weeks=8 + GET /users/{id}/stats/monthly?months=6.

ACHADOS que moldaram o plano:

    #1 StatsCards e ByTypeList no web são "burros" (sem filtro). O filtro de period/compare fica no caller. Paridade estrutural preservada.

    #2 StatsSummary mobile já tem totalCalories e StatsCards mobile já o exibe. Nada a mudar.

    #3 PeriodChart.tsx no web é UM componente parametrizado por (period × metric). As 4 combinações saem do mesmo componente. Segui a mesma assinatura no mobile (StatsChart).

    #4 stats.dart mobile NÃO tinha model de weekly/monthly. Precisou de StatsPeriod + 2 envelopes.

    #5 api.dart mobile NÃO tinha getStatsWeekly/getStatsMonthly. Precisou de 2 métodos novos.

    #6 profile_page.dart e user_profile_page.dart passavam period: '90d', compare: 'prev' fixos. Ambos ganharam estado.

    #7 fl_chart não estava no pubspec.yaml. Adicionado ^1.1.0 (resolveu em 1.3.1, Dart puro, MIT).

    #8 Shape real do backend confirmado por HTTP: {weeks|months: int, items: [{period_start, total_activities, total_distance_m, total_duration_s, total_calories}]}. StatsPeriod tem 5 campos (não 3 como o PeriodChart usa). Model mobile expõe os 5; StatsChart usa 3.

3.3 Fase 2 — contrato travado

Decisão de dependência: fl_chart ^1.1.0 (Dart puro, MIT, sem código nativo — roda no Windows sem Developer Mode). Alternativa syncfusion_flutter_charts descartada (licença comercial para algumas features).

Escopo: 7 arquivos (2 novos, 5 editados). Backend zero. Web zero.

Decisões travadas:

    period/compare como String (não enum) — consistência com getStatsByType.

    SegmentedButton M3 para os 2 filtros.

    compare desabilitado quando period == 'all' (regra do backend).

    Ordem: _StatsFilters → StatsCards → ByTypeList → 4 StatsChart.

    Default: period='90d', compare='prev' (não regride do que já existia).

    weeks=8, months=6 (defaults do useStats.ts do web, confirmados).

    _loadStats faz 4 requests em paralelo (summary, byType, weekly, monthly) com catchError individual. UserProfilePage curto-circuita em 403.

    activity_type fora do escopo da S38 (fica pra S39+).

Ordem de entrega: pubspec.yaml → stats.dart → api.dart → stats_filters.dart → stats_chart.dart → profile_page.dart → user_profile_page.dart.
3.4 Fase 3 — entrega incremental

    pubspec.yaml (+fl_chart: ^1.1.0). pub get resolveu fl_chart 1.3.1 + equatable 3.0.0 (dep transitiva). Changed 2 dependencies!. flutter analyze: No issues found! (4.8s). git status --short: só M pubspec.yaml + M pubspec.lock. Nenhum generated_* tocado — confirmado: fl_chart é Dart puro (S37b não se aplica).

    mobile/lib/models/stats.dart (224 linhas, +90 de [Sessão 38]). StatsPeriod (5 campos), StatsWeeklyResponse {weeks, items}, StatsMonthlyResponse {months, items}. Models da S33 intocados. flutter analyze verde.

    mobile/lib/services/api.dart (751 linhas, +49 de [Sessão 38]). getStatsWeekly(userId, weeks: 8), getStatsMonthly(userId, months: 6). Import de stats.dart atualizado. flutter analyze verde.

    mobile/lib/widgets/stats_filters.dart (novo, 116 linhas). StatsFilters com 2 SegmentedButton. period == 'all' desabilita só compare. disabled geral desabilita os 2. Constantes kStatsPeriod*/kStatsCompare*. flutter analyze verde.

    mobile/lib/widgets/stats_chart.dart (novo, 304 linhas). StatsChart({period, metric, items, isLoading, isError}) com fl_chart. Eixo Y adaptativo (km ou contagem com yMax >= 5 múltiplo de 5). Tooltip, grid, cor #f97316, altura 256px. fl_chart 1.3.1 API OK (getTooltipColor, FlDotCirclePainter, LineTouchTooltipData — todos existem). flutter analyze verde.

    mobile/lib/pages/profile_page.dart (1043 linhas). Estado _statsPeriod/_statsCompare/_weekly/_monthly. _loadStats 4 requests em paralelo com catchError individual. _StatsSection com StatsFilters + 4 StatsChart. flutter analyze verde.

    mobile/lib/pages/user_profile_page.dart (1110 linhas). Idem + classe _Stats403 interna + short-circuit em 403 (fase 1: summary+byType; se 403, marca _statsForbidden e para; senão fase 2: weekly+monthly). Filtros desabilitados quando forbidden || isLoading. flutter analyze verde.

3.5 Fase 3.5 — verificar save + commit

    7 arquivos com git hash-object ≠ git rev-parse HEAD:<path> confirmado.

    Tropeço S38c: git add com ^ de continuação falhou (fatal: pathspec '^' did not match any files), nada staged, commit falhou, push "Everything up-to-date". Recuperado com git add numa linha só.

    Commit c9543fb — 8 files changed, +996/−112. create mode dos 2 arquivos novos.

    Push OK (d4b8c8b..c9543fb), HEAD == origin/main, working tree limpo.

    Warnings LF→CRLF do Git no Windows — cosméticos, não erro.

3.6 Fase 4 — validação manual no Chrome

flutter run -d chrome (login prod@rumo.com). 7/7 passos verdes (descritos na Seção 1).
3.7 Observações / bugs encontrados

Nenhum bug de código na S38. Os tropeços foram todos meus/operacionais:

    S38a: "esperado" de Select-String contou errado 2× (o arquivo entregue tem quebras/comentários que não batem com o disco). Reforço: piso/faixa, sem exceção.

    S38b: Select-String -SimpleMatch com | reincidiu. Resultado veio vazio. Prova de que o arquivo estava correto veio do flutter analyze verde, não do Select-String.

    S38c: ^ de continuação do PowerShell não funciona consistentemente. O git add recebeu ^ como pathspec literal. Recuperado com uma linha só.

    S38d: "esperado" de git diff --cached --stat chutou ~+1500/−50; real foi +996/−112. O número que importa (8 files) bateu.

Desvio de expectativa (não bug) sobre o estado de follow do Prod2: o handoff da S37 registrava Prod2 seguindo: 0; a Fase 0 da S38 mediu 1 (Prod2 segue produser). Diagnóstico: o toggle follow/unfollow da validação manual da S37 alterou o backend real e o estado final persistido é prod ↔ Prod2 bidirecional. Não é bug, é estado pós-validação. Confirmado com $following | ForEach-Object { Write-Host "Prod2 segue: $($_.username)" } → Prod2 segue: produser.

Divergência de hash do build web local vs Vercel: index-DvGu4786.js (local) vs index-CJjOEm0V.js (servido). Esperado: web intocado desde S30, nenhum push de web desde então, Vercel serve o build da S36. A variação de hash local é do ambiente de build, não de código. Não é bug (S29b).
3.8 Resultado da suíte (S38)

    pytest -q → 173 passed (inalterado).

    ruff check . → All checks passed!

    npm run build → 824 modules (web inalterado).

    npm run lint → limpo (web inalterado).

    flutter analyze → No issues found! (mobile com 2 novos + 5 modificados).

    Validação manual no Chrome → 7/7.

3.9 Commit pushado (S38)
text

c9543fb feat(mobile): filtros period/compare + charts weekly/monthly (Sessao 38) — 8 files, +996/−112

Push feito. HEAD == origin/main == c9543fb. Working tree limpo.
Pendente: docs: handoff da Sessao 38 (este arquivo).
SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

(Contratos do backend inalterados desde S36 — repetidos por completude.)

GET /activities/{id}/track (auth: Bearer JWT). Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota". Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { id, user_id, activity_type, title, description, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, cover_photo_url, photo_count, created_at, likes_count, liked_by_me, comments_count, bbox: [minLon, minLat, maxLon, maxLat] | null }. Não tem user embutido (só /feed e /activities/search embutem, via FeedItemResponse).

FeedItemResponse (S36): herda de ActivityResponse e expõe autor em DUAS chaves:
python

class FeedItemResponse(ActivityResponse):
    author: UserPublic = Field(validation_alias="user")
    user: UserPublic = Field(validation_alias="user")  # [Sessão 36]

author — web. user — mobile. Ambos apontam pro mesmo Activity.user do ORM.

GET /activities?user_id=<uuid>&limit=<1..100>&offset=<>=0 (auth: Bearer JWT) — S32. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro.

GET /users/{user_id} (auth: Bearer JWT) — S32. Retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). Sem email, avatar_url, created_at, is_following. Para perfil próprio, usar GET /auth/me.

GET /auth/me — UserResponse completo: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }. NÃO é /users/me (422).

GET /activities/search?q=<min 2>&limit&offset (auth: Bearer JWT) — S10. Busca em title ILIKE %q% ou description ILIKE %q%. Visibilidade: dono OU seguido. Retorna list[FeedItemResponse] (com author E user). Rate limit: 20/min por IP.

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21. Permissão: dono OU seguidor do dono. format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.csv". Funciona com/sem rota. format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.gpx". S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. Exige rota → 404 se route IS NULL. format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22. Auth: self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). format=csv: ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota). Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

POST /activities/upload (auth: Bearer JWT) — S31. multipart/form-data: file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120), activity_type (opcional), description (opcional). Sucesso: 201 com ActivityResponse. Erro: 422/429/401. Rate limit: 10/hora por IP.

Stats:

    GET /activities/stats/summary?activity_type → StatsSummary. Inclui total_duration_s e total_calories.

    GET /activities/stats/weekly?weeks=N&activity_type → StatsWeeklyResponse ({ weeks: int, items: [StatsPeriod] }).

    GET /activities/stats/monthly?months=N&activity_type → StatsMonthlyResponse ({ months: int, items: [StatsPeriod] }).

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. Cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5. NÃO inclui avg_pace_s_per_km — pace derivado no front (computePace).

StatsPeriod (item de weekly/monthly): { period_start: string (YYYY-MM-DD), total_activities: int, total_distance_m: float, total_duration_s: int, total_calories: int }. Backend devolve items em ordem crescente de period_start.

Janelas (S17/S18/S20):
period	compare	janela
all	qualquer	null
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide)

Stats em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. ensure_can_view_stats: self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Follows:

    POST /users/{user_id}/follow — 204.

    DELETE /users/{user_id}/follow — 204.

    GET /users/{user_id}/followers?limit&offset — list[UserPublic].

    GET /users/{user_id}/following?limit&offset — list[UserPublic].

    GET /users/search?q=<min 2>&limit — list[UserPublic]. Rate limit 20/min.

⚡ NÃO existe GET /users/{id}/is-following. O cliente (web desde S19/S20; mobile desde S34) INFERE via GET /users/{meId}/following e checa se o alvo está na lista.
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–38 commitadas e pushadas. HEAD == origin/main == c9543fb. Working tree limpo.
Pendente: este handoff.

Primeira ação da Sessão 39 (REGRA S27a — handoff primeiro):
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 38"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 38 no topo, working tree limpo.
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 39 — primeira ação] Abrir PowerShell via Win+R → powershell
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 38"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 39 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 39 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432

Se o prompt já mostra (venv), PULE a linha abaixo:
powershell

.\venv\Scripts\Activate.ps1

powershell

python -m pytest -q
ruff check .

Esperado: 173 passed, ruff limpo, container Up (healthy).
[Sessão 39 — primeira ação] Detecção de versão em produção (front — Vercel)
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
# REGRA S36b: bundle é minified. Usar [regex]::Matches, não Select-String.
$chunks = [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }

Esperado (S38): web inalterado desde S30 — index-CJjOEm0V.js, ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, leaflet-Bw7RoR_1.js, recharts-DI5KUTLO.js, rolldown-runtime-hePW80VL.js.
Login (produção)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$meId = $me.id

[Sessão 39 — validação dos endpoints consumidos na S38]
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$meId = "01a12c83-be2a-71fa-b966-1c93ca64f341"

# weekly
$w = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/weekly?weeks=8" -Headers $h
Write-Host "weekly: weeks=$($w.weeks) items=$($w.items.Count) primeiro=$($w.items[0].period_start) ultimo=$($w.items[$w.items.Count-1].period_start)"

# monthly
$m = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/monthly?months=6" -Headers $h
Write-Host "monthly: months=$($m.months) items=$($m.items.Count) primeiro=$($m.items[0].period_start) ultimo=$($m.items[$m.items.Count-1].period_start)"

# by-type com period/compare (paridade com S17/S18/S20)
$bt = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d&compare=prev" -Headers $h
Write-Host "by-type 90d/prev: itens=$($bt.items.Count)"
$btYoy = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d&compare=yoy" -Headers $h
Write-Host "by-type 90d/yoy: itens=$($btYoy.items.Count)"
$btAll = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=all" -Headers $h
Write-Host "by-type all: itens=$($btAll.items.Count) (previous deve ser null em todos)"

Esperado (S38): weekly com 4 itens (2021-07-19 → 2026-11-02), monthly com 4 itens (2021-07-01 → 2026-11-01), by-type 90d/prev com N itens, by-type all com previous == null em todos.
Ruff (backend)
powershell

cd D:\Rumo\backend

Se o prompt já mostra (venv), pule:
powershell

.\venv\Scripts\Activate.ps1

powershell

ruff check .

Recuperação de arquivo corrompido (lição S21)
powershell

cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>

Se o último commit for anterior à mudança quebrada:
powershell

git restore <arquivo>

Se a versão quebrada JÁ foi commitada:
powershell

git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22 + S26c)
powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "stats/weekly|stats/monthly"

Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy.
Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b+S36b)

Mesmo script da "Detecção de versão em produção" acima. Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. ⚡ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.
Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S36 + S37 + S38)

Depois de salvar, ANTES de commitar:
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

Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou. Se [5] != [6] e [4] mostra M → save pegou, pode commitar.

⚡ REGRA S34a: o git rev-parse exige path relativo à raiz do repo (mobile/lib/main.dart), não ao CWD (lib/main.dart). O git hash-object aceita CWD.
⚡ REGRA S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS". Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b.
⚡ REGRA S32a/S32b/S33a/S36d/S38b: -SimpleMatch 'class X' casa class Xxx (prefixo). -SimpleMatch '_X' casa menções em //. -SimpleMatch 'a|b' NÃO é alternância. Para contagem exata/alternância, usar -Pattern (sem -SimpleMatch) com regex ancorado.
⚡ REGRA S33b/S34b/S38a: o "esperado" de qualquer Select-String é piso/faixa, nunca exato sem contagem real.
Contornar editor que não salva (REGRA S31c + S36f)

Se Select-String do disco mostrar conteúdo antigo depois do save do editor:
powershell

cd D:\Rumo\mobile
$content = @'
// [Sessão N] conteúdo completo do arquivo aqui (SEM PLACEHOLDER — REGRA S36g)
'@
[System.IO.File]::WriteAllText("D:\Rumo\mobile\lib\pages\arquivo.dart", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "total de linhas: $((Get-Content -Encoding UTF8 'D:\Rumo\mobile\lib\pages\arquivo.dart').Count)"

O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.
Comando git add/commit sem ^ (S38c — NOVO)

ERRADO (o ^ de continuação do PowerShell não funciona consistentemente):
powershell

git add arquivo1 ^
        arquivo2 ^
        arquivo3

CERTO (uma linha só):
powershell

git add arquivo1 arquivo2 arquivo3

CERTO também (backtick):
powershell

git add arquivo1 `
        arquivo2 `
        arquivo3

share_plus 13.x — API (S37c)
dart

// Web + nativo. Dispara download no browser (web) ou share sheet (nativo).
await SharePlus.instance.share(
  ShareParams(
    files: [XFile.fromData(bytes, mimeType: contentType, name: filename)],
    text: shareText,
    subject: filename,
  ),
);

A antiga Share.shareXFiles foi removida (mesma família de mudança do file_picker 13.x da S31b).
fl_chart 1.3.1 — API (S38 — NOVO)
dart

LineChart(
  LineChartData(
    minX: 0, maxX: (n - 1).toDouble(),
    minY: 0, maxY: yMax,
    gridData: FlGridData(
      show: true,
      drawVerticalLine: false,
      getDrawingHorizontalLine: (v) => FlLine(
        color: Color(0xFFE5E7EB), strokeWidth: 1, dashArray: [3, 3],
      ),
    ),
    borderData: FlBorderData(show: false),
    titlesData: FlTitlesData(
      // leftTitles com SideTitles(getTitlesWidget: ...)
      // bottomTitles idem
    ),
    lineTouchData: LineTouchData(
      touchTooltipData: LineTouchTooltipData(
        getTooltipColor: (_) => Colors.white,  // NÃO tooltipBgColor (removido)
        getTooltipItems: (spots) => spots.map((s) => LineTooltipItem(...)).toList(),
      ),
    ),
    lineBarsData: [
      LineChartBarData(
        spots: spots,
        isCurved: false,
        color: Color(0xFFF97316),
        barWidth: 2,
        dotData: FlDotData(
          show: true,
          getDotPainter: (spot, percent, bar, index) => FlDotCirclePainter(
            radius: 3, color: Color(0xFFF97316), strokeWidth: 0,
          ),
        ),
        belowBarData: BarAreaData(show: false),
      ),
    ],
  ),
)

Assinaturas que existem na 1.3.1 (validadas na S38): getTooltipColor, FlDotCirclePainter, LineTouchTooltipData, AxisTitles(sideTitles: SideTitles(...)), FlBorderData(show: false). tooltipBgColor foi removido — usar getTooltipColor.
Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)

ERRADO — Content é string, não byte[]:
powershell

[System.IO.File]::WriteAllBytes($path, $resp.Content)

CERTO (texto UTF-8):
powershell

[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($resp.Content))

CERTO (bytes crus — ZIP, imagem):
powershell

$fs = [System.IO.File]::OpenWrite($path)
$resp.RawContentStream.Position = 0
$resp.RawContentStream.CopyTo($fs)
$fs.Close()

MELHOR para inspecionar GPX — sem arquivo, regex no Content:
powershell

$times = [regex]::Matches($resp.Content, '<time>([^<]+)</time>')

Upload de arquivo via PowerShell (lição S33)

Invoke-RestMethod -Form NÃO existe no PS 5.1 (só PS 6+). Para multipart/form-data, usar curl.exe (nativo no Windows 10+):
powershell

curl.exe -X POST "https://rumo-api-5s0b.onrender.com/activities/upload" -H "Authorization: Bearer $($login.access_token)" -F "file=@D:\caminho\arquivo.gpx" -F "title=Titulo opcional"

Validar filtros + charts no Chrome (S38 — NOVO)
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d chrome

Login como prod@rumo.com.

Filtros: bottom nav → Perfil → seção "Estatísticas" → 2 SegmentedButton (Janela: Todas/90d/1a; Comparar com: Período anterior/Ano anterior). compare desabilitado quando period == 'all'.

4 charts: abaixo do ByTypeList — "Distância por semana (km)", "Atividades por semana", "Distância por mês (km)", "Atividades por mês". Linha laranja #f97316.

Perfil de terceiro: abrir /user/<id-do-Prod2> → com follow: stats + filtros funcionando; sem follow: filtros desabilitados + "Siga pra ver as estatísticas".

⚡ REGRA S34c/S36c: se a tela mostrar perfil errado, confirmar (a) usuário logado, (b) URL, (c) restart do flutter run.
SEÇÃO 7 — DÍVIDAS TÉCNICAS
Fechadas

    (S20) Duas pastas de venv — única é backend\venv.

    (S20) Pylance reclamando de imports — .vscode/settings.json aponta para backend/venv.

    (S25) RouteMap.tsx reutilizável — agora é lazy no ActivityDetailPage.

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

    (S35) onAuthorTap no card do feed implementado mas ninguém passava — FeedPage passa onAuthorTap condicional.

    (S36) S35a: /feed não embutia user — adicionado user ao lado de author. Mobile funcionou sem mudança. Web intacto.

    (S36) Mobile sem busca de atividades — searchActivities + SearchPage (2 abas) + rota /search.

    (S37) Mobile sem export (unitário + lote) — downloadActivityExport + downloadActivityExportBulk + saveAndShare + menu no ActivityDetailPage + card "Exportar tudo" no ProfilePage.

    (S37) Mobile sem lista de seguidores/seguindo — listFollowers + abas no UserProfilePage.

    (S38) Mobile sem filtros de period/compare na UI — StatsFilters + estado nos 2 perfis.

    (S38) Mobile sem weekly/monthly charts — StatsChart + getStatsWeekly/getStatsMonthly + 3 models.

Conhecidas (não-bug)

    (S14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.

    (S17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.

    (S18) WHERE mata a janela anterior antes do CASE WHEN.

    (S17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.

    (S17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. Não é bug. (Atualização S33: com a sintética de 2026-06-01, o previous de walk em 90d agora vem preenchido.)

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

    (S32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id, /user/:id e /search ficam FORA do shell (sem bottom nav). Decisão intencional.

    (S32) O FAB de upload some quando o usuário está na aba Perfil. Intencional.

    (S33) period/compare FIXOS no mobile (90d/prev) — FECHADO na S38 (agora têm UI).

    (S33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web).

    (S33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 em vez de text-green-600/red-600.

    (S33) O _formatThousands é inline (sem intl).

    (S33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético. Fica como dado de teste.

    (S33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Usar curl.exe.

    (S34) O backend NÃO tem GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following?limit=100.

    (S34) O _activitiesForbidden do UserProfilePage é heurístico: se listActivities voltou vazio E isFollowing==false E não é self → assume 403.

    (S34) O toggle follow/unfollow altera o backend real (não é mock). Testado nos dois sentidos e restaurado. Estado ao fim da S38: prod ↔ Prod2 bidirecional (o handoff da S37 dizia "Prod2 seguindo: 0", desatualizado).

    (S34) A inferência isFollowing com limit=100 só enxerga os primeiros 100 follows.

    (S35) O debounce da busca é manual (Timer de 300ms) em cada aba do SearchPage, não um Hook/utilitário reusável. Se aparecer terceira tela de busca, extrair pra utils/.

    (S35) O _query do SearchPage não vai pra URL. O web usa searchParams.set('q', ...) pra deep-link; no mobile é fluxo efêmero (YAGNI).

    (S35) O guard de 2 chars está DUPLICADO: client-side (ApiClient.searchUsers/searchActivities: if (len < 2) return []) e server-side (422). Dupla validação proposital.

    (S35) Os 4 avisos [flutter_map] no console do Chrome são informativos (tile server público do OSM). Formalizar tile server próprio para produção.

    (S36) O // ignore_for_file: unnecessary_overrides na linha 1 do search_page.dart suprime o lint no arquivo INTEIRO. Trade-off aceitável (arquivo pequeno, overrides justificados pelo mixin).

    (S36) A aba Usuários do SearchPage recebe autoFocus na 1ª carga; a aba Atividades não. Decisão: evita dois teclados brigando quando o usuário troca de aba.

    (S36) SearchPage usa DefaultTabController + TabBarView. Cada aba tem seu próprio estado (query, resultados, scroll) via AutomaticKeepAliveClientMixin. Trocar de aba NÃO perde estado.

    (S36) O main.dart mudou só 2 linhas (import + classe na rota /search). Nada da bottom nav ou do shell foi tocado.

    (S37) O _SocialListsSection no user_profile_page.dart carrega SEMPRE as duas listas (followers + following) no initState, mesmo que o usuário nunca abra as abas. É 2 requests extras por perfil aberto. No web, o ProfilePage.tsx faz o mesmo (hooks useFollowers/useFollowing sempre montados) — paridade. Intencional.

    (S37) O _toggleFollow do UserProfilePage NÃO recarrega as listas após follow/unfollow. Se o self segue o alvo, a lista "Seguindo (N)" do alvo não muda (é do alvo, não do self) — sem inconsistência visível. Paridade com web.

    (S37) O _exportInfo (feedback verde/âmbar) some em ~4s via Timer. O dispose cancela o Timer; pull-to-refresh cancela o antigo e agenda um novo. Sem vazamento.

    (S37) Passo 3 da validação da S37 (GPX sem rota → erro) NÃO foi exercitado por falta de atividade sem rota na conta. A lógica é idêntica à do _fetchBlob para qualquer ApiException, e o backend já está coberto por test_export.py (S21).

    (S37) share_plus 13.x removeu Share.shareXFiles — a API nova é SharePlus.instance.share(ShareParams(...)). Mesma família de mudança do file_picker 13.x (S31b).

    (S37) path_provider ^2.1.5 + share_plus ^13.3.1 conflitam com flutter_secure_storage ^11.2.0 em versões antigas. A compatível é share_plus ^13.3.1.

    (S37) flutter pub get com plugin nativo modifica pubspec.lock + 2 arquivos windows/flutter/generated_*. Os 3 entram no commit. S38 NÃO tocou nesses — fl_chart é Dart puro (não é plugin nativo).

    (S38) _loadStats do ProfilePage faz 4 requests em paralelo, cada um com catchError individual. Se um falhar, os dados dos que voltaram continuam visíveis e o erro agregado lista os que falharam ('Falha ao carregar: resumo, semanal.'). Não é bug; é UX.

    (S38) _loadStats do UserProfilePage faz short-circuit em 403 (classe _Stats403 interna). Fase 1 (summary + byType); se 403, marca _statsForbidden e não tenta weekly/monthly (o backend devolveria 403 nos 4). Economiza 2 requests em perfil de terceiro não seguido.

    (S38) StatsFilters usa String (não enum) para period/compare — consistência com getStatsByType. Constantes kStatsPeriod*/kStatsCompare* evitam string solta.

    (S38) period == 'all' desabilita só o compare (o period continua ativo). O valor de compare persiste no estado quando volta pra 90d/1a (paridade com o web: o <select> de compare não é resetado).

    (S38) StatsChart reexporta StatsPeriod (export '../models/stats.dart' show StatsPeriod;) — evita 2 imports redundantes no caller. S37e: StatsPeriod é usado de fato, então o export é legítimo.

    (S38) StatsChart não reordena items — confia na ordem do backend (crescente em period_start), paridade com PeriodChart.tsx do web.

    (S38) StatsChart mostra só alguns labels no eixo X quando tem >6 pontos (step = labels.length / 6). O web delega ao recharts; no mobile é manual, mas o efeito visual é o mesmo.

    (S38) _yInterval do StatsChart: activities = passo 5 (paridade com yMax múltiplo de 5 do web); distance = adaptativo (0.25/1/5/20/yMax/5). O web delega ao recharts.

    (S38) fl_chart 1.1.0 resolveu em 1.3.1 (o caret permite <2.0.0). getTooltipColor (não tooltipBgColor, removido), FlDotCirclePainter, LineTouchTooltipData — todos existem na 1.3.1.

    (S38) Build web local vs Vercel: index-DvGu4786.js (local) vs index-CJjOEm0V.js (servido). Esperado: web intocado desde S30, nenhum push de web desde então. Variação de hash local é do ambiente de build, não de código. Não é bug (S29b).

    (S38) Follow Prod2: o handoff da S37 registrava Prod2 seguindo: 0; mediu-se 1 na Fase 0 (Prod2 segue produser). Estado pós-validação manual da S37. Não é bug.

Oportunidades

    (S18–38) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.

    (S19–38) Stats públicas só quando viewer segue o alvo.

    (S22–37) Export em lote no mobile — FECHADO S37.

    (S30) Testes unitários do DeltaLine no web e no mobile (puro, testável).

    (S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.

    (S31) Testar upload em Android físico/emulador.

    (S31) UI dedicada para 429 (rate limit) com cooldown visual.

    (S31) activity_type como dropdown opcional na UploadPage.

    (S33) Filtros de period/compare na UI do perfil — FECHADO S38.

    (S33) Weekly/monthly charts no perfil — FECHADO S38.

    (S33) Filtros de activity_type na UI do perfil — S39+.

    (S34) Lista de seguidores/seguindo no UserProfilePage — FECHADO S37.

    (S34) Export no mobile (unitário + lote) — FECHADO S37.

    (S34) Editar perfil (peso, altura, etc.) — requer PUT /users/me ou similar, não existe — S39+ (rota travada da S39).

    (S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S39+.

    (S34) Endpoint GET /users/{id}/is-following no backend — S39+.

    (S36) Deep-link ?q= na busca mobile (se aparecer necessidade).

    (S36) Extrair o debounce manual (Timer 300ms) para um helper utils/debounce.dart se aparecer terceira tela de busca.

    (S36) Testar busca de atividades com termo vazio/1 char (guard client-side + 422 backend).

    (S36) Tile server próprio do OSM (formalizar para produção).

    (S37) Incluir botão de export unitário no web/src/pages/ActivityDetailPage.tsx para paridade com o mobile (hoje só o ProfilePage.tsx tem).

    (S37) Mostrar o _exportInfo como SnackBar (em vez de texto inline) no mobile, se a UX pedir — hoje é inline (paridade com web).

    (S37) Testar export em Android/iOS físico (hoje só Chrome/web). O share sheet nativo não foi exercitado.

    (S37) Criar atividade sintética sem rota para exercitar o passo 3 da validação da S37 (GPX → 404 "Atividade não possui rota").

    (S38) Filtros de activity_type na UI do perfil (o backend aceita em todos os 4 endpoints de stats).

    (S38) Testar StatsChart em Android/iOS físico (hoje só Chrome/web). fl_chart é Dart puro, mas o comportamento em tela pequena pode diferir.

    (S38) Extrair o padrão _loadStats de 4 requests em paralelo para um helper se aparecer terceira tela de stats (improvável).

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 39 e além)

Sessão 38 fechada. Filtros de period/compare + 4 charts weekly/monthly entregues. Backend com 173 testes, web intocado, mobile com 5 arquivos editados + 2 novos + 1 dep. Mobile subiu de ~93% para ~97% de cobertura.
Primeira ação obrigatória da Sessão 39 (REGRA S27a)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 39 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 38, push, confirmar HEAD == origin/main.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (173 passed).

    Detecção de versão em produção (front Vercel + back Render).

Rota travada para a Sessão 39

S39 = OPÇÃO 3 (Editar perfil — backend PUT /users/me + mobile EditProfilePage).

    Backend: novo endpoint PUT /users/me (ou PATCH /users/me) aceitando weight_kg, height_cm, birth_date, full_name. Schema Pydantic de update (todos opcionais). Testes em test_*_update.py (novo arquivo ou extensão de test_auth.py). Provavelmente novo router ou extensão de auth.py.

    Mobile: nova EditProfilePage acessível pelo ProfilePage (botão "Editar perfil" no _ProfileHeader). Consome PUT /users/me via ApiClient.updateMe(...). AuthService precisa expor o UserMe atual e atualizar após edição.

    Web: o ProfilePage.tsx do web já tem UI de edição? Não foi confirmado nesta sessão — precisa pedir web/src/pages/ProfilePage.tsx (já lido na S37 mas não nesta) ou confirmar que o web também precisa ganhar a paridade. Decisão pendente da S39.

    Risco: escopo maior (backend + mobile). Cabe numa sessão se for só weight_kg/height_cm/birth_date/full_name. Se incluir avatar, é S40.

Ordem de entrega da S39 (proposta):

    Fase 0 (padrão).

    Fase 1 — pedir backend/app/routers/auth.py (ou users.py), backend/app/schemas/user.py (ou equivalente), backend/app/models/user.py, backend/tests/test_auth.py, web/src/pages/ProfilePage.tsx, mobile/lib/pages/profile_page.dart, mobile/lib/models/user_me.dart, mobile/lib/services/auth_service.dart, mobile/lib/services/api.dart.

    Fase 2 — contrato: PUT /users/me (ou PATCH), body, 200/422/401, o que volta. Mobile: EditProfilePage campos, validação client-side, fluxo de save/cancel.

    Fase 3 — entrega incremental (backend primeiro, testes verdes; depois mobile).

    Fase 3.5 — verificar save + commit.

    Fase 4 — validação manual no Chrome (editar peso/altura, ver refletir no perfil; backend coberto por teste).

    Fase 5 — handoff + percentual.

Alternativas (se a S39 quiser reduzir escopo)

    OPÇÃO 3a (reduzida): só PUT /users/me com weight_kg + height_cm. Mobile ganha EditProfilePage mínima.

    OPÇÃO 3b (com web): incluir paridade web no ProfilePage.tsx.

    OPÇÃO 4 (release): tile server próprio, ícone, identidade, build assinado, política de privacidade. Bloqueadores não-código.

Recomendação final: S39 = OPÇÃO 3a (só backend PUT /users/me com weight_kg/height_cm + EditProfilePage mínima no mobile). A S40 fica para OPÇÃO 3b (web) + OPÇÃO 4 (release).
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordadas, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25 (abertura): reforçou os mesmos acordos. Tolerou 3 tropeços.

Na S26 (abertura): reforçou os mesmos acordos. Tolerou 2 tropeços.

Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a.

Na S28 (abertura): handoff S27 já commitado. Fase 1 revelou escopo real (1 arquivo, não 6).

Na S29 (abertura): handoff S28 já commitado. Fase 1 revelou 2 arquivos. Entreguei activities.ts, o usuário colou erro do ESLint no-useless-assignment — corrigi, REGRA S29d.

Na S30 (abertura): handoff S29 já commitado. Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. 1 tropeço (contagem "5x vs 6x", REGRA S29c).

Na S31 (abertura): handoff S30 já commitado (3a154b1). Fase 0 limpa. Tropeços: (1) file_picker 13.x mudou a API (REGRA S31b); (2) o editor falhou 3 vezes em salvar o upload_page.dart (REGRA S31c); (3) teste manual revelou que na web file_picker retorna path == null mas readAsBytes() funciona; (4) commit duplicado (a83ed82 + 71a00d4).

Na S32 (abertura): handoff S31 já commitado (f39820f). Fase 0 limpa. Fase 1 revelou 5 achados. Entrega incremental: 6 arquivos, 4 builds. 5 desvios de contagem (S32a–S32d). Validação manual no Chrome: 11/11.

Na S33 (abertura): handoff S32 já commitado (919ccea). Fase 0 limpa. Fase 1 revelou 6 achados. Entrega incremental: 6 arquivos, 6 builds + 1 fix. 2 desvios de contagem (S33a, S33b). Validação manual no Chrome: 12/12.

Na S34 (abertura): handoff S33 já commitado (ce09eb6). Fase 0 limpa (5 blocos). Fase 1 revelou 8 achados. Entrega incremental: 4 arquivos, 4 builds. 2 desvios de contagem (S34a, S34b) + 1 achado operacional (S34c). Validação manual no Chrome: 9/9.

Na S35 (abertura): handoff S34 já commitado (2b312ec). Fase 0 limpa. Fase 1 revelou 8 achados. Entrega incremental: 5 arquivos, 4 builds. 3 desvios de contagem. Validação manual no Chrome: 8/8 + achado S35a.

Na S36 (abertura): handoff S35 já commitado (8bff66b). Fase 0 limpa (5 blocos). Fase 1 revelou 8 achados, incluindo o crítico: /feed já devolvia author, só que o mobile lia user. Entrega incremental: 4 arquivos (1 novo backend, 1 novo teste backend, 1 editado mobile, 1 novo mobile), 3 commits. MUITOS tropeços: $times[-1] no PS 5.1 (S36a), Select-String -SimpleMatch 'a|b|c' (S36d), placeholder em here-string (S36g, recuperado), 3 tentativas de // ignore: (solução: // ignore_for_file na linha 1 — S36e), editor falhou 2× em salvar search_page.dart (S36f), 2 desvios de contagem, 1 desvio de tela (S36c). Validação manual no Chrome: 7/7 + 1 iteração no feed.

Na S37 (abertura): handoff S36 já commitado (b05e870, fora do chat). Fase 0 limpa (6 blocos verdes). Fase 1 revelou 8 achados. Entrega incremental: 6 arquivos (1 de deps + 1 novo + 4 editados), 6 builds + 2 fixes de lint. Tropeços: (1) conflito de versão share_plus 12.0.1 vs flutter_secure_storage 11.2.0 — resolvido lendo a sugestão do pub (share_plus ^13.3.1, REGRA S37a); (2) unused_import: dart:typed_data em activity_detail_page.dart (removido, REGRA S37e); (3) unnecessary_underscores (_, __) em user_profile_page.dart (fix trivial, REGRA S37f). pub get modificou 3 arquivos gerados (REGRA S37b). Validação manual no Chrome: 6/7 (passo 3 não aplicável — sem atividade sem rota).

Na S38 (abertura): handoff S37 já commitado (d4b8c8b, fora do chat). Fase 0 limpa (6 blocos verdes). Fase 1 revelou 8 achados. Entrega incremental: 7 arquivos (1 de deps + 2 novos + 4 editados), 7 builds. Tropeços: (1) "esperado" de Select-String errou 2× (S38a — piso/faixa, sem exceção); (2) Select-String -SimpleMatch com | reincidiu (S38b — reforço da S36d); (3) ^ de continuação do PowerShell falhou no git add (S38c — usar uma linha só); (4) "esperado" de git diff --cached --stat chutou ~+1500/−50, real foi +996/−112 (S38d — piso/faixa). fl_chart 1.3.1 compilou sem ajuste de API (a aposta na assinatura da 1.3.1 pagou). Validação manual no Chrome: 7/7.

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Acordo novo na S32: manter o processo da S21–S31. Concretamente:

    Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

    Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> (com path relativo à RAIZ do repo — REGRA S34a) + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b + S34b + S38a: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c). git add com todos os paths numa linha só (REGRA S38c).

    Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local. REGRA S34c: no mobile, confirmar login/URL/restart antes de declarar bug de tela.

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S38 (Seção 0, itens 60–63): S38a (piso/faixa sem exceção — mesmo contando o arquivo entregue), S38b (-SimpleMatch com | é sempre erro — reforço), S38c (^ de continuação do PowerShell não é confiável — usar uma linha só ou backtick), S38d ("esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas).

O que funcionou nas S21–S38 (manter):

    Ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão).

    Disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33, S34, S35, S36, S37, S38).

    Consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor, sessão do localStorage, tela errada, placeholder em here-string, conflito de versão de plugin, import não usado, ^ de continuação, hash git diff --cached --stat) na hora e corrigir/registrar, sem contornar.

    A S38 acrescentou: ler o erro inteiro do pub get antes de consertar (o pub sugere a versão compatível); validar a API do fl_chart 1.3.1 antes de codar (a aposta pagou — getTooltipColor, FlDotCirclePainter, LineTouchTooltipData existem); curto-circuitar em 403 nos stats de terceiro (economiza 2 requests); usar String + constantes em vez de enum para paridade de API.