===============================================================================
HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 12
===============================================================================

===============================================================================
0. LEIA PRIMEIRO — CONTEXTO OPERACIONAL (evita retrabalho no próximo chat)
===============================================================================

⚠️ REGRA DE OURO PARA O ASSISTENTE NOVO (leia antes de qualquer coisa)
-----------------------------------------------------------------------
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir
arquivo", "ver o repo". Toda informação sobre o projeto chega por DUAS vias:
  (a) o usuário cola o conteúdo de um arquivo com `Get-Content -Encoding UTF8`
  (b) o usuário cola a saída de um comando de terminal
NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA
reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um
arquivo, PEÇA e espere o usuário colar. Se a estrutura de pastas for
necessária, PEÇA a saída de `Get-ChildItem` (há script pronto na seção 6).
Sessões anteriores perderam tempo precioso porque o assistente tentou
"adivinhar" a árvore de diretórios e errou. Não repetir.

O QUE É LOCAL vs O QUE É PRODUÇÃO
----------------------------------
- LOCAL (na máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI
  + Postgres/PostGIS + Alembic), D:\Rumo\web (React 19 + Vite 8 + TypeScript
  + Tailwind + react-leaflet na ActivityDetailPage), D:\Rumo\mobile (Flutter).
  O assistente NÃO tem acesso a esses arquivos neste chat — o usuário precisa
  colar conteúdo de arquivos e saídas de terminal. Não assumir que o
  assistente consegue "ver" pastas.
- PRODUÇÃO (na nuvem, acessível por HTTP): backend no Render
  (https://rumo-api-5s0b.onrender.com), frontend web na Vercel
  (https://rumo-wheat.vercel.app). O backend de produção usa Postgres/PostGIS
  gerenciado (não é o local). Testar via HTTP é sempre possível sem Docker.
- DOCKER: NÃO instalado no Windows local (ver dívidas técnicas). É o PRÓXIMO
  PASSO BLOQUEANTE da Sessão 13. Ignorar Docker em trabalho de código até
  ele estar instalado e `pytest -q` verde localmente.

ESTRUTURA DO REPO (referência — NÃO É PARA ASSUMIR, É PARA CONFERIR)
--------------------------------------------------------------------
Árvore de alto nível esperada em D:\Rumo (validar com `Get-ChildItem` na
primeira ação da Sessão 13; se divergir, PEDIR ao usuário antes de mexer):

D:\Rumo\
├── backend\           # FastAPI + Postgres/PostGIS + Alembic + pytest
│   ├── app\           # código da aplicação
│   ├── tests\         # testes (pytest)
│   ├── alembic\       # migrations
│   ├── docker-compose.test.yml   # Postgres/PostGIS de teste na 5433
│   └── ...
├── web\               # React 19 + Vite 8 + TS + Tailwind
│   ├── src\
│   │   ├── components\   # ActivityCard.tsx, etc.
│   │   ├── pages\        # ActivityDetailPage.tsx, ProfilePage.tsx, SearchPage.tsx, ...
│   │   ├── lib\          # geo.ts, api client, etc.
│   │   ├── types\        # api.ts (tipos do backend)
│   │   └── ...
│   ├── package.json      # scripts: build = "tsc -b && vite build"
│   └── ...
├── mobile\            # Flutter (flutter_map, OSM/Esri satélite)
│   ├── lib\
│   │   ├── models\       # activity.dart, comment.dart, ...
│   │   ├── pages\        # feed_page.dart, activity_detail_page.dart, ...
│   │   ├── widgets\      # activity_map.dart, like_button.dart, ...
│   │   ├── services\     # auth_service.dart, api_client.dart, ...
│   │   └── ...
│   ├── pubspec.yaml
│   └── ...
└── docs\
    └── HANDOFF.md     # este arquivo

Se um arquivo específico for necessário, o pedido correto é:
    Get-Content -Encoding UTF8 <caminho completo>
E o script de descoberta (primeira ação de sessão) está na seção 6.

COMO RODAR COMANDOS FLUTTER NO WINDOWS DESTE USUÁRIO
-----------------------------------------------------
- Flutter instalado em: C:\Users\nasci\flutter (bin em ...\flutter\bin).
- Versões: Flutter 3.47.9 (stable) / Dart 3.13.7 / DevTools 2.60.0.
- PROBLEMA CONHECIDO: mesmo com C:\Users\nasci\flutter\bin no PATH do usuário
  e flutter.bat existindo, o PowerShell frequentemente NÃO reconhece o
  comando `flutter` — é cache de sessão do terminal/VS Code.
- SOLUÇÃO QUE FUNCIONA (usar por padrão):
      & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>
- Repo/repo mobile: D:\Rumo e D:\Rumo\mobile. PowerShell, Windows 5.1.

COMO TESTAR O BACKEND DE PRODUÇÃO SEM O APP (PowerShell)
--------------------------------------------------------
1) Login (retorna JWT):
     $body = "username=prod@rumo.com&password=senha12345"
     $login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
     $token = $login.access_token
2) Feed (agora com bbox):
     $feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
     $feed | ForEach-Object { Write-Host "id=$($_.id.Substring(0,8))  title=$($_.title)  bbox=$($_.bbox -join ',')" }
3) Track de uma atividade (GeoJSON-like):
     $id = "UUID"
     $t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }
     Write-Host "n=$($t.n_points) bbox=$($t.bbox -join ',')"
- Conta de teste usada: prod@rumo.com / senha12345.
- Latências medidas em 2026-11-06: backend quente, /track de rota sintética
  ~306ms. Não confundir com cold start do Render (~30s após ociosidade).

O QUE O ASSISTENTE PRECISA PEDIR AO USUÁRIO (não tem acesso a arquivos)
-----------------------------------------------------------------------
- Conteúdo de arquivos específicos via: Get-Content -Encoding UTF8 <caminho>
  (SEMPRE passar -Encoding UTF8; sem isso, acentos viram "inÃ­cio" e o
  arquivo fica corrompido na leitura.)
- Saídas de comandos (flutter analyze, npm run build, git log, git status).
- Nunca assumir estrutura de pastas "de cabeça": pedir o arquivo antes de
  reescrevê-lo, para não quebrar o que já funciona.
- ATENÇÃO — arquivos truncados: se um Get-Content vier com a última linha
  cortada (ex.: "upda"), o arquivo está corrompido no disco. NÃO adivinhar o
  final. Pedir `git status --short -- <arquivo>`; se estiver " M", rodar
  `git checkout -- <arquivo>` e recuperar do HEAD. Isso aconteceu na Sessão
  11 com web/src/types/api.ts e o usuário resolveu com Ctrl+Z antes do
  `git checkout`. Documentar sempre que acontecer.
- ATENÇÃO — `git diff` pipeado no PowerShell pode exibir acentos como
  mojibake (ex.: "Sess笏愿ｺo"). É artefato de codepage do pipe, NÃO corrupção
  do arquivo. Usar `Get-Content -Encoding UTF8` para inspecionar o conteúdo
  real antes de qualquer decisão sobre o arquivo.

ACORDOS DE TRABALHO (válidos em todas as sessões)
--------------------------------------------------
1. SEMPRE seguir a recomendação do assistente. Quando houver decisão
   pendente, executar a recomendada salvo instrução explícita em contrário.
2. SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff
   parcial, nunca "// resto igual". Preservar imports, comentários e trechos
   que já funcionam. Destacar o trecho alterado com comentário curto acima
   (// [Sessão N] ou // [Sessão N — fix]).
3. UMA versão por arquivo por resposta. Se errar no meio do raciocínio,
   cortar a versão errada e entregar só a corrigida com nota de 1 linha.
   NUNCA duas versões do mesmo arquivo na mesma resposta.
4. HANDOFF PREVENTIVO em ~70-80% do limite de contexto: parar o trabalho em
   curso e entregar o HANDOFF completo neste mesmo formato (seções 0 a 8),
   pronto para colar no próximo chat.

===============================================================================
1. TL;DR PARA QUEM CHEGA AGORA
===============================================================================

- Backend: 111 testes passando (inalterado desde a Sessão 10). Activity.route
  é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com
  coordinates em ordem GeoJSON [lon, lat], bbox [minLon,minLat,maxLon,maxLat],
  n_points, simplified. Responde 404 quando route é NULL. Acesso: dono OU
  seguidor do dono.
- [Sessão 10] ActivityResponse (feed/lista/detalhe/busca) inclui
  `bbox: list[float] | None`, calculado via ST_XMin/YMin/XMax/YMax do PostGIS
  no mesmo SELECT (sem N+1). `None` quando route é NULL. Validado em produção
  (commit b8e4084).
- [Sessão 11] Opção B COMPLETA nas 3 plataformas:
  * Mobile: miniatura estática no card do feed (ActivityMap.fromBbox, com
    InteractiveFlag.none). Validado no emulador (6/6 testes).
  * Web: miniatura estática no card do feed via 1 tile OSM (<img>, sem
    react-leaflet no card). Validado na Vercel.
  * Web: toggle Mapa/Satélite no mapa do detalhe (OSM ↔ Esri World Imagery),
    mesmo padrão visual do mobile. Validado na Vercel.
- Frontend Web: React 19 + Vite 8 + TypeScript + Tailwind; react-leaflet já
  no bundle (ActivityDetailPage).
- Mobile: mapa de rota no detalhe (flutter_map, OSM/Esri satélite),
  alternância Mapa/Satélite, currentUserId no AuthService.
- [Sessão 12] Sessão de housekeeping e fechamento:
  * Acordos de trabalho reafirmados (código completo, uma versão por arquivo,
    handoff preventivo em ~70-80% do contexto, seguir sempre a recomendação).
  * Estado do repo validado no início: git log coerente com a Sessão 11
    (bc0b9d9 no topo), build web verde, flutter analyze 0 issues.
  * Pendência do docs/HANDOFF.md FECHADA: arquivo sobrescrito com o handoff
    da Sessão 11 e commitado (894e4b5). Working tree limpo.
  * Sessão encerrada ANTES do Docker Desktop de propósito: instalação
    interativa (WSL2, reboot, possível troubleshooting) é cara em contexto e
    pobre em código. Decisão registrada na seção 8.
  * Este handoff foi reescrito com ênfase em "não adivinhar estrutura de
    pastas" (seção 0) para evitar retrabalho em chats novos.

===============================================================================
2. PRODUÇÃO E AMBIENTE
===============================================================================

- Backend: https://rumo-api-5s0b.onrender.com
- Docs Backend: https://rumo-api-5s0b.onrender.com/docs
- Frontend Web: https://rumo-wheat.vercel.app
- Repo local: D:\Rumo
- Mobile: D:\Rumo\mobile
- Web: D:\Rumo\web (scripts: "build": "tsc -b && vite build", "lint": "eslint .")
- Flutter: 3.47.9 / Dart 3.13.7
- SO: Windows, PowerShell 5.1
- Git (estado ao fim da Sessão 12 — CONFIRMAR com git log + git status no
  início da Sessão 13):
    894e4b5 (HEAD -> main) docs: handoff da Sessão 11 (toggle Mapa/Satélite, miniaturas, bbox)
    bc0b9d9 (origin/main) feat(web): toggle Mapa/Satélite no mapa do detalhe (igual mobile)
    1fa8863 feat(web): miniatura de mapa no card do feed (bbox estático via tile OSM)
    77b1722 feat(mobile): miniatura de mapa no card do feed (bbox estático)
    b8e4084 feat(backend): bbox no ActivityResponse (feed/lista/detalhe/busca) para miniatura de mapa
- ATENÇÃO: 894e4b5 está LOCAL, não pushado. origin/main ainda está em
  bc0b9d9. Executar `git push` no início da Sessão 13 (antes de qualquer
  mudança de código) para evitar divergência futura.

===============================================================================
3. O QUE FOI FEITO NA SESSÃO 12
===============================================================================

3.1 Acordos reafirmados no início (valem daqui pra frente)
    - Seguir sempre a recomendação do assistente.
    - Sempre entregar arquivo completo ao atualizar.
    - Uma versão por arquivo por resposta.
    - Handoff preventivo em ~70-80% do contexto.

3.2 Validação de estado (antes de qualquer mudança)
    - git log --oneline -5: bc0b9d9 (toggle) no topo, seguido por 1fa8863,
      77b1722, b8e4084, c26239b. Bate com o esperado na Sessão 11.
    - git status --short: apenas " M docs/HANDOFF.md" (pendência recorrente).
    - cd web ; npm run build: verde (1.84s, ActivityDetailPage em 11.91 kB).
    - cd mobile ; flutter analyze: No issues found! (3.9s).

3.3 Diagnóstico do docs/HANDOFF.md
    - git diff --stat: 276 inserções, 56 remoções (reescrita total).
    - Get-Content -Encoding UTF8 primeiras linhas: cabeçalho "Sessão 11".
    - Diagnóstico: o arquivo no working tree JÁ era o handoff da Sessão 11
      completo; o HEAD ainda era o handoff da Sessão 8. Hipótese A confirmada
      (não havia edição manual inédita a preservar).
    - Artefato de leitura: o pipe do `git diff` no PowerShell exibiu acentos
      como mojibake ("Sess笏愿ｺo"). Não é corrupção do arquivo — é codepage
      do pipe. Anotado na seção 0.

3.4 Fechamento da pendência do docs/HANDOFF.md
    - docs/HANDOFF.md sobrescrito com o conteúdo canônico da Sessão 11 (o
      mesmo já presente no working tree, para eliminar qualquer divergência).
    - Commit: 894e4b5 docs: handoff da Sessão 11 (toggle Mapa/Satélite,
      miniaturas, bbox).
    - git status --short final: vazio. Pendência fechada.

3.5 Decisão de encerrar a sessão antes do Docker Desktop
    - Contexto estimado nesta sessão: ~15-20k tokens (≈10-15% do limite),
      ainda LONGE do gatilho de 70-80%. Portanto esta NÃO foi uma parada
      forçada por limite — foi decisão de planejamento.
    - Motivo: instalar Docker Desktop no Windows (WSL2, reboot, possível
      troubleshooting de driver/Hyper-V) gera muito output de terminal e
      pouco código. Melhor abrir a Sessão 13 já com Docker pronto e pytest
      verde, para gastar contexto em código real (Perfil/Estatísticas).
    - Registrado para não confundir "handoff preventivo por limite" com
      "handoff de fechamento planejado". Ambos usam o mesmo formato.

3.6 Reescrita deste handoff com foco em não-adivinhação de pastas
    - Após a Sessão 12, o usuário relatou que chats novos perderam tempo
      tentando "descobrir" a estrutura de pastas do repo. Este handoff
      ganhou o bloco "ESTRUTURA DO REPO" + "REGRA DE OURO" na seção 0, e
      um script de descoberta (`Get-ChildItem`) na seção 6, para que o
      assistente novo peça a árvore real ANTES de qualquer edição.

===============================================================================
4. CONTRATOS DO BACKEND RELEVANTES (referência)
===============================================================================

- GET /activities/{id}/track  (auth: Bearer JWT)
  Permissão: dono OU seguidor do dono (404 caso contrário).
  404 quando activity.route is None → detail "Atividade não possui rota".
  Resposta (TrackResponse):
    {
      "activity_id": "uuid",
      "type": "LineString",
      "coordinates": [[lon, lat], [lon, lat], ...],  // GeoJSON
      "bbox": [minLon, minLat, maxLon, maxLat],
      "n_points": 60,
      "simplified": false
    }

- ActivityResponse (feed/lista/detalhe/busca):
    {
      ...,
      "bbox": [minLon, minLat, maxLon, maxLat]  // ou null
    }
  Ordem GeoJSON. Null quando route IS NULL. Sem N+1, via 4 funções PostGIS
  no SELECT.

- ActivityResponse NÃO inclui route nem coordinates (polyline só via /track).

===============================================================================
5. COMMITS PENDENTES / ESTADO DO REPO
===============================================================================

- Sessões 9, 10, 11 e 12 commitadas localmente.
- 894e4b5 (docs: handoff da Sessão 11) está LOCAL, NÃO pushado. origin/main
  ainda está em bc0b9d9. PENDÊNCIA: rodar `git push` no início da Sessão 13.
- docs/HANDOFF.md RESOLVIDO (não é mais dívida). Este handoff da Sessão 12
  deve substituí-lo no início da Sessão 13 e ser commitado como
  `docs: handoff da Sessão 12` (1 commit adicional, junto ou após o push).

===============================================================================
6. SCRIPTS ÚTEIS (PowerShell)
===============================================================================

# [Sessão 13 — primeira ação] Descoberta da estrutura do repo
# Rodar e colar a saída no chat ANTES de qualquer edição de código.
cd D:\Rumo
Get-ChildItem -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name

# [Sessão 13 — primeira ação] Estado do repo
cd D:\Rumo
git push
git log --oneline -5
git status --short

# [Sessão 13 — primeira ação] Sanidade de build
cd D:\Rumo\web
npm run build

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# Login (produção)
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

# Feed com bbox (produção)
$feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
$feed | ForEach-Object { Write-Host "id=$($_.id.Substring(0,8))  title=$($_.title)  bbox=$($_.bbox -join ',')" }

# Track de uma atividade (produção)
$t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }

# Build web
cd D:\Rumo\web
npm run build

# Flutter analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

# [Sessão 13] Subir Postgres/PostGIS de teste (após instalar Docker Desktop)
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d

# [Sessão 13] Rodar pytest local
cd D:\Rumo\backend
pytest -q

===============================================================================
7. DÍVIDAS TÉCNICAS
===============================================================================

- PRÓXIMO PASSO BLOQUEANTE (Sessão 13): Docker Desktop NÃO instalado no
  Windows local. pytest local em 94 erros de ConnectionRefusedError
  (conftest.py aponta para docker-compose.test.yml, Postgres/PostGIS na 5433).
  Os 17 testes que passam são só os que não tocam banco. WORKAROUND atual:
  validar em produção (Render). RESOLVER: instalar Docker Desktop → reiniciar
  → `cd D:\Rumo\backend && docker compose -f docker-compose.test.yml up -d`
  → `pytest -q` verde ANTES de qualquer mudança que dependa de testes locais.
- 894e4b5 (docs: handoff da Sessão 11) está local, não pushado. Rodar
  `git push` no início da Sessão 13.
- Web: miniatura do feed usa 1 tile OSM centralizado (bbox grande pode cortar
  bordas). Aceitável; se virar problema, evoluir para mosaico 2x2 ou
  staticmap.openstreetmap.de.
- Web: toggle Mapa/Satélite está inline na ActivityDetailPage (não extraído
  para componente próprio). Se o mapa for reutilizado em outra página, extrair
  `RouteMap.tsx` com o estado do toggle encapsulado.
- Mobile: sem inclinação/rotação 3D (flutter_map é 2D). Se 3D for requisito,
  avaliar maplibre_gl (decisão maior, pesada).
- TimeoutException do app mobile não reproduzido desde a Sessão 9. Registrar
  se voltar (tela + log do flutter run).
- (Resolvido na Sessão 12) docs/HANDOFF.md modificado no working tree.
  Fechado em 894e4b5. Não é mais dívida.
- (Mitigado na Sessão 12) Chats novos perdiam tempo tentando adivinhar a
  estrutura de pastas do repo. Mitigação: bloco "ESTRUTURA DO REPO" + "REGRA
  DE OURO" na seção 0 e script `Get-ChildItem` na seção 6. Se ainda assim
  acontecer, reforçar a regra no início da sessão.

===============================================================================
8. PRÓXIMOS PASSOS RECOMENDADOS (Sessão 13)
===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 13 (antes de qualquer mudança de código):
  1) Colar este handoff em docs/HANDOFF.md e commitar como
     `docs: handoff da Sessão 12`.
  2) No terminal:
        cd D:\Rumo
        git push
        git log --oneline -5
        git status --short
        cd web ; npm run build
        cd ..\mobile
        & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
     Confirmar com o usuário: push aceito, 894e4b5 em origin/main, build e
     analyze verdes, working tree limpo.
  3) DESCOBERTA DE ESTRUTURA (obrigatória — não adivinhar):
        cd D:\Rumo
        Get-ChildItem -Directory | Select-Object Name
        Get-ChildItem D:\Rumo\web\src -Directory | Select-Object Name
        Get-ChildItem D:\Rumo\web\src\pages | Select-Object Name
        Get-ChildItem D:\Rumo\web\src\components | Select-Object Name
        Get-ChildItem D:\Rumo\mobile\lib -Directory | Select-Object Name
        Get-ChildItem D:\Rumo\backend -Directory | Select-Object Name
     Colar as saídas no chat ANTES de pedir ou reescrever qualquer arquivo.

ORDEM DE TRABALHO RECOMENDADA:
1) Instalar Docker Desktop (passo bloqueante, interativo):
   a) Baixar em https://www.docker.com/products/docker-desktop/ (canal stable).
   b) Instalar com WSL2 como backend (padrão). Reiniciar quando solicitado.
   c) Abrir Docker Desktop e confirmar que o engine está "running".
   d) `docker version` e `docker compose version` no PowerShell devem responder.
   e) `cd D:\Rumo\backend ; docker compose -f docker-compose.test.yml up -d`
      — aguardar o Postgres/PostGIS na 5433 ficar healthy.
   f) `pytest -q` — esperado: 111 testes passando (mesmo número da produção).
   g) Se algo falhar: ver seção 7 (dívidas) e registrar o erro exato antes de
      tentar workaround.
2) Com pytest local verde, retomar trabalho de feature na ordem:
   a) Perfil / Estatísticas na web. StatsSummary, StatsPeriod,
      StatsWeeklyResponse, StatsMonthlyResponse já estão tipados em
      web/src/types/api.ts. Falta UI (ProfilePage.tsx e componentes).
   b) Refinamento visual do feed: revisar altura das miniaturas (mobile 120px,
      web 96px) se ficarem altas demais. Ajuste de UX, não feature.
3) Handoff preventivo em ~70-80% do contexto — antes do fim, parar e
   entregar o HANDOFF completo da Sessão 13 neste mesmo formato.