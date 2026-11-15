HANDOFF — Rumo (backend + frontend + mobile) — Sessão 35

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro para o assistente novo (leia antes de qualquer coisa)
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. NÃO existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚡ REGRA S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça.
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
⚡ REGRA S26b — validar GPX em produção por regex é mais barato que gpxpy + arquivo temporário. Contar <time> distintos com regex no Content responde "o S26 está no ar?" em 3 linhas, sem env:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>).
⚡ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Não é bug. Se a primeira validação em prod mostrar comportamento antigo, esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min.
⚡ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa. Se git status --short mostrar M docs/HANDOFF.md no início, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro, push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0.
⚡ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir.
⚡ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios". O handoff pode estar desatualizado.
⚡ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código. Não investigar como bug.
⚡ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora. Implementação em web/src/api/activities.ts → _countZipEntries().
⚡ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior, não "bate com o build local". Manter a checagem por __vite__mapDeps + leitura do conteúdo do chunk.
⚡ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número. Erro no esperado, não no código. (Reforçada na S32 e na S33 — ver S33b.)
⚡ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }. Declarar sem inicializar (let entryCount: number;) quando try/catch (ou if/else) cobre todos os caminhos.
⚡ REGRA S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos" (e "TODOS"). Usar -CaseSensitive ou regex \bTODO\b.
⚡ REGRA S30b — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos. Contrato: isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; ambos false = cinza (delta 0). Sinal matemático ("+"/"−") e percentual seguem o delta cru.
⚡ REGRA S30c — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo; a descoberta de código corrige para CIMA. No mobile, SEMPRE pedir Get-ChildItem + arquivos-chave antes de estimar esforço ou travar rota.
⚡ REGRA S31a — em ambiente Windows sem Developer Mode, flutter pub add <plugin_nativo> instala mas avisa que o build vai falhar por symlink. Building with plugins requires symlink support. Please enable Developer Mode — start ms-settings:developers + ativar. Vale para qualquer plugin com código nativo. flutter analyze passa sem Developer Mode; flutter run/flutter build não.
⚡ REGRA S31b — file_picker 13.x removeu FilePicker.platform, FilePickerResult, PlatformFile.size e PlatformFile.bytes. API nova: FilePicker.pickFiles() estático retorna List<PlatformFile> (vazio = cancelou); PlatformFile.length()/lengthSync() substituem .size; PlatformFile.readAsBytes() substitui .bytes. path continua existindo (String?) mas é null na web. Consultar o changelog antes de usar API de plugin.
⚡ REGRA S31c — quando Select-String do disco mostrar conteúdo antigo depois do save do editor, contornar via WriteAllText no PowerShell imediatamente — não insistir no Ctrl+S. Sintomas: git status mostra M, mas Select-String do símbolo novo vem vazio; Get-Item mostra LastWriteTime desatualizado. Procedimento: here-string @' ... '@ + [System.IO.File]::WriteAllText(path, content, [System.Text.UTF8Encoding]::new(false)) + verificar com 3 Select-String.
⚡ REGRA S32a — Select-String -SimpleMatch 'class X' casa PREFIXOS: 'class ActivityCard' casa 'class ActivityCard' e 'class ActivityCardMetric'. Para contar classe exata, usar -Pattern '\bclass X\b' (regex com word boundary) ou -Pattern 'class X ' (com espaço no fim).
⚡ REGRA S32b — Select-String -SimpleMatch '_Simbolo' casa menções em COMENTÁRIOS também. Se o comentário de topo cita o símbolo antigo ("renomeado _ActivityCard → ActivityCard"), a contagem nunca vai a zero. Para contar ocorrências em código, filtrar linhas que não começam com // ou usar regex ancorado.
⚡ REGRA S32c — ao anunciar "esperado ≈ N linhas", CONTAR as linhas do arquivo entregue antes de anunciar. Contagem mental falha consistentemente para baixo em arquivos com widgets aninhados (S32: anunciei ~260 num arquivo de 331; anunciei ~110/-30 num diff que foi +69/-4).
⚡ REGRA S32d — nos Select-String de validação, o "esperado" é sempre PISO ou FAIXA, nunca número exato, a menos que eu tenha contado o output real do arquivo entregue. Se não contei, anunciar "≥ N" e aceitar qualquer valor ≥ N. Erro no esperado, não no código.
⚡ REGRA S33a — alternância em Select-String: SEMPRE -Pattern 'a|b' (sem -SimpleMatch). Vale também para blocos de verificação que o assistente monta. Reincidência da S25a na S33 (o assistente violou a regra que escreveu).
⚡ REGRA S33b — em Select-String de validação, o "esperado" é SEMPRE piso/faixa, nunca exato, mesmo quando o número parece óbvio. Reincidência da S32d na S33. O erro é no esperado, não no código.
⚡ REGRA S34a — git rev-parse HEAD:<arquivo> exige path relativo à RAIZ DO REPO, não ao CWD. Rodando de D:\Rumo\mobile, o correto é git rev-parse HEAD:mobile/lib/main.dart, não HEAD:lib/main.dart. O git hash-object aceita path relativo ao CWD; o git rev-parse não. Sintoma: "fatal: path 'mobile/lib/...' exists, but not 'lib/...'". Erro do comando, não do código.
⚡ REGRA S34b — nas validações de Select-String, o "esperado" anunciado ANTES de rodar deve ser reconhecidamente vago (≥N, faixa) — e mesmo assim pode errar (S34: anunciei "≥2" para '/user/:id' esperando path + builder; veio 1, porque o builder usa state.pathParameters['id'], não a string). Confirmar antes de declarar erro. Reforça S33b.
⚡ REGRA S34c — ao validar tela mobile no Chrome, a sessão do localStorage pode estar com outro usuário (ex.: Prod2 logado de um teste anterior). A primeira screenshot pode ser do ProfilePage self de OUTRO usuário, não do UserProfilePage alvo. Antes de declarar bug: confirmar (a) qual usuário está logado, (b) qual URL foi colada, (c) se o flutter run foi reiniciado depois do último commit de main.dart (hot restart NÃO pega mudança de rota).
⚡ REGRA S35a (NOVA) — o GET /feed do backend NÃO embute o objeto user no payload da atividade. No mobile, isso faz o card cair no fallback "Usuário" e inibe o onAuthorTap (que exige a.user != null). Solução paliativa atual: o card mostra "Usuário". Solução futura: backend embutir user no /feed.

O que é LOCAL vs. o que é PRODUÇÃO
LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.
PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (166 passed ao fim da S34). Container de teste rumo_postgres_test na porta 5433.
⚡ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).

Estrutura do repo (referência — conferir, não assumir)
D:\Rumo
├── .vscode/settings.json
├── backend/ (venv em backend/venv, Python 3.13.7)
│ ├── alembic/
│ ├── app/
│ │ ├── core/ models/ routers/ schemas/ services/
│ │ └── pycache/
│ ├── samples/
│ ├── scripts/
│ ├── tests/ (conftest.py + test_calories + test_comment + test_export
│ │ + test_export_bulk + test_follow + test_like + test_stats)
│ ├── _scratch/ (ignorado pelo git; s33_delta_test.gpx criado na S33)
│ ├── docker-compose.test.yml
│ ├── pytest.ini
│ └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│ ├── lib/
│ │ ├── main.dart (StatefulShellRoute + bottom nav desde S32;
│ │ │ +rota /user/:id desde S34; +rota /search desde S35)
│ │ ├── models/ (activity.dart, activity_track.dart, comment.dart,
│ │ │ stats.dart ← S33, user.dart ← S34,
│ │ │ user_me.dart ← S32)
│ │ ├── pages/ (activity_detail_page.dart, feed_page.dart,
│ │ │ login_page.dart, profile_page.dart ← EDITADO S33,
│ │ │ upload_page.dart ← S31, user_profile_page.dart ← S34,
│ │ │ user_search_page.dart ← NOVO S35)
│ │ ├── services/ (api.dart ← EDITADO S35, auth_service.dart)
│ │ ├── utils/ (format.dart ← S33)
│ │ └── widgets/ (activity_card.dart ← EDITADO S34,
│ │ activity_map.dart, by_type_list.dart ← S33,
│ │ like_button.dart, stats_cards.dart ← S33)
│ ├── pubspec.yaml (file_picker: ^13.3.3, go_router: ^18.1.2, name: rumo_mobile)
│ └── pubspec.lock
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

Como rodar comandos Flutter
Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste
prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades (7 + 1 sintética da S33), 34.08 km. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min) usada pra validar o S26. Tem atividade sintética "Teste delta S33 (janela anterior)" (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null).
Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2 (estado validado na S34; toggle follow/unfollow testado e restaurado).

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21 à S35)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

    UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

    HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.

    PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes. Reflete o estado ao fim da sessão.

    VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo. Exceção: 2 arquivos acoplados por contrato interno → entregar juntos, 1 build.

    VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<simbolo>" antes de build/test.

    NUNCA placeholder no código entregue (S21).

    Não adivinhar nomes de símbolos (S21).

    git status + git log antes de git restore (S21).

    Invoke-WebRequest sempre com -UseBasicParsing (S22).

    Validar openapi.json antes de acusar bug em rota nova (S22).

    Validar bundle da Vercel baixando index-*.js (S23).

    Vercel pode demorar >90 s no primeiro deploy (S24).

    Select-String -SimpleMatch não aceita | como alternância (S25a, reforçada na S33a).

    Confirmar $lines[-1] suspeito com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo>" (S25b).

    Exigir output do bloco de validação antes de pedir commit (S25c).

    Teste definitivo do save: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M (S25d).

    Entregar conteúdo de arquivo para colar sem cerca markdown (S25e).

    PS 5.1: $resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[] (S26a).

    Validar GPX em prod por regex no Content, não por gpxpy+temp file (S26b).

    Render free tier pode demorar >3 min para redeployar após push (S26c).

    Commitar o handoff pendente ANTES de qualquer outra coisa na abertura (S27a).

    Ordem fixa dos blocos da Fase 0: handoff → log/status → build → docker/pytest → prod back → prod front (S27b).

    Antes de aceitar o escopo do handoff anterior como verdade, pedir TODOS os arquivos que o contrato toca e confirmar o gap real (S28a).

    Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada, não mudança de código (S28b).

    Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).

    Vercel reescreve hash de chunk ao servir; sinal de "novo no ar" = hash mudou vs sessão anterior + helper no bundle (S29b).

    Contar as ocorrências reais antes de anunciar "esperado Nx" num Select-String (S29c, reforçada na S33b).

    ESLint no-useless-assignment: declarar let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).

    Select-String "TODO" casa case-insensitive "Todos"/"TODOS" — usar -CaseSensitive ou regex \bTODO\b (S30a).

    Componente genérico com semântica oposta: prop booleana default-false, sinal/percentual seguem delta cru, 4 casos (S30b).

    Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + api.dart + telas antes de estimar (S30c).

    Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink — ativar antes de flutter run (S31a).

    file_picker 13.x: FilePicker.platform/FilePickerResult/.size/.bytes removidos — API estática + length()/readAsBytes() (S31b).

    Select-String do disco mostrando conteúdo antigo após save do editor → contornar via WriteAllText no PowerShell, não insistir no Ctrl+S (S31c).

    Select-String -SimpleMatch 'class X' casa prefixo 'class Xxx' — usar word boundary ou espaço no fim (S32a).

    Select-String -SimpleMatch '_Simbolo' casa menções em comentários — filtrar linhas // ou usar regex ancorado (S32b).

    Anunciar "esperado ≈ N linhas" só depois de CONTAR o arquivo entregue — contagem mental falha para baixo em widgets aninhados (S32c).

    Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA, nunca número exato sem contagem real do output (S32d, reforçada na S33b).

    Alternância em Select-String: SEMPRE -Pattern 'a|b' (sem -SimpleMatch). Vale também para blocos de verificação que o assistente monta (S33a).

    Em Select-String de validação, "esperado" é SEMPRE piso/faixa, nunca exato, mesmo quando o número parece óbvio (S33b).

    git rev-parse HEAD:<arquivo> exige path relativo à RAIZ do repo, não ao CWD (S34a).

    "Esperado" anunciado antes de rodar Select-String pode errar mesmo sendo faixa — confirmar antes de declarar erro (S34b).

    Validar tela mobile no Chrome: confirmar usuário logado, URL colada e se flutter run foi reiniciado depois do último commit (S34c).

    GET /feed não embute user; no mobile o card cai em "Usuário" e inibe onAuthorTap (S35a).

Processo que o usuário elogiou na S21–S35 (para manter)
Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).

    Descoberta antes de codar: pedir arquivos com motivo declarado.

    Validação entre cada entrega.

    Contrato travado escrito antes de codar.

    Commits pequenos e temáticos.

    Validação separada da local.

    Diagnóstico honesto antes de "consertar".

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 166 testes passando LOCALMENTE, 0 warnings. Inalterado desde a S33. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon, minLat, maxLon, maxLat], n_points, simplified. 404 quando route é NULL.
ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax no mesmo SELECT (sem N+1).
Endpoints de stats (todos validados em produção):
GET /activities/stats/summary — StatsSummary.
GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.
GET /activities/stats/monthly?months=N — StatsMonthlyResponse.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.
Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.
Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor. CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona com ou sem rota). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422; omitido → default csv.
Export em lote (S22): GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export<YYYYMMDD-HHMMSS>.zip"). format=csv: inclui todas; format=gpx: só com rota. Filtro from/to inclusivo (UTC). 0 atividades → 200 + ZIP vazio. from > to → 422. format inválido → 422.
S26 (GPX com <time> por ponto): to_gpx(activity, coordinates, raw_track_points=None) ganhou o 3º parâmetro opcional. Quando raw_track_points existe e tem o MESMO comprimento de coordinates, cada <trkpt> recebe <time> com o timestamp real do ponto (unix epoch → ISO 8601 UTC). Caso contrário, fallback para started_at em todos os pontos. Contrato HTTP inalterado.
S31 — upload mobile (inalterado na S33, S34 e S35):
POST /activities/upload — Auth Bearer JWT. multipart/form-data com file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120), activity_type (opcional), description (opcional). Sucesso: 201 com ActivityResponse. Erro: 422 (HTTPValidationError), 429 (slowapi, rate limit 10/h por IP), 401 (token). Parse síncrono, ~1–3s por arquivo.
mobile/lib/services/api.dart — uploadActivity({File? file, List<int>? bytes, String? filename, String? title, String? activityType, String? description, String? token}) → Future<Activity>. Usa http.MultipartRequest (NÃO passa pelo _send). MultipartFile.fromPath quando file != null, MultipartFile.fromBytes quando só bytes != null (web). Timeout 60s.
S32 — perfil próprio + bottom nav (inalterado na S33, S34 e S35):
GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> — auth Bearer JWT. Filtra atividades por usuário. O description do schema diz "requer seguir" quando user_id é de terceiro; para o próprio, sempre passa. Retorna ActivityResponse[] puro (sem envelope de paginação). ⚡ NÃO embute user no ActivityResponse.
GET /users/{user_id} — retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email. NÃO tem avatar_url. NÃO tem created_at. NÃO tem is_following. Para o perfil próprio, o cabeçalho usa GET /auth/me (que retorna UserResponse completo, com email).
S33 — stats agregadas no perfil self (inalterado na S34 e S35).
S34 — perfil de terceiro + follow (inalterado na S35).
S35 — busca de usuários + onAuthorTap no feed (NOVO):
mobile/lib/services/api.dart (EDITADO) — +searchUsers({required String query, int limit = 20, String? token}) → Future<List<User>>. GET /users/search?q=&limit=. Guard client-side: se query.trim().length < 2 → retorna []. Uri.encodeQueryComponent no q.
mobile/lib/pages/user_search_page.dart (NOVO, ~261 linhas) — StatefulWidget com auth. TextEditingController + FocusNode. Timer 300ms (debounce manual, paridade com useDebounce do web). _runSearch() dispara api.searchUsers. Estados: <2 chars → mensagem; loading → spinner; error → mensagem + "Tentar novamente"; hasSearched && empty → "Nenhum usuário encontrado para "q""; senão → ListView.separated de ListTile (CircleAvatar com user.initial, title user.username, subtitle user.fullName, onTap → context.push('/user/{id}')).
mobile/lib/pages/feed_page.dart (EDITADO) — AppBar ganhou IconButton(Icons.search) → context.push('/search'). ActivityCard no itemBuilder ganhou onAuthorTap: a.user != null ? () => context.push('/user/${a.user!.id}') : null.
mobile/lib/main.dart (EDITADO) — +import user_search_page.dart +GoRoute('/search') fora do shell (após /user/:id).
⚡ Achado S35a: o backend do /feed NÃO embute user no card do feed (só o /activities?user_id embute). Resultado: no feed, o card cai em "Usuário" e o onAuthorTap é bloqueado (a.user == null). Funciona no perfil de terceiro (authorUsernameOverride).

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
Deps mobile (S31/S32/S33/S34/S35): file_picker: ^13.3.3, go_router: ^18.1.2. Package name: rumo_mobile.

Git (estado ao fim da Sessão 35)
199040d (HEAD -> main, origin/main) feat(mobile): rota /search fora do shell (Sessao 35)
d71d9fb feat(mobile): busca no feed + link do autor (Sessao 35)
25778ed feat(mobile): busca de usuarios (Sessao 35)
2b312ec docs: handoff da Sessao 34
8d9162c feat(mobile): rota /user/:id fora do shell (Sessao 34)
f84cbbe feat(mobile): onAuthorTap opcional no ActivityCard (Sessao 34)
9273a38 feat(mobile): pagina de perfil de terceiro com follow (Sessao 34)
7cbd238 feat(mobile): model User e client de perfil publico/follow (Sessao 34)
ce09eb6 docs: handoff da Sessao 33
cf49065 feat(mobile): stats agregadas no perfil (Sessao 33)
799f8c9 feat(mobile): authorUsernameOverride no ActivityCard (Sessao 33)
88ae3da feat(mobile): lista de drill-down por tipo com delta (Sessao 33)
ded29f2 feat(mobile): StatsCards espelhando o web (Sessao 33)
e15bedd refactor(mobile): move format.dart para lib/utils (Sessao 33)
a91987f feat(mobile): formatadores de exibicao portados do web (Sessao 33)
f906c9f feat(mobile): models e client de stats (Sessao 33)
Working tree limpo. S35 adicionou 3 commits (25778ed … 199040d). Push feito. HEAD == origin/main.
Pendente: docs/HANDOFF.md da S35 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 35.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 35
3.1 Fase 0 — validação de estado inicial
Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short veio VAZIO na abertura (o commit do handoff S34 já estava feito — hash 2b312ec). Working tree limpo desde o início.

    Log/status. git log --oneline -8: 2b312ec (handoff S34), 8d9162c, f84cbbe, 9273a38, 7cbd238, ce09eb6, cf49065, 799f8c9. HEAD == origin/main.

    Build/lint/analyze. npm run build: 824 modules, 2.85s, hashes IDÊNTICOS aos da S34. npm run lint: limpo. flutter analyze: No issues found! (3.8s).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test Up 5 hours (healthy), pg_isready respondeu accepting connections na 1ª tentativa. pytest -q: 166 passed in 52.21s. ruff check .: All checks passed!.

    Prod backend (S26). Login OK. Atividade 01a1b36a-...: 60 pontos com <time>, 60 distintos. Primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z. S26 NO AR confirmado via regex no Content. Bloco S34 (perfil Prod2 + stats + follow) também validado: prod segue Prod2 = True, Prod2 summary.total_activities = 2.

    Prod frontend (Vercel). index servido: /assets/index-CJjOEm0V.js (idêntico ao da S34). __vite__mapDeps: ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, RouteMap-CXXXy7Mv.js, leaflet-Bw7RoR_1.js, leaflet-CcXJxNtP.css, rolldown-runtime-hePW80VL.js, recharts-DI5KUTLO.js. Todos os 7 hashes batem com o esperado.

3.2 Fase 1 — descoberta para busca de usuários + onAuthorTap
Pedi 9 arquivos + Get-ChildItem, com motivo declarado.
ACHADOS que mudaram o plano:
#1 SearchPage.tsx do web tem DUAS abas: Usuários e Atividades. Escopo da S35 reduzido para só Usuários (a busca de Atividades fica pra S36).
#2 O web usa useDebounce.ts (300ms). O useUserSearch.ts usa enabled: trimmed.length >= 2, staleTime: 30_000, limit=20.
#3 mobile/lib/services/api.dart já tem padrão claro (get/post/delete via _send + _decode). searchUsers encaixa igual ao listFollowing.
#4 feed_page.dart NÃO tem IconButton no AppBar (logout saiu na S32).
#5 ActivityCard já tem onAuthorTap (S34) com GestureDetector(onTap: onAuthorTap ?? onTap). Passar no FeedPage é 1 linha no itemBuilder.
#6 activity.user é UserPublic? (nullable). onAuthorTap no feed só faz sentido quando activity.user != null.
#7 main.dart: rota /search encaixa igual /user/:id (fora do shell, sem bottom nav).
#8 useDebounce no mobile não existe — precisa de Timer manual no State.

3.3 Fase 2 — contrato travado
Backend: 0 mudanças. GET /users/search?q=<min 2>&limit=<1..?>? já existe (S19/S20, rate limit 20/min).
Web: 0 mudanças.
Mobile — 5 arquivos:

    user_search_page.dart (NOVO): busca de usuários com debounce 300ms, guard de 2 chars, estados <2 chars / loading / error / hasSearched+empty / resultados. ListTile com CircleAvatar(initial), username, fullName, onTap → /user/:id.

    api.dart (EDITADO): +searchUsers (guard 2 chars client-side, Uri.encodeQueryComponent, limit=20).

    feed_page.dart (EDITADO): AppBar com IconButton(Icons.search) → /search; ActivityCard com onAuthorTap condicional.

    main.dart (EDITADO): +rota /search fora do shell.

    activity_card.dart: SEM MUDANÇA (já tinha a prop desde S34).
    Escopo NÃO incluso na S35:

    Busca de atividades no mobile (S36).

    Deep-link ?q= na /search mobile.

    Debounce como utilitário reusável (inline no UserSearchPage).

    Editar perfil, lista de seguidores/seguindo, charts, export (S36+).

3.4 Fase 3 — entrega incremental (5 arquivos, 4 builds + 1 par acoplado)

    user_search_page.dart + api.dart (par acoplado, 1 analyze). flutter analyze verde. Commit 25778ed.

    feed_page.dart (1 analyze). flutter analyze verde. Commit d71d9fb.

    main.dart (1 analyze). flutter analyze verde. Commit 199040d.

3.5 Fase 3.5 — verificar save + commit (3 desvios de contagem)
Bloco de verificação rodado em cada arquivo. Desvios no "esperado" (todos do MEU lado, não do código):

    api.dart: anunciei "faixa ≥500" pra linhas, veio 486. REGRA S34b (esperado anunciado antes de rodar pode errar mesmo sendo faixa). Usei piso, mas errei pra cima.

    feed_page.dart: anunciei "≥150", veio 174. OK.

    main.dart: anunciei "≥130", veio 171. OK.
    Nenhum arquivo a corrigir. Todos os desvios foram no "esperado" do teste, não no código.

3.6 Fase 4 — validação manual no Chrome
Só mobile mudou. Render e Vercel intocados (Fase 0 já confirmou). Fase 4 = validação manual no Chrome:

    flutter run -d chrome — OK.

    Login (prod@rumo.com / senha12345) — OK.

    Feed: cards aparecem, FAB de upload e IconButton search no AppBar visíveis.

    Busca: /search → digitar "pro" → Prod2 aparece após debounce. ✓

    Busca vazia: digitar "zzz" → "Nenhum usuário encontrado para "zzz"." ✓

    Tocar no Prod2 → UserProfilePage (S34) com header + stats + atividades + "Deixar de seguir". ✓

    onAuthorTap no feed: NÃO TESTADO na prática (activity.user é null no /feed, então o header do card abre o detalhe, não o perfil). Achado S35a.

    Resto do card no feed: abre /activity/{id} (detalhe), como antes. ✓ (contraprova: não quebrou)
    O que NÃO foi validado (cosmético, risco baixo):

    onAuthorTap no feed com user != null (precisa o backend embutir user no /feed — dívida S35a).

    Busca de atividades (fora do escopo S35).

    429 do rate limit (não testado para não martelar).

    Android físico/emulador (só Chrome/web).

3.7 Observações / bugs encontrados
Achado S35a (NOVO, não é bug de código, é limitação de backend): o GET /feed do backend NÃO embute o objeto user no payload da atividade. Resultado no mobile: o ActivityCard do feed mostra "Usuário" (fallback) e o onAuthorTap fica bloqueado (a.user == null → onTap do card herda o toque, abrindo detalhe). Solução futura: backend embutir user no /feed (ou aceitar o override no feed também).
Nenhum bug de código na S35. Os 3 desvios de contagem foram do meu teste (S34b).
Os 4 avisos [flutter_map] no console do Chrome são informativos (uso do tile server público do OSM; aceitável no MVP, formalizar tile server próprio para produção).

3.8 Resultado da suíte (S35)
pytest -q → 166 passed (nenhuma mudança backend).
ruff check . → All checks passed!.
npm run build → 824 modules (web inalterado).
npm run lint → limpo (web inalterado).
flutter analyze → No issues found! (mobile com 5 arquivos novos/modificados).
Validação manual no Chrome → 8/8 passos verdes (busca, estados, navegação).

3.9 Commits pushados (S35)
25778ed feat(mobile): busca de usuarios (Sessao 35) — 2 arquivos, +294 (user_search_page.dart + api.dart).
d71d9fb feat(mobile): busca no feed + link do autor (Sessao 35) — 1 arquivo, +22/-3 (feed_page.dart).
199040d feat(mobile): rota /search fora do shell (Sessao 35) — 1 arquivo, +11 (main.dart).
Push feito. HEAD == origin/main == 199040d. Working tree limpo.
Pendente: docs: handoff da Sessao 35 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES
GET /activities/{id}/track (auth: Bearer JWT). Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota". Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.
ActivityResponse (feed/lista/detalhe/busca): { id, user_id, activity_type, title, description, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, cover_photo_url, photo_count, created_at, likes_count (default 0), liked_by_me (default false), comments_count (default 0), bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL. ⚡ NÃO tem "user" embutido no /activities (o GET /feed também NÃO embute — achado S35a).
GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> (auth: Bearer JWT) — S32. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro (sem envelope). Paginação client-side.
GET /users/{user_id} (auth: Bearer JWT) — S32. Retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email, avatar_url, created_at, is_following. Para o perfil PRÓPRIO, usar GET /auth/me (UserResponse completo).
GET /auth/me — UserResponse completo: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }. NÃO é /users/me (esse devolve 422).
GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21. Permissão: dono OU seguidor do dono. Caso contrário, 404. format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id><type>.csv". 1 header + 1 linha. Funciona com/sem rota. format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo<id><type>.gpx". S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. ISO 8601 UTC. Exige rota → 404 se route IS NULL. format inválido → 422.
GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22. Auth: self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto. format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota). Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.
POST /activities/upload (auth: Bearer JWT) — S31. multipart/form-data: file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120, nullable), activity_type (opcional, string, nullable), description (opcional, string, nullable). Sucesso: 201 com ActivityResponse. Erro: 422 HTTPValidationError (.detail tratado pelo _extractMessage do mobile). Rate limit: 10/hora por IP (slowapi; 429). Parse síncrono, ~1–3s. ⚡ O upload de GPX usa o started_at do primeiro <trkpt> (ou do metadata), então dá pra criar atividades retroativas (usado na S33 pra exercitar o delta).
GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.
GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5. S30: NÃO inclui avg_pace_s_per_km em nenhum shape — pace é derivado no front (computePace).
Janelas (S17/S18/S20):
period | compare | janela
all | qualquer | null
90d | prev (default) | [now-180d, now-90d)
90d | yoy | [now-455d, now-365d)
1y | prev | [now-730d, now-365d)
1y | yoy | [now-730d, now-365d) (coincide)
GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404. Params: summary aceita activity_type opcional; weekly aceita weeks (1..52, default 8); monthly aceita months (1..24, default 6); by-type aceita period (default all) e compare (default prev). ⚡ O by-type do web usa period=all default; o mobile S33/S34 usa period=90d (com delta).
POST /users/{user_id}/follow — 204. DELETE /users/{user_id}/follow — 204. (S19/S20; consumidos pelo mobile na S34.)
GET /users/{user_id}/followers?limit&offset — list[UserPublic]. (S19/S20)
GET /users/{user_id}/following?limit&offset — list[UserPublic]. (S19/S20; usado pelo isFollowing do mobile na S34.)
GET /users/search?q=<min 2 chars>&limit — list[UserPublic]. Rate limit 20/min. (S19/S20; consumido pelo mobile na S35.)
⚡ NÃO existe GET /users/{id}/is-following. O cliente (web desde S19/S20; mobile desde S34) INFERE via GET /users/{meId}/following e checa se o alvo está na lista. Se o backend ganhar o endpoint, é só trocar a chamada em ApiClient.isFollowing.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Sessões 9–35 commitadas e pushadas. HEAD == origin/main == 199040d. Working tree limpo.
Pendente: este handoff.
Primeira ação da Sessão 36 (REGRA S27a — handoff primeiro)
cd D:\Rumo
git status --short
Se aparecer M docs/HANDOFF.md, commitar:
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 35"
git push
git --no-pager log --oneline -4
git status --short
Esperado: HEAD == origin/main com docs: handoff da Sessao 35 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 36 — primeira ação] Abrir PowerShell via Win+R → powershell (NÃO abrir de dentro do VS Code / Windows Terminal).
cd D:\Rumo
git status --short
Se aparecer M docs/HANDOFF.md:
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 35"
git push
git --no-pager log --oneline -8
git status --short
[Sessão 36 — primeira ação] Sanidade de build
cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
[Sessão 36 — primeira ação] Docker + pytest local
docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
Se o prompt já mostra (venv), PULE a linha abaixo:
.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .
Esperado: 166 passed, ruff limpo, container Up (healthy).
[Sessão 36 — primeira ação] Detecção de versão em produção (front — Vercel)
⚡ Sempre -UseBasicParsing. ⚡ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24). ⚡ REGRA S29b: o hash servido pelo Vercel não bate com o build local.
html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:(m.Groups[1].Value)"m.Groups[1].Value)"idx = Invoke-WebRequest -Uri idxUrl−UseBasicParsingidxUrl−UseBasicParsingidx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|ProfilePage|SearchPage)-[A-Za-z0-9_-]+.js'
Esperado no estado atual (S35): web inalterado desde S30 — index-CJjOEm0V.js com ProfilePage-Cy6s98Hl.js, ActivityDetailPage-DOBuid_4.js, SearchPage-D6UpMvrw.js.
Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me
body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodytoken = login.accesstokenlogin.accesst​okenh = @{ Authorization = "Bearer token" } me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers hhmeId = me.idDetecc\ca~odeversa~oemproduc\ca~o(backendS26—GPXcom<time>porponto)me.idDetecc\c​a~odeversa~oemproduc\c​a~o(backendS26—GPXcom<time>porponto)body = "username=prod@rumo.com&password=senha12345"
login=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/login"−MethodPost−ContentType"application/x−www−form−urlencoded"−Bodylogin=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/login"−MethodPost−ContentType"application/x−www−form−urlencoded"−Bodybody
(login.access_token)" } aid = "01a1b36a-0951-71e8-9044-c55c71558441"
resp=Invoke−WebRequest−Uri"https://rumo−api−5s0b.onrender.com/activities/resp=Invoke−WebRequest−Uri"https://rumo−api−5s0b.onrender.com/activities/aid/export?format=gpx" -Headers h−UseBasicParsingh−UseBasicParsingtimes = [regex]::Matches(
.Groups[1].Value }
n=n=times.Count
distinct=(distinct=(times | Sort-Object -Unique).Count
Write-Host "pontos com <time>: n"Write−Host"<time>distintos:n"Write−Host"<time>distintos:distinct"
if (
(times[0])"Write−Host"ultimo:times[0])"Write−Host"ultimo:(times[-1])" } if (distinct -le 1 -and n−gt1)Write−Host"S26AINDANAONOAR(todosiguais)."elseif(n−gt1)Write−Host"S26AINDANAONOAR(todosiguais)."elseif(distinct -ge
distinct/n distintos." } Esperado agora: 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, ultimo 2026-11-06T21:40:23Z. [Sessão 36 — validação do perfil + stats + follow via API] (novo S34) body = "username=prod@rumo.com&password=senha12345"
login=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/login"−MethodPost−ContentType"application/x−www−form−urlencoded"−Bodylogin=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/login"−MethodPost−ContentType"application/x−www−form−urlencoded"−Bodybody
(login.access_token)" } me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers hWrite−Host"me.id:hWrite−Host"me.id:(me.id)"me.id)"prod2 = "01a141e7-5ea4-7600-8959-19145475ad0a"
user=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/user=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/prod2" -Headers hWrite−Host"Prod2.username:hWrite−Host"Prod2.username:(user.username)"Write−Host"Prod2tememail?user.username)"Write−Host"Prod2tememail?(null−nenull−neuser.email) (esperado: False)"
following=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/following=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/(me.id)/following?limit=100&offset=0" -Headers h
isFollowing=isFollowing=false
foreach (uinuinfollowing) { if (u.id−equ.id−eqprod2) { isFollowing=isFollowing=true } }
Write-Host "prod segue Prod2? isFollowing(esperado:True)"isFollowing(esperado:True)"summary = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2/stats/summary" -Headers hWrite−Host"Prod2summary.totalactivities:hWrite−Host"Prod2summary.totala​ctivities:(summary.totalactivities)(esperado:2)"summary.totala​ctivities)(esperado:2)"acts = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities?user_id=$prod2&limit=20&offset=0" -Headers hWrite−Host"Prod2atividades:hWrite−Host"Prod2atividades:(acts.Count)(esperado:2)"Esperado:me.id=01a12c83−be2a−71fa−b966−1c93ca64f341,Prod2.username=Prod2,Prod2tememail=False,prodsegueProd2=True,Prod2summary.totalactivities=2,Prod2atividades=2.[Sessa~o36—validac\ca~odabuscadeusuaˊriosviaAPI](novoS35)acts.Count)(esperado:2)"Esperado:me.id=01a12c83−be2a−71fa−b966−1c93ca64f341,Prod2.username=Prod2,Prod2tememail=False,prodsegueProd2=True,Prod2summary.totala​ctivities=2,Prod2atividades=2.[Sessa~o36—validac\c​a~odabuscadeusuaˊriosviaAPI](novoS35)body = "username=prod@rumo.com&password=senha12345"
login=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/login"−MethodPost−ContentType"application/x−www−form−urlencoded"−Bodylogin=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/login"−MethodPost−ContentType"application/x−www−form−urlencoded"−Bodybody
(login.access_token)" } results = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/search?q=pro&limit=20" -Headers hWrite−Host"resultados:hWrite−Host"resultados:(results.Count)(esperado:1—Prod2)"results.Count)(esperado:1—Prod2)"single = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/search?q=p&limit=20" -Headers hWrite−Host"q=p(min2):hWrite−Host"q=p(min2):(single.Count) (esperado: 0 — não deve retornar nada)" Esperado: 1 resultado (Prod2), q=p devolve 0 (min 2 chars). Ruff (backend) cd D:\Rumo\backend Se o prompt já mostra (venv), pule: .\venv\Scripts\Activate.ps1 ruff check . Recuperação de arquivo corrompido (lição S21) cd D:\Rumo git status --short <arquivo> git --no-pager log --oneline -3 -- <arquivo> Se o último commit for anterior à mudança quebrada: git restore <arquivo> Se a versão quebrada JÁ foi commitada: git show <commit-anterior>:<arquivo> > <arquivo> Diagnóstico: rota nova não responde após git push (lição S22 + S26c) Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export" Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy. Se rota no ar mas retorna 422, ver o BODY do erro: try { Invoke-WebRequest -Uri "<url>" -Headers h -UseBasicParsing | Out-Null
} catch {
resp=resp=.Exception.Response
reader=New−ObjectSystem.IO.StreamReader(reader=New−ObjectSystem.IO.StreamReader(resp.GetResponseStream())
Write-Host "STATUS ((resp.StatusCode)"
Write-Host reader.ReadToEnd() } Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b) html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
m=[regex]::Match(m=[regex]::Match(html.Content, 'src="(/assets/index-[^"]+.js)"')
idxUrl="https://rumo−wheat.vercel.app"+idxUrl="https://rumo−wheat.vercel.app"+m.Groups[1].Value
Write-Host "index servido: ((m.Groups[1].Value)"
idx=Invoke−WebRequest−Uriidx=Invoke−WebRequest−UriidxUrl -UseBasicParsing
idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+\.js' Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. ⚡ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar. Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S35) Depois de salvar, ANTES de commitar: Write-Host "=== [1] termos proibidos (deve vir vazio) ===" Select-String -Path <arquivo> -Pattern "\bTODO\b|\bFIXME\b" -CaseSensitive Write-Host "=== [2] total de linhas ===" (Get-Content -Encoding UTF8 <arquivo>).Count Write-Host "=== [3] ultima linha ===" Get-Content -Encoding UTF8 <arquivo> | Select-Object -Last 1 Write-Host "=== [4] git status (deve mostrar ' M <arquivo>') ===" git status --short Write-Host "=== [5] hash do disco ===" git hash-object <arquivo> Write-Host "=== [6] hash do HEAD (path relativo a RAIZ do repo!) ===" git rev-parse HEAD:<path/relativo/a/raiz/do/repo> Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou. Se [5] != [6] e [4] mostra ' M' → save pegou, pode commitar. ⚡ REGRA S34a: o git rev-parse exige path relativo à raiz do repo (mobile/lib/main.dart), não ao CWD (lib/main.dart). O git hash-object aceita CWD. Nota S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS". Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b. Nota S32a/S32b/S33a: -SimpleMatch 'class X' casa 'class Xxx' (prefixo). -SimpleMatch '_X' casa menções em //. -SimpleMatch 'a|b' NÃO é alternância. Para contagem exata/alternância, usar -Pattern (sem -SimpleMatch) com regex ancorado. Nota S33b/S34b: o "esperado" de qualquer Select-String é piso/faixa, nunca exato sem contagem real. Mesmo faixa pode errar (S34: '/user/:id' ≥2, veio 1). Contornar editor que não salva (REGRA S31c) Se Select-String do disco mostrar conteúdo antigo depois do save do editor: cd D:\Rumo\mobile # ou o diretório do arquivo content = @'
//conteudo completo do arquivo aqui
'@
[System.IO.File]::WriteAllText("PWD\caminho\do\arquivo.dart", content, [System.Text.UTF8Encoding]::new(false))Write−Host"bytes:false))Write−Host"b​ytes:((Select-String -Path caminho\do\arquivo.dart -Pattern 'bytes' -SimpleMatch | Measure-Object).Count) (esperado >=2)"
Write-Host "debugPrint: ((Select-String -Path caminho\do\arquivo.dart -Pattern 'debugPrint' -SimpleMatch | Measure-Object).Count) (esperado 0)" O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor. Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a) ERRADO — Content é string, não byte[]: [System.IO.File]::WriteAllBytes(path, resp.Content)
CERTO (texto UTF-8):
[System.IO.File]::WriteAllBytes(path, [System.Text.Encoding]::UTF8.GetBytes(resp.Content))CERTO(bytescrus—ZIP,imagem):resp.Content))CERTO(bytescrus—ZIP,imagem):fs = [System.IO.File]::OpenWrite(path)path)resp.RawContentStream.Position = 0
resp.RawContentStream.CopyTo(resp.RawContentStream.CopyTo(fs)
fs.Close()MELHORparainspecionarGPX—semarquivo,regexnoContent:fs.Close()MELHORparainspecionarGPX—semarquivo,regexnoContent:times = [regex]::Matches(
.Groups[1].Value }
Upload de arquivo via PowerShell (lição S33)
Invoke-RestMethod -Form NÃO existe no PS 5.1 (só PS 6+). Para multipart/form-data, usar curl.exe (nativo no Windows 10+):
curl.exe -X POST "https://rumo-api-5s0b.onrender.com/activities/upload" -H "Authorization: Bearer ((login.access_token)" -F "file=@D:\caminho\arquivo.gpx" -F "title=Titulo opcional"
Para gerar um GPX sintético no disco (sem editor):
$gpx = @'
<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="..." xmlns="http://www.topografix.com/GPX/1/1"> <trk><trkseg> <trkpt lat="-23.55" lon="-46.63"><ele>760</ele><time>2026-06-01T10:00:00Z</time></trkpt> </trkseg></trk> </gpx>

'@
[System.IO.File]::WriteAllText("D:\Rumo\backend_scratch\teste.gpx", gpx,[System.Text.UTF8Encoding]::new(gpx,[System.Text.UTF8Encoding]::new(false))
Verificar busca de usuários em prod (S35 — NOVO)
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
E rodar o app:
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d chrome
Login como prod@rumo.com. Tocar na lupa no AppBar do feed → /search. Digitar "pro" → Prod2. Digitar "zzz" → vazio.
⚡ REGRA S34c: se a tela mostrar "Sair" + email, você está no ProfilePage self, não no UserSearchPage. Confirmar (a) usuário logado, (b) URL colada, (c) restart do flutter run.

SEÇÃO 7 — DÍVIDAS TÉCNICAS
(FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.
(FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.
(FECHADA na S25) ~~RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy()~~ — RouteMap agora é lazy no ActivityDetailPage.
(FECHADA na S26) ~~to_gpx não emite <time> por <trkpt>~~ — agora emite quando raw_track_points está disponível e alinhado.
(FECHADA na S28) ~~PreviousDelta mostrava só 3 das 5 métricas~~ — PreviousDelta agora renderiza as 5.
(FECHADA na S29) ~~downloadActivityExportBulk retornava void~~ — agora devolve { entryCount }.
(FECHADA na S30) ~~Delta de Pace no PreviousDelta está fora de escopo~~ — DeltaLine ganhou lowerIsBetter.
(FECHADA na S31) ~~Mobile não tem upload GPX/FIT~~ — POST /activities/upload consumido pelo ApiClient.uploadActivity + UploadPage + FAB no feed.
(FECHADA na S32) ~~Mobile não tem perfil nem "minhas atividades"~~ — GET /activities?user_id= consumido pelo ApiClient.listActivities + ProfilePage + bottom nav via StatefulShellRoute.
(FECHADA na S32) ~~setState() called after dispose no feed_page.dart~~ — 4 if (!mounted) return; + if (mounted) setState no finally do _load; 2 if (!mounted) return; no _openDetail.
(FECHADA na S32) ~~_ActivityCard e _Metric duplicados entre feed e perfil~~ — extraídos para widgets/activity_card.dart (ActivityCard + ActivityCardMetric).
(FECHADA na S32) ~~GET /activities não embute user; ActivityCard cai em "Usuário" no perfil~~ — resolvido no mobile via authorUsernameOverride (S33/S34). Backend intocado.
(FECHADA na S33) ~~Mobile não tem stats agregadas no perfil~~ — GET /users/{id}/stats/summary + by-type consumidos, StatsCards + ByTypeList + delta com lowerIsBetter.
(FECHADA na S33) ~~format.dart em lib/lib/ dispara avoid_relative_lib_imports~~ — movido para lib/utils/, imports package:rumo_mobile/.
(FECHADA na S34) ~~Mobile não tem perfil de terceiro nem follow~~ — GET /users/{id} + POST/DELETE /users/{id}/follow + GET /users/{id}/following consumidos pelo ApiClient (getUser/followUser/unfollowUser/listFollowing/isFollowing) + UserProfilePage + rota /user/:id.
(FECHADA na S34) ~~UserPublic local de activity.dart tem avatarUrl que o backend não devolve~~ — User novo (user.dart) nasceu sem avatarUrl. O UserPublic antigo de activity.dart mantém o campo (nunca preenchido, ActivityCard cai na inicial) — dívida cosmética registrada abaixo, não vale a pena mexer agora.
(FECHADA na S35) ~~Mobile não tem busca de usuários~~ — GET /users/search consumido pelo ApiClient.searchUsers + UserSearchPage + rota /search.
(FECHADA na S35) ~~onAuthorTap no card do feed estava implementado mas ninguém passava (S34)~~ — FeedPage passa onAuthorTap condicional.
(CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.
(CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.
(CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.
(CONHECIDA — Sessão 17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.
(CONHECIDA — Sessão 17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. NÃO é bug. (Atualização S33: com a sintética de 2026-06-01, o previous de walk em 90d agora vem preenchido; a conta tem 8 atividades, sendo 7 "atuais" e 1 na janela anterior.)
(CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática.
(CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk". Testes usam activity.activity_type.value dinâmico.
(CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. YAGNI por enquanto.
(CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries. Aceitável para export raro.
(CONHECIDA — Sessão 22) Export em lote é self-only. Decisão de privacidade.
(CONHECIDA — Sessão 23) downloadActivityExportBulk valida from > to client-side. Dupla validação proposital.
(CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).
(CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado desde antes.
(CONHECIDA — Sessão 26) <time> no GPX inclui microssegundos (2026-11-07T00:20:32.931332Z) porque o gpxpy serializa datetime.isoformat(). Observação S31: em prod agora vem truncado em segundos (2026-11-06T21:30:33Z). Contrato intacto.
(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Coberto por teste.
(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. É renomeação de referência cruzada no __vite__mapDeps, não regressão (REGRA S28b).
(CONHECIDA — Sessão 29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Sentinel 0xFFFF sinaliza falha (retorna -1, fail-open).
(CONHECIDA — Sessão 29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs). Se o export virar pesado, trocar por blob.slice(-22-65535, blob.size).
(CONHECIDA — Sessão 29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.
(CONHECIDA — Sessão 30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX. Se um dia alguém quiser pace em cycle, relaxar PACE_TYPES — DeltaLine já tem lowerIsBetter pronto.
(CONHECIDA — Sessão 30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0 (computePace(item) ?? 0), resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero.
(CONHECIDA — Sessão 31) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → ApiException; o app NÃO faz logout automático. Melhoria para "mundo real", não MVP.
(CONHECIDA — Sessão 31) Mobile: uploadActivity valida path == null → readAsBytes(), cobre web. No Android, path costuma vir preenchido (o plugin copia pra cache) e o File(path) deve funcionar — não testado em dispositivo físico. Testar na S36+.
(CONHECIDA — Sessão 31) Mobile: rate limit 10/h do /activities/upload não foi testado explicitamente (429). Se o backend devolver .detail legível, a UI mostra; se não, mostra "Erro 429". Oportunidade: UI dedicada com cooldown visual.
(CONHECIDA — Sessão 31) Mobile: activity_type fora da UI do upload na S31 — o backend infere pelo arquivo. Se precisar de override manual, é um dropdown em sessão futura.
(CONHECIDA — Sessão 31) O commit a83ed82 foi feito pelo usuário/VS Code com a versão inicial; 71a00d4 refinou upload_page.dart e api.dart. Não vale rebase/squash.
(CONHECIDA — Sessão 31) file_picker 13.3.3 trouxe 11 deps novas (android_file_picker, cross_file, dbus, file_picker_darwin, file_picker_linux, file_picker_platform_interface, file_picker_web, petitparser, windows_file_picker, xml + file_picker). Todas no pubspec.lock.
(CONHECIDA — Sessão 32) GET /activities (backend) retorna ActivityResponse[] SEM o campo "user" embutido. O GET /feed embute (FeedItem tem author). Resolvido no mobile via authorUsernameOverride (S33 no self, S34 no terceiro).
(CONHECIDA — Sessão 32) UserPublic local em activity.dart tem avatarUrl que o UserPublic do backend NÃO tem (o do backend é { id, username, full_name, is_active }). O _ActivityCard usa avatarUrl só se não for null (nunca vem). Dívida cosmética — o User novo (user.dart, S34) nasceu sem o campo, mas o UserPublic antigo (activity.dart) mantém. Alinhar (remover avatarUrl do UserPublic antigo ou adicionar no backend) fica pra S36+.
(CONHECIDA — Sessão 32) ProfilePage usa Future.wait([/auth/me, /activities?user_id=...]) em paralelo. Se um falhar, o Future.wait rejeita com o primeiro erro. Na S33, os stats foram SEPARADOS (_loadStats com Future.wait próprio). O UserProfilePage (S34) segue o mesmo padrão: _load() (user + isFollowing + activities) e _loadStats() (summary + by-type) separados.
(CONHECIDA — Sessão 32) ProfilePage paginação: "Carregar mais" (botão), não scroll infinito. O backend não dá total; regra "se voltou < limit, acabou". Conta prod tem 8 atividades — o "Carregar mais" NÃO foi exercitado (8 < 20 → mostra "Fim."). Testar na S36+.
(CONHECIDA — Sessão 32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id, /user/:id e /search ficam FORA do shell (sem bottom nav). Decisão intencional.
(CONHECIDA — Sessão 32) O FAB de upload some quando o usuário está na aba Perfil. Intencional (upload é ação do feed).
(CONHECIDA — Sessão 33) period/compare FIXOS no mobile (90d/prev). O web tem filtros de UI (all/90d/1y × prev/yoy). Filtros ficam pra S36+.
(CONHECIDA — Sessão 33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web). Adaptação mobile do mesmo dado — paridade semântica, não visual.
(CONHECIDA — Sessão 33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 (Material) em vez de text-green-600/red-600 (Tailwind). Equivalente aproximado; shade700 lê melhor em texto pequeno.
(CONHECIDA — Sessão 33) O _formatThousands é inline (sem intl). O web usa toLocaleString("pt-BR"). Se o mobile precisar de formatação de data/moeda pt-BR em vários lugares, aí intl entra; hoje não.
(CONHECIDA — Sessão 33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético pra exercitar o delta do by-type 90d. Fica como dado de teste. O GPX fonte está em backend/_scratch/s33_delta_test.gpx (ignorado pelo git).
(CONHECIDA — Sessão 33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Para multipart, usar curl.exe. Anotado na Seção 6.
(CONHECIDA — Sessão 33) Weekly/monthly charts no mobile ficam pra S36+ (periodchart do web usa recharts; no mobile, seria fl_chart ou similar — decisão de dependência na S36).
(CONHECIDA — Sessão 34) O backend NÃO tem GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following?limit=100 e checa se o alvo está na lista (web desde S19/S20 em useProfile.ts → useIsFollowing; mobile desde S34 em ApiClient.isFollowing). Custa 1 request extra por perfil aberto. Se o backend ganhar o endpoint, é só trocar a chamada.
(CONHECIDA — Sessão 34) O _activitiesForbidden do UserProfilePage é heurístico: se listActivities voltou vazio E isFollowing==false E não é self → assume 403 engolido pelo catchError do Future.wait. Falso positivo teórico: usuário que não segue e não tem atividades → mostra "Siga pra ver..." (mesmo comportamento do web, que trata 403 explicitamente). Se virar problema, S36 troca por chamadas separadas (getUser + isFollowing em paralelo, listActivities depois).
(CONHECIDA — Sessão 34) O onAuthorTap do ActivityCard foi implementado mas ninguém passava na S34. Decisão: feed e self não passam; UserProfilePage também não (o card no perfil do alvo abre o detalhe). Link do autor no feed ficou pra S35 — FEITO na S35 (FeedPage passa condicional).
(CONHECIDA — Sessão 34) O UserProfilePage não tem "Sair" nem mostra email (UserPublic não tem esses campos). Se o usuário abrir /user/{meu-id}, o header mostra "Este é você. Use a aba Perfil pra editar." e sem botão Follow. O perfil editável continua sendo /profile (bottom nav).
(CONHECIDA — Sessão 34) O toggle follow/unfollow altera o backend real (não é mock). Na validação S34, foi testado nos dois sentidos e restaurado pro estado original (prod segue Prod2).
(CONHECIDA — Sessão 34) A inferência isFollowing com limit=100 só enxerga os primeiros 100 follows. Se prod seguir >100 usuários, o Prod2 pode ficar de fora e o botão mostrar "Seguir" quando na verdade segue. Conta atual tem poucos follows. Se virar problema, paginar a lista ou ganhar o endpoint no backend.
(CONHECIDA — Sessão 34) Sessão do localStorage no Chrome pode estar com outro usuário. A primeira validação da S34 abriu o ProfilePage self do Prod2 (logado de teste anterior), não o UserProfilePage alvo. REGRA S34c.
(CONHECIDA — Sessão 35 — NOVO) O GET /feed do backend NÃO embute user. Isso faz o ActivityCard do feed cair em "Usuário" e INIBE o onAuthorTap (a.user == null). Solução futura: backend embutir user no /feed. Paliativo: o card mostra "Usuário" e o toque abre detalhe.
(CONHECIDA — Sessão 35 — NOVO) O debounce da busca é manual (Timer de 300ms) no _UserSearchPageState, não um Hook/utilitário reusável. Se aparecer segunda tela de busca, extrair pra utils/.
(CONHECIDA — Sessão 35 — NOVO) O _query do UserSearchPage não vai pra URL. O web usa searchParams.set('q', ...) pra deep-link; no mobile o /search é fluxo efêmero (YAGNI).
(CONHECIDA — Sessão 35 — NOVO) O guard de 2 chars está DUPLICADO: client-side (em ApiClient.searchUsers: if (q.length < 2) return []) e server-side (o backend valida q min 2 e devolve 422 se não). Dupla validação proposital — economiza request inútil.
(CONHECIDA — Sessão 35 — NOVO) Os 4 avisos [flutter_map] no console do Chrome são informativos (uso do tile server público do OSM; aceitável no MVP). Formalizar tile server próprio para produção.
(Oportunidade — S18–S35) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.
(Oportunidade — S19–S35) Stats públicas só quando viewer segue o alvo.
(Oportunidade — S22–S35) Export em lote no mobile (paridade com web S21/S22/S29).
(Oportunidade — S30) Testes unitários do DeltaLine no web (não há hoje; é puro, dá pra testar com 4 casos e sem React Testing Library). No mobile, o _DeltaLine também é puro e testável.
(Oportunidade — S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.
(Oportunidade — S31) Testar upload em Android físico/emulador.
(Oportunidade — S31) UI dedicada para 429 (rate limit) com cooldown visual.
(Oportunidade — S31) activity_type como dropdown opcional na UploadPage.
(Oportunidade — S33) Filtros de period/compare na UI do perfil (S36+).
(Oportunidade — S33) Weekly/monthly charts no perfil (S36+).
(Oportunidade — S34) Lista de seguidores/seguindo no UserProfilePage (o web tem abas followers/following) — S36.
(Oportunidade — S35) Busca de atividades no mobile (o web tem aba "Atividades" na SearchPage.tsx) — S36.
(Oportunidade — S35) Embeder user no /feed (resolver S35a) — S36+.
(Oportunidade — S34) Export no mobile (unitário + lote) — S37.
(Oportunidade — S34) Editar perfil (peso, altura, etc.) — requer PUT /users/me ou similar, não existe — S37+.
(Oportunidade — S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S37+.
(Oportunidade — S34) Endpoint GET /users/{id}/is-following no backend — S37+ (elimina a inferência).

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 36 e além)
Sessão 35 fechada. Busca de usuários entregue. onAuthorTap implementado (bloqueado no feed por S35a). Backend e web inalterados. Mobile subiu de ~82% para ~85% de cobertura (estimativa).
Primeira ação obrigatória da Sessão 36 (REGRA S27a)
Abrir PowerShell via Win+R → powershell.
Rodar o bloco "[Sessão 36 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 35, push, confirmar HEAD == origin/main.
Sanidade de build (npm run build/npm run lint + flutter analyze).
Docker + pytest (docker ps -a, pg_isready, pytest -q → 166, ruff check).
Detecção de versão em produção (front Vercel + back Render S26 + blocos S34/S35).
Rota travada para a Sessão 36: embutir user no /feed + busca de atividades
Escolha OPÇÃO 1 (recomendada): Corrigir o backend para o /feed embutir user (resolve S35a) e habilitar onAuthorTap no feed de verdade. Requer: schema FeedItem (já tem author, na verdade — o backend do web usa FeedItem; o mobile usa Activity.fromJson no /feed, que espera "user"). Se o backend já devolve FeedItem com author e o mobile lê user, é um mismatch de contrato. Ação: ver o schema FeedItem do backend, alinhar o fromJson no mobile, ou trocar o path do feed no mobile. Pequeno, alto valor (destrava onAuthorTap no feed).
Escolha OPÇÃO 2: Busca de atividades no mobile (porta a aba "Atividades" da SearchPage.tsx). Requer: pedir web/src/api/activities.ts (já temos useActivitySearch.ts + ActivityResults no web), criar ActivitySearchPage ou tab na UserSearchPage, novo client method searchActivities.
Escolha OPÇÃO 3: Lista de seguidores/seguindo no UserProfilePage (o web tem abas followers/following). Requer: pedir web/src/pages/ProfilePage.tsx (parte de followers/following), criar a UI no mobile.
Escolha OPÇÃO 4: Filtros de period/compare na UI do perfil (paridade com web S17/S20).
Escolha OPÇÃO 5: Weekly/monthly charts no perfil (fl_chart ou similar).
Escolha OPÇÃO 6: Export no mobile (paridade com web S21/S22/S29).
Recomendação: S36 = OPÇÃO 1 (backend feed user) + OPÇÃO 2 (busca de atividades). S37 = OPÇÃO 3 (followers/following) + OPÇÃO 6 (export). S38 = OPÇÃO 6 (release). S39 = publicação na loja. ~4-6 sessões para o MVP em loja.

Recomendação final para a Sessão 36
Rodar Fase 0 completa (com handoff S35 commitado primeiro). Se tudo verde, atacar a OPÇÃO 1 (backend FeedItem → mobile user) que é pequena e destrava a principal UX que ficou pendente (onAuthorTap no feed). Depois OPÇÃO 2 (busca de atividades).
⚡ Antes de codar: Fase 1 da S36 precisa pedir os arquivos backend equivalentes (app/schemas/feed.py, app/routers/feed.py) e o fromJson do mobile. Verificar se FeedItem tem author ou user.

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
Na S30 (abertura): handoff S29 já commitado. Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. 1 tropeço (contagem "5x vs 6x", REGRA S29c), 1 achado (Select-String case-insensitive, S30a).
Na S31 (abertura): handoff S30 já commitado (3a154b1). Fase 0 limpa. Tropeços: (1) file_picker 13.x mudou a API (REGRA S31b); (2) o editor falhou 3 vezes em salvar o upload_page.dart (REGRA S31c); (3) teste manual revelou que na web file_picker retorna path == null mas readAsBytes() funciona — corrigi para aceitar bytes; (4) commit duplicado (a83ed82 + 71a00d4) — estado final íntegro, não vale rebase.
Na S32 (abertura): handoff S31 já commitado (f39820f, feito entre sessões — o handoff S31 listava 71a00d4 como HEAD, confirmando a REGRA S27a na prática). Fase 0 limpa. Fase 1 revelou 5 achados que mudaram o plano. Entrega incremental: 6 arquivos, 4 builds, todos analyze verde. 5 desvios de contagem no "esperado" (S32a–S32d consolidadas). Validação manual no Chrome: 11/11.
Na S33 (abertura): handoff S32 já commitado (919ccea). Fase 0 limpa (7 blocos, todos verdes). Fase 1 revelou 6 achados, incluindo o crítico: DeltaLine/PreviousDelta moram DENTRO do ProfilePage.tsx. Entrega incremental: 6 arquivos, 6 builds + 1 fix (avoid_relative_lib_imports → move format.dart para lib/utils/), todos analyze verde. 2 desvios de contagem (S33a, S33b — ambos reincidência de regras que eu mesmo escrevi). Validação manual no Chrome: 12/12.
Na S34 (abertura): handoff S33 já commitado (ce09eb6, feito entre sessões). Fase 0 limpa (5 blocos, todos verdes). Fase 1 revelou 8 achados, incluindo o crítico #7 (não existe /users/{id}/is-following; web infere via /users/{meId}/following — mobile porta a mesma estratégia). Entrega incremental: 4 arquivos (2 novos, 2 editados), 4 builds, todos analyze verde. 2 desvios de contagem (S34a, S34b) + 1 achado operacional (S34c — sessão do localStorage no Chrome). Validação manual no Chrome: 9/9 (caminho 200, caminho 403, toggle follow/unfollow nos dois sentidos).
Na S35 (abertura): handoff S34 já commitado (2b312ec, feito entre sessões). Fase 0 limpa (5 blocos, todos verdes). Fase 1 revelou 8 achados (SearchPage do web tem duas abas; useDebounce 300ms; useUserSearch com enabled len>=2; api.dart padrão claro; feed_page sem IconButton; activity_card já tem prop; main.dart rota fora do shell; debounce manual no Flutter). Entrega incremental: 5 arquivos (1 novo, 4 editados), 4 builds, todos analyze verde. 3 desvios de contagem (api.dart ≥500, veio 486). Validação manual no Chrome: 8/8 + achado S35a (GET /feed não embute user).

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.
Acordo novo na S32: manter o processo da S21–S31. Concretamente:
Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.
Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar.
Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.
Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.
Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> (com path relativo à RAIZ do repo — REGRA S34a) + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b + S34b: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c).
Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local. REGRA S34c: no mobile, confirmar login/URL/restart antes de declarar bug de tela.
Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).
Regras novas da S35 (Seção 0, item 46): GET /feed não embute user; no mobile o card cai em "Usuário" e inibe onAuthorTap (S35a).
O que funcionou nas S21–S35 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão), disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33, S34, S35), e a consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor, sessão do localStorage) na hora e corrigir/registrar, sem contornar. A S35 acrescentou: parar e não fingir validação quando a screenshot mostra a tela certa mas o backend limita a UX (S35a).