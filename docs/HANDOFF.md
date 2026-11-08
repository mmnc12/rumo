HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 23
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo com Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

Sessões anteriores perderam tempo porque o assistente tentou "adivinhar" a árvore de diretórios e errou. Não repetir.
⚠️ REGRA S21 — nunca placeholder no código entregue

A S21 teve dois tropeços causados pela mesma causa raiz: eu entreguei um bloco com # ... (resto do arquivo INALTERADO ...) como "rascunho didático". O usuário colou no activity_service.py (arquivo grande) e sobrescreveu tudo. Recuperado com git restore.

Regra permanente: quando eu não tiver o conteúdo de um arquivo existente, NÃO entrego nem "rascunho de bloco". Peço o arquivo (Get-Content -Encoding UTF8) e só entrego completo, pronto para Ctrl+A → colar → salvar. Nunca marcador no meio do código. É o único jeito de eliminar esse tipo de erro.
⚠️ REGRA S21 — não adivinhar nomes de símbolos do projeto

No test_export.py, escrevi ActivityType.run (era ActivityType.RUN) e Follow(followed_id=...) (era following_id=...). O ruff não pega (é semântico, não sintático) — só o pytest pegou.

Regra permanente: antes de escrever teste ou código que referencia símbolo de model/enum/schema do projeto, peça o arquivo (models/activity.py, models/follow.py, schemas/activity.py, etc.). É barato (são pequenos) e elimina a classe de erro.
⚠️ REGRA S21 — git status antes de qualquer git restore/git checkout

Sempre rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo> antes de tentar restaurar. Se o último commit que tocou o arquivo for anterior à mudança quebrada, git checkout/git restore restaura. Se a versão quebrada já foi commitada, git show <commit-anterior>:<caminho> > <caminho> é o caminho.
⚠️ REGRA S22 (nova) — Invoke-WebRequest com -UseBasicParsing

O PowerShell 5.1 emite prompt de segurança ("Risco de Execução de Script") em Invoke-WebRequest sem -UseBasicParsing. Sempre entregar Invoke-WebRequest com -UseBasicParsing — elimina o prompt e não muda nada para CSV/GPX/ZIP (texto/binário puro).
⚠️ REGRA S22 (nova) — validar deploy do Render antes de acusar bug no código

Na S22, os primeiros Invoke-WebRequest para /activities/export retornaram 422 e eu quase abri diagnóstico de bug. Causa: o Render ainda não tinha terminado o redeploy do commit. Regra permanente: depois de git push, aguardar o redeploy do Render terminar antes de validar produção. Sinal objetivo: Invoke-RestMethod https://rumo-api-5s0b.onrender.com/openapi.json | Select-String "<rota nova>" — se a rota aparecer no openapi.json, o deploy está no ar. Alternativa: dashboard do Render → "Events"/"Deploys" → ver o commit como Live. Se der 404/422 em rota nova após push, primeiro checar openapi.json, depois acusar código.
⚠️ REGRA S23 (nova) — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele

Na S23, tentei `Select-String -Pattern "ProfilePage-"` no HTML da Vercel e não achou nada — o HTML referencia só o index-*.js; o ProfilePage-<hash>.js aparece dentro do index como import dinâmico. O teste correto:

    $html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
    $m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
    $idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
    $idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
    $idx.Content | Select-String -Pattern 'assets/ProfilePage-[A-Za-z0-9_-]+\.js'

Se o hash do ProfilePage bater com o build local (ex.: BPFFRQ5R), é o commit local. Se for diferente, é a Vercel buildando com envs de prod — ambos são "novo". Se for o hash antigo, Vercel não redeployou.
O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos — o usuário precisa colar conteúdo e saídas de terminal.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app). Backend de produção usa Postgres/PostGIS gerenciado. Testar via HTTP é sempre possível.

IMPORTANTE — usuário NÃO tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam automaticamente, validar via HTTP em produção. Não presumir que o usuário vai "rodar o app localmente" para testar UI.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (164 passed ao fim da S22; mantido 164 na S23 — nenhum teste novo adicionado, nenhuma regressão). Container de teste rumo_postgres_test na porta 5433.

⚠️ ATENÇÃO — docker ps sozinho esconde container parado. Primeira verificação da S24+ deve ser docker ps -a --filter "name=rumo_postgres_test" (com -a), não só docker ps.

Para reativar numa sessão nova:

    Abrir Docker Desktop e esperar a baleia verde.

    Garantir que o terminal foi aberto via Win+R (fora do VS Code / Windows Terminal).

    cd D:\Rumo\backend

    docker compose -f docker-compose.test.yml up -d

    docker ps -a --filter "name=rumo_postgres_test" (deve mostrar Up … (healthy))

    docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432 (deve dizer accepting connections)

    .\venv\Scripts\Activate.ps1 (UM ponto, não dois)

    python -m pytest -q

VENV: ao fim da S22, a única venv é D:\Rumo\backend\venv (sem ponto), Python 3.13.7. .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"].

ATENÇÃO: py -3 deste Windows aponta para Python 3.14 (incompatível com requirements.txt). Se precisar recriar a venv: py -3.13 -m venv D:\Rumo\backend\venv ou C:\Python313\python.exe -m venv D:\Rumo\backend\venv.
Estrutura do repo (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)

Árvore de alto nível REAL, confirmada na Sessão 19 e inalterada em estrutura na S20/S21/S22/S23 (só arquivos modificados/criados, nenhum removido):
text

D:\Rumo
├── .vscode
│   └── settings.json
├── backend
│   ├── .pytest_cache
│   ├── .ruff_cache
│   ├── venv\                      # ATIVA (Python 3.13.7)
│   ├── alembic
│   ├── app
│   │   ├── core
│   │   ├── models                  # activity.py, follow.py, user.py, like.py,
│   │   │                          # comment.py, notification.py, activity_photo.py
│   │   ├── routers\               # activities.py, auth.py, comments.py, feed.py,
│   │   │                          # notifications.py, photos.py, users.py, __init__.py
│   │   ├── schemas\               # activity.py, like.py, stats.py, user.py, ...
│   │   ├── services\              # activity_service.py, comment_service.py, errors.py,
│   │   │                          # feed_service.py, fit_service.py, follow_service.py,
│   │   │                          # gpx_service.py, like_service.py, notification_service.py,
│   │   │                          # photo_service.py, stats_service.py, user_service.py
│   │   └── __pycache__
│   ├── samples
│   ├── scripts
│   ├── tests\                     # conftest.py + test_calories.py + test_comment.py +
│   │                              # test_export.py + test_export_bulk.py (NOVO S22)
│   │                              # + test_follow.py + test_like.py + test_stats.py + __init__.py
│   ├── _scratch
│   ├── docker-compose.test.yml
│   ├── pytest.ini
│   └── requirements.txt
├── docs
│   └── HANDOFF.md
├── mobile
│   └── lib
│       ├── models\                # activity.dart, activity_track.dart, comment.dart
│       ├── pages\                 # activity_detail_page.dart, feed_page.dart, login_page.dart
│       ├── services
│       └── widgets\               # activity_map.dart, like_button.dart
└── web
    └── src
        ├── api\                   # activities.ts, auth.ts, client.ts, notifications.ts,
        │                          # photos.ts, social.ts, stats.ts
        ├── assets
        ├── components\            # ActivityCard, ActivityResults, AppHeader, CommentsSection,
        │                          # LikeButton, NotificationBell, PeriodChart, PhotoGallery,
        │                          # PhotoUpload, ProtectedRoute, RouteMap, StatsCards, UserResults
        ├── contexts
        ├── hooks\                 # useActivities, useActivitySearch, useAuth, useDebounce,
        │                          # useNotifications, usePhotos, useProfile, useSocial,
        │                          # useStats, useUserSearch
        ├── lib\                   # format.ts, geo.ts
        ├── pages\                 # ActivitiesPage, ActivityDetailPage, FeedPage, LoginPage,
        │                          # NotificationsPage, ProfilePage, RegisterPage, SearchPage, UploadPage
        └── types\                 # api.ts

Como rodar comandos Flutter no Windows deste usuário

Flutter instalado em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7 / DevTools 2.60.0.

PROBLEMA CONHECIDO: mesmo com C:\Users\nasci\flutter\bin no PATH, o PowerShell frequentemente NÃO reconhece flutter (cache de sessão). SOLUÇÃO QUE FUNCIONA: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Como rodar Docker e pytest local (Windows deste usuário)

Docker Desktop instalado em C:\Users\nasci\AppData\Local\Programs\DockerDesktop. Se docker não for reconhecido, abrir PowerShell via Win+R → powershell.

Container de teste: rumo_postgres_test (5433). Containers permanentes rumo-redis (6379) e rumo-postgres (5432) NÃO são de teste.
Como testar o backend de produção sem o app (PowerShell)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me. /users/me devolve 422.
powershell

$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer $token" }
$meId = $me.id

Contas de teste:

    prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341 (6 atividades, 26.443 m).

    Prod2 (id 01a141e7-5ea4-7600-8959-19145475ad0a) — 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

    Para o cenário "terceiro NÃO seguido": usar a busca (/users/search?q=a) e escolher um id que não seja prod nem Prod2.

⚠️ Lições S18–S23 — detecção de versão no ar:

    422 de versão NÃO distingue S17 de S18. /activities/stats/by-type?period=30d devolve 422 desde a S17.

    Para S19: GET /users/{meId}/stats/summary responde 200 (não 404) e GET /users/me responde 422.

    Para S20: GET /activities/stats/by-type?period=90d&compare=yoy responde 200. E ?compare=xpto responde 422.

    Para S21: GET /activities/{id}/export?format=csv e ?format=gpx respondem 200; ?format=xpto responde 422. Se der 404 em format=csv num id válido, o backend ainda está na S20.

    Para S22: GET /activities/export?format=csv responde 200 application/zip (ZIP com N .csv dentro); GET /activities/export?format=gpx responde 200 application/zip (só com rota); ?format=xpto responde 422; ?from=2099-01-01 responde 200 com ZIP vazio (0 entries); ?from=2026-12-01&to=2026-01-01 responde 422. Se der 422 em format=csv sem filtro, checar openapi.json primeiro (deploy do Render pode não ter terminado).

    Para S23 (front): a validação correta é baixar o index-*.js e procurar assets/ProfilePage-<hash>.js dentro dele (ver REGRA S23 acima). O bundle novo contém downloadActivityExportBulk (minificado como ya ou similar) dentro do index. Se o hash do ProfilePage for o antigo (D83pyXao), Vercel não redeployou.

⚠️ Lição S20/S21/S22/S23 — previous: null em prod/Prod2 não é bug. Nenhuma das contas de teste tem atividade na janela de comparação. Os 164 testes locais provam que a janela funciona.
O que o assistente precisa pedir ao usuário (não tem acesso a arquivos)

    Conteúdo de arquivos via Get-Content -Encoding UTF8 <caminho>. SEMPRE passar -Encoding UTF8; sem isso, acentos viram inÃ­cio.

    Saídas de comandos (flutter analyze, npm run build, git log, git status, pytest -q, ruff check).

    Nunca assumir estrutura "de cabeça": pedir o arquivo antes de reescrevê-lo.

ATENÇÃO — arquivos truncados/duplicados: se um Get-Content vier com a última linha cortada OU com o conteúdo DUPLICADO, NÃO adivinhar o final. Pedir ruff check <arquivo> (lista duplicatas de uma vez) e entregar o arquivo completo para Ctrl+A → colar → salvar.

ATENÇÃO — arquivo "salvo" que não salvou. SINTOMA: build ou pytest falha dizendo que um símbolo novo não existe, mesmo o assistente tendo entregado o arquivo. DIAGNÓSTICO: Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>". Se não aparecer, o disco ainda é o antigo. REGRA: depois de entregar um arquivo que muda contrato, pedir a confirmação com Get-Content | Select-String antes de rodar build/test.

ATENÇÃO — git diff pipeado no PowerShell pode exibir acentos como mojibake. Artefato de codepage do pipe, NÃO corrupção.

ATENÇÃO — git log --oneline no PowerShell às vezes cola a última linha com o prompt. Formatação, não corrupção.

ATENÇÃO — git log sem --no-pager abre o less e trava o terminal. SEMPRE usar git --no-pager log ... ou prefixar com $env:PAGER="".

ATENÇÃO — Pylance reclamando de imports (fastapi/sqlalchemy/pytest) NÃO é erro de código. Interpretador errado. Causa raiz corrigida na S20: .vscode/settings.json aponta para backend/venv + python.analysis.extraPaths: ["${workspaceFolder}/backend"]. Se voltar: Ctrl+Shift+P → "Python: Select Interpreter" → D:\Rumo\backend\venv\Scripts\python.exe → Developer: Reload Window.

ATENÇÃO — Invoke-WebRequest sem -UseBasicParsing pergunta sobre risco de execução de script. Responder a (Sim para Todos) funciona, mas entregar Invoke-WebRequest sempre com -UseBasicParsing elimina o prompt.

ATENÇÃO — validar openapi.json antes de acusar bug em rota nova. Se git push acabou de acontecer e uma rota nova responde 422/404, é quase certo que o Render ainda não redeployou. Confirmado na S22.

ATENÇÃO — validar bundle da Vercel buscando o chunk dentro do index-*.js (REGRA S23). HTML só referencia index-*.js; os chunks aparecem dentro dele como import dinâmico.
Acordos de trabalho (válidos em todas as sessões — REFORÇADOS na S21/S22/S23)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário. (Usuário reforçou nas S15–S23.) O assistente decide e recomenda; não fica perguntando "qual opção você prefere?".

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder no meio do código. Preservar imports, comentários e trechos que já funcionam. Destacar o trecho alterado com comentário curto acima (// [Sessão N] ou // [Sessão N — fix]).

    UMA versão por arquivo por resposta. Se errar no meio do raciocínio, cortar a versão errada e entregar só a corrigida com nota de 1 linha. NUNCA duas versões do mesmo arquivo na mesma resposta.

    HANDOFF PREVENTIVO em ~70–80% do limite de contexto: parar o trabalho em curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 9), pronto para colar no próximo chat. Deve ser COMPLETO e bem explicado, não resumido. (Usuário reforçou explicitamente na abertura da S23.)

    VALIDAÇÃO INCREMENTAL: quando a mudança toca mais de um arquivo da mesma stack, colar o(s) arquivo(s) base e rodar build/analyze antes de entregar o próximo — reduz superfície de erro. Exceção legítima: 2 arquivos acoplados por mudança de contrato interno (ex.: hook + consumidor do hook). Nesse caso, entregar os 2 juntos e rodar 1 build.

    VERIFICAR SAVE ANTES DE BUILD: quando o assistente entrega um arquivo com símbolo novo (tipo, função, param), pedir ao usuário Get-Content -Encoding UTF8 <caminho> | Select-String -Pattern "<simbolo>" antes de rodar build/test.

    (S21) NUNCA placeholder no código entregue. Se o assistente não tem o conteúdo de um arquivo existente, peça e espere — não entregue "rascunho de bloco".

    (S21) Não adivinhar nomes de símbolos. Antes de referenciar ActivityType.X, Follow(...), campos de schema, etc., peça o arquivo do model/enum/schema. ruff não pega, pytest pega com traceback claro — mas custa ida e volta.

    (S21) Antes de git restore/git checkout, rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>. Confirmar que o último commit que tocou o arquivo é anterior à mudança quebrada.

    (S22) Invoke-WebRequest sempre com -UseBasicParsing.

    (S22) Depois de git push, aguardar redeploy do Render e validar openapi.json antes de acusar bug em rota nova.

    (S23) Para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele (REGRA S23). Nunca procurar "ProfilePage-" direto no HTML.

Processo que o usuário elogiou na S21/S22 (para manter)

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho." Na abertura da S23, reforçou: "sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

O que funcionou:

    Ordem clara: Fase 0 (validação de estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 4 (validação em produção) → Fase 5 (handoff).

    Descoberta antes de codar: pedir os arquivos com motivo declarado. Cada pedido justificado.

    Validação entre cada entrega: Select-String (save) + ruff + pytest no backend; npm run build + npm run lint no front. Nunca acumular 2 arquivos sem validar.

    Contrato travado escrito antes de codar: endpoint, auth, 404 vs 422, headers, formato. O usuário lê e aprova tacitamente.

    Commits pequenos e temáticos: docs: handoff da Sessao N, feat(activities): ..., feat(web): ....

    Validação em produção separada da local: local verde é pré-requisito, mas prod via HTTP/browser é o que fecha.

    Diagnóstico honesto antes de "consertar": quando o 422 apareceu em /activities/export (S22), o correto foi pedir o BODY e o openapi.json — não presumir bug. Na S23, o "ProfilePage-" não achado no HTML foi má escolha de teste, não bug de deploy — corrigido baixando o index e procurando dentro dele.

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 164 testes passando LOCALMENTE, 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax do PostGIS no mesmo SELECT (sem N+1). None quando route é NULL.

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (helper _ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor (mesma regra do /track; senão 404). Response com Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>". CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona sem rota, bbox_* vazios). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422. format omitido → default csv.

Export em lote (S22): GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only. Saída é ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip") com N arquivos dentro, cada um no formato unitário (rumo_<id>_<type>.csv ou .gpx). format=csv: inclui todas (com ou sem rota). format=gpx: só com rota (omite sem rota). Filtro from/to inclusivo (UTC, to inclui o dia inteiro). 0 atividades → 200 + ZIP vazio. from > to → 422. format inválido → 422.

Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet (RouteMap no detalhe) + recharts (gráficos no perfil). Drill-down por tipo com segmented control de janela temporal (S17), coluna "vs. anterior" com delta colorido (S18), 2º segmented control "Comparar com:" (prev/yoy) que só aparece quando period !== "all" (S20). S21: botões "Baixar CSV" (sempre) e "Baixar GPX" (condicional a track) no cabeçalho do ActivityDetailPage. S23: card "Exportar tudo" no ProfilePage (só isSelf) — dropdown CSV/GPX + dois <input type="date"> opcionais (De/Até) + validação client-side de from>to + loading + erro inline. Helper apiFetchBlob em client.ts (aditivo, S21). downloadActivityExport em activities.ts (S21) e downloadActivityExportBulk (S23).

Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite), alternância Mapa/Satélite, miniatura no feed via CameraFit.bounds. Intocado desde a S11. Sem drill-down de stats, sem export.
Entregas da Sessão 23 (frontend — "Exportar tudo")

Arquivo 1/2 — web/src/api/activities.ts (completo, 157 insertions): adicionado bloco // ===== Export em lote — [Sessão 23] ===== com:

    DownloadActivityExportBulkParams { format, from?, to? }.

    async downloadActivityExportBulk(params) — monta URLSearchParams com format/from/to, chama apiFetchBlob("/activities/export?..."), reusa _triggerDownload; filename do Content-Disposition, fallback "rumo_export.zip".

Resto do arquivo idêntico à S21.

Arquivo 2/2 — web/src/pages/ProfilePage.tsx (completo): adicionado

    import { downloadActivityExportBulk, type ActivityExportFormat } from "../api/activities" com // [Sessão 23].

    const EXPORT_FORMATS: {label,value}[] no nível do módulo (CSV/GPX).

    5 estados: exportFormat, exportFrom, exportTo, exportLoading, exportError.

    async function handleExportAll — valida client-side from>to (mensagem "A data inicial não pode ser maior que a final."), setExportError(null), setExportLoading(true), try downloadActivityExportBulk({format, from||undefined, to||undefined}), catch ApiError/detail string → mensagem inline, finally setExportLoading(false).

    Bloco JSX dentro de {profile && (...)} condicional a isSelf: <div> com título "Exportar tudo", <p> explicativo, <select> CSV/GPX, dois <input type="date"> (De/Até), botão "Exportar tudo"/"Preparando…", <p> de erro condicional.

    Resto do arquivo idêntico à S22.

Nenhuma mudança em backend, mobile, types/api.ts, client.ts, ActivityDetailPage.

Estado final da S23:

    Commit 18efeb0 (handoff S22) no topo da main ao abrir.

    Commit db092ce feat(web): botao exportar tudo no perfil (Sessao 23) — 2 files, 157 insertions. Push OK.

    Vercel redeployou: bundle novo contém downloadActivityExportBulk (minificado) e ProfilePage-SP0KNqPy.js (hash diferente do antigo e do local). Validado via PowerShell baixando o index-*.js.

    pytest -q → 164 passed (mantido). ruff → All checks passed. npm run build → 824 modules. npm run lint → limpo. flutter analyze → No issues.

Pendente: validação no browser (Fase 4 da S23) — checklist na Seção 8.

SEÇÃO 2 — PRODUÇÃO E AMBIENTE

    Backend: https://rumo-api-5s0b.onrender.com

    Docs Backend: https://rumo-api-5s0b.onrender.com/docs

    Frontend Web: https://rumo-wheat.vercel.app

    Repo local: D:\Rumo

    Mobile: D:\Rumo\mobile

    Web: D:\Rumo\web (scripts: "build": "tsc -b && vite build", "lint": "eslint .")

    Flutter: 3.47.9 / Dart 3.13.7

    Docker Desktop: 4.93.0 (engine 29.8.1, compose v5.5.1)

    SO: Windows, PowerShell 5.1

    Python: 3.13.7 (venv em D:\Rumo\backend\venv) — NÃO usar 3.14

    Venv backend: D:\Rumo\backend\venv (ativa com .\venv\Scripts\Activate.ps1)

    Deps novas em S23: nenhuma.

Git (estado ao fim da Sessão 23, ANTES do commit do handoff)
text

db092ce (HEAD -> main, origin/main) feat(web): botao exportar tudo no perfil (Sessao 23)
18efeb0 docs: handoff da Sessao 22
6cce475 feat(activities): export em lote CSV/GPX em ZIP (Sessao 22)
ad7b99a docs: handoff da Sessao 21
ee3215b feat(web): botoes baixar CSV/GPX no detalhe (Sessao 21)
8936415 feat(activities): export CSV/GPX (Sessao 21)
19ebc3b docs: handoff da Sessao 20
2ca4c81 feat(web): toggle year-over-year no drill-down por tipo (Sessao 20)

Pendente: docs/HANDOFF.md da S23 (este arquivo) — usuário vai salvar e commitar como docs: handoff da Sessao 23 (instruções na Seção 5).

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 23
3.1 Validação de estado inicial (Fase 0)

PowerShell via Win+R. git push → Everything up-to-date. HEAD == origin/main == 18efeb0 (handoff S22 já commitado). git status --short vazio.

Build sanity: npm run build → 824 modules, ProfilePage 18.32 kB (idêntico à S22); npm run lint limpo; flutter analyze No issues found. Docker: rumo_postgres_test Up 4 hours (healthy), pg_isready OK. pytest -q → 164 passed (60.67s). ruff check . → All checks passed.

Produção: openapi.json contém /activities/export (True). Backend S22 no ar.

3.2 Fase 1 — descoberta

Pedidos ao usuário (todos com motivo):

    routers/activities.py completo — para confirmar o contrato exato do GET /export (nomes dos params via alias Pydantic, Literal, headers).

    activities.ts completo — para ver o padrão do downloadActivityExport (S21) e reusar _triggerDownload.

    client.ts completo — para confirmar apiFetchBlob (sem skipAuth — YAGNI).

    ProfilePage.tsx completo — alvo da UI.

    types/api.ts completo — para não inventar tipo novo.

Todos vieram completos, sem truncamento.

3.3 Fase 2 — contrato travado

Revisado contra o código real:

    Nome dos query params: "format", "from", "to" (alias="from", alias="to" no backend — o nome na URL é from/to, não from_/to_).

    Resposta ZIP: application/zip, filename rumo_export_<YYYYMMDD-HHMMSS>.zip.

    Erros: 422 em format inválido, from>to, data inválida.

    Auth: self-only (diferente do unitário).

    Front: apiFetchBlob já cobre (Authorization injetado); _triggerDownload reusado; sem tipo novo em types/api.ts; ProfilePage renderiza só isSelf.

Escopo travado em 2 arquivos (activities.ts + ProfilePage.tsx), client.ts intocado.

3.4 Fase 3 — entrega incremental

Arquivo 1/2 — activities.ts. Validação: Select-String (3 matches: interface + function + param); npm run build 824 modules verde (ProfilePage ainda 18.32 kB, esperado); npm run lint limpo.

Arquivo 2/2 — ProfilePage.tsx. Validação: Select-String (6 matches: downloadActivityExportBulk, EXPORT_FORMATS decl, handleExportAll decl, chamada, EXPORT_FORMATS.map, onClick={handleExportAll}); npm run build → ProfilePage 18.32 → 20.56 kB (o bloco novo entrou de fato); lint limpo.

3.5 Fase 3.5 — commit + push

git status --short: M web/src/api/activities.ts, M web/src/pages/ProfilePage.tsx.

git add <os dois> ; git commit -m "feat(web): botao exportar tudo no perfil (Sessao 23)" → db092ce (2 files, 157 insertions). git push → 18efeb0..db092ce. git status --short vazio. Log: db092ce HEAD/main/origin/main.

3.6 Fase 4 — validação de deploy da Vercel (com falso negativo diagnosticado)

Primeira tentativa: Select-String -Pattern "ProfilePage-" no HTML da Vercel → não achou nada. Diagnóstico: o HTML referencia só /assets/index-*.js; os chunks aparecem dentro do index como import dinâmico (const __vite__mapDeps=...["assets/ProfilePage-<hash>.js"...]). Regra S23 nasce daqui.

Segunda tentativa (correta): baixar o index-*.js e procurar assets/ProfilePage-<hash>.js dentro dele. Achei:

    index-DtsElaP5.js e index-CdQz_-xG.js (duas coletas em momentos diferentes) → ambos referenciam assets/ProfilePage-SP0KNqPy.js.

    ProfilePage-SP0KNqPy.js ≠ ProfilePage-BPFFRQ5R.js (build local) e ≠ ProfilePage-D83pyXao.js (S22) → bundle novo no ar, hash de prod.

    Bônus: dentro do index minificado, achei o corpo do downloadActivityExportBulk (minificado como ya) com URLSearchParams, format/from/to, apiFetchBlob → Ei, _triggerDownload → _a, fallback rumo_export.zip. Prova direta de que o commit db092ce está sendo servido.

3.7 Tropeços e correções (S23)

Tropeço 1 — teste de deploy mal desenhado. Achei que Select-String -Pattern "ProfilePage-" no HTML da Vercel ia encontrar o chunk. Não encontra: o HTML só referencia o index. Corrigido baixando o index e procurando o chunk dentro. Regra S23 registrada.

Tropeço 2 — aspas no regex PowerShell. O regex 'src="(/assets/index-[^"]+\.js)"' dentro de Invoke-WebRequest | Select-String precisou de aspas simples + escape em [^"]+\.js. Funcionou, mas o primeiro Select-String cuspiu o HTML inteiro (sem destacar). Lição: em PowerShell 5.1, quando o Select-String devolve o input inteiro é porque não casou; é sinal de regex errado, não de "não existe".

3.8 Resultado da suíte (S23)

pytest -q → 164 passed (mantido). ruff → All checks passed. npm run build → 824 modules verde (ProfilePage 20.56 kB). npm run lint limpo. flutter analyze No issues. Sem teste novo (feature é de UI, sem lógica de backend nova — os 164 testes backend já cobrem o endpoint).

3.9 Commits pushados (S23)

    db092ce feat(web): botao exportar tudo no perfil (Sessao 23) — 2 files, 157 insertions.

Pendente: docs: handoff da Sessao 23 (este arquivo).

3.10 Validação em produção (front)

Vercel: bundle novo no ar (ProfilePage-SP0KNqPy.js, contém downloadActivityExportBulk). Validação no browser PENDENTE (checklist na Seção 8). Se algo falhar, anotar na Seção 7 como dívida/observação e corrigir na S24.

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES
GET /activities/{id}/track (auth: Bearer JWT)

Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota".

Resposta (TrackResponse):
json

{
  "activity_id": "uuid",
  "type": "LineString",
  "coordinates": [[lon, lat], ...],
  "bbox": [minLon, minLat, maxLon, maxLat],
  "n_points": 60,
  "simplified": false
}

ActivityResponse (feed/lista/detalhe/busca)
json

{ ..., "bbox": [minLon, minLat, maxLon, maxLat] | null }

Ordem GeoJSON. null quando route IS NULL. Sem N+1.
GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21

    Permissão: dono OU seguidor do dono. Caso contrário, 404 ("Atividade não encontrada" — não vaza existência).

    format=csv (default): 200, Content-Type: text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.csv". 1 header + 1 linha. Funciona com ou sem rota (bbox_* vazios se sem rota). None → string vazia. lineterminator="\n". Colunas:
    id, activity_type, title, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, bbox_min_lon, bbox_min_lat, bbox_max_lon, bbox_max_lat

    format=gpx: 200, Content-Type: application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id>_<type>.gpx". <trk><name>{title}</name><trkseg><trkpt lat="…" lon="…"> por ponto. Inverte [lon, lat] (GeoJSON) → lat/lon no atributo. Exige rota → 404 "Atividade não possui rota" se route IS NULL.

    format inválido → 422 (Literal do Pydantic).

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22

    Auth: self-only. Exporta apenas as atividades do usuário autenticado.

    Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos, cada um no formato unitário.

    format=csv (default): ZIP com N .csv (todas do filtro, com ou sem rota).

    format=gpx: ZIP com N .gpx (só com rota; omite sem rota).

    Filtro from/to (YYYY-MM-DD, UTC, inclusivo): from → >= 00:00; to → < (to+1 dia) 00:00.

    Casos de borda: 0 atividades → 200 ZIP vazio; from>to → 422 "from deve ser <= to"; format inválido → 422; data malformada → 422 (Pydantic).

GET /activities/stats/summary?activity_type=<opcional>

→ StatsSummary: total_activities, total_distance_m, total_duration_s, total_elevation_gain_m, total_calories, avg_pace_s_per_km, avg_speed_mps.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional>

→ StatsWeeklyResponse: { weeks, items: [StatsPeriod] }.
GET /activities/stats/monthly?months=N&activity_type=<opcional>

→ StatsMonthlyResponse: { months, items: [StatsPeriod] }.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy>

→ StatsByTypeResponse: { items: [StatsByTypeItem] }. StatsByTypeItem: activity_type, total_activities, total_distance_m, total_duration_s, total_elevation_gain_m, total_calories, previous | null. period inválido → 422. compare inválido → 422. previous null para period="all" ou tipo ausente na janela.

Janelas (S17/S18/S20):
period	compare	janela
all	qualquer	null
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide — documentado em teste)
GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}

Mesmos shapes. by-type aceita period + compare. Permissão (_ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403 ("Você precisa seguir este usuário pra ver as estatísticas dele"); target inexistente → 404 ("Usuário não encontrado").
GET /auth/me — identidade do usuário logado (NÃO é /users/me)

Resposta: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9 a 22 commitadas e pushadas. Sessão 23 commitada e pushada (db092ce).

Pendente: este handoff.

Primeira ação da S24:
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

Se aparecer M docs/HANDOFF.md, commitar (bloco abaixo). Se não aparecer, o handoff da S23 já foi commitado — pular.

Commitando o handoff da S23:
powershell

cd D:\Rumo
git status --short
# Esperado: M docs/HANDOFF.md (o handoff da S23)
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 23"
git push
git --no-pager log --oneline -4
git status --short

Esperado depois: HEAD == origin/main com docs: handoff da Sessao 23 no topo, working tree limpo.

Nenhuma outra pendência conhecida de git.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
[Sessão 24 — primeira ação] Abrir PowerShell via Win+R → powershell

NÃO abrir de dentro do VS Code / Windows Terminal. Depois:
powershell

cd D:\Rumo
git push
git --no-pager log --oneline -8
git status --short

[Sessão 24 — primeira ação] Commitar handoff S23 (se ainda não foi)
powershell

cd D:\Rumo
git status --short
# Esperado: M docs/HANDOFF.md
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 23"
git push
git --no-pager log --oneline -4
git status --short

[Sessão 24 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 24 — primeira ação] Docker + pytest local
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

[Sessão 24 — primeira ação] Detecção de versão em produção (S23 — exportar tudo no front)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, aguardar redeploy da Vercel antes de validar.
powershell

# Passo 1: baixar o HTML e o index-*.js
$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing

# Passo 2: listar os chunks de página referenciados pelo index
$idx.Content | Select-String -Pattern 'assets/[A-Za-z]+-[A-Za-z0-9_-]+\.js' -AllMatches |
  ForEach-Object { $_.Matches.Value } | Sort-Object -Unique

# Passo 3: procurar o corpo do downloadActivityExportBulk (minificado) dentro do index
$idx.Content | Select-String -Pattern 'activities/export'

# Esperado: /activities/export presente no index (confirma que o bundle S23 está no ar).
# Se não aparecer, Vercel não redeployou: aguardar 1-2 min ou Redeploy manual no dashboard.

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
git restore <arquivo>                                          # ou git checkout -- <arquivo>
# Se a versão quebrada JÁ foi commitada:
git show <commit-anterior>:<arquivo> > <arquivo>
# Conferir que voltou:
Get-Content -Encoding UTF8 <arquivo> | Select-String -Pattern "async def "

Diagnóstico: rota nova não responde após git push (lição S22)
powershell

# 1) openapi.json — a rota está no ar?
Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"
# Se vazio: Render não redeployou. Aguardar ou Manual Deploy no dashboard.
# 2) se a rota está no ar mas retorna 422, ver o BODY do erro:
try {
  Invoke-WebRequest -Uri "<url>" -Headers $h -UseBasicParsing | Out-Null
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "STATUS $($resp.StatusCode.value__): $($reader.ReadToEnd())"
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23)
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$idx.Content | Select-String -Pattern 'assets/ProfilePage-[A-Za-z0-9_-]+\.js'
# hash igual ao local (ex: BPFFRQ5R) → o build local subiu sem variação de env
# hash diferente → Vercel buildou de novo com VITE_API_URL de prod (esperado, é "novo")
# hash do S22 (D83pyXao) → Vercel não redeployou: aguardar ou Redeploy manual

SEÇÃO 7 — DÍVIDAS TÉCNICAS

    (FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.

    (FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.

    (CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python. Qualquer ORDER BY em coluna Enum DEVE (a) sort final em Python, ou (b) ser testado.

    (CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.

    (CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN. WHERE deve cobrir a união; cada métrica recorta via SUM(CASE WHEN <janela> THEN col ELSE 0 END).

    (CONHECIDA — Sessão 17/18/19/20/21/22/23) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. O segmented control de período afeta APENAS a tabela por tipo. Intencional.

    (CONHECIDA — Sessão 17/18/19/20/22/23) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. NÃO é bug. Os 164 testes locais provam filtro e previous.

    (CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática. Documentado em teste.

    (CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk" via map_gpx_type. Testes de export usam activity.activity_type.value dinâmico. Se trocar o sample, testes continuam passando.

    (CONHECIDA — Sessão 21) to_gpx não emite <time> por <trkpt> (a geometria em route é só LineString, sem stream temporal — decisão da S10). O <trk> tem <name> e <type>, mas sem timestamps por ponto. Strava/Garmin aceitam. Se "export com timestamps" virar requisito, ler raw_track_points (mudança pontual em to_gpx + assinatura).

    (CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. Não há caso de uso hoje (todo export exige auth). Adicionar quando aparecer (YAGNI).

    (CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries (get_activity por atividade + get_activity_track por atividade com rota no GPX). Aceitável para export raro. Se virar gargalo, otimizar com SELECT único + bbox por linha — mas duplica lógica de _attach_counts. Preferi reusar.

    (CONHECIDA — Sessão 22) Export em lote é self-only. Se o produto quiser "exportar atividades de quem eu sigo", precisa mudar _get_user_activity_ids_in_range para aceitar user_id de terceiros + checar follow em _ensure_can_view_stats (ou equivalente). Decisão de privacidade, não é bug.

    (CONHECIDA — Sessão 23) downloadActivityExportBulk em activities.ts valida from>to client-side (evita request inútil) e o backend também valida (422). Dupla validação é proposital — o backend é autoritativo; o client é UX.

    (CONHECIDA — Sessão 23) UI "Exportar tudo" é self-only (renderiza só isSelf), espelhando o backend. Se o produto quiser "exportar atividades de terceiros", precisa backend (ver dívida acima) + UI nova.

    (Oportunidade — S18/S19/S20/S21/S22/S23) Delta "vs. anterior / vs. ano anterior" cobre 3 métricas (atividades, distância, elevação). Tempo e calorias ficaram fora por legibilidade. Extensão trivial.

    (Oportunidade — S18/S19/S20/S23) Semântica do delta é NEUTRA (subiu=verde, desceu=vermelho, igual=cinza). Sem "melhor/pior". Se o produto quiser meta, feature nova.

    (Oportunidade — S19/S20/S23) Stats públicas só quando viewer segue o alvo. "Stats públicas sempre" = mudança em _ensure_can_view_stats (endpoint + teste + front). Decisão de privacidade.

    (Oportunidade — S23) RouteMap.tsx é reutilizável. Se aparecer segundo uso, considerar React.lazy() para tirar o leaflet (163.60 kB) do chunk.

    (Oportunidade — S21/S22/S23) Export com timestamps por ponto — ver dívida da S21.

    (Oportunidade — S22/S23) Export em lote no app mobile (mesma feature do web). Mobile está parado desde S11; seria sessão grande.

    (Oportunidade — S22/S23) Export em lote concatenado (1 CSV com todas as atividades + 1 GPX com todos os tracks). Decidimos ZIP na S22. Se o produto quiser "1 arquivo grande", é feature paralela.

Mobile: sem drill-down de stats. Sem inclinação/rotação 3D. Sem export. TimeoutException do app mobile não reproduzido desde a Sessão 9.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 24 e além)
PENDÊNCIA DE VALIDAÇÃO DA SESSÃO 23 (antes de qualquer coisa na S24)

Checklist no browser (Vercel):

    Login prod@rumo.com / senha12345.

    Abrir https://rumo-wheat.vercel.app/users/01a12c83-be2a-71fa-b966-1c93ca64f341.

    Ver o card "Exportar tudo" abaixo de "Este é você.".

    CSV sem filtro → ZIP rumo_export_*.zip com 6 entries.

    GPX sem filtro → ZIP com 6 entries (prod tem rota em todas).

    De=2099-01-01 → ZIP com 0 entries.

    De > Até → mensagem vermelha "A data inicial não pode ser maior que a final.", sem request em /activities/export (DevTools → Network).

    Perfil do Prod2 (01a141e7-5ea4-7600-8959-19145475ad0a) → card NÃO aparece.

    DevTools → Network → /activities/export?format=csv: Authorization: Bearer …, 200, Content-Type: application/zip, Content-Disposition: attachment; filename="rumo_export_…zip".

Se qualquer item falhar, anotar sintoma exato (status, body, screenshot) e abrir a S24 corrigindo.

Depois da validação (se verde), a Sessão 23 está 100% fechada — feature de export completa (unitário S21 + em lote S22 + UI S23).
PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 24 (antes de qualquer mudança de código)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco da Seção 6 "[Sessão 24 — primeira ação]": git push, log, status; commitar handoff S23 se pendente.

    Sanidade de build (npm run build/lint + flutter analyze).

    Docker + pytest (docker ps -a, não só ps; pg_isready; pytest -q → 164; ruff check).

    Detecção de versão em produção (front S23): baixar index-*.js e procurar /activities/export dentro dele. Esperado: presente.

    Se a validação do browser ainda não foi feita, fazer o checklist acima.
Estado da Rota B (fim da Sessão 23)

Seis itens fechados: filtro de período (S17), comparação com janela anterior (S18), stats públicas em perfis de terceiros (S19), year-over-year (S20), export unitário CSV/GPX (S21), export em lote CSV/GPX em ZIP (S22), UI "Exportar tudo" no perfil (S23). A feature de export está completa do lado do produto (backend + front).
Próximos passos (escolha entre opções)

OPÇÃO 1 — Fechar validação da S23 no browser + polir ProfilePage. ← RECOMENDADA

    Fazer o checklist da Seção 8 (5 min).

    Se algo falhar, corrigir na S24 (escopo pequeno).

    Se verde, 1 polimento opcional: desabilitar o botão "Exportar tudo" quando loading (já está desabilitado — verificar visual), mostrar "0 atividades no filtro" como mensagem neutra após download de ZIP vazio (hoje o usuário baixa 0 entries sem aviso). Escopo: ~20–30 min, 1 arquivo (ProfilePage.tsx).

    Motivos: fecha a feature, sem risco de regressão, escopo mínimo.

OPÇÃO 2 — Export no app mobile (paridade com web).

    Mobile parado desde S11. Sessão grande. Só se houver demanda real. Não recomendo para S24.

OPÇÃO 3 — Resíduos de baixo risco (Rota A+).

    (a) RouteMap com React.lazy() — prepara para segundo uso. ~30 min.

    (b) README.md com cheat sheet de endpoints. ~30 min.

    Ganho marginal. Só se não houver Rota B clara.

OPÇÃO 4 — Export com timestamps por ponto.

    Muda to_gpx para ler raw_track_points em vez de route. Feature de nicho.

OPÇÃO 5 — Export em lote no mobile (paridade) ou "exportar tudo" via app.

    Combina com Opção 2. Só depois de decidir se o mobile vai evoluir.

Recomendação final para a Sessão 24

Antes de escolher, VALIDAR ESTADO (Seção 8 — primeira ação). Se tudo verde (build, lint, analyze, pytest 164, index-*.js com /activities/export), aí escolher.

Rota recomendada: OPÇÃO 1 (fechar validação + polir ProfilePage).

Motivos:

    Fecha a feature de export (unitário S21 + em lote S22 + UI S23) do lado do produto.

    Escopo pequeno (~20–30 min), 1 arquivo, sem dependência nova.

    Baixo risco de regressão.

Se preferir escopo maior: OPÇÃO 2 (mobile) — avisar antes que é sessão grande.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 24 neste mesmo formato (seções 0 a 9).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22, reforçou: "sempre vamos seguir o que você recomendar" e "vamos sempre fazer o que você recomendar".

Na abertura da S23, reforçou de novo: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Pedido para o assistente da S24 (e além): manter o processo da S21/S22/S23. Concretamente:

    Fase 0 obrigatória: validar estado (git, build, lint, analyze, docker -a, pytest, detecção de versão em prod) antes de tocar em qualquer código.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — regra S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (front) entre cada entrega. Nunca acumular 2 arquivos sem validar.

    Fase 4 — validação em produção: local verde é pré-requisito; prod via HTTP/browser é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js e procurar o chunk (front) antes de acusar bug.

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir.

Regras novas das S21/S22/S23 (Seção 0, itens 7–12): nunca placeholder no código; não adivinhar nomes de símbolos; git status + git log antes de git restore; Invoke-WebRequest sempre com -UseBasicParsing; validar openapi.json antes de acusar bug em rota nova; validar bundle da Vercel baixando o index-*.js.

O que funcionou nas S21/S22/S23 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros (placeholder e 3 nomes errados na S21; falso alarme de 422 na S22; teste de deploy mal desenhado na S23 — "ProfilePage-" no HTML) e correção com base no output real do terminal, não na previsão.