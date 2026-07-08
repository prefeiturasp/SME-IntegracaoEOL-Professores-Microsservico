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
        descricao_turma_escola="1A",
        codigo_grade=100,
        codigo_componente_curricular=138,
        descricao_componente_curricular="Matematica",
        ano_escolar="1",
        ano_atribuicao=date.today().year,
        codigo_etapa_ensino=1,
        dt_atribuicao_aula=date(date.today().year, 1, 1),
    )


def test_autocomplete_filtra_por_ue(atribuicao):
    """Verifica filtro direto por unidade educacional."""
    resultado = repository.autocomplete_professores(
        2024,
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

    resultado = repository.autocomplete_professores(date.today().year)

    assert len(resultado) == 10


def test_autocomplete_ordena_por_nome_no_top_10(db):
    """Top 10 sai ordenado por nome e limitado a 10 resultados."""
    for indice in range(11):
        _cria_professor_com_atribuicao(
            f"91000{indice}",
            2120000 + indice,
        )

    resultado = repository.autocomplete_professores(date.today().year)

    nomes = [item["nome_servidor"] for item in resultado]
    assert nomes == sorted(nomes)
    assert len(resultado) == 10


def test_autocomplete_inclui_professor_externo(atribuicao_externa):
    """Verifica inclusao de contrato externo no autocomplete."""
    resultado = repository.autocomplete_professores(2024)

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
        2024, ue_id="000532", nome="ana"
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

    resultado = repository.autocomplete_professores(2024, ue_id="000532")

    assert resultado == []


def test_codigo_turma_retorna_none_sem_turma_ou_serie():
    """Verifica atribuicao sem turma e sem serie-grade."""
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=None,
    )

    assert repository._codigo_turma(atribuicao) is None


def test_codigo_turma_nao_resolve_por_serie_grade():
    """Verifica que serie-grade nao e convertida em turma."""
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
            "nome_turma": "1A",
            "codigo_serie_grade": None,
            "componente_curricular": "Matematica",
            "codigo_unidade_educacao": "000532",
            "ano": "1",
            "etapa_ensino": 1,
            "data_atribuicao": f"01/01/{date.today().year} 00:00:00",
            "data_disponibilizacao": None,
            "data_inicio_turma": None,
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
        descricao_turma_escola="Programa",
        codigo_serie_grade=1040353,
        codigo_grade=100,
        codigo_componente_curricular=138,
        descricao_componente_curricular="Territorio do Saber",
        ano_escolar="4",
        ano_atribuicao=date.today().year,
        codigo_etapa_ensino=2,
        dt_atribuicao_aula=date(date.today().year, 1, 1),
    )

    resultado = repository.buscar_turmas_professor("7654322")

    assert resultado == [
        {
            "codigo_turma": None,
            "nome_turma": "Programa",
            "codigo_serie_grade": 1040353,
            "componente_curricular": "Territorio do Saber",
            "codigo_unidade_educacao": "000532",
            "ano": "4",
            "etapa_ensino": 2,
            "data_atribuicao": f"01/01/{date.today().year} 00:00:00",
            "data_disponibilizacao": None,
            "data_inicio_turma": None,
        }
    ]


def test_buscar_turmas_professor_escola_ano_usa_dados_atribuicao(
    db, cargo_base, ue
):
    """Verifica payload de turma com campos desnormalizados da atribuicao."""
    fim = date(date.today().year + 1, 1, 1)
    AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_turma_escola=2112345,
        descricao_turma_escola="1A",
        codigo_grade=100,
        codigo_componente_curricular=138,
        descricao_componente_curricular="Matematica",
        ano_escolar="1",
        ano_atribuicao=date.today().year,
        codigo_etapa_ensino=1,
        dt_atribuicao_aula=date(date.today().year, 2, 1),
        dt_disponibilizacao_aulas=fim,
        dt_inicio_turma=date(date.today().year, 1, 15),
    )

    resultado = repository.buscar_turmas_professor_escola_ano(
        "7654321", ue.codigo_ue, date.today().year
    )

    assert resultado == [
        {
            "codigo_turma": 2112345,
            "nome_turma": "1A",
            "componente_curricular": "Matematica",
            "data_inicio_atribuicao": (f"02/01/{date.today().year} 00:00:00"),
            "data_fim_atribuicao": (f"01/01/{date.today().year + 1} 00:00:00"),
            "data_inicio_turma": (f"01/15/{date.today().year} 00:00:00"),
            "ano": "1",
            "etapa_ensino": 1,
        }
    ]


def test_buscar_turmas_professor_escola_ano_sem_rf_filtra_anos_iniciais(
    db, cargo_base, ue
):
    """Verifica filtro de anos iniciais quando RF nao e informado."""
    AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_turma_escola=2112345,
        descricao_turma_escola="1A",
        codigo_grade=100,
        codigo_componente_curricular=138,
        descricao_componente_curricular="Matematica",
        ano_escolar="1",
        ano_atribuicao=2024,
        codigo_etapa_ensino=1,
        dt_atribuicao_aula=date(2024, 2, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_turma_escola=2112346,
        descricao_turma_escola="7A",
        codigo_grade=100,
        codigo_componente_curricular=138,
        descricao_componente_curricular="Matematica",
        ano_escolar="7",
        ano_atribuicao=2024,
        codigo_etapa_ensino=1,
        dt_atribuicao_aula=date(2024, 2, 1),
    )

    resultado = repository.buscar_turmas_professor_escola_ano(
        None, ue.codigo_ue, 2024
    )

    assert [item["nome_turma"] for item in resultado] == ["1A"]


def test_buscar_turmas_professor_ano_inclui_campos_atribuicao_externa(
    atribuicao_externa,
):
    """Verifica payload de vinculo externo com dados desnormalizados."""
    resultado = repository.buscar_turmas_professor_ano("98765432100", 2024)

    assert resultado == [
        {
            "codigo_turma": 2112345,
            "nome_turma": "1A",
            "componente_curricular": "Matematica",
            "codigo_serie_grade": None,
            "codigo_unidade_educacao": "000532",
            "ano": "1",
            "etapa_ensino": 1,
            "data_atribuicao": "02/01/2024 00:00:00",
            "data_disponibilizacao": None,
            "data_inicio_turma": None,
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
