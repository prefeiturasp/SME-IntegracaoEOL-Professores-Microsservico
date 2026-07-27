"""Testes dos repositories do dominio de professores."""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from apps.professores import repositories
from apps.professores.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoAula,
    CargoBaseServidor,
    Professor,
    TurmaAtribuidaUe,
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
    resultado = repositories.autocomplete_professores(
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

    resultado = repositories.autocomplete_professores(date.today().year)

    assert len(resultado) == 10


def test_autocomplete_ordena_por_nome_no_top_10(db):
    """Top 10 sai ordenado por nome e limitado a 10 resultados."""
    for indice in range(11):
        _cria_professor_com_atribuicao(
            f"91000{indice}",
            2120000 + indice,
        )

    resultado = repositories.autocomplete_professores(date.today().year)

    nomes = [item["nome_servidor"] for item in resultado]
    assert nomes == sorted(nomes)
    assert len(resultado) == 10


def test_autocomplete_inclui_professor_externo(atribuicao_externa):
    """Verifica inclusao de contrato externo no autocomplete."""
    resultado = repositories.autocomplete_professores(2024)

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

    resultado = repositories.autocomplete_professores(
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

    resultado = repositories.autocomplete_professores(2024, ue_id="000532")

    assert resultado == []


def test_codigo_turma_retorna_none_sem_turma_ou_serie():
    """Verifica atribuicao sem turma e sem serie-grade."""
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=None,
    )

    assert repositories._codigo_turma(atribuicao) is None


def test_codigo_turma_nao_resolve_por_serie_grade():
    """Verifica que serie-grade nao e convertida em turma."""
    atribuicao = SimpleNamespace(
        codigo_turma_escola=None,
        codigo_serie_grade=999999,
    )

    assert repositories._codigo_turma(atribuicao) is None


def test_buscar_turmas_professor_ancora_regular(db):
    """Âncora de turma regular: codigo_turma vem de codigo_turma_escola."""
    _cria_professor_com_atribuicao("7654321", 2112345, "000532")

    resultado = repositories.buscar_turmas_professor("7654321")

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

    resultado = repositories.buscar_turmas_professor("7654322")

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

    resultado = repositories.buscar_turmas_professor_escola_ano(
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

    resultado = repositories.buscar_turmas_professor_escola_ano(
        None, ue.codigo_ue, 2024
    )

    assert [item["nome_turma"] for item in resultado] == ["1A"]


def test_buscar_turmas_professor_ano_inclui_campos_atribuicao_externa(
    atribuicao_externa,
):
    """Verifica payload de vinculo externo com dados desnormalizados."""
    resultado = repositories.buscar_turmas_professor_ano("98765432100", 2024)

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
    resultado = repositories.buscar_turmas_professor("98765432100")

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

    assert repositories.buscar_turmas_professor("7654323") == []


def test_atribuicao_disciplina_territorio_filtra_por_data():
    """Verifica atribuicao de territorio do saber com data."""
    AgrupamentoAtribuicaoTerritorioSaber.objects.create(
        codigo_agrupamento=1,
        rf_professor="7654321",
        codigo_turma=2112345,
        dt_inicio_atribuicao=date(2024, 2, 1),
    )

    assert repositories.atribuicao_disciplina_data(
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

    resultado = repositories.titulares_por_turma_agrupamento(
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

    resultado = repositories.titulares_por_turma_agrupamento(2112345, True)

    assert resultado[0]["disciplinas_id"] is None


def test_atribuicao_turmas_lista_sem_turmas_retorna_vazio(
    atribuicao,
):
    """Verifica retorno vazio sem lista de turmas informada."""
    resultado = repositories.atribuicao_turmas_lista("7654321", 138, [])

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

    resultado = repositories.atribuicao_turmas_lista(
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


def _cria_atribuicao_abrangencia(
    codigo_rf: str,
    codigo_ue: str,
    codigo_turma: int,
    codigo_dre: str,
    codigo_tipo_turma: int = 1,
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
        ano_escolar="1",
        ano_atribuicao=date.today().year,
        codigo_etapa_ensino=1,
        dt_atribuicao_aula=date(date.today().year, 1, 1),
        codigo_dre=codigo_dre,
        nome_dre="DRE Teste",
        abreviacao_dre="DT",
        nome_unidade_educacional="EMEF Teste",
        codigo_tipo_escola=4,
        codigo_tipo_turma=codigo_tipo_turma,
        modalidade="Fundamental",
        codigo_modalidade=5,
        semestre=0,
        duracao_turno=5,
        tipo_turno=1,
    )


def test_buscar_abrangencia_funcionario_perfil_monta_hierarquia(db):
    """Abrangência agrupa turmas vigentes por DRE e UE."""
    _cria_atribuicao_abrangencia("770001", "000532", 2112345, "108100")

    resultado = repositories.buscar_abrangencia_funcionario_perfil(
        "770001", "perfil-x"
    )

    assert resultado["abrangencia"] is None
    assert len(resultado["dres"]) == 1
    dre = resultado["dres"][0]
    assert dre["codigo"] == "108100"
    assert dre["nome"] == "DRE Teste"
    assert [ue["codigo"] for ue in dre["ues"]] == ["000532"]
    turmas = dre["ues"][0]["turmas"]
    assert [t["codigo"] for t in turmas] == [2112345]
    assert turmas[0]["modalidade"] == "Fundamental"


def test_buscar_abrangencia_funcionario_perfil_turma_programa(db):
    """Turma de programa (tipo 2-5) vira Fundamental com ano '0'."""
    _cria_atribuicao_abrangencia(
        "770002", "000600", 2113000, "108200", codigo_tipo_turma=2
    )

    resultado = repositories.buscar_abrangencia_funcionario_perfil(
        "770002", "perfil-x"
    )

    turma = resultado["dres"][0]["ues"][0]["turmas"][0]
    assert turma["modalidade"] == "Fundamental"
    assert turma["ano"] == "0"
    assert turma["codigo_modalidade"] == 5


def test_buscar_abrangencia_ignora_atribuicao_de_outro_ano(db):
    """Atribuição de ano diferente do corrente não entra na abrangência."""
    professor = Professor.objects.create(
        codigo_rf="770003", nome="Prof Antigo", cpf="00000770003"
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
        ano_atribuicao=date.today().year - 1,
        dt_atribuicao_aula=date(date.today().year - 1, 2, 1),
    )

    resultado = repositories.buscar_abrangencia_funcionario_perfil(
        "770003", "perfil-x"
    )

    assert resultado == {"abrangencia": None, "dres": []}


def test_turmas_atribuidas_ue_filtra_rf_cargo_dre(db):
    """turmas_atribuidas_ue filtra por RF, cargo/sobreposto e DRE."""

    def _cria(rf, escola, turma, cargo=None, sobreposto=None, dre="108100"):
        TurmaAtribuidaUe.objects.create(
            codigo_escola=escola,
            codigo_turma=turma,
            ano_letivo=date.today().year,
            codigo_dre=dre,
            dre="DRE Teste",
            nome_turma="1A",
            usuario_rf=rf,
            cargo=cargo,
            cargo_sobreposto=sobreposto,
        )

    _cria("111", "000001", 10, cargo=3360)
    _cria("111", "000002", 20, sobreposto=3379)
    _cria("111", "000003", 30, cargo=9999, dre="200000")
    _cria("222", "000004", 40, cargo=3360)

    todas = repositories.turmas_atribuidas_ue("111")
    assert {t["codigo_turma"] for t in todas} == {10, 20, 30}
    assert {t["codigo_dre"] for t in todas} == {"108100", "200000"}

    por_cargo = repositories.turmas_atribuidas_ue("111", cargos=[3360, 3379])
    assert {t["codigo_turma"] for t in por_cargo} == {10, 20}

    por_dre = repositories.turmas_atribuidas_ue("111", codigo_dre="200000")
    assert [t["codigo_turma"] for t in por_dre] == [30]


def test_buscar_abrangencia_deduplica_turma_repetida(db):
    """Mesma UE+turma em duas atribuições aparece uma única vez."""
    professor = Professor.objects.create(
        codigo_rf="770004", nome="Prof Dup", cpf="00000770004"
    )
    cargo = CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
    )
    for componente in (138, 139):
        AtribuicaoAula.objects.create(
            cargo_base=cargo,
            codigo_unidade_educacao="000532",
            codigo_turma_escola=2112345,
            descricao_turma_escola="1A",
            codigo_grade=100,
            codigo_componente_curricular=componente,
            ano_escolar="1",
            ano_atribuicao=date.today().year,
            codigo_etapa_ensino=1,
            dt_atribuicao_aula=date(date.today().year, 1, 1),
            codigo_dre="108100",
        )

    resultado = repositories.buscar_abrangencia_funcionario_perfil(
        "770004", "perfil-x"
    )

    turmas = resultado["dres"][0]["ues"][0]["turmas"]
    assert [t["codigo"] for t in turmas] == [2112345]


def test_buscar_abrangencia_exclui_atribuicao_ja_disponibilizada(db):
    """Atribuição já disponibilizada (mesmo de programa no mês) fica fora."""
    professor = Professor.objects.create(
        codigo_rf="770006", nome="Prof Disp", cpf="00000770006"
    )
    cargo = CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        descricao_cargo="Professor",
        dt_posse=date(2020, 1, 1),
    )
    hoje = date.today()
    comum = {
        "cargo_base": cargo,
        "codigo_unidade_educacao": "000532",
        "codigo_turma_escola_grade_programa": 555001,
        "codigo_grade": 100,
        "codigo_componente_curricular": 138,
        "codigo_tipo_turma": 3,
        "ano_atribuicao": hoje.year,
        "dt_atribuicao_aula": date(hoje.year, 1, 1),
        "codigo_dre": "108100",
    }
    AtribuicaoAula.objects.create(
        codigo_turma_escola=2110001,
        dt_disponibilizacao_aulas=hoje - timedelta(days=1),
        **comum,
    )
    AtribuicaoAula.objects.create(
        codigo_turma_escola=2110002,
        dt_disponibilizacao_aulas=date(hoje.year, 12, 22),
        **comum,
    )

    resultado = repositories.buscar_abrangencia_funcionario_perfil(
        "770006", "perfil-x"
    )

    turmas = {
        t["codigo"]
        for dre in resultado["dres"]
        for ue in dre["ues"]
        for t in ue["turmas"]
    }
    assert turmas == {2110002}
