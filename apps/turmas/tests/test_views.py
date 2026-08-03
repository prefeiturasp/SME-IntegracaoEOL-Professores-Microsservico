"""Testes das views do domínio de turmas."""

from datetime import date

import pytest

pytestmark = pytest.mark.django_db

_BASE = "/api/v1/professores/turmas/anos-letivos"


class TestEP24TurmasHistoricas:
    _url = f"{_BASE}/2024/professor/7654321/turmas-historicas-geral/"

    def test_retorna_lista_de_codigos(self, client, atribuicao):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(self._url)
        assert res.status_code == 200
        assert res.data == [2112345]

    def test_corpo_e_lista_de_inteiros(self, client, atribuicao):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(self._url)
        assert res.status_code == 200
        assert all(isinstance(codigo, int) for codigo in res.data)

    def test_sem_atribuicao_retorna_lista_vazia(self, client, db):
        res = client.get(self._url)
        assert res.status_code == 200
        assert res.data == []

    def test_atribuicao_sem_disponibilizacao_retorna_lista_vazia(
        self, client, atribuicao
    ):
        """Atribuição existente sem disponibilização não conta como turma."""
        assert atribuicao.dt_disponibilizacao_aulas is None
        res = client.get(self._url)
        assert res.status_code == 200
        assert res.data == []

    def test_ano_diferente_retorna_lista_vazia(self, client, atribuicao):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(
            f"{_BASE}/2099/professor/7654321/turmas-historicas-geral/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_professor_diferente_retorna_lista_vazia(self, client, atribuicao):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(
            f"{_BASE}/2024/professor/0000000/turmas-historicas-geral/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(self._url)
        assert res.status_code == 403
