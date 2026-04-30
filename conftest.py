"""Fixtures globais de teste."""

from datetime import date, datetime, timezone

import pytest
from rest_framework.test import APIClient

from apps.professores.models import (
    AtribuicaoAula,
    AtribuicaoExterno,
    CargoBaseServidor,
    ContratoExterno,
    FuncaoAtividadeCargoServidor,
    LotacaoServidor,
    Pessoa,
    Professor,
    TurmaEscola,
    UnidadeEducacional,
)

_API_KEY = "test-key"
_DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=timezone.utc)


def date_to_ticks(d: date) -> int:
    """Converte date Python para .NET ticks (100ns desde 0001-01-01)."""
    dt = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    return int((dt - _DOTNET_EPOCH).total_seconds() * 10_000_000)


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Cria tabelas managed=False no banco SQLite em memória antes dos testes."""
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
    """APIClient autenticado com a API Key de teste."""
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
    return Professor.objects.create(
        codigo_rf="7654321", nome="Ana Silva", cpf="12345678900"
    )


@pytest.fixture
def ue(db) -> UnidadeEducacional:
    return UnidadeEducacional.objects.create(
        codigo_ue="000532", codigo_dre="108100", codigo_tipo_escola=4
    )


@pytest.fixture
def cargo_base(professor) -> CargoBaseServidor:
    return CargoBaseServidor.objects.create(
        professor=professor,
        codigo_cargo=3379,
        situacao_funcional=6,
        dt_posse=date(2020, 1, 1),
    )


@pytest.fixture
def lotacao(cargo_base, ue) -> LotacaoServidor:
    return LotacaoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        dt_inicio=date(2024, 2, 1),
    )


@pytest.fixture
def turma(db) -> TurmaEscola:
    return TurmaEscola.objects.create(
        codigo_turma=2112345,
        codigo_escola="000532",
        ano_letivo=2024,
        status="A",
    )


@pytest.fixture
def atribuicao(cargo_base, ue) -> AtribuicaoAula:
    return AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_turma_escola=2112345,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao_aula=date(2024, 2, 1),
    )


@pytest.fixture
def pessoa(db) -> Pessoa:
    return Pessoa.objects.create(
        codigo_pessoa=1, cpf="98765432100", nome="João Ext"
    )


@pytest.fixture
def contrato_externo(pessoa, ue) -> ContratoExterno:
    return ContratoExterno.objects.create(
        codigo_contrato=1,
        pessoa=pessoa,
        codigo_tipo_funcao=5,
        codigo_unidade_educacao=ue.codigo_ue,
    )


@pytest.fixture
def atribuicao_externa(contrato_externo, ue) -> AtribuicaoExterno:
    return AtribuicaoExterno.objects.create(
        contrato_externo=contrato_externo,
        codigo_unidade_educacao=ue.codigo_ue,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=2024,
        dt_atribuicao=date(2024, 2, 1),
    )


@pytest.fixture
def funcao_atividade(cargo_base, ue) -> FuncaoAtividadeCargoServidor:
    return FuncaoAtividadeCargoServidor.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_local_servico=ue.codigo_ue,
    )
