HANDOFF — Rumo (backend + frontend + mobile) — Sessão 32

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚠️ REGRA S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça.
⚠️ REGRA S21 — não adivinhar nomes de símbolos do projeto. Pedir o model/enum/schema antes de referenciar.
⚠️ REGRA S21 — git status antes de qualquer git restore/git checkout. git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>.
⚠️ REGRA S22 — Invoke-WebRequest com -UseBasicParsing. Elimina o prompt de segurança do PS 5.1.
⚠️ REGRA S22 — validar deploy do Render antes de acusar bug no código. Depois de push, checar openapi.json para a rota nova antes de acusar 422/404.
⚠️ REGRA S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele. Nunca procurar "ProfilePage-" direto no HTML.
⚠️ REGRA S24 — Vercel às vezes demora >90 s para o primeiro deploy após push. Se o hash antigo aparecer após 90 s, rodar o teste de novo. Não presumir bug.
⚠️ REGRA S25a — Select-String -SimpleMatch NÃO aceita | como alternância. Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo.
⚠️ REGRA S25b — quando lines[−1]forsuspeito,confirmarcomGet−Content∣Select−Object−LastN+Select−String−Pattern"<termouˊnico>"antesdeconcluir.Na~odar"OK"nem"corrompido"semevide^ncia.⚠®REGRAS25c—antesdepedirgitadd/gitcommitdeumarquivoqueousuaˊrioacaboudesalvar,EXIGIRooutputdoblocodevalidac\ca~oeESPERAR.⚠®REGRAS25d—otestedefinitivode"osavepegou"eˊgithash−object<arquivo>≠gitrev−parseHEAD:<arquivo>+gitstatus−−shortmostrarM<arquivo>.Segitstatus−−shortviervaziodepoisdesalvar,odiscoeˊigualaocommitado.Osavena~opegou.⚠®REGRAS25e—aoentregaroconteuˊdodeumarquivoparacolarnoeditor,entregarSEMcercamarkdownenvolvendo.Entregaroarquivointeirocomoouˊnicotextodaresposta,seminstruc\co~esantes/depois.⚠®REGRAS26a—noPowerShell5.1,Invoke−WebRequest−UseBasicParsingdevolveresp.ContentcomoSTRING,na~ocomobyte[].[System.IO.File]::WriteAllBytes(path,resp.Content)falha.ParatextoUTF−8:[System.Text.Encoding]::UTF8.GetBytes(resp.Content).Parabytescrus(ZIP,imagem):resp.RawContentStream.CopyTo(fileStream).ParainspecionarGPX/XML:regexdiretonoContent.⚠®REGRAS26b—validarGPXemproduc\ca~oporregexeˊmaisbaratoquegpxpy+arquivotemporaˊrio.Contar<time>distintoscomregexnoContentresponde"oS26estaˊnoar?"em3linhas,semlines[−1]forsuspeito,confirmarcomGet−Content∣Select−Object−LastN+Select−String−Pattern"<termouˊnico>"antesdeconcluir.Na~odar"OK"nem"corrompido"semevide^ncia.⚠R◯REGRAS25c—antesdepedirgitadd/gitcommitdeumarquivoqueousuaˊrioacaboudesalvar,EXIGIRooutputdoblocodevalidac\c​a~oeESPERAR.⚠R◯REGRAS25d—otestedefinitivode"osavepegou"eˊgithash−object<arquivo>=gitrev−parseHEAD:<arquivo>+gitstatus−−shortmostrarM<arquivo>.Segitstatus−−shortviervaziodepoisdesalvar,odiscoeˊigualaocommitado.Osavena~opegou.⚠R◯REGRAS25e—aoentregaroconteuˊdodeumarquivoparacolarnoeditor,entregarSEMcercamarkdownenvolvendo.Entregaroarquivointeirocomoouˊnicotextodaresposta,seminstruc\c​o~esantes/depois.⚠R◯REGRAS26a—noPowerShell5.1,Invoke−WebRequest−UseBasicParsingdevolveresp.ContentcomoSTRING,na~ocomobyte[].[System.IO.File]::WriteAllBytes(path,resp.Content)falha.ParatextoUTF−8:[System.Text.Encoding]::UTF8.GetBytes(resp.Content).Parabytescrus(ZIP,imagem):resp.RawContentStream.CopyTo(fileStream).ParainspecionarGPX/XML:regexdiretonoContent.⚠R◯REGRAS26b—validarGPXemproduc\c​a~oporregexeˊmaisbaratoquegpxpy+arquivotemporaˊrio.Contar<time>distintoscomregexnoContentresponde"oS26estaˊnoar?"em3linhas,semenv:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>).
⚠️ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Não é bug. Se a primeira validação em prod mostrar comportamento antigo, esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min.
⚠️ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa. Se git status --short mostrar M docs/HANDOFF.md no início, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro, push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0.
⚠️ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir.
⚠️ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios". O handoff pode estar desatualizado.
⚠️ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código. Não investigar como bug.
⚠️ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora. Implementação em web/src/api/activities.ts → _countZipEntries().
⚠️ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior, não "bate com o build local". Manter a checagem por __vite__mapDeps + leitura do conteúdo do chunk.
⚠️ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número. Erro no esperado, não no código. (Reforçada na S32 — reincidiu 5 vezes; ver S32d.)
⚠️ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }. Declarar sem inicializar (let entryCount: number;) quando try/catch (ou if/else) cobre todos os caminhos.
⚠️ REGRA S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos" (e "TODOS"). Usar -CaseSensitive ou regex \bTODO\b.
⚠️ REGRA S30b — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos. Contrato: isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; ambos false = cinza (delta 0). Sinal matemático ("+"/"−") e percentual seguem o delta cru.
⚠️ REGRA S30c — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo; a descoberta de código corrige para CIMA. No mobile, SEMPRE pedir Get-ChildItem + arquivos-chave antes de estimar esforço ou travar rota.
⚠️ REGRA S31a — em ambiente Windows sem Developer Mode, flutter pub add <plugin_nativo> instala mas avisa que o build vai falhar por symlink. Building with plugins requires symlink support. Please enable Developer Mode — start ms-settings:developers + ativar. Vale para qualquer plugin com código nativo. flutter analyze passa sem Developer Mode; flutter run/flutter build não.
⚠️ REGRA S31b — file_picker 13.x removeu FilePicker.platform, FilePickerResult, PlatformFile.size e PlatformFile.bytes. API nova: FilePicker.pickFiles() estático retorna List<PlatformFile> (vazio = cancelou); PlatformFile.length()/lengthSync() substituem .size; PlatformFile.readAsBytes() substitui .bytes. path continua existindo (String?) mas é null na web. Consultar o changelog antes de usar API de plugin.
⚠️ REGRA S31c — quando Select-String do disco mostrar conteúdo antigo depois do save do editor, contornar via WriteAllText no PowerShell imediatamente — não insistir no Ctrl+S. Sintomas: git status mostra M, mas Select-String do símbolo novo vem vazio; Get-Item mostra LastWriteTime desatualizado. Procedimento: here-string @' ... '@ + [System.IO.File]::WriteAllText(path, content,[System.Text.UTF8Encoding]::new(content,[System.Text.UTF8Encoding]::new(false)) + verificar com 3 Select-String.
⚠️ REGRA S32a (NOVA) — Select-String -SimpleMatch 'class X' casa PREFIXOS: 'class ActivityCard' casa 'class ActivityCard' e 'class ActivityCardMetric'. Para contar classe exata, usar -Pattern '\bclass X\b' (regex com word boundary) ou -Pattern 'class X ' (com espaço no fim).
⚠️ REGRA S32b (NOVA) — Select-String -SimpleMatch '_Simbolo' casa menções em COMENTÁRIOS também. Se o comentário de topo cita o símbolo antigo ("renomeado _ActivityCard → ActivityCard"), a contagem nunca vai a zero. Para contar ocorrências em código, filtrar linhas que não começam com // ou usar regex ancorado.
⚠️ REGRA S32c (NOVA) — ao anunciar "esperado ≈ N linhas", CONTAR as linhas do arquivo entregue antes de anunciar. Contagem mental falha consistentemente para baixo em arquivos com widgets aninhados (S32: anunciei ~260 num arquivo de 331; anunciei ~110/-30 num diff que foi +69/-4).
⚠️ REGRA S32d (NOVA) — nos Select-String de validação, o "esperado" é sempre PISO ou FAIXA, nunca número exato, a menos que eu tenha contado o output real do arquivo entregue. Se não contei, anunciar "≥ N" e aceitar qualquer valor ≥ N. Erro no esperado, não no código.

O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (166 passed ao fim da S32). Container de teste rumo_postgres_test na porta 5433.

⚠️ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).

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
│ ├── _scratch/
│ ├── docker-compose.test.yml
│ ├── pytest.ini
│ └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│ ├── lib/
│ │ ├── main.dart (StatefulShellRoute + bottom nav desde S32)
│ │ ├── models/ (activity.dart, activity_track.dart, comment.dart,
│ │ │ user_me.dart ← NOVO S32)
│ │ ├── pages/ (activity_detail_page.dart, feed_page.dart,
│ │ │ login_page.dart, profile_page.dart ← NOVO S32,
│ │ │ upload_page.dart ← NOVO S31)
│ │ ├── services/ (api.dart, auth_service.dart)
│ │ └── widgets/ (activity_card.dart ← NOVO S32,
│ │ activity_map.dart, like_button.dart)
│ ├── pubspec.yaml (file_picker: ^13.3.3, go_router: ^18.1.2)
│ └── pubspec.lock
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 6 atividades, 26.443 m. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, tipo walk, 60 pontos, ~10 min de duração) usada para validar o S26.

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21/S22/S23/S24/S25/S26/S27/S28/S29/S30/S31/S32)

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

    Select-String -SimpleMatch não aceita | como alternância (S25a).

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

    Contar as ocorrências reais antes de anunciar "esperado Nx" num Select-String (S29c).

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

    Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA, nunca número exato sem contagem real do output (S32d).

Processo que o usuário elogiou na S21–S32 (para manter)

Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).

    Descoberta antes de codar: pedir arquivos com motivo declarado.

    Validação entre cada entrega.

    Contrato travado escrito antes de codar.

    Commits pequenos e temáticos.

    Validação separada da local.

    Diagnóstico honesto antes de "consertar".

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 166 testes passando LOCALMENTE, 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon, minLat, maxLon, maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax no mesmo SELECT (sem N+1).

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (_ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor. CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona com ou sem rota). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422; omitido → default csv.

Export em lote (S22): GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). format=csv: inclui todas; format=gpx: só com rota. Filtro from/to inclusivo (UTC). 0 atividades → 200 + ZIP vazio. from > to → 422. format inválido → 422.

S26 (GPX com <time> por ponto): to_gpx(activity, coordinates, raw_track_points=None) ganhou o 3º parâmetro opcional. Quando raw_track_points existe e tem o MESMO comprimento de coordinates, cada <trkpt> recebe <time> com o timestamp real do ponto (unix epoch → ISO 8601 UTC). Caso contrário, fallback para started_at em todos os pontos. Contrato HTTP inalterado.

S31 — upload mobile (NOVO na S31, inalterado na S32):

    POST /activities/upload — Auth Bearer JWT. multipart/form-data com file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120), activity_type (opcional), description (opcional). Sucesso: 201 com ActivityResponse. Erro: 422 (HTTPValidationError), 429 (slowapi, rate limit 10/h por IP), 401 (token). Parse síncrono, ~1–3s por arquivo.

    mobile/lib/services/api.dart — uploadActivity({File? file, List<int>? bytes, String? filename, String? title, String? activityType, String? description, String? token}) → Future<Activity>. Usa http.MultipartRequest (NÃO passa pelo _send). MultipartFile.fromPath quando file != null, MultipartFile.fromBytes quando só bytes != null (web). Timeout 60s.

    mobile/lib/pages/upload_page.dart (NOVO) — StatefulWidget, ~239 linhas. _pickFile() → FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['gpx','fit']) → List<PlatformFile> (vazio = cancelou). Se path != null → File; senão → readAsBytes() → _bytes. Valida extensão e tamanho ≤ 20 MB. _submit() → auth.api.uploadActivity(...) → SnackBar verde + context.pop(true).

S32 — perfil próprio + bottom nav (NOVO):

    GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> — auth Bearer JWT. Filtra atividades por usuário. O description do schema diz "requer seguir" quando user_id é de terceiro; para o próprio, sempre passa. Retorna ActivityResponse[] puro (sem envelope de paginação — sem total/has_more). Paginação client-side por "se voltou < limit, acabou".

    GET /users/{user_id} — retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email. NÃO tem avatar_url. NÃO tem created_at. Para o perfil próprio, o cabeçalho usa GET /auth/me (que retorna UserResponse completo, com email). getUser(id) fica para o perfil de terceiro (S34+).

    mobile/lib/services/api.dart — listActivities({String? userId, int limit = 20, int offset = 0, String? token}) → Future<List<Activity>>. Usa get('/activities?limit=&offset=[&user_id=]'). Propaga ApiException. Retorno é List<Activity> via Activity.fromJson.

    mobile/lib/models/user_me.dart (NOVO) — UserMe { id, email, username, fullName, isActive }. fromJson de GET /auth/me. Só os campos que o perfil usa (weight_kg/height_cm/birth_date ficam de fora — YAGNI).

    mobile/lib/widgets/activity_card.dart (NOVO) — ActivityCard extraído do feed_page.dart. Mesmo layout, mesmas props (activity, auth, onTap, onChanged). Reusado pelo FeedPage e pelo ProfilePage. ActivityCardMetric (privado do arquivo) substituiu o _Metric interno.

    mobile/lib/pages/feed_page.dart (REFATORADO) — Removeu _ActivityCard/_Metric (foram para widgets/activity_card.dart). _load() ganhou 4 if (!mounted) return; + if (mounted) setState no finally (fix do setState() after dispose, dívida registrada na S31). _openDetail() ganhou 2 if (!mounted) return;. AppBar perdeu o IconButton(Icons.logout) (foi para o perfil, bottom nav dá acesso). FAB de upload mantido.

    mobile/lib/pages/profile_page.dart (NOVO, ~331 linhas) — StatefulWidget, recebe AuthService. Estado: UserMe? _me, List<Activity> _activities, bool _loading, String? _error, int _offset, bool _hasMore, bool _loadingMore. _load() faz Future.wait([/auth/me, /activities?user_id=<me>&limit=20&offset=0]) em paralelo. _loadMore() pagina (GET /activities?offset=<_offset>). Pull-to-refresh → _load(). _logout() → auth.logout() + context.go('/login'). _openDetail() → push /activity/:id + reload do item. UI: _ProfileHeader (CircleAvatar com inicial + username + full_name + email + TextButton Sair) + "Minhas atividades" + lista de ActivityCard + "Carregar mais"/"Fim.".

    mobile/lib/main.dart (REESCRITO) — StatefulShellRoute.indexedStack com 2 StatefulShellBranch (/feed, /profile). _ScaffoldWithNavBar fornece NavigationBar (Feed, Perfil). /login, /upload, /activity/:id ficam FORA do shell (rotas planas, sem bottom nav). redirect inalterado (mesma lógica). refreshListenable: _auth mantido. initialLocation: '/feed' mantido.

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
Deps mobile (S31/S32): file_picker: ^13.3.3, go_router: ^18.1.2 (StatefulShellRoute disponível desde 6.x).

Git (estado ao fim da Sessão 32)

883b0f9 (HEAD -> main, origin/main) feat(mobile): bottom nav Feed/Perfil via StatefulShellRoute (Sessao 32)
dd83f60 feat(mobile): tela de perfil com minhas atividades (Sessao 32)
7d84765 refactor(mobile): extrai ActivityCard e corrige setState/mounted no feed (Sessao 32)
ff3cb55 feat(mobile): listActivities e UserMe (Sessao 32)
f39820f docs: handoff da Sessao 31
71a00d4 feat(mobile): upload GPX/FIT no feed (Sessao 31)
a83ed82 feat(mobile): upload GPX/FIT no feed (Sessao 31)
3a154b1 docs: handoff da Sessao 30
ffaaea0 feat(web): delta de pace no drill-down por tipo (Sessao 30)
852608c docs: handoff da Sessao 29
ca855ee feat(web): detecta ZIP vazio no export em lote (Sessao 29)
a3268eb docs: handoff da Sessao 28
ba43fad feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28)
db2e224 docs: handoff da Sessao 27
585839f docs: handoff da Sessao 26
15ccccb feat(activities): GPX export com <time> por ponto (Sessao 26)
7bf5bc2 docs: handoff da Sessao 25
4146c3a docs: corrige README (remove instrucoes de sessao por engano)

Working tree limpo. S32 adicionou 4 commits (ff3cb55, 7d84765, dd83f60, 883b0f9). Push feito. HEAD == origin/main.

Pendente: docs/HANDOFF.md da S32 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 32.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 32

3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short veio VAZIO na abertura (o commit do handoff S31 já estava feito ANTES do início da S32 — hash f39820f, mas o handoff S31 listava 71a00d4 como HEAD; o f39820f foi commitado entre sessões, confirmando a REGRA S27a na prática: sempre checar git status --short, nunca assumir que o handoff reflete o HEAD real).

    Log/status. git log -8: f39820f (handoff S31), 71a00d4, a83ed82 (upload S31), 3a154b1 (handoff S30), ffaaea0 (pace S30), 852608c (handoff S29), ca855ee (ZIP vazio S29), a3268eb (handoff S28). git diff --stat HEAD~4..HEAD: só docs/ + mobile/ (zero backend/, zero web/). Bate com o handoff S31.

    Build/lint/analyze. npm run build: 824 modules, 4.53s, hashes idênticos ao build da S30/S31 (ProfilePage-pXfRJdbD.js 21.54 kB, index-DvGu4786.js 436.15 kB, ActivityDetailPage-C1KScSo5.js 11.38 kB, SearchPage-Bpu7TeFA.js 4.16 kB, RouteMap-CXXXy7Mv.js 2.41 kB, leaflet-Bw7RoR_1.js 163.60 kB, recharts-DI5KUTLO.js 351.26 kB). npm run lint: limpo. flutter analyze: No issues found! (4.0s, cache quente).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test já estava Up 2 hours (healthy), pg_isready respondeu accepting connections na 1ª tentativa (diferente da S31 que teve timing). pytest -q: 166 passed in 50.47s. ruff check .: All checks passed!.

    Prod backend (S26). Login OK. Atividade 01a1b36a-0951-71e8-9044-c55c71558441: 60 pontos com <time>, 60 distintos. Primeiro 2026-11-06T21:30:33Z (sem microssegundos, como na S31), último 2026-11-06T21:40:23Z. S26 NO AR confirmado via regex no Content. Sem cold start, sem rate limit, sem erro de login.

    Prod frontend (Vercel). index servido: /assets/index-CJjOEm0V.js (idêntico ao da S31). __vite__mapDeps: ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, leaflet-Bw7RoR_1.js, leaflet-CcXJxNtP.css, rolldown-runtime-hePW80VL.js, recharts-DI5KUTLO.js. Tríade de "S30 no ar" confirmada. Sanity semântico (6b) implícito no 6a: ProfilePage-Cy6s98Hl.js referenciado no __vite__mapDeps com nome idêntico ao da S30/S31 — a S30 está no ar por construção (hash do chunk só muda quando o conteúdo muda).

3.2 Fase 1 — descoberta para perfil + minhas atividades

Pedi 5 arquivos + openapi.json (4 schemas), com motivo declarado:

    openapi.json GET /activities: query { limit (1..100, default 20), offset (>=0, default 0), user_id (uuid|null, opcional, "requer seguir") }. Retorno ActivityResponse[]. Sem envelope de paginação. ACHADO #1: "requer seguir" quando user_id é de terceiro — para o próprio, sempre passa. ACHADO #2: sem total/has_more — paginação por "se voltou < limit, acabou".

    openapi.json GET /users/{user_id}: retorna UserPublic, não UserResponse. ACHADO #3: UserPublic é minimalista (id, username, full_name, is_active). NÃO tem email, avatar_url, created_at. ACHADO #4: para o perfil PRÓPRIO, o cabeçalho usa GET /auth/me (UserResponse completo, com email), NÃO getUser(id). Isso reduziu o escopo da S32 (sem getUser, sem model User separado).

    mobile/lib/main.dart: GoRouter simples, sem ShellRoute, 4 rotas planas (/login, /feed, /upload, /activity/:id). redirect protege tudo. refreshListenable: _auth. ACHADO #5: decidir bottom nav via ShellRoute vs IconButton no AppBar — decidi ShellRoute (padrão Material 3, preserva scroll, escalável para S33+).

    mobile/lib/services/api.dart: ApiClient com login, get, post, delete, uploadActivity, listComments, createComment, deleteComment, getActivityTrack. _send é JSON-only. _extractMessage pega .detail. _decode trata UTF-8. Padrão: token: String? em cada chamada (não AuthService inteiro). ACHADO #6: listActivities segue o mesmo padrão (token: String?).

    mobile/lib/services/auth_service.dart: AuthService extends ChangeNotifier. currentUserId SÍNCRONO (cacheado do JWT, getter String?). token SÍNCRONO. api getter (ApiClient). logout() limpa token + storage + notifica. ACHADO #7: currentUserId síncrono — o ProfilePage pode usar widget.auth.currentUserId direto, sem Future.

    mobile/lib/pages/feed_page.dart: _ActivityCard é StatelessWidget privado. _Metric é privado. _load() tem 4 setState sem mounted (não 1, como o handoff S31 dizia "linha 51"). _openDetail() tem 1 setState via _replaceActivity sem mounted. ACHADO #8: extrair _ActivityCard para widgets/activity_card.dart (reuso no perfil), corrigir 4+ pontos de mounted.

    mobile/lib/models/activity.dart: Activity com UserPublic LOCAL (id, username, fullName, avatarUrl). ACHADO #9: o UserPublic local tem avatarUrl que o UserPublic do backend NÃO tem — dívida conhecida, não tocada na S32 (o _ActivityCard usa avatarUrl só se não for null, fallback inicial do username). Activity.fromJson cobre ActivityResponse inteiro, incluindo bbox (List<double>?).

3.3 Fase 2 — contrato travado

Ver Seção 1 (TL;DR). Contrato completo: endpoint, schema, métodos, model, UI, validação, decisão de bottom nav travada (A: StatefulShellRoute), ordem de entrega (6 arquivos, 2 pares acoplados: card+feed, profile+main).

3.4 Fase 3 — entrega incremental (6 arquivos, 4 builds)

    api.dart — listActivities. analyze verde.

    models/user_me.dart (novo) — UserMe. analyze verde.

    widgets/activity_card.dart (novo) + pages/feed_page.dart (refatorado) — par acoplado, 1 build. ActivityCard extraído, _load() com 4+ mounted, AppBar sem IconButton(logout). analyze verde.

    pages/profile_page.dart (novo, 331 linhas) — ProfilePage + _ProfileHeader. analyze verde.

    main.dart (reescrito) — StatefulShellRoute + _ScaffoldWithNavBar + NavigationBar. analyze verde.

3.5 Fase 3.5 — verificar save + commit (com 5 desvios de contagem)

Bloco de verificação rodado em cada arquivo. 5 desvios no "esperado" do Select-String, todos do MEU lado (não do código):

    api.dart (arquivo 1/6): fromJson em user_me.dart contou 2 (1 no comentário "e o 'fromJson' lançaria", 1 na factory). REGRA S32b (SimpleMatch casa comentário).

    user_me.dart (arquivo 2/6): 33 linhas, anunciei ~37. Erro de contagem mental (S32c).

    activity_card.dart (arquivo 3/6): class ActivityCard contou 2 (casa class ActivityCardMetric por prefixo). REGRA S32a (SimpleMatch casa prefixo). _ActivityCard no card contou 2 (2 menções no comentário de topo). _ActivityCard no feed contou 1 (1 menção no comentário de topo).

    profile_page.dart (arquivo 5/6): 331 linhas, anunciei ~260. Erro de contagem mental (S32c). mounted 13, anunciei ≥ 8 (piso OK).

    main.dart (arquivo 6/6): StatefulShellRoute.indexedStack 2 (1 no código + 1 no comentário). diff +69/-4, anunciei ~110/-30. Erro de estimativa de diff (S32c).

Nenhum arquivo a corrigir. Todos os desvios foram no "esperado" do teste, não no código.

3.6 Fase 4 — validação (manual no Chrome, 11/11)

Só mobile mudou. Render e Vercel intocados (Fase 0 já confirmou). Fase 4 = validação manual no Chrome:

    flutter run -d chrome — OK.

    Login (prod@rumo.com / senha12345) — OK.

    Bottom nav com 2 abas (Feed / Perfil) — OK.

    Aba Feed: carrega, FAB de upload presente, SEM IconButton(logout) no AppBar — OK.

    Aba Perfil: cabeçalho (username + email + full_name + Sair) + "Minhas atividades" com ActivityCard (mesmo layout) + "Carregar mais"/"Fim." — OK.

    Troca de aba preserva scroll — OK (StatefulShellRoute.indexedStack).

    Logout funciona — OK.

    Re-login cai em /feed — OK.

    FAB upload ainda funciona (abrir, cancelar, feed recarrega) — OK.

    Detalhe abre como rota plana /activity/:id, sem bottom nav — OK (intencional).

    Voltar do detalhe restaura o Perfil com bottom nav — OK.

Nenhum bug encontrado. Nada a corrigir.

O que NÃO foi validado:

    Upload em Android físico/emulador (mesma dívida da S31 — só web validado).

    Paginação real com >20 atividades (conta prod tem 6 — não exercitou "Carregar mais").

    Estado de erro do perfil (forçar 500/401 no /auth/me) — não exercitado.

    Rate limit 429 do upload — não exercitado (dívida S31).

    Acessibilidade (semântica dos destinos do NavigationBar) — não verificada.

3.7 Observações / bugs encontrados

    setState() called after dispose() no feed_page.dart — CORRIGIDO na S32 (4 if (!mounted) return; + if (mounted) setState no finally do _load; 2 if (!mounted) return; no _openDetail). Dívida da S31 fechada.

    UserPublic local em activity.dart tem avatarUrl que o UserPublic do backend não tem. Dívida conhecida (S32 — achado #9). O _ActivityCard usa avatarUrl só se não for null. Não tocado.

    Timestamps do GPX em prod sem microssegundos (S26) — continua. Contrato intacto (60/60 distintos). Dívida S31.

    AuthService SEM refresh token — continua (dívida S31). Token expirado → 401 → ApiException; o app NÃO faz logout automático.

    Nenhum bug novo na S32.

3.8 Resultado da suíte (S32)

    pytest -q → 166 passed (nenhuma mudança backend).

    ruff check . → All checks passed!.

    npm run build → 824 modules (web inalterado).

    npm run lint → limpo (web inalterado).

    flutter analyze → No issues found! (mobile com 6 arquivos novos/modificados).

    Validação manual no Chrome → 11/11 passos verdes.

3.9 Commits pushados (S32)

    ff3cb55 feat(mobile): listActivities e UserMe (Sessao 32) — 2 arquivos, +65 (api.dart +32, user_me.dart +33).

    7d84765 refactor(mobile): extrai ActivityCard e corrige setState/mounted no feed (Sessao 32) — 2 arquivos, +192/-177 (feed_page.dart -177/+14, activity_card.dart +178).

    dd83f60 feat(mobile): tela de perfil com minhas atividades (Sessao 32) — 1 arquivo, +331 (profile_page.dart).

    883b0f9 feat(mobile): bottom nav Feed/Perfil via StatefulShellRoute (Sessao 32) — 1 arquivo, +69/-4 (main.dart).

Push feito. HEAD == origin/main == 883b0f9. Working tree limpo.

Pendente: docs: handoff da Sessao 32 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT). Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota". Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { id, user_id, activity_type, title, description, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, cover_photo_url, photo_count, created_at, likes_count (default 0), liked_by_me (default false), comments_count (default 0), bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL. Não tem "user" embutido — o feed e o perfil recebem ActivityResponse "cru" (sem username do autor); o mobile não tem como renderizar username a partir do /activities. ⚠️ NOVO: o _ActivityCard usa activity.user?.username — se o backend não manda user, o card cai no fallback "Usuário" / inicial "?". Isso é dívida (o feed usa GET /feed, que provavelmente embute user; o perfil usa GET /activities, que talvez não — testar na S33).

GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> (auth: Bearer JWT) — S32. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro (sem envelope). Paginação client-side.

GET /users/{user_id} (auth: Bearer JWT) — S32. Retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email, avatar_url, created_at. Para o perfil PRÓPRIO, usar GET /auth/me (UserResponse completo).

GET /auth/me — UserResponse completo: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }. NÃO é /users/me (esse devolve 422).

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21. Permissão: dono OU seguidor do dono. Caso contrário, 404. format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id><type>.csv". 1 header + 1 linha. Funciona com/sem rota. format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo<id>_<type>.gpx". S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. ISO 8601 UTC. Exige rota → 404 se route IS NULL. format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22. Auth: self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto. format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota). Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

POST /activities/upload (auth: Bearer JWT) — S31. multipart/form-data: file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120, nullable), activity_type (opcional, string, nullable), description (opcional, string, nullable). Sucesso: 201 com ActivityResponse. Erro: 422 HTTPValidationError (.detail tratado pelo _extractMessage do mobile). Rate limit: 10/hora por IP (slowapi; 429). Parse síncrono, ~1–3s.

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.
GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5. S30: NÃO inclui avg_pace_s_per_km em nenhum shape — pace é derivado no front (computePace).

Janelas (S17/S18/S20):
period	compare	janela
all	qualquer	null
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide)

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–32 commitadas e pushadas. HEAD == origin/main == 883b0f9. Working tree limpo.

Pendente: este handoff.

Primeira ação da Sessão 33 (REGRA S27a — handoff primeiro)

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 32"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 32 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)

[Sessão 33 — primeira ação] Abrir PowerShell via Win+R → powershell (NÃO abrir de dentro do VS Code / Windows Terminal).

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 32"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 33 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 33 — primeira ação] Docker + pytest local

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

[Sessão 33 — primeira ação] Detecção de versão em produção (front — Vercel)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24). ⚠️ REGRA S29b: o hash servido pelo Vercel não bate com o build local. O sinal de "novo no ar" é o hash mudou vs sessão anterior.

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:($m.Groups[1].Value)"

idx=Invoke−WebRequest−Uriidx=Invoke−WebRequest−UriidxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|ProfilePage|SearchPage)-[A-Za-z0-9_-]+.js'

Esperado no estado atual (S32): web inalterado desde S30 — index-CJjOEm0V.js com ProfilePage-Cy6s98Hl.js, ActivityDetailPage-DOBuid_4.js, SearchPage-D6UpMvrw.js.

[Sessão 33 — sanity opcional] Validar S30 semanticamente

chunkUrl="https://rumo−wheat.vercel.app/assets/ProfilePage−Cy6s98Hl.js"chunkUrl="https://rumo−wheat.vercel.app/assets/ProfilePage−Cy6s98Hl.js"chunk = Invoke-WebRequest -Uri chunkUrl−UseBasicParsingchunkUrl−UseBasicParsinghits = ([regex]::Matches(chunk.Content,′Pace∣lower′)).CountWrite−Host"ocorrenciasdePace/lowernochunk:chunk.Content,′Pace∣lower′)).CountWrite−Host"ocorrenciasdePace/lowernochunk:hits"

Esperado: 12.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodytoken = login.accesstokenlogin.accesst​okenme = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer token" } meId = $me.id

Detecção de versão em produção (backend S26 — GPX com <time> por ponto)

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodyh = @{ Authorization = "Bearer ((login.access_token)" }

aid="01a1b36a−0951−71e8−9044−c55c71558441"aid="01a1b36a−0951−71e8−9044−c55c71558441"resp = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$aid/export?format=gpx" -Headers $h -UseBasicParsing

times=[regex]::Matches(times=[regex]::Matches(resp.Content, '<time>([^<]+)</time>') | ForEach-Object { _.Groups[1].Value } n = times.Counttimes.Countdistinct = (times∣Sort−Object−Unique).CountWrite−Host"pontoscom<time>:times∣Sort−Object−Unique).CountWrite−Host"pontoscom<time>:n"
Write-Host "<time> distintos: distinct"if(distinct"if(n -gt 0) {
Write-Host "primeiro: ((times[0])"
Write-Host "ultimo: ((times[-1])"
}
if (distinct−le1−anddistinct−le1−andn -gt 1) {
Write-Host "S25 AINDA NO AR (todos iguais)."
} elseif (distinct−gedistinct−gen - 1) {
Write-Host "S26 NO AR (timestamps distintos por ponto)."
} else {
Write-Host "ATENCAO: apenas distinct/distinct/n distintos."
}

Esperado agora: 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, ultimo 2026-11-06T21:40:23Z (sem microssegundos desde a S31).

[Sessão 33 — validação do perfil via API] (novo S32)

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodyh = @{ Authorization = "Bearer ((login.access_token)" }
me=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/me"−Headersme=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/me"−Headersh
Write-Host "me.id: ((me.id)"
Write-Host "me.email: ((me.email)"
acts=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities?userid=acts=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities?useri​d=(me.id)&limit=20&offset=0" -Headers h
Write-Host "minhas atividades: ((acts.Count)"
$acts | Select-Object -First 1 | ConvertTo-Json -Depth 3

Esperado: me.id = 01a12c83-be2a-71fa-b966-1c93ca64f341, me.email = prod@rumo.com, minhas atividades = 6 (conta prod). O JSON do primeiro item mostra os campos do ActivityResponse.

Teste real do ZIP (auth) — bytes crus via RawContentStream (REGRA S26a)

Add-Type -AssemblyName System.IO.Compression.FileSystem
body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodyh = @{ Authorization = "Bearer ((login.access_token)" }
r=Invoke−WebRequest−Uri"https://rumo−api−5s0b.onrender.com/activities/export?format=csv"−Headersr=Invoke−WebRequest−Uri"https://rumo−api−5s0b.onrender.com/activities/export?format=csv"−Headersh -UseBasicParsing
Write-Host "CSV default: ((r.StatusCode) ((r.Headers['Content-Type'])"
tmp=[System.IO.Path]::GetTempFileName()tmp=[System.IO.Path]::GetTempFileName()fs = [System.IO.File]::OpenWrite(tmp)tmp)r.RawContentStream.Position = 0
r.RawContentStream.CopyTo(r.RawContentStream.CopyTo(fs)
fs.Close()fs.Close()zip = [System.IO.Compression.ZipFile]::OpenRead(tmp)Write−Host"entries:tmp)Write−Host"entries:(zip.Entries.Count)"zip.Entries.Count)"zip.Dispose()

Stats de terceiros (S19/S20)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3 Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/meId/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

Ruff (backend)

cd D:\Rumo\backend
Se o prompt já mostra (venv), pule:

.\venv\Scripts\Activate.ps1
ruff check .

Recuperação de arquivo corrompido (lição S21)

cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>
Se o último commit for anterior à mudança quebrada:

git restore <arquivo>
Se a versão quebrada JÁ foi commitada:

git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22 + S26c)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"

Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy.

Se rota no ar mas retorna 422, ver o BODY do erro:

try {
Invoke-WebRequest -Uri "<url>" -Headers h -UseBasicParsing | Out-Null } catch { resp = .Exception.Response.​Exception.Responsereader = New-Object System.IO.StreamReader(resp.GetResponseStream())Write−Host"STATUSresp.GetResponseStream())Write−Host"STATUS(resp.StatusCode)"Write−Host(resp.StatusCode)"Write−Host(reader.ReadToEnd())
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b)

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:(m.Groups[1].Value)"m.Groups[1].Value)"idx = Invoke-WebRequest -Uri idxUrl−UseBasicParsingidxUrl−UseBasicParsingidx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+.js'

Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. Para confirmar conteúdo: baixar o chunk novo e Select-String do símbolo/helper que mudou.

⚠️ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.

Diagnóstico de save de arquivo (lição S25 + S32)

Depois de salvar, ANTES de commitar:

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
Write-Host "=== [6] hash do HEAD ==="
git rev-parse HEAD:<arquivo>

Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou.
Se [5] != [6] e [4] mostra ' M' → save pegou, pode commitar.

Nota S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS". Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b.
Nota S32a/S32b: -SimpleMatch 'class X' casa 'class Xxx' (prefixo). -SimpleMatch '_X' casa menções em //. Para contagem exata, -Pattern '\bclass X\b' ou filtrar linhas //.

Contornar editor que não salva (REGRA S31c)

Se Select-String do disco mostrar conteúdo antigo depois do save do editor:

cd D:\Rumo\mobile # ou o diretório do arquivo
content=@′//conteuˊdocompletodoarquivoaqui′@[System.IO.File]::WriteAllText("content=@′//conteuˊdocompletodoarquivoaqui′@[System.IO.File]::WriteAllText("PWD\caminho\do\arquivo.dart", content,[System.Text.UTF8Encoding]::new(content,[System.Text.UTF8Encoding]::new(false))
Write-Host "_bytes: ((Select-String -Path caminho\do\arquivo.dart -Pattern '_bytes' -SimpleMatch | Measure-Object).Count) (esperado >=2)" Write-Host "debugPrint: ((Select-String -Path caminho\do\arquivo.dart -Pattern 'debugPrint' -SimpleMatch | Measure-Object).Count) (esperado 0)"

O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.

Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)

ERRADO — Content é string, não byte[]:
[System.IO.File]::WriteAllBytes(path, $resp.Content)

CERTO (texto UTF-8):
[System.IO.File]::WriteAllBytes(path, [System.Text.Encoding]::UTF8.GetBytes($resp.Content))

CERTO (bytes crus — ZIP, imagem):
fs=[System.IO.File]::OpenWrite(fs=[System.IO.File]::OpenWrite(path)
resp.RawContentStream.Position=0resp.RawContentStream.Position=0resp.RawContentStream.CopyTo(fs)fs)fs.Close()

MELHOR para inspecionar GPX — sem arquivo, regex no Content:
times=[regex]::Matches(times=[regex]::Matches(resp.Content, '<time>([^<]+)</time>') | ForEach-Object { $_.Groups[1].Value }

Verificar perfil mobile em prod (S32 — NOVO)

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

E rodar o app:
& "C:\Users\nasci\flutter\bin\flutter.bat" run

Escolher device (Chrome para web, Android para emulador/aparelho). Testar: login → bottom nav → aba Perfil carrega cabeçalho + lista + Sair → aba Feed mantém scroll → detalhe abre sem bottom nav. O backend Render responde.

⚠️ Developer Mode: se flutter run falhar com erro de symlink, rodar start ms-settings:developers e ativar (REGRA S31a).

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

(CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.
(CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.
(CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.
(CONHECIDA — Sessão 17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.
(CONHECIDA — Sessão 17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. NÃO é bug.
(CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática.
(CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk". Testes usam activity.activity_type.value dinâmico.
(CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. YAGNI por enquanto.
(CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries. Aceitável para export raro.
(CONHECIDA — Sessão 22) Export em lote é self-only. Decisão de privacidade.
(CONHECIDA — Sessão 23) downloadActivityExportBulk valida from > to client-side. Dupla validação proposital.
(CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).
(CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado desde antes.
(CONHECIDA — Sessão 26) <time> no GPX inclui microssegundos (2026-11-07T00:20:32.931332Z) porque o gpxpy serializa datetime.isoformat(). Observação S31: em prod agora vem truncado em segundos (2026-11-06T21:30:33Z). Contrato intacto. Investigar se/quando quiser.
(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Coberto por teste.
(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. É renomeação de referência cruzada no __vite__mapDeps, não regressão (REGRA S28b).
(CONHECIDA — Sessão 29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Sentinel 0xFFFF sinaliza falha (retorna -1, fail-open).
(CONHECIDA — Sessão 29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs). Se o export virar pesado, trocar por blob.slice(-22-65535, blob.size).
(CONHECIDA — Sessão 29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.
(CONHECIDA — Sessão 30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX. Se um dia alguém quiser pace em cycle, relaxar PACE_TYPES — DeltaLine já tem lowerIsBetter pronto.
(CONHECIDA — Sessão 30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0 (computePace(item) ?? 0), resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero.
(CONHECIDA — Sessão 31) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → ApiException; o app NÃO faz logout automático. Melhoria para "mundo real", não MVP.
(CONHECIDA — Sessão 31) Mobile: uploadActivity valida path == null → readAsBytes(), cobre web. No Android, path costuma vir preenchido (o plugin copia pra cache) e o File(path) deve funcionar — não testado em dispositivo físico. Testar na S33+.
(CONHECIDA — Sessão 31) Mobile: rate limit 10/h do /activities/upload não foi testado explicitamente (429). Se o backend devolver .detail legível, a UI mostra; se não, mostra "Erro 429". Oportunidade: UI dedicada com cooldown visual.
(CONHECIDA — Sessão 31) Mobile: activity_type fora da UI do upload na S31 — o backend infere pelo arquivo. Se precisar de override manual, é um dropdown em sessão futura.
(CONHECIDA — Sessão 31) Mobile: upload_page.dart tem ~239 linhas. debugPrint removido após diagnóstico. _clearFile() extraído. hasFile derivado de _file != null || _bytes != null.
(CONHECIDA — Sessão 31) O commit a83ed82 foi feito pelo usuário/VS Code com a versão inicial; 71a00d4 refinou upload_page.dart e api.dart. Não vale rebase/squash.
(CONHECIDA — Sessão 31) file_picker 13.3.3 trouxe 11 deps novas (android_file_picker, cross_file, dbus, file_picker_darwin, file_picker_linux, file_picker_platform_interface, file_picker_web, petitparser, windows_file_picker, xml + file_picker). Todas no pubspec.lock.
(CONHECIDA — Sessão 32) GET /activities (backend) retorna ActivityResponse[] SEM o campo "user" embutido (o schema não tem user). O _ActivityCard usa activity.user?.username — se o backend não manda user, cai no fallback "Usuário"/"?" (inicial). O GET /feed provavelmente embute user (o feed renderiza username); o GET /activities NÃO. TESTAR NA S33: abrir o perfil e ver se o username aparece no ActivityCard. Se não, ou (a) o backend precisa passar a embutir user no /activities, ou (b) o mobile renderiza sem username (só o tipo). Anotado.
(CONHECIDA — Sessão 32) UserPublic local em activity.dart tem avatarUrl que o UserPublic do backend NÃO tem (o do backend é { id, username, full_name, is_active }). O _ActivityCard usa avatarUrl só se não for null. Dívida: alinhar o model local com o schema (remover avatarUrl) ou o backend ganhar o campo. Não tocado na S32.
(CONHECIDA — Sessão 32) ProfilePage usa Future.wait([/auth/me, /activities?user_id=...]) em paralelo. Se um falhar, o Future.wait rejeita com o primeiro erro. O catch genérico mostra "Erro: $e" — se o erro for do /auth/me, o /activities pode ter sucesso e ser descartado. Aceitável para o perfil (ambos são essenciais), mas anotado.
(CONHECIDA — Sessão 32) ProfilePage paginação: "Carregar mais" (botão), não scroll infinito. O backend não dá total; regra "se voltou < limit, acabou". Conta prod tem 6 atividades — o "Carregar mais" NÃO foi exercitado na S32. Testar na S33+ (criar conta com >20 atividades ou aumentar temporariamente o limit).
(CONHECIDA — Sessão 32) ProfilePage estado de erro: se /auth/me falha, mostra mensagem + "Tentar novamente". Não exercitado (forçar 500/401). Testar na S33+.
(CONHECIDA — Sessão 32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id ficam FORA do shell (sem bottom nav). Decisão intencional: upload é ação do feed (FAB), detalhe é fluxo (volta para a aba de origem).
(CONHECIDA — Sessão 32) initialLocation: index == navigationShell.currentIndex no NavigationBar. É o padrão "tocar na aba atual volta à raiz". Hoje não tem sub-rotas nas branches, então não tem efeito. Defensivo para o futuro.
(CONHECIDA — Sessão 32) O FAB de upload some quando o usuário está na aba Perfil. Intencional (upload é ação do feed). Se quiser FAB global, mover para o _ScaffoldWithNavBar — NÃO recomendado (o FAB do shell fica estranho sobre o bottom nav).

(Oportunidade — S18–S32) Semântica do delta é NEUTRA. Sem "melhor/pior". Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.
(Oportunidade — S19–S32) Stats públicas só quando viewer segue o alvo.
(Oportunidade — S22–S32) Export em lote no mobile (paridade com web S21/S22/S29).
(Oportunidade — S30) Testes unitários do DeltaLine (não há hoje; é puro, dá pra testar com 4 casos e sem React Testing Library).
(Oportunidade — S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.
(Oportunidade — S31) Testar upload em Android físico/emulador (o path do Android e o File(path) não foram exercitados).
(Oportunidade — S31) UI dedicada para 429 (rate limit) com cooldown visual.
(Oportunidade — S31) activity_type como dropdown opcional na UploadPage.
(Oportunidade — S32) Stats agregados no perfil (GET /users/{id}/stats/summary) — S33.
(Oportunidade — S32) Perfil de terceiro + follow (GET /users/{id}, GET /users/{id}/stats/*) — S34.
(Oportunidade — S32) getUser(id) no ApiClient + model User (contra UserPublic) — S34.
(Oportunidade — S32) Busca de usuários — S35.
(Oportunidade — S32) Export no mobile (unitário + lote) — S36.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 33 e além)

Sessão 32 fechada. Perfil próprio + "minhas atividades" funcionando, bottom nav via StatefulShellRoute. Mobile subiu de ~48% para ~55% de cobertura. Backend/web inalterados.

Primeira ação obrigatória da Sessão 33 (REGRA S27a)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 33 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 32, push, confirmar HEAD == origin/main.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (docker ps -a, pg_isready, pytest -q → 166, ruff check).

    Detecção de versão em produção (front Vercel + back Render S26 + GET /activities?user_id=<me> — bloco novo de validação do perfil).

Rota travada para a Sessão 33: Stats agregados no perfil (paridade com web S18/S20/S28/S30)

Este é o próximo gap funcional do mobile: o perfil hoje mostra cabeçalho + lista, mas não mostra os números agregados (distância total, duração total, calorias, atividades por tipo, deltas). O backend já tem os 4 endpoints prontos (validados desde S19/S20):

    GET /users/{user_id}/stats/summary

    GET /users/{user_id}/stats/weekly?weeks=N

    GET /users/{user_id}/stats/monthly?months=N

    GET /users/{user_id}/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy>

Contrato preliminar (a confirmar na Fase 1 da S33, pedindo api.dart, profile_page.dart, e o openapi.json dos 4 endpoints + os shapes StatsSummary/StatsWeeklyResponse/StatsMonthlyResponse/StatsByTypeResponse):

    lib/services/api.dart — adicionar 4 métodos (ou 1 por endpoint):

        Future<StatsSummary> getStatsSummary(String userId, {String? token})

        Future<StatsWeekly> getStatsWeekly(String userId, {int weeks = 8, String? token})

        Future<StatsMonthly> getStatsMonthly(String userId, {int months = 6, String? token})

        Future<StatsByType> getStatsByType(String userId, {String period = '90d', String compare = 'prev', String? token})

    lib/models/stats.dart (NOVO) — StatsSummary, StatsWeekly, StatsMonthly, StatsByType (+ StatsByTypeItem + StatsByTypePreviousItem). Pedir o schema antes de codar.

    lib/widgets/stats_cards.dart (NOVO) — os cards do resumo (distância total, duração total, calorias, atividades). Reusar o padrão do ActivityDetailPage (que já tem StatsCards, mas por atividade — o do perfil é agregado). Ou extrair o padrão.

    lib/widgets/stats_delta_line.dart (NOVO) — o delta (paridade com o web DeltaLine, incluindo lowerIsBetter para Pace). Pedir o web/src/lib/format.ts e o DeltaLine.tsx antes de portar.

    lib/pages/profile_page.dart — adicionar a seção de stats entre o cabeçalho e "Minhas atividades". Estados: _statsLoading, _statsError, _summary. Não bloquear a lista se os stats falharem (Future.wait separado ou carregamento em cascata).

Escopo NÃO incluso na S33:

    Weekly/monthly charts (barras, linhas) — o StatsByType com delta é o mais valioso; weekly/monthly pode ficar para S34.

    Follow/seguidores — S34.

    Notificações — S35+.

    Busca de usuários — S35.

    Export no mobile — S36.

Escolha para a Sessão 34 (a decidir depois da S33)

OPÇÃO 1 — Weekly/monthly charts no perfil (barras por semana/mês).
OPÇÃO 2 — Perfil de terceiro (tocar no avatar/nome no feed/detalhe → perfil público com stats, follow/unfollow). Requer getUser(id) + model User (contra UserPublic) + GET /users/{id}/stats/* (já existe) + follow.
OPÇÃO 3 — Busca de usuários.
OPÇÃO 4 — Export no mobile (paridade com web S21/S22/S29).
OPÇÃO 5 — Build de release + ícone + splash + política de privacidade + exclusão de conta (bloqueadores de loja).

Recomendação: S33 = stats no perfil (fecha o ciclo do perfil). S34 = perfil de terceiro + follow. S35 = busca. S36 = export. S37 = build de release + loja. ~5–7 sessões para o MVP em loja.

Recomendação final para a Sessão 33

Rodar Fase 0 completa (com handoff S32 commitado primeiro). Se tudo verde, começar os stats no perfil seguindo o contrato acima — entrega incremental (stats.dart + api.dart → stats_cards.dart + stats_delta_line.dart → profile_page.dart), com flutter analyze entre cada entrega e validação manual (Chrome/web primeiro, Android depois se o Developer Mode estiver ligado).

⚠️ Antes de codar: Fase 1 da S33 precisa pedir os arquivos web equivalentes (web/src/lib/format.ts, web/src/components/StatsCards.tsx, web/src/components/DeltaLine.tsx ou PreviousDelta.tsx) para portar a semântica correta (lowerIsBetter, isGood/isBad, 4 casos). Não inventar do zero — o web é a fonte da verdade para a semântica de stats/delta.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 33 neste mesmo formato (seções 0 a 9) + o percentual de prontidão atualizado.

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".
Na S23: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."
Na S24: confirmou "tudo como esperado" duas vezes.
Na S25 (abertura): reforçou os mesmos acordos. Tolerou 3 tropeços.
Na S26 (abertura): reforçou os mesmos acordos. Tolerou 2 tropeços.
Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a.
Na S28 (abertura): handoff S27 já commitado. Fase 1 revelou escopo real (1 arquivo, não 6).
Na S29 (abertura): handoff S28 já commitado. Fase 1 revelou 2 arquivos. Entreguei activities.ts, o usuário colou erro do ESLint no-useless-assignment — corrigi, REGRA S29d.
Na S30 (abertura): handoff S29 já commitado. Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. 1 tropeço (contagem "5x vs 6x", REGRA S29c), 1 achado (Select-String case-insensitive, S30a).
Na S31 (abertura): handoff S30 já commitado (3a154b1). Fase 0 limpa. Tropeços: (1) file_picker 13.x mudou a API (REGRA S31b); (2) o editor falhou 3 vezes em salvar o upload_page.dart (REGRA S31c); (3) teste manual revelou que na web file_picker retorna path == null mas readAsBytes() funciona — corrigi para aceitar bytes; (4) commit duplicado (a83ed82 + 71a00d4) — estado final íntegro, não vale rebase. Validação final: FAB → selecionar .gpx → preview → enviar → SnackBar verde → feed recarrega. Funcionou.
Na S32 (abertura): handoff S31 já commitado (f39820f, feito entre sessões — o handoff S31 listava 71a00d4 como HEAD, confirmando a REGRA S27a na prática). Fase 0 limpa. Fase 1 revelou 5 achados que mudaram o plano (UserPublic minimalista → perfil próprio usa /auth/me; feed usa /feed, perfil usa /activities; _ActivityCard privado → extrair; _load tem 4 setState sem mounted, não 1; StatefulShellRoute vs IconButton → decidi ShellRoute). Entrega incremental: 6 arquivos, 4 builds, todos analyze verde. 5 desvios de contagem no "esperado" (S32a–S32d consolidadas). Validação manual no Chrome: 11/11. Funcionou.

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Acordo novo na S32: manter o processo da S21–S31. Concretamente:

    Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os 5 arquivos pivô antes de estimar.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

    Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c).

    Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local.

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S32 (Seção 0, itens 32a–32d): Select-String -SimpleMatch 'class X' casa prefixo; -SimpleMatch '_X' casa comentários; "esperado ≈ N linhas" só depois de contar; "esperado" nos Select-String é sempre piso/faixa.

O que funcionou nas S21–S32 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão), disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32), e a consistência em aceitar os erros (API do plugin, contagem, lint, falsos positivos, save do editor) na hora e corrigir/registrar, sem contornar. E a novidade da S32: aceitar que a contagem mental falha para baixo de forma sistemática, e mudar o método (piso/faixa) em vez de tentar "contar melhor".