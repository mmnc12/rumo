from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.config import settings
from app.core.rate_limit import limiter, rate_limit_handler
from app.database import engine
from app.routers import (
    activities,
    auth,
    comments,
    feed,
    notifications,
    photos,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda no startup e shutdown da aplicação."""
    # Startup: testar conexão com o banco
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT version();"))
        version = result.scalar()
        print(f"✅ Conectado ao banco: {version[:50]}...")

        result = await conn.execute(text("SELECT PostGIS_Version();"))
        postgis = result.scalar()
        print(f"✅ PostGIS: {postgis}")

    print(f"🚀 {settings.PROJECT_NAME} iniciada em modo {settings.ENVIRONMENT}")
    yield
    # Shutdown: fechar pool
    await engine.dispose()
    print("👋 Aplicação encerrada")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API do Rumo — Sistema de monitoramento de exercícios físicos",
    lifespan=lifespan,
)

# CORS — libera o frontend (Vercel) e mobile a consumirem a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting: estado e handler de 429.
# Sem SlowAPIMiddleware — o limite é cirúrgico por endpoint (decorators),
# não global, para não punir usuário legítimo scrollando o feed.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.include_router(auth.router)
app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(feed.router, prefix="/feed", tags=["feed"])
app.include_router(comments.router, tags=["comments"])
app.include_router(photos.router, tags=["photos"])
app.include_router(notifications.router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "nome": settings.PROJECT_NAME,
        "versao": settings.VERSION,
        "ambiente": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Verifica se a API e o banco estão funcionando."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"erro: {e}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "ambiente": settings.ENVIRONMENT,
    }