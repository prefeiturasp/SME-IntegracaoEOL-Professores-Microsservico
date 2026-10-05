"""Testes dos repositories do dominio de funcionarios."""

from datetime import UTC, date, datetime

import pytest

from apps.funcionarios import repositories
from apps.professores.models import (
    AtribuicaoAula,
    CargoSobrepostoServidor,
    FuncionarioConectaFormacao,
    FuncionarioConectaModalidadeEscola,
    FuncionarioSistemaPerfil,
    FuncionarioUnidadeEducacional,
    FuncionarioVinculoFuncional,
    LotacaoServidor,
)

pytestmark = pytest.mark.django_db

_PERFIL_1 = "ea741bf4-47ea-486d-8b88-5327521bcfc5"
_PERFIL_2 = "5f7d2f11-a7d6-4055-9a02-4af25e94b640"
_GUID_VAZIO = "00000000-0000-0000-0000-000000000000"

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


def test_cargos_funcionario_usa_vinculo_funcional_consolidado(db):
    """Verifica cargo do funcionário pelo consolidado funcional."""
    FuncionarioVinculoFuncional.objects.create(
        rf="7654321",
        cpf="12345678900",
        cd_cargo_base=3360,
        cargo_base="DIRETOR DE ESCOLA - v1",
        cd_dre_cargo_base="108100",
        cd_ue_cargo_base="000532",
        ue_cargo_base="ESCOLA TESTE",
        tipo_vinculo_cargo_base=1,
        data_inicio_cargo_base=datetime(2024, 1, 1, tzinfo=UTC),
        cd_cargo_sobreposto=3352,
        cargo_sobreposto="SUPERVISOR ESCOLAR - v1",
        cd_dre_cargo_sobreposto="108100",
        cd_ue_cargo_sobreposto="000533",
        ue_cargo_sobreposto="ESCOLA SOBREPOSTA",
        tipo_vinculo_cargo_sobreposto=1,
        data_inicio_cargo_sobreposto=datetime(2024, 1, 1, tzinfo=UTC),
    )

    resultado = list(repositories.cargos_funcionario("7654321"))

    assert len(resultado) == 1
    assert resultado[0].rf == "7654321"
    assert resultado[0].cargo_base == "DIRETOR DE ESCOLA - v1"
    assert resultado[0].cd_ue_cargo_base == "000532"
    assert resultado[0].cargo_sobreposto == "SUPERVISOR ESCOLAR - v1"


def test_funcionarios_conecta_formacao_filtra_cargo_dre_e_componente(db):
    """Verifica filtros da consulta do Conecta Formação."""
    FuncionarioConectaFormacao.objects.create(
        rf="7654321",
        nome="Ana Servidora",
        cpf="12345678900",
        cargo_codigo=3360,
        cargo="DIRETOR",
        cargo_dre_codigo="108100",
        cargo_ue_codigo="000532",
        tipo_vinculo=1,
        codigo_modalidade=5,
        ano_turma="6",
        codigo_componente_curricular=512,
        eh_tipo_jornada_jeif=True,
    )
    FuncionarioConectaFormacao.objects.create(
        rf="9999999",
        nome="Fora Filtro",
        cargo_codigo=3379,
        cargo="COORDENADOR",
        cargo_dre_codigo="108200",
        cargo_ue_codigo="000533",
        codigo_modalidade=5,
        ano_turma="7",
        codigo_componente_curricular=513,
    )

    resultado = list(
        repositories.funcionarios_conecta_formacao(
            {
                "codigos_cargos": [3360],
                "codigo_modalidade": [5],
                "anos_turma": ["6"],
                "codigos_dres": ["108100"],
                "codigos_componentes_curriculares": [512],
                "eh_tipo_jornada_jeif": True,
            }
        )
    )

    assert len(resultado) == 1
    assert resultado[0]["rf"] == "7654321"
    assert resultado[0]["cargo_codigo"] == 3360


def test_funcionarios_conecta_formacao_filtra_modalidade_por_unidade(db):
    """Verifica modalidade por unidade quando não há filtro de turma."""
    FuncionarioConectaModalidadeEscola.objects.create(
        codigo_ue="000532",
        codigo_modalidade=5,
    )
    FuncionarioConectaFormacao.objects.create(
        rf="7654321",
        nome="Ana Servidora",
        cargo_codigo=3360,
        cargo="DIRETOR",
        cargo_dre_codigo="108100",
        cargo_ue_codigo="000532",
        tipo_vinculo=1,
    )
    FuncionarioConectaFormacao.objects.create(
        rf="9999999",
        nome="Fora Filtro",
        cargo_codigo=3360,
        cargo="DIRETOR",
        cargo_dre_codigo="108100",
        cargo_ue_codigo="000533",
        tipo_vinculo=1,
    )

    resultado = list(
        repositories.funcionarios_conecta_formacao(
            {
                "codigos_cargos": [3360],
                "codigo_modalidade": [5],
            }
        )
    )

    assert len(resultado) == 1
    assert resultado[0]["rf"] == "7654321"


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


def test_funcionarios_por_unidade_perfis_filtra_unidade_e_perfil(db):
    """Verifica funcionarios por unidade e perfis do sistema."""
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Ana Perfil",
        email="ana@sme.prefeitura.sp.gov.br",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1000,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000002",
        nome_servidor="Fora Perfil",
        uad_codigo="108100",
        perfil=_PERFIL_2,
        sis_id=1000,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000003",
        nome_servidor="Fora Unidade",
        uad_codigo="999999",
        perfil=_PERFIL_1,
        sis_id=1000,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000004",
        nome_servidor="Fora Sistema",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1007,
    )

    resultado = repositories.funcionarios_por_unidade_perfis(
        "108100",
        [_PERFIL_1],
    )

    assert resultado == [
        {
            "login": "0000001",
            "nome_servidor": "Ana Perfil",
            "perfil": _PERFIL_1,
        }
    ]


def test_logins_admins_sme_por_perfis_remove_duplicados(db):
    """Verifica logins de administradores por perfis."""
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Ana Perfil",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1000,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Ana Outro Sistema",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1007,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000002",
        nome_servidor="Outro Perfil",
        uad_codigo="108100",
        perfil=_PERFIL_2,
        sis_id=1000,
    )

    resultado = repositories.logins_admins_sme_por_perfis([_PERFIL_1])

    assert resultado == ["0000001"]


def test_buscar_por_lista_login_consulta_funcionario_sistema_perfil(db):
    """Verifica busca de logins na tabela de perfis do sistema."""
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Ana Perfil",
        uad_codigo="108100",
        perfil=_GUID_VAZIO,
        sis_id=1000,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Ana Conecta",
        uad_codigo="108100",
        perfil=_GUID_VAZIO,
        sis_id=1007,
    )

    resultado = repositories.buscar_por_lista_login(["0000001"])

    assert resultado == [
        {
            "login": "0000001",
            "nome_servidor": "Ana Perfil",
            "perfil": _GUID_VAZIO,
        }
    ]


def test_usuarios_conecta_formacao_filtra_sistema_e_perfil(db):
    """Verifica usuários do Conecta Formação por perfil."""
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Ana Conecta",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1007,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000002",
        nome_servidor="Fora Sistema",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1000,
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000003",
        nome_servidor="Fora Perfil",
        uad_codigo="108100",
        perfil=_PERFIL_2,
        sis_id=1007,
    )

    resultado = repositories.usuarios_conecta_formacao([_PERFIL_1])

    assert resultado == [
        {
            "login": "0000001",
            "nome": "Ana Conecta",
            "nome_social": None,
            "perfil": _PERFIL_1,
        }
    ]


def test_dados_sigpae_por_rf_retorna_dados_consolidados(
    criar_funcionario_ue,
):
    """Verifica dados SIGPAE de funcionario existente no EOL."""
    criar_funcionario_ue(
        codigo_rf="0000001",
        nome="Vanessa Santicioli Guerreiro",
        cpf="000000000000",
        codigo_ue="000532",
        codigo_dre="108100",
        codigo_cargo="3379",
        cargo="SUPERVISOR ESCOLAR",
        nome_ue="SUPERVISAO ESCOLAR - PE",
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Vanessa Santicioli Guerreiro",
        email="email@sme.prefeitura.sp.gov.br",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1000,
    )

    resultado = repositories.dados_sigpae_por_rf("0000001")

    assert resultado == {
        "rf": "0000001",
        "cpf": "000000000000",
        "email": "email@sme.prefeitura.sp.gov.br",
        "cargos": [
            {
                "codigo_cargo": 3379,
                "descricao_cargo": "SUPERVISOR ESCOLAR",
                "codigo_unidade": "000532",
                "descricao_unidade": "SUPERVISAO ESCOLAR - PE",
                "codigo_dre": "108100",
                "contrato_externo": False,
            }
        ],
        "nome": "Vanessa Santicioli Guerreiro",
        "inexistente_eol": False,
    }


def test_cargos_sigpae_prioriza_cargo_de_gestao():
    """Verifica seleção de cargo de gestão conforme compatibilidade legada."""
    funcionarios = [
        FuncionarioUnidadeEducacional(
            codigo_rf="7750536",
            codigo_cargo="3085",
            cargo="ASSISTENTE DE DIRETOR DE ESCOLA",
            codigo_ue="093130",
            nome_ue="EMEF TESTE",
            codigo_dre="108100",
        ),
        FuncionarioUnidadeEducacional(
            codigo_rf="7750536",
            codigo_cargo="3182",
            cargo="SECRETARIO DE ESCOLA                    ",
            codigo_ue="093131",
            nome_ue="EMEF - MARIA ANTONIETA D'ALKIMIN BASTO, PROFA.",
            codigo_dre="108100",
        ),
        FuncionarioUnidadeEducacional(
            codigo_rf="7750536",
            codigo_cargo="4906",
            cargo="AUXILIAR TECNICO DE EDUCACAO",
            codigo_ue="093203",
            nome_ue="LAERTE RAMOS DE CARVALHO, PROF.",
            codigo_dre="109100",
        ),
    ]

    resultado = repositories._cargos_sigpae(funcionarios, funcionarios[-1])

    assert resultado == [
        {
            "codigo_cargo": 3085,
            "descricao_cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
            "codigo_unidade": "093130",
            "descricao_unidade": "EMEF TESTE",
            "codigo_dre": "108100",
            "contrato_externo": False,
        }
    ]


def test_cargos_sigpae_prioriza_cargo_sobreposto():
    """Verifica seleção de cargo sobreposto conforme compatibilidade legada."""
    funcionarios = [
        FuncionarioUnidadeEducacional(
            codigo_rf="7750536",
            codigo_cargo="3182",
            cargo="SECRETARIO DE ESCOLA                    ",
            codigo_ue="093131",
            nome_ue="EMEF - MARIA ANTONIETA D'ALKIMIN BASTO, PROFA.",
            codigo_dre="108100",
            origem_vinculo="cargo_sobreposto",
        ),
        FuncionarioUnidadeEducacional(
            codigo_rf="7750536",
            codigo_cargo="4906",
            cargo="AUXILIAR TECNICO DE EDUCACAO",
            codigo_ue="093203",
            nome_ue="LAERTE RAMOS DE CARVALHO, PROF.",
            codigo_dre="109100",
            origem_vinculo="lotacao",
        ),
    ]

    resultado = repositories._cargos_sigpae(funcionarios, funcionarios[-1])

    assert resultado == [
        {
            "codigo_cargo": 3182,
            "descricao_cargo": "SECRETARIO DE ESCOLA                    ",
            "codigo_unidade": "093131",
            "descricao_unidade": (
                "EMEF - MARIA ANTONIETA D'ALKIMIN BASTO, PROFA."
            ),
            "codigo_dre": "108100",
            "contrato_externo": False,
        }
    ]


def test_dados_sigpae_por_rf_retorna_fallback_sem_eol(db):
    """Verifica fallback SIGPAE quando funcionario inexiste no EOL."""
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Usuario CoreSSO",
        email="core@sme.prefeitura.sp.gov.br",
        cpf="12345678900",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1000,
    )

    resultado = repositories.dados_sigpae_por_rf("0000001")

    assert resultado == {
        "rf": "0000001",
        "cpf": "12345678900",
        "email": "core@sme.prefeitura.sp.gov.br",
        "cargos": None,
        "nome": "Usuario CoreSSO",
        "inexistente_eol": True,
    }


def test_dados_sigpae_por_rf_retorna_ultimo_cargo_sem_cargo_ativo(
    criar_funcionario_ue,
):
    """Verifica retorno do último cargo quando cargos ativos ficam vazios."""
    criar_funcionario_ue(
        codigo_rf="0000001",
        nome="Usuario EOL",
        cpf="12345678900",
        codigo_ue="000532",
        codigo_dre="108100",
        codigo_cargo="3085",
        cargo="PROFESSOR",
        nome_ue="EMEF TESTE",
        data_fim=datetime(2024, 12, 31, tzinfo=UTC),
    )
    FuncionarioSistemaPerfil.objects.create(
        login="0000001",
        nome_servidor="Usuario CoreSSO",
        email="core@sme.prefeitura.sp.gov.br",
        cpf="12345678900",
        uad_codigo="108100",
        perfil=_PERFIL_1,
        sis_id=1000,
    )

    resultado = repositories.dados_sigpae_por_rf("0000001")

    assert resultado == {
        "rf": "0000001",
        "cpf": "12345678900",
        "email": "core@sme.prefeitura.sp.gov.br",
        "cargos": [
            {
                "codigo_cargo": 3085,
                "descricao_cargo": "PROFESSOR",
                "codigo_unidade": "000532",
                "descricao_unidade": "EMEF TESTE",
                "codigo_dre": "108100",
                "contrato_externo": False,
            }
        ],
        "nome": "Usuario EOL",
        "inexistente_eol": False,
    }


def test_dados_sigpae_por_rf_sem_dados_retorna_none(db):
    """Verifica ausencia total de dados SIGPAE."""
    assert repositories.dados_sigpae_por_rf("0000001") is None


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
    funcionario = criar_vinculo_externo_consolidado(pessoa)
    funcionario.nome_ue = "CEI INDIR - JARDIM NORONHA"
    funcionario.save()

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
            "nome_ue": "JARDIM NORONHA",
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


def test_dre_ue_cargo_usa_data_de_origem_da_disponibilizacao(
    cargo_base, ue
):
    """Verifica atribuição ativa pela data de origem, não pela substituída."""
    LotacaoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_dre=ue.codigo_dre,
        dt_inicio=date(2020, 1, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2025,
        dt_atribuicao_aula=date(2025, 2, 1),
        # A carga substitui o nulo da origem pela data de fim da turma.
        dt_disponibilizacao_aulas=date(2025, 12, 20),
        dt_disponibilizacao_aulas_origem=None,
    )

    resultado = repositories.dre_ue_cargo(
        cargo_base.professor.codigo_rf,
        cargo_base.codigo_cargo,
    )

    assert resultado == [
        {
            "codigo_rf": "7654321",
            "codigo_dre": ue.codigo_dre,
            "codigo_ue": ue.codigo_ue,
            "cargo": None,
        }
    ]


def test_dre_ue_cargo_ignora_atribuicao_ja_disponibilizada(cargo_base, ue):
    """Verifica exclusão de atribuição com disponibilização na origem."""
    LotacaoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_dre=ue.codigo_dre,
        dt_inicio=date(2020, 1, 1),
    )
    AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2025,
        dt_atribuicao_aula=date(2025, 2, 1),
        dt_disponibilizacao_aulas=date(2025, 6, 30),
        dt_disponibilizacao_aulas_origem=date(2025, 6, 30),
    )

    resultado = repositories.dre_ue_cargo(
        cargo_base.professor.codigo_rf,
        cargo_base.codigo_cargo,
    )

    assert resultado == []
