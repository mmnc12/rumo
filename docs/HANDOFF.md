HANDOFF — SESSÃO 44
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro (S21–S44, inalterada): você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho, nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

Regras críticas S21–S43 mantidas integralmente. Adições da S44:

S44a (NOVA — bloqueador AGP 9 + Flutter 3.47.9). O build Android NÃO compila. O projeto está em AGP 9.0.0 com android.newDsl=false + android.builtInKotlin=false (modo de compatibilidade). O Flutter Gradle Plugin falha ao aplicar no subprojeto :app com: Cannot add task 'generateLockfiles' as a task with that name already exists. A tarefa generateLockfiles já é registrada no projeto raiz; o plugin do Flutter tenta registrá-la de novo no :app e o Gradle rejeita. O flag --android-skip-build-dependency-validation NÃO resolve (o erro é de conflito de task, não de validação de versão). O flutter clean também não resolve. É incompatibilidade real entre Flutter 3.47.9 e AGP 9.

S44b (NOVA — tentativa de rebaixar AGP para 8.7.3 falhou). A S44 tentou AGP 8.7.3 (seguindo sugestão de "voltar para AGP 8"). Resultado: o Flutter 3.47.9 rejeita — exige AGP >= 8.11.1. Ou seja, a janela útil de AGP é [8.11.1, 9.0.0], mas o Flutter 3.47.9 ainda tem bug com AGP 9.0.0 (S44a). A faixa 8.11.1–8.13.x é a única teoricamente segura, mas NÃO foi testada na S44.

S44c (NOVA — app NUNCA rodou nos scaffolds novos). O item 7 do mapa (testar no emulador Android) continua 0%. O app compilou em sessões anteriores? Não há evidência. O primeiro flutter run real foi na S44 e falhou no Gradle. O emulador emulador1 (Android 16, API 36) está funcionando e o Flutter o enxerga (emulator-5554). O problema é 100% build, não device.

S44d (NOVA — edições feitas no app/build.gradle.kts na S44, precisam ser revisadas). Durante a S44, o usuário editou mobile/android/app/build.gradle.kts várias vezes (a pedido do assistente). Estado atual conhecido:
- plugins { } contém id("com.android.application"), id("kotlin-android"), id("dev.flutter.flutter-gradle-plugin") (a linha kotlin-android foi adicionada)
- O bloco kotlin { compilerOptions { jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17 } } foi mantido no final (formato "oficial Flutter" para AGP 9 + builtInKotlin=false)
- android/build.gradle.kts (nível superior) também recebeu id("kotlin-android") no plugins { } — isso pode ser redundante ou prejudicial (S44e)
- gradle.properties tem android.newDsl=false e android.builtInKotlin=false
NÃO há backup do estado anterior. A próxima sessão deve inspecionar o arquivo real antes de mexer (regra de ouro).

S44e (NOVA — id("kotlin-android") no android/build.gradle.kts de nível superior é suspeito). O arquivo de nível superior (android/build.gradle.kts) NÃO é o app/build.gradle.kts. Adicionar kotlin-android lá pode aplicar o KGP a todos os subprojetos, incluindo :app, e é possível que isso contribua para o conflito de generateLockfiles. A próxima sessão deve considerar remover essa linha do arquivo de nível superior (mas só depois de inspecionar).

S44f (NOVA — rota de correção recomendada para S45). A rota mais promissora, não testada na S44, é: rebaixar AGP para 8.13.0 (ou 8.11.1, mínimo do Flutter) em settings.gradle.kts, REMOVER android.newDsl=false e android.builtInKotlin=false do gradle.properties (essas flags são só para AGP 9), e reverter o app/build.gradle.kts para o formato AGP 8 (kotlinOptions dentro de android { }, sem bloco kotlin { } externo). Se isso falhar, a alternativa é atualizar o Flutter para uma versão que suporte AGP 9 (Flutter 3.48+? verificar release notes) ou usar --android-skip-build-dependency-validation (que já falhou na S44).

S44g (NOVA — limite de site respeitado). A S44 parou o build no meio da batalha AGP e fez o handoff antes de esgotar o site, conforme pedido do usuário (S40, S41). O usuário pediu explicitamente "vamos fazer o handoff completo, pois quem sabe se no outro chat resolvemos". A S45 deve começar pela rota S44f, não por tentativas aleatórias.

SEÇÃO 1 — TL;DR para quem chega agora
Estado do repo: HEAD == origin/main == 0ce5626 (handoff S43). Working tree deve estar limpo exceto pelas edições da S44 em mobile/android/ (ver S44d) e este handoff.

S44 feita nesta sessão:
- Fase 0 completa: 6/6 verdes (web build/lint, mobile analyze, backend pytest 180, ruff)
- Emulador Android: emulador1 (Android 16, API 36) rodando, Flutter enxerga emulator-5554
- flutter doctor: licenças Android aceitas (All SDK package licenses accepted)
- flutter run: FALHOU. Bloqueador AGP 9 + Flutter 3.47.9 (S44a). 3 tentativas, 3 erros diferentes:
  1. AGP 9.0.0 original: Unresolved reference 'compilerOptions' (bloco kotlin { } não reconhecido)
  2. AGP 8.7.3: Flutter exige >= 8.11.1 (S44b)
  3. AGP 9.0.0 + kotlin-android no app + flags: Cannot add task 'generateLockfiles' (S44a)
- 0 arquivos de código entregues com sucesso. 3 arquivos tocados (app/build.gradle.kts, android/build.gradle.kts, gradle.properties) em estado incerto (S44d).

O que falta (7–13): teste no emulador (item 7, bloqueado por S44a), keystore (10), contas (12), higiene de BOM (13). Tudo depende de resolver S44a primeiro.

Percentual consolidado: caiu de ~85,6% (S43) para ~82–83% (S44). O código não mudou, mas o item 7 (teste no emulador) provou-se bloqueado por incompatibilidade de toolchain, o que reduz a confiança no "mobile ~96%".

SEÇÃO 2 — PRODUÇÃO E AMBIENTE (inalterado)
Backend: https://rumo-api-5s0b.onrender.com
Frontend Web: https://rumo-wheat.vercel.app
Repo local: D:\Rumo
Flutter: 3.47.9 / Dart 3.13.7 (C:\Users\nasci\flutter)
SO: Windows 11 (26H2), PowerShell 5.1
Python: 3.13.7 (venv em D:\Rumo\backend\venv)
Android SDK: C:\Users\nasci\AppData\Local\Android\Sdk (SDK 36.0.0)
Android Studio: C:\Program Files\Android\Android Studio\bin\studio64.exe
Emulador: emulador1 (Android 16, API 36, x86_64) — rodando, emulator-5554
AVDs disponíveis: emulador1, meuEmulador

Git ao fim da S44 (esperado):
0ce5626 (HEAD -> main, origin/main) docs: handoff da Sessao 43
2e09068 feat(mobile): package br.com.rumo.app + label Rumo + iOS bundle id (Sessao 43, 6/13)
deb7969 feat(web): politica de privacidade (/privacy) + link no AppHeader (Sessao 43, 3/13)
3fb3c5e docs: handoff da Sessao 42
aaeb7c4 feat(mobile): scaffolds android/ios + icone e splash nativo (Sessao 42)
8576d95 feat(web): identidade visual — favicon laranja + manifest PWA + index.html (Sessao 42)

git status --short --untracked-files=all ao fim da S44: deve mostrar M em mobile/android/app/build.gradle.kts, mobile/android/build.gradle.kts, mobile/android/gradle.properties (edições da S44, S44d) + M docs/HANDOFF.md. NADA disso foi commitado na S44 — a próxima sessão decide se commita como "wip: tentativa AGP" ou reverte.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 44
3.1 Fase 0 — validação (6/6 verdes)
git: HEAD == origin/main == 0ce5626, working tree limpo
web build: 826 modules, built in 2.08s (index-BizVMh0m.js)
web lint: OK (silencioso)
mobile analyze: No issues found! (ran in 4.2s)
backend pytest: 180 passed in 50.49s
backend ruff: All checks passed!
Observação: hash do index-*.js mudou vs. S43 (index-CPP87bow.js -> index-BizVMh0m.js). Deploy Vercel saudável (S42o). Não é problema.

3.2 Emulador Android — preparação (itens 1–4 da Seção 8 do handoff S43)
flutter emulators: 2 AVDs (emulador1, meuEmulador)
flutter devices: 3 devices (Windows, Chrome, Edge) — sem emulador rodando
Android Studio: instalado
SDK: C:\Users\nasci\AppData\Local\Android\Sdk
flutter doctor: [!] Android toolchain — Some Android licenses not accepted
Ação: flutter doctor --android-licenses -> All SDK package licenses accepted
emulador1 iniciado: flutter emulators --launch emulador1
flutter devices: sdk gphone64 x86 64 (mobile) • emulator-5554 • android-x64 • Android 16 (API 36) (emulator)
Ou seja: emulador OK, Flutter enxerga. O problema é só build.

3.3 flutter run — 3 tentativas, 3 falhas (S44a/b)
Tentativa 1 (AGP 9.0.0 original, app/build.gradle.kts com bloco kotlin { compilerOptions { } }):
  Erro: Unresolved reference 'compilerOptions' / 'jvmTarget' / candidatos kotlin()
  Causa: AGP 9 mudou DSL; bloco kotlin { } só existe se KGP aplicado; Flutter 3.47.9 não aplica.
Tentativa 2 (AGP 8.7.3, seguindo "voltar para AGP 8"):
  Erro: Android Gradle Plugin version 8.7.3 is lower than Flutter's minimum supported version 8.11.1
  Causa: Flutter 3.47.9 exige AGP >= 8.11.1 (S44b).
Tentativa 3 (AGP 9.0.0 + kotlin-android no app + flags newDsl=false/builtInKotlin=false):
  Erro: Cannot add task 'generateLockfiles' as a task with that name already exists
  Causa: conflito de task entre root project e :app; Flutter Gradle Plugin tenta registrar generateLockfiles duas vezes (S44a).
  Flag --android-skip-build-dependency-validation NÃO resolveu.
  flutter clean NÃO resolveu.

3.4 Mapa dos 13 itens (atualizado S44)
#	Item	Status	Evidência	Depende de
1	Package Android br.com.rumo.app	✅	2e09068	—
2	Bundle id iOS br.com.rumo.app	✅	2e09068	—
3	Label Android "Rumo"	✅	2e09068	—
4	Info.plist sem hardcode	✅	2e09068	—
5	Política de privacidade (/privacy)	✅	deb7969	—
6	Link no AppHeader	✅	deb7969	—
7	Testar no emulador Android	❌ (BLOQUEADO S44a)	emulador OK, build falha	AGP/Flutter compat (S44f)
8	Testar splash + ícone no launcher	❌	—	item 7
9	Testar no simulador iOS	❌	—	usuário ter Mac
10	Gerar keystore + signingConfigs	❌	—	item 7 (build precisa passar)
11	.gitignore do keystore	❌	—	item 10
12	Contas Google Play ($25) + Apple ($99/ano)	❌	—	só usuário
13	Remover BOM/comentário com.example	❌	—	eu (higiene)
Fora dos 13 (S45+): screenshots + descrição da loja, submissão Google Play, submissão App Store, tile server próprio, correções de review.

3.5 Tropeços da S44
3 falhas de build consecutivas (S44a/b) — causa raiz não resolvida.
1 erro de leitura meu: no início, assumi que o arquivo colado pelo usuário (plugins + allprojects + subprojects + clean) era o app/build.gradle.kts; era o android/build.gradle.kts de nível superior. Corrigido ao reler.
1 correção errada minha: mandei rebaixar AGP para 8.7.3 sem verificar o mínimo do Flutter 3.47.9 (8.11.1). Custou 1 rodada de 8 min.
Nenhum arquivo de código entregue com sucesso. 3 arquivos tocados em estado incerto (S44d).
O usuário pediu handoff antes do limite do site (S44g) — respeitado.

SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)
Nenhuma mudança desde S39. 180 testes passando. Nada a fazer no backend para a S45.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Primeira ação da S45 (S27a):
  cd D:\Rumo
  git status --short --untracked-files=all
  # Esperado: M docs/HANDOFF.md + M mobile/android/app/build.gradle.kts + M mobile/android/build.gradle.kts + M mobile/android/gradle.properties
  # Decisão da S45: commitar como "wip: tentativa AGP 9 (falhou)" OU reverter com git checkout -- mobile/android/
  # Recomendação: commitar o handoff S44 separado; as edições de mobile/android/ podem ser revertidas ou commitadas como wip — o importante é registrar.

Segunda ação (S27b): Fase 0 (handoff -> log/status -> build/lint/analyze -> docker/pytest/ruff -> prod backend -> prod frontend).

SEÇÃO 6 — SCRIPTS ÚTEIS (S44)
Fase 0 — sanidade (inalterado)
  cd D:\Rumo\web; npm run build; npm run lint
  cd ..\mobile; & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
  cd ..\backend; .\venv\Scripts\Activate.ps1; python -m pytest -q; ruff check .

Inspecionar estado do AGP/Kotlin (S44d — fazer PRIMEIRO na S45)
  cd D:\Rumo
  Write-Host "=== app/build.gradle.kts ==="
  Get-Content mobile\android\app\build.gradle.kts -Encoding UTF8
  Write-Host "=== android/build.gradle.kts (nível superior) ==="
  Get-Content mobile\android\build.gradle.kts -Encoding UTF8
  Write-Host "=== gradle.properties ==="
  Get-Content mobile\android\gradle.properties -Encoding UTF8
  Write-Host "=== settings.gradle.kts (AGP version) ==="
  Get-Content mobile\android\settings.gradle.kts -Encoding UTF8 | Select-String "com.android.application|com.android.library|kotlin"

Emulador (S44 — já funcionou)
  & "C:\Users\nasci\flutter\bin\flutter.bat" emulators
  & "C:\Users\nasci\flutter\bin\flutter.bat" emulators --launch emulador1
  & "C:\Users\nasci\flutter\bin\flutter.bat" devices
  # esperado: sdk gphone64 x86 64 • emulator-5554 • android-x64 • Android 16 (API 36)

Build Android (S44 — FALHOU, não repetir sem S44f)
  cd D:\Rumo\mobile
  & "C:\Users\nasci\flutter\bin\flutter.bat" run -d emulator-5554
  # NÃO repetir cegamente. Ler S44f primeiro.

Rota S44f (recomendada para S45, NÃO testada)
  # 1) Inspecionar arquivos (comandos acima)
  # 2) Rebaixar AGP para 8.13.0 (ou 8.11.1) em settings.gradle.kts
  # 3) REMOVER android.newDsl=false e android.builtInKotlin=false do gradle.properties
  # 4) Reverter app/build.gradle.kts para formato AGP 8:
  #    - plugins { id("com.android.application"); id("kotlin-android"); id("dev.flutter.flutter-gradle-plugin") }
  #    - SEM bloco kotlin { } externo
  #    - DENTRO de android { }: kotlinOptions { jvmTarget = "17" } (ou compileOptions)
  # 5) Remover id("kotlin-android") do android/build.gradle.kts de nível superior (S44e)
  # 6) flutter clean && flutter run -d emulator-5554

Keystore Android (item 10 — S45+, só depois do build passar)
  keytool -genkey -v -keystore D:\Rumo\mobile\android\app\rumo-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias rumo
  # .gitignore: mobile/android/app/*.jks, mobile/android/key.properties

SEÇÃO 7 — DÍVIDAS TÉCNICAS (S44)
Fechadas na S44:
  (nenhuma — a S44 não fechou item do mapa; só preparou emulador e expôs o bloqueador AGP)

Conhecidas (não-bug):
  (S41) prod@rumo.com state (weight_kg=null height_cm=null full_name="Prod User") — 6 sessões confirmando. Estado, não bug.
  (S42k) PWA sem PNGs no manifest — SVG cobre navegadores modernos. Não-bloqueador.
  (S42m) analysis_options.yaml reescrito pelo flutter create — benéfico. Commitado como está.
  (S42o) Hash do index-*.js não muda com index.html/public/ — sinal de deploy é o conteúdo do index.html.
  (S42p) flutter_native_splash:create tocou mobile/web/index.html — restaurado na S42. mobile/web não é usado em produção.
  (S42q) Content byte[] no PS 5.1 para manifest — comportamento do PS, não-bug.
  (S43d) BOM em build.gradle.kts e AndroidManifest.xml — tolerado por Kotlin/XML. Não-bloqueador. Higiene (item 13).
  (S43e) Info.plist sem hardcode — correto no Flutter (nome vem do PRODUCT_NAME/loja). Não "corrigir".

Oportunidades (S45+):
  (S44a/b/f) RESOLVER BUILD ANDROID — prioridade absoluta. Rota S44f.
  (S43) Testar app no emulador Android — bloqueado por S44a.
  (S43) Testar splash + ícone no launcher — após item 7.
  (S43) Gerar keystore + signingConfigs — após build passar.
  (S43) Contas Google Play + Apple Developer — só o usuário.
  (S43) Remover BOM/comentário com.example — higiene.
  (S42) Gerar logo192.png + logo512.png — S45+.
  (S42) Ícone adaptativo monochrome Android 13+ — S45+.
  (S34) Alinhar UserPublic local de activity.dart — S45+.
  (S36) Deep-link ?q= na busca mobile — S45+.
  (S37) Botão de export unitário no web — S45+.
  (S38) Filtros de activity_type no perfil — S45+.
  (S39) Editar birth_date/email/username — S45+.
  (S39) Trocar extra do /edit-profile por GET /auth/me — S45+.
  (S43+) Tile server próprio do OSM — S45+.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 45)
Primeira ação (S27a): commit do handoff S44 + decisão sobre edições de mobile/android/ (S44d).
  cd D:\Rumo
  git status --short --untracked-files=all
  # Opção 1 (recomendada): commitar handoff separado, reverter edições de mobile/android/
  #   git add docs/HANDOFF.md && git commit -m "docs: handoff da Sessao 44" && git push
  #   git checkout -- mobile/android/app/build.gradle.kts mobile/android/build.gradle.kts mobile/android/gradle.properties
  # Opção 2: commitar tudo como wip
  #   git add -A && git commit -m "wip: tentativa AGP 9 (falhou) + handoff S44" && git push

Segunda ação: inspecionar os 4 arquivos Android (Seção 6, "Inspecionar estado do AGP/Kotlin") ANTES de qualquer edição.

Terceira ação: aplicar rota S44f (rebaixar AGP para 8.13.0, remover flags AGP 9, reverter app/build.gradle.kts para formato AGP 8, remover kotlin-android do nível superior).

Quarta ação: flutter clean && flutter run -d emulator-5554.

Quinta ação: se build passar -> checklist de teste (login prod@rumo.com/senha12345 -> feed -> perfil -> upload). Se falhar -> NÃO insistir cegamente; considerar:
  - Atualizar Flutter para versão que suporte AGP 9 (verificar release notes)
  - flutter analyze --suggestions (sugerido pelo próprio log de erro)
  - Pedir ajuda no canal Flutter/GitHub issue

Fora do escopo da S45: screenshots + descrição da loja, submissão Google Play, submissão App Store, tile server, correções de review. Ficam para S46+.

Ordem crítica: S44a (build Android) é o bloqueador de TUDO no mobile. Sem ele, não há keystore, não há publicação, não há teste no emulador. A S45 deve gastar no máximo 1–2 tentativas na rota S44f; se não funcionar, escalar (atualizar Flutter ou abrir issue).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S44)
S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido [...] faça um handoff bem detalhado [...] sempre trabalhe desta forma."
S22: "sempre vamos seguir o que você recomendar."
S23: "sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado [...] quando o limite estiver próximo do limite de 70% a 80%."
S24–S43: reforçou os mesmos acordos. Tolerou tropeços (S21–S39: 1–8 por sessão; S40: 0; S41: 0; S42: 0; S43: 1 erro de leitura).
S40: "estou com receio de ficar na mão pois fique ontem. [...] me mande o comando no powershell [...] tome cuidado para não esgotar o site ou chat para fazer o handoff."
S41: "ontem o chat acabou no meio do código, gostaria que você avisasse se caso isso for ocorrer, não estou falando apenas do limite do chat, mas sim o limite do site (IA)."
S42: "já falei, vamos fazer sempre o que você recomendar."
S43: "como você recomendar" (3×). Interpretado como delegação (S43b).
S44: "estou com medo de acabar o limite do site ou do chat, pois não estamos progredindo deu erro novamente" / "vamos fazer o handoff completo, pois quem sabe se no outro chat resolvemos."
Acordos novos da S44: S44a–S44g (vide Seção 0).

O que funcionou na S44 (manter):
  Fase 0 completa, 6/6 verdes.
  Emulador configurado e funcionando (licenças aceitas, emulator-5554 visível).
  Parada no momento certo: handoff antes do limite do site (S44g).
  Registro honesto das 3 falhas de build (S44a/b) e das edições em estado incerto (S44d).

O que não funcionou (evitar na S45):
  Tentar correções incrementais de build sem inspecionar o arquivo real (S44d) — a S45 deve ler os 4 arquivos ANTES de editar.
  Mandar rebaixar AGP sem verificar o mínimo do Flutter (8.11.1) — custou 1 rodada.
  Assumir que o arquivo colado era o app/build.gradle.kts quando era o de nível superior — pedir o caminho exato.
  Insistir no flutter run após 3 falhas sem parar para handoff — a S44 parou no limite certo, mas poderia ter parado 1 rodada antes.

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 44)
Backend — ~95% (inalterado desde S39)
  Auth, perfil, atividades, feed, comentários, upload, stats, follows, export, 180 testes — 100% ✅
  Ruff (0 warnings) — 100% ✅
  Faltando pro MVP: editar email/username, birth_date, is-following (opcional), notificações (pós-MVP) — ⏳
  Consolidado backend — ~95% ✅

Web — ~99% (inalterado desde S43)
  Feed, perfil, detalhe, busca, editar perfil, stats — 100% ✅
  Identidade visual (favicon + manifest + theme-color + logo.svg) — 100% ✅ S42
  Política de privacidade (/privacy + link) — 100% ✅ S43
  Upload (se houver — não confirmado) — ? ❓
  Tile server próprio do OSM — 0% ❌ S45+
  Consolidado web — ~99% ✅

Mobile — ~92% (caiu de ~96% na S43)
  Feed, perfil, detalhe, upload, busca, editar perfil, stats, export — 100% ✅ (código)
  Scaffolds Android/iOS — 100% ✅ S42
  Ícone + splash nativo — 100% ✅ S42
  Package br.com.rumo.app (Android + iOS) — 100% ✅ S43
  Label "Rumo" + Info.plist correto — 100% ✅ S43
  BUILD ANDROID COMPILA — 0% ❌ S44a (bloqueador)
  Teste em emulador Android / simulador iOS — 0% ❌ S44 (bloqueado por S44a)
  Paridade visual exata com o web — ~90% 🟡
  Refresh token / logout automático em 401 — 0% ❌ S45+
  Consolidado mobile — ~92% 🟡 (código ~96%, mas build quebrado puxa para baixo)

Bloqueadores não-código — ~25% (inalterado desde S43)
  Ícone do app (mobile + favicon web) — 100% ✅ S42
  Identidade visual (logo, splash) — 100% ✅ S42
  Política de privacidade — 100% ✅ S43
  Package real (br.com.rumo.app) — 100% ✅ S43
  Teste em emulador (pré-requisito de release) — 0% ❌ S44 (bloqueado por S44a)
  Build assinado (keystore + provisioning) — 0% ❌ S45 (bloqueado por S44a)
  Conta Google Play Developer ($25) — 0% ❌ S45
  Conta Apple Developer ($99/ano) — 0% ❌ S45
  Publicação nas lojas — 0% ❌ S46
  Tile server próprio do OSM — 0% ❌ S45+
  Screenshots / descrição da loja — 0% ❌ S46
  Consolidado bloqueadores — ~25% 🟡

Consolidado
  Camada	%	Peso estimado	Contribuição
  Backend	~95%	35%	33.3%
  Web	~99%	20%	19.8%
  Mobile	~92%	30%	27.6%
  Bloqueadores não-código	~25%	15%	3.75%
  MVP consolidado	~84,5%	100%	~84,5%

Interpretação: caiu de ~85,6% (S43) para ~84,5% (S44). A queda de ~1,1 pt veio do mobile (96% -> 92%) porque o build Android provou-se quebrado (S44a). O código não regrediu, mas a confiança no "mobile pronto" caiu: sem build, não há app. O backend e o web estão intactos. O bloqueador S44a é o único item que realmente trava o lançamento agora — resolvido ele, o mobile volta a ~96% e o consolidado a ~86%.

Estimativa de sessões restantes
  Sessão	Foco	Estimativa
  S45	Resolver build Android (S44f: AGP 8.13 + formato AGP 8) + testar no emulador	1–2 sessões (depende de S44f funcionar)
  S46	Keystore + contas + higiene + screenshots	1 sessão
  S47	Submissão Google Play (review ~1–3 dias)	1 sessão + review
  S48	Submissão App Store (review ~1–7 dias) + correções	1 sessão + review
  S49+	Pós-MVP (notificações, editar email/username, refresh token, tile server)	contínuo
  Estimativa: ~3–4 sessões até "pronto pra submeter" (S45–S46), +1–2 sessões de review (S47+). Total: ~5–6 sessões até o app publicado (subiu de ~4–5 na S43 porque o build Android revelou-se um bloqueador real, não só "não testado").