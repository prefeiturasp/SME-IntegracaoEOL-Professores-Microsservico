"""Testes dos serializers do domínio de funcionários."""

from datetime import UTC, datetime
from types import SimpleNamespace

from apps.funcionarios.serializers import (
    BuscarFuncionariosFiltroSerializer,
    CargoFuncionarioSerializer,
    ConectaFormacaoFiltroSerializer,
    ConectaFormacaoSerializer,
    FuncionariosSGPDreFiltroSerializer,
    ListaTextoSerializer,
    ListaUUIDSerializer,
    UsuarioConectaFormacaoSerializer,
    UsuariosConectaFormacaoFiltroSerializer,
    UsuariosSGPFiltroSerializer,
)


def test_cargo_funcionario_serializa_vinculo_funcional():
    """Verifica contrato de cargo do funcionário."""
    vinculo = SimpleNamespace(
        rf="7654321",
        cpf="12345678900",
        cd_cargo_base=3360,
        cargo_base="DIRETOR DE ESCOLA - v1",
        cd_dre_cargo_base="108100",
        cd_ue_cargo_base="000532",
        ue_cargo_base="ESCOLA TESTE",
        tipo_vinculo_cargo_base=1,
        data_inicio_cargo_base=datetime(2024, 1, 1, tzinfo=UTC),
        cd_cargo_sobreposto=None,
        cargo_sobreposto=None,
        cd_dre_cargo_sobreposto=None,
        cd_ue_cargo_sobreposto=None,
        ue_cargo_sobreposto=None,
        tipo_vinculo_cargo_sobreposto=None,
        data_inicio_cargo_sobreposto=None,
        cd_funcao_atividade=None,
        funcao_atividade=None,
        cd_dre_funcao_atividade=None,
        cd_ue_funcao_atividade=None,
        ue_funcao_atividade=None,
        tipo_vinculo_funcao_atividade=None,
        data_inicio_funcao_atividade=None,
        dt_cancelamento_funcao_atividade=None,
        dt_fim_funcao_atividade=None,
    )

    resultado = CargoFuncionarioSerializer(vinculo).data

    assert resultado == {
        "rf": 7654321,
        "cpf": "12345678900",
        "cd_cargo_base": 3360,
        "cargo_base": "DIRETOR DE ESCOLA - v1",
        "cd_dre_cargo_base": "108100",
        "cd_ue_cargo_base": "000532",
        "ue_cargo_base": "ESCOLA TESTE",
        "tipo_vinculo_cargo_base": 1,
        "data_inicio_cargo_base": "2024-01-01T00:00:00",
        "cd_cargo_sobreposto": None,
        "cargo_sobreposto": None,
        "cd_dre_cargo_sobreposto": None,
        "cd_ue_cargo_sobreposto": None,
        "ue_cargo_sobreposto": None,
        "tipo_vinculo_cargo_sobreposto": None,
        "data_inicio_cargo_sobreposto": None,
        "cd_funcao_atividade": None,
        "funcao_atividade": None,
        "cd_dre_funcao_atividade": None,
        "cd_ue_funcao_atividade": None,
        "ue_funcao_atividade": None,
        "tipo_vinculo_funcao_atividade": None,
        "data_inicio_funcao_atividade": None,
    }


def test_cargo_funcionario_omite_funcao_atividade_encerrada():
    """Verifica contrato de cargo com função atividade encerrada."""
    vinculo = SimpleNamespace(
        rf="7654321",
        cpf="12345678900",
        cd_cargo_base=3239,
        cargo_base="PROF.ED.INF.E ENS.FUND.I - v3",
        cd_dre_cargo_base="108800",
        cd_ue_cargo_base="094854",
        ue_cargo_base="ESCOLA TESTE",
        tipo_vinculo_cargo_base=3,
        data_inicio_cargo_base=datetime(2024, 1, 1, tzinfo=UTC),
        cd_cargo_sobreposto=None,
        cargo_sobreposto=None,
        cd_dre_cargo_sobreposto=None,
        cd_ue_cargo_sobreposto=None,
        ue_cargo_sobreposto=None,
        tipo_vinculo_cargo_sobreposto=None,
        data_inicio_cargo_sobreposto=None,
        cd_funcao_atividade=30,
        funcao_atividade="PROF APOIO PEDAGOGICO PAP - v3",
        cd_dre_funcao_atividade="108800",
        cd_ue_funcao_atividade="094854",
        ue_funcao_atividade="ESCOLA TESTE",
        tipo_vinculo_funcao_atividade=3,
        data_inicio_funcao_atividade=datetime(2024, 1, 1, tzinfo=UTC),
        dt_cancelamento_funcao_atividade=None,
        dt_fim_funcao_atividade=datetime(2024, 12, 31, tzinfo=UTC),
    )

    resultado = CargoFuncionarioSerializer(vinculo).data

    assert resultado["cd_funcao_atividade"] is None
    assert resultado["funcao_atividade"] is None
    assert resultado["cd_dre_funcao_atividade"] is None
    assert resultado["cd_ue_funcao_atividade"] is None
    assert resultado["ue_funcao_atividade"] is None
    assert resultado["tipo_vinculo_funcao_atividade"] is None
    assert resultado["data_inicio_funcao_atividade"] is None


def test_conecta_formacao_filtro_valida_parametros():
    """Verifica validação dos filtros do Conecta Formação."""
    serializer = ConectaFormacaoFiltroSerializer(
        data={
            "codigos_cargos": [3360],
            "codigos_funcoes": [],
            "codigo_modalidade": [5],
            "anos_turma": ["6"],
            "codigos_dres": ["108100"],
            "codigos_componentes_curriculares": [512],
            "eh_tipo_jornada_jeif": "true",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["codigos_cargos"] == [3360]
    assert serializer.validated_data["eh_tipo_jornada_jeif"] is True


def test_conecta_formacao_serializa_funcionario():
    """Verifica contrato de funcionário do Conecta Formação."""
    resultado = ConectaFormacaoSerializer(
        {
            "rf": "7654321",
            "nome": "Ana Servidora",
            "cpf": "12345678900",
            "cargo_codigo": 3360,
            "cargo": "DIRETOR",
            "cargo_dre_codigo": "108100",
            "cargo_ue_codigo": "000532",
            "funcao_codigo": None,
            "funcao": None,
            "funcao_dre_codigo": None,
            "funcao_ue_codigo": None,
            "tipo_vinculo": 1,
        }
    ).data

    assert resultado == {
        "rf": "7654321",
        "nome": "Ana Servidora",
        "cpf": "12345678900",
        "cargo_codigo": "3360",
        "cargo": "DIRETOR",
        "cargo_dre_codigo": "108100",
        "cargo_ue_codigo": "000532",
        "funcao_codigo": None,
        "funcao": None,
        "funcao_dre_codigo": None,
        "funcao_ue_codigo": None,
        "tipo_vinculo": 1,
    }


def test_usuarios_conecta_formacao_filtro_valida_perfis():
    """Verifica validação de perfis para usuários do Conecta."""
    serializer = UsuariosConectaFormacaoFiltroSerializer(
        data={"perfis": ["ea741bf4-47ea-486d-8b88-5327521bcfc5"]}
    )

    assert serializer.is_valid(), serializer.errors
    assert str(serializer.validated_data["perfis"][0]) == (
        "ea741bf4-47ea-486d-8b88-5327521bcfc5"
    )


def test_lista_texto_serializer_normaliza_corpo_invalido():
    """Verifica normalização de corpo não-lista para lista vazia."""
    serializer = ListaTextoSerializer(data={"invalido": True})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["itens"] == []


def test_lista_uuid_serializer_valida_identificadores():
    """Verifica validação de lista de identificadores."""
    serializer = ListaUUIDSerializer(
        data=["ea741bf4-47ea-486d-8b88-5327521bcfc5"]
    )

    assert serializer.is_valid(), serializer.errors
    assert str(serializer.validated_data["itens"][0]) == (
        "ea741bf4-47ea-486d-8b88-5327521bcfc5"
    )


def test_usuarios_sgp_filtro_exige_dre_ou_rf():
    """Verifica validação mínima dos filtros de usuários SGP."""
    serializer = UsuariosSGPFiltroSerializer(data={})

    assert not serializer.is_valid()


def test_usuarios_sgp_filtro_valida_codigo_rf():
    """Verifica filtros de usuários SGP por RF."""
    serializer = UsuariosSGPFiltroSerializer(data={"codigo_rf": "7654321"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["codigo_rf"] == "7654321"


def test_funcionarios_sgp_dre_filtro_valida_funcao():
    """Verifica filtros de funcionários SGP por DRE."""
    serializer = FuncionariosSGPDreFiltroSerializer(
        data={"codigo_funcao_atividade": "10"}
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["codigo_funcao_atividade"] == 10


def test_buscar_funcionarios_filtro_normaliza_corpo_invalido():
    """Verifica normalização de corpo não-dict para filtros vazios."""
    serializer = BuscarFuncionariosFiltroSerializer(data=["7654321"])

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {
        "codigo_rf": None,
        "codigo_ue": None,
        "nome_servidor": None,
    }


def test_usuario_conecta_formacao_serializa_usuario():
    """Verifica contrato de usuário do Conecta Formação."""
    resultado = UsuarioConectaFormacaoSerializer(
        {
            "login": "0000001",
            "nome": "Ana Conecta",
            "nome_social": None,
            "perfil": "ea741bf4-47ea-486d-8b88-5327521bcfc5",
        }
    ).data

    assert resultado == {
        "login": "0000001",
        "nome": "Ana Conecta",
        "nome_social": None,
        "perfil": "ea741bf4-47ea-486d-8b88-5327521bcfc5",
    }
