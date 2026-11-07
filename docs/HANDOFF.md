===============================================================================
HANDOFF — Rumo (backend + frontend + mobile) — gerado ao fim da Sessão 11
===============================================================================

===============================================================================
0. LEIA PRIMEIRO — CONTEXTO OPERACIONAL (evita retrabalho no próximo chat)
===============================================================================

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
- DOCKER: NÃO instalado no Windows local (ver dívidas técnicas). Ignorar
  Docker nesta sessão; validar tudo via produção (Render).

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

- Backend: 111 testes passando (inalterado na Sessão 11). Activity.route é
  PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com
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
- Git (estado esperado ao fim da Sessão 11 — CONFIRMAR com git log):
    <novo commit> feat(web): toggle Mapa/Satélite no mapa do detalhe (igual mobile)
    1fa8863 (HEAD -> main, origin/main) feat(web): miniatura de mapa no card do feed (bbox estático via tile OSM)
    77b1722 feat(mobile): miniatura de mapa no card do feed (bbox estático)
    b8e4084 feat(backend): bbox no ActivityResponse (feed/lista/detalhe/busca) para miniatura de mapa
    c26239b refactor(mobile): currentUserId no AuthService (remove decode JWT duplicado no detalhe)
    32d3e42 feat(mobile): mapa de rota no detalhe (flutter_map, OSM/Esri satélite, timeout dedicado)

===============================================================================
3. O QUE FOI FEITO NA SESSÃO 11
===============================================================================

3.1 Acordos reafirmados no início (valem daqui pra frente)
    - Seguir sempre a recomendação do assistente.
    - Sempre entregar arquivo completo ao atualizar.
    - Handoff preventivo em ~70-80% do contexto.

3.2 Etapa 3 (mobile) — CONCLUÍDA E VALIDADA
    - mobile/lib/models/activity.dart:
      * Campo `bbox` (List<double>?) adicionado.
      * fromJson converte List<num> → List<double>; null quando ausente.
      * copyWith propaga bbox.
    - mobile/lib/widgets/activity_map.dart:
      * Construtor original `ActivityMap(track: ...)` preservado.
      * Novo construtor `ActivityMap.fromBbox(...)`: enquadra LatLngBounds
        a partir do bbox GeoJSON, sem polyline, sem pinos. Defaults
        interactive=false, showLayerToggle=false, height=120.
      * Import `package:latlong2/latlong.dart` adicionado.
      * InteractionOptions respeita `widget.interactive`.
    - mobile/lib/pages/feed_page.dart:
      * Bloco de miniatura no _ActivityCard, abaixo do título, se
        activity.bbox != null. Envolvido em GestureDetector(onTap: onTap).
    - Testes manuais (emulador): 6/6 ok. flutter analyze: 0 issues.
    - Commit: 77b1722 feat(mobile): miniatura de mapa no card do feed.

3.3 Etapa 2 (web) — CONCLUÍDA E VALIDADA
    - web/src/types/api.ts:
      * `bbox: [number, number, number, number] | null` adicionado em
        Activity (herdado por ActivityDetail e FeedItem).
      * Incidente: arquivo foi encontrado truncado em "upda" no working
        tree (corrompido no disco, não bug de leitura). Resolvido com
        Ctrl+Z + `git checkout --` (usuário recuperou). Documentado na
        seção 0.
    - web/src/lib/geo.ts (NOVO):
      * bboxToOsmTileUrl(bbox, zoom=12) → URL de 1 tile OSM
        (https://tile.openstreetmap.org/{z}/{x}/{y}.png).
      * Cálculo slippy map EPSG:3857; centro do bbox; zoom fixo 12.
      * Sem mosaico (aceitável para thumbnail).
    - web/src/components/ActivityCard.tsx:
      * Miniatura em largura total (~96px, h-24) abaixo da row principal,
        dentro do <Link> do card (clique herda navegação do pai).
      * Só renderiza se activity.bbox != null.
      * <img loading="lazy" decoding="async"> — não pesa o feed.
    - npm run build: verde. Validação visual na Vercel: OK.
    - Commit: 1fa8863 feat(web): miniatura de mapa no card do feed.

3.4 Toggle Mapa/Satélite no detalhe (web) — CONCLUÍDO E VALIDADO
    - web/src/pages/ActivityDetailPage.tsx:
      * Imports: useEffect, useState.
      * Constantes OSM_URL, OSM_ATTRIBUTION, ESRI_URL, ESRI_ATTRIBUTION
        (extraídas do hardcoded antigo).
      * Estado `satelite` (false = mapa, true = satélite).
      * <TileLayer> ganhou `key={satelite ? "esri" : "osm"}` (força remount
        e evita cache de tile entre camadas), `url` e `attribution`
        condicionais.
      * Wrapper do mapa ganhou `relative`; botão overlay
        `absolute top-2 right-2 z-[1000]` com SVG condicional (mapa vs
        satélite).
      * Polyline (laranja), FitBounds, scrollWheelZoom: intactos.
    - npm run build: verde (ActivityDetailPage subiu de 10.62 kB para
      11.91 kB — toggle + 2 SVGs).
    - Validação visual na Vercel: OK. Mesmos providers/atribuição do
      mobile (OSM ↔ Esri World Imagery).
    - Commit: feat(web): toggle Mapa/Satélite no mapa do detalhe
      (igual mobile). [confirmar hash com git log]

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

- Sessões 9, 10 e 11 commitadas e pushadas (confirmar com git log + git
  status no início da Sessão 12; o commit do toggle é o mais recente).
- docs/HANDOFF.md está modificado no working tree (resíduo de sessão antiga).
  DECISÃO PRÓXIMA SESSÃO: sobrescrever com este HANDOFF e commitar, ou
  descartar com `git checkout -- docs/HANDOFF.md`. Não incluir em commits de
  código.

===============================================================================
6. SCRIPTS ÚTEIS (PowerShell)
===============================================================================

# Login
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token

# Feed com bbox
$feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=5" -Headers @{ Authorization = "Bearer $token" }
$feed | ForEach-Object { Write-Host "id=$($_.id.Substring(0,8))  title=$($_.title)  bbox=$($_.bbox -join ',')" }

# Track de uma atividade
$t = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/$id/track" -Headers @{ Authorization = "Bearer $token" }

# Build web
cd D:\Rumo\web
npm run build

# Flutter analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

===============================================================================
7. DÍVIDAS TÉCNICAS
===============================================================================

- Docker Desktop NÃO instalado no Windows local. pytest local em 94 erros de
  ConnectionRefusedError (conftest.py aponta para docker-compose.test.yml,
  Postgres/PostGIS na 5433). Os 17 testes que passam são só os que não tocam
  banco. WORKAROUND: validar em produção (Render). RESOLVER: instalar Docker
  Desktop → `cd D:\Rumo\backend && docker compose -f docker-compose.test.yml up -d`
  → `pytest -q` verde antes de qualquer mudança que dependa de testes locais.
- docs/HANDOFF.md modificado no working tree (ver seção 5).
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

===============================================================================
8. PRÓXIMOS PASSOS RECOMENDADOS (Sessão 12)
===============================================================================

PRIMEIRA AÇÃO OBRIGATÓRIA DA SESSÃO 12 (antes de qualquer mudança):
    cd D:\Rumo
    git log --oneline -5
    git status --short
    cd web ; npm run build
    cd ..\mobile
    & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
Confirmar com o usuário que o commit do toggle está no topo e que não há
pendências inesperadas.

ORDEM DE TRABALHO RECOMENDADA:
1) Resolver docs/HANDOFF.md no working tree (sobrescrever com o handoff novo
   e commitar, ou git checkout -- para descartar). Fecha pendência recorrente.
2) Instalar Docker Desktop → docker compose -f docker-compose.test.yml up -d
   → pytest -q local verde. Destrava o backend para mudanças futuras. É a
   dívida de maior impacto: sem isso, qualquer mudança de backend depende de
   validar em produção (Render), o que é lento e sujeito a cold start.
3) Perfil / Estatísticas na web. StatsSummary, StatsPeriod,
   StatsWeeklyResponse, StatsMonthlyResponse já estão tipados em
   web/src/types/api.ts. Falta UI.
4) Refinamento visual do feed: revisar altura das miniaturas (mobile 120px,
   web 96px) se ficarem altas demais. Ajuste de UX, não feature.