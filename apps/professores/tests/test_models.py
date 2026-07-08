"""Testes dos models do dominio de professores."""

from apps.professores.models import (
    AtribuicaoAula,
    AtribuicaoExterno,
    Pessoa,
    Professor,
)


def test_str_professor_retorna_rf_e_nome():
    """Verifica representacao textual do professor."""
    professor = Professor(codigo_rf="7654321", nome="Ana Silva")

    assert str(professor) == "7654321 - Ana Silva"


def test_str_pessoa_retorna_cpf_e_nome():
    """Verifica representacao textual da pessoa."""
    pessoa = Pessoa(cpf="98765432100", nome="Joao Ext")

    assert str(pessoa) == "98765432100 - Joao Ext"


def test_atribuicao_aula_mapeia_campos_desnormalizados():
    """Verifica campos desnormalizados da atribuicao de aula."""
    campos = [
        AtribuicaoAula._meta.get_field("descricao_turma_escola"),
        AtribuicaoAula._meta.get_field("descricao_componente_curricular"),
        AtribuicaoAula._meta.get_field("ano_escolar"),
        AtribuicaoAula._meta.get_field("codigo_etapa_ensino"),
        AtribuicaoAula._meta.get_field("dt_inicio_turma"),
        AtribuicaoAula._meta.get_field("dt_fim_turma"),
    ]

    assert all(campo.null for campo in campos)
    assert all(campo.blank for campo in campos)


def test_atribuicao_externo_mapeia_campos_desnormalizados():
    """Verifica campos desnormalizados da atribuicao externa."""
    campos = [
        AtribuicaoExterno._meta.get_field("descricao_turma_escola"),
        AtribuicaoExterno._meta.get_field("descricao_componente_curricular"),
        AtribuicaoExterno._meta.get_field("ano_escolar"),
        AtribuicaoExterno._meta.get_field("codigo_etapa_ensino"),
        AtribuicaoExterno._meta.get_field("dt_inicio_turma"),
        AtribuicaoExterno._meta.get_field("dt_fim_turma"),
    ]

    assert all(campo.null for campo in campos)
    assert all(campo.blank for campo in campos)
