"""Testes dos repositories do dominio de funcionarios."""

import pytest

from apps.funcionarios import repository

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
    assert repository.funcionarios_por_lista_funcoes_externas("000532", []) == []


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

