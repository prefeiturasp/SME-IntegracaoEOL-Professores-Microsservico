"""Testes dos utilitarios compartilhados."""

from types import SimpleNamespace

from apps.core.utils import get_nome


def test_get_nome_prioriza_nome_social_preenchido():
    """Verifica uso do nome social quando preenchido."""
    pessoa = SimpleNamespace(nome="Nome Civil", nome_social="Nome Social")

    assert get_nome(pessoa) == "Nome Social"
