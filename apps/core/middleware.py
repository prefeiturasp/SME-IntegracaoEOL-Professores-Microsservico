"""Middleware de reescrita de prefixo de rota para deploy com subpath."""

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class PrefixMiddleware:
    """Remove o prefixo de publicação do path antes do roteamento Django.

    Necessário quando o microsserviço é publicado sob um subpath (ex: /professores)
    via proxy reverso (nginx, Traefik), pois o Django roteia internamente sem prefixo.

    Configurado via SCRIPT_PREFIX no settings.py (variável de ambiente APP_PREFIX).
    """

    def __init__(self, get_response: callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Reescreve path e path_info removendo o prefixo de publicação."""
        prefix: str = getattr(settings, "SCRIPT_PREFIX", "")

        if prefix and request.path.startswith(prefix):
            request.path_info = request.path_info[len(prefix):] or "/"
            request.path = request.path[len(prefix):] or "/"

        return self.get_response(request)
