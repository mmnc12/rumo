"""Erros de negócio reutilizáveis pelos services."""


class ServiceError(Exception):
    """Erro de negócio com status HTTP embutido."""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(ServiceError):
    """Recurso não encontrado (404)."""

    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404)


class ConflictError(ServiceError):
    """Conflito de estado (409)."""

    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409)


class BadRequestError(ServiceError):
    """Input inválido (400)."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400)