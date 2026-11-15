HANDOFF da Sessão 33 (seções 0–9)

Vou entregar o handoff completo no formato do HANDOFF S32 (que você colou no início desta sessão), com as atualizações da S33. Como é um arquivo longo (~800 linhas), vou entregar em bloco único, sem cerca markdown envolvendo (REGRA S25e), pra você colar no editor como D:\Rumo\docs\HANDOFF.md (substituindo o atual).

Antes de colar, 2 perguntas de ajuste:

    A conta prod@rumo.com agora tem 8 atividades (7 + 1 sintética). No handoff, atualizo a Seção 2 ("Contas de teste") de 6 → 8, com nota da sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal, dentro da janela [now-180d, now-90d)). Confirma?

    As 2 lições novas (S33a, S33b) vão pra Seção 0 (regras de ouro). Confirma que eu registro como "reincidência do assistente" (é o honesto — eu violei regras que eu mesmo escrevi)?

    A S34 fica travada como "perfil de terceiro + follow" (Opção 2 da Seção 8 do handoff S32)? Recomendo que sim — é o próximo gap funcional, e o backend já tem GET /users/{id}, GET /users/{id}/stats/*, POST/DELETE /users/{id}/follow, GET /users/{id}/followers|following prontos desde a S19/S20. O mobile só precisa consumir. Confirma ou prefere outra rota?

Responde as 3 e eu entrego o handoff completo. Se preferir que eu entregue o handoff agora e você ajuste os 3 pontos depois, é só dizer "manda o handoff".
1 - sim, vamos fazer o que você recomendar, faça o handoff

Combinado. Handoff da Sessão 33 completo, seções 0 a 9, formato do HANDOFF S32, com as atualizações da S33 já incorporadas (8 atividades na conta prod, sintética registrada, lições S33a/S33b, S34 travada em perfil de terceiro + follow).

Cole o conteúdo abaixo em D:\Rumo\docs\HANDOFF.md (substituindo o atual). Sem cerca markdown envolvendo — o conteúdo inteiro é o arquivo.

HANDOFF — Rumo (backend + frontend + mobile) — Sessão 33

SEÇÃO 0 — LEIA PRIMEIRO (contexto operacional)

Regra de ouro para o assistente novo (leia antes de qualquer coisa)

VOCÊ NÃO TEM ACESSO AO DISCO DO USUÁRIO. Não existe "listar pasta", "abrir arquivo", "ver o repo". Toda informação chega por DUAS vias:

(a) o usuário cola o conteúdo de um arquivo via Get-Content -Encoding UTF8
(b) o usuário cola a saída de um comando de terminal

NUNCA invente caminho de arquivo. NUNCA diga "vou olhar o arquivo X". NUNCA reescreva um arquivo que você não recebeu nesta sessão. Se precisar de um arquivo, PEÇA e espere. Se a estrutura de pastas for necessária, PEÇA a saída de Get-ChildItem.

⚠️ REGRA S21 — nunca placeholder no código entregue. Não entregar bloco com # ... (resto inalterado ...). Se não tem o arquivo, peça.
⚠️ REGRA S21 — não adivinhar nomes de símbolos do projeto. Pedir o model/enum/schema antes de referenciar.
⚠️ REGRA S21 — git status antes de qualquer git restore/git checkout. git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo>.
⚠️ REGRA S22 — Invoke-WebRequest com -UseBasicParsing. Elimina o prompt de segurança do PS 5.1.
⚠️ REGRA S22 — validar deploy do Render antes de acusar bug no código. Depois de push, checar openapi.json para a rota nova antes de acusar 422/404.
⚠️ REGRA S23 — para validar bundle novo na Vercel, baixar o index-*.js e procurar o chunk dentro dele. Nunca procurar "ProfilePage-" direto no HTML.
⚠️ REGRA S24 — Vercel às vezes demora >90 s para o primeiro deploy após push. Se o hash antigo aparecer após 90 s, rodar o teste de novo. Não presumir bug.
⚠️ REGRA S25a — Select-String -SimpleMatch NÃO aceita | como alternância. Com -SimpleMatch, "a|b" busca a string literal a|b, não "a ou b". Para alternância, usar Select-String -Pattern "a|b" (sem -SimpleMatch), ou rodar separado por termo.
⚠️ REGRA S25b — quando lines[−1]forsuspeito,confirmarcomGet−Content∣Select−Object−LastN+Select−String−Pattern"<termo>"antesdeconcluir.Na~odar"OK"nem"corrompido"semevide^ncia.⚠®REGRAS25c—antesdepedirgitadd/gitcommitdeumarquivoqueousuaˊrioacaboudesalvar,EXIGIRooutputdoblocodevalidac\ca~oeESPERAR.⚠®REGRAS25d—otestedefinitivode"osavepegou"eˊgithash−object<arquivo>≠gitrev−parseHEAD:<arquivo>+gitstatus−−shortmostrarM<arquivo>.Segitstatus−−shortviervaziodepoisdesalvar,odiscoeˊigualaocommitado.Osavena~opegou.⚠®REGRAS25e—aoentregaroconteuˊdodeumarquivoparacolarnoeditor,entregarSEMcercamarkdownenvolvendo.Entregaroarquivointeirocomouˊnicotextodaresposta,seminstruc\co~esantes/depois.⚠®REGRAS26a—noPowerShell5.1,Invoke−WebRequest−UseBasicParsingdevolvelines[−1]forsuspeito,confirmarcomGet−Content∣Select−Object−LastN+Select−String−Pattern"<termo>"antesdeconcluir.Na~odar"OK"nem"corrompido"semevide^ncia.⚠R◯REGRAS25c—antesdepedirgitadd/gitcommitdeumarquivoqueousuaˊrioacaboudesalvar,EXIGIRooutputdoblocodevalidac\c​a~oeESPERAR.⚠R◯REGRAS25d—otestedefinitivode"osavepegou"eˊgithash−object<arquivo>=gitrev−parseHEAD:<arquivo>+gitstatus−−shortmostrarM<arquivo>.Segitstatus−−shortviervaziodepoisdesalvar,odiscoeˊigualaocommitado.Osavena~opegou.⚠R◯REGRAS25e—aoentregaroconteuˊdodeumarquivoparacolarnoeditor,entregarSEMcercamarkdownenvolvendo.Entregaroarquivointeirocomouˊnicotextodaresposta,seminstruc\c​o~esantes/depois.⚠R◯REGRAS26a—noPowerShell5.1,Invoke−WebRequest−UseBasicParsingdevolveresp.Content como STRING, não como byte[]. [System.IO.File]::WriteAllBytes(path, resp.Content) falha. Para texto UTF-8: [System.Text.Encoding]::UTF8.GetBytes(resp.Content).Parabytescrus(ZIP,imagem):resp.Content).Parabytescrus(ZIP,imagem):resp.RawContentStream.CopyTo(fileStream).ParainspecionarGPX/XML:regexdiretonofileStream).ParainspecionarGPX/XML:regexdiretonoContent.
⚠️ REGRA S26b — validar GPX em produção por regex é mais barato que gpxpy + arquivo temporário. Contar <time> distintos com regex no Content responde "o S26 está no ar?" em 3 linhas, sem env:TEMP nem WriteAllBytes. Usar gpxpy só quando precisar validar estrutura interna (eixos, hierarquia <trkseg>). ⚠️ REGRA S26c — Render free tier pode demorar >3 min para redeployar após push. Não é bug. Se a primeira validação em prod mostrar comportamento antigo, esperar 2 min e rodar de novo. Se após ~5 min continuar antigo, ir ao dashboard do Render → Manual Deploy. Não presumir bug no código antes de ~5 min. ⚠️ REGRA S27a — ao abrir sessão, commitar o handoff pendente ANTES de qualquer outra coisa. Se git status --short mostrar M docs/HANDOFF.md no início, esse é o handoff da sessão anterior ainda não commitado. Commitar primeiro, push, confirmar HEAD == origin/main, e SÓ ENTÃO rodar os demais blocos da Fase 0. ⚠️ REGRA S27b — a ordem dos blocos da Fase 0 é: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só começa depois do anterior verde. Se algum falhar, PARAR e mostrar ao usuário antes de seguir. ⚠️ REGRA S28a — antes de entregar código de feature, confirmar o escopo real pedindo TODOS os arquivos que o contrato toca, incluindo os "óbvios". O handoff pode estar desatualizado. ⚠️ REGRA S28b — quando o build gerar chunks com hash diferente do esperado mas TAMANHO idêntico, é renomeação de referência cruzada, não mudança de código. Não investigar como bug. ⚠️ REGRA S29a — ao contar entradas de um ZIP no client, usar EOCD com fail-open; ZIP64 fica de fora. Implementação em web/src/api/activities.ts → _countZipEntries(). ⚠️ REGRA S29b — o Vercel reescreve o hash dos chunks ao servir; o sinal de "bundle novo no ar" é o hash mudou vs sessão anterior, não "bate com o build local". Manter a checagem por __vite__mapDeps + leitura do conteúdo do chunk. ⚠️ REGRA S29c — ao declarar o "esperado" de um Select-String, contar as ocorrências reais no arquivo entregue antes de anunciar o número. Erro no esperado, não no código. (Reforçada na S32 e na S33 — ver S33b.) ⚠️ REGRA S29d — ESLint no-useless-assignment pega let x = -1; try { x = ... } catch { x = -1 }. Declarar sem inicializar (let entryCount: number;) quando try/catch (ou if/else) cobre todos os caminhos. ⚠️ REGRA S30a — Select-String -Pattern "TODO" casa case-insensitive "Todos" (e "TODOS"). Usar -CaseSensitive ou regex \bTODO\b. ⚠️ REGRA S30b — ao estender um componente genérico (DeltaLine) com semântica oposta, usar prop booleana default-false e testar os 4 cantos. Contrato: isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; ambos false = cinza (delta 0). Sinal matemático ("+"/"−") e percentual seguem o delta cru. ⚠️ REGRA S30c — handoff escrito com base em memória pode SUBESTIMAR o que existe no repo; a descoberta de código corrige para CIMA. No mobile, SEMPRE pedir Get-ChildItem + arquivos-chave antes de estimar esforço ou travar rota. ⚠️ REGRA S31a — em ambiente Windows sem Developer Mode, flutter pub add <plugin_nativo> instala mas avisa que o build vai falhar por symlink. Building with plugins requires symlink support. Please enable Developer Mode — start ms-settings:developers + ativar. Vale para qualquer plugin com código nativo. flutter analyze passa sem Developer Mode; flutter run/flutter build não. ⚠️ REGRA S31b — file_picker 13.x removeu FilePicker.platform, FilePickerResult, PlatformFile.size e PlatformFile.bytes. API nova: FilePicker.pickFiles() estático retorna List<PlatformFile> (vazio = cancelou); PlatformFile.length()/lengthSync() substituem .size; PlatformFile.readAsBytes() substitui .bytes. path continua existindo (String?) mas é null na web. Consultar o changelog antes de usar API de plugin. ⚠️ REGRA S31c — quando Select-String do disco mostrar conteúdo antigo depois do save do editor, contornar via WriteAllText no PowerShell imediatamente — não insistir no Ctrl+S. Sintomas: git status mostra M, mas Select-String do símbolo novo vem vazio; Get-Item mostra LastWriteTime desatualizado. Procedimento: here-string @' ... '@ + [System.IO.File]::WriteAllText(path, content, [System.Text.UTF8Encoding]::new(false)) + verificar com 3 Select-String.
⚠️ REGRA S32a — Select-String -SimpleMatch 'class X' casa PREFIXOS: 'class ActivityCard' casa 'class ActivityCard' e 'class ActivityCardMetric'. Para contar classe exata, usar -Pattern '\bclass X\b' (regex com word boundary) ou -Pattern 'class X ' (com espaço no fim).
⚠️ REGRA S32b — Select-String -SimpleMatch '_Simbolo' casa menções em COMENTÁRIOS também. Se o comentário de topo cita o símbolo antigo ("renomeado _ActivityCard → ActivityCard"), a contagem nunca vai a zero. Para contar ocorrências em código, filtrar linhas que não começam com // ou usar regex ancorado.
⚠️ REGRA S32c — ao anunciar "esperado ≈ N linhas", CONTAR as linhas do arquivo entregue antes de anunciar. Contagem mental falha consistentemente para baixo em arquivos com widgets aninhados (S32: anunciei ~260 num arquivo de 331; anunciei ~110/-30 num diff que foi +69/-4).
⚠️ REGRA S32d — nos Select-String de validação, o "esperado" é sempre PISO ou FAIXA, nunca número exato, a menos que eu tenha contado o output real do arquivo entregue. Se não contei, anunciar "≥ N" e aceitar qualquer valor ≥ N. Erro no esperado, não no código.
⚠️ REGRA S33a (NOVA) — reincidência da S25a na S33: entreguei um bloco de verificação com Select-String -SimpleMatch 'a|b' (esperando alternância). Veio 0; o código estava certo (flutter analyze verde). O próprio assistente violou a regra que escreveu. Para alternância, SEMPRE -Pattern 'a|b' (sem -SimpleMatch). Vale também para blocos de verificação que o assistente monta.
⚠️ REGRA S33b (NOVA) — reincidência da S32d na S33: anunciei "esperado 2" exato num Select-String que casava import package: (2 imports reais + 1 menção em comentário = 3). O certo era "esperado ≥2". Regra: em Select-String de validação, o "esperado" é SEMPRE piso/faixa, nunca exato, mesmo quando o número parece óbvio. O erro é no esperado, não no código.

O que é LOCAL vs. o que é PRODUÇÃO

LOCAL (máquina do usuário): D:\Rumo (repo git), D:\Rumo\backend (FastAPI + Postgres/PostGIS + Alembic + pytest), D:\Rumo\web (React 19 + Vite 8 + TypeScript + Tailwind + react-leaflet + recharts), D:\Rumo\mobile (Flutter). O assistente NÃO tem acesso a esses arquivos.

PRODUÇÃO (nuvem, acessível por HTTP): backend no Render (https://rumo-api-5s0b.onrender.com), frontend web na Vercel (https://rumo-wheat.vercel.app).

IMPORTANTE — usuário não tem ambiente local rodando. Fluxo: editar em D:\Rumo, rodar pytest localmente (Docker de teste na 5433), commitar, push, Render + Vercel redeployam, validar via HTTP em produção. Mobile roda em emulador/aparelho (Chrome/web nesta sessão), consumindo o mesmo backend Render — não tem "deploy mobile" separado.

DOCKER: instalado e funcional no Windows local. pytest -q local verde (166 passed ao fim da S33). Container de teste rumo_postgres_test na porta 5433.

⚠️ docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test" (com -a).

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
│ │ + test_export_bulk + test_follow + test_like + test_stats)
│ ├── _scratch/ (ignorado pelo git; s33_delta_test.gpx criado na S33)
│ ├── docker-compose.test.yml
│ ├── pytest.ini
│ └── requirements.txt
├── docs/HANDOFF.md
├── mobile/
│ ├── lib/
│ │ ├── main.dart (StatefulShellRoute + bottom nav desde S32)
│ │ ├── models/ (activity.dart, activity_track.dart, comment.dart,
│ │ │ stats.dart ← NOVO S33, user_me.dart ← NOVO S32)
│ │ ├── pages/ (activity_detail_page.dart, feed_page.dart,
│ │ │ login_page.dart, profile_page.dart ← EDITADO S33,
│ │ │ upload_page.dart ← NOVO S31)
│ │ ├── services/ (api.dart ← EDITADO S33, auth_service.dart)
│ │ ├── utils/ (format.dart ← NOVO S33, movido de lib/lib/ no
│ │ │ commit e15bedd)
│ │ └── widgets/ (activity_card.dart ← EDITADO S33,
│ │ │ activity_map.dart, by_type_list.dart ← NOVO S33,
│ │ │ like_button.dart, stats_cards.dart ← NOVO S33)
│ ├── pubspec.yaml (file_picker: ^13.3.3, go_router: ^18.1.2, name: rumo_mobile)
│ └── pubspec.lock
├── web/src/ (api/ assets/ components/ contexts/ hooks/ lib/ pages/ types/)
└── README.md

Como rodar comandos Flutter

Flutter em C:\Users\nasci\flutter (bin em ...\flutter\bin). Versões: Flutter 3.47.9 / Dart 3.13.7. Problema conhecido: mesmo com o bin no PATH, o PowerShell às vezes não reconhece flutter. Solução: & "C:\Users\nasci\flutter\bin\flutter.bat" <comando>.

Contas de teste

prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 8 atividades (era 7; +1 sintética na S33), 34.08 km. Tem atividade "Teste mapa - rota sintetica" (01a1b36a-0951-71e8-9044-c55c71558441, tipo walk, 60 pontos, ~10 min de duração) usada para validar o S26. Tem atividade sintética "Teste delta S33 (janela anterior)" (01a1e10b-8012-711a-9216-19d3eac8ed19, tipo walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal, bbox null, dentro da janela anterior [now-180d, now-90d) do by-type period=90d — criada na S33 pra exercitar o delta).
Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

⚠️ "Quem sou eu" é GET /auth/me, NÃO /users/me (esse devolve 422).

Acordos de trabalho (válidos em todas as sessões — reforçados na S21/S22/S23/S24/S25/S26/S27/S28/S29/S30/S31/S32/S33)

    SEMPRE seguir a recomendação do assistente. Quando houver decisão pendente, executar a recomendada salvo instrução explícita em contrário.

    SEMPRE entregar o CÓDIGO COMPLETO ao atualizar um arquivo — nunca diff parcial, nunca // resto igual, nunca placeholder. Destacar o trecho alterado com // [Sessão N] ou // [Sessão N — fix].

    UMA versão por arquivo por resposta. Se errar, cortar a errada e entregar só a corrigida com nota de 1 linha.

    HANDOFF PREVENTIVO em ~70–80% do limite de contexto. Completo, seções 0 a 9, sem resumir.

    PERCENTUAL DE PRONTIDÃO DO PROJETO anexo ao handoff (não no meio da sessão, não na abertura). Quebrado por camada (backend / web / mobile / bloqueadores não-código), com consolidado e estimativa de sessões restantes. Reflete o estado ao fim da sessão.

    VALIDAÇÃO INCREMENTAL. Arquivos da mesma stack: colar o base e buildar antes de entregar o próximo. Exceção: 2 arquivos acoplados por contrato interno → entregar juntos, 1 build.

    VERIFICAR SAVE ANTES DE BUILD (S21) — Get-Content | Select-String "<simbolo>" antes de build/test.

    NUNCA placeholder no código entregue (S21).

    Não adivinhar nomes de símbolos (S21).

    git status + git log antes de git restore (S21).

    Invoke-WebRequest sempre com -UseBasicParsing (S22).

    Validar openapi.json antes de acusar bug em rota nova (S22).

    Validar bundle da Vercel baixando index-*.js (S23).

    Vercel pode demorar >90 s no primeiro deploy (S24).

    Select-String -SimpleMatch não aceita | como alternância (S25a, reforçada na S33a).

    Confirmar $lines[-1] suspeito com Get-Content | Select-Object -Last N + Select-String -Pattern "<termo>" (S25b).

    Exigir output do bloco de validação antes de pedir commit (S25c).

    Teste definitivo do save: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M (S25d).

    Entregar conteúdo de arquivo para colar sem cerca markdown (S25e).

    PS 5.1: $resp.Content de Invoke-WebRequest -UseBasicParsing é string, não byte[] (S26a).

    Validar GPX em prod por regex no Content, não por gpxpy+temp file (S26b).

    Render free tier pode demorar >3 min para redeployar após push (S26c).

    Commitar o handoff pendente ANTES de qualquer outra coisa na abertura (S27a).

    Ordem fixa dos blocos da Fase 0: handoff → log/status → build → docker/pytest → prod back → prod front (S27b).

    Antes de aceitar o escopo do handoff anterior como verdade, pedir TODOS os arquivos que o contrato toca e confirmar o gap real (S28a).

    Chunk com hash novo e tamanho idêntico = renomeação de referência cruzada, não mudança de código (S28b).

    Contar entradas de ZIP no client via EOCD, fail-open, sem ZIP64 (S29a).

    Vercel reescreve hash de chunk ao servir; sinal de "novo no ar" = hash mudou vs sessão anterior + helper no bundle (S29b).

    Contar as ocorrências reais antes de anunciar "esperado Nx" num Select-String (S29c, reforçada na S33b).

    ESLint no-useless-assignment: declarar let x: T; sem inicializar quando try/catch cobre todos os caminhos (S29d).

    Select-String "TODO" casa case-insensitive "Todos"/"TODOS" — usar -CaseSensitive ou regex \bTODO\b (S30a).

    Componente genérico com semântica oposta: prop booleana default-false, sinal/percentual seguem delta cru, 4 casos (S30b).

    Handoff de memória sobre mobile SUBESTIMA o que existe — pedir Get-ChildItem + api.dart + telas antes de estimar (S30c).

    Windows sem Developer Mode: flutter pub add <plugin_nativo> instala mas build falha por symlink — ativar antes de flutter run (S31a).

    file_picker 13.x: FilePicker.platform/FilePickerResult/.size/.bytes removidos — API estática + length()/readAsBytes() (S31b).

    Select-String do disco mostrando conteúdo antigo após save do editor → contornar via WriteAllText no PowerShell, não insistir no Ctrl+S (S31c).

    Select-String -SimpleMatch 'class X' casa prefixo 'class Xxx' — usar word boundary ou espaço no fim (S32a).

    Select-String -SimpleMatch '_Simbolo' casa menções em comentários — filtrar linhas // ou usar regex ancorado (S32b).

    Anunciar "esperado ≈ N linhas" só depois de CONTAR o arquivo entregue — contagem mental falha para baixo em widgets aninhados (S32c).

    Nos Select-String de validação, "esperado" é sempre PISO ou FAIXA, nunca número exato sem contagem real do output (S32d, reforçada na S33b).

    Alternância em Select-String: SEMPRE -Pattern 'a|b' (sem -SimpleMatch). Vale também para blocos de verificação que o assistente monta (S33a).

    Em Select-String de validação, "esperado" é SEMPRE piso/faixa, nunca exato, mesmo quando o número parece óbvio (S33b).

Processo que o usuário elogiou na S21–S33 (para manter)

Fase 0 (validar estado) → Fase 1 (descoberta, pedir arquivos) → Fase 2 (contrato travado) → Fase 3 (entrega incremental, 1 arquivo por vez) → Fase 3.5 (verificar save + commit) → Fase 4 (validação) → Fase 5 (handoff + percentual).

    Descoberta antes de codar: pedir arquivos com motivo declarado.

    Validação entre cada entrega.

    Contrato travado escrito antes de codar.

    Commits pequenos e temáticos.

    Validação separada da local.

    Diagnóstico honesto antes de "consertar".

SEÇÃO 1 — TL;DR para quem chega agora

Backend: 166 testes passando LOCALMENTE, 0 warnings. Activity.route é PostGIS LINESTRING. GET /activities/{id}/track devolve TrackResponse com coordinates em ordem GeoJSON [lon, lat], bbox [minLon, minLat, maxLon, maxLat], n_points, simplified. 404 quando route é NULL.

ActivityResponse (feed/lista/detalhe/busca) inclui bbox: list[float] | None, calculado via ST_XMin/YMin/XMax/YMax no mesmo SELECT (sem N+1).

Endpoints de stats (todos validados em produção):

    GET /activities/stats/summary — StatsSummary.

    GET /activities/stats/weekly?weeks=N — StatsWeeklyResponse.

    GET /activities/stats/monthly?months=N — StatsMonthlyResponse.

    GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> — StatsByTypeResponse.

Stats públicas em perfis de terceiros (S19 + S20): GET /users/{user_id}/stats/{summary,weekly,monthly,by-type}. Regra (_ensure_can_view_stats em routers/users.py): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Export unitário (S21): GET /activities/{activity_id}/export?format=csv|gpx — auth dono OU seguidor. CSV: text/csv; charset=utf-8, 1 header + 1 linha (funciona com ou sem rota). GPX: application/gpx+xml; charset=utf-8, exige rota (404 "Atividade não possui rota"). format inválido → 422; omitido → default csv.

Export em lote (S22): GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] — auth self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). format=csv: inclui todas; format=gpx: só com rota. Filtro from/to inclusivo (UTC). 0 atividades → 200 + ZIP vazio. from > to → 422. format inválido → 422.

S26 (GPX com <time> por ponto): to_gpx(activity, coordinates, raw_track_points=None) ganhou o 3º parâmetro opcional. Quando raw_track_points existe e tem o MESMO comprimento de coordinates, cada <trkpt> recebe <time> com o timestamp real do ponto (unix epoch → ISO 8601 UTC). Caso contrário, fallback para started_at em todos os pontos. Contrato HTTP inalterado.

S31 — upload mobile (S31, inalterado na S33):

    POST /activities/upload — Auth Bearer JWT. multipart/form-data com file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120), activity_type (opcional), description (opcional). Sucesso: 201 com ActivityResponse. Erro: 422 (HTTPValidationError), 429 (slowapi, rate limit 10/h por IP), 401 (token). Parse síncrono, ~1–3s por arquivo.

    mobile/lib/services/api.dart — uploadActivity({File? file, List<int>? bytes, String? filename, String? title, String? activityType, String? description, String? token}) → Future<Activity>. Usa http.MultipartRequest (NÃO passa pelo _send). MultipartFile.fromPath quando file != null, MultipartFile.fromBytes quando só bytes != null (web). Timeout 60s.

    mobile/lib/pages/upload_page.dart (NOVO) — StatefulWidget, ~239 linhas. _pickFile() → FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['gpx','fit']) → List<PlatformFile> (vazio = cancelou). Se path != null → File; senão → readAsBytes() → _bytes. Valida extensão e tamanho ≤ 20 MB. _submit() → auth.api.uploadActivity(...) → SnackBar verde + context.pop(true).

S32 — perfil próprio + bottom nav (NOVO na S32, inalterado na S33 exceto profile_page.dart):

    GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> — auth Bearer JWT. Filtra atividades por usuário. O description do schema diz "requer seguir" quando user_id é de terceiro; para o próprio, sempre passa. Retorna ActivityResponse[] puro (sem envelope de paginação — sem total/has_more). Paginação client-side por "se voltou < limit, acabou". ⚠️ NÃO embute user no ActivityResponse.

    GET /users/{user_id} — retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email. NÃO tem avatar_url. NÃO tem created_at. Para o perfil próprio, o cabeçalho usa GET /auth/me (que retorna UserResponse completo, com email). getUser(id) fica para o perfil de terceiro (S34+).

    mobile/lib/services/api.dart — listActivities({String? userId, int limit = 20, int offset = 0, String? token}) → Future<List<Activity>>. Usa get('/activities?limit=&offset=[&user_id=]'). Propaga ApiException. Retorno é List<Activity> via Activity.fromJson.

    mobile/lib/models/user_me.dart (NOVO) — UserMe { id, email, username, fullName, isActive }. fromJson de GET /auth/me. Só os campos que o perfil usa (weight_kg/height_cm/birth_date ficam de fora — YAGNI).

    mobile/lib/widgets/activity_card.dart (NOVO na S32, EDITADO na S33) — ActivityCard extraído do feed_page.dart. Mesmo layout, mesmas props (activity, auth, onTap, onChanged) + [S33] authorUsernameOverride (String?, opcional). Reusado pelo FeedPage e pelo ProfilePage. ActivityCardMetric (privado do arquivo) substituiu o _Metric interno.

    mobile/lib/pages/feed_page.dart (REFATORADO na S32) — Removeu _ActivityCard/_Metric (foram para widgets/activity_card.dart). _load() ganhou 4 if (!mounted) return; + if (mounted) setState no finally (fix do setState() after dispose, dívida registrada na S31). _openDetail() ganhou 2 if (!mounted) return;. AppBar perdeu o IconButton(Icons.logout) (foi para o perfil, bottom nav dá acesso). FAB de upload mantido. [S33] O FeedPage NÃO passa authorUsernameOverride (o GET /feed já embute user).

    mobile/lib/pages/profile_page.dart (NOVO na S32, EDITADO na S33) — StatefulWidget, recebe AuthService. [S32] Estado: UserMe? _me, List<Activity> _activities, bool _loading, String? _error, int _offset, bool _hasMore, bool _loadingMore. _load() faz Future.wait([/auth/me, /activities?user_id=<me>&limit=20&offset=0]) em paralelo. _loadMore() pagina (GET /activities?offset=<_offset>). Pull-to-refresh → _load(). _logout() → auth.logout() + context.go('/login'). _openDetail() → push /activity/:id + reload do item. UI: _ProfileHeader (CircleAvatar com inicial + username + full_name + email + TextButton Sair) + "Minhas atividades" + lista de ActivityCard + "Carregar mais"/"Fim.". [S33] +seção de stats entre _ProfileHeader e "Minhas atividades": _StatsSection (StatsCards + ByTypeList) com estados _statsLoading/_statsError SEPARADOS de _loading/_error. _loadStats() faz Future.wait([getStatsSummary, getStatsByType(period:90d, compare:prev)]) em paralelo, com try/catch próprio. _refreshAll() = Future.wait([_load(), _loadStats()]) no RefreshIndicator.onRefresh. ActivityCard recebe authorUsernameOverride: _me?.username (resolve dívida S32 do user não embutido no /activities).

    mobile/lib/main.dart (REESCRITO na S32, inalterado na S33) — StatefulShellRoute.indexedStack com 2 StatefulShellBranch (/feed, /profile). _ScaffoldWithNavBar fornece NavigationBar (Feed, Perfil). /login, /upload, /activity/:id ficam FORA do shell (rotas planas, sem bottom nav). redirect inalterado (mesma lógica). refreshListenable: _auth mantido. initialLocation: '/feed' mantido.

S33 — stats agregadas no perfil (NOVO na S33):

    mobile/lib/models/stats.dart (NOVO) — espelho 1:1 de web/src/types/api.ts (que bate com backend/app/schemas/stats.py): StatsSummary (7 campos, 5 "totais" + avg_pace_s_per_km? + avg_speed_mps?), StatsByTypePrevious (5 campos), StatsByTypeItem (6 campos + previous?), StatsByTypeResponse ({ items }). Casts: int → as int; float → (num).toDouble(); nullable → (num?)?.toDouble().

    mobile/lib/services/api.dart (EDITADO) — +getStatsSummary(String userId, {String? token}) → Future<StatsSummary> (GET /users/{userId}/stats/summary). +getStatsByType(String userId, {String period='90d', String compare='prev', String? token}) → Future<StatsByTypeResponse> (GET /users/{userId}/stats/by-type?period=&compare=). Segue o padrão do listActivities (monta qs, valida is! Map, fromJson).

    mobile/lib/utils/format.dart (NOVO, movido de lib/lib/ no commit e15bedd) — portado de web/src/lib/format.ts. Funções: formatDistance(num? meters), formatElevation(num? meters), formatDuration(num? seconds), formatCalories(num? kcal), formatPace(num? sPerKm), computePace({num totalDurationS, num totalDistanceM}). Helper privado _formatThousands (sem intl). NÃO portados (YAGNI): formatSpeed, formatDateTime, formatRelativeDate, formatActivityType, activityEmoji.

    mobile/lib/widgets/stats_cards.dart (NOVO) — 5 StatCards espelhando StatsCards.tsx do web: Atividades, Distância, Tempo, Elevação, Calorias. Wrap (não GridView) com _StatCard (width 160) e _SkeletonCard. Estados: loading (5 skeletons), error (mensagem vermelha), data (5 cards). Ignora avg_pace_s_per_km e avg_speed_mps do StatsSummary (mesmo que o web).

    mobile/lib/widgets/by_type_list.dart (NOVO) — porta a seção "Por tipo de atividade" do ProfilePage.tsx. ByTypeList (header + estados + lista de _ByTypeCard). _ByTypeCard: header (label + N atividades) + grade 2×3 (Distância, Elevação, Tempo, Pace médio, Calorias) + _PreviousDelta embaixo se previous != null. _PreviousDelta: 5 _DeltaLine (Ativ., Dist., Elev., Tempo, Cal.) + Pace (lowerIsBetter: true) só nos _paceTypes = {'run','walk','hike'}. _DeltaLine: delta = current - previous; sign '+' / '−' (U+2212) / ''; pct só se previous > 0; isGood = lowerIsBetter ? delta<0 : delta>0; isBad = lowerIsBetter ? delta>0 : delta<0; cor verde/vermelho/cinza. Sinal matemático segue o delta cru (não inverte em lowerIsBetter) — só a cor inverte (S30 no web, portado).

    mobile/lib/widgets/activity_card.dart (EDITADO) — +prop authorUsernameOverride (String?, default null). displayUsername = activity.user?.username ?? authorUsernameOverride ?? 'Usuário'. Avatar continua usando activity.user?.avatarUrl (override não tem avatar — cai na inicial). Feed NÃO passa (GET /feed já embute user); ProfilePage passa _me.username.

    mobile/lib/pages/profile_page.dart (EDITADO) — ver acima (S32 + S33).

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
Deps mobile (S31/S32/S33): file_picker: ^13.3.3, go_router: ^18.1.2 (StatefulShellRoute disponível desde 6.x). Package name: rumo_mobile (imports package:rumo_mobile/...).

Git (estado ao fim da Sessão 33)

cf49065 (HEAD -> main, origin/main) feat(mobile): stats agregadas no perfil (Sessao 33)
799f8c9 feat(mobile): authorUsernameOverride no ActivityCard (Sessao 33)
88ae3da feat(mobile): lista de drill-down por tipo com delta (Sessao 33)
ded29f2 feat(mobile): StatsCards espelhando o web (Sessao 33)
e15bedd refactor(mobile): move format.dart para lib/utils (Sessao 33)
a91987f feat(mobile): formatadores de exibicao portados do web (Sessao 33)
f906c9f feat(mobile): models e client de stats (Sessao 33)
919ccea docs: handoff da Sessao 32
883b0f9 feat(mobile): bottom nav Feed/Perfil via StatefulShellRoute (Sessao 32)
dd83f60 feat(mobile): tela de perfil com minhas atividades (Sessao 32)
7d84765 refactor(mobile): extrai ActivityCard e corrige setState/mounted no feed (Sessao 32)
ff3cb55 feat(mobile): listActivities e UserMe (Sessao 32)
f39820f docs: handoff da Sessao 31
71a00d4 feat(mobile): upload GPX/FIT no feed (Sessao 31)
a83ed82 feat(mobile): upload GPX/FIT no feed (Sessao 31)
3a154b1 docs: handoff da Sessao 30
ffaaea0 feat(web): delta de pace no drill-down por tipo (Sessao 30)

Working tree limpo. S33 adicionou 7 commits (f906c9f … cf49065). Push feito. HEAD == origin/main.

Pendente: docs/HANDOFF.md da S33 (este arquivo) — usuário salva e commita como docs: handoff da Sessao 33.

SEÇÃO 3 — O QUE FOI FEITO NA SESSÃO 33

3.1 Fase 0 — validação de estado inicial

Tudo verde. Execução na ordem fixa da REGRA S27b:

    Handoff pendente. git status --short veio VAZIO na abertura (o commit do handoff S32 já estava feito — hash 919ccea). Working tree limpo desde o início.

    Log/status. git log -8: 919ccea (handoff S32), 883b0f9, dd83f60, 7d84765, ff3cb55, f39820f, 71a00d4, a83ed82. git diff --stat HEAD~4..HEAD: só docs/ + mobile/ (zero backend/, zero web/). Bate com o handoff S32.

    Build/lint/analyze. npm run build: 824 modules, 2.60s, hashes idênticos ao build da S30/S31/S32 (ProfilePage-pXfRJdbD.js 21.54 kB, index-DvGu4786.js 436.15 kB, ActivityDetailPage-C1KScSo5.js 11.38 kB, SearchPage-Bpu7TeFA.js 4.16 kB, RouteMap-CXXXy7Mv.js 2.41 kB, leaflet-Bw7RoR_1.js 163.60 kB, recharts-DI5KUTLO.js 351.26 kB). npm run lint: limpo. flutter analyze: No issues found! (4.0s).

    Docker + pytest. Docker 29.8.1 / compose v5.5.1 OK. rumo_postgres_test já estava Up 2 hours (healthy), pg_isready respondeu accepting connections na 1ª tentativa. pytest -q: 166 passed in 50.16s. ruff check .: All checks passed!.

    Prod backend (S26). Login OK. Atividade 01a1b36a-0951-71e8-9044-c55c71558441: 60 pontos com <time>, 60 distintos. Primeiro 2026-11-06T21:30:33Z, último 2026-11-06T21:40:23Z. S26 NO AR confirmado via regex no Content.

    Prod frontend (Vercel). index servido: /assets/index-CJjOEm0V.js (idêntico ao da S31/S32). __vite__mapDeps: ActivityDetailPage-DOBuid_4.js, ProfilePage-Cy6s98Hl.js, SearchPage-D6UpMvrw.js, leaflet-Bw7RoR_1.js, leaflet-CcXJxNtP.css, rolldown-runtime-hePW80VL.js, recharts-DI5KUTLO.js. Todos os 7 hashes batem com o esperado.

    Bloco 6b (novo — perfil via API). Login + /auth/me OK (me.id correto, me.email prod@rumo.com). GET /activities?user_id=<me>&limit=20&offset=0 devolveu 7 atividades (era 6 no handoff S32 — o upload de teste da S31/S32 deixou uma a mais). ActivityResponse confirmado SEM campo user (dívida S32 confirmada). ACHADO: a conta tinha 7 atividades, não 6.

3.2 Fase 1 — descoberta para stats no perfil

Pedi 10 arquivos + Get-ChildItem, com motivo declarado:

    backend/app/schemas/stats.py: shapes (StatsSummary 7 campos, StatsByTypeItem com previous?, StatsByTypeResponse { items }).

    backend/app/routers/users.py: rotas /users/{id}/stats/*, _ensure_can_view_stats (self → 200, segue → 200, não segue → 403, não existe → 404).

    web/src/lib/format.ts: formatadores (formatDistance, formatElevation, formatDuration, formatCalories, formatPace, computePace).

    web/src/types/api.ts: tipos TS (StatsSummary 7 campos, StatsByTypeItem, StatsByTypePrevious, StatsByTypeResponse).

    web/src/hooks/useStats.ts: hooks (useStatsSummary, useStatsByType) — ACHADO: o consumidor do by-type está aqui, não em components/.

    web/src/pages/ProfilePage.tsx: ACHADO CRÍTICO — o DeltaLine e o PreviousDelta existem, mas moram DENTRO do ProfilePage.tsx (funções privadas no fim do arquivo). O handoff S30 fala deles como componentes — na prática são helpers locais. Semântica portada 1:1.

    mobile/lib/pages/profile_page.dart: estado atual do perfil (S32).

    mobile/lib/services/api.dart: client atual (S32).

    mobile/lib/models/activity.dart: padrão de fromJson.

    mobile/lib/widgets/activity_card.dart: padrão de widget + ActivityCardMetric.

    mobile/lib/pages/feed_page.dart: call site do ActivityCard (o feed usa GET /feed, que embute user).

    Get-ChildItem web/src/components -Name: 13 componentes (ActivityCard, ActivityResults, AppHeader, CommentsSection, LikeButton, NotificationBell, PeriodChart, PhotoGallery, PhotoUpload, ProtectedRoute, RouteMap, StatsCards, UserResults). ACHADO: não existe DeltaLine.tsx nem PreviousDelta.tsx.

    Select-String recursivo achou o consumidor em hooks/useStats.ts + pages/ProfilePage.tsx.

ACHADOS que mudaram o plano:
#1 "requer seguir" quando user_id é de terceiro — para o próprio, sempre passa.
#2 StatsByTypeResponse tem só { items } (sem envelope).
#3 DeltaLine/PreviousDelta moram dentro de ProfilePage.tsx (não são componentes separados).
#4 PACE_TYPES = {run, walk, hike} — pace só nesses tipos, com lowerIsBetter.
#5 O web usa period=all por default (sem delta); o mobile prioriza 90d (com delta).
#6 UserPublic do backend é minimalista (id, username, full_name, is_active) — sem email, sem avatar_url.

3.3 Fase 2 — contrato travado

Ver Seção 1 (TL;DR). Contrato completo: 2 endpoints (self-only), models stats.dart, format.dart (5 formatadores), stats_cards.dart (5 cards), by_type_list.dart (cards por tipo + PreviousDelta + DeltaLine), activity_card.dart (+authorUsernameOverride), profile_page.dart (seção de stats + _loadStats separado + _refreshAll). Ordem de entrega: 6 arquivos, ~6 builds. Default period=90d&compare=prev.

Decisões travadas:

    Dívida do user no /activities: resolver no mobile (authorUsernameOverride), não no backend.

    Escopo da S33: só summary + by-type. Weekly/monthly → S34.

    Default period=90d no by-type (web usa all, mas all não tem delta — o delta é o valor da seção).

    Layout mobile do by-type em cards (não tabela de 8 colunas) — adaptação mobile do mesmo dado.

3.4 Fase 3 — entrega incremental (6 arquivos, 6 builds + 1 fix)

    stats.dart + api.dart (par acoplado, 1 build). flutter analyze verde.

    format.dart (1 build). flutter analyze verde.

    stats_cards.dart (1 build). flutter analyze PEGOU avoid_relative_lib_imports em ../lib/format.dart. Fix: mover format.dart para lib/utils/ (commit e15bedd) e trocar os imports para package:rumo_mobile/. flutter analyze verde depois do fix.

    by_type_list.dart (1 build). flutter analyze verde.

    activity_card.dart (1 build). flutter analyze verde.

    profile_page.dart (1 build). flutter analyze verde.

3.5 Fase 3.5 — verificar save + commit (com 3 desvios de contagem)

Bloco de verificação rodado em cada arquivo. Desvios no "esperado" do Select-String (todos do MEU lado, não do código):

    api.dart (arquivo 1/6): getStatsSummary|getStatsByType contou 0 (usei -SimpleMatch com |, REGRA S33a). O flutter analyze estava verde, confirmando que os métodos existiam. Refiz com -Pattern (sem -SimpleMatch) → 2, e as assinaturas completas → 1 cada. Falso negativo do meu teste.

    stats_cards.dart (arquivo 3/6): package:rumo_mobile contou 3, anunciei "esperado 2". Eram 2 imports reais + 1 menção em comentário. REGRA S33b (piso, não exato).

    Nenhum desvio nos arquivos 2, 4, 5, 6 (usei piso/faixa em todos, REGRA S32d/S33b).

Nenhum arquivo a corrigir. Todos os desvios foram no "esperado" do teste, não no código.

3.6 Fase 4 — validação manual no Chrome (S33 parcial + delta exercitado)

Só mobile mudou. Render e Vercel intocados (Fase 0 já confirmou). Fase 4 = validação manual no Chrome:

    flutter run -d chrome — OK.

    Login (prod@rumo.com / senha12345) — OK.

    Aba Perfil — cabeçalho (produser + Prod User + prod@rumo.com + Sair) — OK.

    Seção "Estatísticas" acima de "Minhas atividades" — OK.

    5 cards do resumo: Atividades 7, Distância 33,76 km, Tempo 5h 11min, Elevação 5.412 m (milhar pt-BR), Calorias 1.091 kcal — OK.

    "Por tipo de atividade" com card "Caminhada" (4 atividades, 22,96 km, 78 m, 2h 11min, pace 5:43 /km, 41 kcal) — OK.

    Delta NÃO apareceu na 1ª validação (previous null). DIAGNÓSTICO: a conta prod não tinha atividade de caminhada na janela anterior [now-180d, now-90d). Não era bug — era falta de dado.

    FIX DE DADO: criada atividade sintética "Teste delta S33 (janela anterior)" (id 01a1e10b-8012-711a-9216-19d3eac8ed19, walk, started_at 2026-06-01T10:00:00Z, 316.73 m, 480 s, 33 kcal) via upload de GPX sintético (D:\Rumo\backend_scratch\s33_delta_test.gpx, ignorado pelo git). Upload via curl.exe (Invoke-RestMethod -Form não existe no PS 5.1). by-type passou a ter previous preenchido.

    Delta apareceu no card "Caminhada" com 6 linhas verdes: Ativ. +3 (+300%), Dist. +22,65 km (+7151%), Elev. +70 m (+870%), Tempo +2h 03min (+1541%), Cal. +8 kcal (+24%), Pace −19:33 /km (−77%). O Pace é o caso 2 do lowerIsBetter (pace caiu = melhor = verde, com sinal −). O sinal U+2212 sobreviveu ao save e renderizou. — OK.

    Username produser nos cards de atividade (não "Usuário") — authorUsernameOverride funcionando — OK.

    "Minhas atividades" com cards (Teste mapa, Caminhada vespertina, etc.) — OK.

    Pull-to-refresh funcionou (o delta apareceu após o refresh, confirmando _refreshAll) — OK.

O que NÃO foi validado (cosmético, risco baixo):

    "Fim." no fim da lista (conta tem 8 atividades, _pageSize 20 → _hasMore false).

    Aba Feed (S32 já validou 11/11; override não afeta o feed).

    Logout (S32 já validou).

3.7 Observações / bugs encontrados

    avoid_relative_lib_imports em stats_cards.dart (../lib/format.dart) — CORRIGIDO na S33. Movido format.dart para lib/utils/ (commit e15bedd), imports package:rumo_mobile/. O caminho lib/lib/ era esquisito (espelhava web/src/lib/ mas não trazia benefício real).

    Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Fix: curl.exe (nativo no Windows 10+). Anotado como dívida do handoff (não é código, é script de teste).

    Nenhum bug de código na S33. Os 3 desvios de contagem foram do meu teste (S33a, S33b).

3.8 Resultado da suíte (S33)

    pytest -q → 166 passed (nenhuma mudança backend).

    ruff check . → All checks passed!.

    npm run build → 824 modules (web inalterado).

    npm run lint → limpo (web inalterado).

    flutter analyze → No issues found! (mobile com 7 arquivos novos/modificados).

    Validação manual no Chrome → 12/12 passos verdes (delta exercitado).

3.9 Commits pushados (S33)

    f906c9f feat(mobile): models e client de stats (Sessao 33) — 2 arquivos, +179 (stats.dart + api.dart).

    a91987f feat(mobile): formatadores de exibicao portados do web (Sessao 33) — 1 arquivo, +123 (format.dart).

    e15bedd refactor(mobile): move format.dart para lib/utils (Sessao 33) — 1 arquivo, rename 100% (lib/lib/format.dart → lib/utils/format.dart).

    ded29f2 feat(mobile): StatsCards espelhando o web (Sessao 33) — 1 arquivo, +153 (stats_cards.dart).

    88ae3da feat(mobile): lista de drill-down por tipo com delta (Sessao 33) — 1 arquivo, +360 (by_type_list.dart).

    799f8c9 feat(mobile): authorUsernameOverride no ActivityCard (Sessao 33) — 1 arquivo, +20/-4 (activity_card.dart).

    cf49065 feat(mobile): stats agregadas no perfil (Sessao 33) — 1 arquivo, +190/-5 (profile_page.dart).

Push feito. HEAD == origin/main == cf49065. Working tree limpo.

Pendente: docs: handoff da Sessao 33 (este arquivo).

SEÇÃO 4 — CONTRATOS DO BACKEND RELEVANTES

GET /activities/{id}/track (auth: Bearer JWT). Permissão: dono OU seguidor do dono (404 caso contrário). 404 quando activity.route é None → detail "Atividade não possui rota". Resposta (TrackResponse): { activity_id, type: "LineString", coordinates: [[lon, lat], ...], bbox: [minLon, minLat, maxLon, maxLat], n_points, simplified }.

ActivityResponse (feed/lista/detalhe/busca): { id, user_id, activity_type, title, description, started_at, finished_at, duration_s, distance_m, elevation_gain_m, calories, avg_pace_s_per_km, avg_speed_mps, cover_photo_url, photo_count, created_at, likes_count (default 0), liked_by_me (default false), comments_count (default 0), bbox: [minLon, minLat, maxLon, maxLat] | null }. Ordem GeoJSON. null quando route IS NULL. ⚠️ NÃO tem "user" embutido — o GET /feed embute (FeedItem tem author), mas o GET /activities NÃO. O mobile resolveu no self via authorUsernameOverride (S33); no perfil de terceiro (S34) vai precisar do backend ou de outro override.

GET /activities?user_id=<uuid>&limit=<1..100, default 20>&offset=<>=0, default 0> (auth: Bearer JWT) — S32. Filtra por usuário. Para user_id == currentUserId, sempre passa; para terceiro, requer seguir (403 se não seguir). Retorna ActivityResponse[] puro (sem envelope). Paginação client-side.

GET /users/{user_id} (auth: Bearer JWT) — S32. Retorna UserPublic (MINIMALISTA: id, username, full_name, is_active). NÃO tem email, avatar_url, created_at. Para o perfil PRÓPRIO, usar GET /auth/me (UserResponse completo).

GET /auth/me — UserResponse completo: { id, email, username, full_name, weight_kg, height_cm, birth_date, is_active, created_at }. NÃO é /users/me (esse devolve 422).

GET /activities/{id}/export?format=csv|gpx (auth: Bearer JWT) — S21. Permissão: dono OU seguidor do dono. Caso contrário, 404. format=csv (default): 200, text/csv; charset=utf-8, Content-Disposition: attachment; filename="rumo_<id><type>.csv". 1 header + 1 linha. Funciona com/sem rota. format=gpx: 200, application/gpx+xml; charset=utf-8, Content-Disposition: attachment; filename="rumo<id>_<type>.gpx". S26: <time> por <trkpt> usa timestamp real do raw_track_points quando alinhado; senão started_at. ISO 8601 UTC. Exige rota → 404 se route IS NULL. format inválido → 422.

GET /activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD] (auth: Bearer JWT) — S22. Auth: self-only. Saída: ZIP (application/zip, Content-Disposition: attachment; filename="rumo_export_<YYYYMMDD-HHMMSS>.zip"). N arquivos internos. S26: .gpx internos herdam <time> real por ponto. format=csv (default): ZIP com N .csv. format=gpx: ZIP com N .gpx (só com rota). Filtro from/to (YYYY-MM-DD, UTC, inclusivo). 0 atividades → 200 ZIP vazio; from > to → 422; format inválido → 422.

POST /activities/upload (auth: Bearer JWT) — S31. multipart/form-data: file (obrigatório, .gpx ou .fit), title (opcional, maxLength 120, nullable), activity_type (opcional, string, nullable), description (opcional, string, nullable). Sucesso: 201 com ActivityResponse. Erro: 422 HTTPValidationError (.detail tratado pelo _extractMessage do mobile). Rate limit: 10/hora por IP (slowapi; 429). Parse síncrono, ~1–3s. ⚠️ O upload de GPX usa o started_at do primeiro <trkpt> (ou do metadata), então dá pra criar atividades retroativas (usado na S33 pra exercitar o delta).

GET /activities/stats/summary?activity_type=<opcional> → StatsSummary. Inclui total_duration_s e total_calories.
GET /activities/stats/weekly?weeks=N&activity_type=<opcional> → StatsWeeklyResponse.
GET /activities/stats/monthly?months=N&activity_type=<opcional> → StatsMonthlyResponse.
GET /activities/stats/by-type?period=<all|90d|1y>&compare=<prev|yoy> → StatsByTypeResponse. S18/S20: cada item carrega as 5 métricas; previous (nullable) carrega as mesmas 5. S30: NÃO inclui avg_pace_s_per_km em nenhum shape — pace é derivado no front (computePace).

Janelas (S17/S18/S20):
period | compare | janela
all | qualquer | null
90d | prev (default) | [now-180d, now-90d)
90d | yoy | [now-455d, now-365d)
1y | prev | [now-730d, now-365d)
1y | yoy | [now-730d, now-365d) (coincide)

GET /users/{user_id}/stats/{summary,weekly,monthly,by-type} — mesmos shapes. _ensure_can_view_stats: self → 200; segue → 200; não segue → 403; não existe → 404. Params: summary aceita activity_type opcional; weekly aceita weeks (1..52, default 8); monthly aceita months (1..24, default 6); by-type aceita period (default all) e compare (default prev). ⚠️ O by-type do web usa period=all default; o mobile S33 usa period=90d (com delta).

POST /users/{user_id}/follow — 204. DELETE /users/{user_id}/follow — 204. (S19/S20)
GET /users/{user_id}/followers?limit&offset — list[UserPublic]. (S19/S20)
GET /users/{user_id}/following?limit&offset — list[UserPublic]. (S19/S20)
GET /users/search?q=<min 2 chars>&limit — list[UserPublic]. Rate limit 20/min. (S19/S20)

SEÇÃO 5 — COMMITS PENDENTES / ESTADO DO REPO

Sessões 9–33 commitadas e pushadas. HEAD == origin/main == cf49065. Working tree limpo.

Pendente: este handoff.

Primeira ação da Sessão 34 (REGRA S27a — handoff primeiro)

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md, commitar:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 33"
git push
git --no-pager log --oneline -4
git status --short

Esperado: HEAD == origin/main com docs: handoff da Sessao 33 no topo, working tree limpo.

SEÇÃO 6 — SCRIPTS ÚTEIS (PowerShell)

[Sessão 34 — primeira ação] Abrir PowerShell via Win+R → powershell (NÃO abrir de dentro do VS Code / Windows Terminal).

cd D:\Rumo
git status --short

Se aparecer M docs/HANDOFF.md:

git add docs/HANDOFF.md
git commit -m "docs: handoff da Sessao 33"
git push
git --no-pager log --oneline -8
git status --short

[Sessão 34 — primeira ação] Sanidade de build

cd D:\Rumo\web
npm run build
npm run lint
cd ..\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

[Sessão 34 — primeira ação] Docker + pytest local

docker version
docker compose version
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432

Se o prompt já mostra (venv), PULE a linha abaixo:

.\venv\Scripts\Activate.ps1
python -m pytest -q
ruff check .

Esperado: 166 passed, ruff limpo, container Up (healthy).

[Sessão 34 — primeira ação] Detecção de versão em produção (front — Vercel)

⚠️ Sempre -UseBasicParsing. ⚠️ Depois de git push, se o hash antigo ainda aparecer, aguardar 90 s e rodar de novo (REGRA S24). ⚠️ REGRA S29b: o hash servido pelo Vercel não bate com o build local. O sinal de "novo no ar" é o hash mudou vs sessão anterior.

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:(m.Groups[1].Value)"m.Groups[1].Value)"idx = Invoke-WebRequest -Uri idxUrl−UseBasicParsingidxUrl−UseBasicParsingidx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|ProfilePage|SearchPage)-[A-Za-z0-9_-]+.js'

Esperado no estado atual (S33): web inalterado desde S30 — index-CJjOEm0V.js com ProfilePage-Cy6s98Hl.js, ActivityDetailPage-DOBuid_4.js, SearchPage-D6UpMvrw.js.

Login (produção) — ATENÇÃO: identidade é /auth/me, NÃO /users/me

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodytoken = login.accesstokenlogin.accesst​okenme = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/me" -Headers @{ Authorization = "Bearer token" } meId = $me.id

Detecção de versão em produção (backend S26 — GPX com <time> por ponto)

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodyh = @{ Authorization = "Bearer ((login.access_token)" }

aid="01a1b36a−0951−71e8−9044−c55c71558441"aid="01a1b36a−0951−71e8−9044−c55c71558441"resp = Invoke-WebRequest -Uri "https://rumo-api-5s0b.onrender.com/activities/$aid/export?format=gpx" -Headers $h -UseBasicParsing

times=[regex]::Matches(times=[regex]::Matches(resp.Content, '<time>([^<]+)</time>') | ForEach-Object { _.Groups[1].Value } n = times.Counttimes.Countdistinct = (times∣Sort−Object−Unique).CountWrite−Host"pontoscom<time>:times∣Sort−Object−Unique).CountWrite−Host"pontoscom<time>:n"
Write-Host "<time> distintos: distinct"if(distinct"if(n -gt 0) {
Write-Host "primeiro: ((times[0])"
Write-Host "ultimo: ((times[-1])"
}
if (distinct−le1−anddistinct−le1−andn -gt 1) {
Write-Host "S25 AINDA NO AR (todos iguais)."
} elseif (distinct−gedistinct−gen - 1) {
Write-Host "S26 NO AR (timestamps distintos por ponto)."
} else {
Write-Host "ATENCAO: apenas distinct/distinct/n distintos."
}

Esperado agora: 60 pontos, 60 distintos, primeiro 2026-11-06T21:30:33Z, ultimo 2026-11-06T21:40:23Z (sem microssegundos desde a S31).

[Sessão 34 — validação do perfil + stats via API] (novo S33)

body = "username=prod@rumo.com&password=senha12345" login = Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/auth/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body bodybodyh = @{ Authorization = "Bearer ((login.access_token)" }
me=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/me"−Headersme=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/auth/me"−Headersh
Write-Host "me.id: ((me.id)"
Write-Host "me.email: ((me.email)"

acts=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities?userid=acts=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/activities?useri​d=(me.id)&limit=20&offset=0" -Headers h
Write-Host "minhas atividades: ((acts.Count)"

summary=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/summary=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/(me.id)/stats/summary"−Headersme.id)/stats/summary"−Headersh
Write-Host "summary.total_activities: ((summary.total_activities)"
Write-Host "summary.total_distance_m: ((summary.total_distance_m)"

bt=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/bt=Invoke−RestMethod−Uri"https://rumo−api−5s0b.onrender.com/users/(me.id)/stats/by-type?period=90d&compare=prev" -Headers h
prev = if (.previous−eq.​previous−eqnull) { "null" } else { "preenchido" }
Write-Host "((.activity_type): ((.total_activities) atividades, previous=$prev"
}

Esperado: me.id = 01a12c83-be2a-71fa-b966-1c93ca64f341, me.email = prod@rumo.com, minhas atividades = 8 (7 + 1 sintética da S33), summary.total_activities = 8, walk com previous=preenchido (a sintética de 2026-06-01 está na janela anterior).

Stats de terceiros (S19/S20)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/$meId/stats/summary" -Headers @{ Authorization = "Bearer token" } | ConvertTo-Json -Depth 3 Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/users/meId/stats/by-type?period=90d&compare=yoy" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 4

Ruff (backend)

cd D:\Rumo\backend
Se o prompt já mostra (venv), pule:

.\venv\Scripts\Activate.ps1
ruff check .

Recuperação de arquivo corrompido (lição S21)

cd D:\Rumo
git status --short <arquivo>
git --no-pager log --oneline -3 -- <arquivo>
Se o último commit for anterior à mudança quebrada:

git restore <arquivo>
Se a versão quebrada JÁ foi commitada:

git show <commit-anterior>:<arquivo> > <arquivo>

Diagnóstico: rota nova não responde após git push (lição S22 + S26c)

Invoke-RestMethod -Uri "https://rumo-api-5s0b.onrender.com/openapi.json" | ConvertTo-Json -Depth 6 | Select-String -Pattern "activities/export"

Se vazio: Render não redeployou. Aguardar (S26c: >3 min) ou Manual Deploy.

Se rota no ar mas retorna 422, ver o BODY do erro:

try {
Invoke-WebRequest -Uri "<url>" -Headers h -UseBasicParsing | Out-Null } catch { resp = .Exception.Response.​Exception.Responsereader = New-Object System.IO.StreamReader(resp.GetResponseStream())Write−Host"STATUSresp.GetResponseStream())Write−Host"STATUS(resp.StatusCode)"Write−Host(resp.StatusCode)"Write−Host(reader.ReadToEnd())
}

Diagnóstico: bundle novo não aparece na Vercel (lição S23+S24+S29b)

html=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsinghtml=Invoke−WebRequest−Uri"https://rumo−wheat.vercel.app"−UseBasicParsingm = [regex]::Match(html.Content,′src="(/assets/index−["]+j˙s)"′)html.Content,′src="(/assets/index−["]+j˙​s)"′)idxUrl = "https://rumo-wheat.vercel.app" + m.Groups[1].ValueWrite−Host"indexservido:m.Groups[1].ValueWrite−Host"indexservido:(m.Groups[1].Value)"m.Groups[1].Value)"idx = Invoke-WebRequest -Uri idxUrl−UseBasicParsingidxUrl−UseBasicParsingidx.Content | Select-String -Pattern 'assets/(ActivityDetailPage|RouteMap|ProfilePage)-[A-Za-z0-9_-]+.js'

Hash novo → bundle novo no ar (mesmo que não bata com o build local — REGRA S29b). Hash antigo → Vercel não redeployou: aguardar 90s. Para confirmar conteúdo: baixar o chunk novo e Select-String do símbolo/helper que mudou.

⚠️ REGRA S28b: se ProfilePage novo mas ActivityDetailPage/SearchPage com hash novo e TAMANHO idêntico, é renomeação de referência cruzada. Não investigar.

Diagnóstico de save de arquivo (lição S25 + S32 + S33)

Depois de salvar, ANTES de commitar:

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
Write-Host "=== [6] hash do HEAD ==="
git rev-parse HEAD:<arquivo>

Se [5] == [6] e [4] vazio → o disco é igual ao commitado. O save NÃO pegou.
Se [5] != [6] e [4] mostra ' M' → save pegou, pode commitar.

Nota S30a: -Pattern "TODO" sozinho casa "Todos"/"TODOS". Sempre usar -CaseSensitive OU regex \bTODO\b|\bFIXME\b.
Nota S32a/S32b/S33a: -SimpleMatch 'class X' casa 'class Xxx' (prefixo). -SimpleMatch '_X' casa menções em //. -SimpleMatch 'a|b' NÃO é alternância. Para contagem exata/alternância, usar -Pattern (sem -SimpleMatch) com regex ancorado.
Nota S33b: o "esperado" de qualquer Select-String é piso/faixa, nunca exato sem contagem real.

Contornar editor que não salva (REGRA S31c)

Se Select-String do disco mostrar conteúdo antigo depois do save do editor:

cd D:\Rumo\mobile # ou o diretório do arquivo
content=@′//conteuˊdocompletodoarquivoaqui′@[System.IO.File]::WriteAllText("content=@′//conteuˊdocompletodoarquivoaqui′@[System.IO.File]::WriteAllText("PWD\caminho\do\arquivo.dart", content,[System.Text.UTF8Encoding]::new(content,[System.Text.UTF8Encoding]::new(false))
Write-Host "_bytes: ((Select-String -Path caminho\do\arquivo.dart -Pattern '_bytes' -SimpleMatch | Measure-Object).Count) (esperado >=2)" Write-Host "debugPrint: ((Select-String -Path caminho\do\arquivo.dart -Pattern 'debugPrint' -SimpleMatch | Measure-Object).Count) (esperado 0)"

O @' precisa estar sozinho na linha, e o '@ também. WriteAllText grava direto no disco, sem passar pelo editor.

Baixar bytes de GPX/XML no PS 5.1 SEM quebrar (lição S26a)

ERRADO — Content é string, não byte[]:
[System.IO.File]::WriteAllBytes(path, $resp.Content)

CERTO (texto UTF-8):
[System.IO.File]::WriteAllBytes(path, [System.Text.Encoding]::UTF8.GetBytes($resp.Content))

CERTO (bytes crus — ZIP, imagem):
fs=[System.IO.File]::OpenWrite(fs=[System.IO.File]::OpenWrite(path)
resp.RawContentStream.Position=0resp.RawContentStream.Position=0resp.RawContentStream.CopyTo(fs)fs)fs.Close()

MELHOR para inspecionar GPX — sem arquivo, regex no Content:
times=[regex]::Matches(times=[regex]::Matches(resp.Content, '<time>([^<]+)</time>') | ForEach-Object { $_.Groups[1].Value }

Upload de arquivo via PowerShell (lição S33)

Invoke-RestMethod -Form NÃO existe no PS 5.1 (só PS 6+). Para multipart/form-data, usar curl.exe (nativo no Windows 10+):

curl.exe -X POST "https://rumo-api-5s0b.onrender.com/activities/upload" -H "Authorization: Bearer $($login.access_token)"
-F "file=@D:\caminho\arquivo.gpx" `
-F "title=Titulo opcional"

Para gerar um GPX sintético no disco (sem editor):

$gpx = @'
<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="..." xmlns="http://www.topografix.com/GPX/1/1"> <trk><trkseg> <trkpt lat="-23.55" lon="-46.63"><ele>760</ele><time>2026-06-01T10:00:00Z</time></trkpt> </trkseg></trk> </gpx> '@ [System.IO.File]::WriteAllText("D:\Rumo\backend\_scratch\teste.gpx", $gpx, [System.Text.UTF8Encoding]::new($false))

Verificar perfil mobile em prod (S33 — NOVO)

cd D:\Rumo\mobile
& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

E rodar o app:
& "C:\Users\nasci\flutter\bin\flutter.bat" run -d chrome

Escolher device (Chrome para web, Android para emulador/aparelho). Testar: login → bottom nav → aba Perfil carrega cabeçalho + StatsCards (5 cards) + ByTypeList (cards por tipo + delta se houver previous) + "Minhas atividades" com username (authorUsernameOverride) → pull-to-refresh recarrega tudo → aba Feed mantém scroll → detalhe abre sem bottom nav.

⚠️ Developer Mode: se flutter run falhar com erro de symlink, rodar start ms-settings:developers e ativar (REGRA S31a).

Testar delta no by-type (S33 — NOVO)

Com a conta prod (8 atividades, sendo 1 sintética em 2026-06-01), o by-type period=90d&compare=prev deve ter previous preenchido para walk. Se quiser reexercitar o delta em outra conta/tipo, criar atividade sintética na janela [now-180d, now-90d) via upload de GPX com <time> no passado (ver "Upload de arquivo via PowerShell" acima).

SEÇÃO 7 — DÍVIDAS TÉCNICAS

(FECHADA na S20) ~~Duas pastas de venv~~ — .venv removida. Única venv é backend\venv.
(FECHADA na S20) ~~Pylance reclamando de imports~~ — .vscode/settings.json aponta para backend/venv.
(FECHADA na S25) ~~RouteMap.tsx é reutilizável; se aparecer segundo uso, considerar React.lazy()~~ — RouteMap agora é lazy no ActivityDetailPage.
(FECHADA na S26) ~~to_gpx não emite <time> por <trkpt>~~ — agora emite quando raw_track_points está disponível e alinhado.
(FECHADA na S28) ~~PreviousDelta mostrava só 3 das 5 métricas~~ — PreviousDelta agora renderiza as 5.
(FECHADA na S29) ~~downloadActivityExportBulk retornava void~~ — agora devolve { entryCount }.
(FECHADA na S30) ~~Delta de Pace no PreviousDelta está fora de escopo~~ — DeltaLine ganhou lowerIsBetter.
(FECHADA na S31) ~~Mobile não tem upload GPX/FIT~~ — POST /activities/upload consumido pelo ApiClient.uploadActivity + UploadPage + FAB no feed.
(FECHADA na S32) ~~Mobile não tem perfil nem "minhas atividades"~~ — GET /activities?user_id= consumido pelo ApiClient.listActivities + ProfilePage + bottom nav via StatefulShellRoute.
(FECHADA na S32) ~~setState() called after dispose no feed_page.dart~~ — 4 if (!mounted) return; + if (mounted) setState no finally do _load; 2 if (!mounted) return; no _openDetail.
(FECHADA na S32) ~~_ActivityCard e _Metric duplicados entre feed e perfil~~ — extraídos para widgets/activity_card.dart (ActivityCard + ActivityCardMetric).
(FECHADA na S32) ~~GET /activities não embute user; ActivityCard cai em "Usuário" no perfil~~ — resolvido no mobile via authorUsernameOverride (S33). Backend intocado.
(FECHADA na S33) ~~Mobile não tem stats agregadas no perfil~~ — GET /users/{id}/stats/summary + by-type consumidos, StatsCards + ByTypeList + delta com lowerIsBetter.
(FECHADA na S33) ~~format.dart em lib/lib/ dispara avoid_relative_lib_imports~~ — movido para lib/utils/, imports package:rumo_mobile/.

(CONHECIDA — Sessão 14) Enums nativos do Postgres ordenam pela ORDEM DE DECLARAÇÃO. get_by_type desempata em Python.
(CONHECIDA — Sessão 17) Filtro period usa now() do Postgres. Testes DEVEM usar datetime.now(timezone.utc) - timedelta(days=N) com margem ≥10 dias.
(CONHECIDA — Sessão 18) WHERE mata a janela anterior antes do CASE WHEN.
(CONHECIDA — Sessão 17–28) StatsCards mostra summary "todos os tempos", não filtrado por period nem por previous. Intencional.
(CONHECIDA — Sessão 17–28) Conta prod@rumo.com não tem atividade >90d. period=all, 90d e 1y retornam iguais em produção para prod; previous vem null. NÃO é bug. (Atualização S33: com a sintética de 2026-06-01, o previous de walk em 90d agora vem preenchido; a conta tem 8 atividades, sendo 7 "atuais" e 1 na janela anterior.)
(CONHECIDA — Sessão 20) period="1y" faz compare=yoy ≡ compare=prev por definição matemática.
(CONHECIDA — Sessão 21) sample_run.gpx em backend/samples/ não é "run" — <type> traduz para "walk". Testes usam activity.activity_type.value dinâmico.
(CONHECIDA — Sessão 21) apiFetchBlob não tem skipAuth. YAGNI por enquanto.
(CONHECIDA — Sessão 22) export_activities_bulk faz O(N) queries. Aceitável para export raro.
(CONHECIDA — Sessão 22) Export em lote é self-only. Decisão de privacidade.
(CONHECIDA — Sessão 23) downloadActivityExportBulk valida from > to client-side. Dupla validação proposital.
(CONHECIDA — Sessão 24) useEffect de auto-limpeza do exportInfo usa window.setTimeout(..., 4000) e window.clearTimeout(t).
(CONHECIDA — Sessão 25) React.lazy() no RouteMap não tira o leaflet do index — o leaflet já era chunk separado desde antes.
(CONHECIDA — Sessão 26) <time> no GPX inclui microssegundos (2026-11-07T00:20:32.931332Z) porque o gpxpy serializa datetime.isoformat(). Observação S31: em prod agora vem truncado em segundos (2026-11-06T21:30:33Z). Contrato intacto.
(CONHECIDA — Sessão 26) raw_track_points e coordinates normalmente têm o mesmo comprimento, mas o código NÃO assume isso — fallback por ponto se divergir. Coberto por teste.
(CONHECIDA — Sessão 28) ActivityDetailPage/SearchPage mudam de hash no bundle quando ProfilePage muda de tamanho. É renomeação de referência cruzada no __vite__mapDeps, não regressão (REGRA S28b).
(CONHECIDA — Sessão 29) _countZipEntries NÃO suporta ZIP64. Aceitável: export de atividades fica < 4 GB e < 65535 arquivos. Sentinel 0xFFFF sinaliza falha (retorna -1, fail-open).
(CONHECIDA — Sessão 29) downloadActivityExportBulk lê blob.arrayBuffer() ANTES de disparar o download. Custo: 1 passada no buffer (KBs). Se o export virar pesado, trocar por blob.slice(-22-65535, blob.size).
(CONHECIDA — Sessão 29) O hash servido pelo Vercel não bate com o build local (REGRA S29b). Não investigar.
(CONHECIDA — Sessão 30) Pace em cycle/swim/other fica fora do delta (e fora da coluna "Pace médio") por decisão de UX. Se um dia alguém quiser pace em cycle, relaxar PACE_TYPES — DeltaLine já tem lowerIsBetter pronto.
(CONHECIDA — Sessão 30) computePace retorna null quando total_distance_m <= 0. PreviousDelta coalesce para 0 (computePace(item) ?? 0), resultando em "Pace 0:00 /km" cinza quando ambos os lados são zero.
(CONHECIDA — Sessão 31) Mobile: AuthService SEM refresh token. Token expirado → 401 na request seguinte → ApiException; o app NÃO faz logout automático. Melhoria para "mundo real", não MVP.
(CONHECIDA — Sessão 31) Mobile: uploadActivity valida path == null → readAsBytes(), cobre web. No Android, path costuma vir preenchido (o plugin copia pra cache) e o File(path) deve funcionar — não testado em dispositivo físico. Testar na S34+.
(CONHECIDA — Sessão 31) Mobile: rate limit 10/h do /activities/upload não foi testado explicitamente (429). Se o backend devolver .detail legível, a UI mostra; se não, mostra "Erro 429". Oportunidade: UI dedicada com cooldown visual.
(CONHECIDA — Sessão 31) Mobile: activity_type fora da UI do upload na S31 — o backend infere pelo arquivo. Se precisar de override manual, é um dropdown em sessão futura.
(CONHECIDA — Sessão 31) O commit a83ed82 foi feito pelo usuário/VS Code com a versão inicial; 71a00d4 refinou upload_page.dart e api.dart. Não vale rebase/squash.
(CONHECIDA — Sessão 31) file_picker 13.3.3 trouxe 11 deps novas (android_file_picker, cross_file, dbus, file_picker_darwin, file_picker_linux, file_picker_platform_interface, file_picker_web, petitparser, windows_file_picker, xml + file_picker). Todas no pubspec.lock.
(CONHECIDA — Sessão 32) GET /activities (backend) retorna ActivityResponse[] SEM o campo "user" embutido. O GET /feed embute (FeedItem tem author). Resolvido no mobile via authorUsernameOverride (S33). No perfil de terceiro (S34), o backend precisa embutir user no /activities OU o mobile precisa buscar o UserPublic do alvo e passar como override — decisão da S34.
(CONHECIDA — Sessão 32) UserPublic local em activity.dart tem avatarUrl que o UserPublic do backend NÃO tem (o do backend é { id, username, full_name, is_active }). O _ActivityCard usa avatarUrl só se não for null. Dívida: alinhar o model local com o schema (remover avatarUrl) ou o backend ganhar o campo. Não tocado na S33.
(CONHECIDA — Sessão 32) ProfilePage usa Future.wait([/auth/me, /activities?user_id=...]) em paralelo. Se um falhar, o Future.wait rejeita com o primeiro erro. O catch genérico mostra "Erro: $e". Na S33, os stats foram SEPARADOS (_loadStats com Future.wait próprio), então uma falha de stats não derruba a lista e vice-versa.
(CONHECIDA — Sessão 32) ProfilePage paginação: "Carregar mais" (botão), não scroll infinito. O backend não dá total; regra "se voltou < limit, acabou". Conta prod tem 8 atividades — o "Carregar mais" NÃO foi exercitado (8 < 20 → mostra "Fim."). Testar na S34+ (criar conta com >20 atividades ou aumentar temporariamente o limit).
(CONHECIDA — Sessão 32) Bottom nav via StatefulShellRoute.indexedStack. Rotas /login, /upload, /activity/:id ficam FORA do shell (sem bottom nav). Decisão intencional.
(CONHECIDA — Sessão 32) O FAB de upload some quando o usuário está na aba Perfil. Intencional (upload é ação do feed).
(CONHECIDA — Sessão 33) period/compare FIXOS no mobile (90d/prev). O web tem filtros de UI (all/90d/1y × prev/yoy). Filtros ficam pra S34 (quando o perfil de terceiro chegar, ou antes).
(CONHECIDA — Sessão 33) O by-type do mobile mostra os cards em Wrap (não tabela de 8 colunas como o web). Adaptação mobile do mesmo dado — paridade semântica, não visual.
(CONHECIDA — Sessão 33) O _DeltaLine do mobile usa Colors.green.shade700 / red.shade700 (Material) em vez de text-green-600/red-600 (Tailwind). Equivalente aproximado; shade700 lê melhor em texto pequeno.
(CONHECIDA — Sessão 33) O _formatThousands é inline (sem intl). O web usa toLocaleString("pt-BR"). Se o mobile precisar de formatação de data/moeda pt-BR em vários lugares, aí intl entra; hoje não.
(CONHECIDA — Sessão 33) A conta prod@rumo.com tem uma atividade sintética (01a1e10b-8012-711a-9216-19d3eac8ed19, 2026-06-01, walk, 316.73 m, 480 s, 33 kcal) criada via upload de GPX sintético pra exercitar o delta do by-type 90d. Fica como dado de teste (não vale deletar; serve pra S34). O GPX fonte está em backend/_scratch/s33_delta_test.gpx (ignorado pelo git).
(CONHECIDA — Sessão 33) Invoke-RestMethod -Form não existe no PS 5.1 (só PS 6+). Para multipart, usar curl.exe. Anotado na Seção 6.
(CONHECIDA — Sessão 33) Weekly/monthly charts no mobile ficam pra S34 (periodchart do web usa recharts; no mobile, seria fl_chart ou similar — decisão de dependência na S34).

(Oportunidade — S18–S33) Semântica do delta é NEUTRA. Sem "melhor/pior" no label. Pace entrou com lowerIsBetter, mas o label não diz "melhor/pior" — só a cor.
(Oportunidade — S19–S33) Stats públicas só quando viewer segue o alvo.
(Oportunidade — S22–S33) Export em lote no mobile (paridade com web S21/S22/S29).
(Oportunidade — S30) Testes unitários do DeltaLine no web (não há hoje; é puro, dá pra testar com 4 casos e sem React Testing Library). No mobile, o _DeltaLine também é puro e testável.
(Oportunidade — S31) Mobile: refresh token no AuthService, logout automático em 401, retry com backoff no ApiClient.
(Oportunidade — S31) Testar upload em Android físico/emulador (o path do Android e o File(path) não foram exercitados).
(Oportunidade — S31) UI dedicada para 429 (rate limit) com cooldown visual.
(Oportunidade — S31) activity_type como dropdown opcional na UploadPage.
(Oportunidade — S32) Stats agregados no perfil — FEITO na S33.
(Oportunidade — S33) Filtros de period/compare na UI do perfil (S34).
(Oportunidade — S33) Weekly/monthly charts no perfil (S34).
(Oportunidade — S33) Perfil de terceiro + follow (S34) — getUser(id) + model User (contra UserPublic) + GET /users/{id}/stats/* + follow/unfollow.
(Oportunidade — S33) Busca de usuários (S35).
(Oportunidade — S33) Export no mobile (unitário + lote) (S36).
(Oportunidade — S33) Editar perfil (peso, altura, etc.) (S34+).
(Oportunidade — S33) Alinhar UserPublic local com o backend (remover avatarUrl do model, ou adicionar no backend) (S34).

SEÇÃO 8 — PRÓXIMOS PASSOS RECOMENDADOS (Sessão 34 e além)

Sessão 33 fechada. Perfil próprio agora tem stats agregadas (summary + by-type com delta), e o username no perfil funciona (authorUsernameOverride). Mobile subiu de ~55% para ~68% de cobertura. Backend/web inalterados.

Primeira ação obrigatória da Sessão 34 (REGRA S27a)

    Abrir PowerShell via Win+R → powershell.

    Rodar o bloco "[Sessão 34 — primeira ação]": git status --short → se M docs/HANDOFF.md, commitar como docs: handoff da Sessao 33, push, confirmar HEAD == origin/main.

    Sanidade de build (npm run build/npm run lint + flutter analyze).

    Docker + pytest (docker ps -a, pg_isready, pytest -q → 166, ruff check).

    Detecção de versão em produção (front Vercel + back Render S26 + bloco novo de perfil/stats da S33).

Rota travada para a Sessão 34: perfil de terceiro + follow (paridade com web S19/S20)

Este é o próximo gap funcional do mobile: tocar no avatar/username de um card (no feed, no detalhe, ou numa lista) abre o perfil de terceiro, com stats públicas (se o viewer segue) e botão follow/unfollow. O backend já tem TUDO pronto desde a S19/S20 (validado em produção):

    GET /users/{user_id} → UserPublic (id, username, full_name, is_active). Sem email, sem avatar_url.

    GET /users/{user_id}/stats/summary (self ou segue)

    GET /users/{user_id}/stats/weekly (self ou segue)

    GET /users/{user_id}/stats/monthly (self ou segue)

    GET /users/{user_id}/stats/by-type?period=&compare= (self ou segue)

    POST /users/{user_id}/follow → 204

    DELETE /users/{user_id}/follow → 204

    GET /users/{user_id}/followers?limit&offset → list[UserPublic]

    GET /users/{user_id}/following?limit&offset → list[UserPublic]

    GET /users/search?q=&limit (S35, já existe)

Regra de visibilidade (_ensure_can_view_stats): self → 200; viewer segue target → 200; viewer não segue → 403; target não existe → 404.

Contrato preliminar (a confirmar na Fase 1 da S34, pedindo api.dart, profile_page.dart, activity_card.dart, main.dart, e o openapi.json dos endpoints de user/follow):

    lib/models/user.dart (NOVO) — User { id, username, fullName, isActive } (contra UserPublic do backend). Ou reaproveitar o UserPublic local de activity.dart (alinhando com o backend — dívida conhecida).

    lib/services/api.dart — getUser(String userId, {String? token}) → Future<User>; isFollowing(String userId, {String? token}); followUser(String userId, {String? token}) → Future<void>; unfollowUser(String userId, {String? token}) → Future<void>; listFollowers(String userId, {int limit, int offset, String? token}); listFollowing(...). Reusar getStatsSummary/getStatsByType (já existem) passando o userId do alvo (o backend aplica a regra).

    lib/pages/profile_page.dart — generalizar para aceitar userId opcional (null = self, atual; não-null = terceiro). Se terceiro: cabeçalho vem de GET /users/{id} (sem email), botão Follow/Unfollow, stats só se isFollowing (senão 403 — mostrar "Siga pra ver as estatísticas"), lista de atividades só se isFollowing (403 se não). Se self: comportamento atual (auth/me, email, sem botão de follow).

    lib/pages/user_profile_page.dart (NOVO, ou reescrever profile_page.dart) — a tela de perfil de terceiro. Recebe userId. Reusa _ProfileHeader, StatsCards, ByTypeList, ActivityCard (com authorUsernameOverride: user.username do alvo).

    lib/widgets/activity_card.dart — onTap no avatar/username → context.push('/user/<userId>') (ou só no username, ou no card inteiro). Decisão de UX na S34.

    lib/main.dart — rota nova /user/:id (fora do shell, como /activity/:id).

Escopo NÃO incluso na S34:

    Filtros de period/compare na UI (S35 ou antes).

    Weekly/monthly charts (S35).

    Busca de usuários (S35).

    Export no mobile (S36).

    Editar perfil (S37+).

    Refresh token (S37+).

    Build de release + loja (S37+).

Escolha para a Sessão 35 (a decidir depois da S34)

OPÇÃO 1 — Filtros de period/compare na UI do perfil (paridade com web S17/S20).
OPÇÃO 2 — Weekly/monthly charts no perfil (fl_chart ou similar — decisão de dependência).
OPÇÃO 3 — Busca de usuários (GET /users/search?q=, já existe).
OPÇÃO 4 — Export no mobile (paridade com web S21/S22/S29).
OPÇÃO 5 — Editar perfil (peso, altura, etc. — requer PUT /users/me ou similar, não existe ainda).
OPÇÃO 6 — Build de release + ícone + splash + política de privacidade + exclusão de conta (bloqueadores de loja).

Recomendação: S34 = perfil de terceiro + follow. S35 = busca de usuários. S36 = export no mobile. S37 = build de release + loja. ~5–7 sessões para o MVP em loja.

Recomendação final para a Sessão 34

Rodar Fase 0 completa (com handoff S33 commitado primeiro). Se tudo verde, começar o perfil de terceiro + follow seguindo o contrato acima — entrega incremental (user.dart + api.dart → profile_page.dart generalizado ou user_profile_page.dart → activity_card.dart onTap → main.dart rota), com flutter analyze entre cada entrega e validação manual (Chrome primeiro, Android depois se o Developer Mode estiver ligado).

⚠️ Antes de codar: Fase 1 da S34 precisa pedir os arquivos web equivalentes (web/src/pages/ProfilePage.tsx — já temos na S33, mas confirmar se mudou; web/src/hooks/useProfile.ts, useSocial.ts; web/src/api/social.ts) para portar a semântica de follow/canView. Não inventar do zero — o web é a fonte da verdade.

⚠️ A decisão de "o backend embutir user no /activities" fica para a S34. Com o perfil de terceiro, o authorUsernameOverride do self não basta (o card no perfil de terceiro precisa mostrar o username do alvo, não do viewer). Opções: (a) backend embutir user no /activities; (b) o UserProfilePage passa authorUsernameOverride: user.username do alvo (que já tem do GET /users/{id}). Recomendo (b) na S34 e (a) na S35 se aparecer mais um consumidor.

Em qualquer rota, handoff preventivo em ~70–80% do contexto — antes do fim, parar e entregar o HANDOFF completo da Sessão 34 neste mesmo formato (seções 0 a 9) + o percentual de prontidão atualizado.

SEÇÃO 9 — PEDIDO EXPLÍCITO DO USUÁRIO PARA O PRÓXIMO CHAT

O usuário disse textualmente ao fim da S21: "gostei da sua forma de trabalho código e teste. ficou bem fluido o trabalho. faça um handoff bem detalhado para o proximo chat e se tiver como pedir para que sempre trabalhe desta forma."

Na S22: "sempre vamos seguir o que você recomendar".
Na S23: "vamos deixar algumas coisas acordada, sempre seguir suas recomendações, mesmo que atualize apenas parte do código, sempre colocar o código completo, fazer o handoff completo e bem explicado para o próximo chat quando o limite estiver próximo do limite de 70% a 80%."
Na S24: confirmou "tudo como esperado" duas vezes.
Na S25 (abertura): reforçou os mesmos acordos. Tolerou 3 tropeços.
Na S26 (abertura): reforçou os mesmos acordos. Tolerou 2 tropeços.
Na S27 (abertura): rodou Fase 0 com o handoff S26 ainda não commitado — motivou a REGRA S27a.
Na S28 (abertura): handoff S27 já commitado. Fase 1 revelou escopo real (1 arquivo, não 6).
Na S29 (abertura): handoff S28 já commitado. Fase 1 revelou 2 arquivos. Entreguei activities.ts, o usuário colou erro do ESLint no-useless-assignment — corrigi, REGRA S29d.
Na S30 (abertura): handoff S29 já commitado. Recomendei OPÇÃO 2 (delta de Pace), ele aceitou. 1 tropeço (contagem "5x vs 6x", REGRA S29c), 1 achado (Select-String case-insensitive, S30a).
Na S31 (abertura): handoff S30 já commitado (3a154b1). Fase 0 limpa. Tropeços: (1) file_picker 13.x mudou a API (REGRA S31b); (2) o editor falhou 3 vezes em salvar o upload_page.dart (REGRA S31c); (3) teste manual revelou que na web file_picker retorna path == null mas readAsBytes() funciona — corrigi para aceitar bytes; (4) commit duplicado (a83ed82 + 71a00d4) — estado final íntegro, não vale rebase.
Na S32 (abertura): handoff S31 já commitado (f39820f, feito entre sessões — o handoff S31 listava 71a00d4 como HEAD, confirmando a REGRA S27a na prática). Fase 0 limpa. Fase 1 revelou 5 achados que mudaram o plano. Entrega incremental: 6 arquivos, 4 builds, todos analyze verde. 5 desvios de contagem no "esperado" (S32a–S32d consolidadas). Validação manual no Chrome: 11/11.
Na S33 (abertura): handoff S32 já commitado (919ccea). Fase 0 limpa (7 blocos, todos verdes). Fase 1 revelou 6 achados, incluindo o crítico: DeltaLine/PreviousDelta moram DENTRO do ProfilePage.tsx (não são componentes separados, como o handoff S30 dava a entender). Entrega incremental: 6 arquivos, 6 builds + 1 fix (avoid_relative_lib_imports → move format.dart para lib/utils/), todos analyze verde. 2 desvios de contagem (S33a, S33b — ambos reincidência de regras que eu mesmo escrevi). Validação manual no Chrome: 12/12 (com a sintética pra exercitar o delta). Perfil próprio + stats + delta + authorUsernameOverride funcionando.

Acordo novo na S31: percentual de prontidão anexo do handoff (não no meio da sessão, não na abertura). Entregar no fechamento, junto com o handoff, refletindo o estado ao fim da sessão.

Acordo novo na S32: manter o processo da S21–S31. Concretamente:

    Fase 0 obrigatória na ordem da REGRA S27b: handoff pendente → log/status → build/lint/analyze → docker/pytest/ruff → prod backend → prod frontend. Cada bloco só depois do anterior verde. Se algum falhar, parar e mostrar.

    Fase 1 — descoberta: pedir os arquivos relevantes (Get-Content -Encoding UTF8) com motivo. Não adivinhar estrutura, nomes de símbolos, campos de model/enum/schema. REGRA S28a: pedir TODOS os arquivos que o contrato toca. REGRA S30c: no mobile, pedir Get-ChildItem + os arquivos pivô antes de estimar.

    Fase 2 — contrato travado: escrever endpoint/auth/404/422/headers/formato (backend) ou componentes/props/estado/fluxo (front/mobile) antes de codar. Apresentar ao usuário.

    Fase 3 — entrega incremental: 1 arquivo por resposta, código completo (nunca placeholder — REGRA S21), com Select-String (save) + ruff/pytest (backend) ou npm run build/npm run lint (web) ou flutter analyze (mobile) entre cada entrega.

    Fase 3.5 — verificar save + commit: git hash-object ≠ git rev-parse HEAD:<arquivo> + git status --short mostra M. Só então pedir commit. Contar as ocorrências reais antes de anunciar "esperado Nx" (REGRA S29c + S32d + S33b: piso ou faixa, nunca exato sem contagem). No PS 5.1, usar -CaseSensitive ou \bTODO\b em Select-String (REGRA S30a). Se o editor não salvar, contornar com WriteAllText (REGRA S31c).

    Fase 4 — validação: local verde é pré-requisito; prod via HTTP/browser (web) ou app rodando (mobile) é o que fecha. Depois de git push, checar openapi.json (backend) e baixar index-*.js (front) antes de acusar bug. Se hash/comportamento antigo aparecer, aguardar 90 s (Vercel) ou >3 min (Render) antes de acusar bug. REGRA S28b: chunk com hash novo mas tamanho idêntico é renomeação de referência cruzada. REGRA S29b: hash servido pelo Vercel não bate com build local.

    Fase 5 — handoff preventivo em ~70–80% do contexto, no formato completo (seções 0 a 9), sem resumir, + percentual de prontidão atualizado (anexo do handoff, não no meio da sessão).

Regras novas da S33 (Seção 0, itens 41 e 42): alternância em Select-String é SEMPRE -Pattern (sem -SimpleMatch) — S33a; "esperado" de Select-String é SEMPRE piso/faixa — S33b.

O que funcionou nas S21–S33 (manter): ordem clara de fases, validação entre cada arquivo, contrato escrito antes, commits pequenos e temáticos, honestidade sobre os próprios erros e correção com base no output real do terminal (não na previsão), disposição de REDUZIR escopo quando a descoberta mostrou que o handoff anterior estava desatualizado (S28, S29, S30, S32, S33), e a consistência em aceitar os erros (API do plugin, contagem, lint, falso positivo, save do editor) na hora e corrigir/registrar, sem contornar. A S33 acrescentou: aceitar que o próprio assistente reincide em regras que escreveu (S33a, S33b), e registrar isso explicitamente no handoff em vez de esconder.