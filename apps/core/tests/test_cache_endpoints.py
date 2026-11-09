"""Confere contrato, validação e atualização das consultas reutilizadas."""

from datetime import date

import pytest

from apps.professores.models import (
    FuncionarioCargo,
    FuncionarioConectaFormacao,
)

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("cache_ativo")]
_BASE = "/api/v1/professores"


def test_cargo_reutiliza_contrato_e_atualiza_apos_expiracao(client, relogio):
    """Preserva a representação até a validade terminar."""
    funcionario = FuncionarioCargo.objects.create(
        codigo_rf="000001",
        nome="Antes",
        codigo_cargo=1,
        cargo="Cargo",
    )
    path = f"{_BASE}/funcionarios/cargos/1/"
    antes = client.get(path)
    funcionario.nome = "Depois"
    funcionario.save()
    assert client.get(path).json() == antes.json()
    relogio[0] += 301
    assert client.get(path).json()[0]["nome"] == "Depois"


def test_conecta_separa_filtros_e_preserva_contrato(client, relogio):
    """Distingue funções ausentes das funções solicitadas."""
    funcionario = FuncionarioConectaFormacao.objects.create(
        rf="000001",
        nome="Antes",
        cargo_codigo=1,
        funcao_codigo=None,
    )
    FuncionarioConectaFormacao.objects.create(
        rf="000002",
        nome="Função",
        cargo_codigo=1,
        funcao_codigo=20,
    )
    path = f"{_BASE}/funcionarios/registros-funcionais/conecta-formacao/"
    antes = client.get(path)
    assert [x["rf"] for x in antes.json()] == ["000001"]
    funcionario.nome = "Depois"
    funcionario.save()
    assert client.get(path).json() == antes.json()
    outra_funcao = client.get(path, {"codigos_funcoes": [20]})
    assert [x["rf"] for x in outra_funcao.json()] == ["000002"]
    relogio[0] += 301
    assert client.get(path).json()[0]["nome"] == "Depois"


def test_titulares_consultam_origem_com_cache_do_ms_habilitado(
    client,
    atribuicao,
    professor,
):
    """Entrega os titulares atuais sem reutilização neste serviço."""
    atribuicao.ano_atribuicao = 2026
    atribuicao.codigo_tipo_turma = 1
    atribuicao.dt_atribuicao_aula = date(2026, 1, 1)
    atribuicao.save()
    path = f"{_BASE}/titulares/ue/000532/2026-10-20/"
    antes = client.get(path)
    assert antes.json()
    professor.nome = "Depois"
    professor.save()
    assert client.get(path).json()[0]["nome_professor"] == "Depois"
    assert client.get(f"{_BASE}/titulares/ue/000532/2025-10-20/").json() == []


def test_hit_nao_dispensa_autenticacao(client, anon):
    """Rejeita uma consulta anônima mesmo com resultado disponível."""
    path = f"{_BASE}/funcionarios/cargos/1/"
    assert client.get(path).status_code == 200
    assert anon.get(path).status_code == 403


def test_hit_nao_dispensa_validacao_dos_filtros(client):
    """Rejeita filtros inválidos mesmo com resultado disponível."""
    path = f"{_BASE}/funcionarios/registros-funcionais/conecta-formacao/"
    assert client.get(path).status_code == 200
    resposta = client.get(path, {"codigos_cargos": ["invalido"]})
    assert resposta.status_code == 400
