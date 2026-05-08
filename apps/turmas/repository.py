"""Queries do domínio Turmas (EP-24).

Importa models de apps.professores pois compartilham o mesmo banco.
"""

from apps.professores.models import (
    AtribuicaoAula,
    SerieTurmaGrade,
    TurmaEscola,
)

_STATUS_HISTORICO = ("O", "A", "C", "E")


def turmas_historicas_professor(
    ano_letivo: int,
    professor_rf: str,
) -> list[dict]:
    """EP-24 — Turmas históricas no formato TurmaDTO."""
    atribuicoes = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=professor_rf,
        ano_atribuicao=ano_letivo,
        dt_cancelamento__isnull=True,
    )
    codigos = set(
        atribuicoes.exclude(codigo_turma_escola__isnull=True)
        .values_list("codigo_turma_escola", flat=True)
    )
    series = set(
        atribuicoes.exclude(codigo_serie_grade__isnull=True)
        .values_list("codigo_serie_grade", flat=True)
    )
    if series:
        codigos.update(
            SerieTurmaGrade.objects.filter(codigo_serie_grade__in=series)
            .values_list("codigo_turma", flat=True)
        )

    if not codigos:
        return []

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
