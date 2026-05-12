"""Testes das views do domínio Turmas (EP-24)."""

from datetime import date

import pytest

from apps.professores.models import (
    AtribuicaoAula,
    SerieTurmaGrade,
    TurmaEscola,
)

pytestmark = pytest.mark.django_db

_BASE = "/api/v1/professores/turmas/anos-letivos"


# ---------------------------------------------------------------------------
# EP-24 — Turmas históricas do professor por ano
# ---------------------------------------------------------------------------


class TestEP24TurmasHistoricas:
    _url = f"{_BASE}/2024/professor/7654321/turmas-historicas-geral/"

    def test_retorna_turmas_do_professor(self, client, atribuicao, turma):
        # atribuicao liga professor 7654321 à turma 2112345 no ano 2024
        # turma fixture cria TurmaEscola 2112345 com status="A"
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(self._url)
        assert res.status_code == 200
        assert any(t["codigo"] == 2112345 for t in res.data)

    def test_estrutura_dos_campos(self, client, atribuicao, turma):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(self._url)
        assert res.status_code == 200
        assert len(res.data) >= 1
        item = res.data[0]
        campos = (
            "codigo",
            "nomeTurma",
            "ueCodigo",
            "anoLetivo",
            "ehistorico",
        )
        for campo in campos:
            assert campo in item

    def test_sem_atribuicao_retorna_404(self, client, db):
        res = client.get(self._url)
        assert res.status_code == 404

    def test_atribuicao_sem_turma_retorna_404(self, client, atribuicao):
        # AtribuicaoAula existe, mas TurmaEscola nao foi criada.
        # Assim o JOIN com TurmaEscola nao devolve a turma.
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(self._url)
        assert res.status_code == 404

    def test_atribuicao_ativa_retorna_turma(
        self,
        client,
        atribuicao,
        turma,
    ):
        res = client.get(self._url)
        assert res.status_code == 200
        assert any(t["codigo"] == 2112345 for t in res.data)

    def test_retorna_turma_via_serie_grade(self, client, cargo_base, ue):
        AtribuicaoAula.objects.create(
            cargo_base=cargo_base,
            codigo_unidade_educacao=ue.codigo_ue,
            codigo_turma_escola=None,
            codigo_grade=100,
            codigo_componente_curricular=138,
            codigo_serie_grade=1040353,
            ano_atribuicao=2024,
            dt_atribuicao_aula=date(2024, 2, 1),
            dt_disponibilizacao_aulas=date(2024, 3, 1),
        )
        SerieTurmaGrade.objects.create(
            codigo_serie_grade=1040353,
            codigo_turma=3034841,
            codigo_escola=ue.codigo_ue,
            codigo_escola_grade=100,
        )
        TurmaEscola.objects.create(
            codigo_turma=3034841,
            codigo_escola=ue.codigo_ue,
            ano_letivo=2024,
            status="O",
        )

        res = client.get(self._url)

        assert res.status_code == 200
        assert any(t["codigo"] == 3034841 for t in res.data)

    def test_ano_diferente_retorna_404(self, client, atribuicao, turma):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(
            f"{_BASE}/2099/professor/7654321/turmas-historicas-geral/"
        )
        assert res.status_code == 404

    def test_professor_diferente_retorna_404(
        self,
        client,
        atribuicao,
        turma,
    ):
        atribuicao.dt_disponibilizacao_aulas = date(2024, 3, 1)
        atribuicao.save(update_fields=["dt_disponibilizacao_aulas"])
        res = client.get(
            f"{_BASE}/2024/professor/0000000/turmas-historicas-geral/"
        )
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(self._url)
        assert res.status_code == 403
