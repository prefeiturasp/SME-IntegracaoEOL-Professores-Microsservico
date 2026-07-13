"""Testes do repository do domínio de turmas."""

from datetime import date

import pytest

from apps.professores.models import AtribuicaoAula, CargoBaseServidor
from apps.turmas import repository

pytestmark = pytest.mark.django_db


def _criar_atribuicao(
    cargo_base: CargoBaseServidor,
    codigo_turma_escola: int | None,
    *,
    ano_atribuicao: int = 2025,
    dt_disponibilizacao_aulas: date | None = date(2025, 3, 1),
    dt_cancelamento: date | None = None,
) -> AtribuicaoAula:
    """Cria atribuição de aula com os campos relevantes ao filtro."""
    return AtribuicaoAula.objects.create(
        cargo_base=cargo_base,
        codigo_unidade_educacao="000532",
        codigo_turma_escola=codigo_turma_escola,
        codigo_grade=100,
        codigo_componente_curricular=138,
        ano_atribuicao=ano_atribuicao,
        dt_atribuicao_aula=date(2025, 2, 1),
        dt_disponibilizacao_aulas=dt_disponibilizacao_aulas,
        dt_cancelamento=dt_cancelamento,
    )


class TestTurmasHistoricasProfessor:
    def test_retorna_codigos_unicos_ordenados(self, cargo_base):
        """Códigos distintos do professor, sem duplicatas e ordenados."""
        _criar_atribuicao(cargo_base, 3016391)
        _criar_atribuicao(cargo_base, 2822488)
        _criar_atribuicao(cargo_base, 2822488)
        _criar_atribuicao(cargo_base, 2822517)

        resultado = repository.turmas_historicas_professor(
            2025, cargo_base.professor.codigo_rf
        )

        assert resultado == [2822488, 2822517, 3016391]

    def test_exclui_atribuicao_cancelada(self, cargo_base):
        """Atribuição com dt_cancelamento preenchida é excluída."""
        _criar_atribuicao(
            cargo_base, 2822488, dt_cancelamento=date(2025, 4, 1)
        )

        resultado = repository.turmas_historicas_professor(
            2025, cargo_base.professor.codigo_rf
        )

        assert resultado == []

    def test_exclui_sem_disponibilizacao(self, cargo_base):
        """Atribuição sem dt_disponibilizacao_aulas é excluída."""
        _criar_atribuicao(cargo_base, 2822488, dt_disponibilizacao_aulas=None)

        resultado = repository.turmas_historicas_professor(
            2025, cargo_base.professor.codigo_rf
        )

        assert resultado == []

    def test_exclui_ano_divergente(self, cargo_base):
        """Atribuição de outro ano é excluída."""
        _criar_atribuicao(cargo_base, 2822488, ano_atribuicao=2024)

        resultado = repository.turmas_historicas_professor(
            2025, cargo_base.professor.codigo_rf
        )

        assert resultado == []

    def test_exclui_rf_divergente(self, cargo_base):
        """Consulta de outro RF não retorna as turmas do professor."""
        _criar_atribuicao(cargo_base, 2822488)

        resultado = repository.turmas_historicas_professor(2025, "0000000")

        assert resultado == []

    def test_ignora_turma_nula(self, cargo_base):
        """Atribuição com codigo_turma_escola nula é ignorada."""
        _criar_atribuicao(cargo_base, None)
        _criar_atribuicao(cargo_base, 2822498)

        resultado = repository.turmas_historicas_professor(
            2025, cargo_base.professor.codigo_rf
        )

        assert resultado == [2822498]

    def test_sem_atribuicoes_retorna_vazio(self, cargo_base):
        """Professor sem atribuições retorna lista vazia."""
        resultado = repository.turmas_historicas_professor(
            2025, cargo_base.professor.codigo_rf
        )

        assert resultado == []
