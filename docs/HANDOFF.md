HANDOFF — Rumo (backend + frontend + mobile) — Sessão 37
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. NÃO existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

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

⚡ REGRA S37a (NOVA) — conflito de versão de plugin no pub get: ler o erro inteiro antes de tentar consertar. O pub sugere a versão compatível no final do output ("Try upgrading your constraint on X: Y"). Usar a sugestão em vez de adivinhar. Caso da S37: share_plus ^12.0.1 + flutter_secure_storage ^11.2.0 brigavam por win32 (6.x vs 5.x). Solução: share_plus ^13.3.1.

⚡ REGRA S37b (NOVA) — ao adicionar plugin nativo ao pubspec.yaml, o pub get modifica pubspec.lock + windows/flutter/generated_plugin_registrant.cc + windows/flutter/generated_plugins.cmake. Esses 3 entram no commit junto (não são "lixo").

⚡ REGRA S37c (NOVA) — share_plus 13.x: API nova é SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])). A antiga Share.shareXFiles foi removida (mesma família de mudança do file_picker 13.x da S31b).

⚡ REGRA S37d (NOVA) — ao testar download no Chrome, o share_plus dispara o download no browser via Share API. O arquivo aparece na barra de downloads do Chrome, não no share sheet do SO (que não existe no Chrome). É o comportamento esperado.

⚡ REGRA S37e (NOVA) — ao adicionar import que parece necessário mas o tipo vem por inferência (Uint8List do result.bytes), o flutter analyze acusa unused_import. Remover o import (não forçar uso). Caso da S37: dart:typed_data no activity_detail_page.dart.

⚡ REGRA S37f (NOVA) — unnecessary_underscores (Dart 3.7+): (_, __) vira (_, _) em callbacks com múltiplos parâmetros ignorados. O flutter analyze acusa info, não warning.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (173 passed ao fim da S37). Container de teste rumo_postgres_test na porta 5433.

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
│   │   │   stats.dart ← S33, user.dart ← S34, user_me.dart ← S32)
│   │   ├── pages/ (activity_detail_page.dart ← EDITADO S37 (menu export),
│   │   │   feed_page.dart, login_page.dart,
│   │   │   profile_page.dart ← EDITADO S37 (seção "Exportar tudo"),
│   │   │   search_page.dart ← S36, upload_page.dart ← S31,
│   │   │   user_profile_page.dart ← EDITADO S37 (abas Seguidores/Seguindo))
│   │   ├── services/ (api.dart ← EDITADO S37 (+4 métodos),
│   │   │   auth_service.dart)
│   │   ├── utils/ (download.dart ← NOVO S37 (saveAndShare + countZipEntries),
│   │   │   format.dart ← S33)
│   │   └── widgets/ (activity_card.dart ← S34, activity_map.dart,
│   │       by_type_list.dart ← S33, like_button.dart,
│   │       stats_cards.dart ← S33)
│   ├── pubspec.yaml (file_picker: ^13.3.3, go_router: ^18.1.2,
│   │   path_provider: ^2.1.5 ← S37, share_plus: ^13.3.1 ← S37,
│   │   name: rumo_mobile)
│   ├── pubspec.lock
│   └── windows/flutter/ (generated_plugin_registrant.cc,
│       generated_plugins.cmake — modificados pelo pub get S37)
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

⚡ mobile/lib/pages/user_search_page.dart NÃO EXISTE MAIS (removido na S36). Foi substituído por search_page.dart (2 abas: Usuários | Atividades).
Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades (7 + 1 sintética da S33), 34.08 km. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min) usada pra validar o S26 e o export GPX da S37. Tem atividade sintética "Teste delta S33 (janela anterior)" (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null). Username no backend: produser (confirmado na S36 via /feed).

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2. Usado pra validar abas Seguidores/Seguindo na S37.

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).
Acordos de trabalho (válidos em todas as sessões — reforçados na S21 à S37)

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

    Select-String -SimpleMatch não aceita | como alternância (S25a, reforçada S33a, S36d).

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

    Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA (S32d, reforçada S33b).

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

Processo que o usuário elogiou na S21–S37 (para manter)

Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).
SEÇÃO 1 — TL;DR para quem chega agora

Backend: 173 testes passando LOCALMENTE, 0 warnings. Sem mudança na S37. FeedItemResponse expõe autor em author (web) + user (mobile) desde S36. Todos os endpoints do MVP em produção.

Web: intocado desde S30. ActivityDetailPage.tsx não tem botão de export unitário (só o ProfilePage.tsx tem "Exportar tudo") — o mobile ganhou o botão no detalhe como adição de paridade, não espelho. Build/lint limpos.

Mobile: flutter analyze limpo. S37 adicionou:

    Export unitário (ActivityDetailPage → menu AppBar com "Exportar CSV" / "Exportar GPX"). ApiClient.downloadActivityExport.

    Export em lote (ProfilePage → card "Exportar tudo" com formato + datas + feedback âmbar/verde/vermelho). ApiClient.downloadActivityExportBulk + countZipEntries.

    Followers/Following (UserProfilePage → abas Seguidores/Seguindo abaixo das atividades). ApiClient.listFollowers (novo) + listFollowing (já existia).

    utils/download.dart (novo): saveAndShare (web: download no browser; nativo: share sheet) + countZipEntries (EOCD fail-open).

    Deps novas: path_provider ^2.1.5, share_plus ^13.3.1. O pub get também modificou pubspec.lock + 2 arquivos windows/flutter/generated_*.

Endpoints relevantes para export (S37 — consumidos pelo mobile)
text

GET /activities/{id}/export?format=csv|gpx   — auth dono OU seguidor
GET /activities/export?format=csv|gpx[&from][&to]  — auth self-only → ZIP
GET /users/{id}/followers?limit&offset       — auth Bearer JWT
GET /users/{id}/following?limit&offset       — auth Bearer JWT

O export unitário devolve Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>". O lote devolve Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip". O ApiClient._fetchBlob parseia o filename via regex filename="([^"]+)".
S37 — validação manual no Chrome (6/7)

    Passo 1 (CSV no detalhe): ✅

    Passo 2 (GPX no detalhe): ✅

    Passo 3 (GPX sem rota → erro): ⏸️ não aplicável (todas as 8 atividades têm rota). Lógica idêntica ao erro genérico do _fetchBlob; backend testado por test_export.py (S21).

    Passo 4 (Export em lote, CSV, 8 atividades): ✅

    Passo 5 (ZIP vazio → âmbar): ✅

    Passo 6 (from > to → erro client-side): ✅

    Passo 7 (abas Seguidores/Seguindo no Prod2): ✅

Commits S37:
text

15f7602 (HEAD -> main, origin/main) feat(mobile): export CSV/GPX (unitario + lote) + followers/following (Sessao 37)
b05e870 docs: handoff da Sessao 36
dba8594 refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36)
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36)
86179f2 feat(backend): expoe user no FeedItemResponse + testes de /feed (Sessao 36)
8bff66b docs: handoff da Sessao 35

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

    Deps mobile (S31/S32/S33/S34/S35/S36/S37): file_picker: ^13.3.3, go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1. Package name: rumo_mobile.

Git (estado ao fim da Sessão 37):
text

15f7602 (HEAD -> main, origin/main) feat(mobile): export CSV/GPX (unitario + lote) + followers/following (Sessao 37)
b05e870 docs: handoff da Sessao 36
dba8594 refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36)
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36)
86179f2 feat(backend): expoe user no FeedItemResponse + testes de /feed (Sessao 36)
8bff66b docs: handoff da Sessao 35
199040d feat(mobile): rota /search fora do shell (Sessao 35)
d71d9fb feat(mobile): busca no feed + link do autor (Sessao 35)
25778ed feat(mobile): busca de usuarios (Sessao 35)
2b312ec docs: handoff da Sessao 34

Working tree limpo. S37 adicionou 1 commit (15f7602, 9 files changed, +1107/−5).
Pendente: docs/HANDOFF.md da S37 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 37.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 37
3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short mostrou working tree limpo (b05e870 já commitado antes da sessão começar — o usuário commitou fora do chat). Sem M docs/HANDOFF.md.

    Log/status. HEAD == origin/main == b05e870. Working tree limpo.

    Build/lint/analyze. npm run build: 824 modules, 6.72s, index-DvGu4786.js (hash novo vs index-CJjOEm0V.js da S36), chunks-folha idênticos — renomeação de referência cruzada (REGRA S28b), web intocado. npm run lint: limpo. flutter analyze: No issues found! (58.1s — cache frio).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. Container rumo_postgres_test Started no primeiro up -d (healthy em ~1min). pg_isready "no response" na 1ª tentativa (container subindo) → "accepting connections" na 2ª. pytest -q: 173 passed in 62.43s. ruff check .: All checks passed!.

    Prod backend. S36 FeedItemResponse: 3 itens, author=True, user=True, author.id == user.id, ambos produser. S26 GPX: 60 <time>, 60 distintos, primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z.

    Prod frontend. index-CJjOEm0V.js + 7 chunks batendo 1:1 com S36. Web intocado desde S30.

3.2 Fase 1 — descoberta

Pedidos e recebidos: web/src/api/activities.ts, mobile/lib/pages/activity_detail_page.dart, mobile/lib/services/api.dart, mobile/pubspec.yaml, web/src/pages/ProfilePage.tsx, Get-ChildItem web/src e mobile/lib. Depois: mobile/lib/pages/profile_page.dart (antes do arquivo 5) e mobile/lib/pages/user_profile_page.dart (antes do arquivo 6).

ACHADOS que moldaram o plano:

    #1 O api.dart mobile não tem helper de download binário (só get/post/delete com jsonDecode). Precisa de _fetchBlob.

    #2 O pubspec.yaml mobile não tem path_provider/share_plus/url_launcher. Só file_picker, http, flutter_secure_storage, go_router, flutter_map, latlong2.

    #3 O web/src/api/activities.ts usa _triggerDownload via <a download> + Blob (padrão web). No mobile, FilePicker.saveFile é desktop-only no 13.x (mesma família de mudança do S31b) — não serve.

    #4 O ProfilePage.tsx web tem a seção "Exportar tudo" (formato + De + Até + botão) e as abas followers/following no fim. Paridade direta.

    #5 O web/src/pages/ActivityDetailPage.tsx não foi pedido — o web/src/api/activities.ts tem downloadActivityExport (unitário), mas não se sabe se o detalhe web tem botão. Assumido que não tem (adição de paridade no mobile, não espelho). Se a S38 descobrir que tem, é só alinhar a UI.

    #6 O _extractMessage do mobile só entende JSON com detail — funciona no export porque o FastAPI devolve JSON de erro mesmo no export.

    #7 O _send mobile fixa Accept: application/json. _fetchBlob usa Accept: */*.

    #8 Content-Disposition do backend tem filename="rumo_<id>_<type>.csv" (S21) ou filename="rumo_export_<YYYYMMDD-HHMMSS>.zip" (S22).

3.3 Fase 2 — contrato travado

Decisão de dependência: adicionar path_provider ^2.1.5 + share_plus ^13.3.1 (12.0.1 brigava com flutter_secure_storage 11.2.0 por win32). Sem essas, o download no Android/iOS fica inútil.

Escopo:

    OPÇÃO 1 — Export mobile (unitário + lote). ApiClient + activity_detail_page.dart + profile_page.dart.

    OPÇÃO 2 — Followers/Following no UserProfilePage. ApiClient.listFollowers + user_profile_page.dart.

    Backend: zero. Web: zero. Mobile: 6 arquivos (2 deps + 4 de código) + 1 novo (utils/download.dart).

Ordem ajustada (por dependência de import): pubspec.yaml → utils/download.dart (novo, sem deps internas) → api.dart (importa download.dart) → activity_detail_page.dart → profile_page.dart → user_profile_page.dart.
3.4 Fase 3 — entrega incremental

    pubspec.yaml (+2 deps). FALHOU no pub get: conflito share_plus 12.0.1 × flutter_secure_storage 11.2.0 por win32 (5.x vs 6.x). O pub sugeriu share_plus ^13.3.1 → pub get + flutter analyze verdes (52.4s). pub get modificou pubspec.lock + windows/flutter/generated_plugin_registrant.cc + windows/flutter/generated_plugins.cmake (REGRA S37b).

    mobile/lib/utils/download.dart (novo, 109 linhas). saveAndShare (web: share_plus download no browser; nativo: getTemporaryDirectory + share_plus) + countZipEntries (EOCD fail-open, porta do web S29). flutter analyze verde.

    mobile/lib/services/api.dart (704 linhas, +4 métodos): _fetchBlob, downloadActivityExport, downloadActivityExportBulk, listFollowers. Imports novos: dart:typed_data, ../utils/download.dart. flutter analyze verde.

    mobile/lib/pages/activity_detail_page.dart (645 linhas). Menu PopupMenuButton<_ExportFormat> no AppBar.actions (CSV/GPX) + _export() + _exporting bool. flutter analyze acusou unused_import: dart:typed_data (o saveAndShare recebe Uint8List por inferência do result.bytes). Removido via PowerShell cirúrgico (1 linha). flutter analyze verde.

    mobile/lib/pages/profile_page.dart (905 linhas). _ExportSection (dropdown + 2 date pickers + botão + feedback âmbar/verde/vermelho), _DateField, _BulkExportFormat, _ExportInfo, _ExportInfoKind. Timer de 4s para limpar feedback (paridade web S24). Validação client-side from > to. flutter analyze verde.

    mobile/lib/pages/user_profile_page.dart (946 linhas). _SocialListsSection (abas Seguidores/Seguindo), _UserRow, _TabButton, _loadLists() (Future.wait([listFollowers, listFollowing])). flutter analyze acusou unnecessary_underscores ((_, __) → (_, _)), fix trivial. flutter analyze verde.

3.5 Fase 3.5 — verificar save + commit

    Hash check dos 6 arquivos: todos OK (diferente).

    Commit 15f7602 — 9 files changed, +1107/−5, create mode do download.dart.

    Push OK (b05e870..15f7602), HEAD == origin/main, working tree limpo.

    Warnings LF→CRLF do Git no Windows (autocrlf) — cosméticos, não erro.

3.6 Fase 4 — validação manual no Chrome

flutter run -d chrome (login prod@rumo.com).

    Passo 1 (CSV no detalhe): ✅ menu aparece, download dispara (rumo_<id>_<type>.csv).

    Passo 2 (GPX no detalhe): ✅ download dispara (rumo_<id>_<type>.gpx).

    Passo 3 (GPX sem rota): ⏸️ não aplicável — todas as 8 atividades da conta têm rota.

    Passo 4 (lote CSV, 8 atividades): ✅ ZIP baixa, feedback verde "Download iniciado (8 atividades)."

    Passo 5 (lote com período vazio): ✅ ZIP vazio, feedback âmbar "Nenhuma atividade no período — ZIP vazio."

    Passo 6 (from > to): ✅ não chama backend, erro vermelho "A data inicial não pode ser maior que a final."

    Passo 7 (abas Seguidores/Seguindo no Prod2): ✅ Seguindo (0) com mensagem, Seguidores (≥1) com @produser, tap navega pra /user/<id-do-prod>.

3.7 Observações / bugs encontrados

Nenhum bug de código na S37. Os erros foram todos meus/operacionais:

    S37a: conflito de versão no pub get (resolvido lendo a sugestão do pub).

    S37e: import dart:typed_data desnecessário em activity_detail_page.dart (removido).

    S37f: unnecessary_underscores em user_profile_page.dart (fix trivial).

3.8 Resultado da suíte (S37)

    pytest -q → 173 passed (inalterado).

    ruff check . → All checks passed!.

    npm run build → 824 modules (web inalterado).

    npm run lint → limpo (web inalterado).

    flutter analyze → No issues found! (mobile com 1 novo + 4 modificados).

    Validação manual no Chrome → 6/7 (passo 3 não aplicável).

3.9 Commit pushado (S37)
text

15f7602 feat(mobile): export CSV/GPX (unitario + lote) + followers/following (Sessao 37) — 9 files, +1107/−5

Push feito. HEAD == origin/main == 15f7602. Working tree limpo.
Pendente: docs: handoff da Sessao 37 (este arquivo).
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

    GET /activities/stats/weekly?weeks=N&activity_type → StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N&activity_type → StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. Cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5. NÃO inclui avg_pace_s_per_km — pace derivado no front (computePace).

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

    GET /users/{user_id}/followers?limit&offset — list[UserPublic]. (consumido pelo ApiClient.listFollowers desde S37)

    GET /users/{user_id}/following?limit&offset — list[UserPublic]. (usado pelo isFollowing do mobile desde S34)

    GET /users/search?q=<min 2>&limit — list[UserPublic]. Rate limit 20/min.

⚡ NÃO existe GET /users/{id}/is-following. O cliente (web desde S19/S20; mobile desde S34) INFERE via GET /users/{meId}/following e checa se o alvo está na lista.
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–37 commitadas e pushadas. HEAD == origin/main == 15f7602. Working tree limpo.
Pendente: este handoff.
Primeira ação da Sessão 38 (REGRA S27a — handoff primeiro)
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 37"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 37 no topo, working tree limpo.
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 38 — primeira ação] Abrir PowerShell via Win+R → powershell
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 37"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 38 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 38 — primeira ação] Docker + pytest local
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

Esperado: 173 passed, ruff limpo, container Up (healthy). Se pg_isready der "no response", rodar de novo — o container pode estar subindo (S37).
[Sessão 38 — primeira ação] Detecção de versão em produção (front — Vercel)
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
# REGRA S36b: bundle é minified. Usar [regex]::Matches, não Select-String.
$chunks = [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }

Esperado (S37): web inalterado desde S30 — index-CJjOEm0V.js, ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, RouteMap-CXXXy7Mv.js, leaflet-Bw7RoR_1.js, recharts-DI5KUTLO.js, rolldown-runtime-hePW80VL.js.
Login (produção)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$meId = $me.id

[Sessão 38 — validação dos endpoints consumidos na S37]
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$prod2 = "01a141e7-5ea4-7600-8959-19145475ad0a"

# followers / following do Prod2 (abas da S37)
$followers = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2/followers?limit=100&offset=0" -Headers $h
$following = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2/following?limit=100&offset=0" -Headers $h
Write-Host "Prod2 seguidores: $($followers.Count) (esperado: >= 1 — produser)"
Write-Host "Prod2 seguindo:   $($following.Count) (esperado: 0)"

# export unitario GPX (botao do detalhe)
$aid = "01a1b36a-0951-71e8-9044-c55c71558441"
$gpx = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$aid/export?format=gpx" -Headers $h -UseBasicParsing
$cd = $gpx.Headers['Content-Disposition']
Write-Host "Content-Disposition GPX: $cd"
Write-Host "Content-Type GPX: $($gpx.Headers['Content-Type'])"

# export em lote (botao do perfil)
$zip = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/export?format=csv" -Headers $h -UseBasicParsing
$cdZip = $zip.Headers['Content-Disposition']
Write-Host "Content-Disposition ZIP: $cdZip"
Write-Host "Content-Type ZIP: $($zip.Headers['Content-Type'])"

Esperado: Prod2 seguidores: 1, Prod2 seguindo: 0, Content-Disposition GPX: attachment; filename="rumo_...", Content-Type GPX: application/gpx+xml; charset=utf-8, Content-Disposition ZIP: attachment; filename="rumo_export_...", Content-Type ZIP: application/zip.
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

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"

Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy.
Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b+S36b)

Mesmo script da "Detecção de versão em produção" acima. Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. ⚡ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.
Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S36 + S37)

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
⚡ REGRA S32a/S32b/S33a/S36d: -SimpleMatch 'class X' casa 'class Xxx' (prefixo). -SimpleMatch '_X' casa menções em //. -SimpleMatch 'a|b' NÃO é alternância. Para contagem exata/alternância, usar -Pattern (sem -SimpleMatch) com regex ancorado.
⚡ REGRA S33b/S34b: o "esperado" de qualquer Select-String é piso/faixa, nunca exato sem contagem real.
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
Resolver conflito de versão no pub get (S37a — NOVO)

Quando pub get falhar por conflito de versão, ler o final do output. O pub sugere a correção:
text

You can try the following suggestion to make the pubspec resolve:
* Try upgrading your constraint on <pacote>: <versão>

Aplicar a sugestão no pubspec.yaml (versão exata sugerida) e rodar pub get de novo.
share_plus 13.x — API (S37c — NOVO)
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

Validar export no Chrome (S37 — NOVO)
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d chrome

Login como prod@rumo.com.

Export unitário: feed → tocar atividade → AppBar → ícone compartilhar → "Exportar CSV"/"Exportar GPX". O download aparece na barra de downloads do Chrome (não share sheet — REGRA S37d).

Export em lote: bottom nav → Perfil → card "Exportar tudo". Feedback verde/âmbar/vermelho inline.

Followers/Following: abrir /user/<id-do-Prod2> → rolar até o fim → abas Seguidores/Seguindo.

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

    (S33) period/compare FIXOS no mobile (90d/prev). O web tem filtros de UI. Filtros ficam pra S38+.

    (S33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web).

    (S33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 em vez de text-green-600/red-600.

    (S33) O _formatThousands é inline (sem intl).

    (S33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético. Fica como dado de teste.

    (S33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Usar curl.exe.

    (S33) Weekly/monthly charts no mobile ficam pra S38+ (recharts no web; no mobile, seria fl_chart ou similar — decisão de dependência).

    (S34) O backend NÃO tem GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following?limit=100.

    (S34) O _activitiesForbidden do UserProfilePage é heurístico: se listActivities voltou vazio E isFollowing==false E não é self → assume 403.

    (S34) O toggle follow/unfollow altera o backend real (não é mock). Testado nos dois sentidos e restaurado.

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

    (S37) Passo 3 da validação (GPX sem rota → erro) NÃO foi exercitado por falta de atividade sem rota na conta. A lógica é idêntica à do _fetchBlob para qualquer ApiException, e o backend já está coberto por test_export.py (S21).

    (S37) share_plus 13.x removeu Share.shareXFiles — a API nova é SharePlus.instance.share(ShareParams(...)). Mesma família de mudança do file_picker 13.x (S31b).

    (S37) path_provider ^2.1.5 + share_plus ^13.3.1 conflitam com flutter_secure_storage ^11.2.0 em versões antigas. A compatível é share_plus ^13.3.1.

    (S37) flutter pub get com plugin nativo modifica pubspec.lock + 2 arquivos windows/flutter/generated_*. Os 3 entram no commit.

Oportunidades

    (S18–37) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.

    (S19–37) Stats públicas só quando viewer segue o alvo.

    (S22–37) Export em lote no mobile — FECHADO S37.

    (S30) Testes unitários do DeltaLine no web e no mobile (puro, testável).

    (S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.

    (S31) Testar upload em Android físico/emulador.

    (S31) UI dedicada para 429 (rate limit) com cooldown visual.

    (S31) activity_type como dropdown opcional na UploadPage.

    (S33) Filtros de period/compare na UI do perfil (S38+).

    (S33) Weekly/monthly charts no perfil (S38+).

    (S34) Lista de seguidores/seguindo no UserProfilePage — FECHADO S37.

    (S34) Export no mobile (unitário + lote) — FECHADO S37.

    (S34) Editar perfil (peso, altura, etc.) — requer PUT /users/me ou similar, não existe — S38+.

    (S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S38+.

    (S34) Endpoint GET /users/{id}/is-following no backend — S38+.

    (S36) Deep-link ?q= na busca mobile (se aparecer necessidade).

    (S36) Extrair o debounce manual (Timer 300ms) para um helper utils/debounce.dart se aparecer terceira tela de busca.

    (S36) Testar busca de atividades com termo vazio/1 char (guard client-side + 422 backend).

    (S36) Tile server próprio do OSM (formalizar para produção).

    (S37) Incluir botão de export unitário no web/src/pages/ActivityDetailPage.tsx para paridade com o mobile (hoje só o ProfilePage.tsx tem).

    (S37) Mostrar o _exportInfo como SnackBar (em vez de texto inline) no mobile, se a UX pedir — hoje é inline (paridade com web).

    (S37) Testar export em Android/iOS físico (hoje só Chrome/web). O share sheet nativo não foi exercitado.

    (S37) Criar atividade sintética sem rota para exercitar o passo 3 da validação (GPX → 404 "Atividade não possui rota").

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 38 e além)

Sessão 37 fechada. Export mobile (unitário + lote) + followers/following entregues. Backend com 173 testes, web intocado, mobile com 4 arquivos editados + 1 novo + 2 deps. Mobile subiu de ~88% para ~93% de cobertura.
Primeira ação obrigatória da Sessão 38 (REGRA S27a)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 38 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 37, push, confirmar HEAD == origin/main.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (173 passed).

    Detecção de versão em produção (front Vercel + back Render).

Rota travada para a Sessão 38

Escolha OPÇÃO 1 (recomendada): Filtros de period/compare na UI do perfil mobile (paridade com web S17/S20).

    Mexe em profile_page.dart + user_profile_page.dart + stats_cards.dart/by_type_list.dart.

    Backend já suporta (period, compare no by-type; activity_type nos 4 endpoints).

    Requer: ver web/src/components/StatsCards.tsx, web/src/components/PeriodChart.tsx (já temos o ProfilePage.tsx) para paridade de UX. Decidir se os filtros ficam no topo (como no web) ou num menu.

    Risco: nenhum no backend. Só UI.

Escolha OPÇÃO 2: Weekly/monthly charts no perfil (paridade com web S13/S14).

    Requer dependência nova no mobile: fl_chart ou similar (decisão de dependência — charts_flutter está descontinuado).

    Mexe em profile_page.dart + user_profile_page.dart + novo widget stats_charts.dart.

    Backend já suporta (/stats/weekly e /stats/monthly).

    Risco: decisão de dependência (S31a — plugin nativo se tiver; fl_chart é Dart puro, sem código nativo, então OK no Windows sem Developer Mode).

Escolha OPÇÃO 3: Editar perfil (peso/altura).

    Requer endpoint novo PUT /users/me no backend (não existe).

    Mexe em backend/app/routers/auth.py (ou users.py) + schema novo + EditProfilePage no mobile.

    Escopo maior (backend + mobile). Cabe numa sessão se for só peso/altura.

Escolha OPÇÃO 4: Encerrar features e partir para release.

    Tile server próprio, ícone, identidade visual, build assinado Android/iOS, política de privacidade, screenshots.

    Bloqueadores não-código que só o usuário resolve.

Recomendação final para a Sessão 38

S38 = OPÇÃO 1 (filtros period/compare no perfil mobile) + OPÇÃO 2 (weekly/monthly charts com fl_chart).

    São features de UI puras, backend já suporta, zero risco de regressão no backend.

    A S39 fica para OPÇÃO 3 (editar perfil — backend + mobile).

    A S40 fica para OPÇÃO 4 (release — bloqueadores não-código).

Antes de codar a S38: Fase 1 precisa pedir os arquivos relevantes:

    web/src/components/StatsCards.tsx

    web/src/components/PeriodChart.tsx

    web/src/hooks/useStats.ts

    mobile/lib/widgets/stats_cards.dart

    mobile/lib/widgets/by_type_list.dart

    mobile/lib/models/stats.dart

    mobile/lib/pages/profile_page.dart (já temos)

    mobile/lib/pages/user_profile_page.dart (já temos)

E decidir a lib de charts: fl_chart (Dart puro, sem nativo, mais popular) vs syncfusion_flutter_charts (mais features, licença comercial para algumas). Recomendação: fl_chart (licença MIT, sem código nativo, sem Developer Mode).
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

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Acordo novo na S32: manter o processo da S21–S31. Concretamente:

    Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

    Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> (com path relativo à RAIZ do repo — REGRA S34a) + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b + S34b: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c).

    Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local. REGRA S34c: no mobile, confirmar login/URL/restart antes de declarar bug de tela.

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S37 (Seção 0, itens 60–65): S37a (conflito de versão no pub get — ler o erro inteiro antes de consertar), S37b (pub get de plugin nativo modifica 3 arquivos gerados), S37c (share_plus 13.x API nova), S37d (download no Chrome via share_plus = download no browser, não share sheet), S37e (import não usado por inferência → remover, não forçar uso), S37f (unnecessary_underscores: (_, __) → (_, _)).
O que funcionou nas S21–S37 (manter)

    Ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão).

    Disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33, S34, S35, S36).

    Consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor, sessão do localStorage, tela errada, placeholder em here-string, conflito de versão de plugin, import não usado) na hora e corrigir/registrar, sem contornar.

    A S37 acrescentou: ler o erro inteiro do pub get antes de consertar (o pub sugere a versão compatível); aceitar info de lint mesmo sendo cosmético (fixar antes de commitar); documentar que o pub get de plugin nativo toca 3 arquivos gerados.

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 37)
Backend — ~97% (inalterado)

    173 testes verdes, ruff limpo.

    Todos os endpoints do MVP funcionam em prod (auth, atividades CRUD, track, upload GPX/FIT, export CSV/GPX unitário + lote, stats summary/weekly/monthly/by-type, follows, followers/following, search usuários, search atividades).

    Falta: PUT /users/me (editar perfil), GET /users/{id}/is-following (elimina inferência no client), índice GIN gin_trgm_ops em title/description (escala de busca), paginação real no /activities (envelope), tile server do OSM (não é backend nosso, é infra).

    Backend não tem nenhum bloqueador para MVP.

Web — ~92% (inalterado desde S30)

    Build/lint limpos, 824 modules, bundle estável.

    Todas as telas do MVP: login, feed, detalhe, perfil self, perfil de terceiro, busca (usuários + atividades), upload, export unitário + lote.

    Falta: filtros de period/compare na UI (S38+), weekly/monthly charts mais elaborados (recharts já está lá, mas é básico), editar perfil (depende de endpoint), botão de export unitário no ActivityDetailPage.tsx (hoje só o ProfilePage.tsx tem).

    Web não tem nenhum bloqueador para MVP.

Mobile — ~93% (subiu de ~88% na S36)

    flutter analyze limpo, export (unitário + lote) + followers/following funcionando, 6/7 na validação manual.

    Telas: login, feed, detalhe, perfil self, perfil de terceiro, busca (usuários + atividades), upload, export (unitário + lote), abas followers/following, bottom nav.

    Falta: filtros de period/compare, weekly/monthly charts, editar perfil, refresh token / logout 401, upload em Android físico (só testado no Chrome web), export em Android/iOS físico (share sheet nativo não exercitado), tile server próprio (mesma dívida do backend), ícone/identidade visual, build Android/iOS assinado.

    Mobile tem bloqueadores não-código para release (loja, ícone, assinatura).

Bloqueadores não-código (para MVP em loja)

    Tile server próprio do OSM (hoje usa o público; não escala para produção).

    Ícone + identidade visual do app.

    Conta de desenvolvedor Google Play (~US25uˊnico)eAppleDeveloper(US25uˊnico)eAppleDeveloper(US 99/ano).

    Build assinado (Android keystore + iOS provisioning profile).

    Política de privacidade e Termos de uso (exigidos pelas lojas).

    Screenshots e descrição para as lojas.

    Testes em dispositivo físico (Android e iOS) — hoje só Chrome/web.

Consolidado: ~94% (média ponderada)

Média ponderada: backend 0.3 × 0.97 + web 0.3 × 0.92 + mobile 0.4 × 0.93 = 0.291 + 0.276 + 0.372 = 0.939 ≈ 94%.

Subiu de 91% (S36) para 94% (S37) graças ao mobile (88% → 93%).
Estimativa de sessões restantes para o MVP em loja: 3–5 sessões

    S38: filtros period/compare + weekly/monthly charts (fl_chart).

    S39: editar perfil (backend PUT /users/me + mobile EditProfilePage) + botão de export unitário no web (paridade).

    S40: tile server próprio + ícone + identidade + build assinado Android + política de privacidade.

    S41: submissão Google Play + correções.

    S42: submissão App Store + correções (se for iOS também).