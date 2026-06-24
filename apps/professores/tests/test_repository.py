"""Testes dos repositories do dominio de professores."""

from datetime import date
from types import SimpleNamespace

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

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
    """Verifica limite de resultados do autocomplete."""
    for indice in range(11):
        _cria_professor_com_atribuicao(
            f"90000{indice}",
            2110000 + indice,
        )

    resultado = repository.autocomplete_professores(2024, "")

    assert len(resultado) == 10


def test_autocomplete_ordena_por_nome_no_top_10(db, atribuicao_externa):
    """Top 10 sai ordenado por nome sobre a união (efetivos + externos)."""
    for indice in range(10):
        _cria_professor_com_atribuicao(
            f"91000{indice}",
            2120000 + indice,
        )

    resultado = repository.autocomplete_professores(2024, "")

    nomes = [item["nome_servidor"] for item in resultado]
    assert nomes == sorted(nomes)
    assert len(resultado) == 10
    # "João Ext" ordena antes de "Professor ..." e entra no top 10.
    assert any(item["codigo_rf"] == "98765432100" for item in resultado)


def test_autocomplete_inclui_professor_externo(atribuicao_externa):
    """Verifica inclusao de contrato externo no autocomplete."""
    resultado = repository.autocomplete_professores(2024, "")

    assert resultado[0]["codigo_rf"] == "98765432100"


def test_autocomplete_filtra_nome_por_prefixo(db):
    """Nome filtra por prefixo (istartswith), não por substring."""
    ana = Professor.objects.create(
        codigo_rf="800001", nome="Ana Souza", cpf="00000800001"
    )
    mariana = Professor.objects.create(
        codigo_rf="800002", nome="Mariana Lima", cpf="00000800002"
    )
    for prof in (ana, mariana):
        cargo = CargoBaseServidor.objects.create(
            professor=prof,
            codigo_cargo=3379,
            descricao_cargo="Professor",
            dt_posse=date(2020, 1, 1),
        )
        AtribuicaoAula.objects.create(
            cargo_base=cargo,
            codigo_unidade_educacao="000532",
            codigo_turma_escola=2112345,
            codigo_grade=100,
            codigo_componente_curricular=138,
            ano_atribuicao=2024,
            dt_atribuicao_aula=date(2024, 2, 1),
        )

    resultado = repository.autocomplete_professores(
        2024, "108100", ue_id="000532", nome="ana"
    )

    assert [item["codigo_rf"] for item in resultado] == ["800001"]


def test_autocomplete_exclui_cancelada_e_nomeacao_encerrada(db):
    """Atribuição cancelada e nomeação encerrada não entram."""
    prof = Professor.objects.create(
        codigo_rf="800003", nome="Carlos Dias", cpf="00000800003"
    )
    cargo_ok = CargoBaseServidor.objects.create(
        professor=prof,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
    )
    # Atribuição cancelada do cargo válido.
    AtribuicaoAula.objects.create(
        cargo_base=cargo_ok,
        codigo_unidade_educacao="000532",
        codigo_turma_escola=2112345,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao_aula=date(2024, 2, 1),
        dt_cancelamento=date(2024, 6, 1),
    )
    # Atribuição válida, mas com nomeação encerrada.
    cargo_encerrado = CargoBaseServidor.objects.create(
        professor=prof,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
        dt_fim_nomeacao=date(2024, 1, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo_encerrado,
        codigo_unidade_educacao="000532",
        codigo_turma_escola=2112346,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao_aula=date(2024, 2, 1),
    )

    resultado = repository.autocomplete_professores(
        2024, "108100", ue_id="000532"
    )

    assert resultado == []


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


def test_buscar_turmas_professor_ancora_regular(db):
    """Âncora de turma regular: codigo_turma vem de codigo_turma_escola."""
    _cria_professor_com_atribuicao("7654321", 2112345, "000532")

    resultado = repository.buscar_turmas_professor("7654321")

    assert resultado == [
        {
            "codigo_turma": 2112345,
            "codigo_serie_grade": None,
            "codigo_unidade_educacao": "000532",
            "data_atribuicao": "02/01/2024 00:00:00",
            "data_disponibilizacao": None,
        }
    ]


def test_buscar_turmas_professor_ancora_programa(db):
    """Âncora de programa: sem codigo_turma, expõe codigo_serie_grade."""
    professor = Professor.objects.create(
        codigo_rf="7654322",
        nome="Professor Programa",
        cpf="00000000000",
    )
    cargo = CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo,
        codigo_unidade_educacao="000532",
        codigo_turma_escola=None,
        codigo_serie_grade=1040353,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao_aula=date(2024, 2, 1),
    )

    resultado = repository.buscar_turmas_professor("7654322")

    assert resultado == [
        {
            "codigo_turma": None,
            "codigo_serie_grade": 1040353,
            "codigo_unidade_educacao": "000532",
            "data_atribuicao": "02/01/2024 00:00:00",
            "data_disponibilizacao": None,
        }
    ]


def test_buscar_turmas_professor_ignora_atribuicao_externa(
    db, atribuicao_externa
):
    """Atribuição externa não entra no recorte de /turmas."""
    resultado = repository.buscar_turmas_professor("98765432100")

    assert resultado == []


def test_buscar_turmas_professor_ignora_atribuicao_cancelada(db):
    """Atribuição cancelada não entra (dt_cancelamento via _vigentes_em)."""
    professor = Professor.objects.create(
        codigo_rf="7654323", nome="Professor Cancelado", cpf="11111111111"
    )
    cargo = CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo,
        codigo_unidade_educacao="000532",
        codigo_turma_escola=2112345,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao_aula=date(2024, 2, 1),
        dt_cancelamento=date(2024, 6, 1),
    )

    assert repository.buscar_turmas_professor("7654323") == []


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


def test_atribuicao_turmas_lista_sem_turmas_retorna_vazio(
    atribuicao,
):
    """Verifica retorno vazio sem lista de turmas informada."""
    resultado = repository.atribuicao_turmas_lista("7654321", 138, [])

    assert resultado == []


def test_atribuicao_turmas_lista_inclui_atribuicao_externa(
    atribuicao_externa,
):
    """Verifica retorno de atribuicao externa com motivo esperado."""
    atribuicao_externa.codigo_turma_escola = 2112345
    atribuicao_externa.codigo_motivo_disponibilizacao_externo = 3
    atribuicao_externa.save(
        update_fields=[
            "codigo_turma_escola",
            "codigo_motivo_disponibilizacao_externo",
        ]
    )

    resultado = repository.atribuicao_turmas_lista(
        "98765432100",
        138,
        [2112345],
    )

    assert resultado == [
        {
            "codigo_turma": "2112345",
            "data_disponibilizacao_aulas": None,
            "data_atribuicao_aula": "2024-02-01T00:00:00",
        }
    ]


def test_atribuicao_turmas_lista_nao_consulta_tabelas_inexistentes(
    atribuicao,
):
    """Verifica ausencia de dependencias de tabelas fora do DB."""
    with CaptureQueriesContext(connection) as queries:
        repository.atribuicao_turmas_lista("7654321", 138, [2112345])

    sql = "\n".join(query["sql"].lower() for query in queries)

    assert 'from "turma_escola"' not in sql
    assert 'join "turma_escola"' not in sql
    assert 'from "serie_turma_grade"' not in sql
    assert 'join "serie_turma_grade"' not in sql
