"""Testes do middleware de prefixo de rota."""

from django.http import HttpRequest, HttpResponse
from django.test import override_settings

from apps.core.middleware import PrefixMiddleware


def _process_request(path: str, path_info: str) -> dict[str, str]:
    captured = {}

    def get_response(request: HttpRequest) -> HttpResponse:
        captured["path"] = request.path
        captured["path_info"] = request.path_info
        return HttpResponse()

    request = HttpRequest()
    request.path = path
    request.path_info = path_info

    PrefixMiddleware(get_response)(request)
    return captured


@override_settings(SCRIPT_PREFIX="")
def test_prefix_vazio_nao_altera_caminhos():
    """Verifica path sem prefixo configurado."""
    result = _process_request("/api/v1/docs/", "/api/v1/docs/")

    assert result["path"] == "/api/v1/docs/"
    assert result["path_info"] == "/api/v1/docs/"


@override_settings(SCRIPT_PREFIX="/professores")
def test_remove_prefix_quando_proxy_mantem_subpath():
    """Verifica remoção de prefixo publicado."""
    result = _process_request(
        "/professores/api/v1/docs/",
        "/professores/api/v1/docs/",
    )

    assert result["path"] == "/api/v1/docs/"
    assert result["path_info"] == "/api/v1/docs/"


@override_settings(SCRIPT_PREFIX="/professores")
def test_nao_corta_path_info_quando_apenas_path_tem_script_prefix():
    """Verifica preservação quando path_info já vem sem prefixo."""
    result = _process_request(
        "/professores/api/v1/professores/6576753/",
        "/api/v1/professores/6576753/",
    )

    assert result["path"] == "/api/v1/professores/6576753/"
    assert result["path_info"] == "/api/v1/professores/6576753/"
