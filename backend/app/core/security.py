from passlib.context import CryptContext

# Contexto de hashing: bcrypt é o padrão recomendado hoje
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)