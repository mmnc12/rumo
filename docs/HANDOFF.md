SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro (S21–S42, inalterada)
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Toda informação chega por (a) Get-Content -Encoding UTF8 de um arquivo, ou (b) saída de comando de terminal. Nunca inventar caminho, nunca dizer "vou olhar X", nunca reescrever arquivo não recebido. Se precisar, pedir e esperar. Se a estrutura for necessária, pedir Get-ChildItem.

Regras críticas (S21–S42) — contrato de trabalho, não sugestão
Todas as S21–S41 mantidas. Adições da S42:

S42a (NOVA — validação de arquivo de scaffold antes do commit). O flutter create e o flutter_native_splash:create reescrevem arquivos que não são alvo (ex.: mobile/web/index.html, analysis_options.yaml). Sempre rodar git status --short + git diff <arquivo> antes de commitar arquivos que o comando de scaffold tocou. Na S42, o flutter_native_splash:create colapsou o HTML de mobile/web/index.html e comeu o <link rel="icon"> — foi restaurado com git restore + Remove-Item -Recurse do mobile/web/splash/ (S42p). Regra: commitar só o que o escopo pede; o que o scaffold tocou de colateral, restaurar.

S42b (NOVA — hash do index-*.js não muda com mudanças em index.html/public/). O index.html e os assets de public/ são copiados pro dist/ sem entrar no bundle JS. Mudanças nesses arquivos não alteram o hash do index-*.js. O sinal de "deploy novo no ar" é o conteúdo do index.html (meta tags novas, favicon novo) e o favicon servido, não o hash do JS. (S42o — evita falso alarme "o hash não mudou, o deploy não foi".)

S42c (NOVA — Invoke-WebRequest.Content é byte[] para application/manifest+json). No PS 5.1, -UseBasicParsing devolve Content como string para text/html, mas como byte[] para application/json/application/manifest+json (que é o Content-Type do Vercel para manifest.webmanifest). .Substring() quebra. Usar [System.Text.Encoding]::UTF8.GetString($resp.Content) se precisar do texto. Não é bug do Rumo; é comportamento do PS 5.1. (S42q.)

S42d (NOVA — flutter_launcher_icons não aceita SVG, só PNG). O image_path do config tem que apontar pra um PNG 1024×1024 (mínimo). SVG não funciona. No fluxo S42: web/public/logo.svg (master, texto, ~1.6 KB) → gerar logo1024.png (ferramenta externa: cloudconvert, Chrome, magick) → salvar em mobile/assets/icon/logo1024.png → config flutter_launcher_icons aponta pra ele. O logo1024.png também foi copiado pra web/public/ como fallback iOS antigo (hashes idênticos, S42 — verificado).

S42e (NOVA — flutter create --platforms=... respeita unmanaged_files do .metadata). O lib/main.dart não é tocado (o .metadata lista como unmanaged). Mas o flutter create cria test/widget_test.dart (template padrão) que referencia MyApp — se o lib/main.dart real não tem MyApp, o flutter analyze acusa erro. Fix: deletar test/widget_test.dart (template inútil). Idempotente.

S42f (NOVA — mobile sem scaffolds Android/iOS desde o início). O .metadata do mobile/ só listava web e windows. Não havia android/ nem ios/. Bloqueador real pra publicação nas lojas. Resolvido na S42 com flutter create --platforms=android,ios . (64 arquivos gerados). Lição: antes de planejar identidade visual nativa, checar se os scaffolds existem (Test-Path android, Test-Path ios).

S42g (NOVA — favicon existia mas não era referenciado). web/public/favicon.svg (9.5 KB, roxo/violeta, arte gerada por IA) existia no repo, mas o web/index.html apontava pra /vite.svg (genérico). Além disso, roxo ≠ laranja do app (rumo-500 = #f97316). Fix: favicon recriado em laranja (mantendo a forma de raio/energia), index.html corrigido. Lição: verificar se os assets de identidade que existem no repo estão referenciados (não só presentes).

S42h (NOVA — icons.svg é sprite de UI, não logo). web/public/icons.svg (5 KB) contém <symbol id="bluesky-icon"> — é sprite de ícones de redes sociais, não identidade. Não usar como favicon nem logo.

S42i (NOVA — pubspec.yaml com description: "A new Flutter project."). Placeholder genérico do template. Corrigido na S42 para descrição real do produto.

S42j (NOVA — pubspec.yaml sem flutter_launcher_icons/flutter_native_splash). Adicionados na S42 como dev_dependencies (^0.14.4 / ^2.4.6), resolvidos sem conflito com Dart 3.13.7.

S42k (NOVA — PWA sem PNGs no manifest). O manifest.webmanifest referencia /logo.svg como "src" (SVG cobre navegadores modernos; Lighthouse moderno aceita). logo192.png/logo512.png não foram gerados (não tenho ferramenta de SVG→PNG aqui; o usuário pode gerar quando quiser). Não é bloqueador. O apple-touch-icon aponta pra /logo.svg (iOS 16+ aceita; iOS < 16 cai no fallback favicon). web/public/logo1024.png existe como fallback.

S42l (NOVA — modal à mão sem lib, S41d, continua válido). O repo web não tem modal/dialog genérico. react-hook-form/zod instalados mas não usados. Modal novo à mão (<div> + useEffect para Esc/backdrop/foco/overflow:hidden). Consistência.

S42m (NOVA — flutter create reescreveu analysis_options.yaml). Adicionou exclusões de build/ e das pastas de plataforma na análise. Benéfico, não regressão. Commitar como está.

S42n (NOVA — index.html sem <link rel="manifest">). O manifest.webmanifest foi criado (arquivo 3/7) mas o index.html não o referenciava. Fix de 1 linha no passo 7.1 (S42n): + <link rel="manifest" href="/manifest.webmanifest" /> + apple-touch-icon trocado de /favicon.svg pra /logo.svg (fundo creme é melhor pra ícone de tela inicial).

S42o (NOVA — hash do index-*.js não muda nesta S42). Ver S42b.

S42p (NOVA — flutter_native_splash:create toca mobile/web/index.html). O comando gera splash web (CSS inline, <picture id="splash"> com light-*/dark-*, script de remoção) e colapsa o HTML (parser reformatou <!DOCTYPE html><html><head>, normalizou async="", removeu <link rel="icon">). Restaurado com git restore mobile/web/index.html + Remove-Item -Recurse -Force mobile\web\splash (o mobile/web não é usado em produção; o web real é o web/ React na Vercel). Lição: rodar flutter_native_splash:create em projeto com web/ sempre exige git status + git diff antes do commit (S42a). Se o mobile/web não for usado, git restore + remover splash/.

S42q (NOVA — Content byte[] pra manifest). Ver S42c.

S42r (NOVA — "tudo como esperado" sem output). O usuário às vezes responde "tudo como esperado" sem colar a saída completa. Não assumir verde — quando o comando é crítico (build, pytest, hash, git status), pedir a saída específica mesmo que o usuário já tenha dito "tudo certo". Na S42, o git status --short pós-restore veio completo e confirmou. Mas em caso de dúvida, pedir o output específico. Exceção: se a resposta anterior já mostrou o output completo e o usuário só confirma, aceitar a confirmação (não re-pedir).

Todas as regras S21–S41 permanecem válidas e não foram reincidentes na S42 (0 tropeços de código na entrega; 1 tropeço cosmético no script de validação, S42q — não-bug).

O que é LOCAL vs. PRODUÇÃO (inalterado)
LOCAL: D:\Rumo (repo), D:\Rumo\backend, D:\Rumo\web, D:\Rumo\mobile. Assistente não tem acesso.

PRODUÇÃO: backend Render (https://rumo-api-5s0b.onrender.com), web Vercel (https://rumo-wheat.vercel.app).

Fluxo: editar em D:\Rumo → pytest local (Docker 5433) → commit → push → Render + Vercel redeployam → validar HTTP em produção.

Mobile: roda em emulador/aparelho. Nesta S42, ganhou scaffolds Android/iOS (antes só web/windows).

Estrutura do repo (referência — conferir, não assumir)
text
D:\Rumo
├── backend/ (venv, Python 3.13.7, pytest, 180 testes)
│   └── (inalterado desde S39 — S40/S41/S42 não tocaram)
├── docs/HANDOFF.md
├── mobile/
│   ├── lib/ (inalterado na S42 — S39 foi a última a tocar)
│   ├── android/  ← NOVO S42 (scaffold completo + ícones + splash)
│   ├── ios/      ← NOVO S42 (scaffold completo + ícones + splash)
│   ├── web/      ← existia; flutter_native_splash tentou modificar, foi restaurado (S42p)
│   ├── windows/  (inalterado)
│   ├── assets/icon/logo1024.png  ← NOVO S42
│   ├── pubspec.yaml  ← EDITADO S42 (+deps +config +description)
│   ├── analysis_options.yaml  ← reescrito pelo flutter create (S42m)
│   └── test/widget_test.dart  ← DELETADO S42 (template quebrado)
├── web/src/ (inalterado na S42 — S41 foi a última a tocar)
├── web/public/
│   ├── favicon.svg  ← SUBSTITUÍDO S42 (laranja, era roxo)
│   ├── logo.svg     ← NOVO S42 (master 512×512, fundo creme)
│   ├── logo1024.png ← NOVO S42 (fallback iOS antigo)
│   ├── manifest.webmanifest  ← NOVO S42 (PWA)
│   └── icons.svg    (inalterado — sprite de UI, S42h)
├── web/index.html   ← EDITADO S42 (+favicon +manifest +theme-color +description)
└── README.md
Como rodar comandos Flutter (inalterado)
& "C:\Users\nasci\flutter\bin\flutter.bat" <comando> (Flutter 3.47.9 / Dart 3.13.7 em C:\Users\nasci\flutter).

Contas de teste (inalterado)
prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades, 34.081,56 m. Estado em 2026-11-17 (S42, Fase 0): weight_kg=null, height_cm=null, full_name="Prod User". Confirmado em 4 sessões seguidas (S39 registrou 80.0, S40 null, S41 null, S42 null). Encerrado como estado (não é bug de código).

Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod ↔ Prod2 bidirecional desde S37.

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422/405).

Acordos de trabalho (inalterados + S42)
SEMPRE seguir a recomendação do assistente (você reforçou na S42: "já falei, vamos fazer sempre o que você recomendar").

CÓDIGO COMPLETO ao atualizar arquivo (nunca diff parcial, nunca placeholder), trecho alterado marcado com // [Sessão N].

UMA versão por arquivo por resposta.

HANDOFF PREVENTIVO em ~50–60% quando entregando arquivos grandes em sequência (>250 linhas); ~70–80% no caso normal (S40c).

AVISO PROATIVO DE INTERRUPÇÃO IMINENTE (S41a) — antes de começar a entregar, não depois. Vale pro limite do chat e do site/IA.

PERCENTUAL DE PRONTIDÃO anexo ao handoff (Fase 5), quebrado por camada.

VALIDAÇÃO INCREMENTAL. Buildar antes de entregar o próximo arquivo.

VERIFICAR SAVE ANTES DE BUILD (S21).

NUNCA placeholder no código entregue (S21) nem em comando com here-string (S36g).

Não adivinhar nomes de símbolos (S21/S39b).

git status + git log antes de git restore (S21).

Invoke-WebRequest sempre com -UseBasicParsing (S22).

Validar openapi.json antes de acusar bug em rota nova (S22).

Validar bundle da Vercel baixando index-*.js (S23).

Vercel pode demorar >90s no primeiro deploy (S24).

Select-String -SimpleMatch não aceita | (S25a/S33a/S36d/S38b). Usar -Pattern "a|b".

Confirmar lines[-1] suspeito com Select-Object -Last N (S25b).

Exigir output do bloco de validação antes de pedir commit (S25c).

Teste definitivo do save: git hash-object ≠ git rev-parse HEAD:<path> + git status --short mostra M (S25d + S34a).

Entregar conteúdo de arquivo SEM cerca markdown envolvendo (S25e).

PS 5.1: Content de Invoke-WebRequest -UseBasicParsing é string para text/html, byte[] para JSON/manifest (S26a + S42q).

Validar GPX em prod por regex no Content (S26b).

Render free tier pode demorar >3 min (S26c).

Commitar o handoff pendente ANTES de qualquer outra coisa (S27a).

Ordem fixa da Fase 0: handoff → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde (S27b).

Antes de aceitar o escopo do handoff anterior, pedir TODOS os arquivos que o contrato toca (S28a).

Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada (S28b).

Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).

Vercel reescreve hash de chunk; sinal de "novo no ar" = hash mudou vs. sessão anterior (S29b — exceto para index-*.js quando só index.html/public/ mudaram, S42b).

Contar ocorrências reais antes de anunciar "esperado Nx" (S29c).

ESLint no-useless-assignment: let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).

Select-String "TODO" casa case-insensitive "Todos". Usar -CaseSensitive ou \bTODO\b (S30a).

Componente genérico com semântica oposta: prop booleana default-false, 4 casos (S30b).

Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + arquivos-chave antes de estimar (S30c).

Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink (S31a).

file_picker 13.x: API estática + length()/readAsBytes() (S31b).

Select-String do disco mostrando conteúdo antigo após save → WriteAllText no PowerShell (S31c, reforçada S36f).

Select-String -SimpleMatch 'class X' casa PREFIXOS (S32a/S32b).

"Esperado" de Select-String é SEMPRE piso ou faixa, nunca exato (S32c/S32d/S33b/S34b/S38a).

MatchCollection[-1] não funciona no PS 5.1. Usar $times[$times.Count - 1] (S36a).

Bundle minified: Select-String devolve a linha inteira. Usar [regex]::Matches (S36b).

Toque no ActivityCard: confirmar PRIMEIRO qual tela está aberta pela URL (S36c).

AutomaticKeepAliveClientMixin é @mustCallSuper — super.build obrigatório. Lint: // ignore_for_file: unnecessary_overrides (S36e).

Editor falhou em salvar → WriteAllText com o arquivo inteiro (S36f).

share_plus 13.x: SharePlus.instance.share(ShareParams(files: [XFile.fromData(...)])) (S37c).

Download no Chrome via share_plus dispara download no browser (S37d).

Import não usado por inferência de tipo → remover (S37e).

unnecessary_underscores (Dart 3.7+): (_, __) vira (_, _) (S37f).

^ de continuação do PowerShell não é confiável — usar backtick ou uma linha só (S38c).

"Esperado" de git diff --cached --stat é piso/faixa (S38d).

GoRouterState no go_router 18.x NÃO tem .context (S39a).

REGRA S21 vale pro arquivo que está sendo editado, não só pros novos (S39b).

Só git restore preserva o encoding do blob — git show HEAD:... > ... no PS 5.1 grava UTF-16 LE (S39c).

AuthContext do web ganhou setUser na S40 (S40a).

apiFetch do web já aceita method: "PUT" — não criar put() novo no client.ts (S40b).

Handoff preventivo em ~50–60% quando arquivos grandes em sequência (S40c).

S41a–S41d (vide handoff S41; válidas).

S42a–S42r (vide acima).

Processo que o usuário elogiou (manter)
Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação em produção) → Fase 5 (handoff + percentual).

SEÇÃO 1 — TL;DR para quem chega agora
Backend: 180 testes passando, 0 warnings. Inalterado desde S39. Todos os endpoints do MVP em produção.

Web: S42 fechou a identidade visual. Entregues:

web/public/favicon.svg — recriado em laranja (#f97316/#ea580c), era roxo/violeta. Forma de raio/energia mantida.

web/index.html — <link rel="icon"> de /vite.svg → /favicon.svg; +theme-color; +apple-touch-icon (/logo.svg); +manifest; +description.

web/public/logo.svg — master 512×512, fundo creme #fff7ed (iOS não gosta de PNG transparente).

web/public/logo1024.png — fallback iOS antigo (PNG 1024×1024, 49 KB).

web/public/manifest.webmanifest — PWA (name, short_name, theme_color, background_color, start_url, display: standalone, ícones SVG).

Mobile: S42 fechou scaffolds + identidade nativa. Entregues:

mobile/android/ — scaffold completo (antes não existia), 64 arquivos.

mobile/ios/ — scaffold completo (antes não existia), idem.

mobile/android/app/src/main/res/mipmap-*/launcher_icon.png — 5 densidades + launcher_icon.xml (adaptive icon v26).

mobile/ios/Runner/Assets.xcassets/AppIcon.appiconset/ — 21 PNGs (todos os tamanhos iOS).

mobile/android/app/src/main/res/drawable-*/splash.png + android12splash.png — splash Android por densidade.

mobile/ios/Runner/Base.lproj/LaunchScreen.storyboard + LaunchImage.imageset — splash iOS.

mobile/pubspec.yaml — +flutter_launcher_icons ^0.14.4, +flutter_native_splash ^2.4.6, +assets/icon/, +config dos dois; description corrigida (era "A new Flutter project.").

mobile/assets/icon/logo1024.png — PNG fonte (49 KB).

mobile/test/widget_test.dart — deletado (template quebrado).

mobile/.metadata — +android/ios na lista de plataformas.

mobile/analysis_options.yaml — reescrito pelo flutter create (exclui build/ e plataformas — S42m).

Bloqueadores não-código: ~5% agora (era 0%). O ícone e a identidade visual existem; o splash existe. O que falta: política de privacidade, build assinado, contas de dev, publicação nas lojas, screenshots, tile server próprio.

Próximo alvo: S43 — release prep pesado (política de privacidade + build assinado + contas de dev + tile server próprio). O handoff S41 recomendava "S43 = release prep". Mantido.

SEÇÃO 2 — PRODUÇÃO E AMBIENTE (inalterado)
Backend: https://rumo-api-5s0b.onrender.com

Docs Backend: https://rumo-api-5s0b.onrender.com/docs

Frontend Web: https://rumo-wheat.vercel.app

Repo local: D:\Rumo

Mobile: D:\Rumo\mobile (agora com android/ e ios/)

Web: D:\Rumo\web (scripts: dev, build, lint, preview)

Flutter: 3.47.9 / Dart 3.13.7 (em C:\Users\nasci\flutter)

Docker Desktop: 4.93.0 (engine 29.8.1, compose v5.5.1)

SO: Windows, PowerShell 5.1

Python: 3.13.7 (venv em D:\Rumo\backend\venv)

Venv backend: D:\Rumo\backend\venv

Deps web (inalteradas)
React 19, Vite 8, TypeScript 6, Tailwind 3.4 (rumo-500 = #f97316), react-router-dom 7, @tanstack/react-query 5, react-leaflet 5, recharts 3. Não usa @headlessui/radix/react-modal (S41d). react-hook-form/zod instalados mas não usados (S41).

Deps mobile (atualizadas na S42)
file_picker ^13.3.3, fl_chart ^1.1.0 (resolveu 1.3.1), go_router ^18.1.2, path_provider ^2.1.5, share_plus ^13.3.1, flutter_launcher_icons ^0.14.4 (novo S42), flutter_native_splash ^2.4.6 (novo S42). Package name: rumo_mobile.

Git (estado ao fim da Sessão 42 — working tree limpo)
text
aaeb7c4 (HEAD -> main, origin/main) feat(mobile): scaffolds android/ios + icone e splash nativo (Sessao 42)
8576d95 feat(web): identidade visual — favicon laranja + manifest PWA + index.html (Sessao 42)
9b9df95 docs: handoff da Sessao 41
6701560 feat(web): EditProfileModal + botao Editar perfil no ProfilePage (Sessao 41, 5/5)
fb77754 feat(web): PUT /users/me + setUser no AuthContext + useUpdateMe (Sessao 40, 3/5)
3deb4f8 docs: handoff da Sessao 40
git status --short vazio. HEAD == origin/main == aaeb7c4. Pendente: commit do handoff S42 (este arquivo) — primeira ação da S43 (S27a).

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 42
3.1 Fase 0 — validação de estado inicial (6/6 blocos verdes)
Handoff pendente: git status --short vazio; handoff S41 já commitado como 9b9df95 (S42b do handoff S41 já registrava: "handoff registra estado no momento em que foi escrito; o commit pode ter acontecido depois" — confirmado pela 2ª vez).

Log/status: HEAD == origin/main == 9b9df95. Working tree limpo.

Build/lint/analyze: npm run build verde (✓ built in 2.00s), lint vazio, flutter analyze No issues found!.

Docker + pytest + ruff: rumo_postgres_test Up (healthy) 5433, 180 passed in 47.42s, ruff check . limpo.

Prod backend: /auth/me → weight_kg=null height_cm=null full_name="Prod User". Confirmado pela 4ª sessão seguida (estado, não bug).

Prod frontend: index servido: /assets/index-tC5onOwK.js — diferente do handoff S41 (que registrou index-BRp7iIdJ na Fase 0 + hash novo na Fase 4). Deploy da S41 no ar (S41c).

3.2 Fase 1 — descoberta (8 itens pedidos, 5 entregues, 3 erros de caminho)
Entregues: tailwind.config.js (paleta rumo-500 = #f97316), web/index.html (/vite.svg genérico), web/public/ (favicon.svg roxo 9.5 KB + icons.svg sprite), pubspec.yaml (sem libs de ícone/splash, description genérica), .metadata (só web/windows).

Erros de caminho (S42f): mobile/android/app/src/main/AndroidManifest.xml não existe; mobile/android/app/src/main/res/ não existe; mobile/ios/Runner/Info.plist não existe; mobile/ios/Runner/Assets.xcassets/ não existe. Confirmado por Test-Path android → False, Test-Path ios → False, Test-Path windows → True, Test-Path web → True.

Achados que moldaram o contrato: S42f (sem scaffolds), S42g (favicon roxo não referenciado), S42h (icons.svg sprite), S42i (description), S42j (sem libs), S42k (PWA sem PNG).

3.3 Fase 2 — contrato travado (5 decisões)
Gerar scaffolds Android/iOS agora: SIM (flutter create --platforms=android,ios .).

Paleta: manter laranja (rumo-500); favicon recriado em laranja.

Ferramenta: flutter_launcher_icons + flutter_native_splash (declarativo).

Símbolo: A (raio/energia em laranja — mantém a forma do favicon atual).

Escopo S42: 10 itens (favicon + index.html + logos + manifest + pubspec + scaffolds + comandos + validação + commit).

Fora de escopo (S43+): política de privacidade, build assinado, contas de dev, publicação, screenshots, tile server próprio, PNGs logo192/logo512 (S42k).

3.4 Fase 3 — entrega incremental (7 arquivos, todos verdes)
#	Arquivo	Validação
1/7	web/public/favicon.svg (laranja, 1618 bytes)	Last 3 linhas ok, Length 1618 ✅
2/7	web/index.html (favicon + theme-color + description)	build 1.18 kB ✅
3a/7	web/public/logo.svg (512×512, fundo creme)	✅
3b/7	web/public/manifest.webmanifest (PWA)	ConvertFrom-Json ok, build ✅
4/7	mobile/pubspec.yaml (description + 2 dev_deps)	flutter pub get ok, analyze limpo ✅
5a	flutter create --platforms=android,ios . (64 arquivos)	Test-Path android True, Test-Path ios True ✅
5a-fix	Deletar test/widget_test.dart (template quebrado)	analyze limpo ✅
5b	PNG logo1024.png (49 KB, gerado por você)	Length 49989 ✅
6/7	mobile/pubspec.yaml (config ícone+splash) + geração	5 mipmaps, 21 PNGs iOS, LaunchScreen.storyboard ✅
7/7	Validação final + 2 commits + push + Fase 4	✅
Achados durante a entrega: S42n (index.html sem <link rel="manifest"> — fix no 7.1), S42p (flutter_native_splash:create tocou mobile/web/index.html — restaurado), S42q (Content byte[] no PS 5.1).

3.5 Fase 3.5 — verificar save + commits
Save verificado em todos os 7 arquivos.

Commit 1 (web): 8576d95 — 5 arquivos, +73/−2. web/index.html, web/public/favicon.svg, web/public/logo.svg, web/public/logo1024.png, web/public/manifest.webmanifest.

Commit 2 (mobile): aaeb7c4 — 103 arquivos, +1533/−20. Scaffolds android/ + ios/, assets/icon/logo1024.png, pubspec.yaml, pubspec.lock, .metadata, analysis_options.yaml.

Push: 9b9df95..aaeb7c4 main -> main (142 objetos, 314.78 KiB). HEAD == origin/main == aaeb7c4. Working tree limpo.

3.6 Fase 4 — validação em produção (verde)
index.html servido: 6 matches (favicon, apple-touch, manifest ×3, theme-color).

favicon.svg: OK: favicon laranja no ar + OK: roxo removido.

manifest.webmanifest: 200 (S42q: .Substring deu erro cosmético por Content ser byte[]; não-bug).

logo.svg: 200 + tem #fff7ed.

index-*.js: hash tC5onOwK — igual ao da Fase 0, exatamente como previsto (S42b/S42o): mudanças em index.html/public/ não afetam o hash do index-*.js.

3.7 Tropeços da S42
0 tropeços de código. Os 7 arquivos entregues passaram de primeira.

1 tropeço cosmético no script de validação (S42q): .Substring em Content byte[] do manifest.webmanifest. Não-bug; PS 5.1.

1 surpresa durante o commit (S42p): flutter_native_splash:create tocou mobile/web/index.html + criou mobile/web/splash/. Restaurado com git restore + Remove-Item. S42a (nova regra): git status + git diff antes de commitar arquivos de scaffold.

1 falso alarme evitado (S42o): hash do index-*.js igual ao da Fase 0 não significa "deploy não foi" — significa "só index.html/public/ mudaram". Sinal de deploy é o conteúdo do index.html + favicon.

3.8 Resultado da suíte (S42)
pytest -q → 180 passed (mesmo número desde S39 — S42 não tocou no backend).

ruff check . → All checks passed!

npm run build → ✓ built in 1.60s (Fase 3.5) / 2.00s (Fase 0).

npm run lint → limpo.

flutter analyze → No issues found!

Validação em produção (Vercel) → favicon laranja no ar, roxo removido, manifest 200, logo.svg 200.

3.9 Commits pushados (S42)
aaeb7c4 feat(mobile): scaffolds android/ios + icone e splash nativo (Sessao 42)

8576d95 feat(web): identidade visual — favicon laranja + manifest PWA + index.html (Sessao 42)

9b9df95 docs: handoff da Sessao 41 (já estava — S42b)

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES (INALTERADOS)
Contratos S1–S40 inalterados. Repetidos do handoff S41 por completude (backend não foi tocado na S42):

Auth: POST /auth/login (form-urlencoded), GET /auth/me (Bearer, "quem sou eu").

Perfil próprio: PUT /users/me (Bearer, {weight_kg?, height_cm?, full_name?}, semântica exclude_unset — ausente não toca, null limpa, valor atualiza; extra="forbid"; rota antes de /{user_id}).

Atividades: GET /activities (filtro, self ou seguido), GET /activities/{id}, GET /activities/{id}/track (LineString), GET /activities/search?q=, POST /activities/upload (multipart), GET /activities/{id}/export?format=csv|gpx, GET /activities/export?format=csv|gpx[&from][&to] (ZIP).

Feed: GET /feed (FeedItemResponse com author (web) e user (mobile), S36).

Comentários: GET/POST /activities/{id}/comments, DELETE /comments/{id}.

Stats: GET /activities/stats/summary, /weekly, /monthly, /by-type; GET /users/{user_id}/stats/{...} (self ou seguido → 200, senão 403/404).

Follows: POST/DELETE /users/{user_id}/follow (204, idempotente), GET /users/{user_id}/followers, /following, GET /users/search?q= (rate limit 20/min).

⚡ Não existe GET /users/{id}/is-following — cliente infere via /users/{meId}/following.

⚡ UserPublic = 4 campos (id, username, full_name, is_active). Sem email/avatar. Para self, GET /auth/me.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Sessões 9–42 commitadas e pushadas. HEAD == origin/main == aaeb7c4. Working tree limpo.

Primeira ação da Sessão 43 (REGRA S27a — handoff primeiro):

powershell
cd D:\Rumo
git status --short
# Se M docs/HANDOFF.md (este arquivo):
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 42"
git push
Estado esperado da S43 ao abrir: HEAD == origin/main == aaeb7c4 (ou o commit do handoff S42 se já commitado). git status --short com M docs/HANDOFF.md (se ainda não commitado). Zero arquivos de código pendentes — S42 fechou 7/7 e as surpresas foram resolvidas.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell, atualizado S42)
Fase 0 — sanidade de build
powershell
cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
Fase 0 — Docker + pytest
powershell
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check . 
Fase 0 — Prod backend
powershell
$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
Write-Host "weight_kg=$($me.weight_kg) height_cm=$($me.height_cm) full_name=$($me.full_name)"
Fase 0 / Fase 4 — Prod frontend (Vercel, S42 atualizado)
powershell
$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
Write-Host "index JS: $($m.Groups[1].Value)"
[regex]::Matches($html.Content, 'favicon|theme-color|manifest|apple-touch') | ForEach-Object { Write-Host $_.Value }
# Favicon laranja?
$fav = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app/favicon.svg" -UseBasicParsing
if ($fav.Content -match '#f97316') { Write-Host "OK: favicon laranja" } else { Write-Host "FALHA" }
if ($fav.Content -match '#863bff') { Write-Host "ATENCAO: roxo antigo" } else { Write-Host "OK: roxo removido" }
# manifest (S42q: Content byte[], usar GetString)
$man = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app/manifest.webmanifest" -UseBasicParsing
$manText = [System.Text.Encoding]::UTF8.GetString($man.Content)
Write-Host "manifest: $($man.StatusCode) | 80 chars: $($manText.Substring(0,80))"
Diagnóstico de save (S25 + S42)
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
Write-Host "=== [6] hash do HEAD (path relativo a RAIZ) ==="
git rev-parse HEAD:<path/relativo/a/raiz>
# [5] ≠ [6] e [4] com M → save pegou, pode commitar.
Contornar editor que não salva (S31c + S36f)
powershell
cd D:\Rumo\web
$content = @'
// [Sessão N] conteúdo completo do arquivo (SEM PLACEHOLDER — S36g/S39c)
'@
[System.IO.File]::WriteAllText("D:\Rumo\web\src\components\X.tsx", $content, [System.Text.UTF8Encoding]::new($false))
Commits (S38c — sem ^)
powershell
git add arquivo1 arquivo2 arquivo3
# ou com backtick:
git add arquivo1 `
        arquivo2 `
        arquivo3
git restore + remover pasta órfã (S42p)
powershell
git restore mobile/web/index.html
Remove-Item -Recurse -Force mobile\web\splash
git status --short mobile/web/  # deve vir vazio
apiFetch do web (S40b — inalterado)
ts
return apiFetch<UserResponse>("/users/me", { method: "PUT", body: payload });
useMutation + invalidateQueries (S40 — inalterado)
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
Config flutter_launcher_icons + flutter_native_splash (S42)
yaml
flutter_launcher_icons:
  android: "launcher_icon"
  ios: true
  image_path: "assets/icon/logo1024.png"
  min_sdk_android: 21
  remove_alpha_ios: true
  adaptive_icon_background: "#fff7ed"
  adaptive_icon_foreground: "assets/icon/logo1024.png"

flutter_native_splash:
  color: "#fff7ed"
  image: assets/icon/logo1024.png
  android: true
  ios: true
  android_12:
    color: "#fff7ed"
    image: assets/icon/logo1024.png
SEÇÃO 7 — DÍVIDAS TÉCNICAS (S42)
Fechadas
(S1–S41) todas continuam fechadas.

(S40) Web sem editor de perfil — FECHADO S41.

(S40) AuthContext sem setUser — FECHADO S40.

(S41) Paridade web do "Editar perfil" — FECHADO S41.

(S42f) Mobile sem scaffolds Android/iOS — FECHADO S42.

(S42g) Favicon roxo não referenciado — FECHADO S42.

(S42i) Description genérica — FECHADO S42.

(S42j) Sem libs de ícone/splash — FECHADO S42.

(S42n) index.html sem <link rel="manifest"> — FECHADO S42.

Conhecidas (não-bug)
(S41) Estado do prod@rumo.com: weight_kg=null height_cm=null full_name="Prod User" — 4 sessões confirmando (S39 registrou 80.0, S40/S41/S42 null). Encerrado como estado.

(S41) EditProfileModal.tsx bundlado dentro do ProfilePage-*.js — comportamento esperado do code-splitting. Não é bug.

(S41) EditProfileModal usa useState + validação derivada — consistente com o repo. Não usar react-hook-form/zod.

(S41) formatNumber duplicado entre EditProfileModal.tsx (TS) e edit_profile_page.dart (Dart) — stacks diferentes. Aceitável.

(S41) EditProfileModal recebe current via prop — desacoplamento. Decisão.

(S41) Botão "Editar perfil" só com user && isSelf — boot antes do /auth/me. Aceitável (isLoading cobre).

(S41) Modal sem "Limpar" no full_name — apagar + salvar → null. Paridade mobile.

(S41) Modal sem "Desfazer" global — só por campo. Mesma decisão mobile.

(S41) Apagar texto do peso/altura sem "Limpar" e salvar NÃO manda null — campo intocado/igual fica ausente. Paridade mobile.

(S41) ProfilePage.tsx não exibe weight_kg/height_cm no header — só no modal.

(S41) birth_date fora do escopo — backend não aceita. S43+.

(S41) email/username fora do escopo — rotas próprias. S43+.

(S42k) PWA sem PNGs no manifest — SVG cobre navegadores modernos. Lighthouse moderno aceita. Não é bloqueador.

(S42m) analysis_options.yaml reescrito pelo flutter create — exclui build/ e plataformas. Benéfico. Commitar como está.

(S42o) Hash do index-*.js não muda com index.html/public/ — não é sinal de "deploy não foi". Sinal é o conteúdo do index.html + favicon.

(S42p) flutter_native_splash:create tocou mobile/web/index.html — restaurado. O mobile/web não é usado em produção (web real é o React na Vercel).

(S42q) Content byte[] no PS 5.1 para manifest — comportamento do PS, não-bug do Rumo.

(S42 — novo) mobile/android/ e mobile/ios/ gerados pelo flutter create — os MainActivity.kt e AppDelegate.swift são template padrão. Não foram personalizados (nome do app = rumo_mobile, package = com.example.rumo_mobile). Trocar com.example.rumo_mobile pelo package real antes da publicação nas lojas (S43+) — Google Play rejeita com.example.*.

Oportunidades
(S1–S41) todas continuam.

(S42) Gerar logo192.png + logo512.png — S43+. Ferramenta: cloudconvert (SVG→PNG). Não-bloqueador.

(S42) Trocar com.example.rumo_mobile pelo package real (ex: com.rumo.app) antes da publicação. Bloqueador de loja. S43.

(S42) Personalizar MainActivity.kt — hoje é template (class MainActivity: FlutterActivity()). Funciona, mas S43 pode querer customizar.

(S42) Adicionar ícone adaptativo monochrome para Android 13+ (themed icons) — S43+. O launcher_icon.xml atual tem foreground + background, falta monochrome. Não-bloqueador.

(S43) Política de privacidade — obrigatória nas lojas. 0% hoje.

(S43) Build assinado (Android keystore + iOS provisioning) — 0% hoje.

(S43) Contas Google Play Developer ($25) + Apple Developer ($99/ano) — 0% hoje.

(S43+) Tile server próprio do OSM — 0% hoje. Hoje usa tile.openstreetmap.org público (rate limit).

(S43) Screenshots + descrição da loja — 0% hoje.

(S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S43+.

(S34) Endpoint GET /users/{id}/is-following no backend — S43+.

(S36) Deep-link ?q= na busca mobile — S43+.

(S36) Extrair debounce manual (Timer 300ms) — S43+.

(S36) Tile server próprio do OSM — S43+.

(S37) Botão de export unitário no web ActivityDetailPage.tsx — S43+.

(S38) Filtros de activity_type na UI do perfil — S43+.

(S38) Testar StatsChart em Android/iOS físico — S43+.

(S39) Editar birth_date — S43+.

(S39) Editar email/username — S43+.

(S39) Trocar extra do /edit-profile por GET /auth/me dentro da própria EditProfilePage — S43+.

(S39) Testar EditProfilePage em Android/iOS físico — S43+.

(S40) Exibir weight_kg/height_cm no header do ProfilePage — S43+ se o produto pedir.

(S41) Identidade visual — FECHADO S42 (ícone + splash + paleta).

(S42) Testar o app mobile em emulador Android / simulador iOS — NUNCA foi feito (não havia scaffold antes). Prioridade S43 — antes de qualquer release prep, precisa confirmar que o app roda nos scaffolds novos.

(S42) Testar splash screen no emulador — S43.

(S42) Testar ícone no launcher do Android/iOS — S43.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 43 e além)
Sessão 42 fechada em 7/7 + validada em produção
A S42 fechou o bloqueador não-código de identidade visual (0% → 5%). O código do MVP está em ~95%. O que falta agora é release prep pesado.

Primeira ação obrigatória da Sessão 43 (REGRA S27a)
cd D:\Rumo; git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 42, push, confirmar HEAD == origin/main.

Fase 0 completa (REGRA S27b) — a S43 deve rodar
Handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend (com o script S42 atualizado, seção 6).

Rota recomendada para a Sessão 43
S43 = release prep pesado. Escopo proposto (a travar com você na Fase 1):

Trocar com.example.rumo_mobile pelo package real (com.rumo.app ou similar) — bloqueador de loja. Afeta android/app/build.gradle.kts, AndroidManifest.xml, MainActivity.kt, ios/Runner.xcodeproj.

Política de privacidade — criar web/src/pages/PrivacyPage.tsx + link no rodapé + URL pública (https://rumo-wheat.vercel.app/privacy). Obrigatória pra Google Play e App Store.

Build assinado Android — gerar keystore (keytool -genkey), configurar android/app/build.gradle.kts (signingConfigs), guardar keystore no .gitignore (nunca commitar).

Build assinado iOS — provisioning profile, certificado (precisa de conta Apple Developer paga).

Contas de dev — Google Play Developer ($25 uma vez), Apple Developer ($99/ano). Você precisa criar; eu não posso.

Testar o app no emulador Android — o scaffold existe, mas o app nunca rodou nele. flutter run -d <emulator> + validar login, feed, perfil, upload. Prioridade máxima — antes de qualquer release prep, confirmar que roda.

(Se der tempo) Tile server próprio do OSM — decisão S43/S44.

Fora do escopo da S43 (S44+): screenshots + descrição da loja, submissão Google Play, submissão App Store, correções de review.

Alternativas (se a S43 quiser reduzir escopo)
OPÇÃO 5 reduzida — só o teste no emulador Android (item 6) + trocar package (item 1). Rápido, destrava o "o app roda?" que nunca foi respondido.

OPÇÃO 6 — ir direto pra política + contas (itens 2, 5), deixando build assinado pra S44. Não recomendado: sem testar no emulador, o build assinado pode falhar por motivos que você não viu.

Recomendação final: S43 = teste no emulador (6) + trocar package (1) + política (2) + contas (5). Build assinado (3, 4) e tile server (7) em S44. Screenshots + submissão em S45/S46.

Ordem de entrega da S43 (proposta)
Fase 0 completa (6 blocos).

Fase 1 — descoberta: pedir mobile/android/app/build.gradle.kts, mobile/android/app/src/main/AndroidManifest.xml, mobile/android/app/src/main/kotlin/com/example/rumo_mobile/MainActivity.kt, mobile/ios/Runner.xcodeproj/project.pbxproj (só as partes relevantes), web/src/App.tsx (rotas), web/src/components/AppHeader.tsx (footer/link), web/src/pages/ (Get-ChildItem).

Fase 2 — contrato travado: package name (com.rumo.app? br.com.rumo? decidir), texto da política de privacidade, URL da política, ordem dos passos.

Fase 3 — entrega incremental (1 arquivo por vez).

Fase 3.5 — verificar save + commit.

Fase 4 — validação (rodar flutter run no emulador, validar login/feed/perfil).

Fase 5 — handoff + percentual.

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S42)
S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido [...] faça um handoff bem detalhado [...] e se tiver como pedir para que sempre trabalhe desta forma."

S22: "sempre vamos seguir o que você recomendar."

S23: "sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado [...] quando o limite estiver próximo do limite de 70% a 80%."

S24: confirmou "tudo como esperado" 2×.

S25–S40: reforçou os mesmos acordos. Tolerou tropeços (S21–S39: 1–8 por sessão; S40: 0; S41: 0; S42: 0 de código).

S40: "estou com receio de ficar na mão pois fique ontem. [...] me mande o comando no powershell [...] tome cuidado para não esgotar o site ou chat para fazer o handoff."

S41: "ontem o chat acabou no meio do código, gostaria que você avisasse se caso isso for ocorrer, não estou falando apenas do limite do chat, mas sim o limite do site (IA)."

S42: "já falei, vamos fazer sempre o que você recomendar." (reforço explícito, no início da S42, antes de qualquer decisão).

Acordos novos da S42: S42a–S42r (vide Seção 0).

O que funcionou na S42 (manter):

Fase 0 completa, 6/6 verdes.

Descoberta que encontrou 3 erros de caminho (S42f) — não assumiu que android/ existia.

Contrato travado com 5 decisões (incluindo a não-óbvia: gerar scaffolds, que não estava no handoff S41).

Entrega incremental 7/7 sem tropeço de código.

Validação em produção antes do handoff.

Auto-correção durante a entrega: S42n (faltava <link rel="manifest">), S42p (restaurar mobile/web/index.html).

Honestidade sobre limite: S42k (não consigo gerar PNG a partir de SVG aqui) e S42q (.Substring em byte[]).

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 42)
Backend — ~95% (inalterado desde S39)
Item	%	Status
Auth, perfil próprio, atividades, feed, comentários, upload, stats, follows, export, testes	100%	✅
Ruff (0 warnings)	100%	✅
Faltando pro MVP: editar email/username (rotas próprias), editar birth_date, GET /users/{id}/is-following (opcional), notificações (pós-MVP)	—	⏳
Consolidado backend: ~95%. O que falta é opcional pro MVP.

Web — ~97% (inalterado desde S41; S42 adicionou identidade mas não features)
Item	%	Status
Feed, perfil (próprio + terceiro), detalhe, busca, editar perfil, stats	100%	✅
Identidade visual (favicon + manifest + theme-color + logo.svg)	100%	✅ S42
Upload (se houver — não confirmado)	?	❓
Tile server próprio do OSM	0%	❌ S43+
Consolidado web: ~97%. O gap real é o tile server próprio (S43+) e upload (não verificado).

Mobile — ~93% (S42 adicionou scaffolds + identidade, mas não testou em emulador)
Item	%	Status
Feed, perfil, detalhe, upload, busca, editar perfil, stats, export	100%	✅
Scaffolds Android/iOS	100%	✅ S42
Ícone + splash nativo	100%	✅ S42
Teste em emulador Android / simulador iOS	0%	❌ S43 (prioridade)
Paridade visual exata com o web	~90%	🟡
Refresh token / logout automático em 401	0%	❌ S43+
Consolidado mobile: ~93%. O gap real agora é testar em dispositivo físico/emulador (nunca foi feito — antes não havia scaffold) + paridade visual exata + refresh token.

Bloqueadores não-código — ~5% (subiu de 0% na S42)
Item	%	Status
Ícone do app (mobile + favicon web)	100%	✅ S42
Identidade visual (logo, splash)	100%	✅ S42
Política de privacidade	0%	❌ S43
Build assinado (Android keystore + iOS provisioning)	0%	❌ S43
Conta Google Play Developer ($25)	0%	❌ S43
Conta Apple Developer ($99/ano)	0%	❌ S43
Trocar com.example.rumo_mobile pelo package real	0%	❌ S43 (bloqueador de loja)
Publicação nas lojas	0%	❌ S45
Tile server próprio do OSM	0%	❌ S44+
Screenshots / descrição da loja	0%	❌ S45
Consolidado bloqueadores: ~5%. O maior gap pro lançamento continua sendo não-código, mas a S42 moveu de 0% pra 5% (identidade visual pronta).

Consolidado
Camada	%	Peso estimado	Contribuição
Backend	~95%	35%	33.3%
Web	~97%	20%	19.4%
Mobile	~93%	30%	27.9%
Bloqueadores não-código	~5%	15%	0.75%
MVP consolidado	~81,3%	100%	~81,3%
Interpretação: subiu de ~80,6% (S41) para ~81,3% (S42) — a identidade visual (ícone + splash + favicon + manifest + paleta) compensou o backend/mobile estáveis. O código está em ~95%; os bloqueadores não-código estão em ~5% (identidade pronta, mas política/build/contas/lojas não). Sem eles, não há lançamento.

Estimativa de sessões restantes
Sessão	Foco	Estimativa
S43	Teste no emulador + trocar package + política + contas de dev	1 sessão
S44	Build assinado (Android keystore + iOS provisioning) + tile server próprio	1–2 sessões
S45	Screenshots + descrição da loja + submissão Google Play (review ~1–3 dias)	1 sessão + review
S46	Submissão App Store (review ~1–7 dias) + correções de review	1 sessão + review
S47+	Pós-MVP (notificações, editar email/username, refresh token, paridade visual exata)	contínuo
Estimativa: ~3–4 sessões pra chegar em "pronto pra submeter" (S43–S44), +1–2 sessões de review das lojas (S45+). Total: ~5–6 sessões até o app estar publicado (mesma estimativa do handoff S41 — a S42 não mudou o número, só moveu a identidade de 0% pra 100%).