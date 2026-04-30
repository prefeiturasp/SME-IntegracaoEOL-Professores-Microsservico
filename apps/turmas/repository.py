"""Queries do domínio Turmas (EP-24).

Importa models de apps.professores pois compartilham o mesmo banco.
"""

from apps.professores.models import AtribuicaoAula, TurmaEscola

_STATUS_HISTORICO = ("O", "A", "C", "E")


def turmas_historicas_professor(ano_letivo: int, professor_rf: str) -> list[dict]:
    """EP-24 — Turmas históricas do professor, no formato TurmaDTO do legado."""
    codigos = set(
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf=professor_rf,
            ano_atribuicao=ano_letivo,
        )
        .values_list("codigo_turma_escola", flat=True)
    )
    turmas = TurmaEscola.objects.filter(
        codigo_turma__in=codigos,
        status__in=_STATUS_HISTORICO,
    )
    return [
        {
            "ano": None,
            "anoLetivo": t.ano_letivo,
            "codigo": t.codigo_turma,
            "tipoTurma": t.tipo_turma or 0,
            "modalidade": None,
            "codigoModalidade": None,
            "nomeTurma": None,
            "semestre": 0,
            "duracaoTurno": 0,
            "tipoTurno": 0,
            "dataFim": None,
            "ehistorico": t.status in ("C", "E"),
            "ensinoEspecial": False,
            "etapaEJA": 0,
            "serieEnsino": None,
            "dataInicioTurma": None,
            "extinta": t.status == "E",
            "situacao": None,
            "ueCodigo": t.codigo_escola,
        }
        for t in turmas
    ]
