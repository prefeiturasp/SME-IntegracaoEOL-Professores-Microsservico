"""Testes dos repositories do dominio de professores."""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from apps.professores import repositories
from apps.professores.models import (
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
            "ano_letivo": "2024",
            "data_inicio_atribuicao": "2024-02-01T00:00:00",
            "data_fim_atribuicao": None,
            "data_fim_turma": None,
            "ano_atribuicao": 2024,
            "codigo_rf": "98765432100",
            "disciplina_id": "138",
            "disciplina_nome": "Matematica",
            "disciplinas_agrupadas_ids": None,
            "nome_professor": "João Ext",
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


def test_titulares_por_turma_filtra_rf(atribuicao_ano_corrente):
    """Verifica titulares por RF com disciplina sem espaços à direita."""
    atribuicao_ano_corrente.descricao_componente_curricular = "Matematica   "
    atribuicao_ano_corrente.save(
        update_fields=["descricao_componente_curricular"]
    )

    resultado = repositories.titulares_por_turma(
        2112345,
        codigo_rf="7654321",
    )

    assert resultado == [
        {
            "professor_rf": "7654321",
            "nome_professor": "Ana Silva",
            "disciplina": "Matematica",
            "disciplina_id": 138,
            "disciplinas_id": "138",
            "turma_id": 2112345,
        }
    ]


def test_normalizar_titulares_remove_none_e_ordena_disciplina():
    """Remove disciplina nula e ordena códigos numericamente."""
    resultado = repositories._normalizar_titulares(
        [
            {"disciplina_id": 1522, "professor_rf": "3"},
            {"disciplina_id": None, "professor_rf": "2"},
            {"disciplina_id": 9, "professor_rf": "1"},
        ]
    )

    assert resultado == [
        {"disciplina_id": 9, "professor_rf": "1"},
        {"disciplina_id": 1522, "professor_rf": "3"},
    ]


def test_titular_por_turma_disciplina_retorna_payload(atribuicao):
    """Retorna diretamente os dados do titular e da disciplina."""
    atribuicao.descricao_componente_curricular = "Matematica   "
    atribuicao.save(update_fields=["descricao_componente_curricular"])

    resultado = repositories.titular_por_turma_disciplina(2112345, 138)

    assert resultado == {
        "professor_rf": "7654321",
        "nome_professor": "Ana Silva",
        "disciplina": "Matematica",
        "disciplina_id": "138",
        "disciplinas_id": "138",
        "turma_id": 2112345,
    }


def test_titulares_por_turmas_retorna_payload(atribuicao_ano_corrente):
    """Retorna diretamente os titulares das turmas informadas."""
    resultado = repositories.titulares_por_turmas([2112345])

    assert resultado == [
        {
            "professor_rf": "7654321",
            "nome_professor": "Ana Silva",
            "disciplina": "Matematica",
            "disciplina_id": "138",
            "disciplinas_id": "138",
            "turma_id": 2112345,
        }
    ]


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("ano_atribuicao", date.today().year - 1),
        ("dt_cancelamento", date.today()),
        ("codigo_motivo_disponibilizacao", 34),
    ],
)
def test_titulares_por_turma_ignora_atribuicao_inativa(
    atribuicao_ano_corrente,
    campo,
    valor,
):
    """Ignora atribuição fora do ano ou encerrada."""
    setattr(atribuicao_ano_corrente, campo, valor)
    atribuicao_ano_corrente.save(update_fields=[campo])

    assert repositories.titulares_por_turma(2112345) == []


@pytest.mark.parametrize(
    "campo",
    ["dt_cancelamento", "dt_fim_nomeacao"],
)
def test_titulares_por_turma_ignora_cargo_inativo(
    atribuicao_ano_corrente,
    campo,
):
    """Ignora titular com cargo cancelado ou nomeação encerrada."""
    cargo = atribuicao_ano_corrente.cargo_base
    setattr(cargo, campo, date.today())
    cargo.save(update_fields=[campo])

    assert repositories.titulares_por_turma(2112345) == []


def test_titulares_por_turma_inclui_atribuicao_disponibilizada(
    atribuicao_ano_corrente,
):
    """Inclui atribuição mesmo quando as aulas foram disponibilizadas."""
    atribuicao_ano_corrente.dt_disponibilizacao_aulas = date.today()
    atribuicao_ano_corrente.save(update_fields=["dt_disponibilizacao_aulas"])

    resultado = repositories.titulares_por_turma(2112345)

    assert len(resultado) == 1
    assert resultado[0]["professor_rf"] == "7654321"


def test_titulares_por_turma_inclui_atribuicao_externa(
    atribuicao_externa,
):
    """Inclui atribuição externa ativa do ano corrente."""
    atribuicao_externa.ano_atribuicao = date.today().year
    atribuicao_externa.dt_disponibilizacao = date.today()
    atribuicao_externa.save(
        update_fields=["ano_atribuicao", "dt_disponibilizacao"]
    )

    resultado = repositories.titulares_por_turma(
        2112345,
        codigo_rf="98765432100",
    )

    assert resultado == [
        {
            "professor_rf": "98765432100",
            "nome_professor": "João Ext",
            "disciplina": "Matematica",
            "disciplina_id": 138,
            "disciplinas_id": "138",
            "turma_id": 2112345,
        }
    ]


def test_titulares_por_turma_ignora_contrato_externo_cancelado(
    atribuicao_externa,
):
    """Ignora titular externo com contrato cancelado."""
    atribuicao_externa.ano_atribuicao = date.today().year
    atribuicao_externa.save(update_fields=["ano_atribuicao"])
    contrato = atribuicao_externa.contrato_externo
    contrato.dt_cancelamento = date.today()
    contrato.save(update_fields=["dt_cancelamento"])

    assert repositories.titulares_por_turma(2112345) == []


def test_titulares_por_turma_ignora_motivo_externo(
    atribuicao_externa,
):
    """Ignora titular externo com motivo de disponibilização."""
    atribuicao_externa.ano_atribuicao = date.today().year
    atribuicao_externa.codigo_motivo_disponibilizacao_externo = 3
    atribuicao_externa.save(
        update_fields=[
            "ano_atribuicao",
            "codigo_motivo_disponibilizacao_externo",
        ]
    )

    assert repositories.titulares_por_turma(2112345) == []


def test_titulares_por_turma_prioriza_efetivo_sobre_externo(
    atribuicao_ano_corrente,
    atribuicao_externa,
):
    """Prioriza efetivo quando as duas fontes atribuem a disciplina."""
    atribuicao_externa.ano_atribuicao = date.today().year
    atribuicao_externa.save(update_fields=["ano_atribuicao"])

    resultado = repositories.titulares_por_turma(2112345)

    assert len(resultado) == 1
    assert resultado[0]["professor_rf"] == "7654321"


def test_titulares_por_turma_filtra_apos_priorizar_efetivo(
    atribuicao_ano_corrente,
    atribuicao_externa,
):
    """Aplica RF ou CPF sobre o titular escolhido pela prioridade."""
    atribuicao_externa.ano_atribuicao = date.today().year
    atribuicao_externa.save(update_fields=["ano_atribuicao"])

    resultado = repositories.titulares_por_turma(
        2112345,
        codigo_rf="98765432100",
    )

    assert resultado == []


def test_titulares_por_ue_retorna_payload(atribuicao):
    """Retorna diretamente os titulares vigentes da unidade."""
    resultado = repositories.titulares_por_ue(
        "000532",
        date(2024, 6, 1),
    )

    assert resultado == [
        {
            "professor_rf": "7654321",
            "nome_professor": "Ana Silva",
            "disciplina": "Matematica",
            "disciplina_id": "138",
            "disciplinas_id": "138",
            "turma_id": 2112345,
        }
    ]


def test_titulares_por_ue_ignora_atribuicao_cancelada(atribuicao):
    """Ignora atribuição cancelada."""
    atribuicao.dt_cancelamento = date.today()
    atribuicao.save(update_fields=["dt_cancelamento"])

    assert (
        repositories.titulares_por_ue(
            "000532",
            date(2024, 6, 1),
        )
        == []
    )


def test_titulares_por_ue_nao_filtra_motivo(atribuicao):
    """Mantém atribuição com motivo de disponibilização."""
    atribuicao.codigo_motivo_disponibilizacao = 34
    atribuicao.save(update_fields=["codigo_motivo_disponibilizacao"])

    resultado = repositories.titulares_por_ue(
        "000532",
        date(2024, 6, 1),
    )

    assert len(resultado) == 1


def test_titulares_por_ue_nao_filtra_cargo_encerrado(atribuicao):
    """Mantém atribuição sem filtrar encerramento do cargo."""
    cargo = atribuicao.cargo_base
    cargo.dt_fim_nomeacao = date(2024, 5, 1)
    cargo.save(update_fields=["dt_fim_nomeacao"])

    resultado = repositories.titulares_por_ue(
        "000532",
        date(2024, 6, 1),
    )

    assert len(resultado) == 1


def test_titulares_por_ue_filtra_disponibilizacao_anterior(atribuicao):
    """Ignora disponibilização anterior a cinco de fevereiro."""
    atribuicao.dt_disponibilizacao_aulas = date(2024, 2, 4)
    atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])

    assert (
        repositories.titulares_por_ue(
            "000532",
            date(2024, 6, 1),
        )
        == []
    )


def test_titulares_por_ue_inclui_disponibilizacao_no_limite(atribuicao):
    """Inclui disponibilização realizada em cinco de fevereiro."""
    atribuicao.dt_disponibilizacao_aulas = date(2024, 2, 5)
    atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])

    resultado = repositories.titulares_por_ue(
        "000532",
        date(2024, 6, 1),
    )

    assert len(resultado) == 1


@pytest.mark.parametrize("codigo_tipo_turma", [None, 4])
def test_titulares_por_ue_ignora_tipo_turma_invalido(
    atribuicao,
    codigo_tipo_turma,
):
    """Ignora atribuição sem tipo de turma ou do tipo quatro."""
    atribuicao.codigo_tipo_turma = codigo_tipo_turma
    atribuicao.save(update_fields=["codigo_tipo_turma"])

    assert (
        repositories.titulares_por_ue(
            "000532",
            date(2024, 6, 1),
        )
        == []
    )


def test_titulares_por_ue_nao_inclui_externo(atribuicao_externa):
    """Não inclui atribuições externas no resultado por UE."""
    assert (
        repositories.titulares_por_ue(
            "000532",
            date(2024, 6, 1),
        )
        == []
    )


def test_remover_titulares_duplicados():
    """Mantém somente uma ocorrência de linhas idênticas."""
    titular = {
        "professor_rf": "7654321",
        "nome_professor": "Ana Silva",
        "disciplina": "Matematica",
        "disciplina_id": "138",
        "disciplinas_id": "138",
        "turma_id": 2112345,
    }

    assert repositories._remover_titulares_duplicados(
        [titular, titular.copy()]
    ) == [titular]


def test_buscar_turmas_professor_todos_anos_nao_filtra_ano(atribuicao):
    """Retorna atribuição efetiva sem restringir o ano letivo."""
    atribuicao.dt_atribuicao_aula = date.today() + timedelta(days=30)
    atribuicao.save(update_fields=["dt_atribuicao_aula"])

    resultado = repositories.buscar_turmas_professor_todos_anos("7654321")

    assert len(resultado) == 1
    assert resultado[0]["ano_letivo"] == "2024"
    assert resultado[0]["ano_atribuicao"] == 2024


def test_buscar_turmas_professor_todos_anos_ignora_cancelada(atribuicao):
    """Ignora atribuição com data de cancelamento."""
    atribuicao.dt_cancelamento = date(2024, 3, 1)
    atribuicao.save(update_fields=["dt_cancelamento"])

    resultado = repositories.buscar_turmas_professor_todos_anos("7654321")

    assert resultado == []


def test_buscar_turmas_professor_todos_anos_inclui_disponibilizada(
    atribuicao,
):
    """Inclui atribuição mesmo quando já foi disponibilizada."""
    atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
    atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])

    resultado = repositories.buscar_turmas_professor_todos_anos("7654321")

    assert len(resultado) == 1
    assert resultado[0]["data_fim_atribuicao"] == "2024-03-01T00:00:00"


def test_buscar_turmas_professor_todos_anos_inclui_externo(
    atribuicao_externa,
):
    """Retorna atribuição externa sem restringir o ano letivo."""
    resultado = repositories.buscar_turmas_professor_todos_anos("98765432100")

    assert len(resultado) == 1
    assert resultado[0]["ano_letivo"] == "2024"
    assert resultado[0]["codigo_rf"] == "98765432100"


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
