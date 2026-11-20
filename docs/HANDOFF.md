HANDOFF — SESSÃO 43
SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)
Regra de ouro (S21–S42, inalterada): você não tem acesso ao disco do usuário. Toda informação chega por Get-Content -Encoding UTF8 ou saída de comando. Nunca inventar caminho, nunca reescrever arquivo não recebido. Se precisar, pedir e esperar.

Regras críticas S21–S42 mantidas integralmente. Adições da S43:

S43a (NOVA — sessão paralela em outro chat/site). A S43 foi executada em outro chat/site entre a S42 e esta sessão. O handoff S42 não registrava isso. Resultado: os commits deb7969 (política) e 2e09068 (package) já estavam no origin/main quando esta sessão abriu. Lição: antes de aceitar o escopo do handoff anterior, rodar git log -10 --oneline e git show --stat HEAD — o handoff pode estar defasado em relação ao repo. Não assumir que HEAD do handoff == HEAD real.

S43b (NOVA — "como você recomendar" repetido = decisão delegada). O usuário respondeu "como você recomendar" 3 vezes seguidas (S43). Interpretação: ele delega a decisão, mas não quer que o assistente fique pedindo aprovação em loop. Quando isso acontecer, o assistente deve decidir, declarar a decisão e seguir, não re-perguntar. Exceção: decisões irreversíveis (apagar arquivo, force-push) ainda pedem confirmação explícita.

S43c (NOVA — paste de git show truncado no :). O PowerShell 5.1 corta a saída de git show no meio quando o terminal enche. Nas 3 vezes em que pedi diff, o paste veio truncado no :. Lição: pedir git show -- <arquivo único> (um por vez) ou filtrar com Select-String/Select-Object -First N. Nunca pedir git show de 2+ arquivos grandes de uma vez.

S43d (NOVA — BOM no build.gradle.kts e AndroidManifest.xml). O commit 2e09068 introduziu BOM UTF-8 (U+FEFF) no início de build.gradle.kts e AndroidManifest.xml (visível no diff como +﻿plugins). Kotlin e XML toleram BOM no início — não é bloqueador. Registrar como higiene (item 13 do mapa: remover se sobrar tempo).

S43e (NOVA — Info.plist sem hardcode é o correto). O 2e09068 removeu CFBundleDisplayName = Rumo Mobile e CFBundleName = rumo_mobile do Info.plist. Isso está certo: no Flutter, o nome real vem do PRODUCT_NAME (= $(TARGET_NAME)) e da loja (App Store Connect). Hardcode no plist impede a loja de usar o nome configurado. Não "corrigir" de volta.

S43f (NOVA — itens 7–13 são operação do usuário, não código). O que falta na S43 não é arquivo para o assistente colar — é flutter run no emulador, keytool para keystore, criação de contas Google/Apple. O assistente não pode entregar isso por paste. A S44 deve focar em acompanhar o usuário nesses passos, não em entregar código.

SEÇÃO 1 — TL;DR para quem chega agora
Estado do repo: HEAD == origin/main == 2e09068. Working tree limpo. Handoff S42 commitado como 3fb3c5e.

S43 feita em sessão paralela (6/13):

deb7969 — política de privacidade (/privacy + PrivacyPage.tsx 244 linhas + link no AppHeader)

2e09068 — package Android br.com.rumo.app + bundle id iOS br.com.rumo.app + label "Rumo" + Info.plist sem hardcode

S43 nesta sessão: 0 arquivos entregues. Sessão usada para reconstruir o mapa (o handoff S42 não sabia da S43 paralela) e recalcular o percentual.

O que falta (7–13): teste no emulador Android (prioridade máxima), keystore, contas de dev, higiene de BOM. Tudo depende do usuário.

Percentual consolidado: subiu de ~81,3% (S42) para ~85–86% (S43). O salto veio dos bloqueadores não-código (5% → 25%), não do código.

SEÇÃO 2 — PRODUÇÃO E AMBIENTE (inalterado)
Backend: https://rumo-api-5s0b.onrender.com

Frontend Web: https://rumo-wheat.vercel.app

Repo local: D:\Rumo

Flutter: 3.47.9 / Dart 3.13.7 (C:\Users\nasci\flutter)

SO: Windows, PowerShell 5.1

Python: 3.13.7 (venv em D:\Rumo\backend\venv)

Git ao fim da S43:

text
2e09068 (HEAD -> main, origin/main) feat(mobile): package br.com.rumo.app + label Rumo + iOS bundle id (Sessao 43, 6/13)
deb7969 feat(web): politica de privacidade (/privacy) + link no AppHeader (Sessao 43, 3/13)
3fb3c5e docs: handoff da Sessao 42
aaeb7c4 feat(mobile): scaffolds android/ios + icone e splash nativo (Sessao 42)
8576d95 feat(web): identidade visual — favicon laranja + manifest PWA + index.html (Sessao 42)
git status --short --untracked-files=all vazio. Pendente: este handoff (primeira ação da S44 — S27a).

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 43
3.1 Fase 0 — validação (5/5 verdes)
git: HEAD == origin/main == 2e09068, working tree limpo

build/lint/analyze: No issues found!

pytest: 180 passed in 46.35s

prod backend: state conhecido (weight_kg=null height_cm=null full_name="Prod User")

prod frontend: index JS: /assets/index-CPP87bow.js + OK: favicon laranja

Observação: o hash index-CPP87bow.js é novo vs. o index-tC5onOwK.js da Fase 0 da S42 — houve deploy novo na Vercel (provavelmente disparado pelo commit do handoff S42 ou pelo deb7969). Não é problema — é sinal de Vercel saudável. Lembrete S42b/S42o: hash do index-*.js não muda só por index.html/public/; aqui mudou porque código React mudou (PrivacyPage.tsx + App.tsx + AppHeader.tsx).

3.2 Descoberta — a S43 paralela
O handoff S42 terminava em aaeb7c4. O repo real estava em 2e09068. A diferença: 3fb3c5e (handoff S42) + deb7969 (S43 3/13) + 2e09068 (S43 6/13). A S43 já tinha sido executada em outro chat/site. Nenhum arquivo foi entregue nesta sessão porque o escopo do handoff S42 (package + política) já estava feito.

3.3 Mapa dos 13 itens (reconstruído)
#	Item	Status	Evidência	Depende de
1	Package Android br.com.rumo.app	✅	2e09068	—
2	Bundle id iOS br.com.rumo.app	✅	2e09068	—
3	Label Android "Rumo"	✅	2e09068	—
4	Info.plist sem hardcode	✅	2e09068	—
5	Política de privacidade (/privacy)	✅	deb7969	—
6	Link no AppHeader	✅	deb7969	—
7	Testar no emulador Android	❌	—	usuário ter AVD
8	Testar splash + ícone no launcher	❌	—	item 7
9	Testar no simulador iOS	❌	—	usuário ter Mac
10	Gerar keystore + signingConfigs	❌	—	usuário rodar keytool
11	.gitignore do keystore	❌	—	item 10
12	Contas Google Play ($25) + Apple ($99/ano)	❌	—	só usuário
13	Remover BOM/comentário com.example	❌	—	eu (higiene)
Fora dos 13 (S44+): screenshots + descrição da loja, submissão Google Play, submissão App Store, tile server próprio, correções de review.

3.4 Tropeços da S43
0 tropeços de código (0 arquivos entregues).

3 rodadas de paste truncado (git show cortado no : — S43c).

1 erro de leitura meu: assumi que 2e09068 era o handoff S42; era a S43 paralela. Corrigido ao pedir git show --stat HEAD.

3 "como você recomendar" — interpretado como delegação (S43b).

SEÇÃO 4 — CONTRATOS DO BACKEND (INALTERADOS)
Nenhuma mudança desde S39. Repetidos do handoff S42 por completude: Auth (/auth/login, /auth/me), Perfil próprio (PUT /users/me), Atividades, Feed, Comentários, Stats, Follows, Export. 180 testes passando. Nada a fazer no backend para a S44.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO
Primeira ação da S44 (S27a):

powershell
cd D:\Rumo
git status --short
# Se M docs/HANDOFF.md:
git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 43"
git push
Estado esperado da S44 ao abrir: HEAD == origin/main == 2e09068 (ou o commit do handoff S43 se já commitado). Working tree limpo. Zero arquivos de código pendentes.

SEÇÃO 6 — SCRIPTS ÚTEIS (S43)
Fase 0 — sanidade (inalterado)
powershell
cd D:\Rumo\web; npm run build; npm run lint
cd ..\mobile; & "C:\Users\nasci\flutter\bin\flutter.bat" analyze
cd ..\backend; .\venv\Scripts\Activate.ps1; python -m pytest -q; ruff check .
Verificar estado do package (novo S43)
powershell
cd D:\Rumo
Write-Host "=== package Android ==="
Select-String -Path mobile\android\app\build.gradle.kts -Pattern "namespace|applicationId"
Write-Host "=== bundle id iOS ==="
Select-String -Path mobile\ios\Runner.xcodeproj\project.pbxproj -Pattern "PRODUCT_BUNDLE_IDENTIFIER"
Write-Host "=== label Android ==="
Select-String -Path mobile\android\app\src\main\AndroidManifest.xml -Pattern "android:label"
Write-Host "=== BOM (S43d) ==="
$bytes = [System.IO.File]::ReadAllBytes("D:\Rumo\mobile\android\app\build.gradle.kts")
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { Write-Host "BOM presente (higiene)" } else { Write-Host "sem BOM" }
Testar no emulador (item 7 — S44)
powershell
# 1) listar AVDs
& "C:\Users\nasci\flutter\bin\flutter.bat" emulators
# 2) se não houver, criar (ou abrir Android Studio > Device Manager)
# 3) rodar
cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d <emulator_id>
# 4) validar: login prod@rumo.com/senha12345 → feed → perfil → upload
Keystore Android (item 10 — S44, NUNCA commitar)
powershell
keytool -genkey -v -keystore D:\Rumo\mobile\android\app\rumo-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias rumo
# guardar senha em local seguro (não no repo)
# adicionar ao .gitignore:
#   mobile/android/app/*.jks
#   mobile/android/key.properties
SEÇÃO 7 — DÍVIDAS TÉCNICAS (S43)
Fechadas na S43:

(S42f) Mobile sem scaffolds — FECHADO S42

(S42g) Favicon roxo — FECHADO S42

(S42i) Description genérica — FECHADO S42

(S42j) Sem libs de ícone/splash — FECHADO S42

(S42n) index.html sem manifest — FECHADO S42

(S42 — bloqueador) com.example.rumo_mobile — FECHADO S43 (2e09068)

(S42 — bloqueador) Política de privacidade — FECHADO S43 (deb7969)

(S42 — opcional) Label Android "Rumo" — FECHADO S43 (2e09068)

(S42 — opcional) Bundle id iOS — FECHADO S43 (2e09068)

Conhecidas (não-bug):

(S41) prod@rumo.com state (weight_kg=null height_cm=null full_name="Prod User") — 5 sessões confirmando. Estado, não bug.

(S42k) PWA sem PNGs no manifest — SVG cobre navegadores modernos. Não-bloqueador.

(S42m) analysis_options.yaml reescrito pelo flutter create — benéfico. Commitado como está.

(S42o) Hash do index-*.js não muda com index.html/public/ — sinal de deploy é o conteúdo do index.html.

(S42p) flutter_native_splash:create tocou mobile/web/index.html — restaurado na S42. mobile/web não é usado em produção.

(S42q) Content byte[] no PS 5.1 para manifest — comportamento do PS, não-bug.

(S43d) BOM em build.gradle.kts e AndroidManifest.xml — tolerado por Kotlin/XML. Não-bloqueador. Higiene (item 13).

(S43e) Info.plist sem hardcode — correto no Flutter (nome vem do PRODUCT_NAME/loja). Não "corrigir".

Oportunidades (S44+):

(S43) Testar app no emulador Android — prioridade máxima. Nunca rodou.

(S43) Testar splash + ícone no launcher — após item 7.

(S43) Testar no simulador iOS — se tiver Mac.

(S43) Gerar keystore + signingConfigs — build assinado.

(S43) Contas Google Play + Apple Developer — só o usuário.

(S43) Remover BOM/comentário com.example — higiene.

(S42) Gerar logo192.png + logo512.png — S44+.

(S42) Ícone adaptativo monochrome Android 13+ — S44+.

(S34) Alinhar UserPublic local de activity.dart — S44+.

(S36) Deep-link ?q= na busca mobile — S44+.

(S37) Botão de export unitário no web — S44+.

(S38) Filtros de activity_type no perfil — S44+.

(S39) Editar birth_date/email/username — S44+.

(S39) Trocar extra do /edit-profile por GET /auth/me — S44+.

(S43+) Tile server próprio do OSM — S44+.

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 44)
Primeira ação (S27a): commit do handoff S43 (Seção 5).

Fase 0 completa (S27b): handoff → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend.

Rota recomendada para a S44 — itens 7–13 do mapa:

Passo	Item	Quem faz	Tempo estimado
1	Testar app no emulador Android (flutter run) — login/feed/perfil/upload	usuário (assistente guia)	20–40 min
2	Testar splash + ícone no launcher	usuário	5 min
3	Se item 1 falhar → corrigir (código)	assistente	varia
4	Gerar keystore + signingConfigs	usuário (assistente guia)	15 min
5	.gitignore do keystore	assistente (1 arquivo)	2 min
6	Criar contas Google Play + Apple Developer	só usuário	30–60 min
7	Remover BOM/comentário com.example (higiene)	assistente (1 arquivo)	2 min
Ordem crítica: item 7 (testar no emulador) PRIMEIRO. Se o app não rodar, keystore e contas são trabalho perdido. O handoff S42 já dizia isso; a S43 confirmou (o app nunca rodou nos scaffolds novos).

Fora do escopo da S44: screenshots + descrição da loja, submissão Google Play, submissão App Store, tile server, correções de review. Ficam para S45/S46.

Alternativa (se a S44 quiser reduzir escopo): só o item 7 (teste no emulador) + item 3 (correções se falhar). Rápido, destrava a pergunta "o app roda?" que nunca foi respondida.

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO (histórico + S43)
S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido [...] faça um handoff bem detalhado [...] sempre trabalhe desta forma."

S22: "sempre vamos seguir o que você recomendar."

S23: "sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado [...] quando o limite estiver próximo do limite de 70% a 80%."

S24–S41: reforçou os mesmos acordos. Tolerou tropeços (S21–S39: 1–8 por sessão; S40: 0; S41: 0; S42: 0).

S40: "estou com receio de ficar na mão pois fique ontem. [...] me mande o comando no powershell [...] tome cuidado para não esgotar o site ou chat para fazer o handoff."

S41: "ontem o chat acabou no meio do código, gostaria que você avisasse se caso isso for ocorrer, não estou falando apenas do limite do chat, mas sim o limite do site (IA)."

S42: "já falei, vamos fazer sempre o que você recomendar."

S43: "como você recomendar" (3×). Interpretado como delegação (S43b). Também: "sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado [...] percentual de quanto nosso projeto já está pronto [...] avisasse se caso isso for ocorrer [limite do site]."

Acordos novos da S43: S43a–S43f (vide Seção 0).

O que funcionou na S43 (manter):

Fase 0 completa, 5/5 verdes.

Descoberta da S43 paralela — não assumiu que o repo estava no HEAD do handoff.

Reconstrução do mapa dos 13 sem o plano original.

Recusa de entregar código sem mapa (evitou reentregar package + política).

Aviso de interrupção antes de cada bloco pesado.

O que não funcionou (evitar na S44):

Assumir que HEAD do handoff == HEAD real — pedir git log + git show --stat HEAD no primeiro bloco da Fase 0 (não no terceiro).

Pedir git show de 2+ arquivos grandes — truncou 3×. Pedir um por vez (S43c).

Perguntar "você tem o plano?" 4× — o usuário não tinha. Devia ter proposto o mapa na 2ª pergunta (S43b).

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 43)
Backend — ~95% (inalterado desde S39)
Item	%	Status
Auth, perfil, atividades, feed, comentários, upload, stats, follows, export, 180 testes	100%	✅
Ruff (0 warnings)	100%	✅
Faltando pro MVP: editar email/username, birth_date, is-following (opcional), notificações (pós-MVP)	—	⏳
Consolidado backend	~95%	✅
Web — ~99% (subiu de ~97% na S42)
Item	%	Status
Feed, perfil, detalhe, busca, editar perfil, stats	100%	✅
Identidade visual (favicon + manifest + theme-color + logo.svg)	100%	✅ S42
Política de privacidade (/privacy + link)	100%	✅ S43
Upload (se houver — não confirmado)	?	❓
Tile server próprio do OSM	0%	❌ S44+
Consolidado web	~99%	✅
Mobile — ~96% (subiu de ~93% na S42)
Item	%	Status
Feed, perfil, detalhe, upload, busca, editar perfil, stats, export	100%	✅
Scaffolds Android/iOS	100%	✅ S42
Ícone + splash nativo	100%	✅ S42
Package br.com.rumo.app (Android + iOS)	100%	✅ S43
Label "Rumo" + Info.plist correto	100%	✅ S43
Teste em emulador Android / simulador iOS	0%	❌ S44 (prioridade)
Paridade visual exata com o web	~90%	🟡
Refresh token / logout automático em 401	0%	❌ S44+
Consolidado mobile	~96%	✅
Bloqueadores não-código — ~25% (subiu de ~5% na S42)
Item	%	Status
Ícone do app (mobile + favicon web)	100%	✅ S42
Identidade visual (logo, splash)	100%	✅ S42
Política de privacidade	100%	✅ S43
Package real (br.com.rumo.app)	100%	✅ S43
Teste em emulador (pré-requisito de release)	0%	❌ S44
Build assinado (keystore + provisioning)	0%	❌ S44
Conta Google Play Developer ($25)	0%	❌ S44
Conta Apple Developer ($99/ano)	0%	❌ S44
Publicação nas lojas	0%	❌ S45
Tile server próprio do OSM	0%	❌ S44+
Screenshots / descrição da loja	0%	❌ S45
Consolidado bloqueadores	~25%	🟡
Consolidado
Camada	%	Peso estimado	Contribuição
Backend	~95%	35%	33.3%
Web	~99%	20%	19.8%
Mobile	~96%	30%	28.8%
Bloqueadores não-código	~25%	15%	3.75%
MVP consolidado	~85,6%	100%	~85,6%
Interpretação: subiu de ~81,3% (S42) para ~85,6% (S43). O salto de +4,3 pts veio quase todo dos bloqueadores não-código (5% → 25%): política + package saíram de 0% para 100%. O código já estava em ~95% e continua lá — a S43 não adicionou feature, fechou bloqueador. O que ainda trava o lançamento: teste no emulador (item 7), keystore (10), contas (12), submissão (S45+). Sem eles, não há publicação.

Estimativa de sessões restantes
Sessão	Foco	Estimativa
S44	Teste no emulador + keystore + contas + higiene	1 sessão
S45	Screenshots + descrição + submissão Google Play (review ~1–3 dias)	1 sessão + review
S46	Submissão App Store (review ~1–7 dias) + correções de review	1 sessão + review
S47+	Pós-MVP (notificações, editar email/username, refresh token, tile server)	contínuo
Estimativa: ~2–3 sessões até "pronto pra submeter" (S44–S45), +1–2 sessões de review (S46+). Total: ~4–5 sessões até o app publicado (era ~5–6 no handoff S42 — a S43 encurtou em 1 sessão porque fechou política + package de uma vez).