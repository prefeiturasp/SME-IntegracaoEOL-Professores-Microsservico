"""Queries do domínio de turmas."""

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
    """Lista turmas históricas do professor por ano letivo.

    Args:
        ano_letivo: Ano letivo usado no filtro de atribuições.
        professor_rf: RF do professor consultado.

    Returns:
        Turmas em status histórico atribuídas ao professor no ano.
    """
    atribuicoes = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=professor_rf,
        ano_atribuicao=ano_letivo,
        dt_cancelamento__isnull=True,
    )
    codigos = set(
        atribuicoes.exclude(codigo_turma_escola__isnull=True).values_list(
            "codigo_turma_escola", flat=True
        )
    )
    series = set(
        atribuicoes.exclude(codigo_serie_grade__isnull=True).values_list(
            "codigo_serie_grade", flat=True
        )
    )
    if series:
        codigos.update(
            SerieTurmaGrade.objects.filter(
                codigo_serie_grade__in=series
            ).values_list("codigo_turma", flat=True)
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
            "ano_letivo": t.ano_letivo,
            "codigo": t.codigo_turma,
            "tipo_turma": t.tipo_turma or 0,
            "modalidade": None,
            "codigo_modalidade": None,
            "nome_turma": None,
            "semestre": 0,
            "duracao_turno": 0,
            "tipo_turno": 0,
            "data_fim": None,
            "ehistorico": t.status in ("C", "E"),
            "ensino_especial": False,
            "etapa_eja": 0,
            "serie_ensino": None,
            "data_inicio_turma": None,
            "extinta": t.status == "E",
            "situacao": None,
            "ue_codigo": t.codigo_escola,
        }
        for t in turmas
    ]
