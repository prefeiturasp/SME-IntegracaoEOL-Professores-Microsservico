"""Queries do domínio Turmas (EP-24).

Importa models de apps.professores pois compartilham o mesmo banco.
"""

from apps.professores.models import AtribuicaoAula, AtribuicaoExterno, TurmaEscola

_STATUS_HISTORICO = ("O", "A", "C", "E")


def turmas_historicas_professor(ano_letivo: int, professor_rf: str) -> list[dict]:
    """EP-24 — Turmas históricas (incluindo extintas e canceladas) do professor."""
    codigos_turma_efetivo = set(
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf=professor_rf,
            ano_atribuicao=ano_letivo,
        )
        .values_list("codigo_turma_escola", flat=True)
    )
    turmas = TurmaEscola.objects.filter(
        codigo_turma__in=codigos_turma_efetivo,
        status__in=_STATUS_HISTORICO,
    )
    return [
        {
            "codigoTurma": t.codigo_turma,
            "nomeTurma": None,
            "codigoEscola": t.codigo_escola,
            "anoLetivo": t.ano_letivo,
            "status": t.status,
        }
        for t in turmas
    ]
