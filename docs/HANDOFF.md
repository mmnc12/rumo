HANDOFF — Rumo (backend + frontend + mobile) — Sessão 30

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚠️ REGRA S21 — nunca placeholder no código entregue
Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça.

⚠️ REGRA S21 — não adivinhar nomes de símbolos do projeto
Pedir o model/enum/schema antes de referenciar.

⚠️ REGRA S21 — git status antes de qualquer git restore/git checkout
git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>.

⚠️ REGRA S22 — Invoke-WebRequest com -UseBasicParsing
Elimina o prompt de segurança do PS 5.1.

⚠️ REGRA S22 — validar deploy do Render antes de acusar bug no código
Depois de push, checar openapi.json para a rota nova antes de acusar 422/404.

⚠️ REGRA S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele
Nunca procurar "ProfilePage-" direto no HTML.

⚠️ REGRA S24 — Vercel às vezes demora >90 s para o primeiro deploy após push
Se o hash antigo aparecer após 90 s, rodar o teste de novo. Não presumir bug.

⚠️ REGRA S25a — Select-String -SimpleMatch NÃO aceita | como alternância
Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo.

⚠️ REGRA S25b — quando $lines[-1] for suspeito, confirmar com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo único>" antes de concluir
Não dar "OK" nem "corrompido" sem evidência.

⚠️ REGRA S25c — antes de pedir git add/git commit de um arquivo que o usuário acabou de salvar, EXIGIR o output do bloco de validação e ESPERAR

⚠️ REGRA S25d — o teste definitivo de "o save pegou" é git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M <arquivo>
Se git status --short vier vazio depois de salvar, o disco é igual ao commitado. O save não pegou.

⚠️ REGRA S25e — ao entregar o conteúdo de um arquivo para colar no editor, entregar SEM cerca markdown envolvendo
Entregar o arquivo inteiro como o único texto da resposta, sem instruções antes/depois.

⚠️ REGRA S26a — no PowerShell 5.1, Invoke-WebRequest -UseBasicParsing devolve resp.ContentcomoSTRING,na~ocomobyte[][System.IO.File]::WriteAllBytes(path,resp.Content)falhacom"Na~oeˊpossıˊvelconverterovalor...paraotipoSystem.Byte[]".Paraescreverbytes,usar:[System.IO.File]::WriteAllBytes(path,[System.Text.Encoding]::UTF8.GetBytes(resp.Content))—OKparaGPX/CSV/XML(textoUTF−8),ouresp.RawContentStream.CopyTo(fileStream)—preservabytescrus,idealparabinaˊrios(ZIP,imagem).ParainspecionarGPX/XML,evitarescreverarquivo:usar[regex]::Matches(resp.ContentcomoSTRING,na~ocomobyte[][System.IO.File]::WriteAllBytes(path,resp.Content)falhacom"Na~oeˊpossıˊvelconverterovalor...paraotipoSystem.Byte[]".Paraescreverbytes,usar:[System.IO.File]::WriteAllBytes(path,[System.Text.Encoding]::UTF8.GetBytes(resp.Content))—OKparaGPX/CSV/XML(textoUTF−8),ouresp.RawContentStream.CopyTo(fileStream)—preservabytescrus,idealparabinaˊrios(ZIP,imagem).ParainspecionarGPX/XML,evitarescreverarquivo:usar[regex]::Matches(resp.Content, '<time>([^<]+)</time>') direto no Content.

⚠️ REGRA S26b — validar GPX em produção por regex é mais barato que por gpxpy+arquivo temporário
Contar <time> distintos com regex no Content responde a pergunta "o S26 está no ar?" em 3 linhas de PowerShell, sem $env:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>).

⚠️ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push
Não é bug. Se a primeira validação em prod mostrar o comportamento antigo (S25: todos os <time> iguais), esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, então sim: ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min.

⚠️ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa
Se git status --short mostrar M docs/HANDOFF.md no início da sessão, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro (mensagem docs: handoff da Sessao N), push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0. Motivo: se a Fase 0 revelar algo que exija reverter ou reescrever, o handoff precisa estar preservado no histórico — nunca em risco de ser sobrescrito por uma edição no working tree.

⚠️ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend
Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir. Nunca encadear os 4 blocos num só comando e "ver depois" — o diagnóstico fica ambíguo.

⚠️ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios"
Na S28, o handoff S27 descrevia a OPÇÃO 1 como "delta de tempo/calorias nos stats", sugerindo mudança em schema+service+router+testes+ProfilePage. A descoberta real (pedir schemas/stats.py, services/stats_service.py, ProfilePage.tsx, StatsCards.tsx, lib/format.ts) revelou que: schema já tinha os 5 campos, service já calculava os 5 no previous, StatsCards já renderizava os 5, e o único gap era o componente PreviousDelta mostrar 3 de 5. Escopo real: 1 arquivo, 24 linhas. Lição: sempre pedir os arquivos antes de aceitar o escopo do handoff anterior como verdade. O handoff pode estar desatualizado (foi escrito com base em memória, não no código).

⚠️ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código
Na S28, ActivityDetailPage e SearchPage mudaram de hash (J23GpMg5 → BOuCLIUn, CvOmHzdZ → DVVs61sJ) sem nenhuma linha alterada nesses arquivos. Motivo: o __vite__mapDeps do index renumera índices de chunks quando um chunk muda de tamanho. Se o tamanho do chunk é o mesmo e só o hash mudou, é renomeação de referência, não regressão. Não investigar como bug.

⚠️ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora
Para saber quantos arquivos há dentro de um ZIP (export em lote), ler o End Of Central Directory (assinatura 0x06054b50, little-endian). O campo totalEntries está no offset 10 do EOCD, uint16 LE. Varredura de trás pra frente na janela dos últimos 22 + 65535 bytes (comentário variável do EOCD). NÃO lançar em falha: retornar -1 e deixar o caller cair no fallback (fail-open — o download já aconteceu, o usuário não pode ver erro por falha de leitura do ZIP). ZIP64 (totalEntries == 0xFFFF como sentinela) também retorna -1. Não vale adicionar jszip nem lib externa por 30 linhas. Implementação em web/src/api/activities.ts → _countZipEntries().

⚠️ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior, não "bate com o build local"
Na S29, o build local produziu ProfilePage-B2Qr3yxO.js e index-D7SLM8U1.js. O Vercel serviu ProfilePage-B7f6FP9H.js e index-Bb-PiNPP.js. O conteúdo é idêntico (confirmado pela presença dos símbolos minificados ba = downloadActivityExportBulk devolvendo {entryCount:i}, e ya = _countZipEntries com if(e.byteLength<22)return-1;). Não investigar diferença de hash. O sinal forte de "novo no ar" é (a) hash mudou em relação à sessão anterior, (b) __vite__mapDeps aponta pro novo, (c) conteúdo do chunk contém o helper/símbolo novo. Manter a checagem por __vite__mapDeps (REGRA S23) + leitura do conteúdo do chunk.

⚠️ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número
Na S29 eu anunciei "esperado 5x Sessão 29 no arquivo" e o código tinha 4x. Erro no esperado, não no código. Antes de anunciar N, contar no texto que estou entregando. Se errei a contagem, corrigir e explicar — não empurrar.

⚠️ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }
Regra nova do ESLint (versão atual) detecta atribuição inicial inútil quando ambos os ramos sobrescrevem. Declarar sem inicializar (let entryCount: number;) quando try/catch (ou if/else) cobre todos os caminhos. Vale para qualquer "let X = valorDefault; try {...} catch {X = valorDefault}" — o inicializador é sempre inútil.

⚠️ REGRA S30a (NOVA) — Select-String -Pattern "TODO" casa case-insensitive "Todos" (e "TODOS")
No PS 5.1, Select-String é case-insensitive por padrão. Buscar "TODO|FIXME" contra o arquivo após save acusou 3 matches falsos ("Todos" em labels pt-BR, "TODOS" em comentário). Para evitar: usar Select-String -Pattern "TODO|FIXME" -CaseSensitive, ou buscar \bTODO\b com -Pattern "\bTODO\b" (regex aceita \b, sem -SimpleMatch). NÃO é bug do código — é falso positivo do verificador.

⚠️ REGRA S30b (NOVA) — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos
Na S30, o DeltaLine (que pintava "+" = verde = bom) ganhou lowerIsBetter?: boolean (default false) para o pace, onde "+" = vermelho = ruim. Contrato: isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; ambos false = cinza (delta 0). Sinal matemático ("+"/"−") e percentual seguem o delta cru (não a semântica de cor), para que "Pace −0:15 /km (−4%)" em verde seja lido como "ficou 15s mais rápido". Se um dia outro componente ganhar semântica oposta, seguir o mesmo padrão (prop booleana, default preserva comportamento antigo, 4 casos na cabeça).

⚠️ REGRA S30c (NOVA) — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo; a descoberta de código corrige para CIMA
Na S30, o handoff S29 descrevia o mobile como "parado desde S11" com "mapa no detalhe + miniatura no feed, sem drill-down de stats, sem export" — verdade, mas incompleto. A descoberta real (11 arquivos, 3 páginas, feed interativo com like otimista + comentários + pull-to-refresh, detalhe com 3 requests paralelas e stats em cards, auth com decode local de JWT e secure storage) revelou que o mobile está mais adiantado do que o handoff sugeria (~42% de cobertura vs ~30% estimado). Lição: handoff de sessões anteriores sobre o mobile é o mais volátil de todos — SEMPRE pedir Get-ChildItem + arquivos-chave (api.dart, feed_page.dart, activity_detail_page.dart, auth_service.dart) antes de estimar esforço ou travar rota. O gap é normalmente MENOR do que a memória diz, mas em lugares diferentes.

O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (166 passed ao fim da S30). Container de teste rumo_postgres_test na porta 5433.

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
├── mobile/lib/
│ ├── main.dart
│ ├── models/ (activity.dart, activity_track.dart, comment.dart)
│ ├── pages/ (activity_detail_page.dart, feed_page.dart, login_page.dart)
│ ├── services/ (api.dart, auth_service.dart)
│ └── widgets/ (activity_map.dart, like_button.dart)
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 6 atividades, 26.443 m. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, tipo walk, 60 pontos, ~10 min de duração) usada para validar o S26.

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21/S22/S23/S24/S25/S26/S27/S28/S29/S30)

SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.

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

Processo que o usuário elogiou na S21–S30 (para manter)

Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação em produção) → Fase 5 (handoff).

Descoberta antes de codar: pedir arquivos com motivo declarado.

Validação entre cada entrega.

Contrato travado escrito antes de codar.

Commits pequenos e temáticos.

Validação em produção separada da local.

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

S26 (GPX com <time> por ponto):

to_gpx(activity, coordinates, raw_track_points=None) ganhou o 3º parâmetro opcional. Quando raw_track_points existe e tem o MESMO comprimento de coordinates, cada <trkpt> recebe <time> com o timestamp real do ponto (unix epoch → ISO 8601 UTC). Caso contrário, fallback para started_at em todos os pontos (comportamento S25).

export_activity e export_activities_bulk passam activity.raw_track_points — a coluna JSONB activities.raw_track_points já existia desde a criação (populada por parse_gpx/parse_fit como [[lat, lon, ele, unix_ts], ...]); só não era lida no export.

Contrato HTTP inalterado — só o corpo do GPX ganhou <time> reais.

Validado em produção: atividade 01a1b36a-0951-71e8-9044-c55c71558441 retornou 60 <trkpt> com 60 <time> distintos. Primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z (~10 min).

CSV, ZIP, auth, headers, filename: intactos.

S27: sessão SÓ de Fase 0. Nenhuma feature. Handoff S26 commitado como 585839f na abertura.

S28 (delta de tempo/calorias no drill-down por tipo): escopo real descoberto via Fase 1 (6 arquivos + lib/format.ts): schema/serviço/StatsCards já faziam os 5 campos; único gap era PreviousDelta mostrar 3 de 5. 1 arquivo, 24 inserções + 1 deleção em web/src/pages/ProfilePage.tsx. Commit ba43fad.

S29 (detecção de ZIP vazio no client):

ESCOPO REAL descoberto via Fase 1 (3 arquivos: ProfilePage.tsx, activities.ts, client.ts + Get-ChildItem confirmando que NÃO há helper de ZIP no client). O gap era: downloadActivityExportBulk retornava void; handleExportAll sempre mostrava "Download iniciado." mesmo com ZIP vazio.

MUDANÇA EXECUTADA — 2 arquivos:

    web/src/api/activities.ts: downloadActivityExportBulk passou a devolver { entryCount: number }. Helper novo _countZipEntries(arrayBuffer): number lê EOCD do ZIP (assinatura 0x06054b50 LE), varre últimos 22+65535 bytes, totalEntries em offset 10 (uint16 LE). Fail-open: -1 em qualquer falha (ZIP malformado, < 22 bytes, ZIP64 com 0xFFFF sentinel). Sem jszip, sem dependência nova. _triggerDownload continua acontecendo dentro da função.

    web/src/pages/ProfilePage.tsx: handleExportAll consome { entryCount } e decide a mensagem: entryCount === 0 → { text: "Nenhuma atividade no período — ZIP vazio.", kind: "empty" } (âmbar); entryCount === 1 → "Download iniciado (1 atividade)." (verde); entryCount >= 2 → "Download iniciado (N atividades)." (verde); entryCount === -1 (fail-open) → "Download iniciado." (verde, genérico). Tipo novo ExportInfo = { text: string; kind: "success" | "empty" }. exportInfo deixa de ser string | null e vira ExportInfo | null. exportError continua só para erro de rede/HTTP (vermelho). useEffect de auto-limpeza 4s continua, limpando o objeto inteiro.

Bug pego pelo ESLint no-useless-assignment na primeira entrega: let entryCount = -1; try { entryCount = _countZipEntries(...) } catch { entryCount = -1 } — inicializador inútil. Corrigido para let entryCount: number;. Registrada REGRA S29d.

Validação: tsc -b verde, 824 modules, ProfilePage-xtlegScf.js → ProfilePage-B2Qr3yxO.js (21.08 → 21.37 kB, +0.29 kB). npm run lint limpo. Vercel redeployou; ProfilePage-B7f6FP9H.js servido (Vercel reescreve o hash — REGRA S29b); helper _countZipEntries e downloadActivityExportBulk com entryCount confirmados no bundle minificado. 4 testes manuais em produção passaram (ZIP vazio → âmbar; 6 atividades → verde "N atividades"; from > to → vermelho; GPX com 0 rotas → âmbar).

Commit: ca855ee feat(web): detecta ZIP vazio no export em lote (Sessao 29). Push OK. HEAD == origin/main.

S30 (delta de Pace com semântica correta + descoberta mobile):

PARTE A — feature web (delta de Pace):

ESCOPO REAL descoberto via Fase 1 (4 arquivos: ProfilePage.tsx, api/stats.ts, lib/format.ts, types/api.ts). Achado crítico: StatsByTypePrevious (e StatsByTypeItem) NÃO têm avg_pace_s_per_km — pace é sempre derivado (computePace com duration/distance). Isso simplificou o escopo: current pace = computePace(item), previous pace = computePace(item.previous), mesma fórmula, mesma fonte, zero inconsistência.

O gap real era só semântica de cor: DeltaLine pintava delta > 0 como verde. Em pace, delta > 0 significa PIOR (mais segundos/km = mais devagar). Precisava inverter para pace.

MUDANÇA EXECUTADA — 1 arquivo (web/src/pages/ProfilePage.tsx):

    DeltaLine ganhou prop opcional lowerIsBetter?: boolean (default false, preserva o comportamento antigo para as outras 4 métricas). Quando true: isGood = delta < 0 (métrica diminuiu = bom = verde); isBad = delta > 0 (métrica subiu = ruim = vermelho); delta == 0 → cinza. O SINAL matemático ("+"/"−") e o PERCENTUAL seguem o delta cru (não a semântica de cor), para que "Pace −0:15 /km (−4%)" em verde seja lido como "ficou 15s mais rápido".

    PreviousDelta ganhou 1 linha de pace condicionada a PACE_TYPES.has(item.activity_type) (run/walk/hike), com a mesma regra da coluna "Pace médio" da tabela (cycle/swim/other mostram "—"). current = computePace(item) ?? 0; previous = computePace(item.previous) ?? 0 (coalesce para caber no DeltaLine, que aceita só number); formatter = formatPace; lowerIsBetter = true.

O que NÃO mudou: backend, api/stats.ts, lib/format.ts, types/api.ts, StatsCards, coluna "Pace médio", contrato HTTP. Zero migration, zero teste novo.

Validação: tsc -b verde, 824 modules, 3.67s. ProfilePage-B2Qr3yxO.js → ProfilePage-pXfRJdbD.js (21.37 → 21.54 kB, +0.17 kB). ActivityDetailPage/SearchPage/RouteMap mudaram de hash com tamanho IDÊNTICO (REGRA S28b). leaflet/recharts inalterados. npm run lint limpo. Commit ffaaea0, push OK. Vercel redeployou: index-CJjOEm0V.js + ProfilePage-Cy6s98Hl.js (REGRA S29b). __vite__mapDeps aponta pro chunk novo. Tríade de "S30 no ar" confirmada: hash do ProfilePage mudou, hash do index mudou, __vite__mapDeps aponta pro novo.

PARTE B — descoberta mobile (fecha a pergunta "quanto falta pro mundo real?"):

O usuário perguntou o percentual restante para o app mobile estar "pronto para uso real". Pedi Get-ChildItem + 4 arquivos pivô (api.dart, feed_page.dart, activity_detail_page.dart, auth_service.dart). Achado: mobile está em ~42% de cobertura vs web, NÃO os ~30% que o handoff S29 sugeria (REGRA S30c).

O que EXISTE e funciona bem no mobile:

    Auth sólido: AuthService decodifica JWT localmente (currentUserId do claim sub/user_id), persiste com flutter_secure_storage, bootstrap/login/logout com ChangeNotifier que o GoRouter escuta. SEM refresh token.

    ApiClient limpo: baseUrl aponta pro Render. Métodos genéricos get/post/delete, timeout 30s, _extractMessage pega .detail do FastAPI, decode UTF-8.

    Feed interativo: like otimista com rollback, contador de comentários, pull-to-refresh, paginação por offset, navegação pro detalhe, recarrega item ao voltar.

    Detalhe rico: 3 requests paralelas (activity, comments, track) com loading/error/retry independentes. Like, comentários (listar/criar/deletar), stats em cards (distância, duração, pace, calorias, elevação, velocidade), mapa com track real (n_points), getActivityTrack trata 404 = "sem rota" retornando null.

    Modelos: activity, activity_track, comment. Widgets: activity_map (flutter_map + latlong2), like_button.

    main.dart com 3 rotas: /login, /feed, /activity/:id.

    pubspec.yaml: http, flutter_secure_storage, go_router, flutter_map, latlong2. Mais nada.

O que NÃO existe no mobile (confirmado por ausência no ApiClient + Get-ChildItem):

    upload (GPX/FIT) — zero. Não tem multipart, não tem /activities/upload.

    /activities (lista própria) — zero. Só /feed.

    /users/{id} (perfil próprio ou de terceiro) — zero.

    /users/{id}/stats/* — zero.

    /users/{id}/follow — zero.

    /notifications — zero.

    /search (usuários) — zero.

    /activities/{id}/export (unitário) — zero.

    /activities/export (lote) — zero.

    /auth/me — zero (usa JWT local, funciona, mas não valida no backend).

    followers/following — zero.

Estimativa revisada (baseada em código, não memória):

    Cobertura mobile vs web: ~42%.

    MVP para loja: ~9 a 13 sessões (1 feature por sessão, no ritmo S21-S30).

    Mundo real (backend pago, crash reporting, analytics, testes em dispositivo real, refresh token, exclusão de conta): +4 a 5 sessões.

    Total realista: ~13 a 18 sessões.

Bloqueadores de "mundo real" que NÃO são código:

    Backend pago: Render free dorme após 15 min, primeira request demora 30-60s. Starter US7/me^s+PostgresUS7/me^s+PostgresUS 7/mês.

    Contas de dev: Apple US99/ano,GooglePlayUS99/ano,GooglePlayUS 25 único.

    Política de privacidade pública (URL) — sem isso, Google Play rejeita.

    Exclusão de conta (LGPD + exigência Apple desde 2022) — backend + mobile.

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
Deps novas em S30: nenhuma.

Git (estado ao fim da Sessão 30)

ffaaea0 (HEAD -> main, origin/main) feat(web): delta de pace no drill-down por tipo (Sessao 30)
852608c docs: handoff da Sessao 29
ca855ee feat(web): detecta ZIP vazio no export em lote (Sessao 29)
a3268eb docs: handoff da Sessao 28
ba43fad feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28)
db2e224 docs: handoff da Sessao 27
585839f docs: handoff da Sessao 26
15ccccb feat(activities): GPX export com <time> por ponto (Sessao 26)
7bf5bc2 docs: handoff da Sessao 25
4146c3a docs: corrige README (remove instrucoes de sessao por engano)

Pendente: docs/HANDOFF.md da S30 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 30.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 30

3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

Handoff pendente. git status --short veio VAZIO na abertura — o commit do handoff S29 (852608c) já estava feito ANTES do início da S30 (padrão que virou rotina). Confirmação via git --no-pager log --oneline -4: 852608c no topo, ca855ee abaixo, a3268eb, ba43fad. HEAD == origin/main == 852608c.

Log/status. git status: On branch main / up to date / nothing to commit. Working tree limpo.

Build/lint/analyze. npm run build: 824 modules, 4.49s, ProfilePage-B2Qr3yxO.js 21.37 kB, ActivityDetailPage-BnkM7vWD.js 11.38 kB, SearchPage-Bo_sd9zZ.js 4.16 kB, RouteMap-DXm9jXln.js 2.41 kB, leaflet-Bw7RoR_1.js 163.60 kB, recharts-DI5KUTLO.js 351.26 kB, index-D7SLM8U1.js 436.15 kB. npm run lint: limpo. flutter analyze: No issues found (3.4s).

Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test subiu do zero (estava parado — "Up Less than a second (health: starting)"), pg_isready respondeu "no response" na primeira tentativa (timing), depois "accepting connections". pytest -q: 166 passed in 60.16s. ruff check .: All checks passed.

Prod backend (S26). Login OK. Atividade 01a1b36a-0951-71e8-9044-c55c71558441: 60 pontos com <time>, 60 distintos. Primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z. S26 NO AR confirmado via regex no Content.

Prod frontend (Vercel). index servido: /assets/index-Bb-PiNPP.js (idêntico ao S29). _vite__mapDeps: ActivityDetailPage-CK-oqr7.js, ProfilePage-B7f6FP9H.js, SearchPage-CC8JlqWE.js, leaflet-, recharts-. RouteMap fora do mapDeps — lazy. Bundle confirmou ba = downloadActivityExportBulk devolvendo {entryCount:i}, ya = _countZipEntries — S29 ainda no ar.

3.2 Fase 1 — descoberta para a OPÇÃO 2 (delta de Pace)

Peço 4 arquivos (com motivo declarado):

    web/src/pages/ProfilePage.tsx — ver PreviousDelta e DeltaLine inteiros, e onde StatsByTypeItem/StatsByTypePrevious são consumidos. Resultado: PreviousDelta renderiza 5 métricas (Ativ./Dist./Elev./Tempo/Cal.), PreviousDelta não recebe pace hoje, DeltaLine aceita formatter mas NÃO tem semântica invertida.

    web/src/api/stats.ts — confirmar se StatsByTypeItem/StatsByTypePreviousItem têm avg_pace_s_per_km. Resultado: NÃO têm. Os tipos vivem em types/api.ts, mas o comentário do stats.ts só referencia os shapes.

    web/src/lib/format.ts — ver helpers existentes. Resultado: formatPace(sPerKm) já formata "mm:ss /km" e é compatível com o formatter do DeltaLine.

    web/src/types/api.ts — confirmar shape exato. Resultado CRÍTICO: StatsByTypePrevious tem só 5 campos (Ativ./Dist./Tempo/Elev./Cal.), sem avg_pace_s_per_km. StatsByTypeItem idem (idem 5 + activity_type + previous). Pace é SEMPRE derivado por computePace (já existente no ProfilePage, calcula duration / (distance/1000)).

3.3 Contrato travado (feature web)

Mudança em 1 arquivo (não 3, não 6, não schema/service/router/testes):

web/src/pages/ProfilePage.tsx:

    DeltaLine ganha lowerIsBetter?: boolean (default false). Quando true: inverte isGood/isBad (delta<0 = verde, delta>0 = vermelho), mantém sinal matemático "+"/"−" e percentual seguindo o delta cru. Usado só por pace.

    PreviousDelta ganha 1 linha de pace, condicional a PACE_TYPES.has(item.activity_type): current = computePace(item) ?? 0; previous = computePace(item.previous) ?? 0; formatter = formatPace; lowerIsBetter.

O resto intocado: backend, api/stats.ts, lib/format.ts, types/api.ts, StatsCards, coluna "Pace médio".

Decisão travada: pace SÓ nos PACE_TYPES (run/walk/hike), mesma regra da coluna "Pace médio" da tabela (cycle/swim/other mostram "—"). Pedal usa velocidade, natação usa ritmo/100m.

3.4 Validação local (feature web)

Fase 3.1 (ProfilePage.tsx): bloco de save S25c/S25d pegou 6x Sessão 30 (eu tinha anunciado 5 — erro meu de contagem, REGRA S29c registrada de novo), 994 linhas, última linha }, git status M, hash disco f81d5ad7 ≠ hash HEAD eaef1902.

Achado colateral (REGRA S30a): Select-String -Pattern "TODO|FIXME" acusou 3 matches falsos — "Todos" (label pt-BR) e "TODOS" (comentário). Select-String é case-insensitive por padrão no PS 5.1.

npm run build (com o arquivo): tsc -b verde, 824 modules, 3.67s. ProfilePage-B2Qr3yxO.js → ProfilePage-pXfRJdbD.js (21.37 → 21.54 kB, +0.17 kB). index-D7SLM8U1.js → index-DvGu4786.js (436.15 kB, mesmo tamanho). ActivityDetailPage-BnkM7vWD.js → C1KScSo5.js (11.38 kB, mesmo tamanho), SearchPage-Bo_sd9zZ.js → Bpu7TeFA.js (4.16 kB, mesmo tamanho), RouteMap-DXm9jXln.js → CXXXy7Mv.js (2.41 kB, mesmo tamanho) — todos REGRA S28b. leaflet/recharts inalterados. npm run lint: limpo.

3.5 Commit + push (feature web)

git diff --stat: 1 file changed, 42 insertions(+), 6 deletions(-).

Commit: ffaaea0 feat(web): delta de pace no drill-down por tipo (Sessao 30).

Push: 852608c..ffaaea0 main -> main.

HEAD == origin/main == ffaaea0. Working tree limpo.

3.6 Validação em produção (feature web)

Vercel redeployou (após Start-Sleep 90). index servido: /assets/index-CJjOEm0V.js (hash do Vercel, não bate com o build local DvGu4786 — REGRA S29b). __vite__mapDeps: ProfilePage-Cy6s98Hl.js (novo vs ProfilePage-B7f6FP9H da S29), ActivityDetailPage-DOBuid_4.js, SearchPage-D6UpMvrw.js, leaflet-, recharts-. Tríade de "S30 no ar" confirmada: (a) hash do ProfilePage mudou, (b) hash do index mudou, (c) __vite__mapDeps aponta pro novo. Não baixamos o chunk do ProfilePage para grep lowerIsBetter — a tríade já é prova suficiente.

Teste manual em produção NÃO foi rodado antes do fechamento. Sanity opcional na abertura da S31: abrir /users/<seu_id>, selecionar 90d ou 1 ano, olhar a coluna "vs. anterior" na linha de pace.

3.7 Descoberta mobile (pergunta "quanto falta pro mundo real?")

O usuário perguntou o percentual restante para o app mobile estar "pronto para uso real". Pedi Get-ChildItem + 4 arquivos pivô (api.dart, feed_page.dart, activity_detail_page.dart, auth_service.dart). Achado: mobile está em ~42% de cobertura vs web, NÃO os ~30% que o handoff S29 sugeria (REGRA S30c).

Achados concretos:

    Mobile tem 11 arquivos, 3 páginas (login, feed, activity_detail), 3 models (activity, activity_track, comment), 2 services (api, auth_service), 2 widgets (activity_map, like_button), main.dart com 3 rotas.

    pubspec.yaml: http, flutter_secure_storage, go_router, flutter_map, latlong2. Sem file_picker, sem image_picker, sem shared_preferences.

    ApiClient tem: login, get/post/delete genéricos, listComments, createComment, deleteComment, getActivityTrack. NÃO tem: upload, /activities, /users/*, /stats, /follow, /notifications, /search, /export, /auth/me.

    Feed: like otimista com rollback, contador de comentários, pull-to-refresh, paginação, navegação pro detalhe, recarrega item ao voltar.

    Detalhe: 3 requests paralelas (activity, comments, track), like, comentários (listar/criar/deletar), stats em cards, mapa com track real, getActivityTrack trata 404 = "sem rota" retornando null.

    Auth: JWT decode local (currentUserId), secure storage, bootstrap/login/logout com ChangeNotifier. SEM refresh token. 401 não faz logout automático.

Bloqueadores de "mundo real" fora do código: backend pago, contas de dev (Apple + Google), política de privacidade pública, exclusão de conta.

Estimativa revisada: MVP ~9-13 sessões, mundo real ~13-18 sessões. Ritmo de 1 feature por sessão.

3.8 Resultado da suíte (S30)

pytest -q → 166 passed (nenhuma mudança backend — nenhum teste novo). ruff → All checks passed. npm run build → 824 modules. npm run lint → limpo. flutter analyze → No issues found.

3.9 Commits pushados (S30)

ffaaea0 feat(web): delta de pace no drill-down por tipo (Sessao 30) — 1 file, +42/−6.

Pendente: docs: handoff da Sessao 30 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT)
Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota".
Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { ..., bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL.

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21
Permissão: dono OU seguidor do dono. Caso contrário, 404.
format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id><type>.csv". 1 header + 1 linha. Funciona com/sem rota.
format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…"><time>…</time></trkpt>.... S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. Formato ISO 8601 UTC. Exige rota → 404 "Atividade não possui rota" se route IS NULL.
format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22
Auth: self-only.
Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto.
format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota).
Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.
GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5 da janela de comparação. period/compare inválidos → 422. previous null para period="all" ou tipo ausente na janela. S30: NÃO inclui avg_pace_s_per_km em nenhum dos shapes — pace é sempre derivado no front.

Janelas (S17/S18/S20):
period | compare | janela
all | qualquer | null
90d | prev (default) | [now-180d, now-90d)
90d | yoy | [now-455d, now-365d)
1y | prev | [now-730d, now-365d)
1y | yoy | [now-730d, now-365d) (coincide — documentado em teste)

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404.

GET /auth/me — identidade do usuário logado (NÃO é /users/me).

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–30 commitadas e pushadas. HEAD == origin/main == ffaaea0. Working tree limpo (após commit do handoff S29 na abertura, feito entre sessões).

Pendente: este handoff.

Primeira ação da Sessão 31 (REGRA S27a — handoff primeiro)

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 30"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 30 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)

[Sessão 31 — primeira ação] Abrir PowerShell via Win+R → powershell
NÃO abrir de dentro do VS Code / Windows Terminal.

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 30"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 31 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 31 — primeira ação] Docker + pytest local

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432

Se o prompt já mostra (venv), PULE a linha abaixo.
.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .

Esperado: 166 passed, ruff limpo, container Up (healthy).

[Sessão 31 — primeira ação] Detecção de versão em produção (front — Vercel)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24).
⚠️ REGRA S29b: o hash servido pelo Vercel não bate com o build local. O sinal de "novo no ar" é o hash mudou vs sessão anterior.

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:($m.Groups[1].Value)"

idx=Invoke−WebRequest−Uriidx=Invoke−WebRequest−UriidxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|ProfilePage|SearchPage)-[A-Za-z0-9_-]+.js'

Esperado no estado atual (S30):
index-CJjOEm0V.js com ProfilePage-Cy6s98Hl.js, ActivityDetailPage-DOBuid_4.js, SearchPage-D6UpMvrw.js.
RouteMap-CXXXy7Mv.js NÃO aparece no __vite__mapDeps do index — lazy.

[Sessão 31 — sanity opcional] Validar S30 semanticamente baixando o chunk do ProfilePage

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′assets/(ProfilePage−[A−Za−z0−9−]+j˙s)′)html.Content,′assets/(ProfilePage−[A−Za−z0−9−​]+j˙​s)′)chunkUrl = "https://rumo-wheat.vercel.app/" + m.Groups[1].ValueWrite−Host"chunkservido:m.Groups[1].ValueWrite−Host"chunkservido:(m.Groups[1].Value)"m.Groups[1].Value)"chunk = Invoke-WebRequest -Uri chunkUrl−UseBasicParsingchunkUrl−UseBasicParsinghits = (chunk.Content∣Select−String−Pattern′Pace∣lower′−AllMatches).Matches.CountWrite−Host"ocorrenciasdePace/lowernochunk:chunk.Content∣Select−String−Pattern′Pace∣lower′−AllMatches).Matches.CountWrite−Host"ocorrenciasdePace/lowernochunk:hits"

Esperado: hits > 0. Se 0, buscar pelas strings vs. anterior/vs. ano anterior (que já existiam desde S18). Se ainda assim 0, o sanity definitivo é abrir o navegador.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodytoken = login.accesstokenlogin.accesst​okenme = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer token" } meId = $me.id

Detecção de versão em produção (backend S26 — GPX com <time> por ponto)

⚠️ REGRA S26a/S26b: NÃO usar WriteAllBytes(path,resp.Content). Usar regex direto no Content.

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodyh = @{ Authorization = "Bearer ((login.access_token)" }

aid="01a1b36a−0951−71e8−9044−c55c71558441"aid="01a1b36a−0951−71e8−9044−c55c71558441"resp = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$aid/export?format=gpx" -Headers $h -UseBasicParsing

times=[regex]::Matches(times=[regex]::Matches(resp.Content, '<time>([^<]+)</time>') | ForEach-Object { _.Groups[1].Value } n = times.Counttimes.Countdistinct = (times∣Sort−Object−Unique).CountWrite−Host"pontoscom<time>:times∣Sort−Object−Unique).CountWrite−Host"pontoscom<time>:n"
Write-Host "<time> distintos: distinct"if(distinct"if(n -gt 0) { Write-Host "primeiro: ((times[0])"; Write-Host "ultimo: ((times[-1])" }
if (distinct−le1−anddistinct−le1−andn -gt 1) {
Write-Host "S25 AINDA NO AR (todos iguais)."
} elseif (distinct−gedistinct−gen - 1) {
Write-Host "S26 NO AR (timestamps distintos por ponto)."
} else {
Write-Host "ATENCAO: apenas distinct/distinct/n distintos."
}

Esperado agora (S26 no ar): 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, ultimo 2026-11-06T21:40:23Z.

Teste real do ZIP (auth) — bytes crus via RawContentStream (REGRA S26a)

Add-Type -AssemblyName System.IO.Compression.FileSystem
token"} -UseBasicParsing
Write-Host "CSV default: ((r.StatusCode) (((r.Headers['Content-Type']))"
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
Invoke-WebRequest -Uri "<url>" -Headers h -UseBasicParsing | Out-Null } catch { resp = .Exception.Response.​Exception.Responsereader = New-Object System.IO.StreamReader(resp.GetResponseStream())Write−Host"STATUSresp.GetResponseStream())Write−Host"STATUS(
($reader.ReadToEnd())"
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b)

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:(m.Groups[1].Value)"m.Groups[1].Value)"idx = Invoke-WebRequest -Uri idxUrl−UseBasicParsingidxUrl−UseBasicParsingidx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+.js'
hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b)
hash antigo → Vercel não redeployou: aguardar 90s
Para confirmar conteúdo: baixar o chunk novo e Select-String do símbolo/helper que mudou.

⚠️ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.

Diagnóstico de save de arquivo (lição S25 — mantido)

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

Nota S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS" (Select-String é case-insensitive). Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b.

Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)

ERRADO — Content é string, não byte[]:
[System.IO.File]::WriteAllBytes(path,resp.Content)
CERTO (texto UTF-8):
[System.IO.File]::WriteAllBytes(path,[System.Text.Encoding]::UTF8.GetBytes(resp.Content))
CERTO (bytes crus — ZIP, imagem):
fs=[System.IO.File]::OpenWrite(path)fs=[System.IO.File]::OpenWrite(path)resp.RawContentStream.Position=0
resp.RawContentStream.CopyTo(resp.RawContentStream.CopyTo(fs)
fs.Close()MELHORparainspecionarGPX—semarquivo,regexnoContent:fs.Close()MELHORparainspecionarGPX—semarquivo,regexnoContent:times=[regex]::Matches(
_.Groups[1].Value }

Contar entradas de ZIP no client (S29 — referência de contrato)

O helper _countZipEntries(arrayBuffer) em web/src/api/activities.ts:

    Assinatura EOCD: 0x06054b50 (little-endian).

    Varredura do fim pra trás na janela dos últimos 22 + 65535 bytes.

    totalEntries: DataView.getUint16(eocdOffset + 10, true).

    0xFFFF como sentinela → ZIP64 → retorna -1 (não suportado).

    arrayBuffer.byteLength < 22 → retorna -1.

    Qualquer exceção no caller → -1 (fail-open).
    Sem jszip. O caller (handleExportAll em ProfilePage.tsx) decide a mensagem com base em { 0, 1, >=2, -1 }.

Delta de Pace com semântica invertida (S30 — referência de contrato)

DeltaLine em ProfilePage.tsx:

    Prop lowerIsBetter?: boolean (default false).

    Quando false: isGood = delta > 0 (verde); isBad = delta < 0 (vermelho); delta==0 → cinza.

    Quando true: isGood = delta < 0 (verde); isBad = delta > 0 (vermelho); delta==0 → cinza.

    Sinal matemático ("+"/"−") e percentual seguem o delta CRU (não a semântica de cor).

    Justificativa: o leitor interpreta pelo contexto ("Pace −0:15 /km (−4%)" em verde = ficou 15s mais rápido).

    Uso atual: só dentro de PreviousDelta, condicional a PACE_TYPES.has(item.activity_type) (run/walk/hike). Mesma regra da coluna "Pace médio" da tabela.

Se um dia outro componente ganhar semântica oposta, seguir a REGRA S30b.

Descoberta mobile — como pedir de forma econômica (S30c — referência de contrato)

Para estimar esforço real do mobile, pedir (nesta ordem):

    Estrutura + contagem + pubspec:
    cd D:\Rumo\mobile
    Get-ChildItem -Recurse -Path lib -File -Filter *.dart | Select-Object -ExpandProperty FullName
    Get-ChildItem -Recurse -Path lib -File -Filter *.dart | Group-Object { $_.DirectoryName.Replace((Resolve-Path lib).Path, "") } | Sort-Object Count -Descending | Format-Table Count, Name
    Get-Content -Encoding UTF8 pubspec.yaml

    main.dart (ponto de entrada, rotas, o que inicializa):
    Get-Content -Encoding UTF8 lib\main.dart

    api.dart (o que consome do backend — o mais importante para o gap):
    Get-Content -Encoding UTF8 lib\services\api.dart

    auth_service.dart (gestão de sessão, refresh, currentUserId):
    Get-Content -Encoding UTF8 lib\services\auth_service.dart

    feed_page.dart e activity_detail_page.dart (o que o app faz de fato):
    Get-Content -Encoding UTF8 lib\pages\feed_page.dart
    Get-Content -Encoding UTF8 lib\pages\activity_detail_page.dart

Com os 5 primeiros em mãos, dá para estimar com confiança. Não pedir os models a menos que o ApiClient os referencie e o shape importe.

SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.
(FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.
(FECHADA na S25) ~~RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy()~~ — RouteMap agora é lazy no ActivityDetailPage.
(FECHADA na S26) ~~to_gpx não emite <time> por <trkpt>~~ — agora emite quando raw_track_points está disponível e alinhado.
(FECHADA na S28) ~~PreviousDelta mostrava só 3 das 5 métricas (Ativ./Dist./Elev.), apesar de StatsByTypePreviousItem já ter total_duration_s e total_calories~~ — PreviousDelta agora renderiza as 5.
(FECHADA na S29) ~~downloadActivityExportBulk retornava void; handleExportAll sempre mostrava "Download iniciado." mesmo com ZIP vazio~~ — agora devolve { entryCount } e o feedback distingue "success" de "empty".
(FECHADA na S30) ~~Delta de Pace no PreviousDelta está fora de escopo deliberadamente: pace é ratio, delta percentual dele é ambíguo e o DeltaLine colore "+" como verde~~ — DeltaLine ganhou lowerIsBetter e PreviousDelta ganhou a linha Pace nos PACE_TYPES, com sinal/percentual mantendo o delta cru e cor invertida.

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
(CONHECIDA — Sessão 24) Feedback "Download iniciado." é mostrado quando await downloadActivityExportBulk(...) resolve. Não detecta ZIP vazio (resolvido na S29).
(CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).
(CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado (leaflet-Bw7RoR_1.js 163.60 kB) desde antes.
(CONHECIDA — Sessão 26) <time> no GPX inclui microssegundos (2026-11-07T00:20:32.931332Z) porque o gpxpy serializa datetime.isoformat(). Se algum consumidor reclamar, truncar para segundos é 1 linha em _trkpt_time.
(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Já coberto por teste.
(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. É renomeação de referência cruzada no __vite__mapDeps, não regressão (REGRA S28b).
(CONHECIDA — Sessão 29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Se um dia fizer falta, o sentinel 0xFFFF já sinaliza falha (retorna -1, fail-open).
(CONHECIDA — Sessão 29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs). Ganho: caller recebe entryCount. Se o export virar pesado (centenas de MB), trocar por leitura streaming do rodapé via blob.slice(-22-65535, blob.size).
(CONHECIDA — Sessão 29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.
(CONHECIDA — Sessão 30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX: pedal usa velocidade, natação usa ritmo/100m. Se um dia alguém quiser pace em cycle, é só relaxar PACE_TYPES — o DeltaLine já tem lowerIsBetter pronto.
(CONHECIDA — Sessão 30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0 (computePace(item) ?? 0), resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero (delta = 0).
(CONHECIDA — Sessão 30) Validação semântica do S30 em produção não foi feita via download do chunk do ProfilePage (só a tríade hash/index/mapDeps). Sanity manual ou Select-String do chunk ficam como opcionais na abertura da S31.
(CONHECIDA — Sessão 30) Mobile: ApiClient tem só login + 3 endpoints não-triviais (comments, track, /feed). Os demais (upload, /activities, /users, /stats, /follow, /notifications, /search, /export, /auth/me) NÃO existem. Trabalho futuro, não bug.
(CONHECIDA — Sessão 30) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → o ApiClient lança ApiException; o app NÃO faz logout automático. Melhoria para "mundo real", não MVP.
(CONHECIDA — Sessão 30) Mobile: sem file_picker, sem image_picker, sem shared_preferences. Upload de GPX/FIT exigirá adicionar file_picker (dep nova).
(CONHECIDA — Sessão 30) Mobile: mobile/lib/pages/login_page.dart, feed_page.dart, activity_detail_page.dart, e main.dart — não revisados individualmente linha-a-linha, só estrutura e comportamento inferidos por ApiClient + testes descritos no handoff S11. Se a S31 precisar de detalhe, pedir o arquivo.

(Oportunidade — S21–S30) RouteMap agora é lazy — se um segundo consumidor aparecer, considerar Suspense compartilhado.
(Oportunidade — S18–S30) Semântica do delta é NEUTRA. Sem "melhor/pior". Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor. Decisão de UX mantida.
(Oportunidade — S19–S30) Stats públicas só quando viewer segue o alvo.
(Oportunidade — S22–S30) Export em lote no mobile.
(Oportunidade — S22–S30) Export em lote concatenado (1 CSV + 1 GPX).
(Oportunidade — S24–S30) Detectar ZIP vazio no client via DecompressionStream (a S29 usou EOCD, que é ainda mais barato — fechada).
(Oportunidade — S30) Testes unitários do DeltaLine (não há hoje; é puro, dá pra testar com 4 casos e sem React Testing Library, se algum dia valer a pena).
(Oportunidade — S30) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.
(Oportunidade — S30) Mobile: tela de perfil, stats, notificações, busca, upload — o plano completo está na Seção 8 (S31 em diante).

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 31 e além)

Sessão 30 fechada. Export 100% completo no web (backend S21+S22+S26, front S21+S23+S24+S29). Drill-down por tipo mostra as 5 métricas no delta (S28) + Pace com semântica correta (S30). Descoberta mobile feita (S30): mobile está em ~42% de cobertura, com os bloqueadores de "mundo real" mapeados (backend pago, contas de dev, política de privacidade, exclusão de conta).

Primeira ação obrigatória da Sessão 31 (REGRA S27a)

Abrir PowerShell via Win+R → powershell.
Rodar o bloco "[Sessão 31 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 30, push, confirmar HEAD == origin/main.
Sanidade de build (npm run build/npm run lint + flutter analyze).
Docker + pytest (docker ps -a, pg_isready, pytest -q → 166, ruff check).
Detecção de versão em produção (front Vercel + back Render S26 — GPX com <time> por ponto).

Rota travada para a Sessão 31: Upload GPX/FIT no mobile.

Este é o divisor de águas: sem upload, o app é 100% read-only; com upload, ele começa a ser útil no dia a dia. É o maior gap funcional do mobile (confirmado na descoberta da S30 — ApiClient não tem multipart, não tem /activities/upload).

Contrato travado da S31:

    pubspec.yaml — adicionar file_picker: ^8.x (única dep nova). Verificar versão exata com flutter pub add file_picker para não chutar.

    lib/services/api.dart — adicionar método uploadActivity({required File file, String? title, String? activityType, String? description}) que faz POST multipart/form-data em /activities/upload. Reutiliza _extractMessage e _send-like para tratar erro. ~50 linhas.

    lib/pages/upload_page.dart (NOVO) — tela com:

        FilePicker (file_picker) para selecionar .gpx ou .fit.

        Validação client-side (extensão + tamanho máx 20 MB, igual ao web).

        Campo opcional de título e descrição.

        Botão "Enviar" com loading e feedback (sucesso → volta pro feed; erro → SnackBar).

    lib/main.dart — adicionar rota /upload e botão de FAB/nav no FeedPage para abrir.

Escopo NÃO incluso na S31:

    Múltiplas fotos (Cloudinary upload separado) — fica pra sessão futura.

    Parse local pra preview de stats antes do upload — fica pra S32.

    Upload em background com notificação — fica pra depois.

Risco baixo: endpoint já existe em produção desde S12, sem mudança backend. Validação é manual (upload de GPX real em aparelho/emulador).

Escolha para a Sessão 32 (a decidir depois da S31)

OPÇÃO 1 — Tela de Perfil próprio (stats + atividades).
OPÇÃO 2 — Stats agregados (summary + weekly/monthly + by-type com delta) na tela de perfil.
OPÇÃO 3 — Export unitário + lote no mobile (paridade com web S21/S22/S29).
OPÇÃO 4 — Build de release + ícone + splash + política de privacidade + exclusão de conta (bloqueadores de loja).

Recomendação: depois da S31 (upload), S32 = "Minhas atividades" (/activities?user_id=) + tela de perfil próprio simples, e S33 = stats agregados. É a sequência que torna o app usável para o usuário, antes de paridade social ou export.

Recomendação final para a Sessão 31

Rodar Fase 0 completa (com handoff S30 commitado primeiro). Se tudo verde, começar o upload GPX/FIT seguindo o contrato acima — entrega incremental (pubspec → api.dart → upload_page.dart → main.dart), com flutter analyze entre cada entrega e validação manual em aparelho/emulador no fim.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 31 neste mesmo formato (seções 0 a 9).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25 (abertura): reforçou os mesmos acordos. Tolerou 3 tropeços (Select-String mal desenhado, commit sem validação, README com cerca vazando) — sem reclamar, só reportando. Registrei cada um como regra (S25a–S25e).

Na S26 (abertura): reforçou os mesmos acordos. Tolerou 2 tropeços (WriteAllBytes de string, Render demorando >3 min) — sem reclamar. Registrei (S26a–S26c).

Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a. Perguntou "o que você recomenda?" e seguimos a recomendação.

Na S28 (abertura): handoff S27 já estava commitado (commit entre sessões). Fase 0 limpa. Fase 1 revelou escopo real (1 arquivo, não 6). Ajustei em tempo real, entreguei 1 arquivo, validei em produção. Perguntou "sempre o que você recomendar" ao fim e eu recomendei entregar o handoff agora — ele concordou.

Na S29 (abertura): handoff S28 já commitado (padrão virou rotina). Fase 0 limpa. Fase 1 revelou escopo de 2 arquivos (não 3). Entreguei activities.ts, o usuário colou um erro do ESLint no-useless-assignment — corrigi na hora, registrei REGRA S29d. Entreguei ProfilePage.tsx, build verde, commit, push, validação em produção com 4 testes manuais. Ao fim, "tudo como esperado". Recomendei entregar o handoff agora — ele concordou.

Na S30 (abertura): handoff S29 já commitado. Fase 0 limpa. Ao chegar na escolha de rota, o usuário disse "como já mensionando sempre vamos fazer o que você recomendar". Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. Fase 1 revelou escopo MUITO menor: StatsByTypePrevious nem tem avg_pace_s_per_km — pace é sempre derivado (computePace), o que elimina qualquer mudança em schema/backend/tipos. Contrato travado em 1 arquivo, com DeltaLine ganhando lowerIsBetter e PreviousDelta ganhando 1 linha condicional a PACE_TYPES. Entrega, build verde, 1 tropeço (erro de contagem "5x vs 6x", REGRA S29c), 1 achado colateral (Select-String case-insensitive "Todos"/"TODOS" — REGRA S30a), commit, push, Vercel redeployou (index e ProfilePage com hash novo).

Em seguida, o usuário perguntou o % para "mundo real" do app mobile. Recomendei descoberta de código (não estimar de memória). Ele autorizou. Pedi Get-ChildItem + 4 arquivos pivô (api.dart, feed_page.dart, activity_detail_page.dart, auth_service.dart). Achado: mobile está em ~42% de cobertura vs web, NÃO os ~30% que o handoff S29 sugeria (REGRA S30c). Estimativa revisada: MVP ~9-13 sessões, mundo real ~13-18. Bloqueadores não-código: backend pago, contas de dev, política de privacidade, exclusão de conta.

Ao fim da S30, o usuário perguntou se o handoff devia ser refeito diante das novas informações. Recomendei refazer (este arquivo), porque o S30 original subestimava o mobile. Ele concordou e pediu o handoff completo.

Pedido para o assistente da S31 (e além): manter o processo da S21–S30. Concretamente:

Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca, mesmo os "óbvios", antes de aceitar o escopo do handoff anterior como verdade. REGRA S30c: no mobile, pedir Get-ChildItem + os 5 arquivos pivô (main.dart, api.dart, auth_service.dart, feed_page.dart, activity_detail_page.dart) antes de estimar; handoff de memória SUBESTIMA o que existe.

Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — regra S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a).

Fase 4 — validação em produção: local verde é pré-requisito; prod via HTTP/browser é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js e procurar o chunk (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local — sinal é "mudou vs sessão anterior + conteúdo do chunk".

Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir.

Regras novas da S30 (Seção 0, itens 30a–30c): Select-String "TODO" casa "Todos"/"TODOS" (usar -CaseSensitive ou regex \bTODO\b); componente genérico ganhando semântica oposta → prop booleana default-false, sinal/percentual seguem delta cru, 4 casos; handoff de memória sobre mobile SUBESTIMA o que existe — pedir código antes de estimar.

O que funcionou nas S21–S30 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal, não na previsão. E a disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30) — em vez de implementar trabalho redundante. E a consistência em aceitar os erros (contagem, lint, falsos positivos) na hora e corrigir/registrar, sem contornar.