"""Testes dos services do dominio de funcionarios."""

import pytest

from apps.funcionarios import services


def test_funcionarios_por_lista_cargos_sem_cargos_usa_ue(monkeypatch):
    """Verifica consulta da unidade quando cargos não são informados."""
    chamadas = {}

    def fake(codigo_ue):
        chamadas["codigo_ue"] = codigo_ue
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repository, "funcionarios_por_ue", fake)

    resultado = services.funcionarios_por_lista_cargos("000532", [])

    assert resultado == [{"codigo_rf": "7654321"}]
    assert chamadas["codigo_ue"] == "000532"


@pytest.mark.parametrize(
    ("funcao", "metodo"),
    [
        (
            services.funcionarios_por_lista_funcoes_atividade,
            "funcionarios_por_lista_funcoes_atividade",
        ),
        (
            services.funcionarios_por_lista_funcoes_externas,
            "funcionarios_por_lista_funcoes_externas",
        ),
    ],
)
def test_funcoes_query_converte_lista(monkeypatch, funcao, metodo):
    """Verifica conversao de funcoes recebidas por query string."""
    chamadas = {}

    def fake(codigo_ue, funcoes):
        chamadas["args"] = (codigo_ue, funcoes)
        return [{"ok": True}]

    monkeypatch.setattr(services.repository, metodo, fake)

    resultado = funcao("000532", ["1", "2"])

    assert resultado == [{"ok": True}]
    assert chamadas["args"] == ("000532", [1, 2])


def test_usuarios_sgp_perfil_placeholder_sem_dre_rf_retorna_400(monkeypatch):
    """Verifica mensagem legada para perfil placeholder sem DRE ou RF."""
    monkeypatch.setattr(
        services.repository,
        "perfil_placeholder_invalido",
        lambda id_perfil: True,
    )

    resultado = services.usuarios_sgp_por_perfil("perfil")

    assert resultado.status_code == 400
    assert (
        resultado.payload
        == services.repository.MENSAGEM_ERRO_PERFIL_SEM_DRE_RF
    )


def test_usuarios_sgp_sem_resultado_retorna_404(monkeypatch):
    """Verifica 404 quando perfil nao retorna usuarios."""
    monkeypatch.setattr(
        services.repository,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )
    monkeypatch.setattr(
        services.repository,
        "usuarios_sgp_por_perfil",
        lambda *args, **kwargs: [],
    )

    resultado = services.usuarios_sgp_por_perfil("perfil")

    assert resultado.status_code == 404
    assert resultado.payload is None


def test_funcionarios_sgp_dre_converte_funcao(monkeypatch):
    """Verifica conversao de funcao de atividade opcional."""
    chamadas = {}
    monkeypatch.setattr(
        services.repository,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )

    def fake(*args, **kwargs):
        chamadas["kwargs"] = kwargs
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repository, "funcionarios_sgp_dre", fake)

    resultado = services.funcionarios_sgp_dre(
        "perfil",
        "108100",
        codigo_funcao_atividade="1",
    )

    assert resultado.status_code == 200
    assert chamadas["kwargs"]["codigo_funcao_atividade"] == 1


@pytest.mark.parametrize(
    ("funcao", "metodo"),
    [
        (services.buscar_por_lista_rf, "buscar_por_lista_rf_func"),
        (services.buscar_por_lista_login, "buscar_por_lista_login"),
    ],
)
def test_payload_invalido_usa_lista_vazia(monkeypatch, funcao, metodo):
    """Verifica retorno vazio para entrada inválida."""
    chamadas = {}

    def fake(lista):
        chamadas["lista"] = lista
        return []

    monkeypatch.setattr(services.repository, metodo, fake)

    resultado = funcao({"invalido": True})

    assert resultado == []
    assert chamadas["lista"] == []
