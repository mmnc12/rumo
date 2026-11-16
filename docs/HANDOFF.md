HANDOFF — Rumo (backend + frontend + mobile) — Sessão 36

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro para o assistente novo (leia antes de qualquer coisa)
VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. NÃO existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias: (a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8; (b) o usuário cola a saída de um comando de terminal. NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚡ REGRA S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça. ⚡ Esta regra vale TAMBÉM para comandos PowerShell com here-string @' ... '@: nunca usar "COLE O CONTEÚDO AQUI" como placeholder — o conteúdo tem que ser o arquivo inteiro. (Reforçada na S36 — REGRA S36g.)
⚡ REGRA S21 — não adivinhar nomes de símbolos do projeto. Pedir o model/enum/schema antes de referenciar.
⚡ REGRA S21 — git status antes de qualquer git restore/git checkout. git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>.
⚡ REGRA S22 — Invoke-WebRequest com -UseBasicParsing. Elimina o prompt de segurança do PS 5.1.
⚡ REGRA S22 — validar deploy do Render antes de acusar bug no código. Depois de push, checar openapi.json para a rota nova antes de acusar 422/404.
⚡ REGRA S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele. Nunca procurar "ProfilePage-" direto no HTML.
⚡ REGRA S24 — Vercel às vezes demora >90 s para o primeiro deploy após push. Se o hash antigo aparecer após 90 s, rodar o teste de novo. Não presumir bug.
⚡ REGRA S25a — Select-String -SimpleMatch NÃO aceita | como alternância. Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo.
⚡ REGRA S25b — quando lines[−1] for suspeito, confirmar com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo>" antes de concluir. Não dar "OK" nem "corrompido" sem evidência.
⚡ REGRA S25c — antes de pedir git add/git commit de um arquivo que o usuário acabou de salvar, EXIGIR o output do bloco de validação e ESPERAR.
⚡ REGRA S25d — o teste definitivo de "o save pegou" é git hash-object <arquivo> ≠ git rev-parse HEAD:<arquivo> + git status --short mostrar M <arquivo>. Se git status --short vier vazio depois de salvar, o disco é igual ao commitado. O save não pegou.
⚡ REGRA S25e — ao entregar o conteúdo de um arquivo para colar no editor, entregar SEM cerca markdown envolvendo. Entregar o arquivo inteiro como único texto da resposta, sem instruções antes/depois.
⚡ REGRA S26a — no PowerShell 5.1, Invoke-WebRequest -UseBasicParsing devolve resp.Content como STRING, não como byte[]. [System.IO.File]::WriteAllBytes(path, resp.Content) falha. Para texto UTF-8: [System.Text.Encoding]::UTF8.GetBytes(resp.Content). Para bytes crus (ZIP, imagem): resp.RawContentStream.CopyTo(fileStream). Para inspecionar GPX/XML: regex direto no Content.
⚡ REGRA S26b — validar GPX em produção por regex é mais barato que gpxpy + arquivo temporário. Contar <time> distintos com regex no Content responde "o S26 está no ar?" em 3 linhas, sem env:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>).
⚡ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Não é bug. Se a primeira validação em prod mostrar comportamento antigo, esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min.
⚡ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa. Se git status --short mostrar M docs/HANDOFF.md no início, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro, push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0.
⚡ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir.
⚡ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios". O handoff pode estar desatualizado.
⚡ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código. Não investigar como bug.
⚡ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora. Implementação em web/src/api/activities.ts → _countZipEntries().
⚡ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior, não "bate com o build local". Manter a checagem por __vite__mapDeps + leitura do conteúdo do chunk.
⚡ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número. Erro no esperado, não no código. (Reforçada na S32, S33 e S36.)
⚡ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }. Declarar sem inicializar (let entryCount: number;) quando try/catch (ou if/else) cobre todos os caminhos.
⚡ REGRA S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos" (e "TODOS"). Usar -CaseSensitive ou regex \bTODO\b.
⚡ REGRA S30b — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos. Contrato: isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; ambos false = cinza (delta 0). Sinal matemático ("+"/"−") e percentual seguem o delta cru.
⚡ REGRA S30c — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo; a descoberta de código corrige para CIMA. No mobile, SEMPRE pedir Get-ChildItem + arquivos-chave antes de estimar esforço ou travar rota.
⚡ REGRA S31a — em ambiente Windows sem Developer Mode, flutter pub add <plugin_nativo> instala mas avisa que o build vai falhar por symlink. Building with plugins requires symlink support. Please enable Developer Mode — start ms-settings:developers + ativar. Vale para qualquer plugin com código nativo. flutter analyze passa sem Developer Mode; flutter run/flutter build não.
⚡ REGRA S31b — file_picker 13.x removeu FilePicker.platform, FilePickerResult, PlatformFile.size e PlatformFile.bytes. API nova: FilePicker.pickFiles() estático retorna List<PlatformFile> (vazio = cancelou); PlatformFile.length()/lengthSync() substituem .size; PlatformFile.readAsBytes() substitui .bytes. path continua existindo (String?) mas é null na web. Consultar o changelog antes de usar API de plugin.
⚡ REGRA S31c — quando Select-String do disco mostrar conteúdo antigo depois do save do editor, contornar via WriteAllText no PowerShell imediatamente — não insistir no Ctrl+S. Sintomas: git status mostra M, mas Select-String do símbolo novo vem vazio; Get-Item mostra LastWriteTime desatualizado. Procedimento: here-string @' ... '@ + [System.IO.File]::WriteAllText(path, content, [System.Text.UTF8Encoding]::new(false)) + verificar com 3 Select-String. (Reforçada na S36 — reincidência em dois blocos consecutivos.)
⚡ REGRA S32a — Select-String -SimpleMatch 'class X' casa PREFIXOS: 'class ActivityCard' casa 'class ActivityCard' e 'class ActivityCardMetric'. Para contar classe exata, usar -Pattern '\bclass X\b' (regex com word boundary) ou -Pattern 'class X ' (com espaço no fim).
⚡ REGRA S32b — Select-String -SimpleMatch '_Simbolo' casa menções em COMENTÁRIOS também. Se o comentário de topo cita o símbolo antigo ("renomeado ActivityCard → ActivityCard"), a contagem nunca vai a zero. Para contar ocorrências em código, filtrar linhas que não começam com // ou usar regex ancorado.
⚡ REGRA S32c — ao anunciar "esperado ≈ N linhas", CONTAR as linhas do arquivo entregue antes de anunciar. Contagem mental falha consistentemente para baixo em arquivos com widgets aninhados.
⚡ REGRA S32d — nos Select-String de validação, o "esperado" é sempre PISO ou FAIXA, nunca número exato, a menos que eu tenha contado o output real do arquivo entregue. Se não contei, anunciar "≥ N" e aceitar qualquer valor ≥ N. Erro no esperado, não no código.
⚡ REGRA S33a — alternância em Select-String: SEMPRE -Pattern 'a|b' (sem -SimpleMatch). Vale também para blocos de verificação que o assistente monta. (Reincidências: S25a, S33a, S36d.)
⚡ REGRA S33b — em Select-String de validação, o "esperado" é SEMPRE piso/faixa, nunca exato, mesmo quando o número parece óbvio.
⚡ REGRA S34a — git rev-parse HEAD:<arquivo> exige path relativo à RAIZ DO REPO, não ao CWD. Rodando de D:\Rumo\mobile, o correto é git rev-parse HEAD:mobile/lib/main.dart, não HEAD:lib/main.dart. O git hash-object aceita path relativo ao CWD; o git rev-parse não. Sintoma: "fatal: path 'mobile/lib/...' exists, but not 'lib/...'". Erro do comando, não do código.
⚡ REGRA S34b — nas validações de Select-String, o "esperado" anunciado ANTES de rodar deve ser reconhecidamente vago (≥N, faixa) — e mesmo assim pode errar. Confirmar antes de declarar erro. Reforça S33b.
⚡ REGRA S34c — ao validar tela mobile no Chrome, a sessão do localStorage pode estar com outro usuário (ex.: Prod2 logado de um teste anterior). A primeira screenshot pode ser do ProfilePage self de OUTRO usuário, não do UserProfilePage alvo. Antes de declarar bug: confirmar (a) qual usuário está logado, (b) qual URL foi colada, (c) se o flutter run foi reiniciado depois do último commit de main.dart (hot restart NÃO pega mudança de rota).
⚡ REGRA S35a — (FECHADA na S36) O GET /feed do backend NÃO embutia o objeto user no payload da atividade; o mobile lia json['user'] e caía em "Usuário". Solução S36: o backend já devolvia o autor como author (via FeedItemResponse.author = Field(validation_alias="user")); a S36 ADICIONOU user ao lado de author no FeedItemResponse, apontando para o mesmo Activity.user do ORM. Mobile e web coexistem: mobile lê user, web continua lendo author.
⚡ REGRA S36a (NOVA) — no PS 5.1, MatchCollection[-1] NÃO funciona (indexação negativa). Usar times[times[times.Count - 1]. Sintoma silencioso: Write-Host $times[-1].Groups[1].Value imprime vazio e o teste "passa" por engano. Variante da S25b, específica de MatchCollection.
⚡ REGRA S36b (NOVA) — em arquivos minified (bundle .js da Vercel), Select-String devolve a linha inteira (que é o arquivo todo, uma linha só). Para inspecionar hashes de chunks, usar [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9-]+.js') e iterar sobre os grupos — não Select-String.
⚡ REGRA S36c (NOVA) — ao validar toque no ActivityCard no Chrome, confirmar PRIMEIRO qual tela está aberta pela URL (#/feed vs #/user/:id vs #/profile). O mesmo ActivityCard tem comportamento diferente nas 3 (feed passa onAuthorTap; perfil self passa authorUsernameOverride; perfil de terceiro não passa nem um nem outro — o avatar herda o onTap do card e abre o detalhe). Reincidência da família da S34c, só que "tela errada" em vez de "usuário errado".
⚡ REGRA S36d (NOVA) — reincidência da S25a/S33a. Select-String -SimpleMatch 'a|b|c' NÃO é alternância. Em blocos de validação, usar SEMPRE -Pattern 'a|b|c'. Já errei 3 vezes nisso (S25a, S33a, S36d). REGRA CRÍTICA.
⚡ REGRA S36e (NOVA, CORRIGIDA 3x) — AutomaticKeepAliveClientMixin no Flutter 3.47.9 É @mustCallSuper no build: o super.build(context) É OBRIGATÓRIO (não remover!). O lint unnecessary_overrides acusa o @override Widget build mesmo assim (falso positivo conhecido). Solução definitiva: // ignore_for_file: unnecessary_overrides na LINHA 1 do arquivo. NÃO usar // ignore: local (posicionamento é frágil e gera duplicate_ignore se misturado com o global). Aprendi isso na dor: 3 tentativas de posicionamento local, todas falhas, e a solução global funcionou de primeira.
⚡ REGRA S36f (NOVA) — reincidência da S31c: o editor falhou em salvar search_page.dart duas vezes consecutivas (uma salvou pela metade: _UserSearchTabState com @override mas sem super.build; _ActivitySearchTabState com super.build mas sem @override). Solução foi WriteAllText com o arquivo completo. Sintoma: flutter analyze mostra 3 warnings simultâneos com linhas "erradas". Procedimento: Get-Content | Select-Object -Skip N -First M para ver o estado real, e WriteAllText com o arquivo inteiro.
⚡ REGRA S36g (NOVA) — reforço da S21: comandos PowerShell com here-string @' ... '@ entregam o CONTEÚDO REAL, nunca placeholder tipo "COLE O CONTEÚDO AQUI". Na S36 eu entreguei um WriteAllText com placeholder e o arquivo virou lixo (COLE O CONTEÚDO INTEIRO DO ARQUIVO ACIMA AQUI foi gravado no disco). Felizmente era untracked e recuperável. A regra vale para comandos, não só para código.

O que é LOCAL vs. o que é PRODUÇÃO
LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.
PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (173 passed ao fim da S36). Container de teste rumo_postgres_test na porta 5433.
⚡ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).

Estrutura do repo (referência — conferir, não assumir)
D:\Rumo
├── .vscode/settings.json
├── backend/ (venv em backend/venv, Python 3.13.7)
│ ├── alembic/
│ ├── app/
│ │ ├── core/ models/ routers/ schemas/ services/
│ │ └── pycache/
│ ├── samples/
│ ├── scripts/
│ ├── tests/ (conftest.py + test_calories + test_comment + test_export
│ │ + test_export_bulk + test_feed ← NOVO S36 + test_follow
│ │ + test_like + test_stats) — 8 arquivos, 173 testes
│ ├── _scratch/ (ignorado pelo git; s33_delta_test.gpx criado na S33)
│ ├── docker-compose.test.yml
│ ├── pytest.ini
│ └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│ ├── lib/
│ │ ├── main.dart (StatefulShellRoute + bottom nav desde S32;
│ │ │ +rota /user/:id desde S34;
│ │ │ +rota /search desde S35, atualizada S36 para SearchPage)
│ │ ├── models/ (activity.dart, activity_track.dart, comment.dart,
│ │ │ stats.dart ← S33, user.dart ← S34,
│ │ │ user_me.dart ← S32)
│ │ ├── pages/ (activity_detail_page.dart, feed_page.dart,
│ │ │ login_page.dart, profile_page.dart ← EDITADO S33,
│ │ │ search_page.dart ← NOVO S36 (2 abas),
│ │ │ upload_page.dart ← S31,
│ │ │ user_profile_page.dart ← S34)
│ │ ├── services/ (api.dart ← EDITADO S36 (+searchActivities),
│ │ │ auth_service.dart)
│ │ ├── utils/ (format.dart ← S33)
│ │ └── widgets/ (activity_card.dart ← EDITADO S34,
│ │ activity_map.dart, by_type_list.dart ← S33,
│ │ like_button.dart, stats_cards.dart ← S33)
│ ├── pubspec.yaml (file_picker: ^13.3.3, go_router: ^18.1.2,
│ │ name: rumo_mobile)
│ └── pubspec.lock
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

⚡ mobile/lib/pages/user_search_page.dart NÃO EXISTE MAIS (removido na S36). Foi substituído por search_page.dart (mesma rota /search, mas com 2 abas: Usuários | Atividades).

Como rodar comandos Flutter
Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste
prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades (7 + 1 sintética da S33), 34.08 km. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, walk, 60 pontos, ~10 min) usada pra validar o S26. Tem atividade sintética "Teste delta S33 (janela anterior)" (01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null). Username no backend: produser (confirmado na S36 via /feed).
Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, username Prod2, email prod2@rumo.com, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2 (estado validado na S34; toggle follow/unfollow testado e restaurado).

⚡ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21 à S36)

SEMPRESeguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.
SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].
UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.
HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.
PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes. Reflete o estado ao fim da sessão.
VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo. Exceção: 2 arquivos acoplados por contrato interno → entregar juntos, 1 build.
VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<simbolo>" antes de build/test.
NUNCA placeholder no código entregue (S21) nem em comandos com here-string (S36g).
Não adivinhar nomes de símbolos (S21).
git status + git log antes de git restore (S21).
Invoke-WebRequest sempre com -UseBasicParsing (S22).
Validar openapi.json antes de acusar bug em rota nova (S22).
Validar bundle da Vercel baixando index-*.js (S23).
Vercel pode demorar >90 s no primeiro deploy (S24).
Select-String -SimpleMatch não aceita | como alternância (S25a, reforçada na S33a e na S36d).
Confirmar lines[−1]suspeitocomGet−Content∣Select−Object−LastN(S25b).Exigiroutputdoblocodevalidac\ca~oantesdepedircommit(S25c).Testedefinitivodosave:githash−object≠gitrev−parseHEAD:<arquivo>+gitstatus−−shortmostraM(S25d).Entregarconteuˊdodearquivoparacolarsemcercamarkdown(S25e).PS5.1:lines[−1]suspeitocomGet−Content∣Select−Object−LastN(S25b).Exigiroutputdoblocodevalidac\c​a~oantesdepedircommit(S25c).Testedefinitivodosave:githash−object=gitrev−parseHEAD:<arquivo>+gitstatus−−shortmostraM(S25d).Entregarconteuˊdodearquivoparacolarsemcercamarkdown(S25e).PS5.1:resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[] (S26a).
Validar GPX em prod por regex no Content (S26b).
Render free tier pode demorar >3 min para redeployar após push (S26c).
Commitar o handoff pendente ANTES de qualquer outra coisa na abertura (S27a).
Ordem fixa dos blocos da Fase 0: handoff → log/status → build → docker/pytest → prod back → prod front (S27b).
Antes de aceitar o escopo do handoff anterior como verdade, pedir TODOS os arquivos que o contrato toca e confirmar o gap real (S28a).
Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada, não mudança de código (S28b).
Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).
Vercel reescreve hash de chunk ao servir; sinal de "novo no ar" = hash mudou vs sessão anterior + helper no bundle (S29b).
Contar as ocorrências reais antes de anunciar "esperado Nx" num Select-String (S29c, reforçada na S33b e S36).
ESLint no-useless-assignment: declarar let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).
Select-String "TODO" casa case-insensitive — usar -CaseSensitive ou regex \bTODO\b (S30a).
Componente genérico com semântica oposta: prop booleana default-false, 4 casos (S30b).
Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + api.dart + telas (S30c).
Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink (S31a).
file_picker 13.x: API estática + length()/readAsBytes() (S31b).
Select-String do disco mostrando conteúdo antigo após save do editor → WriteAllText no PowerShell (S31c, reforçada na S36f).
Select-String -SimpleMatch 'class X' casa prefixo (S32a).
Select-String -SimpleMatch '_Simbolo' casa menções em comentários (S32b).
Anunciar "esperado ≈ N linhas" só depois de CONTAR o arquivo entregue (S32c).
Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA (S32d, reforçada S33b).
Alternância em Select-String: SEMPRE -Pattern 'a|b' (S33a, S36d).
"Esperado" é SEMPRE piso/faixa (S33b).
git rev-parse HEAD:<arquivo> exige path relativo à RAIZ do repo (S34a).
"Esperado" anunciado antes de rodar pode errar mesmo sendo faixa (S34b).
Validar tela mobile no Chrome: confirmar usuário logado, URL colada e restart do flutter run (S34c).
S35a fechada: /feed agora devolve user + author (S36).
MatchCollection[-1] não funciona no PS 5.1 — usar times[times[times.Count - 1] (S36a).
Em bundle minified, Select-String devolve a linha inteira — usar [regex]::Matches (S36b).
Ao validar toque no ActivityCard, confirmar PRIMEIRO qual tela está aberta pela URL (S36c).
Select-String -SimpleMatch com | é sempre erro — usar -Pattern (S36d, CRÍTICA).
AutomaticKeepAliveClientMixin é @mustCallSuper — super.build obrigatório. Solução de lint: // ignore_for_file na linha 1, NÃO // ignore: local (S36e).
Editor falhou 2× em salvar search_page.dart — WriteAllText é a solução (S36f).
Comandos com here-string entregam conteúdo REAL, nunca placeholder (S36g).

Processo que o usuário elogiou na S21–S36 (para manter)
Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).

Descoberta antes de codar: pedir arquivos com motivo declarado.
Validação entre cada entrega.
Contrato travado escrito antes de codar.
Commits pequenos e temáticos.
Validação separada da local.
Diagnóstico honesto antes de "consertar".

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 173 testes passando LOCALMENTE, 0 warnings. S36 adicionou test_feed.py (7 testes novos) e FeedItemResponse.user. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon, minLat, maxLon, maxLat], n_points, simplified. 404 quando route é NULL. ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax no mesmo SELECT (sem N+1).

FeedItemResponse (S36 — NOVO): agora expõe o autor em DUAS chaves:

    author: campo legado (S10), lido pelo web (FeedItem.tsx / useFeed.ts / useActivitySearch.ts).

    user: campo novo (S36), lido pelo mobile (Activity.fromJson).
    Ambos apontam para o mesmo Activity.user do ORM via validation_alias="user". Redundância intencional e barata (UserPublic tem 4 campos). O web NÃO foi tocado — continua lendo author.

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.
    Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor. CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona com ou sem rota). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422; omitido → default csv.

Export em lote (S22): GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export<YYYYMMDD-HHMMSS>.zip"). format=csv: inclui todas; format=gpx: só com rota. Filtro from/to inclusivo (UTC). 0 atividades → 200 + ZIP vazio. from > to → 422. format inválido → 422.

S26 (GPX com <time> por ponto): to_gpx(activity, coordinates, raw_track_points=None) ganhou o 3º parâmetro opcional. Quando raw_track_points existe e tem o MESMO comprimento de coordinates, cada <trkpt> recebe <time> com o timestamp real do ponto (unix epoch → ISO 8601 UTC). Caso contrário, fallback para started_at em todos os pontos. Contrato HTTP inalterado.

S31 — upload mobile (inalterado na S32–S36): POST /activities/upload — Auth Bearer JWT. multipart/form-data com file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120), activity_type (opcional), description (opcional). Sucesso: 201 com ActivityResponse. Erro: 422 (HTTPValidationError), 429 (slowapi, rate limit 10/h por IP), 401 (token). Parse síncrono, ~1–3s por arquivo.

S32 — perfil próprio + bottom nav (inalterado na S33–S36):

    GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> — auth Bearer JWT. Filtra atividades por usuário. O description do schema diz "requer seguir" quando user_id é de terceiro; para o próprio, sempre passa. Retorna ActivityResponse[] puro (sem envelope de paginação). ⚡ NÃO embute user no ActivityResponse (só o /feed e /activities/search embutem, via FeedItemResponse).

    GET /users/{user_id} — retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email. NÃO tem avatar_url. NÃO tem created_at. NÃO tem is_following. Para o perfil próprio, o cabeçalho usa GET /auth/me.

S33 — stats agregadas no perfil self (inalterado na S34–S36).

S34 — perfil de terceiro + follow (inalterado na S35–S36).

S35 — busca de usuários + onAuthorTap no feed (inalterado na S36, mas o onAuthorTap agora funciona de fato — ver S35a fechada).

S36 — busca de atividades + FeedItemResponse.user (NOVO):

    backend/app/schemas/activity.py — FeedItemResponse agora tem user: UserPublic = Field(validation_alias="user") ao lado de author.

    backend/tests/test_feed.py — NOVO, 7 testes: feed vazio, feed com atividade própria, author presente, user presente, author.id == user.id == activity.user_id, inclui seguidos, exclui não-seguidos. Total: 173 passed.

    mobile/lib/services/api.dart — +searchActivities({required String query, int limit = 20, String? token}) → Future<List<Activity>>. Guard client-side (len < 2 → []), Uri.encodeQueryComponent.

    mobile/lib/pages/search_page.dart — NOVO (substitui user_search_page.dart). DefaultTabController(length: 2) com TabBar("Usuários" | "Atividades"). Duas _XxxSearchTab (cada uma com seu TextEditingController/FocusNode/Timer 300ms/estado). AutomaticKeepAliveClientMixin preserva estado ao trocar de aba. // ignore_for_file: unnecessary_overrides na linha 1 (falso positivo do mixin). Aba Atividades renderiza ActivityCard com onTap → /activity/:id e onAuthorTap → /user/:id.

    mobile/lib/pages/user_search_page.dart — APAGADO.

    mobile/lib/main.dart — import atualizado (search_page.dart), classe UserSearchPage → SearchPage na rota /search.

Commits S36:
text

dba8594 (HEAD -> main, origin/main) refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36)
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36)
86179f2 feat(backend): expoe user no FeedItemResponse + testes de /feed (Sessao 36)
8bff66b docs: handoff da Sessao 35

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
Deps mobile (S31/S32/S33/S34/S35/S36): file_picker: ^13.3.3, go_router: ^18.1.2. Package name: rumo_mobile.

Git (estado ao fim da Sessão 36)
text

dba8594 (HEAD -> main, origin/main) refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36)
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36)
86179f2 feat(backend): expoe user no FeedItemResponse + testes de /feed (Sessao 36)
8bff66b docs: handoff da Sessao 35
199040d feat(mobile): rota /search fora do shell (Sessao 35)
d71d9fb feat(mobile): busca no feed + link do autor (Sessao 35)
25778ed feat(mobile): busca de usuarios (Sessao 35)
2b312ec docs: handoff da Sessao 34

Working tree limpo. S36 adicionou 3 commits (86179f2 … dba8594). Push feito. HEAD == origin/main.
Pendente: docs/HANDOFF.md da S36 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 36.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 36

3.1 Fase 0 — validação de estado inicial
Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short mostrou ?? mobile/flutter_01.png (screenshot do S35). Removido com Remove-Item. Sem M docs/HANDOFF.md — o handoff S35 já estava commitado (8bff66b).

    Log/status. git log --oneline -4: 8bff66b (handoff S35), 199040d, d71d9fb, 25778ed. HEAD == origin/main.

    Build/lint/analyze. npm run build: 824 modules, 2.74s, hashes novos em index/ProfilePage/ActivityDetailPage/SearchPage mas chunks-folha (RouteMap, leaflet, recharts, rolldown-runtime) idênticos — renomeação de referência cruzada (REGRA S28b), não mudança de código. npm run lint: limpo. flutter analyze: No issues found! (3.9s).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test Up 5h (healthy). pg_isready accepting (1ª tentativa). pytest -q: 166 passed in 55.34s. ruff check .: All checks passed!.

    Prod backend. me.id = 01a12c83-.... S26 GPX: 60 <time>, 60 distintos, primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z (⚠️ o $times[-1] falhou no PS 5.1 — REGRA S36a; corrigido com $times[$times.Count - 1]). S34 Prod2: username Prod2, sem email, prod segue Prod2 = True, summary.total_activities = 2, atividades = 2. S35 busca: q=pro → 1 (Prod2), q=p → 422 (contrato).

    Prod frontend. index servido: /assets/index-CJjOEm0V.js. __vite__mapDeps com 7 hashes batendo 1:1 com S35. Web intocado desde S30 (S31–S35 só mobile). Bloco 5 verde.

3.2 Fase 1 — descoberta para OPÇÃO 1 (destravar onAuthorTap no feed)
Pedidos: schemas/feed.py (NÃO EXISTE — o schema é activity.py), routers/feed.py, models/activity.dart, pages/feed_page.dart, services/api.dart. Depois: services/feed_service.py, schemas/activity.py, routers/activities.py. Depois: tests/test_feed.py (NÃO EXISTE), web/src/api/activities.ts. Depois: tests/conftest.py, tests/test_follow.py, tests/test_like.py.

ACHADOS que mudaram o plano:

    #1 O schema se chama FeedItemResponse e mora em schemas/activity.py, não em schemas/feed.py.

    #2 O router /feed é só return await feed_service.get_feed(...). Quem monta é o service.

    #3 feed_service.get_feed já faz selectinload(Activity.user) — o autor JÁ está no ORM.

    #4 FeedItemResponse já tem author: UserPublic = Field(validation_alias="user"). Ou seja: o /feed já embutia o autor, com a chave author. O handoff S35a estava ERRADO (não é "não embute" — é "embute com chave diferente da que o mobile lê").

    #5 O mobile Activity.fromJson lê json['user'] (não author). Mismatch de contrato.

    #6 O web lê author (FeedItem.tsx). Renomear quebraria o web.

    #7 /activities/search também usa FeedItemResponse — qualquer mudança no schema respinga nele.

    #8 tests/test_feed.py não existia — o /feed nunca teve cobertura desde a S10.

3.3 Fase 2 — contrato travado
Backend (2 arquivos):

    schemas/activity.py: FeedItemResponse ganha user: UserPublic = Field(validation_alias="user") além do author existente. Ambos apontam para o mesmo Activity.user do ORM.

    tests/test_feed.py: NOVO, 7 testes.
    Mobile: zero mudanças (já lia user). Web: zero mudanças (lê author).

3.4 Fase 3 — entrega incremental

    backend/app/schemas/activity.py (edição, +1 campo). flutter analyze não se aplica (backend). Validação de save: Select-String 'user: UserPublic = Field(...)' → OK, 132 linhas, git status M, hash disco ≠ hash HEAD.

    backend/tests/test_feed.py (novo, 193 linhas). pytest -q → 173 passed (166 + 7), ruff check . → limpo. Commit 86179f2.

    mobile/lib/services/api.dart (edição, +searchActivities). flutter analyze verde, 527 linhas (esperado ≥ 490; piso).

    mobile/lib/pages/search_page.dart (novo, 480 linhas após fixes). 3 iterações de lint (REGRA S36e). Commit c15dc8b.

    mobile/lib/main.dart (edição, import + classe). flutter analyze verde. Commit dba8594. user_search_page.dart removido.

3.5 Fase 3.5 — verificar save + commit (desvios de contagem)

    api.dart: anunciei "≥ 490" — veio 527. OK.

    search_page.dart: anunciei "≥ 340" — veio 547, depois 481, depois 480 após remoção de linhas. OK.

    main.dart: símbolos antigos — anunciei "esperado 0" — veio 3 (todas menções em comentários, não em código). Erro no "esperado" (REGRA S33b).

    test_feed.py: anunciei "172 passed" — veio 173 (7 testes, não 6). Erro de contagem mental (REGRA S32c).

3.6 Fase 4 — validação

Backend local: pytest -q → 173 passed. ruff check . → limpo.

Prod backend (Render): após push 86179f2, ~3 min de espera, /feed?limit=3 → tem author: True, tem user: True, author.id == user.id == 01a12c83-..., author.username == user.username == produser. S35a fechado no backend.

Mobile (Chrome, validação manual): 7/7 verde:

    Lupa no AppBar do feed → /search com TabBar Usuários | Atividades.

    Aba Usuários: pro → Prod2 aparece (debounce 300ms).

    Aba Atividades: caminhada → atividades aparecem.

    Voltar para Usuários: query pro e resultado Prod2 continuam (keep-alive).

    Tocar numa atividade → detalhe /activity/:id.

    Tocar no avatar/username → perfil do autor /user/:id.

    Alternar 3× entre abas → estado preservado nas duas.

3.7 Observações / bugs encontrados
S35a — FECHADA: O /feed já devolvia o autor (com a chave author). O mobile lia json['user'] e caía em null. A S36 adicionou user ao lado de author no FeedItemResponse, e o onAuthorTap no feed passou a funcionar sem mudar o mobile (já lia user).
Nenhum bug de código na S36. Os erros foram todos meus (posicionamento de // ignore:, placeholder em comando, Select-String -SimpleMatch com |, editor que não salvou).

3.8 Resultado da suíte (S36)

    pytest -q → 173 passed.

    ruff check . → All checks passed!.

    npm run build → 824 modules (web inalterado).

    npm run lint → limpo (web inalterado).

    flutter analyze → No issues found! (mobile com 4 arquivos novos/modificados).

    Validação manual no Chrome → 7/7.

3.9 Commits pushados (S36)
text

86179f2 feat(backend): expoe user no FeedItemResponse + testes de /feed (Sessao 36) — 2 arquivos, +208/-1
c15dc8b feat(mobile): busca de atividades + tab Usuarios|Atividades (Sessao 36) — 2 arquivos, +521
dba8594 refactor(mobile): SearchPage com 2 abas substitui UserSearchPage (Sessao 36) — 2 arquivos, +12/-272

Push feito. HEAD == origin/main == dba8594. Working tree limpo.
Pendente: docs: handoff da Sessao 36 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT). Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota". Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { id, user_id, activity_type, title, description, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, cover_photo_url, photo_count, created_at, likes_count (default 0), liked_by_me (default false), comments_count (default 0), bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL. ⚡ NÃO tem "user" embutido no /activities (só o /feed e /activities/search embutem, via FeedItemResponse).

FeedItemResponse (S36 — NOVO): herda de ActivityResponse e expõe o autor em DUAS chaves:
python

class FeedItemResponse(ActivityResponse):
    author: UserPublic = Field(validation_alias="user")
    user: UserPublic = Field(validation_alias="user")  # [Sessão 36]

    author — campo legado, lido pelo web.

    user — campo novo, lido pelo mobile (Activity.fromJson).

    Ambos apontam para o mesmo Activity.user do ORM via validation_alias. Redundância intencional (UserPublic tem 4 campos, custo desprezível).

    O backend já carrega o autor via selectinload(Activity.user) — sem mudança no service.

GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> (auth: Bearer JWT) — S32. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro (sem envelope). Paginação client-side.

GET /users/{user_id} (auth: Bearer JWT) — S32. Retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email, avatar_url, created_at, is_following. Para o perfil PRÓPRIO, usar GET /auth/me (UserResponse completo).

GET /auth/me — UserResponse completo: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }. NÃO é /users/me (esse devolve 422).

GET /activities/search?q=<min 2>&limit=<1..100>&offset=<>=0> (auth: Bearer JWT) — S10. Busca em title ILIKE %q% ou description ILIKE %q%. Visibilidade: dono OU seguido (mesma regra do feed). Retorna list[FeedItemResponse] (agora com author E user — bônus da S36). Rate limit: 20/min por IP.

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21. Permissão: dono OU seguidor do dono. Caso contrário, 404. format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id><type>.csv". 1 header + 1 linha. Funciona com/sem rota. format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo<id><type>.gpx". S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. ISO 8601 UTC. Exige rota → 404 se route IS NULL. format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22. Auth: self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto. format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota). Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

POST /activities/upload (auth: Bearer JWT) — S31. multipart/form-data: file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120, nullable), activity_type (opcional, string, nullable), description (opcional, string, nullable). Sucesso: 201 com ActivityResponse. Erro: 422 HTTPValidationError (.detail tratado pelo _extractMessage do mobile). Rate limit: 10/hora por IP (slowapi; 429). Parse síncrono, ~1–3s.

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.
GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5. S30: NÃO inclui avg_pace_s_per_km em nenhum shape — pace é derivado no front (computePace).

Janelas (S17/S18/S20):
period	compare	janela
all	qualquer	null
90d	prev (default)	[now-180d, now-90d)
90d	yoy	[now-455d, now-365d)
1y	prev	[now-730d, now-365d)
1y	yoy	[now-730d, now-365d) (coincide)

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404. Params: summary aceita activity_type opcional; weekly aceita weeks (1..52, default 8); monthly aceita months (1..24, default 6); by-type aceita period (default all) e compare (default prev). ⚡ O by-type do web usa period=all default; o mobile S33/S34 usa period=90d (com delta).

POST /users/{user_id}/follow — 204. DELETE /users/{user_id}/follow — 204. (S19/S20; consumidos pelo mobile na S34.)
GET /users/{user_id}/followers?limit&offset — list[UserPublic]. (S19/S20)
GET /users/{user_id}/following?limit&offset — list[UserPublic]. (S19/S20; usado pelo isFollowing do mobile na S34.)
GET /users/search?q=<min 2 chars>&limit — list[UserPublic]. Rate limit 20/min. (S19/S20; consumido pelo mobile na S35.)

⚡ NÃO existe GET /users/{id}/is-following. O cliente (web desde S19/S20; mobile desde S34) INFERE via GET /users/{meId}/following e checa se o alvo está na lista. Se o backend ganhar o endpoint, é só trocar a chamada em ApiClient.isFollowing.

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–36 commitadas e pushadas. HEAD == origin/main == dba8594. Working tree limpo.
Pendente: este handoff.

Primeira ação da Sessão 37 (REGRA S27a — handoff primeiro)
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 36"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 36 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)

[Sessão 37 — primeira ação] Abrir PowerShell via Win+R → powershell (NÃO abrir de dentro do VS Code / Windows Terminal).
powershell

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:
powershell

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 36"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 37 — primeira ação] Sanidade de build
powershell

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 37 — primeira ação] Docker + pytest local
powershell

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432

Se o prompt já mostra (venv), PULE a linha abaixo:
powershell

.\venv\Scripts\Activate.ps1

powershell

python -m pytest -q
ruff check .

Esperado: 173 passed, ruff limpo, container Up (healthy).

[Sessão 37 — primeira ação] Detecção de versão em produção (front — Vercel)
⚡ Sempre -UseBasicParsing. ⚡ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24). ⚡ REGRA S29b: o hash servido pelo Vercel não bate com o build local.
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
# REGRA S36b: bundle é minified (uma linha). Usar [regex]::Matches, não Select-String.
$chunks = [regex]::Matches($idx.Content, 'assets/(\w+)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }

Esperado no estado atual (S36): web inalterado desde S30 — index-CJjOEm0V.js, ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, RouteMap-CXXXy7Mv.js, leaflet-Bw7RoR_1.js, recharts-DI5KUTLO.js, rolldown-runtime-hePW80VL.js.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$token = $login.access_token
$h = @{ Authorization = "Bearer $token" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$meId = $me.id

[Sessão 37 — validação do FeedItemResponse com user (NOVO S36)]
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$feed = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/feed?limit=3" -Headers $h
Write-Host "itens no feed: $($feed.Count) (esperado: >= 1)"
$first = $feed[0]
Write-Host "tem author? $($null -ne $first.author) (esperado: True)"
Write-Host "tem user?   $($null -ne $first.user)   (esperado: True)"
Write-Host "author.id == user.id? $($first.author.id -eq $first.user.id) (esperado: True)"
Write-Host "author.username: $($first.author.username)"
Write-Host "user.username:   $($first.user.username)"

Esperado: tem author? True, tem user? True, author.id == user.id? True, author.username == user.username == produser.

Detecção de versão em produção (backend S26 — GPX com <time> por ponto)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$aid = "01a1b36a-0951-71e8-9044-c55c71558441"
$resp = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$aid/export?format=gpx" -Headers $h -UseBasicParsing
$times = [regex]::Matches($resp.Content, '<time>([^<]+)</time>')
$n = $times.Count
$distinct = ($times | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique).Count
Write-Host "pontos com <time>: $n"
Write-Host "<time> distintos: $distinct"
# ⚡ REGRA S36a: MatchCollection[-1] NÃO funciona no PS 5.1. Usar $times.Count - 1.
Write-Host "primeiro: $($times[0].Groups[1].Value)"
Write-Host "ultimo:   $($times[$times.Count - 1].Groups[1].Value)"
if ($distinct -le 1 -and $n -gt 1) {
  Write-Host "S26 AINDA NAO NO AR (todos iguais)."
} elseif ($n -gt 1) {
  Write-Host "S26 NO AR: $distinct/$n distintos."
}

Esperado agora: 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z.

[Sessão 37 — validação do perfil + stats + follow via API] (S34)
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }
$me = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers $h
$prod2 = "01a141e7-5ea4-7600-8959-19145475ad0a"
$user = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2" -Headers $h
Write-Host "Prod2.username: $($user.username)"
Write-Host "Prod2 tem email? $($null -ne $user.email) (esperado: False)"
$following = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$($me.id)/following?limit=100&offset=0" -Headers $h
$isFollowing = $false
foreach ($u in $following) { if ($u.id -eq $prod2) { $isFollowing = $true } }
Write-Host "prod segue Prod2? $isFollowing (esperado: True)"
$summary = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$prod2/stats/summary" -Headers $h
Write-Host "Prod2 summary.total_activities: $($summary.total_activities) (esperado: 2)"

[Sessão 37 — validação da busca de usuários + atividades (S35/S36)]
powershell

$body = "username=prod@rumo.com&password=senha12345"
$login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body
$h = @{ Authorization = "Bearer $($login.access_token)" }

# Usuários
$users = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/search?q=pro&limit=20" -Headers $h
Write-Host "users q=pro: $($users.Count) (esperado: 1 — Prod2)"

# Atividades (S36) — usa FeedItemResponse, deve ter author E user
$acts = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/activities/search?q=caminhada&limit=20" -Headers $h
Write-Host "atividades q=caminhada: $($acts.Count) (esperado: >= 1)"
if ($acts.Count -gt 0) {
  $a = $acts[0]
  Write-Host "primeira atividade tem author? $($null -ne $a.author) (esperado: True)"
  Write-Host "primeira atividade tem user?   $($null -ne $a.user)   (esperado: True)"
  Write-Host "author.id == user.id? $($a.author.id -eq $a.user.id) (esperado: True)"
}

Ruff (backend)
powershell

cd D:\Rumo\backend

Se o prompt já mostra (venv), pule:
powershell

.\venv\Scripts\Activate.ps1

powershell

ruff check .

Recuperação de arquivo corrompido (lição S21)
powershell

cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>

Se o último commit for anterior à mudança quebrada:
powershell

git restore <arquivo>

Se a versão quebrada JÁ foi commitada:
powershell

git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22 + S26c)
powershell

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"

Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy. Se rota no ar mas retorna 422, ver o BODY do erro:
powershell

try {
  Invoke-WebRequest -Uri "<url>" -Headers $h -UseBasicParsing | Out-Null
} catch {
  $resp = $_.Exception.Response
  $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
  Write-Host "STATUS $($resp.StatusCode)"
  Write-Host $reader.ReadToEnd()
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b+S36b)
powershell

$html = Invoke-WebRequest -Uri "https://rumo-wheat.vercel.app" -UseBasicParsing
$m = [regex]::Match($html.Content, 'src="(/assets/index-[^"]+\.js)"')
$idxUrl = "https://rumo-wheat.vercel.app" + $m.Groups[1].Value
Write-Host "index servido: $($m.Groups[1].Value)"
$idx = Invoke-WebRequest -Uri $idxUrl -UseBasicParsing
# REGRA S36b: bundle minified é uma linha só. Usar [regex]::Matches.
$chunks = [regex]::Matches($idx.Content, 'assets/(ActivityDetailPage|RouteMap|ProfilePage|SearchPage)-[A-Za-z0-9_-]+\.js')
$chunks | ForEach-Object { Write-Host $_.Value }

Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. ⚡ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.

Diagnóstico de save de arquivo (lição S25 + S32 + S33 + S34 + S36)
Depois de salvar, ANTES de commitar:
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
Write-Host "=== [6] hash do HEAD (path relativo a RAIZ do repo!) ==="
git rev-parse HEAD:<path/relativo/a/raiz/do/repo>

Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou. Se [5] != [6] e [4] mostra ' M' → save pegou, pode commitar.

⚡ REGRA S34a: o git rev-parse exige path relativo à raiz do repo (mobile/lib/main.dart), não ao CWD (lib/main.dart). O git hash-object aceita CWD.
Nota S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS". Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b.
Nota S32a/S32b/S33a/S36d: -SimpleMatch 'class X' casa 'class Xxx' (prefixo). -SimpleMatch '_X' casa menções em //. -SimpleMatch 'a|b' NÃO é alternância. Para contagem exata/alternância, usar -Pattern (sem -SimpleMatch) com regex ancorado.
Nota S33b/S34b: o "esperado" de qualquer Select-String é piso/faixa, nunca exato sem contagem real. Mesmo faixa pode errar (S34: '/user/:id' ≥2, veio 1).

Contornar editor que não salva (REGRA S31c + S36f)
Se Select-String do disco mostrar conteúdo antigo depois do save do editor:
powershell

cd D:\Rumo\mobile
$content = @'
// [Sessão N] conteúdo completo do arquivo aqui (SEM PLACEHOLDER — REGRA S36g)
'@
[System.IO.File]::WriteAllText("D:\Rumo\mobile\lib\pages\arquivo.dart", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "total de linhas: $((Get-Content -Encoding UTF8 'D:\Rumo\mobile\lib\pages\arquivo.dart').Count)"

O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.

Solução para lint unnecessary_overrides em AutomaticKeepAliveClientMixin (S36e):
// ignore_for_file: unnecessary_overrides na LINHA 1 do arquivo. NÃO usar // ignore: local (posicionamento frágil + duplicate_ignore se misturar). O super.build(context) no build é OBRIGATÓRIO (@mustCallSuper).

Remover linha(s) de um arquivo via PowerShell (S36 — cirúrgico, sem reescrever):
powershell

$path = "D:\Rumo\mobile\lib\pages\search_page.dart"
$lines = Get-Content -Encoding UTF8 $path
$filtered = $lines | Where-Object { $_.Trim() -ne "// ignore: unnecessary_overrides" }
[System.IO.File]::WriteAllLines($path, $filtered, [System.Text.UTF8Encoding]::new($false))

Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)
ERRADO — Content é string, não byte[]:
powershell

[System.IO.File]::WriteAllBytes($path, $resp.Content)

CERTO (texto UTF-8):
powershell

[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($resp.Content))

CERTO (bytes crus — ZIP, imagem):
powershell

$fs = [System.IO.File]::OpenWrite($path)
$resp.RawContentStream.Position = 0
$resp.RawContentStream.CopyTo($fs)
$fs.Close()

MELHOR para inspecionar GPX — sem arquivo, regex no Content:
powershell

$times = [regex]::Matches($resp.Content, '<time>([^<]+)</time>')

Upload de arquivo via PowerShell (lição S33)
Invoke-RestMethod -Form NÃO existe no PS 5.1 (só PS 6+). Para multipart/form-data, usar curl.exe (nativo no Windows 10+):
powershell

curl.exe -X POST "https://rumo-api-5s0b.onrender.com/activities/upload" -H "Authorization: Bearer $($login.access_token)" -F "file=@D:\caminho\arquivo.gpx" -F "title=Titulo opcional"

Verificar busca de usuários + atividades no Chrome (S36 — NOVO)
powershell

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d chrome

Login como prod@rumo.com. Tocar na lupa no AppBar do feed → /search com 2 abas.

    Aba Usuários: digitar "pro" → Prod2.

    Aba Atividades: digitar "caminhada" → atividades.

    Alternar 3× → estado preservado nas duas abas.
    ⚡ REGRA S34c/S36c: se a tela mostrar o perfil com "Deixar de seguir" ou "Estatísticas", você está no /user/:id (UserProfilePage), não no /feed ou /search. Confirmar (a) usuário logado, (b) URL colada, (c) restart do flutter run após mudança em main.dart.

SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) Duas pastas de venv — .venv removida. Única venv é backend\venv.
(FECHADA na S20) Pylance reclamando de imports — .vscode/settings.json aponta para backend/venv.
(FECHADA na S25) RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy() — RouteMap agora é lazy no ActivityDetailPage.
(FECHADA na S26) to_gpx não emite <time> por <trkpt> — agora emite quando raw_track_points está disponível e alinhado.
(FECHADA na S28) PreviousDelta mostrava só 3 das 5 métricas — PreviousDelta agora renderiza as 5.
(FECHADA na S29) downloadActivityExportBulk retornava void — agora devolve { entryCount }.
(FECHADA na S30) Delta de Pace no PreviousDelta está fora de escopo — DeltaLine ganhou lowerIsBetter.
(FECHADA na S31) Mobile não tem upload GPX/FIT — POST /activities/upload consumido pelo ApiClient.uploadActivity + UploadPage + FAB no feed.
(FECHADA na S32) Mobile não tem perfil nem "minhas atividades" — GET /activities?user_id= consumido + ProfilePage + bottom nav via StatefulShellRoute.
(FECHADA na S32) setState() called after dispose no feed_page.dart — 4 if (!mounted) return; + if (mounted) setState no finally.
(FECHADA na S32) _ActivityCard e _Metric duplicados entre feed e perfil — extraídos para widgets/activity_card.dart.
(FECHADA na S32) GET /activities não embute user; ActivityCard cai em "Usuário" no perfil — resolvido no mobile via authorUsernameOverride (S33/S34).
(FECHADA na S33) Mobile não tem stats agregadas no perfil — GET /users/{id}/stats/summary + by-type consumidos, StatsCards + ByTypeList + delta com lowerIsBetter.
(FECHADA na S33) format.dart em lib/lib/ dispara avoid_relative_lib_imports — movido para lib/utils/.
(FECHADA na S34) Mobile não tem perfil de terceiro nem follow — GET /users/{id} + POST/DELETE /users/{id}/follow + GET /users/{id}/following consumidos pelo ApiClient + UserProfilePage + rota /user/:id.
(FECHADA na S34) UserPublic local de activity.dart tem avatarUrl que o backend não devolve — User novo (user.dart) nasceu sem avatarUrl. O UserPublic antigo de activity.dart mantém o campo — dívida cosmética registrada abaixo.
(FECHADA na S35) Mobile não tem busca de usuários — GET /users/search consumido pelo ApiClient.searchUsers + UserSearchPage + rota /search.
(FECHADA na S35) onAuthorTap no card do feed estava implementado mas ninguém passava (S34) — FeedPage passa onAuthorTap condicional.
(FECHADA na S36) S35a: GET /feed não embutia user. Na verdade embutia, com chave author. Adicionado user ao lado de author no FeedItemResponse. Mobile passou a funcionar sem mudança. Web intacto.
(FECHADA na S36) Mobile não tem busca de atividades — GET /activities/search consumido pelo ApiClient.searchActivities + SearchPage (2 abas) + rota /search.
(CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.
(CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.
(CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.
(CONHECIDA — Sessão 17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.
(CONHECIDA — Sessão 17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. NÃO é bug. (Atualização S33: com a sintética de 2026-06-01, o previous de walk em 90d agora vem preenchido.)
(CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática.
(CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk". Testes usam activity.activity_type.value dinâmico.
(CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. YAGNI por enquanto.
(CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries. Aceitável para export raro.
(CONHECIDA — Sessão 22) Export em lote é self-only. Decisão de privacidade.
(CONHECIDA — Sessão 23) downloadActivityExportBulk valida from > to client-side. Dupla validação proposital.
(CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).
(CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado desde antes.
(CONHECIDA — Sessão 26) <time> no GPX inclui microssegundos porque o gpxpy serializa datetime.isoformat(). Observação S31: em prod agora vem truncado em segundos. Contrato intacto.
(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Coberto por teste.
(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. Renomeação de referência cruzada no __vite__mapDeps (REGRA S28b).
(CONHECIDA — Sessão 29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Sentinel 0xFFFF sinaliza falha (retorna -1, fail-open).
(CONHECIDA — Sessão 29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs).
(CONHECIDA — Sessão 29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.
(CONHECIDA — Sessão 30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX.
(CONHECIDA — Sessão 30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0, resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero.
(CONHECIDA — Sessão 31) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → ApiException; o app NÃO faz logout automático.
(CONHECIDA — Sessão 31) Mobile: uploadActivity valida path == null → readAsBytes(), cobre web. No Android, path costuma vir preenchido — não testado em dispositivo físico.
(CONHECIDA — Sessão 31) Mobile: rate limit 10/h do /activities/upload não foi testado explicitamente (429).
(CONHECIDA — Sessão 31) Mobile: activity_type fora da UI do upload na S31 — o backend infere pelo arquivo.
(CONHECIDA — Sessão 31) O commit a83ed82 foi feito pelo usuário/VS Code com a versão inicial; 71a00d4 refinou upload_page.dart e api.dart. Não vale rebase/squash.
(CONHECIDA — Sessão 31) file_picker 13.3.3 trouxe 11 deps novas.
(CONHECIDA — Sessão 32) GET /activities (backend) retorna ActivityResponse[] SEM o campo "user" embutido. O GET /feed embute (FeedItemResponse com author + user desde S36). Resolvido no mobile via authorUsernameOverride (S33 no self, S34 no terceiro).
(CONHECIDA — Sessão 32) UserPublic local em activity.dart tem avatarUrl que o UserPublic do backend NÃO tem. Dívida cosmética.
(CONHECIDA — Sessão 32) ProfilePage usa Future.wait([/auth/me, /activities?user_id=...]) em paralelo. Na S33, os stats foram SEPARADOS (_loadStats com Future.wait próprio). O UserProfilePage (S34) segue o mesmo padrão.
(CONHECIDA — Sessão 32) ProfilePage paginação: "Carregar mais" (botão), não scroll infinito. Regra "se voltou < limit, acabou". Conta prod tem 8 atividades — o "Carregar mais" NÃO foi exercitado.
(CONHECIDA — Sessão 32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id, /user/:id e /search ficam FORA do shell (sem bottom nav). Decisão intencional.
(CONHECIDA — Sessão 32) O FAB de upload some quando o usuário está na aba Perfil. Intencional (upload é ação do feed).
(CONHECIDA — Sessão 33) period/compare FIXOS no mobile (90d/prev). O web tem filtros de UI. Filtros ficam pra S37+.
(CONHECIDA — Sessão 33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web).
(CONHECIDA — Sessão 33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 em vez de text-green-600/red-600.
(CONHECIDA — Sessão 33) O _formatThousands é inline (sem intl).
(CONHECIDA — Sessão 33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético. Fica como dado de teste.
(CONHECIDA — Sessão 33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Usar curl.exe.
(CONHECIDA — Sessão 33) Weekly/monthly charts no mobile ficam pra S37+ (recharts no web; no mobile, seria fl_chart ou similar — decisão de dependência).
(CONHECIDA — Sessão 34) O backend NÃO tem GET /users/{id}/is-following. O cliente infere via GET /users/{meId}/following?limit=100.
(CONHECIDA — Sessão 34) O _activitiesForbidden do UserProfilePage é heurístico: se listActivities voltou vazio E isFollowing==false E não é self → assume 403.
(CONHECIDA — Sessão 34) O toggle follow/unfollow altera o backend real (não é mock). Testado nos dois sentidos e restaurado.
(CONHECIDA — Sessão 34) A inferência isFollowing com limit=100 só enxerga os primeiros 100 follows.
(CONHECIDA — Sessão 35) O debounce da busca é manual (Timer de 300ms) em cada aba do SearchPage, não um Hook/utilitário reusável. Se aparecer terceira tela de busca, extrair pra utils/.
(CONHECIDA — Sessão 35) O _query do SearchPage não vai pra URL. O web usa searchParams.set('q', ...) pra deep-link; no mobile é fluxo efêmero (YAGNI).
(CONHECIDA — Sessão 35) O guard de 2 chars está DUPLICADO: client-side (ApiClient.searchUsers / searchActivities: if (len < 2) return []) e server-side (422). Dupla validação proposital.
(CONHECIDA — Sessão 35) Os 4 avisos [flutter_map] no console do Chrome são informativos (tile server público do OSM). Formalizar tile server próprio para produção.
(CONHECIDA — Sessão 36) O // ignore_for_file: unnecessary_overrides na linha 1 do search_page.dart suprime o lint no arquivo INTEIRO. Se aparecer override realmente vazio no futuro, o lint não vai avisar. Trade-off aceitável (arquivo pequeno, overrides justificados pelo mixin).
(CONHECIDA — Sessão 36) A aba Usuários do SearchPage recebe autoFocus na 1ª carga; a aba Atividades não. Decisão: evita dois teclados brigando quando o usuário troca de aba. Se virar problema de UX, reavaliar.
(CONHECIDA — Sessão 36) SearchPage usa DefaultTabController + TabBarView. Cada aba tem seu próprio estado (query, resultados, scroll) via AutomaticKeepAliveClientMixin. Trocar de aba NÃO perde estado.
(CONHECIDA — Sessão 36) O main.dart mudou só 2 linhas (import + classe na rota /search). Nada da bottom nav ou do shell foi tocado.
(Oportunidade — S18–S36) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.
(Oportunidade — S19–S36) Stats públicas só quando viewer segue o alvo.
(Oportunidade — S22–S36) Export em lote no mobile (paridade com web S21/S22/S29).
(Oportunidade — S30) Testes unitários do DeltaLine no web e no mobile (puro, testável).
(Oportunidade — S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.
(Oportunidade — S31) Testar upload em Android físico/emulador.
(Oportunidade — S31) UI dedicada para 429 (rate limit) com cooldown visual.
(Oportunidade — S31) activity_type como dropdown opcional na UploadPage.
(Oportunidade — S33) Filtros de period/compare na UI do perfil (S37+).
(Oportunidade — S33) Weekly/monthly charts no perfil (S37+).
(Oportunidade — S34) Lista de seguidores/seguindo no UserProfilePage (S37+).
(Oportunidade — S34) Export no mobile (unitário + lote) — S37.
(Oportunidade — S34) Editar perfil (peso, altura, etc.) — requer PUT /users/me ou similar, não existe — S37+.
(Oportunidade — S34) Alinhar UserPublic local de activity.dart (remover avatarUrl) — S37+.
(Oportunidade — S34) Endpoint GET /users/{id}/is-following no backend — S37+.
(Oportunidade — S36) Deep-link ?q= na busca mobile (se aparecer necessidade).
(Oportunidade — S36) Extrair o debounce manual (Timer 300ms) para um helper utils/debounce.dart se aparecer terceira tela de busca.
(Oportunidade — S36) Testar busca de atividades com termo vazio/1 char (guard client-side + 422 backend).
(Oportunidade — S36) Tile server próprio do OSM (formalizar para produção).

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 37 e além)

Sessão 36 fechada. Busca de atividades entregue. S35a fechada. Backend com 173 testes, web intocado, mobile com SearchPage 2 abas. Mobile subiu de ~85% para ~88% de cobertura.

Primeira ação obrigatória da Sessão 37 (REGRA S27a)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 37 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 36, push, confirmar HEAD == origin/main.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (173 passed).

    Detecção de versão em produção (front Vercel + back Render S26 + FeedItemResponse.user).

Rota travada para a Sessão 37: export no mobile + lista de seguidores/seguindo

Escolha OPÇÃO 1 (recomendada): Export no mobile (unitário + lote). Paridade com web S21/S22/S29. Requer: ver web/src/api/activities.ts (já temos downloadActivityExport e downloadActivityExportBulk), web/src/components/ (botões de export), e o padrão de download no mobile (file_picker? share_plus? path_provider?). O ApiClient mobile precisa de downloadActivityExport(id, format) e downloadActivityExportBulk(format, from, to) que baixam bytes e salvam/abrem. Backend já tem tudo (S21/S22), zero mudança backend.

Escolha OPÇÃO 2: Lista de seguidores/seguindo no UserProfilePage. O web tem abas followers/following. Requer: web/src/pages/ProfilePage.tsx (parte de followers/following), web/src/api/follows.ts. Backend já tem GET /users/{id}/followers e GET /users/{id}/following. Zero mudança backend.

Escolha OPÇÃO 3: Filtros de period/compare na UI do perfil (paridade com web S17/S20). Requer mexer em profile_page.dart + user_profile_page.dart + stats_cards.dart/by_type_list.dart. Backend já suporta.

Escolha OPÇÃO 4: Weekly/monthly charts no perfil (fl_chart ou similar). Decisão de dependência nova.

Escolha OPÇÃO 5: Editar perfil (peso/altura). Requer endpoint novo PUT /users/me no backend + EditProfilePage no mobile.

Escolha OPÇÃO 6: Encerrar features e partir para release (tile server próprio, ícone, identidade, build Android/iOS, submissão).

Recomendação: S37 = OPÇÃO 1 (export mobile) + OPÇÃO 2 (followers/following). S38 = OPÇÃO 3 + OPÇÃO 4. S39 = OPÇÃO 5 (editar perfil). S40 = OPÇÃO 6 (release). ~4-6 sessões para o MVP em loja.

Recomendação final para a Sessão 37
Rodar Fase 0 completa (com handoff S36 commitado primeiro). Se tudo verde, atacar OPÇÃO 1 (export mobile): pedir os arquivos do web, decidir a lib de download (file_picker tem saveFile? path_provider? share_plus?), e implementar ApiClient.downloadActivityExport + botão no ActivityDetailPage. Depois OPÇÃO 2 (followers/following no UserProfilePage).

Antes de codar a S37: Fase 1 precisa pedir os arquivos do web (web/src/api/activities.ts — a parte de export; web/src/components/ — os botões de export; mobile/lib/pages/activity_detail_page.dart — onde o botão vai). Verificar se file_picker no mobile tem saveFile ou se precisa de outra lib (path_provider, share_plus, url_launcher).

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."
Na S22: "sempre vamos seguir o que você recomendar".
Na S23: "vamos deixar algumas coisas acordadas, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."
Na S24: confirmou "tudo como esperado" duas vezes.
Na S25 (abertura): reforçou os mesmos acordos. Tolerou 3 tropeços.
Na S26 (abertura): reforçou os mesmos acordos. Tolerou 2 tropeços.
Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a.
Na S28 (abertura): handoff S27 já commitado. Fase 1 revelou escopo real (1 arquivo, não 6).
Na S29 (abertura): handoff S28 já commitado. Fase 1 revelou 2 arquivos. Entreguei activities.ts, o usuário colou erro do ESLint no-useless-assignment — corrigi, REGRA S29d.
Na S30 (abertura): handoff S29 já commitado. Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. 1 tropeço (contagem "5x vs 6x", REGRA S29c).
Na S31 (abertura): handoff S30 já commitado (3a154b1). Fase 0 limpa. Tropeços: (1) file_picker 13.x mudou a API (REGRA S31b); (2) o editor falhou 3 vezes em salvar o upload_page.dart (REGRA S31c); (3) teste manual revelou que na web file_picker retorna path == null mas readAsBytes() funciona; (4) commit duplicado (a83ed82 + 71a00d4).
Na S32 (abertura): handoff S31 já commitado (f39820f). Fase 0 limpa. Fase 1 revelou 5 achados. Entrega incremental: 6 arquivos, 4 builds. 5 desvios de contagem (S32a–S32d). Validação manual no Chrome: 11/11.
Na S33 (abertura): handoff S32 já commitado (919ccea). Fase 0 limpa. Fase 1 revelou 6 achados. Entrega incremental: 6 arquivos, 6 builds + 1 fix. 2 desvios de contagem (S33a, S33b). Validação manual no Chrome: 12/12.
Na S34 (abertura): handoff S33 já commitado (ce09eb6). Fase 0 limpa (5 blocos). Fase 1 revelou 8 achados. Entrega incremental: 4 arquivos, 4 builds. 2 desvios de contagem (S34a, S34b) + 1 achado operacional (S34c). Validação manual no Chrome: 9/9.
Na S35 (abertura): handoff S34 já commitado (2b312ec). Fase 0 limpa. Fase 1 revelou 8 achados. Entrega incremental: 5 arquivos, 4 builds. 3 desvios de contagem. Validação manual no Chrome: 8/8 + achado S35a (que era erro do handoff: o /feed JÁ embutia o autor, com chave author).
Na S36 (abertura): handoff S35 já commitado (8bff66b). Fase 0 limpa (5 blocos). Fase 1 revelou 8 achados, incluindo o crítico: o /feed já devolvia author, só que o mobile lia user. Entrega incremental: 4 arquivos (1 novo backend, 1 novo teste backend, 1 editado mobile, 1 novo mobile), 3 commits. MUITOS tropeços:

    $times[-1] no PS 5.1 (S36a) — erro no meu comando de validação, o teste "passou" por engano.

    Select-String -SimpleMatch 'a|b|c' (S36d, reincidência) — erro no meu bloco de validação.

    Placeholder em here-string (S36g) — o WriteAllText gravou COLE O CONTEÚDO AQUI no disco. Recuperado porque era untracked.

    3 tentativas de posicionamento do // ignore: — a solução correta era // ignore_for_file na linha 1, não // ignore: local. S36e.

    Editor falhou 2× em salvar search_page.dart (S36f) — WriteAllText resolveu.

    2 desvios de contagem (S32c/S33b): test_feed.py tinha 7 testes, não 6 (172→173); "esperado 0" de símbolos antigos no main.dart deu 3 (todos em comentários).

    1 desvio de tela (S36c): a primeira validação manual no Chrome mostrou o UserProfilePage do Prod2, não o feed. O "bug" não existia — era tela errada.
    Validação manual no Chrome (S36): 7/7 + 1 iteração no feed (o onAuthorTap funcionou depois de refresh).

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.
Acordo novo na S32: manter o processo da S21–S31. Concretamente:
Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.
Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar.
Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.
Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.
Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> (com path relativo à RAIZ do repo — REGRA S34a) + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b + S34b: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c).
Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local. REGRA S34c: no mobile, confirmar login/URL/restart antes de declarar bug de tela.
Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).
Regras novas da S36 (Seção 0, itens 46–52): S36a (MatchCollection[-1]), S36b (bundle minified = regex), S36c (confirmar tela pela URL), S36d (Select-String -SimpleMatch com |, CRÍTICA), S36e (// ignore_for_file na linha 1), S36f (editor falhou 2x), S36g (here-string com conteúdo real).

O que funcionou nas S21–S36 (manter):

    Ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão).

    Disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33, S34, S35, S36).

    Consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor, sessão do localStorage, tela errada, placeholder em here-string) na hora e corrigir/registrar, sem contornar.

    A S36 acrescentou: parar e não fingir validação quando o flutter analyze dá warning (mesmo cosmético), quando o editor não salva, quando a screenshot mostra tela errada. Nunca commitar com flutter analyze/pytest/npm run lint não-verde.

PERCENTUAL DE PRONTIDÃO DO PROJETO (fim da Sessão 36)

Backend — ~97%

    173 testes verdes, ruff limpo.

    Todos os endpoints do MVP funcionam em prod (auth, atividades CRUD, track, upload GPX/FIT, export CSV/GPX unitário + lote, stats summary/weekly/monthly/by-type, follows, followers/following, search usuários, search atividades).

    Falta: endpoint PUT /users/me (editar perfil — peso/altura), GET /users/{id}/is-following (elimina inferência no client), índice GIN gin_trgm_ops em title/description (escala de busca), paginação real no /activities (envelope), tile server do OSM (não é backend nosso, é infra).

    Backend não tem nenhum bloqueador para MVP.

Web — ~92%

    Build/lint limpos, 824 modules, bundle estável desde S30.

    Todas as telas do MVP: login, feed, detalhe, perfil self, perfil de terceiro, busca (usuários + atividades), upload, export unitário + lote.

    Falta: filtros de period/compare na UI (S37+), weekly/monthly charts mais elaborados (recharts já está lá, mas é básico), editar perfil (depende de endpoint).

    Web não tem nenhum bloqueador para MVP.

Mobile — ~88%

    flutter analyze limpo, SearchPage 2 abas funcionando, onAuthorTap no feed e na busca funcionando, 7/7 na validação manual.

    Telas: login, feed, detalhe, perfil self, perfil de terceiro, busca (usuários + atividades), upload, bottom nav.

    Falta: export (unitário + lote), lista de seguidores/seguindo, filtros de period/compare, weekly/monthly charts, editar perfil, refresh token / logout 401, upload em Android físico (só testado no Chrome web), tile server próprio (mesma dívida do backend), ícone/identidade visual, build Android/iOS assinado.

    Mobile tem bloqueadores não-código para release (loja, ícone, assinatura).

Bloqueadores não-código (para MVP em loja)

    Tile server próprio do OSM (hoje usa o público; não escala para produção).

    Ícone + identidade visual do app.

    Conta de desenvolvedor Google Play (~US25uˊnico)e∗∗AppleDeveloper∗∗( US25uˊnico)e∗∗AppleDeveloper∗∗( US 99/ano).

    Build assinado (Android keystore + iOS provisioning profile).

    Política de privacidade e Termos de uso (exigidos pelas lojas).

    Screenshots e descrição para as lojas.

    Testes em dispositivo físico (Android e iOS) — hoje só Chrome/web.

Consolidado: ~91% (média ponderada: backend 0.3 × 0.97 + web 0.3 × 0.92 + mobile 0.4 × 0.88 = 0.291 + 0.276 + 0.352 = 0.919).

Estimativa de sessões restantes para o MVP em loja: 4–6 sessões.

    S37: export mobile + followers/following.

    S38: filtros period/compare + charts weekly/monthly.

    S39: editar perfil (backend PUT + mobile UI).

    S40: tile server próprio + ícone + identidade + build assinado Android.

    S41: submissão Google Play + correções.

    S42: submissão App Store + correções (se for iOS também).