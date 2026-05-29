"""Testes dos repositories do dominio de funcionarios."""

import pytest

from apps.funcionarios import repository
from apps.professores.models import FuncionarioUnidadeEducacional

pytestmark = pytest.mark.django_db


def test_dre_de_ue_retorna_none_sem_codigo():
    """Verifica consulta de DRE sem UE informada."""
    assert repository._dre_de_ue(None) is None


def test_dre_de_ue_consulta_e_armazena_cache(ue):
    """Verifica busca de DRE por UE com cache local."""
    repository._UE_DRE_CACHE.clear()

    assert repository._dre_de_ue(ue.codigo_ue) == "108100"
    assert repository._UE_DRE_CACHE[ue.codigo_ue] == "108100"


def test_dre_de_ue_guarda_none_quando_ue_nao_existe():
    """Verifica cache para UE inexistente."""
    repository._UE_DRE_CACHE.clear()

    assert repository._dre_de_ue("999999") is None
    assert repository._UE_DRE_CACHE["999999"] is None


def test_funcionarios_por_lista_funcoes_externas_sem_funcoes():
    """Verifica retorno vazio sem funcoes externas."""
    assert (
        repository.funcionarios_por_lista_funcoes_externas("000532", []) == []
    )


def test_nome_funcionario_prioriza_nome_social(lotacao):
    """Verifica uso de nome social no funcionario."""
    funcionario = FuncionarioUnidadeEducacional.objects.get(
        codigo_rf="7654321",
    )
    funcionario.nome_social = "Ana Social"
    funcionario.save()

    assert repository._nome_funcionario(funcionario) == "Ana Social"


def test_lotacoes_ativas_filtra_sem_data_fim(lotacao):
    """Verifica filtro de lotacoes ativas."""
    assert repository._lotacoes_ativas().count() == 1


def test_funcionarios_por_ue_cargo_filtra_cargo(lotacao):
    """Verifica funcionarios por UE e cargo."""
    resultado = repository.funcionarios_por_ue_cargo("000532", 3379)

    assert resultado[0]["codigo_rf"] == "7654321"


def test_funcionarios_por_lista_cargos_retorna_cargo(lotacao):
    """Verifica funcionarios por lista de cargos."""
    resultado = repository.funcionarios_por_lista_cargos("000532", [3379])

    assert resultado[0]["funcionario_rf"] == "7654321"


def test_funcionarios_por_funcao_atividade_retorna_funcionario(
    funcao_atividade,
):
    """Verifica funcionarios por funcao de atividade."""
    resultado = repository.funcionarios_por_funcao_atividade("000532", 1)

    assert resultado[0]["codigo_rf"] == "7654321"


def test_funcionarios_por_lista_funcoes_atividade_retorna_funcionario(
    funcao_atividade,
):
    """Verifica funcionarios por lista de funcoes de atividade."""
    resultado = repository.funcionarios_por_lista_funcoes_atividade(
        "000532",
        [1],
    )

    assert resultado[0]["funcionario_rf"] == "7654321"


def test_funcionarios_por_funcao_externa_retorna_contrato(contrato_externo):
    """Verifica funcionarios externos por funcao."""
    resultado = repository.funcionarios_por_funcao_externa("000532", 5)

    assert resultado[0]["cpf"] == "98765432100"


def test_funcionarios_por_lista_funcoes_externas_retorna_contrato(
    contrato_externo,
):
    """Verifica funcionarios externos por lista de funcoes."""
    resultado = repository.funcionarios_por_lista_funcoes_externas(
        "000532",
        [5],
    )

    assert resultado[0]["cpf"] == "98765432100"


def test_nome_cpf_servidor_retorna_funcionario_lotado(lotacao):
    """Verifica nome e CPF a partir do funcionario lotado."""
    resultado = repository.nome_cpf_servidor("7654321")

    assert resultado == {"nome": "Ana Silva", "cpf": "12345678900"}


def test_usuarios_sgp_por_perfil_filtra_por_dre_e_nome(lotacao):
    """Verifica filtros de DRE e nome em usuarios SGP."""
    resultado = repository.usuarios_sgp_por_perfil(
        "perfil-guid-123",
        codigo_dre="108100",
        nome_servidor_param="Ana",
    )

    assert resultado[0]["codigo_rf"] == "7654321"
    assert resultado[0]["codigo_dre"] == "108100"


def test_funcionarios_sgp_dre_filtra_por_ue_e_nome(lotacao):
    """Verifica filtros opcionais em funcionarios SGP por DRE."""
    resultado = repository.funcionarios_sgp_dre(
        "perfil-guid-123",
        "108100",
        codigo_ue="000532",
        nome_servidor_param="Ana",
    )

    assert resultado[0]["codigo_rf"] == "7654321"
    assert resultado[0]["codigo_ue"] == "000532"

