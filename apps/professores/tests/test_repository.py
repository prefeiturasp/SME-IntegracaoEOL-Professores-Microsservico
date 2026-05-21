"""Testes dos repositories do dominio de professores."""

from datetime import date
from types import SimpleNamespace

import pytest

from apps.professores import repository
from apps.professores.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoAula,
    CargoBaseServidor,
    Professor,
    SerieTurmaGrade,
)

pytestmark = pytest.mark.django_db


def _cria_professor_com_atribuicao(
    codigo_rf: str,
    codigo_turma: int,
    codigo_ue: str = "000532",
) -> None:
    """Cria professor com atribuicao para testes de repository."""
    professor = Professor.objects.create(
        codigo_rf=codigo_rf,
        nome=f"Professor {codigo_rf}",
        cpf=f"000000{codigo_rf}",
    )
    cargo = CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo,
        codigo_unidade_educacao=codigo_ue,
        codigo_turma_escola=codigo_turma,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao_aula=date(2024, 2, 1),
    )


def test_autocomplete_filtra_por_ue(atribuicao):
    """Verifica filtro direto por unidade educacional."""
    resultado = repository.autocomplete_professores(
        2024,
        "108100",
        ue_id="000532",
    )

    assert resultado == [
        {"codigo_rf": "7654321", "nome_servidor": "Ana Silva"}
    ]


def test_autocomplete_limita_dez_resultados(db):
    """Verifica limite legado de resultados do autocomplete."""
    for indice in range(11):
        _cria_professor_com_atribuicao(
            f"90000{indice}",
            2110000 + indice,
        )

    resultado = repository.autocomplete_professores(2024, "")

    assert len(resultado) == 10


def test_autocomplete_limite_interrompe_antes_de_externos(
    db,
    atribuicao_externa,
):
    """Verifica interrupcao quando efetivos ja atingiram o limite."""
    for indice in range(10):
        _cria_professor_com_atribuicao(
            f"91000{indice}",
            2120000 + indice,
        )

    resultado = repository.autocomplete_professores(2024, "")

    assert len(resultado) == 10
    assert all(item["codigo_rf"] != "98765432100" for item in resultado)


def test_autocomplete_inclui_professor_externo(atribuicao_externa):
    """Verifica inclusao de contrato externo no autocomplete."""
    resultado = repository.autocomplete_professores(2024, "")

    assert resultado[0]["codigo_rf"] == "98765432100"


def test_helpers_retornam_vazio_quando_nao_ha_codigos():
    """Verifica retornos vazios dos mapas auxiliares."""
    assert repository._serie_turma_map([]) == {}
    assert repository._turma_map([]) == {}


def test_helpers_retornam_mapas_preenchidos(ue, turma):
    """Verifica montagem dos mapas auxiliares com dados."""
    SerieTurmaGrade.objects.create(
        codigo_serie_grade=1040353,
        codigo_turma=turma.codigo_turma,
        codigo_escola=ue.codigo_ue,
        codigo_escola_grade=100,
    )
    atribuicao = SimpleNamespace(codigo_serie_grade=1040353)

    assert repository._serie_turma_map([atribuicao]) == {1040353: 2112345}
    assert repository._turma_map([2112345]) == {2112345: turma}


def test_codigo_turma_retorna_none_sem_turma_ou_serie():
    """Verifica atribuicao sem turma e sem serie-grade."""
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=None,
    )

    assert repository._codigo_turma(atribuicao) is None


def test_codigo_turma_usa_mapa_informado():
    """Verifica resolucao da turma por mapa pre-carregado."""
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=1040353,
    )

    assert repository._codigo_turma(atribuicao, {1040353: 2112345}) == 2112345


def test_codigo_turma_busca_serie_quando_mapa_nao_foi_informado(ue):
    """Verifica resolucao da turma pela serie-grade."""
    SerieTurmaGrade.objects.create(
        codigo_serie_grade=1040353,
        codigo_turma=2112345,
        codigo_escola=ue.codigo_ue,
        codigo_escola_grade=100,
    )
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=1040353,
    )

    assert repository._codigo_turma(atribuicao) == 2112345


def test_codigo_turma_retorna_none_quando_serie_nao_existe():
    """Verifica serie-grade inexistente."""
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=999999,
    )

    assert repository._codigo_turma(atribuicao) is None


def test_atribuicao_disciplina_territorio_filtra_por_data():
    """Verifica atribuicao de territorio do saber com data."""
    AgrupamentoAtribuicaoTerritorioSaber.objects.create(
        codigo_agrupamento=1,
        rf_professor="7654321",
        codigo_turma=2112345,
        dt_inicio_atribuicao=date(2024, 2, 1),
    )

    assert repository.atribuicao_disciplina_data(
        "7654321",
        2112345,
        138,
        date(2024, 2, 2),
        territorio_saber=True,
    )


def test_titulares_por_turma_agrupamento_com_componentes():
    """Verifica titulares agrupados com componentes informados."""
    AgrupamentoAtribuicaoTerritorioSaber.objects.create(
        codigo_agrupamento=1,
        rf_professor="7654321",
        codigo_turma=2112345,
        codigos_componentes_curriculares="138, 139",
        dt_inicio_atribuicao=date(2024, 2, 1),
    )

    resultado = repository.titulares_por_turma_agrupamento(
        2112345,
        True,
        codigo_rf="7654321",
        data_referencia=date(2024, 2, 2),
    )

    assert [item["disciplinas_id"] for item in resultado] == ["138", "139"]


def test_titulares_por_turma_agrupamento_sem_componentes():
    """Verifica titulares agrupados sem componentes informados."""
    AgrupamentoAtribuicaoTerritorioSaber.objects.create(
        codigo_agrupamento=1,
        rf_professor="7654321",
        codigo_turma=2112345,
    )

    resultado = repository.titulares_por_turma_agrupamento(2112345, True)

    assert resultado[0]["disciplinas_id"] is None
