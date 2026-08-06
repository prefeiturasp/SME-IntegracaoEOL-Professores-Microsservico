"""Testes dos repositories do dominio de funcionarios."""

from datetime import UTC, date, datetime

import pytest

from apps.funcionarios import repositories
from apps.professores.models import (
    CargoSobrepostoServidor,
    FuncionarioUnidadeEducacional,
    LotacaoServidor,
)

pytestmark = pytest.mark.django_db


def test_dre_de_ue_retorna_none_sem_codigo():
    """Verifica consulta de DRE sem UE informada."""
    assert repositories._dre_de_ue(None) is None


def test_dre_de_ue_consulta_e_armazena_cache(ue):
    """Verifica busca de DRE por UE com cache local."""
    repositories._UE_DRE_CACHE.clear()

    assert repositories._dre_de_ue(ue.codigo_ue) == "108100"
    assert repositories._UE_DRE_CACHE[ue.codigo_ue] == "108100"


def test_dre_de_ue_guarda_none_quando_ue_nao_existe():
    """Verifica cache para UE inexistente."""
    repositories._UE_DRE_CACHE.clear()

    assert repositories._dre_de_ue("999999") is None
    assert repositories._UE_DRE_CACHE["999999"] is None


def test_funcionarios_por_lista_funcoes_externas_sem_funcoes():
    """Verifica retorno vazio sem funcoes externas."""
    assert (
        repositories.funcionarios_por_lista_funcoes_externas("000532", [])
        == []
    )


def test_nome_funcionario_prioriza_nome_social(lotacao):
    """Verifica uso de nome social no funcionario."""
    funcionario = FuncionarioUnidadeEducacional.objects.get(
        codigo_rf="7654321",
    )
    funcionario.nome_social = "Ana Social"
    funcionario.save()

    assert repositories._nome_funcionario(funcionario) == "Ana Social"


def test_funcionarios_por_ue_legado_usa_nome_civil(lotacao):
    """Verifica nome civil no contrato legado por UE."""
    funcionario = FuncionarioUnidadeEducacional.objects.get(
        codigo_rf="7654321",
    )
    funcionario.nome_social = "Ana Social"
    funcionario.save()

    resultado = repositories.funcionarios_por_ue(
        "000532",
        somente_professores=False,
    )

    assert resultado[0]["nome"] == "Ana Silva"


def test_lotacoes_ativas_filtra_sem_data_fim(lotacao):
    """Verifica filtro de lotacoes ativas."""
    assert repositories._lotacoes_ativas().count() == 1


def test_funcionarios_por_ue_cargo_filtra_cargo(lotacao):
    """Verifica funcionarios por UE e cargo."""
    resultado = repositories.funcionarios_por_ue_cargo("000532", 3379)

    assert resultado[0]["codigo_rf"] == "7654321"


def test_funcionarios_por_ue_legado_mantem_fim_nomeacao_lotacao(
    lotacao,
    criar_funcionario_ue,
):
    """Verifica fim de nomeação no bloco de lotação."""
    criar_funcionario_ue(
        data_fim=datetime(2024, 12, 31, tzinfo=UTC),
        dt_fim_nomeacao=datetime(2024, 12, 31, tzinfo=UTC),
        origem_vinculo="lotacao",
    )

    resultado = repositories.funcionarios_por_ue(
        "000532",
        somente_professores=False,
        codigos_rfs=["1111111"],
    )

    assert resultado[0]["codigo_rf"] == "1111111"


def test_funcionarios_por_ue_legado_ignora_fim_nomeacao_sobreposto(
    lotacao,
    criar_funcionario_ue,
):
    """Verifica filtro de nomeação no bloco de cargo sobreposto."""
    criar_funcionario_ue(
        data_fim=datetime(2024, 12, 31, tzinfo=UTC),
        dt_fim_nomeacao=datetime(2024, 12, 31, tzinfo=UTC),
        origem_vinculo="cargo_sobreposto",
    )

    resultado = repositories.funcionarios_por_ue(
        "000532",
        somente_professores=False,
        codigos_rfs=["1111111"],
    )

    assert resultado == []


def test_funcionarios_por_ue_legado_ignora_fim_funcao(
    lotacao,
    criar_funcionario_ue,
):
    """Verifica filtro de fim de função atividade no contrato legado."""
    criar_funcionario_ue(
        codigo_tipo_funcao_atividade=27,
        origem_vinculo="funcao_atividade",
        dt_fim_funcao_atividade=datetime(2024, 12, 31, tzinfo=UTC),
    )

    resultado = repositories.funcionarios_por_ue(
        "000532",
        somente_professores=False,
        codigos_rfs=["1111111"],
    )

    assert resultado == []


def test_funcionarios_por_ue_professor_ignora_vinculo_encerrado(
    lotacao,
    criar_funcionario_ue,
):
    """Verifica filtro de professor com vínculo ativo."""
    criar_funcionario_ue(
        nome="Carlos Professor",
        data_fim=datetime(2024, 12, 31, tzinfo=UTC),
        codigo_cargo="3239",
        cargo="PROFESSOR",
        eh_professor=True,
    )

    resultado = repositories.funcionarios_por_ue("000532")

    assert [item["codigo_rf"] for item in resultado] == ["7654321"]


def test_deduplicar_funcionarios_por_rf_mantem_primeira_ocorrencia():
    """Verifica retorno único por RF no contrato legado."""
    rows = [
        {"codigo_rf": "7654321", "nome": "Ana A"},
        {"codigo_rf": "7654321", "nome": "Ana B"},
        {"codigo_rf": "1111111", "nome": "Carlos"},
    ]

    resultado = repositories._deduplicar_funcionarios_por_rf(rows)

    assert resultado == (
        [
            {"codigo_rf": "7654321", "nome": "Ana A"},
            {"codigo_rf": "1111111", "nome": "Carlos"},
        ]
    )


def test_funcionarios_por_lista_cargos_retorna_cargo(lotacao):
    """Verifica funcionarios por lista de cargos."""
    resultado = repositories.funcionarios_por_lista_cargos("000532", [3379])

    assert resultado[0]["funcionario_rf"] == "7654321"


def test_funcionarios_por_funcao_atividade_retorna_funcionario(
    funcao_atividade,
):
    """Verifica funcionarios por funcao de atividade."""
    resultado = repositories.funcionarios_por_funcao_atividade("000532", 1)

    assert resultado[0]["codigo_rf"] == "7654321"


def test_funcionarios_por_lista_funcoes_atividade_retorna_funcionario(
    funcao_atividade,
):
    """Verifica funcionarios por lista de funcoes de atividade."""
    resultado = repositories.funcionarios_por_lista_funcoes_atividade(
        "000532",
        [1],
    )

    assert resultado[0]["funcionario_rf"] == "7654321"


def test_funcionarios_por_funcao_externa_retorna_contrato(contrato_externo):
    """Verifica funcionarios externos por funcao."""
    resultado = repositories.funcionarios_por_funcao_externa("000532", 5)

    assert resultado[0]["cpf"] == "98765432100"


def test_funcionarios_por_lista_funcoes_externas_retorna_contrato(
    contrato_externo,
):
    """Verifica funcionarios externos por lista de funcoes."""
    resultado = repositories.funcionarios_por_lista_funcoes_externas(
        "000532",
        [5],
    )

    assert resultado[0]["cpf"] == "98765432100"


def test_nome_cpf_servidor_retorna_funcionario_lotado(lotacao):
    """Verifica nome e CPF a partir do funcionario lotado."""
    resultado = repositories.nome_cpf_servidor("7654321")

    assert resultado == {"nome": "Ana Silva", "cpf": "12345678900"}


def test_buscar_funcionarios_ignora_vinculo_encerrado(
    lotacao,
    criar_funcionario_ue,
):
    """Verifica busca apenas em vínculos ativos."""
    criar_funcionario_ue(data_fim=datetime(2024, 12, 31, tzinfo=UTC))

    resultado = repositories.buscar_funcionarios(codigo_rf="1111111")

    assert resultado == []


def test_usuarios_sgp_por_perfil_filtra_por_dre_e_nome(lotacao):
    """Verifica filtros de DRE e nome em usuarios SGP."""
    resultado = repositories.usuarios_sgp_por_perfil(
        "perfil-guid-123",
        codigo_dre="108100",
        nome_servidor_param="Ana",
    )

    assert resultado[0]["codigo_rf"] == "7654321"
    assert resultado[0]["codigo_dre"] == "108100"
    assert resultado[0]["cd_cargo"] == "3379"


def test_usuarios_sgp_por_perfil_com_dre_usa_funcionario_consolidado(
    criar_funcionario_ue,
):
    """Verifica consulta por DRE a partir do vínculo consolidado."""
    criar_funcionario_ue(
        origem_vinculo="funcao_atividade",
        codigo_tipo_funcao_atividade=1,
    )

    resultado = repositories.usuarios_sgp_por_perfil(
        "perfil-guid-123",
        codigo_dre="108100",
    )

    assert resultado == [
        {
            "codigo_rf": "1111111",
            "login": "1111111",
            "nome_servidor": "Carlos Gestor",
            "codigo_dre": "108100",
            "codigo_ue": "000532",
            "cd_cargo": "3360",
            "codigo_funcao_atividade": 1,
            "funcao_externo": 0,
            "tipo_funcao_externo": 0,
        }
    ]


def test_usuarios_sgp_por_perfil_com_dre_usa_referencia(
    criar_funcionario_ue,
):
    """Verifica consulta por DRE no fluxo de perfil."""
    criar_funcionario_ue()
    criar_funcionario_ue(
        codigo_rf="2222222",
        nome="Beatriz Gestora",
        codigo_ue="108199",
        codigo_dre="200000",
    )

    resultado = repositories.usuarios_sgp_por_perfil(
        "perfil-guid-123",
        codigo_dre="108100",
    )

    assert [item["codigo_rf"] for item in resultado] == ["1111111"]


def test_usuarios_sgp_por_perfil_com_ue_prioriza_codigo_ue(
    criar_funcionario_ue,
):
    """Verifica consulta por UE quando DRE também é enviada."""
    criar_funcionario_ue(
        codigo_rf="2222222",
        nome="Beatriz Gestora",
        codigo_ue="000999",
        codigo_dre="108999",
    )

    resultado = repositories.usuarios_sgp_por_perfil(
        "perfil-guid-123",
        codigo_dre="108100",
        codigo_ue="000999",
    )

    assert resultado == [
        {
            "codigo_rf": "2222222",
            "login": "2222222",
            "nome_servidor": "Beatriz Gestora",
            "codigo_dre": "108100",
            "codigo_ue": "000999",
            "cd_cargo": "3360",
            "codigo_funcao_atividade": 0,
            "funcao_externo": 0,
            "tipo_funcao_externo": 0,
        }
    ]


def test_usuarios_sgp_por_perfil_com_rf_usa_funcionario_consolidado(
    criar_funcionario_ue,
):
    """Verifica consulta por RF a partir do vínculo consolidado."""
    criar_funcionario_ue(origem_vinculo="cargo_sobreposto")
    resultado = repositories.usuarios_sgp_por_perfil(
        "perfil-guid-123",
        codigo_rf="1111111",
    )

    assert resultado == [
        {
            "codigo_rf": "1111111",
            "login": "1111111",
            "nome_servidor": "Carlos Gestor",
            "codigo_dre": "108100",
            "codigo_ue": "000532",
            "cd_cargo": 0,
            "codigo_funcao_atividade": 0,
            "funcao_externo": 0,
            "tipo_funcao_externo": 0,
        }
    ]


def test_funcionarios_sgp_dre_filtra_por_ue_e_nome(lotacao):
    """Verifica filtros opcionais em funcionarios SGP por DRE."""
    resultado = repositories.funcionarios_sgp_dre(
        "perfil-guid-123",
        "108100",
        codigo_ue="000532",
        nome_servidor_param="Ana",
    )

    assert resultado[0]["codigo_rf"] == "7654321"
    assert resultado[0]["codigo_ue"] == "000532"


def test_funcionarios_sgp_dre_usa_prefixo_da_dre(criar_funcionario_ue):
    """Verifica consulta por DRE no fluxo legado direto."""
    criar_funcionario_ue(
        codigo_ue="108199",
        codigo_dre="200000",
    )
    criar_funcionario_ue(
        codigo_rf="2222222",
        nome="Beatriz Gestora",
        codigo_ue="000532",
        codigo_dre="108100",
    )

    resultado = repositories.funcionarios_sgp_dre(
        "perfil-guid-123",
        "108100",
    )

    assert [item["codigo_rf"] for item in resultado] == ["1111111"]


def test_funcionarios_sgp_dre_remove_duplicados_por_rf(lotacao, monkeypatch):
    """Verifica que funcionários duplicados não são repetidos."""
    funcionario = FuncionarioUnidadeEducacional.objects.get(
        codigo_rf="7654321"
    )

    class QueryFake:
        """Simula a cadeia de queryset usada na consulta."""

        annotate_kwargs = None
        filter_kwargs = None

        def filter(self, **kwargs):
            """Retorna a própria query após filtro."""
            self.filter_kwargs = kwargs
            if kwargs == {"ordem_rf": 1}:
                return [funcionario]
            return self

        def exclude(self, **_kwargs):
            """Retorna a própria query após exclusão."""
            return self

        def order_by(self, *_args):
            """Retorna a própria query após ordenação."""
            return self

        def values(self, *_args):
            """Retorna mapa vazio de funções."""
            return []

        def annotate(self, **kwargs):
            """Guarda as anotações da query."""
            self.annotate_kwargs = kwargs
            return self

    query = QueryFake()
    monkeypatch.setattr(
        repositories,
        "_funcionarios_sgp_por_dre_qs",
        lambda *args, **kwargs: query,
    )

    resultado = repositories.funcionarios_sgp_dre(
        "perfil-guid-123",
        "108100",
        codigo_rf="7654321",
    )

    assert [item["codigo_rf"] for item in resultado] == ["7654321"]
    assert "ordem_rf" in query.annotate_kwargs
    assert "ordem_vinculo" in query.annotate_kwargs
    assert query.filter_kwargs == {"ordem_rf": 1}


def test_supervisores_por_dre_usa_dre_da_lotacao_do_cargo_base(
    cargo_base,
):
    """Verifica supervisor por DRE conforme vínculo do cargo base."""
    LotacaoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao="019653",
        codigo_dre="100013",
        dt_inicio=date(1996, 9, 12),
        dt_fim=date(2000, 1, 1),
    )
    CargoSobrepostoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_cargo=3352,
        codigo_unidade_local_servico="108202",
    )

    resultado = repositories.supervisores_por_dre("100013", ["7654321"])

    assert resultado == [
        {"codigo_rf": "7654321", "nome_servidor": "Ana Silva"}
    ]


def test_supervisores_dres_filtra_por_dre_e_marcacao(
    criar_supervisores_dre,
):
    """Verifica supervisores da DRE no consolidado de funcionarios."""
    criar_supervisores_dre()

    resultado = repositories.supervisores_dres("108100")

    assert resultado == [
        {
            "codigo_rf": "1111111",
            "nome_servidor": "Supervisora Social",
        }
    ]


def test_supervisores_dres_sem_registros_retorna_lista_vazia(db):
    """Verifica lista vazia quando DRE nao possui supervisores."""
    assert repositories.supervisores_dres("108100") == []


def test_funcionario_externo_por_cpf_usa_vinculo_consolidado(
    contrato_externo,
    preparar_pessoa_externa,
    criar_vinculo_externo_consolidado,
):
    """Verifica retorno enriquecido pelo vinculo externo consolidado."""
    pessoa = contrato_externo.pessoa
    preparar_pessoa_externa(pessoa)
    criar_vinculo_externo_consolidado(pessoa)

    resultado = repositories.funcionario_externo_por_cpf("98765432100")

    assert resultado == [
        {
            "nome_pessoa": "Nome social",
            "nome_pai": "Pai Externo",
            "nome_mae": "Mae Externa",
            "data_nascimento": "1985-03-02T00:00:00",
            "rg": "1234567",
            "cpf": "98765432100",
            "titulo_eleitoral": "987654",
            "pis_pasep": "11223344",
            "codigo_contrato_externo": contrato_externo.codigo_contrato,
            "codigo_ue": "000532",
            "nome_ue": "EMEF Teste",
            "funcao": "Auxiliar tecnico",
            "tipo_funcionario": "Terceirizado",
        }
    ]


def test_funcionario_externo_por_cpf_sem_vinculo_retorna_campos_nulos(
    contrato_externo,
):
    """Verifica contrato externo sem vinculo consolidado."""
    pessoa = contrato_externo.pessoa

    resultado = repositories.funcionario_externo_por_cpf("98765432100")

    assert resultado == [
        {
            "nome_pessoa": pessoa.nome,
            "nome_pai": pessoa.nome_pai,
            "nome_mae": pessoa.nome_mae,
            "data_nascimento": None,
            "rg": pessoa.rg,
            "cpf": "98765432100",
            "titulo_eleitoral": pessoa.titulo_eleitoral,
            "pis_pasep": pessoa.pis_pasep,
            "codigo_contrato_externo": contrato_externo.codigo_contrato,
            "codigo_ue": contrato_externo.codigo_unidade_educacao,
            "nome_ue": None,
            "funcao": None,
            "tipo_funcionario": None,
        }
    ]
