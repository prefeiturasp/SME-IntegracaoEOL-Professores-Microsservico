"""Regras de negocio do dominio de professores."""

from dataclasses import dataclass
from datetime import date
from typing import Any

from apps.professores import repository


@dataclass(frozen=True)
class ResultadoServico:
    """Representa payload e status definidos por regra de negocio."""

    payload: Any
    status_code: int = 200


def buscar_professores_escola(
    codigo_eol_escola: str,
    ano_letivo: int = 0,
) -> list[dict]:
    """Lista professores de uma escola."""
    return repository.buscar_professores_escola(
        codigo_eol_escola,
        ano_letivo,
    )


def buscar_turmas_professor_escola_ano(
    codigo_eol_escola: str,
    ano_letivo: int,
    codigo_rf: str | None = None,
) -> list[dict]:
    """Lista turmas atribuidas em escola e ano letivo."""
    return repository.buscar_turmas_professor_escola_ano(
        codigo_rf or "",
        codigo_eol_escola,
        ano_letivo,
    )


def buscar_turmas_professor(
    codigo_rf: str,
    ano_letivo: int | None = None,
) -> list[dict]:
    """Lista turmas atribuidas ao professor."""
    if ano_letivo is not None:
        return repository.buscar_turmas_professor_ano(codigo_rf, ano_letivo)
    return repository.buscar_turmas_professor(codigo_rf)


def obter_nome_rf(rf_professor: str) -> str | None:
    """Retorna nome do professor por registro funcional."""
    return repository.obter_nome_rf(rf_professor)


def buscar_por_rf_ano(codigo_rf: str, ano_letivo: int) -> dict | None:
    """Retorna dados do professor por registro funcional e ano."""
    return repository.buscar_por_rf_ano(codigo_rf, ano_letivo)


def buscar_por_rf_dre_ue(codigo_rf: str) -> dict | None:
    """Retorna dados do professor por registro funcional."""
    return repository.buscar_por_rf_dre_ue(codigo_rf)


def autocomplete_professores(
    ano_letivo: int,
    dre_id: str,
    ue_id: str | None = None,
    nome: str | None = None,
) -> list[dict]:
    """Lista professores para autocomplete."""
    return repository.autocomplete_professores(
        ano_letivo,
        dre_id,
        ue_id=ue_id,
        nome=nome,
    )


def buscar_por_lista_rf(ano_letivo: int, payload: Any) -> list[dict]:
    """Lista professores a partir de payload legado de RFs."""
    lista_rf = payload if isinstance(payload, list) else []
    return repository.buscar_por_lista_rf(ano_letivo, lista_rf)


def verificar_validade(codigo_rf: str) -> bool:
    """Verifica se o professor possui vinculo valido."""
    return repository.verificar_validade(codigo_rf)


def eh_emei(codigo_rf: str) -> bool:
    """Verifica se o professor esta vinculado a EMEI."""
    return repository.eh_emei(codigo_rf)


def atribuicao_status(codigo_rf: str, codigo_turma: int) -> dict:
    """Retorna status de atribuicao do professor na turma."""
    return repository.atribuicao_status(codigo_rf, codigo_turma)


def _data_iso_ou_none(data_str: str | None) -> date | None:
    if not data_str:
        return None
    return date.fromisoformat(data_str)


def atribuicao_verificar_data(
    codigo_rf: str,
    codigo_turma: int,
    data_consulta: str | None,
) -> bool:
    """Verifica atribuicao do professor na turma em uma data."""
    return repository.atribuicao_verificar_data(
        codigo_rf,
        codigo_turma,
        _data_iso_ou_none(data_consulta),
    )


def atribuicao_disciplina_data(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_consulta: str | None,
    territorio_saber: str | None,
) -> bool:
    """Verifica atribuicao do professor na disciplina em uma data."""
    return repository.atribuicao_disciplina_data(
        codigo_rf,
        codigo_turma,
        disciplina_id,
        _data_iso_ou_none(data_consulta),
        (territorio_saber or "").lower() == "true",
    )


def atribuicao_disciplina_datatick(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_consulta_tick: str | None,
) -> ResultadoServico:
    """Verifica atribuicao do professor usando data em ticks."""
    if not data_consulta_tick:
        return ResultadoServico(
            {"detail": "Deve ser informada uma data valida"},
            400,
        )
    return ResultadoServico(
        repository.atribuicao_disciplina_datatick(
            codigo_rf,
            codigo_turma,
            disciplina_id,
            int(data_consulta_tick),
        )
    )


def atribuicao_recorrencia_datas(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_ticks: list[str],
) -> ResultadoServico:
    """Lista resultados de atribuicao para datas recorrentes."""
    ticks = [int(tick) for tick in data_ticks]
    if not ticks:
        return ResultadoServico(
            {"detail": "\u00c9 necess\u00e1rio informar as datas em ticks!"},
            400,
        )
    return ResultadoServico(
        repository.atribuicao_recorrencia_datas(
            codigo_rf,
            codigo_turma,
            disciplina_id,
            ticks,
        )
    )


def atribuicao_turmas_lista(
    codigo_rf: str,
    disciplina_id: int,
    payload: Any,
) -> ResultadoServico:
    """Lista resultados de atribuicao em turmas por disciplina."""
    if not payload:
        return ResultadoServico({"detail": "Informe uma turma!"}, 400)
    if not isinstance(payload, list):
        return ResultadoServico([])
    try:
        codigos_turma = [int(codigo) for codigo in payload]
    except (TypeError, ValueError):
        return ResultadoServico([])
    return ResultadoServico(
        repository.atribuicao_turmas_lista(
            codigo_rf,
            disciplina_id,
            codigos_turma,
        )
    )


def atribuicao_periodo(
    codigo_rf: str,
    codigo_turma: int,
    componente_curricular_id: int,
    data_inicio_periodo: str,
    data_fim_periodo: str,
) -> bool:
    """Verifica atribuicao do professor em periodo."""
    return repository.atribuicao_periodo(
        codigo_rf,
        codigo_turma,
        componente_curricular_id,
        date.fromisoformat(data_inicio_periodo),
        date.fromisoformat(data_fim_periodo),
    )


def professores_atribuidos_turma_disc(
    codigo_turma: int,
    disciplina_id: int,
    data_ticks: str | None,
) -> ResultadoServico:
    """Lista professores atribuidos a turma e disciplina em data."""
    if not data_ticks:
        return ResultadoServico(
            {"detail": "Deve ser informada uma data v\u00e1lida"},
            400,
        )
    return ResultadoServico(
        repository.professores_atribuidos_turma_disc(
            codigo_turma,
            disciplina_id,
            int(data_ticks),
        )
    )


def titular_por_turma_disciplina(
    codigo_turma: int,
    codigo_componente_curricular: int,
) -> dict | None:
    """Retorna professor titular por turma e disciplina."""
    return repository.titular_por_turma_disciplina(
        codigo_turma,
        codigo_componente_curricular,
    )


def titulares_por_turmas(codigos_turmas: list[str]) -> list[dict]:
    """Lista professores titulares por turmas."""
    codigos = [int(codigo) for codigo in codigos_turmas]
    return repository.titulares_por_turmas(codigos)


def titulares_por_turma_agrupamento(
    codigo_turma: int,
    realiza_agrupamento: str,
    codigo_rf: str | None = None,
    data_referencia: str | None = None,
) -> list[dict]:
    """Lista professores titulares por turma com agrupamento."""
    return repository.titulares_por_turma_agrupamento(
        codigo_turma,
        realiza_agrupamento.lower() == "true",
        codigo_rf=codigo_rf,
        data_referencia=_data_iso_ou_none(data_referencia),
    )


def titulares_por_ue(
    ue_codigo: str,
    data_referencia: str,
) -> list[dict]:
    """Lista professores titulares por unidade e data de referencia."""
    return repository.titulares_por_ue(
        ue_codigo,
        date.fromisoformat(data_referencia),
    )
