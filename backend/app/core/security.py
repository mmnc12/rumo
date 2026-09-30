from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Contexto de hashing: bcrypt é o padrão recomendado hoje
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===== Hash de senha =====

def hash_password(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT =====

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """
    Gera um JWT de acesso.

    - `subject`: geralmente o id do usuário (vai no campo 'sub' do token)
    - `expires_delta`: tempo de vida customizado (senão usa o default do .env)
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(subject),   # subject (obrigatório no padrão JWT)
        "exp": expire,         # expiration time
        "iat": datetime.now(timezone.utc),  # issued at
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida um JWT.

    Retorna o payload (dict) ou levanta JWTError se o token for inválido/expirado.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# Exporta JWTError para quem importar daqui
__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]