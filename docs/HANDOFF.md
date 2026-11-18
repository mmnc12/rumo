HANDOFF — Rumo (backend + frontend + mobile) — Sessão 41
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro para o assistente novo
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

Regras críticas (S21–S41) — contrato de trabalho, não sugestão
Mantidas integralmente da S40. Adições da S41:

S41a (NOVA, pedido explícito do usuário) — aviso proativo de interrupção iminente. Se o assistente perceber que o código entregue pode ser cortado no meio (limite de contexto do chat OU limite do site/IA), avisar ANTES de começar a entregar, não depois. O usuário disse textualmente: "ontem o chat acabou no meio do código, gostaria que você avisasse se caso isso for ocorrer, não estou falando apenas do limite do chat, mas sim o limite do site (IA)." Na prática: quando o arquivo for grande (>250 linhas) e o contexto estiver acima de ~60%, avisar antes de colar.

S41b (NOVA — handoff desatualizado) — o handoff S40 dizia "3 arquivos M não commitados + handoff pendente", mas a realidade (git log) já mostrava 3deb4f8 docs: handoff S40 e fb77754 feat(web): ... (3/5) como HEAD==origin/main, working tree limpo. Regra: sempre rodar git status --short + git log --oneline -5 na Fase 0 antes de assumir o estado do handoff anterior. O handoff registra o estado no momento em que foi escrito; o commit pode ter acontecido depois.

S41c (NOVA — Vercel) — o index da Vercel mudou de index-CJjOEm0V.js (S38/S39/S40) para index-BRp7iIdJ.js na Fase 0 da S41, sem a S41 ter pushado nada. Explicação: o commit fb77754 da S40 (3 arquivos web) disparou o deploy; o hash do index mudou porque os 3 chunks de página (ProfilePage, ActivityDetailPage, SearchPage) são dependências transitivas de auth.ts/AuthContext.tsx/useProfile.ts e foram renomeados por referência cruzada (S28b). Os 3 chunks de lib externa (leaflet, recharts, rolldown-runtime) mantiveram hash. Não é bug; é deploy da sessão anterior. Regra: na Fase 0 de qualquer sessão, se o index da Vercel estiver diferente do registrado no handoff, primeiro checar git log — pode ser deploy do último commit já pushado, não bundle estranho.

S41d (NOVA — design de componente sem lib) — o repo web não tem modal/dialog genérico, e não usa @headlessui/react/radix-ui/react-modal no código (só react-hook-form e zod estão instalados, mas o ProfilePage.tsx e o resto do repo usam useState + handlers diretos). Regra: modal novo é feito à mão (<div> + useEffect para Esc/backdrop/foco/overflow:hidden), sem introduzir padrão novo. Se um dia aparecer 3º modal, extrair componente genérico.

Todas as regras S21–S40 permanecem válidas e não foram reincidentes na S41 (0 tropeços de código).

O que é LOCAL vs. o que é PRODUÇÃO
LOCAL: D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). Assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO: backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

Fluxo: editar em D:\Rumo → pytest local (Docker de teste na 5433) → commit → push → Render + Vercel redeployam → validar via HTTP em produção.

Mobile: roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render.

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
│   │   │   stats.dart, user.dart, user_me.dart — EDITADO S39)
│   │   ├── pages/ (activity_detail_page.dart, edit_profile_page.dart
│   │   │   ← NOVO S39, feed_page.dart, login_page.dart,
│   │   │   profile_page.dart, search_page.dart, upload_page.dart,
│   │   │   user_profile_page.dart)
│   │   ├── services/ (api.dart ← EDITADO S39 (+put wrapper),
│   │   │   auth_service.dart)
│   │   ├── utils/ (download.dart, format.dart)
│   │   └── widgets/ (activity_card.dart, activity_map.dart,
│   │       by_type_list.dart, like_button.dart, stats_cards.dart,
│   │       stats_chart.dart, stats_filters.dart)
│   ├── pubspec.yaml (file_picker: ^13.3.3, fl_chart: ^1.1.0 (resolveu 1.3.1),
│   │   go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1)
│   └── windows/flutter/ (generated_plugin_registrant.cc, generated_plugins.cmake)
├── web/src/
│   ├── api/ (activities.ts, auth.ts ← EDITADO S40, client.ts,
│   │   notifications.ts, photos.ts, social.ts, stats.ts)
│   ├── assets/ components/ (EditProfileModal.tsx ← NOVO S41,
│   │   AppHeader.tsx, ActivityCard.tsx, StatsCards.tsx, PeriodChart.tsx,
│   │   CommentsSection.tsx, LikeButton.tsx, NotificationBell.tsx,
│   │   PhotoGallery.tsx, PhotoUpload.tsx, ProtectedRoute.tsx,
│   │   RouteMap.tsx, ActivityResults.tsx, UserResults.tsx)
│   ├── contexts/ (AuthContext.tsx ← EDITADO S40)
│   ├── hooks/ (useActivities.ts, useActivitySearch.ts, useAuth.ts,
│   │   useDebounce.ts, useNotifications.ts, usePhotos.ts,
│   │   useProfile.ts ← EDITADO S40, useSocial.ts, useStats.ts,
│   │   useUserSearch.ts)
│   ├── lib/ pages/ (ProfilePage.tsx ← EDITADO S41) types/ (api.ts)
└── README.md
Como rodar comandos Flutter
Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Sempre usar & "C:\Users\nasci\flutter\bin\flutter.bat" <comando> (o flutter puro às vezes não é reconhecido no PS).

Contas de teste
prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades, 34.081,56 m. Estado em 2026-11-17 (S41, medido na Fase 0 e confirmado na Fase 4): weight_kg=null, height_cm=null, full_name="Prod User". Username backend: produser. O weight_kg=80.0 registrado no handoff S39 não persiste — confirmado em 3 sessões seguidas (S39 registrou 80.0, S40 mediu null, S41 mediu null). Não é bug de código; é estado de dados (alguém limpou entre S39 e S40, ou o handoff S39 registrou estado transitório que não foi persistido). Anotado e encerrado como "estado".

Tem atividade Teste mapa - rota sintetica (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min).

Tem atividade sintética Teste delta S33 (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at=2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null).

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod ↔ Prod2 bidirecional desde a validação manual da S37.

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422 ou 405).

Acordos de trabalho (válidos em todas as sessões — reforçados S21 à S41)
SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar trecho alterado com // [Sessão N] ou // [Sessão N — fix].

UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

HANDOFF PREVENTIVO em ~50–60% quando a sessão estiver entregando arquivos grandes em sequência (>250 linhas); ~70–80% no caso normal. (S40c — pedido explícito do usuário por medo de "ficar na mão".)

AVISO PROATIVO DE INTERRUPÇÃO IMINENTE (S41a) — antes de começar a entregar, não depois.

PERCENTUAL DE PRONTIDÃO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada, com consolidado e estimativa de sessões restantes.

VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo.

VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<símbolo>" antes de build/test.

NUNCA placeholder no código entregue (S21) nem em comandos com here-string (S36g).

Não adivinhar nomes de símbolos (S21, reforçada S39b). Vale pro arquivo que está sendo editado, não só pros novos.

git status + git log antes de git restore (S21).

Invoke-WebRequest sempre com -UseBasicParsing (S22).

Validar openapi.json antes de acusar bug em rota nova (S22).

Validar bundle da Vercel baixando index-*.js (S23).

Vercel pode demorar >90 s no primeiro deploy (S24).

Select-String -SimpleMatch não aceita | como alternância (S25a, S33a, S36d, S38b). Para alternância, usar -Pattern "a|b" (sem -SimpleMatch).

Confirmar lines[-1] suspeito com Get-Content | Select-Object -Last N antes de concluir (S25b).

Exigir output do bloco de validação antes de pedir commit (S25c).

Teste definitivo do save: git hash-object ≠ git rev-parse HEAD:<path> + git status --short mostra M (S25d + S34a — path relativo à raiz do repo no rev-parse; hash-object aceita path relativo ao CWD).

Entregar conteúdo de arquivo para colar SEM cerca markdown envolvendo (S25e).

PS 5.1: resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[] (S26a).

Validar GPX em prod por regex no Content (S26b).

Render free tier pode demorar >3 min (>5 min na S39) para redeployar (S26c).

Commitar o handoff pendente ANTES de qualquer outra coisa (S27a).

Ordem fixa dos blocos da Fase 0: handoff → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde (S27b).

Antes de aceitar o escopo do handoff anterior como verdade, pedir TODOS os arquivos que o contrato toca (S28a).

Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada (S28b).

Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).

Vercel reescreve hash de chunk; sinal de "novo no ar" = hash mudou vs. sessão anterior (S29b).

Contar ocorrências reais antes de anunciar "esperado Nx" (S29c).

ESLint no-useless-assignment: let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).

Select-String "TODO" casa case-insensitive "Todos". Usar -CaseSensitive ou regex \bTODO\b (S30a).

Componente genérico com semântica oposta: prop booleana default-false, 4 casos (S30b).

Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + arquivos-chave antes de estimar (S30c).

Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink (S31a).

file_picker 13.x: API estática + length()/readAsBytes() (S31b).

Select-String do disco mostrando conteúdo antigo após save → WriteAllText no PowerShell (S31c, reforçada S36f).

Select-String -SimpleMatch 'class X' casa PREFIXOS; _Simbolo casa menções em comentários (S32a/S32b).

"Esperado" de Select-String é SEMPRE piso ou faixa, nunca exato (S32c/S32d/S33b/S34b/S38a).

MatchCollection[-1] não funciona no PS 5.1. Usar $times[$times.Count - 1] (S36a).

Bundle minified: Select-String devolve a linha inteira. Usar [regex]::Matches (S36b).

Toque no ActivityCard: confirmar PRIMEIRO qual tela está aberta pela URL (S36c).

AutomaticKeepAliveClientMixin é @mustCallSuper — super.build obrigatório. Lint: // ignore_for_file: unnecessary_overrides na linha 1 (S36e).

Editor falhou em salvar → WriteAllText com o arquivo inteiro (S36f).

share_plus 13.x: SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])) (S37c).

Download no Chrome via share_plus dispara download no browser, não share sheet do SO (S37d).

Import não usado por inferência de tipo → remover, não forçar uso (S37e).

unnecessary_underscores (Dart 3.7+): (_, __) vira (_, _) (S37f).

^ de continuação do PowerShell não é confiável — usar backtick ou uma linha só (S38c).

"Esperado" de git diff --cached --stat é piso/faixa, nunca estimativa de linhas (S38d).

GoRouterState no go_router 18.x NÃO tem .context — usar o 1º parâmetro do builder (S39a).

REGRA S21 vale pro arquivo que está sendo editado, não só pros novos (S39b, CRÍTICA).

Só git restore preserva o encoding do blob — git show HEAD:... > ... no PS 5.1 grava UTF-16 LE e corrompe (S39c).

AuthContext do web ganhou setUser na S40 (S40a).

apiFetch do web já aceita method: "PUT" — não criar put() novo no client.ts. O mobile precisou de put() wrapper no api.dart (S39). As stacks divergem — não assumir simetria (S40b).

Handoff preventivo em ~50–60% quando arquivos grandes em sequência (>250 linhas); ~70–80% no caso normal (S40c).

S41a–S41d (novas, vide acima).

Processo que o usuário elogiou na S21–S41 (para manter)
Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).

SEÇÃO 1 — TL;DR para quem chega agora
Backend: 180 testes passando LOCALMENTE, 0 warnings. S39 adicionou PUT /users/me (commit 9d52470). FeedItemResponse expõe autor em author (web) + user (mobile) desde S36. Todos os endpoints do MVP em produção. Estado inalterado desde S39 (S40 e S41 não tocaram no backend).

Web: S41 fechou a paridade web do "Editar perfil" (5/5). Entregues nas S40+S41:

web/src/api/auth.ts — +UpdateMePayload, +updateMe() (PUT /users/me) ✅ S40

web/src/contexts/AuthContext.tsx — +setUser no AuthContextValue + no useMemo ✅ S40

web/src/hooks/useProfile.ts — +useUpdateMe() (mutation com onSuccess → auth.setUser(updated) + invalidateQueries(["users", updated.id])) ✅ S40

web/src/components/EditProfileModal.tsx — NOVO (~300 linhas): modal com 3 campos, validação espelhando mobile, "Limpar"/"Desfazer", Esc/backdrop, foco, role="dialog" ✅ S41

web/src/pages/ProfilePage.tsx — EDITADO (+~20 linhas): +import useAuth, +import EditProfileModal, +editOpen, botão "Editar perfil" ao lado de "Este é você." quando isSelf, <EditProfileModal> no final ✅ S41

Mobile: flutter analyze limpo. S39 entregou EditProfilePage (384 linhas), api.updateMe, rota /edit-profile, botão no ProfilePage. Nada a fazer no mobile — paridade já fechada na S39.

Bloqueadores não-código: 0%. Ícone, identidade visual, política de privacidade, build assinado, contas de dev, publicação nas lojas. O maior gap pro lançamento. Próximo alvo: OPÇÃO 4 (identidade visual), S42/S43.

Endpoints relevantes (backend, S39)
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

Deps web relevantes: React 19, Vite 8, TypeScript 6, Tailwind 3.4, react-router-dom 7, @tanstack/react-query 5, react-leaflet 5, recharts 3. Não usa @headlessui/radix/react-modal (S41d). Tem react-hook-form e zod instalados, mas não usa no código existente.

Deps mobile: file_picker: ^13.3.3, fl_chart: ^1.1.0 (resolveu 1.3.1), go_router: ^18.1.2, path_provider: ^2.1.5, share_plus: ^13.3.1. Package name: rumo_mobile.

Git (estado ao fim da Sessão 41 — working tree limpo)
text
6701560 (HEAD -> main, origin/main) feat(web): EditProfileModal + botao Editar perfil no ProfilePage (Sessao 41, 5/5)
fb77754 feat(web): PUT /users/me + setUser no AuthContext + useUpdateMe (Sessao 40, 3/5)
3deb4f8 docs: handoff da Sessao 40
e6978d2 docs: handoff da Sessao 39
e251057 feat(mobile): EditProfilePage consumindo PUT /users/me (Sessao 39)
9d52470 feat(backend): PUT /users/me para editar weight_kg e height_cm (Sessao 39)
git status --short vazio. HEAD == origin/main. Pendente: commit do handoff S41 (este arquivo) — primeira ação da S42 (S27a).

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 41
3.1 Fase 0 — validação de estado inicial (completa, 6/6 blocos verdes)
Primeira sessão desde a S40 a rodar a Fase 0 completa na ordem da REGRA S27b. Todos os 6 blocos verdes:

Handoff pendente — git status --short vazio. Handoff S40 já commitado como 3deb4f8. Achado S41b: o handoff S40 dizia "3 arquivos M + handoff pendente", mas o git log mostrou que a S40 já tinha commitado o handoff (3deb4f8) e os 3 arquivos web (fb77754). O handoff S40 registrou estado anterior ao commit.

Log/status — HEAD == origin/main == fb77754. Working tree limpo.

Build/lint/analyze — npm run build verde, npm run lint limpo, flutter analyze No issues found!.

Docker + pytest + ruff — rumo_postgres_test Up (healthy) na 5433, pytest -q → 180 passed, ruff check . → All checks passed!.

Prod backend — OK PUT /users/me (rota da S39 no ar), /auth/me → weight_kg=null height_cm=null full_name=Prod User, /feed → 3 itens com author=produser e user=produser (S36 confirmada), /activities/stats/summary → total_activities=8 total_distance_m=34081.56.

Prod frontend — index servido: /assets/index-BRp7iIdJ.js (diferente do index-CJjOEm0V.js registrado na S40). Achado S41c: o hash mudou porque o commit fb77754 da S40 disparou o deploy; os 3 chunks de página (ProfilePage-, ActivityDetailPage-, SearchPage-) mudaram de hash (S28b), os 3 de lib externa (leaflet-, recharts-, rolldown-runtime-) mantiveram. Não é bug.

3.2 Fase 1 — descoberta (completa)
Arquivos pedidos e recebidos na S41:

web/src/pages/ProfilePage.tsx (~1019 linhas — arquivo a editar, S39b)

web/src/api/auth.ts (S40 — confirmar UpdateMePayload/updateMe)

web/src/contexts/AuthContext.tsx (S40 — confirmar setUser + user)

web/src/hooks/useProfile.ts (S40 — confirmar useUpdateMe)

web/src/types/api.ts (confirmar UserResponse)

mobile/lib/pages/edit_profile_page.dart (384 linhas — referência de UX)

Get-ChildItem web/src/components -Filter "*.tsx" (confirmar que não existe modal/dialog genérico)

web/package.json (confirmar libs)

Achados que moldaram o contrato:

Nenhum modal/dialog genérico existe — modal feito à mão (S41d).

UpdateMePayload já existe (auth.ts, S40). Só importar.

useUpdateMe() já existe (useProfile.ts, S40) com setUser + invalidateQueries no onSuccess. Só chamar .mutate(payload, { onSuccess, onError }).

AuthContext expõe user: UserResponse | null e setUser (S40).

UserResponse extends UserPublic e tem weight_kg/height_cm/full_name: T | null. Bate com o backend.

Referência de UX (mobile): _formatNumber (null→"", inteiro→"80", senão→"80.5"), _parseNumber (aceita ,/.), validação (0,500)/(0,300)/≤120, "vazio = não toca", "Limpar = null explícito", sem "Limpar" no full_name (apagar texto + salvar → null).

ProfilePage.tsx já tem useIsFollowing(id) retornando { isFollowing, isSelf }, mas não importava useAuth diretamente. Adicionado na S41.

Botão "Editar perfil": no bloco {isSelf ? ... : ...}, substituído <p>Este é você.</p> por um <div> com o texto + botão. Fica onde o "Seguir" do terceiro fica (S41).

Modal no final do componente, depois do </main>, dentro do <div className="min-h-screen"> — backdrop fixed inset-0 cobre tudo, AppHeader fica atrás (S41).

Tailwind 3.4 disponível, rumo-500/rumo-600 é a cor de CTA do projeto.

Padrão de erro: ApiError de ../api/client, err.detail string → mostra; senão Falha ao salvar (HTTP N). — mesmo padrão do handleExportAll.

Sem react-hook-form/zod no código existente (só instalados) — useState + validação derivada (S41).

Acessibilidade: role="dialog", aria-modal, aria-labelledby, foco no primeiro input, Esc/backdrop fecham, body com overflow:hidden.

3.3 Fase 2 — contrato travado
Decisões travadas:

Modal à mão (sem lib) — S41d.

useState + validação derivada (sem react-hook-form/zod) — consistente com o repo.

useUpdateMe().mutate(payload, { onSuccess: onClose, onError }) — reaproveita S40.

Payload com semântica do mobile: intocado → ausente; "Limpar" → null; valor novo → valor. payload vazio → onClose() sem request (idempotente).

Botão "Editar perfil" ao lado de "Este é você." (flex-wrap).

Modal fora do <main> (backdrop cobre tudo).

Fora de escopo (confirmado): birth_date (backend não aceita), email/username (rotas próprias), avatar/foto (não existe no backend).

3.4 Fase 3 — entrega incremental (5/5)
Arquivo 4/5 (web/src/components/EditProfileModal.tsx, NOVO) — build/lint verdes de primeira.

Arquivo 5/5 (web/src/pages/ProfilePage.tsx, editado) — build/lint verdes de primeira. 1034 linhas no disco (1019 originais + ~15 do bloco do modal/imports/estado).

3.5 Fase 3.5 — verificar save + commit (completa)
Save verificado: 5694e9... (disco) ≠ f81d5a... (HEAD) + M no git status.

Build: ✓ built in 5.83s, 825 módulos, novos chunks ProfilePage-DBRAiqeH.js (28.31 kB) + index-DqP5ShST.js (436.25 kB).

Lint: limpo.

Commit único: 6701560 feat(web): EditProfileModal + botao Editar perfil no ProfilePage (Sessao 41, 5/5).

Push: HEAD == origin/main, working tree limpo.

3.6 Fase 4 — validação em produção (completa)
Após o push:

Vercel redeployou — index servido com hash novo (diferente do BRp7iIdJ da Fase 0), chunks de página com hash novo e chunks de lib com hash estável (S28b/S29b). Bundle novo no ar.

Backend estável — /auth/me com weight_kg=null height_cm=null full_name=Prod User.

Teste manual no Chrome (feito pelo usuário, relatado como "tudo como esperado"):

Login prod@rumo.com ✅
Perfil mostra "Este é você." + botão "Editar perfil" ✅
Modal abre com pré-preenchimento correto e foco no peso ✅
Preenche peso/altura, salva, modal fecha ✅
Reabre o modal → mostra valores novos (S40a — setUser funcionando) ✅
"Limpar" peso → "Desfazer" vira, input esvazia, salva ✅
Reabre → peso vazio, altura intocada ✅
Cancelar/Esc/backdrop fecham ✅
Validação client-side (peso 999 → borda vermelha + mensagem + Salvar desabilitado) ✅
A S41 fechou a paridade web do "Editar perfil" em produção. ✅

3.7 Tropeços da S41
Nenhum tropeço de código. A S41 foi ainda mais limpa que a S40:

Fase 0 completa, 6/6 blocos verdes.

Fase 1 descoberta, 8 itens pedidos (incluindo Get-ChildItem e package.json), 0 adivinhação.

Fase 2 contrato travado, 3 decisões confirmadas (modal à mão, useState sem RHF, botão ao lado do "Este é você.").

Fase 3 entrega incremental, 2/2 arquivos, build/lint verdes de primeira em ambos.

Fase 4 validação manual no Chrome, todos os cenários passaram.

Único "achado" não-tropeço: S41b (handoff S40 desatualizado sobre o que estava commitado) + S41c (hash da Vercel da S40, não da S41).

3.8 Resultado da suíte (S41)
pytest -q → 180 passed (mesmo número da S39/S40 — S41 não tocou no backend).

ruff check . → All checks passed!.

npm run build → ✓ built in 5.83s (Fase 3.5) e verde na Fase 0.

npm run lint → limpo em ambos os arquivos entregues.

flutter analyze → No issues found!.

Validação manual no Chrome → passou (10 cenários, S41).

3.9 Commits pushados (S41)
6701560 feat(web): EditProfileModal + botao Editar perfil no ProfilePage (Sessao 41, 5/5) (2 files: 1 novo + 1 M).

fb77754 feat(web): PUT /users/me + setUser no AuthContext + useUpdateMe (Sessao 40, 3/5) (já commitado antes da S41 começar — vide S41b).

3deb4f8 docs: handoff da Sessao 40.

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES
(Contratos S1–S40 inalterados. Repetidos por completude.)

Autenticação
text
POST /auth/login — application/x-www-form-urlencoded (username=email, password).
  200: {access_token, token_type}. 401/422.
GET /auth/me — Bearer JWT.
  200: UserResponse completo (id, email, username, full_name, weight_kg,
       height_cm, birth_date, is_active, created_at). É o "quem sou eu".
  /users/me não existe pra GET (405).
Perfil próprio
text
PUT /users/me (S39) — Bearer JWT, body {weight_kg?: float(0,500), height_cm?:
  float(0,300), full_name?: str(≤120)}. Semântica exclude_unset: ausente →
  não toca; null → limpa; valor → atualiza. extra="forbid" (email/username/
  senha → 422). 200: UserResponse pós-update. 401/422. Rota declarada ANTES
  de /{user_id}.
Atividades
text
GET /activities?user_id=&limit=1..100&offset=0 — Bearer JWT. Filtra por
  usuário. Para user_id == currentUserId, sempre passa; para terceiro,
  requer seguir (403 se não seguir). Retorna ActivityResponse[] puro.
GET /activities/{id} — Bearer JWT, dono OU seguidor do dono. 200: ActivityResponse.
GET /activities/{id}/track — Bearer JWT, dono OU seguidor. 200: TrackResponse
  ({activity_id, type: "LineString", coordinates: [[lon,lat],...], bbox,
  n_points, simplified}). 404 se route IS NULL ("Atividade não possui rota").
GET /activities/search?q=<min 2>&limit&offset — Bearer JWT. Busca em title/
  description ILIKE. Visibilidade: dono OU seguido. list[FeedItemResponse].
  Rate limit 20/min.
POST /activities/upload — Bearer JWT, multipart/form-data (file, title?,
  activity_type?, description?). 201: ActivityResponse. 422/429/401.
  Rate limit 10/h.
GET /activities/{id}/export?format=csv|gpx — Bearer JWT, dono OU seguidor.
  CSV funciona com/sem rota; GPX exige rota.
  Content-Disposition: attachment; filename="rumo_<id>_<type>.<ext>".
GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] —
  Bearer JWT, self-only. ZIP. 0 atividades → ZIP vazio (200). from > to → 422.
Feed
text
GET /feed?limit&offset — Bearer JWT. FeedItemResponse (herda ActivityResponse +
  author E user — mesmo Activity.user do ORM; author = web, user = mobile
  desde S36).
Comentários
text
GET /activities/{id}/comments — Bearer JWT. list[CommentResponse] cronológico.
POST /activities/{id}/comments — Bearer JWT, body {content}. 201: CommentResponse. 422/401.
DELETE /comments/{id} — Bearer JWT, só o autor.
Stats
text
GET /activities/stats/summary?activity_type — StatsSummary.
GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse ({weeks, items}).
  Items crescentes em period_start.
GET /activities/stats/monthly?months=N — StatsMonthlyResponse ({months, items}).
GET /activities/stats/by-type?period=all|90d|1y&compare=prev|yoy — StatsByTypeResponse.
  Cada item tem 5 métricas + previous (nullable). Não inclui avg_pace (derivado no front).
GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes.
  Visibilidade: self → 200; viewer segue target → 200; não segue → 403;
  target não existe → 404.
StatsPeriod (item): {period_start: "YYYY-MM-DD", total_activities,
  total_distance_m, total_duration_s, total_calories}.
Follows
text
POST /users/{user_id}/follow — 204. 400 (self) / 404.
DELETE /users/{user_id}/follow — 204. Idempotente.
GET /users/{user_id}/followers?limit&offset — list[UserPublic].
GET /users/{user_id}/following?limit&offset — list[UserPublic].
GET /users/search?q=<min 2>&limit — list[UserPublic]. Rate limit 20/min.
⚡ NÃO existe GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following e checa se o alvo está na lista.

⚡ UserPublic (/users/{id}, /users/{id}/followers, /users/{id}/following, /users/search): 4 campos apenas (id, username, full_name, is_active). Sem email, sem avatar_url. Para self, usar /auth/me.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Sessões 9–41 commitadas e pushadas. HEAD == origin/main == 6701560. Working tree limpo.

Primeira ação da Sessão 42 (REGRA S27a — handoff primeiro):

powershell
cd D:\Rumo
git status --short
Se aparecer M docs/HANDOFF.md (este arquivo), commitar:

powershell
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 41"
git push
Estado esperado da S42 ao abrir: HEAD == origin/main == 6701560 (ou o commit do handoff S41 se já commitado). Working tree com M docs/HANDOFF.md (se ainda não commitado). Zero arquivos de código pendentes — a S41 fechou 5/5 e a S40 já estava commitada.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)
powershell
# [Sessão 42 — primeira ação] Abrir PowerShell via Win+R → powershell
cd D:\Rumo
git status --short
# Se M docs/HANDOFF.md:
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 41"
git push
git --no-pager log --oneline -8
git status --short
powershell
# [Sessão 42 — Fase 0] Sanidade de build:
cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
powershell
# [Sessão 42 — Fase 0] Docker + pytest local:
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
# [Sessão 42 — detecção de versão em produção (front — Vercel)]:
$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
$chunks = [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }
# Esperado (fim da S41): hash do index diferente do BRp7iIdJ (da S40),
# ProfilePage- com hash diferente do BOESyRiB (da S40), libs (leaflet,
# recharts, rolldown-runtime) com hash estável.
powershell
# Login (produção):
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$meId = $me.id
powershell
# Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S36 + S37 + S38 + S39 + S40 + S41):
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
[System.IO.File]::WriteAllText("D:\Rumo\web\src\components\X.tsx", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "total de linhas: $((Get-Content -Encoding UTF8 'D:\Rumo\web\src\components\X.tsx').Count)"
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
apiFetch do web já aceita method: "PUT" (S40b) — usar direto, sem wrapper novo
ts
// CERTO:
return apiFetch<UserResponse>("/users/me", {
  method: "PUT",
  body: payload,
});
// ERRADO (não criar put() novo no client.ts — o apiFetch já cobre):
// export function put<T>(path, body) { ... }
useMutation + invalidateQueries (padrão do web — S40)
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
AuthContext expõe setUser (S40a) — usar no onSuccess do mutation
ts
// No useUpdateMe:
auth.setUser(updated);
// Sem isso, o modal de edição reaberto na mesma sessão mostraria dados velhos.
SEÇÃO 7 — DÍVIDAS TÉCNICAS
Fechadas
(Todas as S1–S39 continuam fechadas. Adicionadas na S40/S41:)

(S40) Web sem editor de perfil — FECHADO na S41 (5/5). updateMe no auth.ts ✅, setUser no AuthContext ✅, useUpdateMe no useProfile ✅ (S40); EditProfileModal.tsx + ProfilePage.tsx ✅ (S41).

(S40) AuthContext não expunha setUser/refresh — setUser adicionado (S40a).

(S40) apiFetch do web já aceita PUT — não criar put() novo (S40b). Mobile divergiu (S39).

(S41) Paridade web do "Editar perfil" — FECHADO. Validado em produção no Chrome.

Conhecidas (não-bug)
(S1–S40 continuam. Adicionadas na S41:)

(S41) Estado do prod@rumo.com: weight_kg=null height_cm=null full_name="Prod User" — confirmado em 3 sessões (S39 registrou 80.0, S40 mediu null, S41 mediu null). Não é bug; é estado de dados. Encerrado como estado.

(S41) EditProfileModal.tsx bundlado dentro de ProfilePage-*.js — o modal só é importado pelo ProfilePage, então o Vite não separa em chunk próprio. Não é bug; é o comportamento esperado de code-splitting por entry point. Se um dia outro lugar precisar do modal, ele vira chunk compartilhado.

(S41) EditProfileModal usa useState + validação derivada, não react-hook-form/zod — consistente com o resto do repo (ProfilePage.tsx, AppHeader.tsx usam useState). react-hook-form e zod estão instalados mas não usados. Decisão de consistência.

(S41) formatNumber em EditProfileModal.tsx duplica a lógica de _formatNumber do edit_profile_page.dart — stacks diferentes (Dart vs TS), paridade manual. Aceitável.

(S41) EditProfileModal recebe current via prop (do useAuth().user no ProfilePage), não lê do contexto direto. Decisão de desacoplamento/testabilidade.

(S41) Botão "Editar perfil" só aparece quando user && isSelf — se user for null (boot antes do /auth/me), o botão não renderiza. Aceitável; isLoading do AuthContext cobre o boot no ProtectedRoute.

(S41) Modal não tem "Limpar" no full_name — apagar o texto + salvar manda null, exatamente como o mobile. Paridade mantida. Decisão de UX.

(S41) Modal não tem "Desfazer" global — só por campo ("Limpar" → "Desfazer" nos numéricos). Nome completo: apagar texto + cancelar descarta; sem "Limpar" específico. Mesma decisão do mobile.

(S41) Apagar o texto do peso/altura sem "Limpar" e salvar NÃO manda null — o campo intocado/igual ao inicial fica ausente. Se o usuário quiser limpar de verdade, precisa acionar "Limpar". Mesma semântica do mobile (S39).

(S41) ProfilePage.tsx não exibe weight_kg/height_cm no header — só no modal. Se o produto quiser exibir, S42+.

(S41) birth_date continua fora do escopo — backend UserUpdate não aceita. S42+ (mudar schema).

(S41) email/username continuam fora do escopo — rotas próprias, chave única. S42+.

Oportunidades
(S1–S40 continuam. Atualizadas na S41:)

(S39) Paridade web do "Editar perfil" — FECHADO S41.

(S40) Testar EditProfileModal no Chrome — FECHADO S41 (10 cenários, passou).

(S40) Validar PUT /users/me em produção após push — FECHADO S41 (validação manual no Chrome exercitou o PUT).

(S40) Confirmar bundle novo no ar — FECHADO S41 (hash do ProfilePage- mudou vs S40).

(S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S42+.

(S34) Endpoint GET /users/{id}/is-following no backend — S42+.

(S36) Deep-link ?q= na busca mobile (se aparecer necessidade) — S42+.

(S36) Extrair o debounce manual (Timer 300ms) para utils/debounce.dart se aparecer terceira tela de busca — S42+.

(S36) Tile server próprio do OSM (formalizar para produção) — S42+.

(S37) Incluir botão de export unitário no web/src/pages/ActivityDetailPage.tsx para paridade com o mobile — S42+.

(S38) Filtros de activity_type na UI do perfil (backend aceita em todos os 4 endpoints de stats) — S42+.

(S38) Testar StatsChart em Android/iOS físico — S42+.

(S39) Editar birth_date — backend UserUpdate não aceita. S42+.

(S39) Editar email/username — rotas próprias. S42+.

(S39) Trocar extra do /edit-profile por GET /auth/me dentro da própria EditProfilePage se o hot reload perder estado de forma recorrente — S42+.

(S39) Testar EditProfilePage em Android/iOS físico — S42+.

(S40) Exibir weight_kg/height_cm no header do ProfilePage (hoje só no modal). S42+ se o produto pedir.

(S41) Identidade visual (ícone + splash) — OPÇÃO 4. Próximo bloqueador não-código (pesa 15% do MVP). S42/S43.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 42 e além)
Sessão 41 fechada em 5/5 + validada em produção
A paridade web do "Editar perfil" está completa e validada. O código do MVP está em ~95% (backend+web+mobile). O que falta agora é bloqueador não-código.

Primeira ação obrigatória da Sessão 42 (REGRA S27a)
Abrir PowerShell via Win+R → powershell. Rodar o bloco "[Sessão 42 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 41, push, confirmar HEAD == origin/main.

Fase 0 completa (REGRA S27b) — a S42 deve rodar
Handoff pendente (git status --short).

Log/status (git log -8, git status).

Build/lint/analyze (npm run build, npm run lint, flutter analyze).

Docker + pytest + ruff (docker ps -a, pytest -q → 180 passed, ruff check .).

Prod backend (/auth/me, /feed, PUT /users/me no openapi.json).

Prod frontend (index-*.js da Vercel).

Nota S41b: rodar git log primeiro. O handoff S40 estava desatualizado sobre o estado do commit; o handoff S41 registra o estado real (6701560 como HEAD==origin/main, working tree limpo), mas sempre confirmar.

Rota recomendada para a Sessão 42
OPÇÃO 4 — identidade visual (começo). A S41 fechou o código do MVP. Agora o gargalo é 100% não-código.

Escopo da S42 (a ser travado com o usuário na Fase 1):

Ícone do app (mobile + favicon web) — gerar/fornecer, criar web/public/favicon.ico + web/public/logo192.png/logo512.png, atualizar web/index.html, atualizar mobile/android/app/src/main/res/mipmap-*/ + mobile/ios/Runner/Assets.xcassets/AppIcon.appiconset/.

Splash screen (mobile) — mobile/android/app/src/main/res/drawable/launch_background.xml + mobile/ios/Runner/Base.lproj/LaunchScreen.storyboard (ou usar flutter_native_splash — decisão na Fase 2).

Identidade visual básica (logo, cores, tipografia) — se o usuário ainda não tem, sugerir paleta coerente com o rumo-500 (Tailwind) já usado no web.

Favicon web — atualizar web/index.html + web/public/.

Fora do escopo da S42 (ficam pra S43): política de privacidade, build assinado, contas de dev, publicação nas lojas.

Alternativas (se a S42 quiser reduzir escopo)
OPÇÃO 5 reduzida — só o ícone (sem splash, sem logo). Não recomendado: o splash é o que mais pesa na primeira impressão e o custo é baixo.

OPÇÃO 6 (release prep pesado já) — pular a identidade e ir direto pra política + build assinado + contas. Não recomendado: a identidade visual trava a geração de screenshots da loja (S44), e sem ícone não dá pra submeter.

OPÇÃO 7 (features extras) — notificações, feed "quem você segue", comentários aninhados. Fora do MVP. Não recomendado.

Recomendação final: S42 = começo da OPÇÃO 4 (ícone + splash + paleta). S43 = release prep pesado (política + build assinado + contas + tile server). S44+ = publicação.

Ordem de entrega da S42 (proposta)
Fase 0 completa (6 blocos).

Fase 1 — descoberta: pedir web/index.html, web/public/ (Get-ChildItem), mobile/pubspec.yaml, mobile/android/app/src/main/AndroidManifest.xml, mobile/ios/Runner/Info.plist, mobile/android/app/src/main/res/ (Get-ChildItem -Recurse), mobile/ios/Runner/Assets.xcassets/ (Get-ChildItem -Recurse). Perguntar se o usuário já tem arte (logo, ícone, paleta) ou se quer que o assistente proponha.

Fase 2 — contrato travado: decidir paleta, formato do ícone (SVG? PNG? usar flutter_launcher_icons?), splash via flutter_native_splash ou XML nativo.

Fase 3 — entrega incremental (1 arquivo/config por vez).

Fase 3.5 — verificar save + commit.

Fase 4 — validação (rodar flutter build local? ou só flutter analyze + confirmar que os assets aparecem?).

Fase 5 — handoff + percentual.

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT
O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".

Na S23: "vamos deixar algumas coisas acordadas, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."

Na S24: confirmou "tudo como esperado" duas vezes.

S25–S40: reforçou os mesmos acordos. Tolerou tropeços (S21–S39: 1 a 8 tropeços por sessão; S40: 0; S41: 0).

Na S40, fez um pedido novo e explícito:

"vamos continuar, só estou com receio de ficar na mão pois fique ontem. [...] me mande o comando no powershell para eu mandar [...] tome cuidado para não esgotar o site ou chat para fazer o handoff e não ficar sem ter como abrir um novo chat, ou o site em outro dia."

Interpretação: handoff preventivo mais cedo (antes de 70–80%) por medo de corte silencioso. A S41 fechou em ~75% de contexto, sem necessidade de handoff preventivo (mas o assistente avisou proativamente em cada arquivo grande — S41a).

Na S41, o usuário reforçou (no início da sessão):

"ontem o chat acabou no meio do código, gostaria que você avisasse se caso isso for ocorrer, não estou falando apenas do limite do chat, mas sim o limite do site (IA)."

Interpretação: S41a — aviso proativo de interrupção iminente (chat OU site), antes de começar a entregar, não depois.

Acordos novos:

S31: percentual de prontidão anexo ao handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff.

S32: manter o processo S21–S31 (Fase 0 obrigatória na ordem S27b, Fase 1 descoberta, Fase 2 contrato, Fase 3 incremental, Fase 3.5 save+commit, Fase 4 validação, Fase 5 handoff+percentual).

S40: handoff preventivo em ~50–60% quando arquivos grandes em sequência (>250 linhas); ~70–80% normal (S40c).

S41: aviso proativo de interrupção iminente (S41a).

O que funcionou nas S21–S41 (manter):

Ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão).

Disposição de reduzir escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32–S41).

Consistência em aceitar os erros na hora e corrigir/registrar, sem contornar.

S41 acrescentou: Fase 0 completa, descoberta cirúrgica (8 itens, incluindo Get-ChildItem e package.json para confirmar que não havia modal genérico), contrato travou 3 decisões (modal à mão, useState sem RHF, botão ao lado do "Este é você."), entrega incremental 2/2 sem tropeço, validação manual no Chrome com 10 cenários, e aviso proativo S41a em cada arquivo grande.

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 41)
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
Faltando pro MVP: editar email/username (rotas próprias), editar birth_date (S42+), GET /users/{id}/is-following (opcional), notificações (pós-MVP)	—	⏳
Consolidado backend: ~95%. O que falta é opcional pro MVP.

Web — ~97% (subiu de ~94% na S40 com a paridade web fechada)
Item	%	Status
Feed	100%	✅
Perfil próprio (com stats + filtros + 4 charts + export em lote + editar perfil)	100%	✅ (S41)
Perfil de terceiro (com follow + abas Seguidores/Seguindo)	100%	✅
Detalhe de atividade (com mapa, comentários, like)	100%	✅
Upload (se houver — não confirmado nesta sessão)	?	❓
Busca (atividades + usuários)	100%	✅
Editar perfil (peso, altura, nome)	100%	✅ S41
Tile server próprio do OSM	0%	❌ S43+
Consolidado web: ~97%. O gap real agora é só o tile server próprio (S43+) e o upload (se ainda não existir — não verificado; a S41 não tocou nisso).

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
Testes em dispositivo físico (Android/iOS)	0%	❌ S42+
Paridade visual exata com o web	~90%	🟡
Refresh token / logout automático em 401	0%	❌ S42+
Consolidado mobile: ~93%. O gap real é testes em dispositivo físico + paridade visual exata + refresh token. S41 não tocou no mobile (paridade já fechada na S39).

Bloqueadores não-código — 0%
Item	%	Status
Ícone do app (mobile + favicon web)	0%	❌ S42
Identidade visual (logo, splash)	0%	❌ S42
Política de privacidade	0%	❌ S43
Build assinado (Android keystore + iOS provisioning)	0%	❌ S43
Conta Google Play Developer ($25)	0%	❌ S43
Conta Apple Developer ($99/ano)	0%	❌ S43
Publicação nas lojas	0%	❌ S44
Tile server próprio do OSM	0%	❌ S43+
Screenshots / descrição da loja	0%	❌ S44
Consolidado bloqueadores: 0%. É o maior gap pro lançamento. Nada disso é código, mas é obrigatório pra publicar.

Consolidado
Camada	%	Peso estimado	Contribuição
Backend	~95%	35%	33.3%
Web	~97%	20%	19.4%
Mobile	~93%	30%	27.9%
Bloqueadores não-código	0%	15%	0%
MVP consolidado	~80,6%	100%	~80,6%
Interpretação: o código está em ~95% (backend+web+mobile) — praticamente pronto. Os bloqueadores não-código (ícone, política, build assinado, lojas) estão em 0% e pesam 15% do MVP. Sem eles, não há lançamento. O consolidado subiu de ~80.0% (S40) para ~80.6% (S41) — a paridade web fechada compensou o backend/mobile estáveis.

Estimativa de sessões restantes
Sessão	Foco	Estimativa
S42	Começo da OPÇÃO 4 (ícone + splash + identidade visual)	1 sessão
S43	Release prep pesado (política de privacidade + build assinado + contas de dev + tile server próprio)	1–2 sessões
S44	Screenshots + descrição da loja + submissão Google Play (review ~1–3 dias)	1 sessão + review
S45	Submissão App Store (review ~1–7 dias) + correções de review	1 sessão + review
S46+	Pós-MVP (notificações, editar email/username, refresh token, paridade visual exata)	contínuo
Estimativa: ~3–4 sessões pra chegar em "pronto pra submeter" (S42–S43), +1–2 sessões de review das lojas (S44+). Total: ~5–6 sessões até o app estar publicado.