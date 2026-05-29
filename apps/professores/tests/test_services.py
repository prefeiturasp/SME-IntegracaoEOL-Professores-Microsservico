"""Testes dos services do dominio de professores."""

from datetime import date

import pytest

from apps.professores import services


def test_atribuicao_verificar_data_converte_data(monkeypatch):
    """Verifica conversao de data opcional."""
    chamadas = {}

    def fake(codigo_rf, codigo_turma, data_consulta):
        chamadas["args"] = (codigo_rf, codigo_turma, data_consulta)
        return True

    monkeypatch.setattr(services.repository, "atribuicao_verificar_data", fake)

    resultado = services.atribuicao_verificar_data(
        "7654321",
        2112345,
        "2024-02-02",
    )

    assert resultado is True
    assert chamadas["args"] == ("7654321", 2112345, date(2024, 2, 2))


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [("true", True), ("TRUE", True), ("false", False), (None, False)],
)
def test_atribuicao_disciplina_data_converte_territorio(
    monkeypatch,
    valor,
    esperado,
):
    """Verifica conversao do indicador de territorio do saber."""
    chamadas = {}

    def fake(
        codigo_rf,
        codigo_turma,
        disciplina_id,
        data_consulta=None,
        territorio_saber=False,
    ):
        chamadas["args"] = (
            codigo_rf,
            codigo_turma,
            disciplina_id,
            data_consulta,
            territorio_saber,
        )
        return territorio_saber

    monkeypatch.setattr(
        services.repository,
        "atribuicao_disciplina_data",
        fake,
    )

    resultado = services.atribuicao_disciplina_data(
        "7654321",
        2112345,
        138,
        None,
        valor,
    )

    assert resultado is esperado
    assert chamadas["args"][-1] is esperado


def test_atribuicao_disciplina_datatick_sem_tick_retorna_400():
    """Verifica resposta legada quando tick nao e informado."""
    resultado = services.atribuicao_disciplina_datatick(
        "7654321",
        2112345,
        138,
        None,
    )

    assert resultado.status_code == 400
    assert resultado.payload == {
        "detail": "Deve ser informada uma data valida"
    }


def test_atribuicao_recorrencia_datas_sem_ticks_retorna_400():
    """Verifica resposta legada quando ticks nao sao informados."""
    resultado = services.atribuicao_recorrencia_datas(
        "7654321",
        2112345,
        138,
        [],
    )

    assert resultado.status_code == 400
    assert resultado.payload == {
        "detail": "\u00c9 necess\u00e1rio informar as datas em ticks!"
    }


@pytest.mark.parametrize("payload", [[], {"codigo_turma": 2112345}])
def test_atribuicao_turmas_lista_payload_invalido(payload):
    """Verifica entrada inválida de turmas."""
    resultado = services.atribuicao_turmas_lista("7654321", 138, payload)

    if payload == []:
        assert resultado.status_code == 400
        assert resultado.payload == {"detail": "Informe uma turma!"}
    else:
        assert resultado.status_code == 200
        assert resultado.payload == []


def test_atribuicao_turmas_lista_codigo_invalido_retorna_vazio():
    """Verifica codigo de turma invalido como lista vazia."""
    resultado = services.atribuicao_turmas_lista(
        "7654321",
        138,
        ["invalido"],
    )

    assert resultado.status_code == 200
    assert resultado.payload == []


def test_titulares_por_turmas_converte_codigos(monkeypatch):
    """Verifica conversao dos codigos de turma."""
    chamadas = {}

    def fake(codigos_turmas):
        chamadas["codigos"] = codigos_turmas
        return [{"turma_id": 2112345}]

    monkeypatch.setattr(services.repository, "titulares_por_turmas", fake)

    resultado = services.titulares_por_turmas(["2112345"])

    assert resultado == [{"turma_id": 2112345}]
    assert chamadas["codigos"] == [2112345]
