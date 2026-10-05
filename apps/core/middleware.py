"""Middleware de reescrita de prefixo de rota para deploy com subpath."""

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


def _strip_prefix(value: str, prefix: str) -> str:
    """Remove o prefixo apenas quando ele realmente estiver no caminho."""
    if value == prefix:
        return "/"
    if value.startswith(f"{prefix}/"):
        return value[len(prefix) :] or "/"
    return value


class PrefixMiddleware:
    """Remove o prefixo de publicação do path antes do roteamento Django."""

    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse]
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Reescreve path e path_info removendo o prefixo de publicação."""
        prefix: str = getattr(settings, "SCRIPT_PREFIX", "").rstrip("/")

        if prefix:
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"
            request.path_info = _strip_prefix(request.path_info, prefix)
            request.path = _strip_prefix(request.path, prefix)

        return self.get_response(request)
