Rumo

App de registro e acompanhamento de atividades físicas (corrida, caminhada, ciclismo, trilha, natação, outro). Backend FastAPI + Postgres/PostGIS, frontend web React, app mobile Flutter. Importa GPX/FIT, calcula métricas (distância, pace, elevação, calorias), guarda a rota como LINESTRING PostGIS e permite exportar em CSV/GPX (unitário e em lote em ZIP).

Estado atual: ver docs/HANDOFF.md — é a fonte da verdade do que está feito, do que está pendente e dos contratos travados. Este README é só um cheat sheet.
Estrutura
text

D:\Rumo
├── backend/        FastAPI + SQLAlchemy + Alembic + PostGIS + pytest
├── web/            React 19 + Vite + TypeScript + Tailwind + react-leaflet + recharts
├── mobile/         Flutter (flutter_map + OSM/Esri)
├── docs/
│   └── HANDOFF.md  handoff da sessão mais recente
└── README.md       este arquivo

Rodar local
Backend (pytest com Docker de teste na 5433)
powershell

# PowerShell via Win+R (fora do VS Code / Windows Terminal)
cd D:\Rumo\backend
docker compose -f docker-compose.test.yml up -d
docker ps -a --filter "name=rumo_postgres_test"      # deve mostrar Up … (healthy)
docker exec rumo_postgres_test pg_isready -h 127.0.0.1 -p 5432
.\venv\Scripts\Activate.ps1                          # UM ponto, NÃO dois
python -m pytest -q                                  # esperado: 164 passed
ruff check .

    Venv única: D:\Rumo\backend\venv (Python 3.13.7). Não usar py -3 deste Windows (aponta para 3.14, incompatível).

    Se precisar recriar: py -3.13 -m venv D:\Rumo\backend\venv.

    docker ps sozinho esconde container parado — usar sempre docker ps -a --filter "name=rumo_postgres_test".

Web (build + lint)
powershell

cd D:\Rumo\web
npm run build      # tsc -b && vite build
npm run lint       # eslint .

Scripts disponíveis: dev, build, lint, preview (ver web/package.json).
Mobile (analyze)
powershell

& "C:\Users\nasci\flutter\bin\flutter.bat" analyze

Se o terminal não reconhecer flutter mesmo com o bin no PATH (problema conhecido no PowerShell deste Windows), usar o caminho absoluto do .bat como acima.
Endpoints principais

Base local/prod: https://rumo-api-5s0b.onrender.com. Auth: Bearer <jwt> (obtido em POST /auth/login, form-urlencoded).
Método	Path	Auth	O que faz
POST	/auth/login	—	Login (form-urlencoded). Retorna access_token.
POST	/auth/register	—	Cadastro.
GET	/auth/me	Bearer	Identidade do usuário logado. Não é /users/me (esse devolve 422).
GET	/activities	Bearer	Lista paginada (limit, offset, user_id opcional).
GET	/activities/{id}	Bearer	Detalhe.
POST	/activities/upload	Bearer	Upload GPX/FIT (multipart).
DELETE	/activities/{id}	Bearer	Apaga (dono).
GET	/activities/{id}/track	Bearer	Rota (LineString GeoJSON [lon, lat] + bbox + n_points). 404 se sem rota.
GET	/activities/{id}/export?format=csv|gpx	Bearer	Export unitário. GPX exige rota.
GET	/activities/export?format=csv|gpx[&from=YYYY-MM-DD][&to=YYYY-MM-DD]	Bearer (self-only)	Export em lote (ZIP com N arquivos). 0 atividades → ZIP vazio; from > to → 422.
GET	/activities/stats/{summary,weekly,monthly,by-type}	Bearer	Stats do usuário. by-type aceita period=<all|90d|1y> e compare=<prev|yoy>.
GET	/users/{user_id}/stats/{summary,weekly,monthly,by-type}	Bearer	Stats públicas de terceiros. Self → 200; segue → 200; não segue → 403; não existe → 404.
GET	/feed	Bearer	Feed paginado de quem você segue.
POST/DELETE	/activities/{id}/like	Bearer	Curtir / descurtir.
GET/POST	/activities/{id}/comments	Bearer	Listar / criar comentário.
DELETE	/comments/{id}	Bearer	Apagar comentário.
POST/DELETE	/users/{id}/follow	Bearer	Seguir / deixar de seguir.
GET	/users/{id}/{followers,following}	Bearer	Listas paginadas.
GET	/notifications	Bearer	Notificações (limit, offset).
GET	/notifications/unread-count	Bearer	Contador de não lidas.
POST	/notifications/{id}/read	Bearer	Marcar uma como lida.
POST	/notifications/read-all	Bearer	Marcar todas como lidas.

Contratos detalhados (headers, formato de resposta, ordem de bbox, casos de borda) estão em docs/HANDOFF.md — seção 4.
Contas de teste (produção)

    prod@rumo.com / senha12345 — id 01a12c83-be2a-71fa-b966-1c93ca64f341, 6 atividades, 26.443 m.

    Prod2 — id 01a141e7-5ea4-7600-8959-19145475ad0a, 2 atividades, 14.643 m, pace 496,89 s/km, 0 kcal. prod segue Prod2.

    Para o cenário "terceiro NÃO seguido": usar /users/search?q=a e escolher um id que não seja prod nem Prod2.

Produção

    Backend (Render): https://rumo-api-5s0b.onrender.com

    Docs (FastAPI/Swagger): https://rumo-api-5s0b.onrender.com/docs

    Frontend web (Vercel): https://rumo-wheat.vercel.app

Stack (versões exatas)
Backend

Python 3.13.7 (venv em backend/venv) · FastAPI · SQLAlchemy · Alembic · PostGIS · pytest · ruff. Versões exatas em backend/requirements.txt.
Web (web/package.json)

React ^19.2.8 · React DOM ^19.2.8 · Vite ^8.3.0 · TypeScript ~6.0.2 · react-router-dom ^7.18.4 · @tanstack/react-query ^5.104.2 · react-leaflet ^5.0.0 · leaflet ^1.9.4 · recharts ^3.10.1 · zod ^4.6.6 · react-hook-form ^7.90.0 · @hookform/resolvers ^5.9.1 · Tailwind CSS ^3.4.19 · ESLint ^10.10.0.
Mobile (mobile/pubspec.yaml)

rumo_mobile · Dart SDK ^3.13.7 · Flutter 3.47.9 (instalado em C:\Users\nasci\flutter) · go_router ^18.1.2 · flutter_map ^8.3.2 · http ^1.6.0 · flutter_secure_storage ^11.2.0 · latlong2 ^0.10.1.
Convenções rápidas

    Terminal: PowerShell 5.1 via Win+R (fora do VS Code / Windows Terminal) — evita cache de sessão e problemas de PATH.

    Get-Content: sempre com -Encoding UTF8 (sem isso, acentos viram mojibake).

    Invoke-WebRequest: sempre com -UseBasicParsing (evita prompt de "Risco de Execução de Script" no PS 5.1).

    git log: sempre com --no-pager (ou $env:PAGER="") — sem isso abre o less e trava o terminal.

    Validar deploy antes de acusar bug: backend → checar /openapi.json para a rota nova; front → baixar index-*.js da Vercel e procurar o chunk dentro dele (não procurar no HTML). Se o hash antigo aparecer, aguardar 90 s e refazer o teste (Vercel pode demorar >90 s no primeiro deploy após push).

    Antes de git restore/git checkout: rodar git status --short <arquivo> + git --no-pager log --oneline -3 -- <arquivo> para confirmar que o último commit é anterior à mudança quebrada.