"""Configuração de rate limiting da aplicação.

Centraliza o Limiter do slowapi e o handler de 429 para que main.py
apenas registre o estado e o exception handler, sem lógica de limite aqui.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# key_func por IP remoto. O Render free tier fica atrás de proxy;
# get_remote_address lê X-Forwarded-For quando presente, então o IP
# do cliente é usado, não o IP do proxy.
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Retorna 429 com mensagem em português para o frontend exibir."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Muitas requisições. Tente novamente em instantes."},
    )