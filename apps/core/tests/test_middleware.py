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
    result = _process_request("/api/docs/", "/api/docs/")

    assert result["path"] == "/api/docs/"
    assert result["path_info"] == "/api/docs/"


@override_settings(SCRIPT_PREFIX="/professores")
def test_remove_prefix_quando_proxy_mantem_subpath():
    result = _process_request(
        "/professores/api/docs/",
        "/professores/api/docs/",
    )

    assert result["path"] == "/api/docs/"
    assert result["path_info"] == "/api/docs/"


@override_settings(SCRIPT_PREFIX="/professores")
def test_nao_corta_path_info_quando_apenas_path_tem_script_prefix():
    result = _process_request(
        "/professores/api/professores/6576753/",
        "/api/professores/6576753/",
    )

    assert result["path"] == "/api/professores/6576753/"
    assert result["path_info"] == "/api/professores/6576753/"
