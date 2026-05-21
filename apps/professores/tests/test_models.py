"""Testes dos models do dominio de professores."""

from apps.professores.models import Pessoa, Professor


def test_str_professor_retorna_rf_e_nome():
    """Verifica representacao textual do professor."""
    professor = Professor(codigo_rf="7654321", nome="Ana Silva")

    assert str(professor) == "7654321 - Ana Silva"


def test_str_pessoa_retorna_cpf_e_nome():
    """Verifica representacao textual da pessoa."""
    pessoa = Pessoa(cpf="98765432100", nome="Joao Ext")

    assert str(pessoa) == "98765432100 - Joao Ext"
