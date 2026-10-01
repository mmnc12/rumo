from contextlib import asynccontextmanager
from app.routers import auth, activities


from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import engine


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

app.include_router(auth.router)
app.include_router(activities.router)

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

