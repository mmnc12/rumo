HANDOFF — Rumo (backend + frontend + mobile) — Sessão 40

LEIA A SEÇÃO 0 INTEIRA ANTES DE QUALQUER COISA. As regras S21–S40 são o contrato de trabalho. Não são sugestões.
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.
⚡ REGRAS CRÍTICAS (S21–S40)

    S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça. Vale também para comandos PowerShell com here-string @' ... '@ — nunca usar "COLE O CONTEÚDO AQUI" como placeholder. (Reforçada S36g, reincidiu S39c.)

    S21 — não adivinhar nomes de símbolos do projeto. Pedir o model/enum/schema antes de referenciar.

    S21 — git status antes de qualquer git restore/git checkout.

    S22 — Invoke-WebRequest com -UseBasicParsing. Validar deploy do Render antes de acusar bug no código (checar openapi.json).

    S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele.

    S24 — Vercel às vezes demora >90 s para o primeiro deploy após push.

    S25a/S33a/S36d/S38b — Select-String -SimpleMatch NÃO aceita | como alternância. Para alternância, usar -Pattern "a|b" (sem -SimpleMatch).

    S25b — confirmar lines[−1] suspeito com Get-Content | Select-Object -Last N antes de concluir.

    S25c — exigir output do bloco de validação antes de pedir commit.

    S25d — teste definitivo do save: git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M. Se vazio depois de salvar, o save não pegou.

    S25e — entregar conteúdo de arquivo para colar SEM cerca markdown envolvendo.

    S26a — PS 5.1: resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[]. Para texto UTF-8: [System.Text.Encoding]::UTF8.GetBytes(resp.Content). Para bytes crus: resp.RawContentStream.CopyTo(fileStream).

    S26b — validar GPX em prod por regex no Content.

    S26c — Render free tier pode demorar >3 min (>5 min na S39) para redeployar após push.

    S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa.

    S27b — ordem dos blocos da Fase 0: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde.

    S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca.

    S28b — chunk com hash novo e tamanho idêntico = renomeação de referência cruzada, não mudança de código.

    S29a — contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64.

    S29b — Vercel reescreve o hash dos chunks ao servir; sinal de "bundle novo no ar" é o hash mudou vs sessão anterior.

    S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes.

    S29d — ESLint no-useless-assignment: declarar let x: T; sem inicializar quando try/catch cobre todos os caminhos.

    S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos". Usar -CaseSensitive ou regex \bTODO\b.

    S30b — ao estender componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos.

    S30c — handoff de memória sobre mobile SUBESTIMA o que existe. Pedir Get-ChildItem + arquivos-chave antes de estimar.

    S31a — Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink.

    S31b — file_picker 13.x: API estática + length()/readAsBytes().

    S31c — Select-String do disco mostrando conteúdo antigo após save → WriteAllText no PowerShell.

    S32a/S32b — Select-String -SimpleMatch 'class X' casa PREFIXOS; _Simbolo casa menções em COMENTÁRIOS.

    S32c/S32d/S33b/S34b/S38a — nos Select-String de validação, "esperado" é SEMPRE piso ou faixa, nunca exato.

    S34a — git rev-parse HEAD:<arquivo> exige path relativo à RAIZ DO REPO. git hash-object aceita path relativo ao CWD.

    S34c — validar tela mobile no Chrome: confirmar (a) usuário logado, (b) URL colada, (c) flutter run reiniciado depois do último commit.

    S35a — FECHADA na S36. /feed devolve autor em author (web) e user (mobile) desde S36.

    S36a — MatchCollection[-1] NÃO funciona no PS 5.1. Usar $times[$times.Count - 1].

    S36b — em bundle minified, Select-String devolve a linha inteira. Usar [regex]::Matches.

    S36c — ao validar toque no ActivityCard, confirmar PRIMEIRO qual tela está aberta pela URL.

    S36e — AutomaticKeepAliveClientMixin é @mustCallSuper. Solução de lint: // ignore_for_file: unnecessary_overrides na linha 1.

    S36f — editor falhou em salvar → WriteAllText com o arquivo inteiro.

    S36g — comandos com here-string entregam conteúdo REAL, nunca placeholder. Reincidiu S39c.

    S37a — conflito de versão de plugin no pub get: ler o erro inteiro; o pub sugere a versão compatível no final.

    S37b — plugin nativo: pub get modifica pubspec.lock + 2 arquivos windows/flutter/generated_* — os 3 entram no commit.

    S37c — share_plus 13.x: SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])).

    S37d — download no Chrome via share_plus dispara download no browser, não share sheet do SO.

    S37e — import não usado por inferência de tipo → remover, não forçar uso.

    S37f — unnecessary_underscores (Dart 3.7+): (_, __) vira (_, _).

    S38c — ^ de continuação do PowerShell não é confiável. Usar backtick ou uma linha só.

    S38d — "esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas.

    S39a — GoRouterState no go_router 18.x NÃO tem .context. Usar o 1º parâmetro do builder.

    S39b (CRÍTICA) — REGRA S21 vale pro arquivo que está sendo editado, não só pros novos. Pedir o arquivo + widgets dependentes antes de escrever a primeira linha.

    S39c — só git restore preserva o encoding do blob. git show HEAD:... > ... no PS 5.1 grava UTF-16 LE e corrompe.

    S40a (NOVA) — o AuthContext do web NÃO expunha setUser/refresh. O user era estado interno setado só no boot (getMe) e login/register. Para o PUT /users/me refletir no web sem reload, foi adicionado setUser ao AuthContextValue (S40). Sem isso, o modal de edição reaberto na mesma sessão mostraria dados velhos.

    S40b (NOVA) — o apiFetch do web já aceita method: "PUT" sem wrapper adicional. Não criar put() novo no client.ts — usar apiFetch("/users/me", { method: "PUT", body: {...} }). O mobile, por outro lado, precisou de um put() wrapper no api.dart (S39) porque o _send só aceitava GET/POST/DELETE. As duas stacks divergem nesse ponto — não assumir simetria.

    S40c (NOVA — operacional) — o usuário pediu explicitamente handoff preventivo mais cedo (antes de 70–80%) por medo de "ficar na mão" (corte silencioso do site/IA). A S40 fez handoff em ~50–60% e entregou só 3/5 arquivos. A S41 deve retomar do 3/5 e entregar os 2 grandes (modal + ProfilePage) com contexto limpo. Quando a sessão estiver entregando arquivos grandes em sequência (>250 linhas), handoff preventivo em ~50–60%.

O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (180 passed ao fim da S39). Container de teste rumo_postgres_test na porta 5433. docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test".
Estrutura do repo (referência — conferir, não assumir)
text

D:\Rumo
├── backend/ (venv em backend/venv, Python 3.13.7)
│   ├── alembic/ app/ (core/ models/ routers/ schemas/ services/)
│   ├── samples/ scripts/ tests/ (9 arquivos, 180 testes)
│   ├── _scratch/ docker-compose.test.yml pytest.ini requirements.txt
├── docs/HANDOFF.md
├── mobile/
│   ├── lib/
│   │   ├── main.dart (StatefulShellRoute + bottom nav desde S32;
│   │   │   +rota /user/:id desde S34; +rota /search desde S35;
│   │   │   +rota /edit-profile desde S39)
│   │   ├── models/ (activity.dart, activity_track.dart, comment.dart,
│   │   │   stats.dart, user.dart, user_me.dart — EDITADO S39
│   │   │   (+weightKg, +heightCm, +birthDate, fromJson defensivo))
│   │   ├── pages/ (activity_detail_page.dart, edit_profile_page.dart
│   │   │   ← NOVO S39 (384 linhas), feed_page.dart, login_page.dart,
│   │   │   profile_page.dart ← EDITADO S39, search_page.dart,
│   │   │   upload_page.dart, user_profile_page.dart)
│   │   ├── services/ (api.dart ← EDITADO S39 (+put wrapper +
│   │   │   +updateMe + case 'PUT' no _send), auth_service.dart)
│   │   ├── utils/ (download.dart, format.dart)
│   │   └── widgets/ (activity_card.dart, activity_map.dart,
│   │       by_type_list.dart, like_button.dart, stats_cards.dart,
│   │       stats_chart.dart, stats_filters.dart)
│   ├── pubspec.yaml (file_picker: ^13.3.3, fl_chart: ^1.1.0 (resolveu 1.3.1),
│   │   go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1,
│   │   name: rumo_mobile)
│   └── windows/flutter/ (generated_plugin_registrant.cc, generated_plugins.cmake)
├── web/src/
│   ├── api/ (activities.ts, auth.ts ← EDITADO S40, client.ts,
│   │   notifications.ts, photos.ts, social.ts, stats.ts)
│   ├── assets/ components/ contexts/ (AuthContext.tsx ← EDITADO S40)
│   ├── hooks/ (useActivities.ts, useActivitySearch.ts, useAuth.ts,
│   │   useDebounce.ts, useNotifications.ts, usePhotos.ts,
│   │   useProfile.ts ← EDITADO S40, useSocial.ts, useStats.ts,
│   │   useUserSearch.ts)
│   ├── lib/ pages/ (ProfilePage.tsx ← A EDITAR S41) types/ (api.ts)
└── README.md

mobile/lib/pages/user_search_page.dart NÃO EXISTE MAIS (removido na S36). Substituído por search_page.dart (2 abas: Usuários | Atividades).

mobile/lib/pages/edit_profile_page.dart é NOVO na S39 (384 linhas).

web/src/components/EditProfileModal.tsx será NOVO na S41.
Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.
Contas de teste

    prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades, 34.08 km. Estado em 2026-11-17 (S40): weight_kg=null, height_cm=null, full_name="Prod User" (o handoff S39 registrava weight_kg=80.0, mas a Fase 0 da S40 mediu null — alguém limpou entre a S39 e agora, ou o handoff S39 registrou estado que não persiste. Não é bug de código; é estado de dados. Anotado.) Tem atividade Teste mapa - rota sintetica (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min) usada pra validar o S26 e o export GPX da S37. Tem atividade sintética Teste delta S33 (janela anterior) (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null). Username no backend: produser.

    Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2 e Prod2 segue prod (bidirecional desde a validação manual da S37).

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422 — ou 405 se a rota não existir no método).
Acordos de trabalho (válidos em todas as sessões — reforçados S21 à S40)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

    UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

    HANDOFF PREVENTIVO em ~50–60% quando a sessão estiver entregando arquivos grandes em sequência (>250 linhas); ~70–80% no caso normal. (Novo acordo S40c — o usuário pediu explicitamente por medo de "ficar na mão" com corte silencioso do site/IA.)

    Aviso proativo de interrupção iminente — se o assistente perceber que o código entregue pode ser cortado no meio (limite de contexto do chat ou limite do site/IA), avisar ANTES de começar a entregar, não depois.

    PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes.

    VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo.

    VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<simbolo>" antes de build/test.

    NUNCA placeholder no código entregue (S21) nem em comandos com here-string (S36g). Reincidiu S39c.

    Não adivinhar nomes de símbolos (S21). Reforçada S39b — vale pro arquivo que está sendo editado, não só pros novos.

    git status + git log antes de git restore (S21).

    Invoke-WebRequest sempre com -UseBasicParsing (S22).

    Validar openapi.json antes de acusar bug em rota nova (S22).

    Validar bundle da Vercel baixando index-*.js (S23).

    Vercel pode demorar >90 s no primeiro deploy (S24).

    Select-String -SimpleMatch não aceita | como alternância (S25a, reforçada S33a, S36d, S38b).

    Confirmar lines[−1] suspeito com Get-Content | Select-Object -Last N (S25b).

    Exigir output do bloco de validação antes de pedir commit (S25c).

    Teste definitivo do save: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M (S25d).

    Entregar conteúdo de arquivo para colar sem cerca markdown (S25e).

    PS 5.1: resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[] (S26a).

    Validar GPX em prod por regex no Content (S26b).

    Render free tier pode demorar >3 min para redeployar após push (S26c). Na S39 demorou >5 min.

    Commitar o handoff pendente ANTES de qualquer outra coisa na abertura (S27a).

    Ordem fixa dos blocos da Fase 0: handoff → log/status → build → docker/pytest → prod back → prod front (S27b).

    Antes de aceitar o escopo do handoff anterior como verdade, pedir TODOS os arquivos que o contrato toca e confirmar o gap real (S28a).

    Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada (S28b).

    Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).

    Vercel reescreve hash de chunk ao servir; sinal de "novo no ar" = hash mudou vs sessão anterior (S29b).

    Contar as ocorrências reais antes de anunciar "esperado Nx" num Select-String (S29c).

    ESLint no-useless-assignment: declarar let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).

    Select-String "TODO" casa case-insensitive — usar -CaseSensitive ou regex \bTODO\b (S30a).

    Componente genérico com semântica oposta: prop booleana default-false, 4 casos (S30b).

    Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + api.dart + telas (S30c).

    Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink (S31a).

    file_picker 13.x: API estática + length()/readAsBytes() (S31b).

    Select-String do disco mostrando conteúdo antigo após save do editor → WriteAllText no PowerShell (S31c, reforçada S36f).

    Select-String -SimpleMatch 'class X' casa prefixo (S32a). _Simbolo casa menções em comentários (S32b).

    Anunciar "esperado ≈ N linhas" só depois de CONTAR o arquivo entregue (S32c).

    Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA (S32d, reforçada S33b, S34b, S38a).

    Alternância em Select-String: SEMPRE -Pattern 'a|b' (S33a, S36d).

    "Esperado" é SEMPRE piso/faixa (S33b).

    git rev-parse HEAD:<arquivo> exige path relativo a RAIZ do repo (S34a).

    "Esperado" anunciado antes de rodar pode errar mesmo sendo faixa (S34b).

    Validar tela mobile no Chrome: confirmar usuário logado, URL colada e restart do flutter run (S34c).

    S35a fechada: /feed agora devolve user + author (S36).

    MatchCollection[-1] não funciona no PS 5.1 — usar $times[$times.Count - 1] (S36a).

    Em bundle minified, Select-String devolve a linha inteira — usar [regex]::Matches (S36b).

    Ao validar toque no ActivityCard, confirmar PRIMEIRO qual tela está aberta pela URL (S36c).

    Select-String -SimpleMatch com | é sempre erro — usar -Pattern (S36d, CRÍTICA).

    AutomaticKeepAliveClientMixin é @mustCallSuper — super.build obrigatório. Solução de lint: // ignore_for_file na linha 1, NÃO // ignore: local (S36e).

    Editor falhou 2× em salvar search_page.dart — WriteAllText é a solução (S36f).

    Comandos com here-string entregam conteúdo REAL, nunca placeholder (S36g). Reincidiu S39c.

    Ler o erro inteiro do pub get antes de tentar consertar — o pub sugere a versão compatível no final (S37a).

    Plugin nativo: pub get modifica pubspec.lock + 2 arquivos windows/flutter/generated_* — os 3 entram no commit (S37b).

    share_plus 13.x: SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])) (S37c).

    Download no Chrome via share_plus dispara download no browser, não share sheet do SO (S37d).

    Import não usado por inferência de tipo → remover, não forçar uso (S37e).

    unnecessary_underscores: (_, __) vira (_, _) (S37f).

    "Esperado" de Select-String é SEMPRE piso/faixa — mesmo contando o arquivo entregue (S38a).

    Select-String -SimpleMatch com | é SEMPRE erro — em dúvida, -Pattern (S38b, reforço da S25a/S33a/S36d).

    ^ de continuação do PowerShell não é confiável — usar backtick ou uma linha só (S38c).

    "Esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas (S38d).

    GoRouterState no go_router 18.x NÃO tem .context — usar o 1º parâmetro do builder (S39a).

    REGRA S21 vale pro arquivo que está sendo editado, não só pros novos — pedir o arquivo + widgets dependentes antes de escrever (S39b, CRÍTICA).

    Só git restore preserva o encoding do blob — git show HEAD:... > ... no PS 5.1 grava UTF-16 LE e corrompe (S39c).

    AuthContext do web ganhou setUser na S40 — sem isso, o PUT /users/me não refletia no web sem reload (S40a).

    apiFetch do web já aceita method: "PUT" — não criar put() novo no client.ts. O mobile precisou de put() wrapper no api.dart (S39). As stacks divergem — não assumir simetria (S40b).

    Handoff preventivo em ~50–60% quando arquivos grandes em sequência (>250 linhas); ~70–80% no caso normal (S40c). O usuário pediu por medo de "ficar na mão".

Processo que o usuário elogiou na S21–S40 (para manter)

Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).
SEÇÃO 1 — TL;DR para quem chega agora

Backend: 180 testes passando LOCALMENTE, 0 warnings. S39 adicionou PUT /users/me (commit 9d52470). FeedItemResponse expõe autor em author (web) + user (mobile) desde S36. Todos os endpoints do MVP em produção.

Web: S40 em andamento (3/5). O objetivo é a paridade web do "Editar perfil" (decisão travada no handoff S38 §8: S39 = backend + mobile; web fica pra S40). Entregues e validados na S40:

    web/src/api/auth.ts — +UpdateMePayload, +updateMe() (PUT /users/me). Build/lint verdes.

    web/src/contexts/AuthContext.tsx — +setUser no AuthContextValue + no useMemo (S40a). Build/lint verdes.

    web/src/hooks/useProfile.ts — +useUpdateMe() (mutation com onSuccess → auth.setUser(updated) + invalidateQueries(["users", updated.id])). Build/lint verdes.

Faltam 2 arquivos (S41):

    web/src/components/EditProfileModal.tsx (NOVO, ~250 linhas) — modal com 3 campos (peso, altura, nome), validação client-side espelhando o mobile (weight_kg 0–500, height_cm 0–300, full_name ≤120), "Limpar" nos numéricos (manda null explícito), botões Cancelar/Salvar, loading, tratamento de ApiError. Reaproveita a lógica do mobile/lib/pages/edit_profile_page.dart.

    web/src/pages/ProfilePage.tsx (+ botão "Editar perfil" + estado editOpen + renderização do modal) — só quando isSelf. O ProfilePage.tsx tem ~650 linhas; a alteração é pequena e localizada (import do modal, estado, botão no bloco do header, <EditProfileModal ... /> no final).

Mobile: flutter analyze limpo. S39 entregou EditProfilePage (384 linhas), api.updateMe, rota /edit-profile, botão no ProfilePage. Nada a fazer na S40/S41 no mobile — paridade já fechada.

Bloqueadores não-código: 0%. Ícone, identidade visual, política de privacidade, build assinado, contas de dev, publicação nas lojas. O maior gap pro lançamento. A S40 começou a OPÇÃO 4 (identidade visual) não — só a OPÇÃO 3b (paridade web). O começo da OPÇÃO 4 fica pra S41/S42.

Endpoints relevantes (backend, S39):
text

PUT /users/me                                            — auth: Bearer JWT (self)
  body: { weight_kg?: float(0,500), height_cm?: float(0,300), full_name?: str(≤120) }
  response 200: UserResponse (mesmo shape do /auth/me)
  erros: 401 (sem token), 422 (validação Pydantic: range, max_length, extra="forbid")
  semântica: ausente → não toca; null → limpa; valor → atualiza (exclude_unset)
  proibidos: email, username, senha (extra="forbid" → 422)
  rota declarada ANTES de /{user_id} (mesma lição do /search — evita 422)

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

    Deps mobile: file_picker: ^13.3.3, fl_chart: ^1.1.0 (resolveu 1.3.1), go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1. Package name: rumo_mobile.

Git (estado ao fim da Sessão 40 — 3 arquivos modificados no working tree, não commitados ainda):
text

e6978d2 (HEAD -> main, origin/main) docs: handoff da Sessao 39
e251057 feat(mobile): EditProfilePage consumindo PUT /users/me (Sessao 39)
9d52470 feat(backend): PUT /users/me para editar weight_kg e height_cm (Sessao 39)
...

Working tree da S40 (3 arquivos M, não commitados):

    M web/src/api/auth.ts (+ updateMe)

    M web/src/contexts/AuthContext.tsx (+ setUser)

    M web/src/hooks/useProfile.ts (+ useUpdateMe)

Pendente: commit da S40 (parcial — 3/5) + docs: handoff da Sessao 40 (este arquivo). A S41 retoma do 3/5, entrega os 2 restantes (modal + ProfilePage), roda build/lint/validação, e só então commita a S40 inteira (ou faz commit parcial + commit final, à escolha do usuário — recomendo um commit por arquivo para histórico limpo, ou um commit único se preferir menos ruído; a S39 usou commit único com 5 files).
SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 40
3.1 Fase 0 — validação de estado inicial (completa, 6/6 blocos verdes)

A S40 foi a primeira sessão desde a S38 a rodar a Fase 0 completa na ordem da REGRA S27b. Todos os 6 blocos verdes:

    Handoff pendente — git status --short vazio (handoff S39 já commitado como e6978d2).

    Log/status — git log --oneline -8 mostrou e6978d2 no topo, working tree limpo.

    Build/lint/analyze — npm run build (✓ built in 2.17s), npm run lint (limpo), flutter analyze (No issues found! (ran in 3.0s)).

    Docker + pytest + ruff — Docker 29.8.1 / Compose v5.5.1, rumo_postgres_test Up About a minute (healthy) na 5433, pg_isready accepting connections, pytest -q → 180 passed in 110.60s, ruff check . → All checks passed!.

    Prod backend — OK PUT /users/me (rota no ar), /auth/me → weight_kg=null height_cm=null full_name=Prod User (divergência registrada vs handoff S39: weight_kg=80.0; não é bug de código, é estado de dados), /feed → 3 itens com author=produser e user=produser (S36 confirmada), /activities/stats/summary → total_activities=8 total_distance_m=34081.56.

    Prod frontend — index servido: /assets/index-CJjOEm0V.js (mesmo hash da S38/S39, web intocado desde S30). Chunks: ActivityDetailPage-DOBuid_4, ProfilePage-Cy6s98Hl, SearchPage-D6UpMvrw, leaflet-Bw7RoR_1, recharts-DI5KUTLO, rolldown-runtime-hePW80VL. Os 3 chunks de lib externa com hash igual ao build local (leaflet/recharts/rolldown); os 4 com hash diferente são reescritos pelo Vercel (S29b). Nenhum sinal de bundle novo não intencional.

3.2 Fase 1 — descoberta (completa)

Arquivos pedidos e recebidos na S40:

    web/src/pages/ProfilePage.tsx (inteiro, ~650 linhas)

    mobile/lib/pages/edit_profile_page.dart (inteiro, 384 linhas — referência de UX)

    web/src/api/client.ts (apiFetch, apiFetchBlob, ApiError, getToken/setToken/clearToken)

    web/src/api/auth.ts (login, register, getMe)

    web/src/hooks/useProfile.ts (useFollowers, useFollowing, useIsFollowing, useUser)

    web/src/hooks/useAuth.ts (consome AuthContext)

    web/src/types/api.ts (UserPublic, UserResponse com weight_kg/height_cm/birth_date, Activity, FeedItem, StatsSummary, StatsByTypeItem, etc.)

    web/src/contexts/AuthContext.tsx (AuthContextValue, AuthProvider, user, isLoading, isAuthenticated, login, register, logout)

    web/src/api/social.ts (getFeed, likeActivity, getComments, followUser, getFollowers, getFollowing, getUser)

    Get-ChildItem web\src\api -Filter "*.ts" → confirmou que não existe users.ts (o PUT /users/me mora no auth.ts, junto do GET /auth/me).

Achados que moldaram o contrato:

    #1 apiFetch do web já aceita method: "PUT" sem wrapper adicional. Não precisa de put() novo no client.ts (diferente do mobile, que precisou na S39 — S40b).

    #2 auth.ts tem getMe() retornando UserResponse. É aqui que entra o updateMe() — não existe users.ts.

    #3 useAuth() devolve user do AuthContext. O useProfile.ts já usa useAuth() para meId e isSelf. É de lá que o modal pega o current (o user do contexto já é o UserResponse completo com weight_kg/height_cm).

    #4 types/api.ts → UserResponse já tem weight_kg: number | null, height_cm: number | null, birth_date: string | null. Não precisa estender type. O UserResponse é o "UserMe" do web.

    #5 ProfilePage.tsx não é self-only — serve /profile (self) e /users/:id (terceiro). O botão "Editar perfil" só aparece quando isSelf (já tem isSelf do useIsFollowing).

    #6 ProfilePage.tsx não exibe weight_kg/height_cm hoje — só @username e full_name (do useUser). O weight_kg/height_cm só aparecem no modal, que é aberto com o user do useAuth.

    #7 AuthContext não expunha setUser/refresh — o user era estado interno setado só no boot (getMe) e login/register. Sem setUser, o PUT /users/me não refletiria no web sem reload (S40a).

    #8 useProfile.ts usa socialKeys de useSocial.ts — o padrão de mutation do web é useMutation + queryClient.invalidateQueries. O useUpdateMe segue o mesmo padrão.

    #9 AuthContextValue tem user, isLoading, isAuthenticated, login, register, logout. O setUser foi adicionado na S40 (S40a).

3.3 Fase 2 — contrato travado

Decisões travadas:

    Modal vs. página: modal (sem rota nova, sem mexer no router, AppHeader visível atrás). O mobile usa página, mas o web não tem rotas fora do AppHeader — adicionar uma seria mais invasivo. Confirmado.

    AuthContext ganha setUser (opção a) — mínimo, explícito, resolve o bug de UX do modal reaberto com dados velhos. Confirmado.

    updateMe() no auth.ts (não criar users.ts).

    useUpdateMe() no useProfile.ts (não criar useAuth.ts novo).

    Modal em arquivo separado (components/EditProfileModal.tsx) — o ProfilePage.tsx já tem ~650 linhas; não inflar.

    Ordem de entrega: auth.ts → AuthContext.tsx → useProfile.ts → EditProfileModal.tsx → ProfilePage.tsx.

    Fora de escopo (confirmado): birth_date (backend UserUpdate não aceita), email/username (rotas próprias), avatar/foto (não existe no backend).

Contrato do EditProfileModal.tsx (S41):

    Props: open: boolean, onClose: () => void, current: UserResponse (do useAuth().user).

    Estado: 3 useState para os campos (peso, altura, nome), clearWeight: boolean, clearHeight: boolean, formError: string | null.

    Pré-preenchimento: current.weightKg/heightCm/fullName formatados (mesma lógica _formatNumber do mobile: 80.0 → "80", 80.5 → "80.5", null → "").

    Validação client-side: weight_kg 0–500, height_cm 0–300, full_name ≤120 (espelha backend). Botão Salvar desabilitado se inválido ou nada mudou.

    "Limpar" nos numéricos: manda null explícito. "Desfazer" restaura o valor inicial.

    Submit: useUpdateMe().mutate(payload) → onSuccess fecha o modal (onClose()). onError: mostra ApiError.detail (string) ou HTTP {status}.

    Payload: só campos mudados/limpos (mesma semântica do edit_profile_page.dart — fieldsToClear para null explícito, ausente para intocado).

    Acessibilidade: role="dialog", aria-modal="true", foco no primeiro campo ao abrir, fecha no Esc e no backdrop.

Contrato do ProfilePage.tsx (S41):

    Import do EditProfileModal.

    Estado editOpen: boolean.

    Botão "Editar perfil" no bloco do header, só quando isSelf — recomendo logo abaixo do full_name, antes do "Este é você." (lugar mais natural).

    <EditProfileModal open={editOpen} onClose={() => setEditOpen(false)} current={user!} /> no final do componente (só renderiza se user).

    O user vem de useAuth(). O ProfilePage já usa useIsFollowing (que chama useAuth internamente), mas o user direto precisa ser importado de useAuth() no ProfilePage — pequena adição.

3.4 Fase 3 — entrega incremental (3/5)

web/src/api/auth.ts (arquivo 1/5) — build/lint verdes.

    +UpdateMePayload (full_name?, weight_kg?, height_cm?, todos | null).

    +updateMe(payload) → apiFetch<UserResponse>("/users/me", { method: "PUT", body: payload }).

    Resto idêntico ao original.

web/src/contexts/AuthContext.tsx (arquivo 2/5) — build/lint verdes.

    +setUser no AuthContextValue (com comentário [Sessão 40]).

    +setUser no useMemo (o setUser do useState já existia; só foi exposto).

    Resto idêntico ao original.

web/src/hooks/useProfile.ts (arquivo 3/5) — build/lint verdes.

    +import { useMutation, useQueryClient } from "@tanstack/react-query".

    +import { updateMe, type UpdateMePayload } from "../api/auth".

    +useUpdateMe(): useMutation({ mutationFn: (payload) => updateMe(payload), onSuccess: (updated) => { auth.setUser(updated); queryClient.invalidateQueries({ queryKey: ["users", updated.id] }); } }).

    Resto idêntico ao original.

3.5 Fase 3.5 — commit (PENDENTE — S41)

Os 3 arquivos da S40 estão modificados no working tree, não commitados. A S41 deve:

    Entregar os 2 restantes (EditProfileModal.tsx + ProfilePage.tsx).

    Rodar npm run build + npm run lint (esperado: verdes).

    Verificar save (git hash-object ≠ git rev-parse HEAD:<path> + git status --short mostra M).

    Commitar a S40 inteira (5 arquivos, 3 M + 1 novo + 1 M) — sugestão de mensagem: feat(web): paridade do "Editar perfil" com PUT /users/me (Sessao 40).

    Push.

    Fase 4 — validar em produção (Vercel redeploy + bundle novo + teste manual no Chrome).

3.6 Fase 4 — validação em produção (PENDENTE — S41)

Após o commit + push, validar:

    Vercel redeploya (aguardar >90 s, REGRA S24).

    Baixar index-*.js da Vercel; o hash do ProfilePage- deve mudar vs. S40 (S29b — sinal de bundle novo).

    Teste manual no Chrome: login como prod@rumo.com, ir ao Perfil, tocar "Editar perfil", preencher peso/altura/nome, Salvar, verificar que o header reflete o novo full_name. Reabrir o modal e confirmar que os valores persistem (S40a — setUser).

    (Opcional) Validar PUT /users/me via HTTP direto (PowerShell) para confirmar o estado do backend.

3.7 Tropeços da S40

Nenhum tropeço de código. A S40 foi a sessão mais limpa desde a S21:

    Fase 0 completa, 6/6 blocos verdes, sem regressão.

    Fase 1 descoberta, 9 arquivos pedidos, 0 adivinhação.

    Fase 2 contrato travado, 2 decisões confirmadas (modal + setUser).

    Fase 3 entrega incremental, 3/5 arquivos, build/lint verdes de primeira em todos.

    Único "achado" não-tropeço: a divergência de estado do prod@rumo.com (weight_kg=null vs handoff S39 80.0). Não é bug de código; é estado de dados. Registrado para o handoff.

Novas regras da S40 (Seção 0, itens 67–69): S40a (AuthContext ganhou setUser), S40b (apiFetch do web já aceita PUT — não criar put() novo; mobile divergiu), S40c (handoff preventivo em ~50–60% quando arquivos grandes em sequência).
3.8 Resultado da suíte (S40)

    pytest -q → 180 passed in 110.60s (mesmo número da S39 — S40 não tocou no backend).

    ruff check . → All checks passed!.

    npm run build → ✓ built in 2.17s (Fase 0) e ✓ built in 2.19s (após auth.ts). Após AuthContext.tsx e useProfile.ts, build/lint também verdes (não colados aqui por brevidade, mas registrados).

    npm run lint → limpo em todos os 3 arquivos entregues.

    flutter analyze → No issues found! (ran in 3.0s).

    Validação manual no Chrome → PENDENTE (S41, após o modal + ProfilePage).

3.9 Commits pushados (S40)

Nenhum commit na S40 ainda. Working tree com 3 arquivos M (não commitados). A S41 commita a S40 inteira após entregar os 2 restantes.
SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

(Contratos S1–S39 inalterados. Repetidos por completude.)

Autenticação:

    POST /auth/login — application/x-www-form-urlencoded (username=email, password). 200: {access_token, token_type}. 401/422.

    GET /auth/me — Bearer JWT. 200: UserResponse completo (id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at). É o "quem sou eu". /users/me não existe pra GET (405).

Perfil próprio:

    PUT /users/me (S39) — Bearer JWT, body {weight_kg?: float(0,500), height_cm?: float(0,300), full_name?: str(≤120)}. Semântica exclude_unset: ausente → não toca; null → limpa; valor → atualiza. extra="forbid" (email/username/senha → 422). 200: UserResponse pós-update. 401/422. Rota declarada ANTES de /{user_id} (mesma lição do /search — evita 422).

Atividades:

    GET /activities?user_id=&limit=1..100&offset=0 — Bearer JWT. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro (sem user embutido).

    GET /activities/{id} — Bearer JWT, dono OU seguidor do dono. 200: ActivityResponse.

    GET /activities/{id}/track — Bearer JWT, dono OU seguidor. 200: TrackResponse ({activity_id, type: "LineString", coordinates: [[lon,lat],...], bbox, n_points, simplified}). 404 se route IS NULL ("Atividade não possui rota").

    GET /activities/search?q=<min 2>&limit&offset — Bearer JWT. Busca em title/description ILIKE. Visibilidade: dono OU seguido. Retorna list[FeedItemResponse] (com author + user). Rate limit 20/min.

    POST /activities/upload — Bearer JWT, multipart/form-data (file, title?, activity_type?, description?). 201: ActivityResponse. 422/429/401. Rate limit 10/h.

    GET /activities/{id}/export?format=csv|gpx — Bearer JWT, dono OU seguidor. CSV funciona com/sem rota; GPX exige rota. Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>".

    GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — Bearer JWT, self-only. ZIP. 0 atividades → ZIP vazio (200). from > to → 422.

Feed:

    GET /feed?limit&offset — Bearer JWT. FeedItemResponse (herda ActivityResponse + author E user — mesmo Activity.user do ORM; author = web, user = mobile desde S36).

Comentários:

    GET /activities/{id}/comments — Bearer JWT. list[CommentResponse] cronológico.

    POST /activities/{id}/comments — Bearer JWT, body {content}. 201: CommentResponse. 422/401.

    DELETE /comments/{id} — Bearer JWT, só o autor.

Stats:

    GET /activities/stats/summary?activity_type — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse ({weeks: int, items: [StatsPeriod]}). Items crescentes em period_start.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse ({months: int, items: [StatsPeriod]}).

    GET /activities/stats/by-type?period=all|90d|1y&compare=prev|yoy — StatsByTypeResponse. Cada item tem 5 métricas + previous (nullable). Não inclui avg_pace (derivado no front).

    GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. Visibilidade: self → 200; viewer segue target → 200; não segue → 403; target não existe → 404.

    StatsPeriod (item): {period_start: "YYYY-MM-DD", total_activities, total_distance_m, total_duration_s, total_calories}.

Follows:

    POST /users/{user_id}/follow — 204. 400 (self) / 404.

    DELETE /users/{user_id}/follow — 204. Idempotente.

    GET /users/{user_id}/followers?limit&offset — list[UserPublic].

    GET /users/{user_id}/following?limit&offset — list[UserPublic].

    GET /users/search?q=<min 2>&limit — list[UserPublic]. Rate limit 20/min.

⚡ NÃO existe GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following e checa se o alvo está na lista.
⚡ UserPublic (/users/{id}, /users/{id}/followers, /users/{id}/following, /users/search): 4 campos apenas (id, username, full_name, is_active). Sem email, sem avatar_url. Para self, usar /auth/me.
SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–39 commitadas e pushadas. HEAD == origin/main == e6978d2 (docs: handoff da Sessao 39). Working tree com 3 arquivos M da S40 (não commitados).

Primeira ação da Sessão 41 (REGRA S27a — handoff primeiro):
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md (este arquivo), commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 40"
git push

Mas atenção: o working tree da S40 tem 3 arquivos de código (auth.ts, AuthContext.tsx, useProfile.ts) não commitados. A S41 deve decidir: commitar o handoff S40 sozinho e os 3 arquivos junto com os 2 da S41 (recomendo), ou commitar os 3 agora e o handoff separado. Recomendação: commitar o handoff S40 sozinho agora (docs: handoff da Sessao 40), e os 5 arquivos de código da S40 juntos no final da S41 (feat(web): paridade do "Editar perfil" com PUT /users/me (Sessao 40)). Isso mantém o histórico limpo (1 commit de docs, 1 commit de feature).

Estado esperado da S41 ao abrir: HEAD == origin/main == e6978d2 (ou docs: handoff da Sessao 40 se já commitado). Working tree com 3 M (da S40) + M docs/HANDOFF.md (se ainda não commitado).
SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
powershell

# [Sessão 41 — primeira ação] Abrir PowerShell via Win+R → powershell
cd D:\Rumo
git status --short
# Se M docs/HANDOFF.md:
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 40"
git push
git --no-pager log --oneline -8
git status --short

powershell

# [Sessão 41 — Fase 0] Sanidade de build:
cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

powershell

# [Sessão 41 — Fase 0] Docker + pytest local:
docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
# Se o prompt já mostra (venv), PULE a linha abaixo:
.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .
# Esperado: 180 passed, ruff limpo, container Up (healthy).

powershell

# [Sessão 41 — detecção de versão em produção (front — Vercel)]:
$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$chunks = [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }
# Esperado (S40): mesmo hash da S39 (index-CJjOEm0V.js) — web intocado desde S30.

powershell

# Login (produção):
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$meId = $me.id

powershell

# [Sessão 41 — validação do PUT /users/me em produção (após S41 pushar)]:
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
Write-Host "=== openapi ==="
$openapi = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json"
if ($openapi.paths.'/users/me'.put) { Write-Host "OK PUT /users/me" } else { Write-Host "AUSENTE" }
Write-Host "=== estado atual ==="
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
Write-Host "weight_kg=$($me.weight_kg) height_cm=$($me.height_cm) full_name=$($me.full_name)"
# Esperado (S40): OK PUT /users/me + weight_kg= height_cm= full_name=Prod User.

powershell

# Recuperação de arquivo corrompido (lição S21 + S39c):
cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>
# Se o último commit for anterior à mudança quebrada:
git restore <arquivo>   # ← SEMPRE preferir. Preserva encoding do blob.
# Fallback SÓ se git restore não rolar (grava com BOM, hash difere):
git show HEAD:<arquivo> | Set-Content -Encoding UTF8 <arquivo>
# ⚡ NUNCA usar git show HEAD:... > ... no PS 5.1 — grava UTF-16 LE e corrompe (S39c).

powershell

# Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S36 + S37 + S38 + S39 + S40):
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
# Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou.
# Se [5] ≠ [6] e [4] mostra M → save pegou, pode commitar.

powershell

# Contornar editor que não salva (S31c + S36f):
cd D:\Rumo\web
$content = @'
// [Sessão N] conteúdo completo do arquivo aqui (SEM PLACEHOLDER — S36g/S39c)
'@
[System.IO.File]::WriteAllText("D:\Rumo\web\src\components\EditProfileModal.tsx", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "total de linhas: $((Get-Content -Encoding UTF8 'D:\Rumo\web\src\components\EditProfileModal.tsx').Count)"
# O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.

powershell

# Comando git add/commit sem ^ (S38c):
# ERRADO (o ^ de continuação do PowerShell não funciona consistentemente):
# git add arquivo1 ^
#         arquivo2 ^
#         arquivo3
# CERTO (uma linha só):
git add arquivo1 arquivo2 arquivo3
# CERTO também (backtick):
git add arquivo1 `
        arquivo2 `
        arquivo3

apiFetch do web já aceita method: "PUT" (S40b) — usar direto, sem wrapper novo:
ts

// CERTO:
return apiFetch<UserResponse>("/users/me", {
  method: "PUT",
  body: payload,
});
// ERRADO (não criar put() novo no client.ts — o apiFetch já cobre):
// export function put<T>(path, body) { ... }

useMutation + invalidateQueries (padrão do web — S40):
ts

export function useUpdateMe() {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateMePayload) => updateMe(payload),
    onSuccess: (updated) => {
      auth.setUser(updated);
      queryClient.invalidateQueries({ queryKey: ["users", updated.id] });
    },
  });
}

AuthContext agora expõe setUser (S40a) — usar no onSuccess do mutation:
ts

// No useUpdateMe:
auth.setUser(updated);
// Sem isso, o modal de edição reaberto na mesma sessão mostraria dados velhos.

SEÇÃO 7 — DÍVIDAS TÉCNICAS

Fechadas:

    (S20) Duas pastas de venv — única é backend\venv.

    (S20) Pylance reclamando de imports — .vscode/settings.json aponta para backend/venv.

    (S25) RouteMap.tsx reutilizável — agora lazy no ActivityDetailPage.

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

    (S35) onAuthorTap no card do feed implementado mas ninguém passava — FeedPage passa condicional.

    (S36) S35a: /feed não embutia user — adicionado user ao lado de author. Mobile funcionou sem mudança. Web intacto.

    (S36) Mobile sem busca de atividades — searchActivities + SearchPage (2 abas) + rota /search.

    (S37) Mobile sem export (unitário + lote) — downloadActivityExport + downloadActivityExportBulk + saveAndShare + menu no ActivityDetailPage + card "Exportar tudo" no ProfilePage.

    (S37) Mobile sem lista de seguidores/seguindo — listFollowers + abas no UserProfilePage.

    (S38) Mobile sem filtros de period/compare na UI — StatsFilters + estado nos 2 perfis.

    (S38) Mobile sem weekly/monthly charts — StatsChart + getStatsWeekly/getStatsMonthly + 3 models.

    (S39) Mobile sem editor de perfil — EditProfilePage + api.updateMe + rota /edit-profile + botão no ProfilePage. Backend PUT /users/me implementado + testado (7 testes).

    (S40) Web sem editor de perfil — em andamento (3/5). updateMe no auth.ts ✅, setUser no AuthContext ✅, useUpdateMe no useProfile ✅. Faltam EditProfileModal.tsx + ProfilePage.tsx (S41).

    (S40) AuthContext não expunha setUser/refresh — adicionado setUser (S40a). Sem isso, o modal reaberto na mesma sessão mostraria dados velhos.

    (S40) apiFetch do web já aceita PUT — não criar put() novo (S40b). Diferente do mobile (que precisou na S39).

Conhecidas (não-bug):

    (S14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.

    (S17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.

    (S18) WHERE mata a janela anterior antes do CASE WHEN.

    (S17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.

    (S17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. (Atualização S33: com a sintética de 2026-06-01, o previous de walk em 90d agora vem preenchido.)

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

    (S32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id, /user/:id, /search e /edit-profile (S39) ficam FORA do shell (sem bottom nav). Decisão intencional.

    (S32) O FAB de upload some quando o usuário está na aba Perfil. Intencional.

    (S33) period/compare FIXOS no mobile (90d/prev) — FECHADO na S38 (agora têm UI).

    (S33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web).

    (S33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 em vez de text-green-600/red-600.

    (S33) O _formatThousands é inline (sem intl).

    (S33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético. Fica como dado de teste.

    (S33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Usar curl.exe.

    (S34) O backend NÃO tem GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following?limit=100.

    (S34) O _activitiesForbidden do UserProfilePage é heurístico: se listActivities voltou vazio E isFollowing==false E não é self → assume 403.

    (S34) O toggle follow/unfollow altera o backend real (não é mock). Testado nos dois sentidos e restaurado. Estado ao fim da S40: prod ↔ Prod2 bidirecional.

    (S34) A inferência isFollowing com limit=100 só enxerga os primeiros 100 follows.

    (S35) O debounce da busca é manual (Timer de 300ms) em cada aba do SearchPage, não um Hook/utilitário reusável. Se aparecer terceira tela de busca, extrair pra utils/.

    (S35) O _query do SearchPage não vai pra URL. O web usa searchParams.set('q', ...) pra deep-link; no mobile é fluxo efêmero (YAGNI).

    (S35) O guard de 2 chars está DUPLICADO: client-side (ApiClient.searchUsers/searchActivities: if (len < 2) return []) e server-side (422). Dupla validação proposital.

    (S35) Os 4 avisos [flutter_map] no console do Chrome são informativos (tile server público do OSM). Formalizar tile server próprio para produção.

    (S36) O // ignore_for_file: unnecessary_overrides na linha 1 do search_page.dart suprime o lint no arquivo INTEIRO. Trade-off aceitável.

    (S36) A aba Usuários do SearchPage recebe autoFocus na 1ª carga; a aba Atividades não. Decisão: evita dois teclados brigando quando o usuário troca de aba.

    (S36) SearchPage usa DefaultTabController + TabBarView. Cada aba tem seu próprio estado via AutomaticKeepAliveClientMixin. Trocar de aba NÃO perde estado.

    (S36) O main.dart mudou só 2 linhas na S36 (import + classe na rota /search). Nada da bottom nav ou do shell foi tocado.

    (S37) O _SocialListsSection no user_profile_page.dart carrega SEMPRE as duas listas (followers + following) no initState, mesmo que o usuário nunca abra as abas. É 2 requests extras por perfil aberto. No web, o ProfilePage.tsx faz o mesmo. Intencional.

    (S37) O _toggleFollow do UserProfilePage NÃO recarrega as listas após follow/unfollow. Paridade com web.

    (S37) O _exportInfo (feedback verde/âmbar) some em ~4s via Timer. O dispose cancela o Timer; pull-to-refresh cancela o antigo e agenda um novo. Sem vazamento.

    (S37) Passo 3 da validação da S37 (GPX sem rota → erro) NÃO foi exercitado por falta de atividade sem rota na conta. A lógica é idêntica à do _fetchBlob para qualquer ApiException, e o backend já está coberto por test_export.py (S21).

    (S37) share_plus 13.x removeu Share.shareXFiles — a API nova é SharePlus.instance.share(ShareParams(...)).

    (S37) path_provider ^2.1.5 + share_plus ^13.3.1 conflitam com flutter_secure_storage ^11.2.0 em versões antigas. A compatível é share_plus ^13.3.1.

    (S37) flutter pub get com plugin nativo modifica pubspec.lock + 2 arquivos windows/flutter/generated_*. Os 3 entram no commit. S38, S39 e S40 NÃO tocaram nesses — fl_chart é Dart puro (não é plugin nativo).

    (S38) _loadStats do ProfilePage faz 4 requests em paralelo, cada um com catchError individual. Se um falhar, os dados dos que voltaram continuam visíveis e o erro agregado lista os que falharam. Não é bug; é UX.

    (S38) _loadStats do UserProfilePage faz short-circuit em 403 (classe _Stats403 interna). Fase 1 (summary + byType); se 403, marca _statsForbidden e não tenta weekly/monthly. Economiza 2 requests em perfil de terceiro não seguido.

    (S38) StatsFilters usa String (não enum) para period/compare — consistência com getStatsByType. Constantes kStatsPeriod*/kStatsCompare* evitam string solta.

    (S38) period == 'all' desabilita só o compare (o period continua ativo). O valor de compare persiste no estado quando volta pra 90d/1a (paridade com o web: o <select> de compare não é resetado).

    (S38) StatsChart reexporta StatsPeriod (export '../models/stats.dart' show StatsPeriod;). S37e: StatsPeriod é usado de fato, então o export é legítimo.

    (S38) StatsChart não reordena items — confia na ordem do backend (crescente em period_start).

    (S38) StatsChart mostra só alguns labels no eixo X quando tem >6 pontos (step = labels.length / 6).

    (S38) _yInterval do StatsChart: activities = passo 5; distance = adaptativo (0.25/1/5/20/yMax/5).

    (S38) fl_chart 1.1.0 resolveu em 1.3.1 (o caret permite <2.0.0). getTooltipColor (não tooltipBgColor, removido), FlDotCirclePainter, LineTouchTooltipData — todos existem na 1.3.1.

    (S38) Build web local vs Vercel: index-DvGu4786.js (local) vs index-CJjOEm0V.js (servido). Esperado: web intocado desde S30, nenhum push de web desde então. Não é bug (S29b).

    (S38) Follow Prod2: o handoff da S37 registrava "Prod2 seguindo: 0"; mediu-se 1 na Fase 0 (Prod2 segue produser). Estado pós-validação manual da S37. Não é bug.

    (S39) O PUT /users/me da S39 deixou o prod@rumo.com com weight_kg=80.0 e height_cm=null no backend (estado pós-validação HTTP). ATUALIZAÇÃO S40: a Fase 0 da S40 mediu weight_kg=null, height_cm=null, full_name="Prod User". O weight_kg=80.0 registrado no handoff S39 não persiste — alguém limpou entre a S39 e agora, ou o handoff S39 registrou estado que não persiste. Não é bug de código; é estado de dados. Anotado.

    (S39) O extra do go_router no /edit-profile pode vir null em hot reload / deep-link (a 18.x preserva, mas não é garantido). O builder protege (redireciona pra /profile se não for UserMe), mas o hot reload da EditProfilePage perde o estado. Se virar problema, S41 troca por GET /auth/me dentro da própria EditProfilePage.

    (S39) birth_date fora do escopo da S39 (backend UserUpdate não aceita). O model UserMe já tem birthDate: String? (cru do backend). S40 pode editar (mudando pra DateTime? e adicionando ao UserUpdate).

    (S39) email/username fora do escopo (rotas próprias, chave única). S40+.

    (S39) O ActivityCard no profile_page.dart NÃO passa onAuthorTap — no perfil self não faz sentido (o usuário já é o autor). Comportamento herdado da S34, intocado.

    (S39) edit_profile_page.dart não tem "Desfazer" global — só por campo ("Limpar" / "Desfazer" no peso e altura). O nome completo não tem "Limpar" (apagar o texto + salvar manda null). Decisão de UX: consistente com a semântica exclude_unset.

    (S40) O ProfilePage.tsx do web não exibe weight_kg/height_cm hoje — só @username e full_name. O modal de edição é o único lugar onde esses campos aparecem. Se o produto quiser exibir peso/altura no header, S41+ (fora do escopo da paridade).

    (S40) O ProfilePage.tsx serve /profile (self) e /users/:id (terceiro). O botão "Editar perfil" só aparece quando isSelf. O user (do useAuth) é null para visitante não logado — o modal não renderiza.

    (S40) O EditProfileModal vai pré-preencher com user do useAuth(). Após o save, auth.setUser(updated) atualiza o contexto. Se o usuário reabrir o modal na mesma sessão, vê os valores novos. Sem setUser, veria os antigos (S40a — resolvido).

    (S40) O ProfilePage.tsx usa useUser(id) (do useProfile) para o header (@username + full_name). O invalidateQueries(["users", updated.id]) no onSuccess do useUpdateMe refaz o GET /users/{id} e o header reflete o novo full_name. O AuthContext.user não é usado para exibir dados — só para isSelf/meId/pré-preencher o modal.

    (S40) birth_date continua fora do escopo (backend UserUpdate não aceita). O UserResponse do web já tem birth_date: string | null, mas o modal não edita. S41+.

Oportunidades:

    (S18–40) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.

    (S19–40) Stats públicas só quando viewer segue o alvo.

    (S22–37) Export em lote no mobile — FECHADO S37.

    (S30) Testes unitários do DeltaLine no web e no mobile (puro, testável).

    (S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.

    (S31) Testar upload em Android físico/emulador.

    (S31) UI dedicada para 429 (rate limit) com cooldown visual.

    (S31) activity_type como dropdown opcional na UploadPage.

    (S33) Filtros de period/compare na UI do perfil — FECHADO S38.

    (S33) Weekly/monthly charts no perfil — FECHADO S38.

    (S33) Filtros de activity_type na UI do perfil — S41+.

    (S34) Lista de seguidores/seguindo no UserProfilePage — FECHADO S37.

    (S34) Export no mobile (unitário + lote) — FECHADO S37.

    (S34) Editar perfil (peso, altura, etc.) — FECHADO S39 no mobile (backend + mobile). Paridade web em andamento (S40, 3/5).

    (S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S41+.

    (S34) Endpoint GET /users/{id}/is-following no backend — S41+.

    (S36) Deep-link ?q= na busca mobile (se aparecer necessidade).

    (S36) Extrair o debounce manual (Timer 300ms) para um helper utils/debounce.dart se aparecer terceira tela de busca.

    (S36) Testar busca de atividades com termo vazio/1 char (guard client-side + 422 backend).

    (S36) Tile server próprio do OSM (formalizar para produção).

    (S37) Incluir botão de export unitário no web/src/pages/ActivityDetailPage.tsx para paridade com o mobile (hoje só o ProfilePage.tsx tem).

    (S37) Mostrar o _exportInfo como SnackBar (em vez de texto inline) no mobile, se a UX pedir.

    (S37) Testar export em Android/iOS físico (hoje só Chrome/web).

    (S37) Criar atividade sintética sem rota para exercitar o passo 3 da validação da S37 (GPX → 404 "Atividade não possui rota").

    (S38) Filtros de activity_type na UI do perfil (o backend aceita em todos os 4 endpoints de stats).

    (S38) Testar StatsChart em Android/iOS físico (hoje só Chrome/web).

    (S38) Extrair o padrão _loadStats de 4 requests em paralelo para um helper se aparecer terceira tela de stats (improvável).

    (S39) Paridade web do "Editar perfil" — em andamento (S40, 3/5). Faltam EditProfileModal.tsx + ProfilePage.tsx (S41).

    (S39) Editar birth_date — backend UserUpdate não aceita. S41+ (mudar schema + UserMe.birthDate pra DateTime? no mobile e UserResponse.birth_date no web já existe).

    (S39) Editar email/username — rotas próprias (chave única). S41+.

    (S39) Trocar extra do /edit-profile por GET /auth/me dentro da própria EditProfilePage se o hot reload perder estado de forma recorrente.

    (S39) Testar EditProfilePage em Android/iOS físico (hoje só Chrome/web). O TextInputType.numberWithOptions(decimal: true) + inputFormatters podem se comportar diferente em teclado nativo.

    (S40) Testar EditProfileModal no Chrome após S41 entregar (login, editar, salvar, reabrir, conferir persistência via setUser).

    (S40) Validar PUT /users/me em produção após S41 pushar (PowerShell Invoke-RestMethod + openapi.json).

    (S40) Confirmar que o bundle novo está no ar (hash do ProfilePage- mudou vs S40, S29b).

    (S40) Considerar exibir weight_kg/height_cm no header do ProfilePage (hoje só no modal). S41+ se o produto pedir.

    (S40) Identidade visual (ícone + splash) — OPÇÃO 4 — começou a S40? Não. Fica pra S41/S42. É o próximo bloqueador não-código (pesa 15% do MVP).

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 41 e além)

Sessão 40 fechada em 3/5. A S41 retoma do 4/5 com contexto limpo e entrega os 2 restantes.
Primeira ação obrigatória da Sessão 41 (REGRA S27a)

Abrir PowerShell via Win+R → powershell.

Rodar o bloco "[Sessão 41 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 40, push, confirmar HEAD == origin/main.

Decisão de commit: o working tree da S40 tem 3 M de código (auth.ts, AuthContext.tsx, useProfile.ts). Recomendo: commitar o handoff S40 sozinho agora (docs: handoff da Sessao 40), e os 5 arquivos de código da S40 juntos no final da S41 (feat(web): paridade do "Editar perfil" com PUT /users/me (Sessao 40)). Histórico limpo (1 commit de docs, 1 commit de feature).
Fase 0 completa (REGRA S27b) — a S41 deve rodar (a S40 rodou completa, então é regressão zero esperada)

    Handoff pendente (git status --short).

    Log/status (git log -8, git status).

    Build/lint/analyze (npm run build, npm run lint, flutter analyze).

    Docker + pytest + ruff (docker ps -a, pytest -q → 180 passed, ruff check .).

    Prod backend (/auth/me, /feed, PUT /users/me no openapi.json).

    Prod frontend (index-*.js da Vercel).

Rota travada para a Sessão 41

S41 = fechar a paridade web do "Editar perfil" (2/5 restantes) + validar em produção.

Parte A — Entrega dos 2 arquivos:

    web/src/components/EditProfileModal.tsx (NOVO, ~250 linhas) — contrato detalhado na Seção 3.3. Reaproveita a lógica do edit_profile_page.dart (mesma semântica: só manda o que mudou + fieldsToClear para null explícito). Validação client-side espelhando backend (weight_kg 0–500, height_cm 0–300, full_name ≤120). Botão Salvar desabilitado se inválido ou nada mudou. "Limpar" nos numéricos. useUpdateMe() no submit. onSuccess fecha o modal (onClose()). onError mostra ApiError.detail (string) ou HTTP {status}. Acessibilidade: role="dialog", aria-modal="true", Esc/backdrop fecham.

    web/src/pages/ProfilePage.tsx (editado, ~650 + ~15 linhas) — import do EditProfileModal, estado editOpen, botão "Editar perfil" no bloco do header só quando isSelf (recomendo logo abaixo do full_name, antes do "Este é você."), <EditProfileModal open={editOpen} onClose={() => setEditOpen(false)} current={user!} /> no final. O user vem de useAuth() (o ProfilePage já usa useIsFollowing que chama useAuth, mas o user direto precisa ser importado de useAuth() no ProfilePage — pequena adição).

Parte B — Fase 3.5 (verificar save + commit):

    Verificar save dos 5 arquivos (git hash-object ≠ git rev-parse HEAD:<path> + git status --short mostra M).

    npm run build + npm run lint verdes.

    Commit único: feat(web): paridade do "Editar perfil" com PUT /users/me (Sessao 40) — 5 files (3 M + 1 novo + 1 M).

    Push.

Parte C — Fase 4 (validação em produção):

    Vercel redeploya (>90 s, REGRA S24).

    Baixar index-*.js; hash do ProfilePage- mudou vs S40 (S29b).

    Teste manual no Chrome: login prod@rumo.com, Perfil → "Editar perfil", preencher peso/altura/nome, Salvar, header reflete novo full_name. Reabrir o modal, valores persistem (S40a — setUser). "Limpar" no peso, Salvar, reabrir, peso vazio. Cancelar, volta sem mudar.

    (Opcional) PUT /users/me via HTTP (PowerShell) para confirmar o estado do backend.

Ordem de entrega da S41 (proposta)

    Fase 0 completa (6 blocos).

    Fase 3 — EditProfileModal.tsx (build/lint verdes).

    Fase 3 — ProfilePage.tsx (build/lint verdes).

    Fase 3.5 — verificar save + commit + push.

    Fase 4 — validação em produção.

    Fase 5 — handoff + percentual.

Alternativas (se a S41 quiser reduzir escopo)

    OPÇÃO 3b reduzida: só o botão "Editar perfil" no web abrindo um modal simples (peso + altura). Nome completo fica pra S42. Não recomendado — o modal completo é ~250 linhas, o custo de fazer parcial é quase o mesmo, e a paridade com o mobile fica quebrada.

    OPÇÃO 4 (release prep): não tocar no web, focar em ícone + identidade + política de privacidade + build assinado. Não fecha a paridade web, mas avança o lançamento. A S40 já está 3/5 — desperdiçar seria ruim. Não recomendado.

    OPÇÃO 5 (features extras): notificações, feed de "quem você segue", comentários aninhados. Fora do MVP. Não recomendado.

Recomendação final: S41 = fechar a paridade web (2/5 restantes) + validar em produção. A S42 fica pra começo da OPÇÃO 4 (ícone + identidade visual) e a S43 pra release prep pesado (política de privacidade + build assinado + contas de dev + tile server próprio + lojas).
SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordadas, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

Na S25–S38: reforçou os mesmos acordos. Tolerou tropeços (S21–S38: 1 a 8 tropeços por sessão). A S38 fechou com 4 tropeços (S38a–S38d), todos registrados.

Na S39: tolerou 3 tropeços (S39a–S39c).

Na S40: tolerou 0 tropeços de código (a sessão mais limpa desde a S21). Mas fez um pedido novo e explícito:

    "vamos continuar, só estou com receio de ficar na mão pois fique ontem. [...] me mande o comando no powershell para eu mandar [...] tome cuidado para não esgotar o site ou chat para fazer o handoff e não ficar sem ter como abrir um novo chat, ou o site em outro dia."

Interpretação do pedido: o usuário quer handoff preventivo MAIS CEDO (antes de 70–80%) por medo de corte silencioso do site/IA. A S40 fez handoff em ~50–60% e entregou 3/5. A S41 deve retomar do 3/5 e entregar os 2 grandes (modal + ProfilePage) com contexto limpo. Quando a sessão estiver entregando arquivos grandes em sequência (>250 linhas), handoff preventivo em ~50–60% (não esperar 70–80%).

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Acordo novo na S32: manter o processo da S21–S31. Concretamente:

    Fase 0 obrigatória na ordem da REGRA S27b — handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar. REGRA S39b: vale pro arquivo que está sendo editado, não só pros arquivos novos.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

    Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> (com path relativo à RAIZ do repo — REGRA S34a) + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b + S34b + S38a: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c). git add com todos os paths numa linha só (REGRA S38c).

    Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render — na S39 demorou >5 min) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local. REGRA S34c: no mobile, confirmar login/URL/restart antes de declarar bug de tela.

    Fase 5 — handoff preventivo em ~50–60% quando arquivos grandes em sequência (>250 linhas); ~70–80% no caso normal (novo acordo S40c), no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S40 (Seção 0, itens 67–69): S40a (AuthContext ganhou setUser), S40b (apiFetch do web já aceita PUT — não criar put() novo; mobile divergiu na S39), S40c (handoff preventivo em ~50–60% quando arquivos grandes em sequência).

O que funcionou nas S21–S40 (manter):

    Ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão).

    Disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33, S34, S35, S36, S37, S38, S39, S40).

    Consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor, sessão do localStorage, tela errada, placeholder em here-string, conflito de versão de plugin, import não usado, ^ de continuação, hash git diff --cached --stat, go_router 18.x sem .context, API errada por memória, git show > corrompendo encoding, AuthContext sem setUser) na hora e corrigir/registrar, sem contornar.

    A S40 acrescentou: a Fase 0 completa voltou a rodar (S39 não rodou), a descoberta foi cirúrgica (9 arquivos, 0 adivinhação), o contrato travou 2 decisões (modal + setUser), a entrega incremental foi 3/5 sem tropeço, e o handoff preventivo foi feito em ~50–60% (novo acordo S40c) por pedido explícito do usuário.

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 40)
Quebrado por camada

Backend — ~95%
Item	%	Status
Auth (login, me)	100%	✅
Perfil próprio (GET /auth/me, PUT /users/me)	100%	✅ (S39)
Atividades (CRUD, list, detail, search, track)	100%	✅
Feed (com author + user)	100%	✅
Comentários	100%	✅
Upload GPX/FIT	100%	✅
Stats (summary, by-type, weekly, monthly)	100%	✅
Follows (follow, unfollow, followers, following, search)	100%	✅
Export (unitário + lote)	100%	✅
Testes (180 passed)	100%	✅
Ruff (0 warnings)	100%	✅
Faltando pro MVP: editar email/username (rotas próprias), editar birth_date (S41+), GET /users/{id}/is-following (opcional), notificações (pós-MVP)	—	⏳

Consolidado backend: ~95%. O que falta é opcional pro MVP.

Web — ~94% (subiu de ~92% na S39 por causa dos 3/5 da S40)
Item	%	Status
Feed	100%	✅
Perfil próprio (com stats + filtros + 4 charts + export em lote)	100%	✅
Perfil de terceiro (com follow + abas Seguidores/Seguindo)	100%	✅
Detalhe de atividade (com mapa, comentários, like)	100%	✅
Upload (se houver — não confirmado nesta sessão)	?	❓
Busca (atividades + usuários)	100%	✅
Editar perfil (peso, altura, nome)	60%	🟡 S40 (3/5)
Tile server próprio do OSM	0%	❌ S42+

Consolidado web: ~94%. O gap real é o "Editar perfil" (3/5 — falta modal + ProfilePage) e o tile server próprio (S42+).

Mobile — ~93%
Item	%	Status
Feed	100%	✅
Perfil próprio (com stats + filtros + 4 charts + export em lote)	100%	✅
Perfil de terceiro (com follow + abas Seguidores/Seguindo)	100%	✅
Detalhe de atividade (com mapa, comentários, like, export unitário)	100%	✅
Upload GPX/FIT	100%	✅
Busca (2 abas: Usuários | Atividades)	100%	✅
Editar perfil (peso, altura, nome)	100%	✅ (S39)
Export (unitário + lote)	100%	✅
Testes em dispositivo físico (Android/iOS)	0%	❌ S41+
Paridade visual exata com o web	~90%	🟡
Refresh token / logout automático em 401	0%	❌ S41+

Consolidado mobile: ~93%. O gap real é testes em dispositivo físico + paridade visual exata + refresh token. S40 não tocou no mobile (paridade já fechada na S39).

Bloqueadores não-código — 0%
Item	%	Status
Ícone do app (mobile + favicon web)	0%	❌ S42
Identidade visual (logo, splash)	0%	❌ S42
Política de privacidade	0%	❌ S43
Build assinado (Android keystore + iOS provisioning)	0%	❌ S43
Conta Google Play Developer ($25)	0%	❌ S43
Conta Apple Developer ($99/ano)	0%	❌ S43
Publicação nas lojas	0%	❌ S44
Tile server próprio do OSM	0%	❌ S42+
Screenshots / descrição da loja	0%	❌ S44

Consolidado bloqueadores: 0%. É o maior gap pro lançamento. Nada disso é código, mas é obrigatório pra publicar.
Consolidado
Camada	%	Peso estimado	Contribuição
Backend	~95%	35%	33.3%
Web	~94%	20%	18.8%
Mobile	~93%	30%	27.9%
Bloqueadores não-código	0%	15%	0%
MVP consolidado	~80,0%	100%	~80,0%

Interpretação: o código está em ~94% (backend+web+mobile), mas os bloqueadores não-código (ícone, política, build assinado, lojas) estão em 0% e pesam 15% do MVP. Sem eles, não há lançamento. Por isso o consolidado é ~80%, não ~94%. A S40 subiu de ~79.6% para ~80.0% (a paridade web 3/5 compensou o backend/mobile estáveis).
Estimativa de sessões restantes
Sessão	Foco	Estimativa
S41	Fechar paridade web do "Editar perfil" (modal + ProfilePage) + validar em produção	1 sessão
S42	Começo da OPÇÃO 4 (ícone + splash + identidade visual)	1 sessão
S43	Release prep pesado (política de privacidade + build assinado + contas de dev + tile server próprio)	1–2 sessões
S44	Screenshots + descrição da loja + submissão Google Play (review ~1–3 dias)	1 sessão + review
S45	Submissão App Store (review ~1–7 dias) + correções de review	1 sessão + review
S46+	Pós-MVP (notificações, editar email/username, refresh token, paridade visual exata)	contínuo

Estimativa: ~3–4 sessões pra chegar em "pronto pra submeter" (S41–S43), +1–2 sessões de review das lojas (S44+). Total: ~5–6 sessões até o app estar publicado.