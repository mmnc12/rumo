HANDOFF — Rumo (backend + frontend + mobile) — Sessão 28

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

⚠️ REGRA S26a — no PowerShell 5.1, Invoke-WebRequest -UseBasicParsing devolve $resp.Content como STRING, não como byte[]

[System.IO.File]::WriteAllBytes(path,path,resp.Content) falha com "Não é possível converter o valor ... para o tipo System.Byte[]". Para escrever bytes, usar:

[System.IO.File]::WriteAllBytes(path,[System.Text.Encoding]::UTF8.GetBytes(path,[System.Text.Encoding]::UTF8.GetBytes(resp.Content)) — OK para GPX/CSV/XML (texto UTF-8), ou

resp.RawContentStream.CopyTo(resp.RawContentStream.CopyTo(fileStream) — preserva bytes crus, ideal para binários (ZIP, imagem).

Para inspecionar GPX/XML, evitar escrever arquivo: usar [regex]::Matches($resp.Content, '<time>([^<]+)</time>') direto no Content.

⚠️ REGRA S26b — validar GPX em produção por regex é mais barato que por gpxpy+arquivo temporário

Contar <time> distintos com regex no Content responde a pergunta "o S26 está no ar?" em 3 linhas de PowerShell, sem $env:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>).

⚠️ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push

Não é bug. Se a primeira validação em prod mostrar o comportamento antigo (S25: todos os <time> iguais), esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, então sim: ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min.

⚠️ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa

Se git status --short mostrar M docs/HANDOFF.md no início da sessão, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro (mensagem docs: handoff da Sessao N), push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0. Motivo: se a Fase 0 revelar algo que exija reverter ou reescrever, o handoff precisa estar preservado no histórico — nunca em risco de ser sobrescrito por uma edição no working tree.

⚠️ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend

Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir. Nunca encadear os 4 blocos num só comando e "ver depois" — o diagnóstico fica ambíguo.

⚠️ REGRA S28a (NOVA) — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios"

Na S28, o handoff S27 descrevia a OPÇÃO 1 como "delta de tempo/calorias nos stats", sugerindo mudança em schema+service+router+testes+ProfilePage. A descoberta real (pedir schemas/stats.py, services/stats_service.py, ProfilePage.tsx, StatsCards.tsx, lib/format.ts) revelou que: schema já tinha os 5 campos, service já calculava os 5 no `previous`, StatsCards já renderizava os 5, e o único gap era o componente `PreviousDelta` mostrar 3 de 5. Escopo real: 1 arquivo, 24 linhas. Lição: sempre pedir os arquivos antes de aceitar o escopo do handoff anterior como verdade. O handoff pode estar desatualizado (foi escrito com base em memória, não no código).

⚠️ REGRA S28b (NOVA) — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código

Na S28, `ActivityDetailPage` e `SearchPage` mudaram de hash (`J23GpMg5` → `BOuCLIUn`, `CvOmHzdZ` → `DVVs61sJ`) sem nenhuma linha alterada nesses arquivos. Motivo: o `__vite__mapDeps` do index renumera índices de chunks quando um chunk muda de tamanho. Se o tamanho do chunk é o mesmo e só o hash mudou, é renomeação de referência, não regressão. Não investigar como bug.

O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (166 passed ao fim da S28). Container de teste rumo_postgres_test na porta 5433.

⚠️ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).

Estrutura do repo (referência — conferir, não assumir)

text

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
├── mobile/lib/ (models/ pages/ services/ widgets/)
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 6 atividades, 26.443 m. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, tipo walk, 60 pontos, ~10 min de duração) usada para validar o S26.

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21/S22/S23/S24/S25/S26/S27/S28)

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

Processo que o usuário elogiou na S21–S28 (para manter)

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

S28 (delta de tempo/calorias no drill-down por tipo):

ESCOPO REAL descoberto via Fase 1 (6 arquivos + lib/format.ts): o handoff S27 descrevia a opção como "adicionar total_duration_s e total_calories ao delta", sugerindo mudança em schema+service+router+testes+frontend. A descoberta revelou que:

- backend/app/schemas/stats.py: StatsByTypePreviousItem JÁ TEM total_duration_s: int e total_calories: int. StatsByTypeItem JÁ TEM os dois. StatsSummary/StatsPeriod JÁ TÊM ambos. → Zero mudança de schema.

- backend/app/services/stats_service.py: get_by_type JÁ CALCULA prev_total_duration_s e prev_total_calories via SUM(CASE WHEN cmp_cond THEN Activity.duration_s/calories). O previous do item JÁ CARREGA os 5 campos reais. → Zero mudança de service/router.

- web/src/components/StatsCards.tsx: JÁ RENDERIZA 5 cards (Atividades, Distância, Tempo, Elevação, Calorias) do StatsSummary. → Zero mudança.

- web/src/pages/ProfilePage.tsx → PreviousDelta: mostrava SÓ 3 das 5 métricas (Ativ., Dist., Elev.) — faltavam Tempo e Calorias. Esse era o ÚNICO gap real.

- web/src/lib/format.ts: formatDuration(seconds: number | null | undefined): string e formatCalories(kcal: number | null | undefined): string — assinaturas compatíveis com DeltaLine.formatter?: (n: number) => string por contravariância (number é subtipo de number | null | undefined). Sem cast, sem wrapper.

MUDANÇA EXECUTADA — 1 arquivo, 24 inserções + 1 deleção em web/src/pages/ProfilePage.tsx:

1) Import ganhou formatCalories.

2) PreviousDelta ganhou 2 DeltaLine novas (label="Tempo", label="Cal.") com formatter={formatDuration} e formatter={formatCalories}.

3) Comentários de doc/header atualizados.

FORA DE ESCOPO (decisão registrada, não fazer): não adicionar delta de Pace — pace é ratio (duration/distance), delta percentual dele é ambíguo e o DeltaLine colore "+" como verde (que inverteria o significado em pace). Ficou fora.

Validação: tsc -b verde (tipagem OK sem cast), 824 modules, ProfilePage-xtlegScf.js 21.08kB (era 20.88kB local; +0.20kB ≈ +50 linhas compiladas). Vercel redeployou como ProfilePage-DuN1Ag-6.js (hash novo, tamanho equivalente). ActivityDetailPage e SearchPage mudaram de hash mas tamanho idêntico — renomeação de referência cruzada, não regressão (REGRA S28b).

Commit: ba43fad feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28). Push OK.

Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet (RouteMap no detalhe, lazy desde S25) + recharts (gráficos no perfil). S21: botões "Baixar CSV" (sempre) e "Baixar GPX" (condicional a track) no ActivityDetailPage. S23: card "Exportar tudo" no ProfilePage (só isSelf). S24: aviso "Se nenhuma atividade casar com o período, o ZIP virá vazio." + feedback "Download iniciado." por ~4s. S26 e S27 intocados em web/. S28: delta de tempo/calorias no PreviousDelta.

Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite), alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds. Intocado desde a S11. Sem drill-down de stats, sem export.

Estado final da S28:

git log: ba43fad feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28), db2e224 docs: handoff da Sessao 27, 585839f docs: handoff da Sessao 26.

Render: backend idêntico ao S27 (S26 no ar, 60/60 <time> distintos na atividade de teste). Nenhum redeploy relevante na S28 (zero mudança backend).

Vercel: bundle redeployado. index-Dz7xtpJW.js com ProfilePage-DuN1Ag-6.js (novo), ActivityDetailPage-BOuCLIUn.js, SearchPage-DVVs61sJ.js. RouteMap-BWdETDdy.js segue lazy, fora do mapDeps.

pytest -q: 166 passed (nenhum teste novo — nenhuma lógica backend mudou). ruff check .: All checks passed. npm run build: 824 modules. npm run lint: limpo. flutter analyze: No issues found.

Nada pendente de código.

Sessão 28 foi curta: Fase 0 limpa + descoberta revelou escopo mínimo + 1 arquivo de front + build + commit + validação em produção.

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

Deps novas em S28: nenhuma.

Git (estado ao fim da Sessão 28)

text

ba43fad (HEAD -> main, origin/main) feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28)
db2e224 docs: handoff da Sessao 27
585839f docs: handoff da Sessao 26
15ccccb feat(activities): GPX export com <time> por ponto (Sessao 26)
7bf5bc2 docs: handoff da Sessao 25
4146c3a docs: corrige README (remove instrucoes de sessao por engano)
eb9ae35 docs: README com cheat sheet de endpoints e comandos
1fbcf0e feat(web): RouteMap com React.lazy no detalhe (Sessao 25)
a485eab feat(web): feedback de sucesso no exportar tudo (Sessao 24)
f1ff9f0 docs: handoff da Sessao 23

Pendente: docs/HANDOFF.md da S28 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 28.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 28

3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

Handoff pendente. git status --short veio VAZIO na abertura — o commit do handoff S27 (db2e224) já estava feito ANTES do início da S28 (provável commit entre sessões). Confirmação: git add + git commit retornaram "nothing to commit, working tree clean"; git push retornou "Everything up-to-date". HEAD == origin/main == db2e224. (REGRA S27a cumprida — o handoff estava commitado e preservado.)

Log/status. git status: On branch main / up to date with 'origin/main' / nothing to commit, working tree clean. git log: db2e224 no topo, 585839f abaixo, 15ccccb, 7bf5bc2, 4146c3a, eb9ae35, 1fbcf0e, a485eab. Sem surpresas.

Build/lint/analyze. npm run build: 824 modules, 1.95s, chunks idênticos ao S27 local (index-BRwYOlv6.js 435.82kB, ProfilePage-DIsNjdrp.js 20.88kB, ActivityDetailPage-CjI4Jf2W.js 11.38kB, SearchPage-B795Q3Kf.js 4.16kB, leaflet-Bw7RoR_1.js 163.60kB, recharts-DI5KUTLO.js 351.26kB, RouteMap-BWdETDdy.js 2.41kB). npm run lint: limpo. flutter analyze: No issues found (3.3s).

Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test Up 8 hours (healthy), pg_isready OK. pytest -q: 166 passed in 43.91s. ruff check .: All checks passed.

Prod backend (S26). Login OK. Atividade 01a1b36a-0951-71e8-9044-c55c71558441: 60 pontos com <time>, 60 distintos. Primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z. S26 NO AR confirmado via regex no Content (REGRA S26b).

Prod frontend (Vercel). index servido: /assets/index-DV3loxrJ.js (idêntico ao S25/S26/S27). __vite__mapDeps confirma ActivityDetailPage-J23GpMg5.js, ProfilePage-Bfp0kvA2.js, SearchPage-CvOmHzdZ.js, leaflet-, recharts-. RouteMap-BWdETDdy.js fora do mapDeps — lazy via import() dentro do ActivityDetailPage, comportamento esperado.

3.2 Fase 1 — descoberta para a OPÇÃO 1 do handoff S27

Peço 6 arquivos + lib/format.ts com motivo declarado:

1) backend/app/schemas/stats.py — ver StatsByTypePreviousItem e StatsByTypeItem. Resultado: AMBOS JÁ TÊM total_duration_s e total_calories. Handoff S27 estava desatualizado.

2) backend/app/services/stats_service.py — ver como get_by_type monta previous. Resultado: JÁ CALCULA prev_total_duration_s e prev_total_calories via SUM(CASE WHEN cmp_cond THEN Activity.duration_s/calories). previous JÁ CARREGA os 5 campos. Zero mudança necessária.

3) (não precisei pedir) backend/app/routers/activities.py — confirmado desnecessário: nada muda no handler.

4) (não precisei pedir) backend/tests/test_stats.py — confirmado desnecessário: nada muda na lógica.

5) web/src/pages/ProfilePage.tsx — ver PreviousDelta. Resultado: mostrava 3 de 5 métricas (Ativ., Dist., Elev.). Faltavam Tempo e Calorias. ESTE É O GAP REAL.

6) web/src/components/StatsCards.tsx — ver summary no topo. Resultado: JÁ renderiza 5 cards (Atividades, Distância, Tempo, Elevação, Calorias). Zero mudança necessária.

7) web/src/lib/format.ts — ver assinaturas de formatDuration e formatCalories. Resultado: ambas são (number | null | undefined) => string, compatíveis com DeltaLine.formatter sem cast.

3.3 Contrato travado

Arquivo único: web/src/pages/ProfilePage.tsx.

Mudança 1: import ganha formatCalories.

Mudança 2: PreviousDelta ganha 2 DeltaLine novas:

<DeltaLine label="Tempo" current={item.total_duration_s} previous={item.previous.total_duration_s} formatter={formatDuration} />
<DeltaLine label="Cal." current={item.total_calories} previous={item.previous.total_calories} formatter={formatCalories} />

Marcação // [Sessão 28] no import, no comentário de doc do PreviousDelta, no comentário do header da tabela e nas 2 DeltaLine.

FORA DE ESCOPO: não adicionar delta de Pace (ratio com semântica ambígua para "+"/"-"); não alterar StatsCards; não alterar backend; não alterar schema; não adicionar testes backend; não alterar format.ts.

3.4 Validação local

Bloco de save check (S25c/S25d): Sessão 28 aparece 4x (import, header, doc, inline); formatCalories 4x (import + comentário + uso); DeltaLine 7 matches (5 <DeltaLine> + 1 function DeltaLine + 1 PreviousDelta que não casa — ver nota); total 913 linhas; git status mostra M; hash disco acebd147... ≠ hash HEAD 67f2e5e8.... Save confirmado.

npm run build: tsc -b verde (tipagem OK — formatDuration e formatCalories casam com formatter por contravariância), 824 modules, 2.22s. ProfilePage-xtlegScf.js 21.08kB (era 20.88kB; +0.20kB ≈ +50 linhas JS compiladas). Demais chunks com hash novo mas tamanho idêntico — renomeação de referência cruzada (REGRA S28b).

npm run lint: limpo.

3.5 Commit + push

git diff --stat: 1 file changed, 24 insertions(+), 1 deletion(-).

Commit: ba43fad feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28).

Push: db2e224..ba43fad main -> main.

HEAD == origin/main == ba43fad. Working tree limpo.

3.6 Validação em produção

Vercel redeployou (após Start-Sleep 90). index servido: /assets/index-Dz7xtpJW.js (novo). __vite__mapDeps mostra ProfilePage-DuN1Ag-6.js (novo, era ProfilePage-Bfp0kvA2.js), ActivityDetailPage-BOuCLIUn.js (hash novo, tamanho igual), SearchPage-DVVs61sJ.js (hash novo, tamanho igual), leaflet-Bw7RoR_1.js, recharts-DI5KUTLO.js (mesmos hashes). RouteMap segue lazy (fora do mapDeps).

Validação visual do usuário: "tudo funcionando como esperado". Delta de 5 métricas (Ativ., Dist., Elev., Tempo, Cal.) renderizando na tabela "Por tipo de atividade" quando period != "all".

3.7 Resultado da suíte (S28)

pytest -q → 166 passed (nenhuma mudança backend — nenhum teste novo). ruff → All checks passed. npm run build → 824 modules. npm run lint → limpo. flutter analyze → No issues found.

3.8 Commits pushados (S28)

ba43fad feat(web): delta de tempo e calorias na tabela por tipo (Sessao 28) — 1 file, +24/−1.

Pendente: docs: handoff da Sessao 28 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT)

Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota".

Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { ..., bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL.

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21

Permissão: dono OU seguidor do dono. Caso contrário, 404.

format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.csv". 1 header + 1 linha. Funciona com/sem rota.

format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…"><time>…</time></trkpt>.... S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. Formato ISO 8601 UTC. Exige rota → 404 "Atividade não possui rota" se route IS NULL.

format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22

Auth: self-only.

Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto.

format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota).

Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.

GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.

GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.

GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; `previous` (nullable) carrega as mesmas 5 da janela de comparação. period/compare inválidos → 422. previous null para period="all" ou tipo ausente na janela.

Janelas (S17/S18/S20):

period compare janela
all qualquer null
90d prev (default) [now-180d, now-90d)
90d yoy [now-455d, now-365d)
1y prev [now-730d, now-365d)
1y yoy [now-730d, now-365d) (coincide — documentado em teste)

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404.

GET /auth/me — identidade do usuário logado (NÃO é /users/me).

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–28 commitadas e pushadas. HEAD == origin/main == ba43fad. Working tree limpo (após commit do handoff S27 na abertura).

Pendente: este handoff.

Primeira ação da Sessão 29 (REGRA S27a — handoff primeiro)

powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 28"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 28 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)

[Sessão 29 — primeira ação] Abrir PowerShell via Win+R → powershell

NÃO abrir de dentro do VS Code / Windows Terminal.

powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 28"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 29 — primeira ação] Sanidade de build

powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 29 — primeira ação] Docker + pytest local

powershell

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

[Sessão 29 — primeira ação] Detecção de versão em produção (front — Vercel)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24).

powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"

$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|ProfilePage|SearchPage)-[A-Za-z0-9_-]+\.js'

Esperado no estado atual (S28):
index-Dz7xtpJW.js com ProfilePage-DuN1Ag-6.js, ActivityDetailPage-BOuCLIUn.js, SearchPage-DVVs61sJ.js.
RouteMap-BWdETDdy.js NÃO aparece no __vite__mapDeps do index — lazy.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me

powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Detecção de versão em produção (backend S26 — GPX com <time> por ponto)

⚠️ REGRA S26a/S26b: NÃO usar WriteAllBytes(path,path,resp.Content). Usar regex direto no Content.

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
if ($n -gt 0) { Write-Host "primeiro: $($times[0])"; Write-Host "ultimo: $($times[-1])" }
if ($distinct -le 1 -and $n -gt 1) {
    Write-Host "S25 AINDA NO AR (todos iguais)."
} elseif ($distinct -ge $n - 1) {
    Write-Host "S26 NO AR (timestamps distintos por ponto)."
} else {
    Write-Host "ATENCAO: apenas $distinct/$n distintos."
}

Esperado agora (S26 no ar): 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, ultimo 2026-11-06T21:40:23Z.

Detecção de versão em produção (backend S22 — export em lote)

powershell

$openapi = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json"
$hasBulkExport = $openapi.paths.PSObject.Properties.Name -contains "/activities/export"
Write-Host "rota /activities/export no ar: $hasBulkExport"
if (-not $hasBulkExport) {
    Write-Host "RENDER AINDA NAO REDEPLOYOU. Aguardar 1-3 min ou Manual Deploy no dashboard."
}

Teste real do ZIP (auth) — bytes crus via RawContentStream (REGRA S26a)

Add-Type -AssemblyName System.IO.Compression.FileSystem
$r = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/export?format=csv" -Headers @{Authorization="Bearer $token"} -UseBasicParsing
Write-Host "CSV default: $($r.StatusCode) ($($r.Headers['Content-Type']))"
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
Se o prompt já mostra (venv), pule:

.\venv\Scripts\Activate.ps1
ruff check .

Recuperação de arquivo corrompido (lição S21)

powershell

cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>
Se o último commit for anterior à mudança quebrada:

git restore <arquivo>
Se a versão quebrada JÁ foi commitada:

git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22 + S26c)

powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"
Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy.
Se rota no ar mas retorna 422, ver o BODY do erro:

try {
  Invoke-WebRequest -Uri "<url>" -Headers $h -UseBasicParsing | Out-Null
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "STATUS $($resp.StatusCode.value__) - $($reader.ReadToEnd())"
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24)

powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+\.js'
hash novo → bundle novo no ar
hash antigo → Vercel não redeployou: aguardar 90s

⚠️ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.

Diagnóstico de save de arquivo (lição S25 — mantido)

powershell
Depois de salvar, ANTES de commitar:

Write-Host "=== [1] termo proibido (deve vir vazio) ==="
Select-String -Path <arquivo> -Pattern "<termo-proibido>"
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

Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)

powershell
ERRADO — Content é string, não byte[]:
[System.IO.File]::WriteAllBytes(path,path,resp.Content)
CERTO (texto UTF-8):

[System.IO.File]::WriteAllBytes(path,[System.Text.Encoding]::UTF8.GetBytes(path,[System.Text.Encoding]::UTF8.GetBytes(resp.Content))
CERTO (bytes crus — ZIP, imagem):

$fs=[System.IO.File]::OpenWrite(fs=[System.IO.File]::OpenWrite(path)
$resp.RawContentStream.Position=0resp.RawContentStream.Position=0resp.RawContentStream.CopyTo(fs)fs)fs.Close()
MELHOR para inspecionar GPX — sem arquivo, regex no Content:

$times=[regex]::Matches(times=[regex]::Matches(resp.Content, '<time>([^<]+)</time>') | ForEach-Object { $_.Groups[1].Value }

SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.

(FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.

(FECHADA na S25) ~~RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy()~~ — RouteMap agora é lazy no ActivityDetailPage.

(FECHADA na S26) ~~to_gpx não emite <time> por <trkpt>~~ — agora emite quando raw_track_points está disponível e alinhado.

(FECHADA na S28) ~~PreviousDelta mostrava só 3 das 5 métricas (Ativ./Dist./Elev.), apesar de StatsByTypePreviousItem já ter total_duration_s e total_calories~~ — PreviousDelta agora renderiza as 5 (Ativ./Dist./Elev./Tempo/Cal.).

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

(CONHECIDA — Sessão 24) Feedback "Download iniciado." é mostrado quando await downloadActivityExportBulk(...) resolve. Não detecta ZIP vazio.

(CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).

(CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado (leaflet-Bw7RoR_1.js 163.60 kB) desde antes. Tira o código do RouteMap (2.41 kB) do chunk do ActivityDetailPage e faz o leaflet baixar só quando o mapa renderiza. Ganho modesto e legítimo.

(CONHECIDA — Sessão 26) <time> no GPX inclui microssegundos (2026-11-07T00:20:32.931332Z) porque o gpxpy serializa datetime.isoformat(). Strava/Garmin aceitam ISO 8601 com fração. Se algum consumidor reclamar, truncar para segundos é 1 linha em _trkpt_time (return dt.replace(microsecond=0)). Não fazer agora (YAGNI).

(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Já coberto por teste.

(CONHECIDA — Sessão 28) Delta de Pace no PreviousDelta está fora de escopo deliberadamente: pace é ratio (duration/distance), delta percentual dele é ambíguo e o DeltaLine colore "+" como verde (que inverteria o significado em pace — pace menor é melhor). Se um dia entrar, precisa de DeltaLine variant ou label invertido.

(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. É renomeação de referência cruzada no __vite__mapDeps, não regressão (REGRA S28b).

(Oportunidade — S21–S28) RouteMap agora é lazy — se um segundo consumidor aparecer, considerar Suspense compartilhado.

(Oportunidade — S18–S28) Semântica do delta é NEUTRA. Sem "melhor/pior". Pace fica de fora por isso.

(Oportunidade — S19–S28) Stats públicas só quando viewer segue o alvo.

(Oportunidade — S22–S28) Export em lote no mobile.

(Oportunidade — S22–S28) Export em lote concatenado (1 CSV + 1 GPX).

(Oportunidade — S24–S28) Detectar ZIP vazio no client via DecompressionStream ou lib.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 29 e além)

Sessão 28 fechada. Feature de export 100% completa (backend S21+S22+S26, front S21+S23+S24). Drill-down por tipo (S14, S15, S17, S18, S20) agora mostra todas as 5 métricas no delta. Nenhuma pendência de código.

Primeira ação obrigatória da Sessão 29 (REGRA S27a)

Abrir PowerShell via Win+R → powershell.

Rodar o bloco "[Sessão 29 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 28, push, confirmar HEAD == origin/main.

Sanidade de build (npm run build/npm run lint + flutter analyze).

Docker + pytest (docker ps -a, pg_isready, pytest -q → 166, ruff check).

Detecção de versão em produção (front Vercel + back Render S26 — GPX com <time> por ponto).

Escolha para a Sessão 29

OPÇÃO 1 — Detectar ZIP vazio no client (RECOMENDADA).

Hoje: o botão "Exportar tudo" mostra "Download iniciado." sempre que downloadActivityExportBulk(...) resolve, mesmo quando o ZIP veio vazio (0 atividades no período). O usuário não tem como saber se baixou algo útil sem abrir o ZIP. Solução: ler o ZIP no client (DecompressionStream nativo ou lib pequena) e mostrar "Nenhuma atividade no período — ZIP vazio." ou "Download iniciado (N atividades)."

Só frontend (ProfilePage.tsx + talvez client.ts). Sem mudança de contrato HTTP. Baixo risco. Valor: feedback preciso ao usuário.

Fase 1 da S29: pedir web/src/pages/ProfilePage.tsx (já conheço o handler handleExportAll) + web/src/api/client.ts (para ver como apiFetchBlob devolve o blob) + web/src/api/activities.ts (downloadActivityExportBulk). Contrato travado antes de codar.

OPÇÃO 2 — Export no app mobile (paridade com web).

Mobile parado desde S11. Sessão grande (backend já está pronto, mas mobile precisa de download + share sheet + tratamento de ZIP). Só se houver demanda real.

OPÇÃO 3 — Delta de Pace com semântica correta.

Adicionar Pace ao PreviousDelta exigiria DeltaLine variant (pace menor = verde) ou label invertido. Só para tipos que usam pace (run/walk/hike). Trabalho pequeno mas não trivial. Valor discutível.

OPÇÃO 4 — Fechar ciclo de novo, sem feature.

Se o usuário preferir pausar. Só faz sentido se houver outra prioridade.

Recomendação final para a Sessão 29

Rodar Fase 0 completa (com handoff S28 commitado primeiro). Se tudo verde, abrir OPÇÃO 1 — detecção de ZIP vazio no client. É pequena, só frontend, resolve um problema real de UX, e não toca contrato.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 29 neste mesmo formato (seções 0 a 9).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25 (abertura): reforçou os mesmos acordos. E ao longo da sessão, tolerou com paciência os 3 tropeços (Select-String mal desenhado, commit sem validação, README com cerca vazando instruções) — sem reclamar, apenas reportando o output. Registrei cada um como regra (S25a–S25e).

Na S26 (abertura): reforçou os mesmos acordos. E ao longo da sessão, tolerou os 2 tropeços (bloco PowerShell com WriteAllBytes de string, Render demorando >3 min) — sem reclamar, apenas reportando o output. Registrei cada um como regra (S26a–S26c).

Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a. Perguntou "o que você recomenda?" e seguimos a recomendação (encerrar com handoff).

Na S28 (abertura): handoff S27 já estava commitado (motivo desconhecido — provavelmente commit entre sessões). Fase 0 rodou limpa. Ao chegar na Fase 1, a descoberta revelou que o escopo do handoff S27 estava desatualizado (schema e service já faziam o que o handoff dizia faltar). Ajustei escopo em tempo real, entreguei 1 arquivo, validei em produção. Perguntou "sempre o que você recomendar" ao fim e eu recomendei entregar o handoff agora — ele concordou.

Pedido para o assistente da S29 (e além): manter o processo da S21–S28. Concretamente:

Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca, mesmo os "óbvios", antes de aceitar o escopo do handoff anterior como verdade.

Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato antes de codar. Apresentar ao usuário.

Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — regra S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (front) entre cada entrega.

Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M. Só então pedir commit.

Fase 4 — validação em produção: local verde é pré-requisito; prod via HTTP/browser é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js e procurar o chunk (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada.

Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir.

Regras novas da S28 (Seção 0, itens 24–25): confirmar escopo real via Fase 1 antes de aceitar o handoff anterior como verdade; chunk renomeado por referência cruzada não é regressão.

O que funcionou nas S21–S28 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal, não na previsão. E, na S28, a disposição de REDUZIR escopo quando a descoberta mostrou que o handoff S27 estava desatualizado — em vez de implementar trabalho redundante.