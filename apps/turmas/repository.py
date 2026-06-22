"""Queries do domínio de turmas."""

from apps.professores.models import AtribuicaoAula


def turmas_historicas_professor(
    ano_letivo: int,
    professor_rf: str,
) -> list[int]:
    """Lista códigos de turma do professor no ano letivo, sem duplicatas.

    Considera apenas atribuições efetivas disponibilizadas e não canceladas,
    vinculadas ao RF informado.

    Args:
        ano_letivo: Ano letivo usado no filtro de atribuições.
        professor_rf: RF do professor consultado.

    Returns:
        Códigos de turma distintos, ordenados de forma crescente.
    """
    codigos = (
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=professor_rf,
            ano_atribuicao=ano_letivo,
            dt_disponibilizacao_aulas__isnull=False,
            dt_cancelamento__isnull=True,
            codigo_turma_escola__isnull=False,
        )
        .values_list("codigo_turma_escola", flat=True)
        .distinct()
    )
    return sorted(codigos)
