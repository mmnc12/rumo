from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Pasta raiz do backend (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Configurações da aplicação, carregadas de variáveis de ambiente."""

    # Ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Banco de dados
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT (ainda não usado, mas já deixamos pronto)
    SECRET_KEY: str = "dev-secret-key-nao-use-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Metadados da API
    PROJECT_NAME: str = "Rumo API"
    VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()