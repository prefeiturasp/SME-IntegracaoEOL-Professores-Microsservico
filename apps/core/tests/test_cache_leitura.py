"""Valida frescor e contrato das leituras reutilizadas."""

from uuid import uuid4

import pytest
from django.db import connection, transaction

from apps.core.cache_leitura import obter_ou_calcular
from apps.professores.models import ControleCargaProfessores

pytestmark = pytest.mark.django_db


@pytest.fixture
def estado(settings):
    """Prepara fontes completas e armazenamento exclusivo do teste."""
    settings.PROFESSORES_CACHE_ENABLED = True
    settings.PROFESSORES_CACHE_TTL = 300
    settings.PROFESSORES_CACHE_MAX_BYTES = 16 * 1024 * 1024
    settings.PROFESSORES_CACHE_LOCK_SECONDS = 30
    settings.PROFESSORES_CACHE_WAIT_SECONDS = 0
    settings.CACHES = {
        "professores": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": str(uuid4()),
        },
    }
    return ControleCargaProfessores.objects.create(
        id=1, geracao=uuid4(), cargas_ativas=[], falha=False
    )


def test_reutiliza_payload_sem_perder_tipos_nulos_e_duplicatas(estado):
    """Preserva valores publicados e isola alterações dos consumidores."""
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


def test_separa_operacoes_e_filtros(estado):
    """Distingue consultas com operações ou filtros diferentes."""
    assert obter_ou_calcular("p47", {"cargo": 1}, lambda: [1]) == [1]
    assert obter_ou_calcular("p47", {"cargo": 2}, lambda: [2]) == [2]
    assert obter_ou_calcular("p44", {"cargo": 1}, lambda: [3]) == [3]


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("cargas_ativas", ["carga-em-andamento"]),
        ("falha", True),
    ],
)
def test_nao_reutiliza_nem_armazena_durante_carga_ou_falha(
    estado,
    campo,
    valor,
):
    """Evita reutilizar resultados de fontes ainda incompletas."""
    obter_ou_calcular("p47", {}, lambda: ["antes"])
    setattr(estado, campo, valor)
    estado.save()
    assert obter_ou_calcular("p47", {}, lambda: ["parcial"]) == ["parcial"]
    setattr(estado, campo, [] if campo == "cargas_ativas" else False)
    estado.geracao = uuid4()
    estado.save()
    assert obter_ou_calcular("p47", {}, lambda: ["completo"]) == ["completo"]


def test_mudanca_de_geracao_invalida_resposta_anterior(estado):
    """Entrega dados da geração atual após a conclusão da carga."""
    obter_ou_calcular("p47", {}, lambda: ["antes"])
    estado.geracao = uuid4()
    estado.save()
    assert obter_ou_calcular("p47", {}, lambda: ["depois"]) == ["depois"]


def test_carga_iniciada_durante_consulta_impede_preenchimento(estado):
    """Descarta a construção quando suas fontes mudam durante a leitura."""

    def consultar():
        estado.cargas_ativas = ["outra-carga"]
        estado.geracao = uuid4()
        estado.save()
        return ["parcial"]

    assert obter_ou_calcular("p47", {}, consultar) == ["parcial"]
    estado.cargas_ativas = []
    estado.save()
    assert obter_ou_calcular("p47", {}, lambda: ["completo"]) == ["completo"]


def test_estado_ausente_mantem_consulta_normal(estado):
    """Consulta a origem enquanto a integridade das fontes é desconhecida."""
    estado.delete()
    assert obter_ou_calcular("p19", {}, lambda: [1]) == [1]
    assert obter_ou_calcular("p19", {}, lambda: [2]) == [2]


def test_tabela_indisponivel_preserva_consulta_em_transacao(estado):
    """Mantém a leitura de dados após falha no controle de validade."""

    def tabela_ausente(executar, sql, parametros, many, contexto):
        if "controle_carga_professores" in sql:
            return executar(
                "SELECT geracao FROM controle_cache_inexistente",
                (),
                many,
                contexto,
            )
        return executar(sql, parametros, many, contexto)

    def consultar():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return list(cursor.fetchone())

    with connection.execute_wrapper(tabela_ausente), transaction.atomic():
        assert obter_ou_calcular("p47", {}, consultar) == [1]


def test_payload_grande_nao_e_armazenado(estado, settings):
    """Respeita o limite de armazenamento sem alterar a resposta."""
    settings.PROFESSORES_CACHE_MAX_BYTES = 10
    obter_ou_calcular("p47", {}, lambda: ["conteudo-grande"])
    assert obter_ou_calcular("p47", {}, lambda: ["novo"]) == ["novo"]


def test_falha_do_backend_mantem_resposta(estado, monkeypatch):
    """Mantém a consulta disponível quando o armazenamento falha."""
    from django.core.cache import caches

    def falhar(*args, **kwargs):
        raise ConnectionError("indisponivel")

    monkeypatch.setattr(caches["professores"], "get", falhar)
    assert obter_ou_calcular("p47", {}, lambda: ["normal"]) == ["normal"]


def test_excecao_da_consulta_nao_e_transformada_em_resultado(estado):
    """Preserva o erro original da consulta."""

    def falhar():
        raise ValueError("falha-da-consulta")

    with pytest.raises(ValueError, match="falha-da-consulta"):
        obter_ou_calcular("p47", {}, falhar)


def test_lista_vazia_legitima_e_reutilizada(estado):
    """Distingue lista vazia de entrada inexistente."""
    assert obter_ou_calcular("p44", {}, lambda: []) == []
    assert obter_ou_calcular("p44", {}, lambda: ["outro"]) == []


def test_desabilitar_reutilizacao_retorna_ao_fluxo_normal(estado, settings):
    """Entrega a consulta atual quando a reutilização é desativada."""
    obter_ou_calcular("p47", {}, lambda: ["anterior"])
    settings.PROFESSORES_CACHE_ENABLED = False
    assert obter_ou_calcular("p47", {}, lambda: ["atual"]) == ["atual"]


def test_expiracao_exige_nova_consulta(estado, monkeypatch):
    """Atualiza a representação quando sua validade termina."""
    import time

    relogio = [time.time()]
    monkeypatch.setattr(time, "time", lambda: relogio[0])
    obter_ou_calcular("p47", {}, lambda: ["anterior"])
    relogio[0] += 301
    assert obter_ou_calcular("p47", {}, lambda: ["atual"]) == ["atual"]
