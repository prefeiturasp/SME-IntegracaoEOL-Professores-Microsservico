"""Regras de negocio do dominio de professores."""

from dataclasses import dataclass
from datetime import date
from typing import Any

from apps.professores import repository


@dataclass(frozen=True)
class ResultadoServico:
    """Representa o resultado produzido pela camada de serviço."""

    payload: Any
    status_code: int = 200


def buscar_professores_escola(
    codigo_eol_escola: str,
    ano_letivo: int = 0,
) -> list[dict]:
    """Lista professores de uma escola.

    Args:
        codigo_eol_escola: Código EOL da escola consultada.
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.buscar_professores_escola(
        codigo_eol_escola,
        ano_letivo,
    )


def buscar_turmas_professor_escola_ano(
    codigo_eol_escola: str,
    ano_letivo: int,
    codigo_rf: str | None = None,
) -> list[dict]:
    """Lista turmas atribuidas em escola e ano letivo.

    Args:
        codigo_eol_escola: Código EOL da escola consultada.
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
        codigo_rf: Registro funcional do professor ou servidor consultado.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.buscar_turmas_professor_escola_ano(
        codigo_rf or "",
        codigo_eol_escola,
        ano_letivo,
    )


def buscar_turmas_professor(
    codigo_rf: str,
    ano_letivo: int | None = None,
) -> list[dict]:
    """Lista turmas atribuidas ao professor.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    if ano_letivo is not None:
        return repository.buscar_turmas_professor_ano(codigo_rf, ano_letivo)
    return repository.buscar_turmas_professor(codigo_rf)


def buscar_abrangencia_funcionario_perfil(
    login: str,
    id_perfil: str,
) -> dict:
    """Lista abrangência de turmas do funcionário.

    Args:
        login: Login do funcionário usado na consulta.
        id_perfil: Identificador do perfil SGP usado na consulta.

    Returns:
        Abrangência organizada por DRE, UE e turma.
    """
    return repository.buscar_abrangencia_funcionario_perfil(login, id_perfil)


def turmas_atribuidas_ue(
    codigo_rf: str,
    cargos: list[int] | None = None,
    codigo_dre: str | None = None,
) -> list[dict]:
    """Lista turmas atribuídas por vínculo com UE.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        cargos: Códigos de cargos usados como filtro.
        codigo_dre: Código EOL da DRE usada na consulta.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.turmas_atribuidas_ue(codigo_rf, cargos, codigo_dre)


def disciplinas_turmas_atribuidas_ue(
    codigo_rf: str,
    codigo_turma: int,
    cargos: list[int] | None = None,
    codigo_dre: str | None = None,
) -> list[dict]:
    """Lista disciplinas atribuídas por vínculo com UE.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        cargos: Códigos de cargos usados como filtro.
        codigo_dre: Código EOL da DRE usada na consulta.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.disciplinas_turmas_atribuidas_ue(
        codigo_rf,
        codigo_turma,
        cargos,
        codigo_dre,
    )


def obter_nome_rf(rf_professor: str) -> str | None:
    """Retorna nome do professor por registro funcional.

    Args:
        rf_professor: Registro funcional do professor consultado.

    Returns:
        Texto encontrado ou ``None`` quando não houver resultado.
    """
    return repository.obter_nome_rf(rf_professor)


def buscar_professor_com_atribuicao_aula_ano_letivo(
    codigo_rf: str, ano_letivo: int
) -> dict | None:
    """Retorna dados do professor com atribuicao de aula no ano letivo.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

    Returns:
        Dados encontrados ou ``None`` quando não houver resultado.
    """
    return repository.buscar_professor_com_atribuicao_aula_ano_letivo(
        codigo_rf, ano_letivo
    )


def buscar_por_rf_dre_ue(
    codigo_rf: str,
    ano_letivo: int,
    ue_id: str | None = None,
    buscar_outros_cargos: bool = False,
) -> dict | None:
    """Retorna dados do professor por RF/ano, com escopo e fallback externo.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
        ue_id: Código opcional da unidade educacional usada como escopo.
        buscar_outros_cargos: Indica se a busca deve ignorar o escopo de cargo.

    Returns:
        Dados encontrados ou ``None`` quando não houver resultado.
    """
    return repository.buscar_por_rf_dre_ue(
        codigo_rf,
        ano_letivo,
        ue_id=ue_id,
        buscar_outros_cargos=buscar_outros_cargos,
    )


def autocomplete_professores(
    ano_letivo: int,
    ue_id: str | None = None,
    nome: str | None = None,
) -> list[dict]:
    """Lista professores para autocomplete.

    Args:
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
        ue_id: Código opcional da unidade educacional usada como escopo.
        nome: Trecho do nome usado no autocomplete.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.autocomplete_professores(
        ano_letivo,
        ue_id=ue_id,
        nome=nome,
    )


def buscar_por_lista_rf(ano_letivo: int, dados: Any) -> list[dict]:
    """Lista professores por registros funcionais.

    Args:
        ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
        dados: Lista de registros funcionais recebida no corpo.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    lista_rf = dados if isinstance(dados, list) else []
    return repository.buscar_por_lista_rf(ano_letivo, lista_rf)


def verificar_validade(codigo_rf: str) -> bool:
    """Verifica se o professor possui vinculo valido.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.

    Returns:
        Resultado booleano da validação solicitada.
    """
    return repository.verificar_validade(codigo_rf)


def unidades_com_atribuicao_valida(codigo_rf: str) -> list[str]:
    """Lista UEs com atribuicao valida do professor (base do recorte EMEI).

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.

    Returns:
        Lista de códigos encontrados para os filtros informados.
    """
    return repository.unidades_com_atribuicao_valida(codigo_rf)


def atribuicao_status(codigo_rf: str, codigo_turma: int) -> dict:
    """Retorna status de atribuicao do professor na turma.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.

    Returns:
        Dados do status de atribuição mais recente na turma.
    """
    return repository.atribuicao_status(codigo_rf, codigo_turma)


def _data_iso_ou_none(data_str: str | None) -> date | None:
    """Retorna data opcional a partir de texto ISO.

    Args:
        data_str: Data em formato ISO recebida pela API.

    Returns:
        Data convertida, ou ``None`` quando não informada.
    """
    if not data_str:
        return None
    return date.fromisoformat(data_str)


def atribuicao_verificar_data(
    codigo_rf: str,
    codigo_turma: int,
    data_consulta: str | None,
) -> bool:
    """Verifica atribuicao do professor na turma em uma data.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        data_consulta: Data opcional usada para validar vigência.

    Returns:
        Resultado booleano da validação solicitada.
    """
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
    """Verifica atribuicao do professor na disciplina em uma data.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        disciplina_id: Identificador do componente curricular ou disciplina.
        data_consulta: Data opcional usada para validar vigência.
        territorio_saber: Indica consulta em território do saber.

    Returns:
        Resultado booleano da validação solicitada.
    """
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
    """Verifica atribuicao do professor usando data em ticks.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        disciplina_id: Identificador do componente curricular ou disciplina.
        data_consulta_tick: Data em ticks usada para validar vigência.

    Returns:
        Resultado do serviço com payload e status HTTP.
    """
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
    """Lista resultados de atribuicao para datas recorrentes.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        disciplina_id: Identificador do componente curricular ou disciplina.
        data_ticks: Datas em ticks usadas para validar vigência.

    Returns:
        Resultado do serviço com payload e status HTTP.
    """
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
    """Lista resultados de atribuicao em turmas por disciplina.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        disciplina_id: Identificador do componente curricular ou disciplina.
        payload: Lista de códigos de turma recebida no corpo.

    Returns:
        Resultado do serviço com payload e status HTTP.
    """
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
    """Verifica atribuicao do professor em periodo.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        componente_curricular_id: ID do componente curricular consultado.
        data_inicio_periodo: Data inicial do período consultado.
        data_fim_periodo: Data final do período consultado.

    Returns:
        Resultado booleano da validação solicitada.
    """
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
    """Lista professores atribuidos a turma e disciplina em data.

    Args:
        codigo_turma: Código EOL da turma consultada.
        disciplina_id: Identificador do componente curricular ou disciplina.
        data_ticks: Datas em ticks usadas para validar vigência.

    Returns:
        Resultado do serviço com payload e status HTTP.
    """
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
    """Retorna professor titular por turma e disciplina.

    Args:
        codigo_turma: Código EOL da turma consultada.
        codigo_componente_curricular: Código do componente curricular.

    Returns:
        Dados encontrados ou ``None`` quando não houver resultado.
    """
    return repository.titular_por_turma_disciplina(
        codigo_turma,
        codigo_componente_curricular,
    )


def titulares_por_turmas(codigos_turmas: list[str]) -> list[dict]:
    """Lista professores titulares por turmas.

    Args:
        codigos_turmas: Códigos EOL das turmas consultadas.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    codigos = [int(codigo) for codigo in codigos_turmas]
    return repository.titulares_por_turmas(codigos)


def titulares_por_turma_agrupamento(
    codigo_turma: int,
    realiza_agrupamento: str,
    codigo_rf: str | None = None,
    data_referencia: str | None = None,
) -> list[dict]:
    """Lista professores titulares por turma com agrupamento.

    Args:
        codigo_turma: Código EOL da turma consultada.
        realiza_agrupamento: Indica se titulares devem ser agrupados.
        codigo_rf: Registro funcional do professor ou servidor consultado.
        data_referencia: Data de referência usada para validar vigência.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
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
    """Lista professores titulares por unidade e data de referencia.

    Args:
        ue_codigo: Código EOL da unidade educacional consultada.
        data_referencia: Data de referência usada para validar vigência.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.titulares_por_ue(
        ue_codigo,
        date.fromisoformat(data_referencia),
    )
