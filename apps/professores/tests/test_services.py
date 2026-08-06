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

    monkeypatch.setattr(
        services.repositories, "atribuicao_verificar_data", fake
    )

    resultado = services.atribuicao_verificar_data(
        "7654321",
        2112345,
        "2024-02-02",
    )

    assert resultado is True
    assert chamadas["args"] == ("7654321", 2112345, date(2024, 2, 2))


def test_atribuicao_disciplina_data_converte_data(monkeypatch):
    """Verifica conversao da data opcional."""
    chamadas = {}

    def fake(
        codigo_rf,
        codigo_turma,
        disciplina_id,
        data_consulta=None,
    ):
        chamadas["args"] = (
            codigo_rf,
            codigo_turma,
            disciplina_id,
            data_consulta,
        )
        return True

    monkeypatch.setattr(
        services.repositories,
        "atribuicao_disciplina_data",
        fake,
    )

    resultado = services.atribuicao_disciplina_data(
        "7654321",
        2112345,
        138,
        "2024-02-02",
    )

    assert resultado is True
    assert chamadas["args"] == (
        "7654321",
        2112345,
        138,
        date(2024, 2, 2),
    )


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

    monkeypatch.setattr(services.repositories, "titulares_por_turmas", fake)

    resultado = services.titulares_por_turmas(["2112345"])

    assert resultado == [{"turma_id": 2112345}]
    assert chamadas["codigos"] == [2112345]


def test_buscar_turmas_professor_todos_anos_delega(monkeypatch):
    """Delega a consulta de todos os anos ao repository."""
    esperado = [{"ano_letivo": "2024"}]

    def fake(codigo_rf):
        assert codigo_rf == "7654321"
        return esperado

    monkeypatch.setattr(
        services.repositories,
        "buscar_turmas_professor_todos_anos",
        fake,
    )

    resultado = services.buscar_turmas_professor_todos_anos("7654321")

    assert resultado == esperado


def test_titulares_por_turma_converte_data_e_delega(monkeypatch):
    """Converte a data opcional e delega os filtros ao repository."""
    chamadas = {}

    def fake(codigo_turma, codigo_rf=None, data_referencia=None):
        chamadas["args"] = (codigo_turma, codigo_rf, data_referencia)
        return [{"turma_id": codigo_turma}]

    monkeypatch.setattr(services.repositories, "titulares_por_turma", fake)

    resultado = services.titulares_por_turma(
        2112345,
        codigo_rf="7654321",
        data_referencia="2024-02-02",
    )

    assert resultado == [{"turma_id": 2112345}]
    assert chamadas["args"] == (
        2112345,
        "7654321",
        date(2024, 2, 2),
    )


def test_buscar_abrangencia_funcionario_perfil_delega(monkeypatch):
    """Service delega a abrangência ao repositories."""
    chamadas = {}

    def fake(login, id_perfil):
        chamadas["args"] = (login, id_perfil)
        return {"abrangencia": None, "dres": []}

    monkeypatch.setattr(
        services.repositories,
        "buscar_abrangencia_funcionario_perfil",
        fake,
    )

    resultado = services.buscar_abrangencia_funcionario_perfil("111", "p")

    assert resultado == {"abrangencia": None, "dres": []}
    assert chamadas["args"] == ("111", "p")


def test_turmas_atribuidas_ue_delega(monkeypatch):
    """Service delega as turmas por vínculo de UE ao repositories."""
    chamadas = {}

    def fake(codigo_rf, cargos, codigo_dre):
        chamadas["args"] = (codigo_rf, cargos, codigo_dre)
        return [{"codigo_turma": 10}]

    monkeypatch.setattr(services.repositories, "turmas_atribuidas_ue", fake)

    resultado = services.turmas_atribuidas_ue("111", [3360], "108100")

    assert resultado == [{"codigo_turma": 10}]
    assert chamadas["args"] == ("111", [3360], "108100")
