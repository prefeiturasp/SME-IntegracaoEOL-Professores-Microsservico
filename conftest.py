"""Fixtures globais de teste."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Any

import pytest
from rest_framework.test import APIClient

from apps.professores.models import (
    AtribuicaoAula,
    AtribuicaoExterno,
    CargoBaseServidor,
    ContratoExterno,
    FuncaoAtividadeCargoServidor,
    FuncionarioUnidadeEducacional,
    LotacaoServidor,
    Pessoa,
    Professor,
    UnidadeEducacional,
)

_API_KEY = "test-key"
_DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=UTC)


def date_to_ticks(d: date) -> int:
    """Retorna data em ticks .NET."""
    dt = datetime(d.year, d.month, d.day, tzinfo=UTC)
    return int((dt - _DOTNET_EPOCH).total_seconds() * 10_000_000)


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Prepara tabelas externas no banco SQLite antes dos testes."""
    from django.apps import apps
    from django.db import connections
    from django.test.utils import setup_databases, teardown_databases

    with django_db_blocker.unblock():
        old_config = setup_databases(verbosity=0, interactive=False)
        with connections["default"].schema_editor() as editor:
            criadas: set[str] = set()
            for model in apps.get_models():
                if not model._meta.managed:
                    table = model._meta.db_table
                    if table not in criadas:
                        editor.create_model(model)
                        criadas.add(table)

    yield

    with django_db_blocker.unblock():
        teardown_databases(old_config, verbosity=0)


@pytest.fixture
def client(settings) -> APIClient:
    """Retorna APIClient autenticado com API key de teste."""
    settings.API_KEY = _API_KEY
    c = APIClient()
    c.credentials(HTTP_X_API_KEY=_API_KEY)
    return c


@pytest.fixture
def anon() -> APIClient:
    """APIClient sem autenticação."""
    return APIClient()


# ---------------------------------------------------------------------------
# Fixtures de modelos
# ---------------------------------------------------------------------------


@pytest.fixture
def professor(db) -> Professor:
    """Cria professor para os testes."""
    return Professor.objects.create(
        codigo_rf="7654321", nome="Ana Silva", cpf="12345678900"
    )


@pytest.fixture
def ue(db) -> UnidadeEducacional:
    """Cria unidade educacional para os testes."""
    return UnidadeEducacional.objects.create(
        codigo_ue="000532", codigo_dre="108100", codigo_tipo_escola=4
    )


@pytest.fixture
def cargo_base(professor) -> CargoBaseServidor:
    """Cria cargo base de servidor para os testes."""
    return CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        situacao_funcional=6,
        dt_posse=date(2020, 1, 1),
    )


@pytest.fixture
def lotacao(cargo_base, ue) -> LotacaoServidor:
    """Cria lotacao de servidor para os testes."""
    FuncionarioUnidadeEducacional.objects.create(
        codigo_rf=cargo_base.professor.codigo_rf,
        nome=cargo_base.professor.nome,
        nome_social=cargo_base.professor.nome_social,
        cpf=cargo_base.professor.cpf,
        codigo_ue=ue.codigo_ue,
        codigo_dre=ue.codigo_dre,
        data_inicio=datetime(2024, 2, 1, tzinfo=UTC),
        codigo_cargo=str(cargo_base.codigo_cargo),
        cargo=cargo_base.descricao_cargo,
        codigo_tipo_funcao_atividade=0,
        origem_vinculo="lotacao",
        eh_professor=True,
        esta_afastado=False,
        funcao_externo=0,
        tipo_funcao_externo=0,
    )
    return LotacaoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_dre=ue.codigo_dre,
        dt_inicio=date(2024, 2, 1),
    )


@pytest.fixture
def criar_funcionario_ue(
    db,
) -> Callable[..., FuncionarioUnidadeEducacional]:
    """Cria funcionario consolidado com dados padrao para testes."""

    def _criar_funcionario_ue(
        codigo_rf: str = "1111111",
        nome: str = "Carlos Gestor",
        cpf: str = "11111111111",
        codigo_ue: str = "000532",
        codigo_dre: str = "108100",
        **campos: Any,
    ) -> FuncionarioUnidadeEducacional:
        dados = {
            "codigo_rf": codigo_rf,
            "nome": nome,
            "cpf": cpf,
            "codigo_ue": codigo_ue,
            "codigo_dre": codigo_dre,
            "data_inicio": datetime(2024, 1, 1, tzinfo=UTC),
            "codigo_cargo": "3360",
            "cargo": "DIRETOR",
            "codigo_tipo_funcao_atividade": 0,
            "origem_vinculo": "lotacao",
            "eh_professor": False,
            "esta_afastado": False,
            "funcao_externo": 0,
            "tipo_funcao_externo": 0,
        }
        dados.update(campos)
        return FuncionarioUnidadeEducacional.objects.create(**dados)

    return _criar_funcionario_ue


@pytest.fixture
def criar_supervisores_dre(
    criar_funcionario_ue,
) -> Callable[[], None]:
    """Cria funcionarios para validar filtro de supervisores da DRE."""

    def _criar_supervisores_dre() -> None:
        criar_funcionario_ue(
            nome="Supervisora Silva",
            nome_social="Supervisora Social",
            supervisor_dre=True,
        )
        criar_funcionario_ue(
            codigo_rf="2222222",
            nome="Funcionario Fora",
            cpf="22222222222",
            supervisor_dre=False,
        )
        criar_funcionario_ue(
            codigo_rf="3333333",
            nome="Supervisora Outra DRE",
            cpf="33333333333",
            codigo_ue="000533",
            codigo_dre="108200",
            supervisor_dre=True,
        )

    return _criar_supervisores_dre


@pytest.fixture
def preparar_pessoa_externa() -> Callable[..., None]:
    """Atualiza pessoa externa com dados completos para testes."""

    def _preparar_pessoa_externa(pessoa: Pessoa) -> None:
        pessoa.nome = "Nome Pessoa"
        pessoa.nome_social = "Nome social"
        pessoa.nome_pai = "Pai Externo"
        pessoa.nome_mae = "Mae Externa"
        pessoa.data_nascimento = date(1985, 3, 2)
        pessoa.rg = "1234567"
        pessoa.titulo_eleitoral = "987654"
        pessoa.pis_pasep = "11223344"
        pessoa.save()

    return _preparar_pessoa_externa


@pytest.fixture
def criar_vinculo_externo_consolidado(
    criar_funcionario_ue,
) -> Callable[..., FuncionarioUnidadeEducacional]:
    """Cria vinculo externo consolidado para testes."""

    def _criar_vinculo_externo_consolidado(
        pessoa: Pessoa,
    ) -> FuncionarioUnidadeEducacional:
        return criar_funcionario_ue(
            codigo_rf="EXT123",
            nome="Nome consolidado",
            nome_social=None,
            cpf="98765432100",
            data_inicio=datetime(2024, 2, 1, tzinfo=UTC),
            origem_vinculo="externo",
            funcao_externo=99,
            tipo_funcao_externo=2,
            nome_ue="EMEF Teste",
            tipo_funcionario_externo="Terceirizado",
            dc_funcao_externo="Auxiliar tecnico",
            pessoa=pessoa,
        )

    return _criar_vinculo_externo_consolidado


@pytest.fixture
def atribuicao(cargo_base, ue) -> AtribuicaoAula:
    """Cria atribuição de aula para os testes."""
    return AtribuicaoAula.objects.create(
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


@pytest.fixture
def atribuicao_ano_corrente(cargo_base, ue) -> AtribuicaoAula:
    """Cria atribuição de aula com ano_atribuicao do ano corrente."""
    return AtribuicaoAula.objects.create(
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
        dt_atribuicao_aula=date(date.today().year, 1, 1),
    )


@pytest.fixture
def pessoa(db) -> Pessoa:
    """Cria pessoa para os testes."""
    return Pessoa.objects.create(
        codigo_pessoa=1, cpf="98765432100", nome="João Ext"
    )


@pytest.fixture
def contrato_externo(pessoa, ue) -> ContratoExterno:
    """Cria contrato externo para os testes."""
    return ContratoExterno.objects.create(
        codigo_contrato=1,
        pessoa=pessoa,
        codigo_tipo_funcao=5,
        codigo_unidade_educacao=ue.codigo_ue,
    )


@pytest.fixture
def atribuicao_externa(contrato_externo, ue) -> AtribuicaoExterno:
    """Cria atribuição externa para os testes."""
    return AtribuicaoExterno.objects.create(
        contrato_externo=contrato_externo,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_turma_escola=2112345,
        descricao_turma_escola="1A",
        codigo_grade=100,
        codigo_componente_curricular=138,
        descricao_componente_curricular="Matematica",
        ano_escolar="1",
        ano_atribuicao=2024,
        codigo_etapa_ensino=1,
        dt_atribuicao=date(2024, 2, 1),
    )


@pytest.fixture
def funcao_atividade(cargo_base, ue) -> FuncaoAtividadeCargoServidor:
    """Cria função de atividade de cargo para os testes."""
    return FuncaoAtividadeCargoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_local_servico=ue.codigo_ue,
    )
