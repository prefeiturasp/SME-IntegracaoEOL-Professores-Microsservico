"""Valida expiração e contrato das leituras reutilizadas."""

import pytest

from apps.core.cache_leitura import obter_ou_calcular

pytestmark = pytest.mark.usefixtures("cache_ativo")


def test_reutiliza_payload_sem_perder_tipos_nulos_e_duplicatas():
    """Preserva valores publicados sem acesso ao banco de dados."""
    esperado = [{"rf": "0001", "nulo": None, "ativo": False}] * 2
    chamadas = []

    def consultar():
        chamadas.append(True)
        return esperado

    primeiro = obter_ou_calcular("p47", {"cargo": 1}, consultar)
    primeiro[0]["rf"] = "alterado"
    segundo = obter_ou_calcular("p47", {"cargo": 1}, consultar)

    assert segundo == [
        {"rf": "0001", "nulo": None, "ativo": False},
        {"rf": "0001", "nulo": None, "ativo": False},
    ]
    assert len(chamadas) == 1


def test_separa_operacoes_e_filtros():
    """Distingue consultas com operações ou filtros diferentes."""
    assert obter_ou_calcular("p47", {"cargo": 1}, lambda: [1]) == [1]
    assert obter_ou_calcular("p47", {"cargo": 2}, lambda: [2]) == [2]
    assert obter_ou_calcular("p44", {"cargo": 1}, lambda: [3]) == [3]


def test_payload_grande_nao_e_armazenado(settings):
    """Respeita o limite de armazenamento sem alterar a resposta."""
    settings.PROFESSORES_CACHE_MAX_BYTES = 10
    obter_ou_calcular("p47", {}, lambda: ["conteudo-grande"])
    assert obter_ou_calcular("p47", {}, lambda: ["novo"]) == ["novo"]


@pytest.mark.parametrize("metodo", ["get", "add", "set"])
def test_falha_do_backend_mantem_resposta(monkeypatch, metodo):
    """Mantém a consulta disponível quando o armazenamento falha."""
    from django.core.cache import caches

    def falhar(*args, **kwargs):
        raise ConnectionError("indisponivel")

    monkeypatch.setattr(caches["professores"], metodo, falhar)
    assert obter_ou_calcular("p47", {}, lambda: ["normal"]) == ["normal"]


def test_excecao_da_consulta_nao_e_transformada_em_resultado():
    """Preserva o erro original sem armazená-lo como resposta."""

    def falhar():
        raise ValueError("falha-da-consulta")

    with pytest.raises(ValueError, match="falha-da-consulta"):
        obter_ou_calcular("p47", {}, falhar)
    assert obter_ou_calcular("p47", {}, lambda: ["recuperado"]) == [
        "recuperado"
    ]


def test_lista_vazia_legitima_e_reutilizada():
    """Distingue lista vazia de entrada inexistente."""
    assert obter_ou_calcular("p44", {}, lambda: []) == []
    assert obter_ou_calcular("p44", {}, lambda: ["outro"]) == []


def test_desabilitar_reutilizacao_retorna_ao_fluxo_normal(settings):
    """Entrega a consulta atual quando a reutilização é desativada."""
    obter_ou_calcular("p47", {}, lambda: ["anterior"])
    settings.PROFESSORES_CACHE_ENABLED = False
    assert obter_ou_calcular("p47", {}, lambda: ["atual"]) == ["atual"]


def test_expiracao_exige_nova_consulta_sem_renovar_ao_ler(relogio):
    """Atualiza a representação após cinco minutos desde a gravação."""
    obter_ou_calcular("p47", {}, lambda: ["anterior"])
    relogio[0] += 299
    assert obter_ou_calcular("p47", {}, lambda: ["atual"]) == ["anterior"]
    relogio[0] += 2
    assert obter_ou_calcular("p47", {}, lambda: ["atual"]) == ["atual"]
