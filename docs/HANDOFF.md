HANDOFF — SESSÃO 44 (ATUALIZADO)
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro (S21–S44, inalterada): você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho, nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

Regras críticas S21–S43 mantidas integralmente. Adições da S44:

S44a (NOVA — bloqueador AGP 9 + Flutter 3.47.9). O build Android NÃO compila. Erro: Cannot add task 'generateLockfiles' as a task with that name already exists. O Flutter Gradle Plugin tenta registrar essa task no root project e/ou no :app, e o Gradle rejeita porque ela já existe. A documentação oficial do Flutter afirma que AGP 9 usa Kotlin integrado por padrão, e apps que usam kotlin-android falham sem migração [citation:4]. O Flutter 3.44+ ofereceu suporte temporário com android.builtInKotlin=false, mas isso tem bugs no AGP 9.0.0. O Flutter 3.47 já suporta Kotlin integrado (android.builtInKotlin=true) se o app e todos os plugins migrarem [citation:4].

S44b (NOVA — AGP 8.13.2 também falhou). A S44 tentou rebaixar AGP para 8.13.2, remover as flags android.newDsl=false e android.builtInKotlin=false, e manter kotlin-android no app. O erro generateLockfiles persistiu. Ou seja: não é a versão do AGP, é o estado do projeto/plugin.

S44c (NOVA — app NUNCA rodou nos scaffolds novos). O item 7 do mapa (testar no emulador Android) continua 0%. O emulador emulador1 (Android 16, API 36) está funcionando e o Flutter o enxerga (emulator-5554). O problema é 100% build.

S44d (NOVA — estado dos arquivos Android após S44, INCERTO). Durante a S44, os seguintes arquivos foram editados múltiplas vezes:
- mobile/android/settings.gradle.kts: atualmente com com.android.application version "8.13.2" (foi 9.0.0, depois 8.7.3, depois 8.13.2)
- mobile/android/gradle.properties: android.newDsl=false e android.builtInKotlin=false FORAM REMOVIDAS na última tentativa (estado atual: sem essas flags)
- mobile/android/build.gradle.kts (nível superior): sem kotlin-android e sem bloco kotlin { } (corrigido)
- mobile/android/app/build.gradle.kts: com id("kotlin-android") no plugins { } e bloco kotlin { compilerOptions { jvmTarget = JVM_17 } } no final (formato AGP 8)
A próxima sessão DEVE inspecionar os 4 arquivos ANTES de qualquer edição (regra de ouro).

S44e (NOVA — rota recomendada para S45: migrar para Kotlin integrado). A documentação oficial do Flutter [citation:4][citation:8] indica que para AGP 9+ o caminho correto é:
1. Atualizar para AGP 9.0.1+ (o template do Flutter 3.47 usa AGP 9.1.0 [citation:5])
2. Remover id("kotlin-android") do app/build.gradle.kts
3. Remover o bloco kotlin { compilerOptions { } }
4. Garantir android.builtInKotlin=true (ou ausente, pois é o padrão no AGP 9)
5. Garantir android.newDsl=true (ou ausente)
Isso NÃO foi testado na S44. A S44 tentou o caminho oposto (manter kotlin-android + flags false) e falhou.

S44f (NOVA — alternativa: projeto novo + copiar lib/). Se a migração S44e falhar, a rota mais segura é criar um projeto Flutter novo com flutter create (que já vem com AGP 9 e configuração correta), copiar a pasta lib/ e o pubspec.yaml, e testar. Isso elimina qualquer resquício de configuração antiga nos arquivos Gradle.

SEÇÃO 1 — TL;DR para quem chega agora
Estado do repo: HEAD == origin/main == 0ce5626 (handoff S43). Working tree deve ter M em docs/HANDOFF.md + M em mobile/android/ (4 arquivos editados na S44, estado S44d).

S44 feita nesta sessão:
- Fase 0 completa: 6/6 verdes (web build/lint, mobile analyze, backend pytest 180, ruff)
- Emulador Android: emulador1 (Android 16, API 36) rodando, Flutter enxerga emulator-5554
- flutter doctor: licenças Android aceitas
- flutter run: FALHOU 5 vezes. Erro persistente: Cannot add task 'generateLockfiles'.
  - AGP 9.0.0 + kotlin-android no app + flags false: falhou
  - AGP 8.7.3: Flutter exige >= 8.11.1 (falhou)
  - AGP 9.0.0 + kotlin-android no nível superior (errado): falhou
  - AGP 9.0.0 + kotlin-android no app (corrigido): falhou
  - AGP 8.13.2 + sem flags: falhou (S44b)

O que falta (7–13): teste no emulador (item 7, bloqueado por S44a), keystore (10), contas (12), higiene de BOM (13).

Percentual consolidado: ~82% (mobile caiu para ~88% porque o build não compila; código está lá, mas não roda).

SEÇÃO 2 — PRODUÇÃO E AMBIENTE (inalterado)
Backend: https://rumo-api-5s0b.onrender.com
Frontend Web: https://rumo-wheat.vercel.app
Repo local: D:\Rumo
Flutter: 3.47.9 / Dart 3.13.7 (C:\Users\nasci\flutter)
SO: Windows 11 (26H2), PowerShell 5.1
Python: 3.13.7 (venv em D:\Rumo\backend\venv)
Android SDK: C:\Users\nasci\AppData\Local\Android\Sdk (SDK 36.0.0, NDK 27.0 instalado na S44)
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

git status --short ao fim da S44: M docs/HANDOFF.md + M mobile/android/app/build.gradle.kts + M mobile/android/build.gradle.kts + M mobile/android/gradle.properties + M mobile/android/settings.gradle.kts. NADA disso foi commitado.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 44
3.1 Fase 0 — validação (6/6 verdes)
git: HEAD == origin/main == 0ce5626, working tree limpo
web build: 826 modules, built in 2.08s (index-BizVMh0m.js)
web lint: OK
mobile analyze: No issues found! (ran in 4.2s)
backend pytest: 180 passed in 50.49s
backend ruff: All checks passed!

3.2 Emulador Android — preparação
flutter emulators: 2 AVDs (emulador1, meuEmulador)
flutter doctor --android-licenses -> All SDK package licenses accepted
emulador1 iniciado: flutter emulators --launch emulador1
flutter devices: sdk gphone64 x86 64 (mobile) • emulator-5554 • android-x64 • Android 16 (API 36) (emulator)

3.3 flutter run — 5 tentativas, todas falharam com generateLockfiles
O erro Cannot add task 'generateLockfiles' é um conflito de registro de task do Flutter Gradle Plugin. A documentação oficial do Flutter [citation:4] diz que AGP 9 exige Kotlin integrado; o caminho de compatibilidade com kotlin-android tem bugs.

3.4 Mapa dos 13 itens (atualizado S44)
#	Item	Status	Evidência	Depende de
1	Package Android br.com.rumo.app	✅	2e09068	—
2	Bundle id iOS br.com.rumo.app	✅	2e09068	—
3	Label Android "Rumo"	✅	2e09068	—
4	Info.plist sem hardcode	✅	2e09068	—
5	Política de privacidade (/privacy)	✅	deb7969	—
6	Link no AppHeader	✅	deb7969	—
7	Testar no emulador Android	❌ (BLOQUEADO S44a)	emulador OK, build falha	AGP/Flutter (S44e)
8	Testar splash + ícone no launcher	❌	—	item 7
9	Testar no simulador iOS	❌	—	usuário ter Mac
10	Gerar keystore + signingConfigs	❌	—	item 7
11	.gitignore do keystore	❌	—	item 10
12	Contas Google Play ($25) + Apple ($99/ano)	❌	—	só usuário
13	Remover BOM/comentário com.example	❌	—	eu (higiene)

SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)
Nenhuma mudança desde S39. 180 testes passando. Nada a fazer no backend para a S45.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Primeira ação da S45 (S27a):
cd D:\Rumo
git status --short --untracked-files=all
# Opção 1 (recomendada): commitar handoff, reverter mobile/android/
git add docs/HANDOFF.md && git commit -m "docs: handoff da Sessao 44 (build Android bloqueado)" && git push
git checkout -- mobile/android/
# Opção 2: commitar tudo como wip
git add -A && git commit -m "wip: tentativa AGP 9/8 (falhou) + handoff S44" && git push

Segunda ação (S27b): Fase 0 (handoff -> log/status -> build/lint/analyze -> docker/pytest/ruff -> prod backend -> prod frontend).

SEÇÃO 6 — SCRIPTS ÚTEIS (S44)
Inspecionar estado dos 4 arquivos Android (FAZER PRIMEIRO na S45)
cd D:\Rumo
Get-Content mobile\android\settings.gradle.kts -Encoding UTF8
Get-Content mobile\android\gradle.properties -Encoding UTF8
Get-Content mobile\android\build.gradle.kts -Encoding UTF8
Get-Content mobile\android\app\build.gradle.kts -Encoding UTF8

Emulador (já funcionou)
& "C:\Users\nasci\flutter\bin\flutter.bat" emulators --launch emulador1
& "C:\Users\nasci\flutter\bin\flutter.bat" devices
# esperado: sdk gphone64 x86 64 • emulator-5554 • android-x64 • Android 16 (API 36)

Rota S44e (Kotlin integrado — NÃO testada na S44)
# 1) Inspecionar os 4 arquivos
# 2) settings.gradle.kts: com.android.application version "9.1.0" (template 3.47 usa 9.1.0 [citation:5])
# 3) gradle.properties: garantir android.builtInKotlin=true (ou ausente) e android.newDsl=true (ou ausente)
# 4) app/build.gradle.kts: REMOVER id("kotlin-android") e o bloco kotlin { }
# 5) android/build.gradle.kts (nível superior): sem kotlin-android, sem bloco kotlin { }
# 6) flutter clean && flutter run -d emulator-5554

Rota S44f (projeto novo — fallback)
# 1) flutter create --org br.com.rumo rumo_novo (em D:\Rumo\_temp, fora do repo)
# 2) Copiar lib/ e pubspec.yaml do projeto atual para o novo
# 3) flutter run -d emulator-5554 no projeto novo
# 4) Se funcionar, comparar os arquivos android/ e aplicar as diferenças ao projeto real

SEÇÃO 7 — DÍVIDAS TÉCNICAS (S44)
Fechadas na S44: nenhuma.

Conhecidas (não-bug):
(S41) prod@rumo.com state — estado, não bug.
(S42k) PWA sem PNGs — não-bloqueador.
(S43d) BOM em build.gradle.kts e AndroidManifest.xml — não-bloqueador.
(S43e) Info.plist sem hardcode — correto.

Oportunidades (S45+):
(S44a/e/f) RESOLVER BUILD ANDROID — prioridade absoluta. Rotas S44e ou S44f.
(S43) Testar app no emulador — bloqueado por S44a.
(S43) Keystore + signingConfigs — após build passar.
(S43) Contas Google Play + Apple — só o usuário.
(S43) Remover BOM — higiene.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 45)
Primeira ação: commit do handoff + reverter mobile/android/ (Seção 5).
Segunda ação: inspecionar os 4 arquivos Android.
Terceira ação: tentar rota S44e (Kotlin integrado, AGP 9.1.0, sem kotlin-android).
Quarta ação: se falhar, rota S44f (projeto novo + copiar lib/).
Quinta ação: se build passar -> checklist de teste (login/feed/perfil/upload).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S44)
S21–S43: acordos mantidos (código completo, handoff completo, aviso de limite, percentual).
S44: "estou com medo de acabar o limite do site ou do chat, pois não estamos progredindo deu erro novamente" / "vamos fazer o handoff completo, pois quem sabe se no outro chat resolvemos."
Acordos novos da S44: S44a–S44f.

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 44)
Backend — ~95%
Web — ~99%
Mobile — ~88% (código ~96%, mas build Android quebrado)
Bloqueadores não-código — ~25%
MVP consolidado — ~82%

Estimativa: ~3–4 sessões até "pronto pra submeter", +1–2 de review. Total ~5–6 sessões.