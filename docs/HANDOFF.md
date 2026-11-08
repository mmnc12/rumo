HANDOFF — Rumo (backend + frontend + mobile) — Sessão 25
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

Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo. Eu errei isso no diagnóstico do README e quase fechei falso positivo.
⚠️ REGRA S25b — quando $lines[-1] for suspeito, confirmar com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo único>" antes de concluir

Não dar "OK" nem "corrompido" sem evidência.
⚠️ REGRA S25c — antes de pedir git add/git commit de um arquivo que o usuário acabou de salvar, EXIGIR o output do bloco de validação e ESPERAR

Foi o que faltou na S25: pedi commit sem esperar a confirmação do save.
⚠️ REGRA S25d — o teste definitivo de "o save pegou" é git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M <arquivo>

Se git status --short vier vazio depois de salvar, o disco é igual ao commitado. O save não pegou.
⚠️ REGRA S25e — ao entregar o conteúdo de um arquivo para colar no editor, entregar SEM cerca ```markdown ... ``` envolvendo

Entregar o arquivo inteiro como o único texto da resposta, sem instruções antes/depois. Isso elimina a ambiguidade "copiei a resposta inteira e colei, o texto de instrução veio junto". Foi o que aconteceu duas vezes na S25 até eu entregar o conteúdo sem cerca.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (164 passed ao fim da S22, mantido na S23, S24, S25). Container de teste rumo_postgres_test na porta 5433.

⚠️ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).
Estrutura do repo (referência — conferir, não assumir)
text

D:\Rumo
├── .vscode/settings.json
├── backend/        (venv em backend/venv, Python 3.13.7)
│   ├── alembic/
│   ├── app/
│   │   ├── core/  models/  routers/  schemas/  services/
│   │   └── __pycache__/
│   ├── samples/
│   ├── scripts/
│   ├── tests/      (conftest.py + test_calories + test_comment + test_export
│   │               + test_export_bulk + test_follow + test_like + test_stats)
│   ├── _scratch/
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs/HANDOFF.md
├── mobile/lib/     (models/  pages/  services/  widgets/)
├── web/src/        (api/  assets/  components/  contexts/  hooks/  lib/  pages/  types/)
└── README.md       ← NOVO na S25

Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Contas de teste

    prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 6 atividades, 26.443 m.

    Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).
Acordos de trabalho (válidos em todas as sessões — reforçados na S21/S22/S23/S24/S25)

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

    Entregar conteúdo de arquivo para colar sem cerca ```markdown ``` — arquivo inteiro como único texto (S25e).

Processo que o usuário elogiou na S21–S24 (para manter)

    Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 4 (validação em produção) → Fase 5 (handoff).

    Descoberta antes de codar: pedir arquivos com motivo declarado.

    Validação entre cada entrega.

    Contrato travado escrito antes de codar.

    Commits pequenos e temáticos.

    Validação em produção separada da local.

    Diagnóstico honesto antes de "consertar".

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 164 testes passando LOCALMENTE, 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon, minLat, maxLon, maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax no mesmo SELECT (sem N+1).

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (_ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor. CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona com ou sem rota). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422; omitido → default csv.

Export em lote (S22): GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). format=csv: inclui todas; format=gpx: só com rota. Filtro from/to inclusivo (UTC). 0 atividades → 200 + ZIP vazio. from > to → 422. format inválido → 422.

Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet (RouteMap no detalhe) + recharts (gráficos no perfil). S21: botões "Baixar CSV" (sempre) e "Baixar GPX" (condicional a track) no cabeçalho do ActivityDetailPage. S23: card "Exportar tudo" no ProfilePage (só isSelf). S24: aviso "Se nenhuma atividade casar com o período, o ZIP virá vazio." + feedback "Download iniciado." por ~4s.

S25 (esta sessão):

    ActivityDetailPage.tsx agora importa RouteMap via React.lazy + Suspense (fallback de 24rem). RouteMap é named export, resolvido com .then(m => ({ default: m.RouteMap })). Validado local (npm run build gera RouteMap-BWdETDdy.js 2.41 kB) e em prod (index-DV3loxrJ.js com chunks novos).

    README.md na raiz (novo) com cheat sheet: estrutura, rodar local, endpoints, contas de teste, produção, stack com versões exatas, convenções rápidas.

    Tropeços da S25 (registrados): (1) Select-String -SimpleMatch com | literal → falso positivo de "README OK"; (2) pedi commit sem esperar validação do save → git commit "nothing to commit"; (3) entreguei README com cerca ```markdown ``` → usuário colou a resposta inteira → "Passo 1/2/3" vazou pro arquivo. Regras S25a–S25e nasceram desses erros.

Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite), alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds. Intocado desde a S11. Sem drill-down de stats, sem export.

Estado final da S25:

    git log: 4146c3a docs: corrige README (remove instrucoes de sessao por engano) no topo, eb9ae35 docs: README com cheat sheet de endpoints e comandos, 1fbcf0e feat(web): RouteMap com React.lazy no detalhe (Sessao 25), a485eab feat(web): feedback de sucesso no exportar tudo (Sessao 24).

    Vercel: index-DV3loxrJ.js com chunks ActivityDetailPage-J23GpMg5.js, ProfilePage-Bfp0kvA2.js, SearchPage-CvOmHzdZ.js dentro (todos novos ≠ S24).

    2a validado local + prod. 2b (README) commitado em eb9ae35 + corrigido em 4146c3a. Nada pendente.

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

    Deps novas em S25: nenhuma.

Git (estado ao fim da Sessão 25)
text

4146c3a (HEAD -> main, origin/main) docs: corrige README (remove instrucoes de sessao por engano)
eb9ae35 docs: README com cheat sheet de endpoints e comandos
1fbcf0e feat(web): RouteMap com React.lazy no detalhe (Sessao 25)
a485eab feat(web): feedback de sucesso no exportar tudo (Sessao 24)
f1ff9f0 docs: handoff da Sessao 23
db092ce feat(web): botao exportar tudo no perfil (Sessao 23)
18efeb0 docs: handoff da Sessao 22
6cce475 feat(activities): export em lote CSV/GPX em ZIP (Sessao 22)
ad7b99a docs: handoff da Sessao 21
ee3215b feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21)
8936415 feat(activities): export CSV/GPX (Sessao 21)

Pendente: docs/HANDOFF.md da S25 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 25.
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 25
3.1 Fase 0 — validação de estado inicial

Tudo verde (git, build, lint, analyze, docker -a, pg_isready, pytest 164, ruff, detecção de prod com index-DzwYSsIb.js + ProfilePage-MTSjQTtf.js da S24). Nenhum falso positivo.
3.2 Fase 2 — contrato travado (OPÇÃO 2a + 2b)

2a — RouteMap com React.lazy(). RouteMap é named export; único consumidor é ActivityDetailPage. lazy fica no consumidor, RouteMap não muda. Fallback <Suspense> de 24rem.

2b — README.md na raiz com cheat sheet. Aditivo, zero mudança de código.
3.3 Fase 1 — descoberta

Pedidos: RouteMap.tsx, ActivityDetailPage.tsx, Select-String -Pattern "RouteMap" -List (confirmou único consumidor), web/package.json, mobile/pubspec.yaml (versões exatas).
3.4 Fase 3 — entrega incremental

Arquivo 1/1 — web/src/pages/ActivityDetailPage.tsx entregue completo. Mudanças: import { lazy, Suspense, useState } from "react", const RouteMap = lazy(() => import("../components/RouteMap").then((m) => ({ default: m.RouteMap }))), <Suspense fallback={...}> com <div> de 24rem + "Carregando mapa…". Validação: Select-String confirmou 5 matches; npm run build → 824 modules, RouteMap-BWdETDdy.js 2.41 kB novo, ActivityDetailPage-CjI4Jf2W.js caiu de 13.00 → 11.38 kB; npm run lint limpo.

Nota importante: o index-*.js continuou com 435.82 kB (mesmo tamanho) porque o leaflet já era um chunk separado (leaflet-Bw7RoR_1.js 163.60 kB) desde antes. O lazy não tira o leaflet do index (ele nunca esteve lá) — tira o código do RouteMap do chunk do detalhe (2.41 kB) e faz o leaflet só baixar quando o mapa renderiza. Ganho real, mas menor do que eu prometi na Fase 2. Corrigi a expectativa no próprio resumo da S25.
3.5 Fase 3.5 — commit + push (2a)

git status --short: M web/src/pages/ActivityDetailPage.tsx. git add + git commit → 1fbcf0e feat(web): RouteMap com React.lazy no detalhe (Sessao 25) (1 file, +22/−5). git push OK.
3.6 Fase 3.6 — README (2b) entregue e commitado (COM TROPEÇO)

Entreguei o README.md completo dentro de uma cerca ```markdown ... ```, seguido de instruções ("Validação", "Passo 1/2/3", "Próximo passo"). O usuário colou a resposta inteira, incluindo as instruções. O README.md salvo virou uma mistura de conteúdo + "Passo 1/2/3" no final, com a formatação Markdown quebrada (fences virando text, pipes virando tabulação).

O commit eb9ae35 docs: README com cheat sheet de endpoints e comandos foi feito com esse conteúdo errado. O git status estava vazio (o usuário rodou git add + git commit sem o save ter pego, ou antes do save — o hash-object e HEAD:README.md eram idênticos: 96d56c32...).
3.7 Fase 3.7 — diagnóstico do README (várias idas e voltas)

    Tentativa 1 (minha): vi $lines[-1] = "Passo 3..." → disse "corrompido". Certo na observação.

    Tentativa 2 (minha, errada): Select-String -SimpleMatch "Passo 1|Passo 2|Passo 3|..." → vazio → disse "não, está OK". Errado: -SimpleMatch com | é literal.

    Tentativa 3 (minha, correta): Select-String -Pattern "Passo" (sem -SimpleMatch) → 3 matches. Confirmado corrompido.

    Tentativa 4 (minha, correta): entreguei README sem cerca (arquivo inteiro como único texto). O usuário colou só o conteúdo (desta vez funcionou).

    Validação final: última linha = bullet git restore ✅; Select-String "Passo" vazio ✅; total 116 linhas ✅; git status mostrou M README.md ✅; git commit → 4146c3a docs: corrige README... (1 file, +14/−51); git push OK; HEAD == origin/main == 4146c3a; working tree limpo.

3.8 Fase 4 — validação em produção (Vercel S25)

git push (S25, antes do fix do README). Start-Sleep 90. index-DV3loxrJ.js (novo ≠ S24). Chunks novos dentro: ActivityDetailPage-J23GpMg5.js, ProfilePage-Bfp0kvA2.js, SearchPage-CvOmHzdZ.js. Bundle da S25 no ar, confirmado. O RouteMap-BWdETDdy.js não aparece no __vite__mapDeps do index porque é carregado por dentro do ActivityDetailPage via import() dinâmico — comportamento esperado do lazy.
3.9 Tropeços e correções (S25)

    Select-String -SimpleMatch com | literalizou a busca → falso positivo de "README OK". Corrigido com Select-String -Pattern "Passo" (sem -SimpleMatch). REGRA S25a.

    Pedi commit sem esperar validação do save → git commit "nothing to commit", git status vazio, hash-object == HEAD:README. Corrigido exigindo hash-object ≠ HEAD:README + git status mostrando M antes de commitar. REGRA S25c + S25d.

    Entreguei README com cerca ```markdown ``` e instruções na mesma resposta → usuário colou a resposta inteira, "Passo 1/2/3" vazou pro arquivo. Corrigido entregando o arquivo sem cerca, como único texto da resposta. REGRA S25e.

3.10 Resultado da suíte (S25)

pytest -q → 164 passed (mantido). ruff → All checks passed. npm run build → 824 modules verde (RouteMap-BWdETDdy.js 2.41 kB). npm run lint limpo. flutter analyze No issues. Sem teste novo (feature é de UI/config, sem lógica de backend nova).
3.11 Commits pushados (S25)

    1fbcf0e feat(web): RouteMap com React.lazy no detalhe (Sessao 25) — 1 file, +22/−5.

    eb9ae35 docs: README com cheat sheet de endpoints e comandos — 1 file, +153 (com lixo).

    4146c3a docs: corrige README (remove instrucoes de sessao por engano) — 1 file, +14/−51.

Pendente: docs: handoff da Sessao 25 (este arquivo).
SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT)

    Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota".

    Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { ..., bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL.

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21

    Permissão: dono OU seguidor do dono. Caso contrário, 404.

    format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.csv". 1 header + 1 linha. Funciona com/sem rota (bbox_* vazios se sem rota).

    format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…">. Exige rota → 404 "Atividade não possui rota" se route IS NULL.

    format inválido → 422 (Literal do Pydantic).

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22

    Auth: self-only.

    Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos, cada um no formato unitário.

    format=csv (default): ZIP com N .csv (todas do filtro, com/sem rota). format=gpx: ZIP com N .gpx (só com rota).

    Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422 "from deve ser <= to"; format inválido → 422.

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary.

GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.

GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.

GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. period/compare inválidos → 422. previous null para period="all" ou tipo ausente na janela.

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

Sessões 9–25 commitadas e pushadas. HEAD == origin/main == 4146c3a. Working tree limpo.

Pendente: este handoff.
Primeira ação da S25 (se ainda não feita)
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

Se aparecer M docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 25"
git push
git --no-pager log --oneline -4
git status --short

Esperado depois: HEAD == origin/main com docs: handoff da Sessao 25 no topo.
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 26 — primeira ação] Abrir PowerShell via Win+R → powershell

NÃO abrir de dentro do VS Code / Windows Terminal.
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

[Sessão 26 — primeira ação] Commitar handoff S25 (se ainda não foi)
powershell

cd D:\Rumo
git status --short
# Esperado: M docs/HANDOFF.md
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 25"
git push
git --no-pager log --oneline -4
git status --short

[Sessão 26 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 26 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"      # ATENÇÃO: -a, não só ps
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
# Se o prompt já mostra (venv), PULE a linha abaixo.
.\venv\Scripts\Activate.ps1      # UM ponto, NÃO dois
python -m pytest -q              # esperado: 164 passed
ruff check .

[Sessão 26 — primeira ação] Detecção de versão em produção (S25)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24).
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+\.js'

# Esperado na S25 (registro histórico): index-DV3loxrJ.js com chunks
# ActivityDetailPage-J23GpMg5.js, ProfilePage-Bfp0kvA2.js, SearchPage-CvOmHzdZ.js.
# O RouteMap-BWdETDdy.js NÃO aparece no __vite__mapDeps do index — é carregado
# por dentro do ActivityDetailPage via import() dinâmico. Comportamento esperado.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Detecção de versão em produção (backend S22 — export em lote)
powershell

$openapi = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json"
$hasBulkExport = $openapi.paths.PSObject.Properties.Name -contains "/activities/export"
Write-Host "rota /activities/export no ar: $hasBulkExport"
if (-not $hasBulkExport) {
  Write-Host "RENDER AINDA NAO REDEPLOYOU. Aguardar 1-3 min ou Manual Deploy no dashboard."
}

# Teste real do ZIP (auth)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$tmp = [System.IO.Path]::GetTempFileName()
try {
  $r = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/export?format=csv" -Headers @{Authorization="Bearer $token"} -UseBasicParsing
  Write-Host "CSV default: $($r.StatusCode) $($r.Headers['Content-Type'])"
  [System.IO.File]::WriteAllBytes($tmp, $r.Content)
  $zip = [System.IO.Compression.ZipFile]::OpenRead($tmp)
  Write-Host "  entries: $($zip.Entries.Count)"
  $zip.Dispose()
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "CSV FALHOU: $($resp.StatusCode.value__) - $($reader.ReadToEnd())"
}

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
git status --short <arquivo>                                   # "M" se modificado, vazio se igual ao HEAD
git --no-pager log --oneline -3 -- <arquivo>                    # último commit que tocou
# Se o último commit for anterior à mudança quebrada:
git restore <arquivo>
# Se a versão quebrada JÁ foi commitada:
git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22)
powershell

# 1) openapi.json — a rota está no ar?
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"
# Se vazio: Render não redeployou. Aguardar ou Manual Deploy.
# 2) se a rota está no ar mas retorna 422, ver o BODY do erro:
try {
  Invoke-WebRequest -Uri "<url>" -Headers $h -UseBasicParsing | Out-Null
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "STATUS $($resp.StatusCode.value__): $($reader.ReadToEnd())"
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24)
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+\.js'
# hash novo → bundle novo no ar
# hash do S24 (DzwYSsIb/MTSjQTtf/CHf94jpD/Czd3J0lL) → Vercel não redeployou: aguardar 90s

Diagnóstico de save de arquivo (lição S25 — NOVA)
powershell

# Depois de salvar, ANTES de commitar:
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
# Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou (ou você commitou antes).
# Se [5] != [6] e [4] mostra ' M' → save pegou, pode commitar.

SEÇÃO 7 — DÍVIDAS TÉCNICAS

    (FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.

    (FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.

    (FECHADA na S25) ~~RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy()~~ — RouteMap agora é lazy no ActivityDetailPage.

    (CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.

    (CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.

    (CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.

    (CONHECIDA — Sessão 17–25) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.

    (CONHECIDA — Sessão 17–25) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. NÃO é bug.

    (CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática.

    (CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk". Testes usam activity.activity_type.value dinâmico.

    (CONHECIDA — Sessão 21) to_gpx não emite <time> por <trkpt> (a geometria em route é só LineString, sem stream temporal). Strava/Garmin aceitam.

    (CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. YAGNI por enquanto.

    (CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries. Aceitável para export raro.

    (CONHECIDA — Sessão 22) Export em lote é self-only. Decisão de privacidade.

    (CONHECIDA — Sessão 23) downloadActivityExportBulk valida from > to client-side. Dupla validação proposital.

    (CONHECIDA — Sessão 24) Feedback "Download iniciado." é mostrado quando await downloadActivityExportBulk(...) resolve. Não detecta ZIP vazio.

    (CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).

    (CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado (leaflet-Bw7RoR_1.js 163.60 kB) desde antes. Tira o código do RouteMap (2.41 kB) do chunk do ActivityDetailPage e faz o leaflet baixar só quando o mapa renderiza. Ganho modesto e legítimo.

    (Oportunidade — S21–S25) RouteMap agora é lazy — se um segundo consumidor aparecer, considerar Suspense compartilhado.

    (Oportunidade — S18–S25) Delta "vs. anterior / vs. ano anterior" cobre 3 métricas. Extensão trivial.

    (Oportunidade — S18–S25) Semântica do delta é NEUTRA. Sem "melhor/pior".

    (Oportunidade — S19–S25) Stats públicas só quando viewer segue o alvo.

    (Oportunidade — S21–S25) Export com timestamps por ponto.

    (Oportunidade — S22–S25) Export em lote no mobile.

    (Oportunidade — S22–S25) Export em lote concatenado (1 CSV + 1 GPX).

    (Oportunidade — S24/S25) Detectar ZIP vazio no client via DecompressionStream ou lib.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 26 e além)

Sessão 25 fechada. Feature de export 100% completa (backend S21+S22, front S21+S23+S24). Resíduos de baixo risco (2a+2b) entregues. Nenhuma pendência de código.
Primeira ação obrigatória da Sessão 26

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 26 — primeira ação]": git push, log, status; commitar handoff S25 se pendente.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (docker ps -a, pg_isready, pytest -q → 164, ruff check).

    Detecção de versão em produção (front S25): baixar index-DV3loxrJ.js e confirmar chunks novos.

Escolha para a Sessão 26 (opções)

OPÇÃO 1 — Fechar ciclo e começar a próxima feature com calma (RECOMENDADA).

    Commitar este handoff.

    Escolher a próxima feature a partir da Seção 7.

    Estado: repo limpo, prod verde, 164 testes. Caminho de menor risco.

OPÇÃO 2 — Export com timestamps por ponto (S21–S25 oportunidade).

    to_gpx lê raw_track_points em vez de route. Muda contrato do GPX (adiciona <time> por <trkpt>). Sessão média, backend + teste + front (regenerar GPX).

OPÇÃO 3 — Detectar ZIP vazio no client.

    DecompressionStream em client.ts (ou dep pequena), downloadActivityExportBulk retorna {entries: N}. UI mostra mensagem pós-download real. ~1h. Só se houver demanda.

OPÇÃO 4 — Export no app mobile (paridade com web).

    Mobile parado desde S11. Sessão grande. Só se houver demanda real.

OPÇÃO 5 — Melhorias incrementais de stats (delta em tempo/calorias, semântica melhor/pior).

    Extensão trivial da S18. Sessão pequena.

Recomendação final para a Sessão 26

Antes de escolher, validar estado (Seção 8 — primeira ação). Se tudo verde, escolher.

Rota recomendada: OPÇÃO 1 — fechar ciclo e começar a próxima feature com calma. Motivos: feature de export 100% fechada há 2 sessões, resíduos de baixo risco entregues na S25, contexto da S25 já foi usado. Começar S26 com repo limpo é o melhor caminho para escolher a próxima feature a partir da lista de oportunidades da Seção 7.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 26 neste mesmo formato (seções 0 a 9).
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25 (abertura): reforçou os mesmos acordos. E ao longo da sessão, tolerou com paciência os 3 tropeços (Select-String mal desenhado, commit sem validação, README com cerca vazando instruções) — sem reclamar, apenas reportando o output. Registrei cada um como regra (S25a–S25e).

Pedido para o assistente da S26 (e além): manter o processo da S21–S25. Concretamente:

    Fase 0 obrigatória: validar estado (git, build, lint, analyze, docker -a, pytest, detecção de versão em prod) antes de tocar em código.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — regra S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (front) entre cada entrega.

    Fase 4 — validação em produção: local verde é pré-requisito; prod via HTTP/browser é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js e procurar o chunk (front) antes de acusar bug. Se hash antigo aparecer, aguardar 90 s (REGRA S24).

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir.

Regras novas da S25 (Seção 0, itens 14–18): Select-String -SimpleMatch não aceita |; confirmar $lines[-1] suspeito com Get-Content | Select-Object -Last N; exigir output de validação antes de pedir commit; teste definitivo do save é git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M; entregar conteúdo de arquivo para colar sem cerca ```markdown ``` — arquivo inteiro como único texto.

O que funcionou nas S21–S25 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal, não na previsão.