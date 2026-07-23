"""Testes dos services do dominio de funcionarios."""

import pytest

from apps.funcionarios import services


def test_funcionarios_por_lista_cargos_sem_cargos_usa_ue(monkeypatch):
    """Verifica consulta da unidade quando cargos não são informados."""
    chamadas = {}

    def fake(codigo_ue):
        chamadas["codigo_ue"] = codigo_ue
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repositories, "funcionarios_por_ue", fake)

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

    monkeypatch.setattr(services.repositories, metodo, fake)

    resultado = funcao("000532", ["1", "2"])

    assert resultado == [{"ok": True}]
    assert chamadas["args"] == ("000532", [1, 2])


def test_usuarios_sgp_perfil_placeholder_sem_dre_rf_retorna_400(monkeypatch):
    """Verifica mensagem legada para perfil placeholder sem DRE ou RF."""
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: True,
    )

    resultado = services.usuarios_sgp_por_perfil("perfil")

    assert resultado.status_code == 400
    assert (
        resultado.payload
        == services.repositories.MENSAGEM_ERRO_PERFIL_SEM_DRE_RF
    )


def test_usuarios_sgp_sem_resultado_retorna_404(monkeypatch):
    """Verifica 404 quando perfil nao retorna usuarios."""
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )
    monkeypatch.setattr(
        services.repositories,
        "usuarios_sgp_por_perfil",
        lambda *args, **kwargs: [],
    )

    resultado = services.usuarios_sgp_por_perfil("perfil")

    assert resultado.status_code == 404
    assert resultado.payload is None


def test_usuarios_sgp_com_dre_sem_resultado_retorna_200(monkeypatch):
    """Verifica resposta legada quando consulta por DRE vem vazia."""
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )
    monkeypatch.setattr(
        services.repositories,
        "usuarios_sgp_por_perfil",
        lambda *args, **kwargs: [],
    )

    resultado = services.usuarios_sgp_por_perfil(
        "perfil",
        codigo_dre="108100",
    )

    assert resultado.status_code == 200
    assert resultado.payload == []


def test_funcionarios_sgp_dre_converte_funcao(monkeypatch):
    """Verifica conversao de funcao de atividade opcional."""
    chamadas = {}
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )

    def fake(*args, **kwargs):
        chamadas["kwargs"] = kwargs
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repositories, "funcionarios_sgp_dre", fake)

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

    monkeypatch.setattr(services.repositories, metodo, fake)

    resultado = funcao({"invalido": True})

    assert resultado == []
    assert chamadas["lista"] == []


def test_buscar_funcionarios_mapeia_filtros_do_payload(monkeypatch):
    """Verifica mapeamento dos filtros do payload para o repositories."""
    chamadas = {}

    def fake(codigo_rf, codigo_ue, nome_servidor):
        chamadas["kwargs"] = {
            "codigo_rf": codigo_rf,
            "codigo_ue": codigo_ue,
            "nome_servidor": nome_servidor,
        }
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repositories, "buscar_funcionarios", fake)

    resultado = services.buscar_funcionarios(
        {"CodigoRF": "7654321", "codigoUE": "000532", "NomeServidor": "Ana"}
    )

    assert resultado == [{"codigo_rf": "7654321"}]
    assert chamadas["kwargs"] == {
        "codigo_rf": "7654321",
        "codigo_ue": "000532",
        "nome_servidor": "Ana",
    }


def test_buscar_funcionarios_payload_invalido_usa_dict_vazio(monkeypatch):
    """Payload não-dict resulta em filtros vazios."""
    chamadas = {}

    def fake(codigo_rf, codigo_ue, nome_servidor):
        chamadas["kwargs"] = (codigo_rf, codigo_ue, nome_servidor)
        return []

    monkeypatch.setattr(services.repositories, "buscar_funcionarios", fake)

    resultado = services.buscar_funcionarios(None)

    assert resultado == []
    assert chamadas["kwargs"] == (None, None, None)
