"""Testes das views do domínio Turmas (EP-24)."""

import pytest

pytestmark = pytest.mark.django_db

_BASE = "/api/turmas/anos-letivos"


# ---------------------------------------------------------------------------
# EP-24 — Turmas históricas do professor por ano
# ---------------------------------------------------------------------------


class TestEP24TurmasHistoricas:
    _url = f"{_BASE}/2024/professor/7654321/turmas-historicas-geral/"

    def test_retorna_turmas_do_professor(self, client, atribuicao, turma):
        # atribuicao liga professor 7654321 à turma 2112345 no ano 2024
        # turma fixture cria TurmaEscola 2112345 com status="A"
        res = client.get(self._url)
        assert res.status_code == 200
        assert any(t["codigo"] == 2112345 for t in res.data)

    def test_estrutura_dos_campos(self, client, atribuicao, turma):
        res = client.get(self._url)
        assert res.status_code == 200
        assert len(res.data) >= 1
        item = res.data[0]
        for campo in ("codigo", "nomeTurma", "ueCodigo", "anoLetivo", "ehistorico"):
            assert campo in item

    def test_sem_atribuicao_retorna_lista_vazia(self, client, db):
        res = client.get(self._url)
        assert res.status_code == 200
        assert res.data == []

    def test_atribuicao_sem_turma_nao_retorna_turma(self, client, atribuicao):
        # AtribuicaoAula existe (codigo_turma_escola=2112345), mas TurmaEscola não foi criada
        # → o JOIN com TurmaEscola falha e nenhuma turma é devolvida
        res = client.get(self._url)
        assert res.status_code == 200
        assert not any(t.get("codigo") == 2112345 for t in res.data)

    def test_ano_diferente_retorna_vazio(self, client, atribuicao, turma):
        res = client.get(f"{_BASE}/2099/professor/7654321/turmas-historicas-geral/")
        assert res.status_code == 200
        assert res.data == []

    def test_professor_diferente_retorna_vazio(self, client, atribuicao, turma):
        res = client.get(f"{_BASE}/2024/professor/0000000/turmas-historicas-geral/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(self._url)
        assert res.status_code == 403
