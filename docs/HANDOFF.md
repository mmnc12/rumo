HANDOFF — Rumo (backend + frontend + mobile) — Sessão 31
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

⚠️ REGRA S25b — quando $lines[-1] for suspeito, confirmar com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo único>" antes de concluir. Não dar "OK" nem "corrompido" sem evidência.

⚠️ REGRA S25c — antes de pedir git add/git commit de um arquivo que o usuário acabou de salvar, EXIGIR o output do bloco de validação e ESPERAR.

⚠️ REGRA S25d — o teste definitivo de "o save pegou" é git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M <arquivo>. Se git status --short vier vazio depois de salvar, o disco é igual ao commitado. O save não pegou.

⚠️ REGRA S25e — ao entregar o conteúdo de um arquivo para colar no editor, entregar SEM cerca markdown envolvendo. Entregar o arquivo inteiro como o único texto da resposta, sem instruções antes/depois.

⚠️ REGRA S26a — no PowerShell 5.1, Invoke-WebRequest -UseBasicParsing devolve resp.Content como STRING, não como byte[]. [System.IO.File]::WriteAllBytes(path, resp.Content) falha com "Não é possível converter o valor... para o tipo System.Byte[]". Para escrever bytes, usar: [System.IO.File]::WriteAllBytes(path, [System.Text.Encoding]::UTF8.GetBytes(resp.Content)) — OK para GPX/CSV/XML (texto UTF-8), ou resp.RawContentStream.CopyTo(fileStream) — preserva bytes crus, ideal para binários (ZIP, imagem). Para inspecionar GPX/XML, evitar escrever arquivo: usar [regex]::Matches(resp.Content, '<time>([^<]+)</time>') direto no Content.

⚠️ REGRA S26b — validar GPX em produção por regex é mais barato que por gpxpy+arquivo temporário. Contar <time> distintos com regex no Content responde a pergunta "o S26 está no ar?" em 3 linhas de PowerShell, sem $env:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>).

⚠️ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Não é bug. Se a primeira validação em prod mostrar o comportamento antigo (S25: todos os <time> iguais), esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, então sim: ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min.

⚠️ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa. Se git status --short mostrar M docs/HANDOFF.md no início da sessão, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro (mensagem docs: handoff da Sessao N), push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0.

⚠️ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir.

⚠️ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios". O handoff pode estar desatualizado (foi escrito com base em memória, não no código).

⚠️ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código. Não investigar como bug.

⚠️ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora. Implementação em web/src/api/activities.ts → _countZipEntries().

⚠️ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior, não "bate com o build local". Manter a checagem por __vite__mapDeps (REGRA S23) + leitura do conteúdo do chunk.

⚠️ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número. Erro no esperado, não no código.

⚠️ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }. Declarar sem inicializar (let entryCount: number;) quando try/catch (ou if/else) cobre todos os caminhos.

⚠️ REGRA S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos" (e "TODOS"). Usar -CaseSensitive ou regex \bTODO\b.

⚠️ REGRA S30b — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos. Contrato: isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; ambos false = cinza (delta 0). Sinal matemático ("+"/"−") e percentual seguem o delta cru (não a semântica de cor).

⚠️ REGRA S30c — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo; a descoberta de código corrige para CIMA. No mobile, SEMPRE pedir Get-ChildItem + arquivos-chave (api.dart, feed_page.dart, activity_detail_page.dart, auth_service.dart) antes de estimar esforço ou travar rota.

⚠️ REGRA S31a (NOVA) — em ambiente Windows sem Developer Mode, flutter pub add <plugin_nativo> instala mas avisa que o build vai falhar por symlink. Building with plugins requires symlink support. Please enable Developer Mode — start ms-settings:developers + ativar. Vale para qualquer plugin com código nativo (file_picker, image_picker, etc). flutter analyze passa sem Developer Mode; flutter run/flutter build não.

⚠️ REGRA S31b (NOVA) — file_picker 13.x removeu FilePicker.platform, FilePickerResult, PlatformFile.size e PlatformFile.bytes. API nova: FilePicker.pickFiles() é estático e retorna List<PlatformFile> direto (vazio = cancelou); PlatformFile.length() (Future<int?>) ou lengthSync() (int?) substituem .size; PlatformFile.readAsBytes() (Future<Uint8List>) substitui .bytes. path continua existindo (String?) mas é null na web. Sempre consultar o changelog antes de usar API de plugin, não a memória. O guia de migração oficial está em https://github.com/miguelpruivo/flutter_file_picker/wiki/Migration-guide.

⚠️ REGRA S31c (NOVA) — quando Select-String do disco mostrar conteúdo antigo depois do save do editor, contornar via WriteAllText no PowerShell imediatamente — não insistir no Ctrl+S. Já rendeu frutos na S31 (editor falhou 3x; WriteAllText pegou na primeira). Sintomas: git status mostra M, mas Select-String do símbolo novo vem vazio; Get-Item mostra LastWriteTime desatualizado; (Get-Content).Count bate com a versão antiga. Procedimento: fechar/reabrir a aba não resolveu → colar via here-string @' ... '@ + [System.IO.File]::WriteAllText(path, $content, [System.Text.UTF8Encoding]::new($false)) + verificar com 3 Select-String (símbolo novo ≥ 2, termo antigo = 0, tamanho ~esperado). Causa provável: VS Code "hot exit" restaurando buffer antigo, ou save cancelado silenciosamente.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (166 passed ao fim da S31). Container de teste rumo_postgres_test na porta 5433.

⚠️ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).
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
│   │         + test_export_bulk + test_follow + test_like + test_stats)
│   ├── _scratch/
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/ (activity.dart, activity_track.dart, comment.dart)
│   │   ├── pages/ (activity_detail_page.dart, feed_page.dart, login_page.dart, upload_page.dart)  ← upload_page.dart é NOVO na S31
│   │   ├── services/ (api.dart, auth_service.dart)
│   │   └── widgets/ (activity_map.dart, like_button.dart)
│   ├── pubspec.yaml (agora com file_picker: ^13.3.3)
│   └── pubspec.lock
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 6 atividades, 26.443 m. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, tipo walk, 60 pontos, ~10 min de duração) usada para validar o S26.

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).
Acordos de trabalho (válidos em todas as sessões — reforçados na S21/S22/S23/S24/S25/S26/S27/S28/S29/S30/S31)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

    UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

    HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.

    PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes. Reflete o estado ao fim da sessão, depois do que foi entregue e validado.

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

    Entregar conteúdo de arquivo para colar sem cerca markdown — arquivo inteiro como único texto (S25e).

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

Processo que o usuário elogiou na S21–S31 (para manter)

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

S26 (GPX com <time> por ponto): to_gpx(activity, coordinates, raw_track_points=None) ganhou o 3º parâmetro opcional. Quando raw_track_points existe e tem o MESMO comprimento de coordinates, cada <trkpt> recebe <time> com o timestamp real do ponto (unix epoch → ISO 8601 UTC). Caso contrário, fallback para started_at em todos os pontos (comportamento S25). Contrato HTTP inalterado — só o corpo do GPX ganhou <time> reais.

S31 — upload mobile (NOVO):

    POST /activities/upload — endpoint já existia desde S12, consumido agora pelo mobile. Auth Bearer JWT. multipart/form-data com file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120), activity_type (opcional), description (opcional). Sucesso: 201 com ActivityResponse. Erro: 422 (HTTPValidationError), provavelmente 429 (slowapi, rate limit 10/h por IP — não testado explicitamente), 401 (token). Parse síncrono, ~1–3s por arquivo (por isso o rate limit).

    mobile/lib/services/api.dart — uploadActivity({File? file, List<int>? bytes, String? filename, String? title, String? activityType, String? description, String? token}) → Future<Activity>. Usa http.MultipartRequest (NÃO passa pelo _send, que é JSON-only). MultipartFile.fromPath quando file != null, MultipartFile.fromBytes quando só bytes != null (web). Timeout 60s. 201 → Activity.fromJson. Reusa _extractMessage para .detail.

    mobile/lib/pages/upload_page.dart (NOVO) — StatefulWidget, ~239 linhas. Estado: File? _file, Uint8List? _bytes, String? _fileName, int? _fileSize, _titleCtrl, _descCtrl, _submitting. _pickFile() → FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['gpx','fit']) → List<PlatformFile> (vazio = cancelou). Se path != null → File; senão → readAsBytes() → _bytes. Valida extensão (defesa dupla) e tamanho ≤ 20 MB. _submit() → auth.api.uploadActivity(...) → SnackBar verde + context.pop(true). _showError para ApiException (mostra .message = .detail do backend). UI: AppBar('Enviar atividade'), ListView com OutlinedButton.icon('Selecionar arquivo'), preview (Card com nome + tamanho formatado), TextField título (opcional, maxLength: 120), TextField descrição (opcional, maxLines: 3), FilledButton.icon('Enviar') (desabilitado se sem arquivo ou _submitting, com CircularProgressIndicator dentro quando enviando). activity_type fora da UI na S31 — o backend infere pelo arquivo; dropdown fica para sessão futura se fizer falta.

    mobile/lib/main.dart — rota /upload adicionada (entre /feed e /activity/:id), builder: (_, _) => UploadPage(auth: _auth). redirect já protege (não-logado → /login).

    mobile/lib/pages/feed_page.dart — FAB (FloatingActionButton, Icons.upload_file, tooltip 'Enviar atividade', onPressed: _openUpload). _openUpload() → await context.push<bool>('/upload') → se uploaded == true, _load() (recarrega o feed inteiro — upload é evento raro, refresh completo é mais correto que refresh de item).

    mobile/pubspec.yaml — file_picker: ^13.3.3 (adicionado via flutter pub add file_picker, que também mexeu no pubspec.lock com 7 pacotes novos: file_picker, android_file_picker, file_picker_darwin, file_picker_linux, file_picker_platform_interface, file_picker_web, windows_file_picker, cross_file, petitparser, xml, dbus).

S28 (delta de tempo/calorias no drill-down por tipo): escopo real descoberto via Fase 1 (6 arquivos + lib/format.ts). Schema/serviço/StatsCards já faziam os 5 campos; único gap era PreviousDelta mostrar 3 de 5. 1 arquivo, 24 inserções + 1 deleção em web/src/pages/ProfilePage.tsx. Commit ba43fad.

S29 (detecção de ZIP vazio no client):

    web/src/api/activities.ts — downloadActivityExportBulk devolve { entryCount: number }. Helper _countZipEntries(arrayBuffer) lê EOCD (assinatura 0x06054b50 LE), varre últimos 22+65535 bytes, totalEntries em offset 10 (uint16 LE). Fail-open: -1 em qualquer falha. Sem jszip.

    web/src/pages/ProfilePage.tsx — handleExportAll consome { entryCount }: 0 → "Nenhuma atividade no período — ZIP vazio." (âmbar); 1 → "Download iniciado (1 atividade)." (verde); ≥2 → "Download iniciado (N atividades)." (verde); -1 → "Download iniciado." (verde, genérico). Tipo novo ExportInfo = { text: string; kind: "success" | "empty" }.

S30 (delta de Pace com semântica correta): DeltaLine ganhou lowerIsBetter?: boolean (default false). Quando true: isGood = delta < 0, isBad = delta > 0; sinal/percentual seguem delta cru. PreviousDelta ganhou 1 linha de pace condicionada a PACE_TYPES.has(item.activity_type) (run/walk/hike), com formatter = formatPace e lowerIsBetter = true. 1 arquivo. Commit ffaaea0.
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

    Venv backend: D:\Rumo\backend\venv (ativa com .\venv\Scripts\Activate.ps1 — UM ponto, não dois)

    Deps novas em S31: file_picker: ^13.3.3 (mobile).

Git (estado ao fim da Sessão 31)
text

71a00d4 (HEAD -> main, origin/main) feat(mobile): upload GPX/FIT no feed (Sessao 31)   ← fix: bytes/web
a83ed82 feat(mobile): upload GPX/FIT no feed (Sessao 31)                                ← versão inicial
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

Sobre o commit duplicado: a83ed82 (feito pelo usuário/VS Code antes de eu perceber) adicionou os 6 arquivos na versão inicial. 71a00d4 refinou só upload_page.dart (+77/−36) e api.dart (+29/−2) para a versão final com _bytes/fromBytes. Working tree limpo, hash do disco == hash do HEAD para upload_page.dart (8b9ed8c...). Não vale rebase/squash — o histórico fica legível.

Pendente: docs/HANDOFF.md da S31 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 31.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 31
3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short veio VAZIO na abertura — o commit do handoff S30 (3a154b1) já estava feito ANTES do início da S31 (padrão S29/S30: handoff commitado entre sessões). HEAD == origin/main == 3a154b1.

    Log/status. git status: working tree limpo. git log confirma 3a154b1 no topo.

    Build/lint/analyze. npm run build: 824 modules, 6.02s, hashes idênticos ao build da S30 (ProfilePage-pXfRJdbD.js 21.54 kB, index-DvGu4786.js 436.15 kB, ActivityDetailPage-C1KScSo5.js 11.38 kB, SearchPage-Bpu7TeFA.js 4.16 kB, RouteMap-CXXXy7Mv.js 2.41 kB, leaflet-Bw7RoR_1.js 163.60 kB, recharts-DI5KUTLO.js 351.26 kB). npm run lint: limpo. flutter analyze: No issues found! (102s, cache frio).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test subiu do zero. pg_isready respondeu no response na 1ª tentativa (timing), accepting connections na 2ª. pytest -q: 166 passed in 76.66s. ruff check .: All checks passed!.

    Prod backend (S26). Login OK. Atividade 01a1b36a-0951-71e8-9044-c55c71558441: 60 pontos com <time>, 60 distintos. Primeiro 2026-11-06T21:30:33Z (sem microssegundos, diferente da S30 que tinha .931332Z), último 2026-11-06T21:40:23Z. S26 NO AR confirmado via regex no Content. Observação nova: o Render agora retorna timestamps truncados em segundos — provavelmente _trkpt_time truncando ou gpxpy diferente. Contrato intacto (60/60 distintos, primeiro/último batem). Não é bug — registro em dívidas.

    Prod frontend (Vercel). index servido: /assets/index-CJjOEm0V.js (idêntico ao da S30). __vite__mapDeps: ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, leaflet-Bw7RoR_1.js, recharts-DI5KUTLO.js. Tríade de "S30 no ar" confirmada. Sanity semântico: baixado ProfilePage-Cy6s98Hl.js, 12 ocorrências de Pace|lower → código da S30 no bundle.

3.2 Fase 1 — descoberta para upload mobile

Pedi 5 arquivos + 1 estrutura, com motivo declarado:

    openapi.json do upload — POST /activities/upload confirmado. Schema Body_upload_activity_activities_upload_post: file (binary, obrigatório), title (string, maxLength 120, nullable), activity_type (string, nullable), description (string, nullable). Resposta 201 → ActivityResponse, 422 → HTTPValidationError. Rate limit 10/h por IP descoberto no description. Auth OAuth2PasswordBearer. Parse síncrono (~1–3s).

    pubspec.yaml — http ^1.6.0, flutter_secure_storage ^11.2.0, go_router ^18.1.2, flutter_map ^8.3.2, latlong2 ^0.10.1. Sem file_picker — dep nova necessária.

    lib/main.dart — 3 rotas (/login, /feed, /activity/:id), GoRouter com refreshListenable: _auth, redirect limpo.

    lib/services/api.dart — ApiClient tem login, get, post, delete, listComments, createComment, deleteComment, getActivityTrack. _send é JSON-only. _extractMessage pega .detail. _decode trata UTF-8. Sem upload, sem /activities, sem /users, sem /stats, sem /follow, sem /notifications, sem /search, sem /export, sem /auth/me — gap do handoff S30 confirmado.

    lib/services/auth_service.dart — token getter exposto, currentUserId via JWT decode local, _storage secure. Sem refresh token, sem logout em 401.

    lib/pages/feed_page.dart — sem FAB. _load() recarrega o feed. _openDetail() já tem o padrão await push + refresh reusável. AppBar só com logout.

    Get-ChildItem lib — 11 arquivos .dart, sem upload, sem perfil, sem stats, sem settings. Nenhuma surpresa.

3.3 Fase 2 — contrato travado

Ver Seção 1 (TL;DR). Contrato completo: endpoint, schema, métodos, UI, validação, mensagens de erro, o que fica fora da S31.
3.4 Fase 3 — entrega incremental (5 arquivos)

    lib/services/api.dart — uploadActivity com File? file + List<int>? bytes + String? filename. MultipartFile.fromPath/fromBytes. analyze verde.

    lib/pages/upload_page.dart (novo) — primeira versão usava FilePicker.platform.pickFiles e PlatformFile.size/.bytes. Erro do analyzer (undefined_getter para platform, depois size/bytes). Corrigido para FilePicker.pickFiles (estático) + length() + readAsBytes(). REGRA S31b registrada.

    lib/main.dart — rota /upload. analyze verde.

    lib/pages/feed_page.dart — FAB + _openUpload. analyze verde.

    pubspec.yaml — file_picker: ^13.3.3 (via flutter pub add).

3.5 Fase 3.5 — verificar save + commit (com reviravolta)

Bloco de verificação S25c/S25d rodado: 6 arquivos M/??, hash do disco ≠ HEAD nos 4 .dart, zero TODO/FIXME, pubspec.lock com 7 pacotes novos. Tudo verde.

Problema descoberto no teste manual: file_picker na web retorna path == null (navegador não tem filesystem), mas readAsBytes() funciona (245708 bytes lidos). O código original (if (path == null) { _showError(...); return; }) rejeitava o arquivo. Correção: aceitar bytes quando path == null, tanto no api.dart (MultipartFile.fromBytes) quanto no upload_page.dart (Uint8List? _bytes).

Segundo problema (save do editor): o upload_page.dart corrigido não foi salvo pelo editor 3 vezes consecutivas — Select-String "_bytes" = 0, debugPrint = 8, LastWriteTime desatualizado. Contornado com WriteAllText no PowerShell (REGRA S31c). Depois do WriteAllText: _bytes = 7, debugPrint = 0, dart:typed_data = 1, 239 linhas. Save pegou.

Terceiro problema (commit duplicado): o usuário/VS Code commitou a83ed82 com a versão inicial (6 arquivos, 414 insertions) em algum ponto que eu não vi. Depois do WriteAllText, o commit 71a00d4 refinou só upload_page.dart (+77/−36) e api.dart (+29/−2). Estado final íntegro — hash do disco == hash do HEAD (8b9ed8c...), _bytes = 7 no HEAD, debugPrint = 0 no HEAD. Não vale rebase.
3.6 Fase 4 — validação

    flutter analyze: No issues found! (4.5s, cache quente).

    flutter run no Chrome (web) — não em Android.

    Teste manual: FAB → Selecionar arquivo → escolhe .gpx → preview aparece (nome + tamanho) → Enviar → SnackBar verde "Atividade enviada: …" → volta pro feed → feed recarrega com a nova atividade. Validado de ponta a ponta contra o backend Render.

O que NÃO foi validado:

    Upload em Android físico/emulador — o caminho File(path) do FilePicker no Android não foi exercitado. O readAsBytes() cobriu (web). No Android, path costuma vir preenchido (o plugin copia pra cache), então File(path) deve funcionar — mas não foi testado.

    Erro 429 (rate limit) — não testado explicitamente. Se o backend devolver 429 com .detail legível, a UI mostra; se não, mostra "Erro 429". Anotado como oportunidade.

    Erro 422 (validação) — não testado. A UI mostra .detail do FastAPI.

    Arquivo > 20 MB — a validação client-side existe, não foi exercitada.

3.7 Observações / bugs encontrados

    setState() called after dispose() no feed_page.dart linha 51 — bug pré-existente, cosmético (só aparece em debug). Aparece quando o _load() do feed ainda está em voo e a tela é desmontada (ex.: login → feed → abrir upload rápido → voltar). Não bloqueia o upload. Oportunidade para S32: if (!mounted) return; antes do setState no catch do _load. Não corrigido na S31 (escopo).

    Timestamps do GPX em prod sem microssegundos (S26) — primeiro 2026-11-06T21:30:33Z (era .931332Z na S30). Contrato intacto. Provável _trkpt_time truncando ou gpxpy diferente. Anotado em dívidas.

    flutter_01.png — screenshot de teste que apareceu em D:\Rumo\mobile\, removido antes do commit (Remove-Item).

3.8 Resultado da suíte (S31)

    pytest -q → 166 passed (nenhuma mudança backend — nenhum teste novo).

    ruff check . → All checks passed!.

    npm run build → 824 modules (web inalterado).

    npm run lint → limpo (web inalterado).

    flutter analyze → No issues found! (mobile com upload).

3.9 Commits pushados (S31)

    a83ed82 feat(mobile): upload GPX/FIT no feed (Sessao 31) — 6 arquivos, +414/−1 (versão inicial, feita pelo usuário/VS Code).

    71a00d4 feat(mobile): upload GPX/FIT no feed (Sessao 31) — 2 arquivos, +70/−36 (fix: _bytes/fromBytes para web).

Pendente: docs: handoff da Sessao 31 (este arquivo).
SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT). Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota". Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { ..., bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL.

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21. Permissão: dono OU seguidor do dono. Caso contrário, 404. format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id><type>.csv". 1 header + 1 linha. Funciona com/sem rota. format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…"><time>…</time></trkpt>.... S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. ISO 8601 UTC. Exige rota → 404 "Atividade não possui rota" se route IS NULL. format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22. Auth: self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto. format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota). Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

POST /activities/upload (auth: Bearer JWT) — S31 (mobile). multipart/form-data:

    file (obrigatório, string/binary, .gpx ou .fit)

    title (opcional, string, maxLength: 120, nullable)

    activity_type (opcional, string, nullable — enum do backend, não documentado no openapi; mobile NÃO envia na S31)

    description (opcional, string, nullable)

Sucesso: 201 com ActivityResponse. Erro: 422 HTTPValidationError (.detail já tratado pelo _extractMessage do mobile). Rate limit: 10/hora por IP (slowapi; provavelmente 429 — não testado explicitamente). Parse síncrono, ~1–3s por arquivo (por isso o limite). Tamanho máximo não declarado no schema — o mobile usa 20 MB client-side (mesmo do web); o backend rejeita se passar (413/422 com .detail).

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.

GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.

GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.

GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5 da janela de comparação. period/compare inválidos → 422. previous null para period="all" ou tipo ausente na janela. S30: NÃO inclui avg_pace_s_per_km em nenhum dos shapes — pace é sempre derivado no front (computePace).

Janelas (S17/S18/S20):
period	compare	janela
all	qualquer	null
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide — documentado em teste)

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404.

GET /auth/me — identidade do usuário logado (NÃO é /users/me).
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–31 commitadas e pushadas. HEAD == origin/main == 71a00d4. Working tree limpo (após a83ed82 + 71a00d4).

Pendente: este handoff.

Primeira ação da Sessão 32 (REGRA S27a — handoff primeiro)
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 31"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 31 no topo, working tree limpo.
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 32 — primeira ação] Abrir PowerShell via Win+R → powershell

NÃO abrir de dentro do VS Code / Windows Terminal.
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 31"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 32 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 32 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432

Se o prompt já mostra (venv), PULE a linha abaixo.
powershell

.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .

Esperado: 166 passed, ruff limpo, container Up (healthy).
[Sessão 32 — primeira ação] Detecção de versão em produção (front — Vercel)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24). ⚠️ REGRA S29b: o hash servido pelo Vercel não bate com o build local. O sinal de "novo no ar" é o hash mudou vs sessão anterior.
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"

$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|ProfilePage|SearchPage)-[A-Za-z0-9_-]+\.js'

Esperado no estado atual (S31): web inalterado desde S30 — index-CJjOEm0V.js com ProfilePage-Cy6s98Hl.js, ActivityDetailPage-DOBuid_4.js, SearchPage-D6UpMvrw.js. RouteMap fora do __vite__mapDeps do index — lazy.
[Sessão 32 — sanity opcional] Validar S30 semanticamente
powershell

$chunkUrl = "https://rumo-wheat.vercel.app/assets/ProfilePage-Cy6s98Hl.js"
$chunk = Invoke-WebRequest -Uri $chunkUrl -UseBasicParsing
$hits = ([regex]::Matches($chunk.Content, 'Pace|lower')).Count
Write-Host "ocorrencias de Pace/lower no chunk: $hits"

Esperado: 12. Se 0, o sanity definitivo é abrir o navegador.
Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Detecção de versão em produção (backend S26 — GPX com <time> por ponto)

⚠️ REGRA S26a/S26b: NÃO usar WriteAllBytes(path, resp.Content). Usar regex direto no Content.
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }

$aid = "01a1b36a-0951-71e8-9044-c55c71558441"
$resp = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$aid/export?format=gpx" -Headers $h -UseBasicParsing

$times = [regex]::Matches($resp.Content, '<time>([^<]+)</time>') | ForEach-Object { $_.Groups[1].Value }
$n = $times.Count
$distinct = ($times | Sort-Object -Unique).Count
Write-Host "pontos com <time>: $n"
Write-Host "<time> distintos: $distinct"
if ($n -gt 0) {
    Write-Host "primeiro: $($times[0])"
    Write-Host "ultimo:   $($times[-1])"
}
if ($distinct -le 1 -and $n -gt 1) {
    Write-Host "S25 AINDA NO AR (todos iguais)."
} elseif ($distinct -ge $n - 1) {
    Write-Host "S26 NO AR (timestamps distintos por ponto)."
} else {
    Write-Host "ATENCAO: apenas $distinct/$n distintos."
}

Esperado agora (S26 no ar): 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, ultimo 2026-11-06T21:40:23Z (sem microssegundos desde a S31).
Teste real do ZIP (auth) — bytes crus via RawContentStream (REGRA S26a)
powershell

Add-Type -AssemblyName System.IO.Compression.FileSystem
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$r = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/export?format=csv" -Headers $h -UseBasicParsing
Write-Host "CSV default: $($r.StatusCode) $($r.Headers['Content-Type'])"
$tmp = [System.IO.Path]::GetTempFileName()
$fs = [System.IO.File]::OpenWrite($tmp)
$r.RawContentStream.Position = 0
$r.RawContentStream.CopyTo($fs)
$fs.Close()
$zip = [System.IO.Compression.ZipFile]::OpenRead($tmp)
Write-Host "entries: $($zip.Entries.Count)"
$zip.Dispose()

Stats de terceiros (S19/S20)
powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

Ruff (backend)
powershell

cd D:\Rumo\backend
# Se o prompt já mostra (venv), pule:
.\venv\Scripts\Activate.ps1
ruff check .

Recuperação de arquivo corrompido (lição S21)
powershell

cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>
# Se o último commit for anterior à mudança quebrada:
git restore <arquivo>
# Se a versão quebrada JÁ foi commitada:
git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22 + S26c)
powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"

Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy.

Se rota no ar mas retorna 422, ver o BODY do erro:
powershell

try {
    Invoke-WebRequest -Uri "<url>" -Headers $h -UseBasicParsing | Out-Null
} catch {
    $resp = $_.Exception.Response
    $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
    Write-Host "STATUS $($resp.StatusCode)"
    Write-Host ($reader.ReadToEnd())
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b)
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+\.js'

Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. Para confirmar conteúdo: baixar o chunk novo e Select-String do símbolo/helper que mudou.

⚠️ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.
Diagnóstico de save de arquivo (lição S25 — mantido)

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
Write-Host "=== [6] hash do HEAD ==="
git rev-parse HEAD:<arquivo>

Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou.
Se [5] != [6] e [4] mostra ' M' → save pegou, pode commitar.

Nota S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS" (Select-String é case-insensitive). Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b.
Contornar editor que não salva (REGRA S31c — NOVO)

Se Select-String do disco mostrar conteúdo antigo depois do save do editor:
powershell

cd D:\Rumo\mobile   # ou o diretório do arquivo
$content = @'
// conteúdo completo do arquivo aqui
'@
[System.IO.File]::WriteAllText("$PWD\caminho\do\arquivo.dart", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "_bytes: $((Select-String -Path caminho\do\arquivo.dart -Pattern '_bytes' -SimpleMatch | Measure-Object).Count) (esperado >=2)"
Write-Host "debugPrint: $((Select-String -Path caminho\do\arquivo.dart -Pattern 'debugPrint' -SimpleMatch | Measure-Object).Count) (esperado 0)"

O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.
Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)

ERRADO — Content é string, não byte[]:
powershell

[System.IO.File]::WriteAllBytes(path, $resp.Content)

CERTO (texto UTF-8):
powershell

[System.IO.File]::WriteAllBytes(path, [System.Text.Encoding]::UTF8.GetBytes($resp.Content))

CERTO (bytes crus — ZIP, imagem):
powershell

$fs = [System.IO.File]::OpenWrite($path)
$resp.RawContentStream.Position = 0
$resp.RawContentStream.CopyTo($fs)
$fs.Close()

MELHOR para inspecionar GPX — sem arquivo, regex no Content:
powershell

$times = [regex]::Matches($resp.Content, '<time>([^<]+)</time>') | ForEach-Object { $_.Groups[1].Value }

Verificar upload mobile em prod (S31 — NOVO)

O "prod" do mobile é o build rodando em dispositivo, consumindo o backend Render. Para validar:
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

E rodar o app:
powershell

& "C:\Users\nasci\flutter\bin\flutter.bat" run

Escolher device (Chrome para web, Android para emulador/aparelho). Testar o fluxo: FAB → Selecionar arquivo → Enviar. O backend Render responde 201 com ActivityResponse.

⚠️ Developer Mode: se flutter run falhar com erro de symlink (Building with plugins requires symlink support), rodar start ms-settings:developers e ativar (REGRA S31a).
Verificar se file_picker está no lock (S31 — NOVO)
powershell

cd D:\Rumo\mobile
Select-String -Path pubspec.lock -Pattern "file_picker" -SimpleMatch

Esperado: 7+ linhas (android_file_picker, file_picker, file_picker_darwin, file_picker_linux, file_picker_platform_interface, file_picker_web, windows_file_picker).
SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.
(FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.
(FECHADA na S25) ~~RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy()~~ — RouteMap agora é lazy no ActivityDetailPage.
(FECHADA na S26) ~~to_gpx não emite <time> por <trkpt>~~ — agora emite quando raw_track_points está disponível e alinhado.
(FECHADA na S28) ~~PreviousDelta mostrava só 3 das 5 métricas (Ativ./Dist./Elev.), apesar de StatsByTypePreviousItem já ter total_duration_s e total_calories~~ — PreviousDelta agora renderiza as 5.
(FECHADA na S29) ~~downloadActivityExportBulk retornava void; handleExportAll sempre mostrava "Download iniciado." mesmo com ZIP vazio~~ — agora devolve { entryCount } e o feedback distingue "success" de "empty".
(FECHADA na S30) ~~Delta de Pace no PreviousDelta está fora de escopo deliberadamente~~ — DeltaLine ganhou lowerIsBetter e PreviousDelta ganhou a linha Pace nos PACE_TYPES.
(FECHADA na S31) ~~Mobile não tem upload GPX/FIT (gap funcional nº 1)~~ — POST /activities/upload consumido pelo ApiClient.uploadActivity + UploadPage + FAB no feed. Validado em Chrome/web.

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
(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Já coberto por teste.
(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. É renomeação de referência cruzada no __vite__mapDeps, não regressão (REGRA S28b).
(CONHECIDA — Sessão 29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Se um dia fizer falta, o sentinel 0xFFFF já sinaliza falha (retorna -1, fail-open).
(CONHECIDA — Sessão 29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs). Ganho: caller recebe entryCount. Se o export virar pesado (centenas de MB), trocar por leitura streaming do rodapé via blob.slice(-22-65535, blob.size).
(CONHECIDA — Sessão 29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.
(CONHECIDA — Sessão 30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX: pedal usa velocidade, natação usa ritmo/100m. Se um dia alguém quiser pace em cycle, é só relaxar PACE_TYPES — o DeltaLine já tem lowerIsBetter pronto.
(CONHECIDA — Sessão 30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0 (computePace(item) ?? 0), resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero (delta = 0).
(CONHECIDA — Sessão 31) setState() called after dispose() no feed_page.dart linha 51 — bug pré-existente, cosmético. Aparece quando o _load() do feed ainda está em voo e a tela é desmontada. Oportunidade para S32: if (!mounted) return; antes do setState no catch do _load. Não corrigido na S31 (escopo).
(CONHECIDA — Sessão 31) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → ApiException; o app NÃO faz logout automático. Melhoria para "mundo real", não MVP.
(CONHECIDA — Sessão 31) Mobile: uploadActivity valida path == null → readAsBytes(), cobre web. No Android, path costuma vir preenchido (o plugin copia pra cache) e o File(path) deve funcionar — não testado em dispositivo físico. Testar na S32+.
(CONHECIDA — Sessão 31) Mobile: rate limit 10/h do /activities/upload não foi testado explicitamente (429). Se o backend devolver .detail legível, a UI mostra; se não, mostra "Erro 429". Oportunidade: UI dedicada com cooldown visual.
(CONHECIDA — Sessão 31) Mobile: activity_type fora da UI do upload na S31 — o backend infere pelo arquivo. Se precisar de override manual, é um dropdown em sessão futura.
(CONHECIDA — Sessão 31) Mobile: upload_page.dart tem ~239 linhas. debugPrint removido após diagnóstico. _clearFile() extraído. hasFile derivado de _file != null || _bytes != null.
(CONHECIDA — Sessão 31) O commit a83ed82 foi feito pelo usuário/VS Code com a versão inicial; 71a00d4 refinou upload_page.dart e api.dart. Não vale rebase/squash — histórico legível.
(CONHECIDA — Sessão 31) file_picker 13.3.3 trouxe 11 deps novas (android_file_picker, cross_file, dbus, file_picker_darwin, file_picker_linux, file_picker_platform_interface, file_picker_web, petitparser, windows_file_picker, xml + file_picker). Todas no pubspec.lock.

(Oportunidade — S18–S31) Semântica do delta é NEUTRA. Sem "melhor/pior". Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor. Decisão de UX mantida.
(Oportunidade — S19–S31) Stats públicas só quando viewer segue o alvo.
(Oportunidade — S22–S31) Export em lote no mobile (paridade com web S21/S22/S29).
(Oportunidade — S30) Testes unitários do DeltaLine (não há hoje; é puro, dá pra testar com 4 casos e sem React Testing Library, se algum dia valer a pena).
(Oportunidade — S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.
(Oportunidade — S31) Mobile: tela de perfil, stats, notificações, busca, export — o plano completo está na Seção 8.
(Oportunidade — S31) Corrigir o setState() after dispose no feed_page.dart (REGRA S31).
(Oportunidade — S31) Testar upload em Android físico/emulador (o path do Android e o File(path) não foram exercitados).
(Oportunidade — S31) UI dedicada para 429 (rate limit) com cooldown visual.
(Oportunidade — S31) activity_type como dropdown opcional na UploadPage.
SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 32 e além)

Sessão 31 fechada. Upload GPX/FIT no mobile funcionando (Chrome/web validado). Mobile subiu de ~42% para ~48% de cobertura. Backend/web inalterados.

Primeira ação obrigatória da Sessão 32 (REGRA S27a)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 32 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 31, push, confirmar HEAD == origin/main.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (docker ps -a, pg_isready, pytest -q → 166, ruff check).

    Detecção de versão em produção (front Vercel + back Render S26 — GPX com <time> por ponto).

Rota travada para a Sessão 32: Tela de Perfil Próprio + "Minhas Atividades"

Este é o próximo divisor de águas: sem perfil, o usuário não vê o que enviou (só o feed geral). Com perfil, o ciclo se fecha — o usuário vê suas atividades, seus stats, e gerencia o que enviou.

Contrato preliminar (a confirmar na Fase 1 da S32, pedindo api.dart, feed_page.dart, activity.dart, e o openapi.json das rotas /activities e /users/{id}):

    lib/services/api.dart — adicionar:

        Future<List<Activity>> listActivities({String? userId, int limit, int offset, String? token}) → GET /activities?user_id=&limit=&offset=

        Future<User> getUser(String userId, {String? token}) → GET /users/{user_id}

    lib/models/user.dart (NOVO) — User com id, username, email, avatar_url, created_at. Pedir o schema antes de codar (REGRA S21).

    lib/pages/profile_page.dart (NOVO) — StatefulWidget com AuthService auth. AppBar('Perfil') + ListView com:

        Cabeçalho: avatar + username + email (do /auth/me ou /users/{currentUserId} — decidir na Fase 1).

        Stats resumidos: GET /users/{currentUserId}/stats/summary (distância total, duração, calorias, atividades). Card com 3–4 métricas.

        "Minhas atividades": lista paginada de listActivities(userId: currentUserId). Cada item reusa o layout do _ActivityCard do FeedPage (ou extrai um widget compartilhado — decidir).

        Botão de logout (ou mantém no FeedPage só).

    lib/main.dart — adicionar rota /profile. O FeedPage pode ganhar um IconButton no AppBar (ícone de pessoa) além do logout, ou mover o logout para o perfil. Decisão de UX a travar na S32: perfil como destino do AppBar vs. bottom nav (Material 3). Recomendação: bottom nav de 2 abas (Feed / Perfil) — o app começa a ter "áreas" e o bottom nav é o padrão Material 3 para isso. Alternativa mais simples: IconButton(Icons.person) no AppBar do feed. Recomendação: bottom nav (mais escalável — Upload não vira aba, mas Feed/Perfil sim; Upload continua como FAB no feed).

Escopo NÃO incluso na S32:

    Stats agregados completos (weekly/monthly/by-type com delta) — fica para S33 (o StatsCards do detalhe já mostra stats por atividade; o perfil mostra o summary).

    Follow/seguidores — S33+.

    Notificações — S34+.

    Busca de usuários — S33+.

    Export no mobile — S34+.

    Corrigir o setState() after dispose — pequeno, pode entrar como "fix" no início da S32 se o usuário quiser. Recomendação: incluir como "fix" no início da S32 (é 2 linhas, e o bug vai aparecer de novo quando a navegação entre abas ficar mais complexa).

Escolha para a Sessão 33 (a decidir depois da S32)

    OPÇÃO 1 — Stats agregados completos no perfil (weekly/monthly/by-type com delta, paridade com web S18/S20/S28/S30).

    OPÇÃO 2 — Perfil de terceiro (tocar no avatar/nome no feed/detalhe → perfil público com stats, follow/unfollow).

    OPÇÃO 3 — Busca de usuários.

    OPÇÃO 4 — Export no mobile (paridade com web S21/S22/S29).

    OPÇÃO 5 — Build de release + ícone + splash + política de privacidade + exclusão de conta (bloqueadores de loja).

Recomendação: S32 = perfil próprio + minhas atividades (fecha o ciclo do upload). S33 = stats agregados completos no perfil (paridade com web). S34 = perfil de terceiro + follow. S35 = busca. S36 = export. S37 = build de release + loja. ~6–8 sessões para o MVP em loja.

Recomendação final para a Sessão 32

Rodar Fase 0 completa (com handoff S31 commitado primeiro). Se tudo verde, começar o perfil próprio + minhas atividades seguindo o contrato acima — entrega incremental (api.dart + user.dart → profile_page.dart → main.dart → feed_page.dart com bottom nav), com flutter analyze entre cada entrega e validação manual (Chrome/web primeiro, Android depois se o Developer Mode estiver ligado).

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 32 neste mesmo formato (seções 0 a 9) + o percentual de prontidão atualizado.
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25 (abertura): reforçou os mesmos acordos. Tolerou 3 tropeços (Select-String mal desenhado, commit sem validação, README com cerca vazando) — sem reclamar, só reportando. Registrei cada um como regra (S25a–S25e).

Na S26 (abertura): reforçou os mesmos acordos. Tolerou 2 tropeços (WriteAllBytes de string, Render demorando >3 min) — sem reclamar. Registrei (S26a–S26c).

Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a. Perguntou "o que você recomenda?" e seguimos a recomendação.

Na S28 (abertura): handoff S27 já estava commitado. Fase 0 limpa. Fase 1 revelou escopo real (1 arquivo, não 6). Entreguei 1 arquivo, validei em produção. Perguntou "sempre o que você recomendar" ao fim e eu recomendei entregar o handoff agora — ele concordou.

Na S29 (abertura): handoff S28 já commitado (padrão virou rotina). Fase 0 limpa. Fase 1 revelou escopo de 2 arquivos (não 3). Entreguei activities.ts, o usuário colou um erro do ESLint no-useless-assignment — corrigi na hora, registrei REGRA S29d. Entreguei ProfilePage.tsx, build verde, commit, push, validação em produção com 4 testes manuais. Ao fim, "tudo como esperado". Recomendei entregar o handoff agora — ele concordou.

Na S30 (abertura): handoff S29 já commitado. Fase 0 limpa. Ao chegar na escolha de rota, o usuário disse "como já mencionado sempre vamos fazer o que você recomendar". Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. Fase 1 revelou escopo MUITO menor. Contrato travado em 1 arquivo. Entrega, build verde, 1 tropeço (erro de contagem "5x vs 6x", REGRA S29c), 1 achado colateral (Select-String case-insensitive — REGRA S30a), commit, push, Vercel redeployou.

Em seguida, o usuário perguntou o % para "mundo real" do app mobile. Recomendei descoberta de código (não estimar de memória). Ele autorizou. Pedi Get-ChildItem + 4 arquivos pivô. Achado: mobile ~42% de cobertura (REGRA S30c). Estimativa revisada: MVP ~9–13 sessões, mundo real ~13–18. Bloqueadores não-código: backend pago, contas de dev, política de privacidade, exclusão de conta.

Ao fim da S30, o usuário pediu o handoff completo. Entreguei.

Na S31 (abertura): handoff S30 já commitado (3a154b1, feito entre sessões). Fase 0 limpa — build/lint/analyze idênticos ao build da S30 (hashes iguais), 166 passed, ruff limpo, S26 no ar (60/60), Vercel servindo index-CJjOEm0V.js com ProfilePage-Cy6s98Hl.js (tríade S30 + sanity: 12 ocorrências de Pace|lower). Fase 1 revelou o contrato real do upload via openapi.json (não da memória): field file, campos opcionais, rate limit 10/h, parse síncrono. Entreguei 5 arquivos incrementalmente. Tropeços da S31: (1) file_picker 13.x mudou a API (FilePicker.platform removido) — o analyzer pegou, corrigi na hora, registrei REGRA S31b; (2) o editor falhou 3 vezes em salvar o upload_page.dart corrigido — Select-String do disco mostrou conteúdo antigo; contornei com WriteAllText no PowerShell, registrei REGRA S31c; (3) o teste manual revelou que na web file_picker retorna path == null mas readAsBytes() funciona — corrigi para aceitar bytes (api.dart + upload_page.dart); (4) commit duplicado (a83ed82 + 71a00d4, mesmo nome) — o usuário/VS Code commitou antes de mim; estado final íntegro, não vale rebase. Validação final: FAB → selecionar .gpx → preview → enviar → SnackBar verde → feed recarrega. Funcionou.

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Pedido para o assistente da S32 (e além): manter o processo da S21–S31. Concretamente:

    Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os 5 arquivos pivô (main.dart, api.dart, auth_service.dart, feed_page.dart, activity_detail_page.dart) antes de estimar.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

    Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c).

    Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local.

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S31 (Seção 0, itens 31a–31c): Windows sem Developer Mode → build de plugin nativo falha por symlink; file_picker 13.x removeu FilePicker.platform/FilePickerResult/.size/.bytes (API estática + length()/readAsBytes()); editor que não salva → contornar via WriteAllText no PowerShell, não insistir no Ctrl+S.

O que funcionou nas S21–S31 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão), disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30), e a consistência em aceitar os erros (API do plugin, contagem, lint, falsos positivos, save do editor) na hora e corrigir/registrar, sem contornar.
ANEXO DO HANDOFF — PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da S31)

    Acordo S31: o percentual é anexo do handoff, entregue no fechamento da sessão, refletindo o estado ao fim da sessão (depois do que foi entregue e validado). Quebrado por camada + consolidado + estimativa de sessões restantes.

Backend — ~92% pronto (inalterado desde S30)
Área	Estado
Auth (login, JWT, /auth/me)	✅ Completo
Upload GPX/FIT (parse, raw_track_points, route PostGIS)	✅ Completo
Feed, atividades, detalhe, busca	✅ Completo
Track (GeoJSON, bbox, n_points)	✅ Completo
Comentários, likes	✅ Completo
Follow + stats públicas com regra de visibilidade	✅ Completo
Stats (summary, weekly, monthly, by-type + compare prev/yoy)	✅ Completo
Export unitário CSV/GPX (S21) + lote ZIP (S22) + GPX com <time> real (S26)	✅ Completo
Testes (166 passed) + ruff limpo	✅ Verde
Notificações	❌ Ausente
Exclusão de conta (LGPD + exigência Apple)	❌ Ausente
Refresh token	❌ Ausente
Deploy pago (Render free dorme em 15 min)	❌ Bloqueador de "mundo real", não de código

Gap backend: ~8% = notificações + exclusão de conta + refresh token + endurecimento para produção.
Web — ~88% pronto (inalterado desde S30)
Área	Estado
Auth, feed, detalhe, busca	✅
Perfil (próprio e de terceiro)	✅
Stats + drill-down por tipo com delta das 5 métricas (S28) + Pace com semântica correta (S30)	✅
Export unitário + lote com detecção de ZIP vazio (S29)	✅
Follow, like, comentários	✅
Responsivo / mobile-first	⚠️ A confirmar
Acessibilidade (ARIA, teclado)	⚠️ Não verificado
Testes de frontend	⚠️ Não há (só build + lint + validação manual em prod)
Notificações, exclusão de conta	❌ Herda o gap do backend
Política de privacidade pública	❌ Ausente

Gap web: ~12% = notificações, exclusão de conta, política de privacidade, responsividade/acessibilidade a confirmar, testes automatizados.
Mobile — ~48% pronto (subiu de ~42% na S30 com o upload)
Área	Estado
Auth (JWT decode local + secure storage)	✅
Feed interativo (like otimista, comentários, pull-to-refresh, paginação)	✅
Detalhe (3 requests paralelas, stats em cards, mapa com track real)	✅
Upload GPX/FIT (S31 — FAB, UploadPage, uploadActivity, validação client-side)	✅ NOVO
Minhas atividades (/activities)	❌
Perfil próprio + perfil de terceiro	❌
Stats agregados no perfil	❌
Follow / seguidores	❌
Notificações	❌
Busca de usuários	❌
Export (unitário + lote)	❌
/auth/me (validação server-side)	❌ (JWT local funciona)
Refresh token / logout em 401	❌
Corrigir setState() after dispose no feed	❌ (bug cosmético)
Testar upload em Android físico	❌ (só web validado)

Gap mobile: ~52% = perfil + minhas atividades + stats + follow + notificações + busca + export + refresh token + fix do setState + teste Android.
Bloqueadores de "mundo real" que não são código (inalterado desde S30)
Item	Custo/impacto
Backend pago (Render Starter + Postgres)	~US$ 14/mês
Conta Apple Developer	US$ 99/ano
Conta Google Play	US$ 25 único
Política de privacidade pública (URL)	Sem isso, Google Play rejeita
Exclusão de conta (LGPD + Apple desde 2022)	Backend + mobile
Consolidado (ponderação por esforço de código restante)

    Pronto em código (backend + web + mobile): ~67% (era ~65% na S30; +2 com o upload mobile).

    Pronto para MVP em loja: ~57% (era ~55% na S30; +2 com upload, mas ainda falta perfil, stats no mobile, política, exclusão).

    Pronto para "mundo real": ~47% (era ~45% na S30; +2 com upload).

Estimativa de sessões restantes (ritmo de 1 feature por sessão)

    MVP em loja: ~7–11 sessões (era ~9–13 na S30; a S31 comeu 1).

        S32: perfil próprio + minhas atividades.

        S33: stats agregados no perfil (paridade web).

        S34: perfil de terceiro + follow.

        S35: busca de usuários.

        S36: export no mobile.

        S37: build de release + ícone + splash + política de privacidade + exclusão de conta.

        S38–S42 (buffer): testes em dispositivo físico, correções, refinos.

    Mundo real: ~11–16 sessões (era ~13–18 na S30; a S31 comeu 1–2).

        +2–3 sessões para backend pago, crash reporting, analytics, refresh token, testes em device real, exclusão de conta de verdade.

Recomendação: seguir o plano da Seção 8 (S32 = perfil próprio + minhas atividades). O mobile é o que puxa o número para baixo — e cada sessão de mobile fecha um gap funcional visível. A S31 tirou o app do modo 100% read-only; a S32 fecha o ciclo (o usuário vê o que enviou).