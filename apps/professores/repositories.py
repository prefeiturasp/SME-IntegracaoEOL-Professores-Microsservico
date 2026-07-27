"""Queries do domínio de professores."""

from datetime import date
from typing import Any

from django.db.models import Q

from apps.core.utils import (
    fmt_br,
    fmt_iso,
    get_nome,
    ticks_to_date,
    ticks_to_datetime_str,
)
from apps.professores.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoAula,
    AtribuicaoExterno,
    CargoBaseServidor,
    ContratoExterno,
    DisciplinaTurmaAtribuidaUe,
    Professor,
    TurmaAtribuidaUe,
)

_CD_MOTIVO_DISPONIBILIZACAO = 34
_CD_MOTIVO_DISPONIBILIZACAO_EXTERNO_FIM_ANO_LETIVO = 3


def _filtrar_localizacao(qs: Any, ue_id: str | None) -> Any:
    """Aplica filtro opcional de unidade educacional.

    Args:
        qs: Atribuições ou contratos externos consultados.
        ue_id: Código EOL da unidade educacional usada como escopo.

    Returns:
        Dados filtrados por UE quando o escopo for informado.
    """
    if ue_id:
        return qs.filter(codigo_unidade_educacao=ue_id)
    return qs


def _filtro_turma(codigo_turma: int) -> Q:
    """Monta filtro para código EOL de turma.

    Args:
        codigo_turma: Código EOL da turma consultada.

    Returns:
        Expressão ``Q`` para filtrar a turma.
    """
    return Q(codigo_turma_escola=codigo_turma)


def _filtro_turmas_anos_iniciais() -> Q:
    """Monta filtro para turmas de anos iniciais.

    Returns:
        Expressão ``Q`` para turmas do 1º ao 6º ano.
    """
    return (
        Q(descricao_turma_escola__startswith="1")
        | Q(descricao_turma_escola__startswith="2")
        | Q(descricao_turma_escola__startswith="3")
        | Q(descricao_turma_escola__startswith="4")
        | Q(descricao_turma_escola__startswith="5")
        | Q(descricao_turma_escola__startswith="6")
    )


def _codigo_turma(atribuicao: Any) -> int | None:
    """Retorna o código de turma da atribuição.

    Args:
        atribuicao: Atribuição efetiva ou externa com código de turma.

    Returns:
        Código EOL da turma como inteiro, ou ``None`` quando ausente.
    """
    if atribuicao.codigo_turma_escola:
        return int(atribuicao.codigo_turma_escola)
    return None


def _vigentes_em(qs: Any, data_ref: date) -> Any:
    """Filtra atribuições vigentes em uma data de referência.

    Args:
        qs: Atribuições consultadas.
        data_ref: Data usada para validar início e disponibilização.

    Returns:
        Atribuições vigentes na data.
    """
    return qs.filter(
        dt_cancelamento__isnull=True, dt_atribuicao_aula__lte=data_ref
    ).filter(
        Q(dt_disponibilizacao_aulas__isnull=True)
        | Q(dt_disponibilizacao_aulas__gte=data_ref)
    )


def _vigentes_abrangencia_professor(qs: Any, data_ref: date) -> Any:
    """Filtra atribuições vigentes para a abrangência de turmas.

    Não considera vigente a atribuição já disponibilizada — inclusive de
    turma de programa no mês corrente —, acompanhando a abrangência do legado.

    Args:
        qs: Atribuições do professor.
        data_ref: Data usada para validar vigência e ano de atribuição.

    Returns:
        Atribuições vigentes para cálculo da abrangência.
    """
    qs = qs.filter(
        dt_cancelamento__isnull=True,
        dt_atribuicao_aula__lte=data_ref,
        ano_atribuicao=data_ref.year,
    )
    return qs.filter(
        Q(dt_disponibilizacao_aulas__isnull=True)
        | Q(dt_disponibilizacao_aulas__gte=data_ref)
    )


def _turma_row(aa: AtribuicaoAula) -> dict:
    """Monta turma atribuída efetiva.

    Args:
        aa: Atribuição de aula efetiva.

    Returns:
        Dicionário com dados da turma atribuída.
    """
    return {
        "codigo_turma": aa.codigo_turma_escola,
        "nome_turma": aa.descricao_turma_escola,
        "componente_curricular": aa.descricao_componente_curricular,
        "data_inicio_atribuicao": fmt_br(aa.dt_atribuicao_aula),
        "data_fim_atribuicao": fmt_br(aa.dt_disponibilizacao_aulas),
        "data_inicio_turma": fmt_br(aa.dt_inicio_turma),
        "ano": aa.ano_escolar,
        "etapa_ensino": aa.codigo_etapa_ensino,
    }


def _turma_row_externo(ae: AtribuicaoExterno) -> dict:
    """Monta turma atribuída externa.

    Args:
        ae: Atribuição de profissional externo.

    Returns:
        Dicionário com dados da turma atribuída externa.
    """
    return {
        "codigo_turma": ae.codigo_turma_escola,
        "nome_turma": ae.descricao_turma_escola,
        "componente_curricular": ae.descricao_componente_curricular,
        "data_inicio_atribuicao": fmt_br(ae.dt_atribuicao),
        "data_fim_atribuicao": fmt_br(ae.dt_disponibilizacao),
        "data_inicio_turma": fmt_br(ae.dt_inicio_turma),
        "ano": ae.ano_escolar,
        "etapa_ensino": ae.codigo_etapa_ensino,
    }


def _ancora_row(aa: AtribuicaoAula) -> dict:
    """Monta o vínculo-âncora de uma atribuição efetiva.

    Args:
        aa: Atribuição de aula efetiva.

    Returns:
        Dicionário com dados da turma, componente e vigência da atribuição.
    """
    codigo_turma_escola = aa.codigo_turma_escola
    return {
        "codigo_turma": (
            int(codigo_turma_escola) if codigo_turma_escola else None
        ),
        "nome_turma": aa.descricao_turma_escola,
        "codigo_serie_grade": aa.codigo_serie_grade,
        "componente_curricular": aa.descricao_componente_curricular,
        "codigo_unidade_educacao": aa.codigo_unidade_educacao,
        "ano": aa.ano_escolar,
        "etapa_ensino": aa.codigo_etapa_ensino,
        "data_atribuicao": fmt_br(aa.dt_atribuicao_aula),
        "data_disponibilizacao": fmt_br(aa.dt_disponibilizacao_aulas),
        "data_inicio_turma": fmt_br(aa.dt_inicio_turma),
    }


def _ancora_row_externo(ae: AtribuicaoExterno) -> dict:
    """Monta o vínculo-âncora de uma atribuição externa.

    Args:
        ae: Atribuição de profissional externo.

    Returns:
        Dicionário com dados da turma, componente e vigência da atribuição.
    """
    codigo_turma_escola = ae.codigo_turma_escola
    return {
        "codigo_turma": (
            int(codigo_turma_escola) if codigo_turma_escola else None
        ),
        "nome_turma": ae.descricao_turma_escola,
        "componente_curricular": ae.descricao_componente_curricular,
        "codigo_serie_grade": ae.codigo_serie_grade,
        "codigo_unidade_educacao": ae.codigo_unidade_educacao,
        "ano": ae.ano_escolar,
        "etapa_ensino": ae.codigo_etapa_ensino,
        "data_atribuicao": fmt_br(ae.dt_atribuicao),
        "data_disponibilizacao": fmt_br(ae.dt_disponibilizacao),
        "data_inicio_turma": fmt_br(ae.dt_inicio_turma),
    }


def _abrangencia_turma_row(
    row: dict,
) -> dict:
    """Monta turma para abrangência.

    Args:
        row: Linha de atribuição com dados de DRE, UE e turma.

    Returns:
        Dicionário da turma no formato de abrangência do legado.
    """
    tipo_turma = row.get("codigo_tipo_turma")
    turma_programa = tipo_turma in (2, 3, 4, 5)
    return {
        "ano": "0" if turma_programa else row["ano"],
        "ano_letivo": row["ano_letivo"],
        "codigo": row["codigo_turma"],
        "codigo_modalidade": (
            5 if turma_programa else row.get("codigo_modalidade") or 0
        ),
        "modalidade": (
            "Fundamental" if turma_programa else row.get("modalidade")
        ),
        "nome_turma": row["nome_turma"],
        "semestre": row.get("semestre") or 0,
        "duracao_turno": row.get("duracao_turno") or 0,
        "tipo_turno": row.get("tipo_turno") or 0,
        "etapa_eja": 0,
        "data_fim": None,
        "ehistorico": False,
        "ensino_especial": False,
        "serie_ensino": None,
        "data_inicio_turma": fmt_iso(row.get("data_inicio_turma")),
        "extinta": False,
        "tipo_turma": tipo_turma,
    }


def _abrangencia_retorno(rows: list[dict]) -> dict:
    """Agrupa linhas de abrangência por DRE e UE.

    Args:
        rows: Linhas de atribuições vigentes para abrangência.

    Returns:
        Estrutura de abrangência organizada por DRE, UE e turma.
    """
    dres: dict[str, dict] = {}

    for row in rows:
        codigo_ue = row["codigo_unidade_educacao"]
        codigo_dre = row.get("codigo_dre")
        dre = dres.setdefault(
            codigo_dre or "",
            {
                "abreviacao": row.get("abreviacao_dre"),
                "codigo": codigo_dre,
                "nome": row.get("nome_dre"),
                "ues": {},
            },
        )
        ues_dre = dre["ues"]
        ue_item = ues_dre.setdefault(
            codigo_ue,
            {
                "codigo": codigo_ue,
                "cod_tipo_escola": row.get("codigo_tipo_escola"),
                "nome": row.get("nome_unidade_educacional"),
                "turmas": [],
            },
        )
        ue_item["turmas"].append(_abrangencia_turma_row(row))

    return {
        "abrangencia": None,
        "dres": [
            {**dre, "ues": list(dre["ues"].values())} for dre in dres.values()
        ],
    }


def _turma_atribuida_ue_row(turma: TurmaAtribuidaUe) -> dict:
    """Monta turma atribuída por vínculo com UE.

    Args:
        turma: Registro de turma atribuída por UE.

    Returns:
        Dicionário no contrato de turmas por vínculo com UE.
    """
    return {
        "codigo_escola": turma.codigo_escola,
        "codigo_turma": turma.codigo_turma,
        "ano_letivo": turma.ano_letivo,
        "modalidade": turma.modalidade,
        "semestre": turma.semestre,
        "codigo_modalidade": turma.codigo_modalidade,
        "codigo_dre": turma.codigo_dre,
        "dre": turma.dre,
        "dre_abreviacao": turma.dre_abreviacao,
        "ue": turma.ue,
        "ue_abreviacao": turma.ue_abreviacao,
        "nome_turma": turma.nome_turma,
        "ano": turma.ano,
        "tipo_ue": turma.tipo_ue,
        "codigo_tipo_ue": turma.codigo_tipo_ue,
        "codigo_tipo_escola": turma.codigo_tipo_escola,
        "tipo_escola": turma.tipo_escola,
        "duracao_turno": turma.duracao_turno,
        "tipo_turno": turma.tipo_turno,
    }


def turmas_atribuidas_ue(
    codigo_rf: str,
    cargos: list[int] | None = None,
    codigo_dre: str | None = None,
) -> list[dict]:
    """Lista turmas atribuídas por vínculo com unidade educacional.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        cargos: Códigos de cargos usados como filtro opcional.
        codigo_dre: Código EOL da DRE usada como filtro opcional.

    Returns:
        Turmas atribuídas ao usuário pelos vínculos com unidades escolares.
    """
    qs = TurmaAtribuidaUe.objects.filter(usuario_rf=codigo_rf)
    if cargos:
        qs = qs.filter(Q(cargo__in=cargos) | Q(cargo_sobreposto__in=cargos))
    if codigo_dre:
        qs = qs.filter(codigo_dre=codigo_dre)
    qs = qs.order_by("codigo_escola", "nome_turma", "codigo_turma")
    return [_turma_atribuida_ue_row(turma) for turma in qs]


def _disciplina_turma_atribuida_ue_row(
    disciplina: DisciplinaTurmaAtribuidaUe,
) -> dict:
    """Monta disciplina atribuída por vínculo com UE.

    Args:
        disciplina: Registro de disciplina atribuída por UE.

    Returns:
        Dicionário no contrato de disciplinas por UE.
    """
    return {
        "codigo": disciplina.codigo_componente_curricular,
        "descricao": disciplina.descricao_componente_curricular,
        "codigo_componente_curricular_pai": (
            disciplina.codigo_componente_curricular_pai
        ),
        "regencia": disciplina.regencia,
        "codigo_componente_territorio_saber": (
            disciplina.codigo_componente_territorio_saber
        ),
        "territorio_saber": disciplina.territorio_saber,
        "tipo_escola": disciplina.tipo_escola,
        "turma_codigo": disciplina.codigo_turma,
        "ano_letivo": disciplina.ano_letivo,
        "professor": disciplina.usuario_rf,
    }


def disciplinas_turmas_atribuidas_ue(
    codigo_rf: str,
    codigo_turma: int,
    cargos: list[int] | None = None,
    codigo_dre: str | None = None,
) -> list[dict]:
    """Lista disciplinas atribuídas por vínculo com unidade educacional.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.
        codigo_turma: Código EOL da turma consultada.
        cargos: Códigos de cargos usados como filtro opcional.
        codigo_dre: Código EOL da DRE usada como filtro opcional.

    Returns:
        Disciplinas da turma atribuídas ao usuário pelos vínculos com UE.
    """
    qs = DisciplinaTurmaAtribuidaUe.objects.filter(
        usuario_rf=codigo_rf,
        codigo_turma=codigo_turma,
    )
    if cargos:
        qs = qs.filter(Q(cargo__in=cargos) | Q(cargo_sobreposto__in=cargos))
    if codigo_dre:
        qs = qs.filter(codigo_dre=codigo_dre)
    qs = qs.order_by("descricao_componente_curricular")
    return [_disciplina_turma_atribuida_ue_row(item) for item in qs]


def _linhas_abrangencia_atribuicoes(qs: Any) -> list[dict]:
    """Extrai linhas únicas de abrangência a partir de atribuições.

    Args:
        qs: Atribuições vigentes do funcionário.

    Returns:
        Linhas únicas por unidade educacional e turma.
    """
    vistas: set[tuple] = set()
    rows = []
    for aa in qs:
        codigo_turma = _codigo_turma(aa)
        chave = (aa.codigo_unidade_educacao, codigo_turma)
        if chave in vistas:
            continue
        vistas.add(chave)
        rows.append(
            {
                "codigo_unidade_educacao": aa.codigo_unidade_educacao,
                "codigo_turma": codigo_turma,
                "nome_turma": aa.descricao_turma_escola,
                "ano": aa.ano_escolar,
                "ano_letivo": aa.ano_atribuicao,
                "codigo_dre": aa.codigo_dre,
                "nome_dre": aa.nome_dre,
                "abreviacao_dre": aa.abreviacao_dre,
                "nome_unidade_educacional": aa.nome_unidade_educacional,
                "codigo_tipo_escola": aa.codigo_tipo_escola,
                "codigo_tipo_turma": aa.codigo_tipo_turma,
                "modalidade": aa.modalidade,
                "codigo_modalidade": aa.codigo_modalidade,
                "semestre": aa.semestre,
                "duracao_turno": aa.duracao_turno,
                "tipo_turno": aa.tipo_turno,
                "data_inicio_turma": aa.dt_inicio_turma,
            }
        )
    return rows


def buscar_professores_escola(codigo_ue: str, ano_letivo: int) -> list[dict]:
    """Lista professores de uma escola por ano letivo.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        ano_letivo: Ano letivo usado no filtro de atribuições.

    Returns:
        Lista de professores vinculados à escola no ano informado.
    """
    qs = _vigentes_em(
        AtribuicaoAula.objects.filter(
            codigo_unidade_educacao=codigo_ue,
            ano_atribuicao=ano_letivo,
        ),
        date.today(),
    ).select_related("cargo_base__professor")
    resultado = []
    for aa in qs:
        prof = aa.cargo_base.professor
        resultado.append(
            {
                "codigo_rf": int(prof.codigo_rf),
                "nome": get_nome(prof),
                "cargo": None,
                "cpf": prof.cpf,
                "data_inicio_exercicio": fmt_iso(aa.cargo_base.dt_posse),
            }
        )
    return resultado


def buscar_turmas_professor_escola_ano(
    codigo_rf: str, codigo_ue: str, ano_letivo: int
) -> list[dict]:
    """Lista turmas do professor em uma escola por ano.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_ue: CodigoEOL da unidade educacional.
        ano_letivo: Ano letivo usado no filtro de atribuições.

    Returns:
        Lista de turmas efetivas e externas do professor.
    """
    efetivas_qs = AtribuicaoAula.objects.filter(
        codigo_unidade_educacao=codigo_ue,
        ano_atribuicao=ano_letivo,
    )
    if codigo_rf:
        efetivas_qs = efetivas_qs.filter(
            cargo_base__professor__codigo_rf=codigo_rf
        )
    else:
        efetivas_qs = efetivas_qs.filter(_filtro_turmas_anos_iniciais())

    efetivas = list(
        _vigentes_em(
            efetivas_qs,
            date.today(),
        )
    )
    externas_qs = AtribuicaoExterno.objects.filter(
        codigo_unidade_educacao=codigo_ue,
        ano_atribuicao=ano_letivo,
    )
    if codigo_rf:
        externas_qs = externas_qs.filter(
            contrato_externo__pessoa__cpf=codigo_rf
        )
    else:
        externas_qs = externas_qs.filter(_filtro_turmas_anos_iniciais())
    return [_turma_row(aa) for aa in efetivas] + [
        _turma_row_externo(ae) for ae in externas_qs
    ]


def buscar_turmas_professor(codigo_rf: str) -> list[dict]:
    """Lista os vínculos-âncora de turma atribuídos ao professor.

    Args:
        codigo_rf: Registro funcional do professor.

    Returns:
        Lista de vínculos-âncora efetivos do professor.
    """
    efetivas = _vigentes_em(
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            ano_atribuicao=date.today().year,
        ),
        date.today(),
    )
    vistas: set[tuple] = set()
    resultado = []
    for aa in efetivas:
        chave = (aa.codigo_turma_escola, aa.codigo_unidade_educacao)
        if chave not in vistas:
            vistas.add(chave)
            resultado.append(_ancora_row(aa))
    return resultado


def buscar_turmas_professor_ano(codigo_rf: str, ano_letivo: int) -> list[dict]:
    """Lista turmas atribuídas ao professor por ano.

    Args:
        codigo_rf: Registro funcional do professor.
        ano_letivo: Ano letivo usado no filtro de atribuições.

    Returns:
        Lista de turmas atribuídas ao professor no ano informado.
    """
    efetivas = _vigentes_em(
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            ano_atribuicao=ano_letivo,
        ),
        date.today(),
    )
    externas = AtribuicaoExterno.objects.filter(
        contrato_externo__pessoa__cpf=codigo_rf,
        ano_atribuicao=ano_letivo,
    )
    return [_ancora_row(aa) for aa in efetivas] + [
        _ancora_row_externo(ae) for ae in externas
    ]


def buscar_abrangencia_funcionario_perfil(
    login: str,
    _id_perfil: str,
) -> dict:
    """Lista abrangência de turmas do funcionário.

    Args:
        login: Login do funcionário.
        _id_perfil: Perfil recebido na consulta.

    Returns:
        Abrangência organizada por DRE, UE e turma.
    """
    efetivas = _vigentes_abrangencia_professor(
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=login,
        ),
        date.today(),
    )
    rows = _linhas_abrangencia_atribuicoes(efetivas)
    return _abrangencia_retorno(rows)


def obter_nome_rf(rf: str) -> str | None:
    """Retorna nome do professor por RF.

    Args:
        rf: Registro funcional do professor.

    Returns:
        Nome do professor encontrado ou ``None``.
    """
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    return get_nome(prof)


def buscar_professor_com_atribuicao_aula_ano_letivo(
    codigo_rf: str, ano_letivo: int
) -> dict | None:
    """Retorna professor com atribuição de aula.

    Args:
        codigo_rf: Registro funcional do professor.
        ano_letivo: Ano letivo da data de atribuição de aula.

    Returns:
        Dados básicos do professor encontrado ou ``None``.
    """
    atribuicao = (
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            dt_cancelamento__isnull=True,
            dt_atribuicao_aula__lte=date.today(),
        )
        .filter(
            Q(dt_disponibilizacao_aulas__isnull=True)
            | Q(dt_disponibilizacao_aulas__year=ano_letivo)
        )
        .select_related("cargo_base__professor")
        .first()
    )

    if not atribuicao:
        return None

    prof = atribuicao.cargo_base.professor

    return {
        "codigo_rf": prof.codigo_rf,
        "nome": get_nome(prof),
    }


def buscar_por_rf_dre_ue(
    rf: str,
    ano_letivo: int,
    ue_id: str | None = None,
    buscar_outros_cargos: bool = False,
) -> dict | None:
    """Retorna dados do professor, com fallback externo.

    Args:
        rf: Registro funcional (ou CPF, no caso externo) do professor.
        ano_letivo: Ano letivo de referência.
        ue_id: Código opcional da UE para escopo.
        buscar_outros_cargos: Quando ``True``, ignora o escopo de DRE/UE.

    Returns:
        Dados básicos do professor encontrado ou ``None``.
    """
    atribuicoes = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=rf,
        ano_atribuicao=ano_letivo,
        dt_cancelamento__isnull=True,
    )
    if not buscar_outros_cargos:
        atribuicoes = _filtrar_localizacao(atribuicoes, ue_id)
    aa = atribuicoes.select_related("cargo_base__professor").first()
    if aa:
        prof = aa.cargo_base.professor
        return {"codigo_rf": prof.codigo_rf, "nome": get_nome(prof)}

    contrato = (
        ContratoExterno.objects.filter(
            pessoa__cpf=rf, dt_cancelamento__isnull=True
        )
        .select_related("pessoa")
        .first()
    )
    if contrato:
        pessoa = contrato.pessoa
        return {"codigo_rf": pessoa.cpf, "nome": get_nome(pessoa)}
    return None


def autocomplete_professores(
    ano_letivo: int,
    ue_id: str | None = None,
    nome: str | None = None,
) -> list[dict]:
    """Lista professores para autocomplete.

    Args:
        ano_letivo: Ano letivo usado no filtro de atribuições.
        ue_id: Código opcional da unidade educacional.
        nome: Trecho opcional do nome do professor.

    Returns:
        Lista limitada de professores encontrados para autocomplete.
    """
    # NOSONAR # TODO: dt_disponibilizacao_aulas__isnull=True é um proxy para
    # atribuição ativa. O filtro pode restringir codigos_turma_escola
    # com status in ('A','O') e dt_fim nulo.
    efetivos = AtribuicaoAula.objects.filter(
        ano_atribuicao=ano_letivo,
        dt_cancelamento__isnull=True,
        dt_disponibilizacao_aulas__isnull=True,
        cargo_base__dt_fim_nomeacao__isnull=True,
    ).select_related("cargo_base__professor")

    externos = AtribuicaoExterno.objects.filter(
        ano_atribuicao=ano_letivo,
        dt_cancelamento__isnull=True,
        dt_disponibilizacao__isnull=True,
        contrato_externo__dt_cancelamento__isnull=True,
    ).select_related("contrato_externo__pessoa")

    efetivos = _filtrar_localizacao(efetivos, ue_id)
    externos = _filtrar_localizacao(externos, ue_id)

    if nome:
        efetivos = efetivos.filter(
            cargo_base__professor__nome__istartswith=nome
        )
        externos = externos.filter(
            contrato_externo__pessoa__nome__istartswith=nome
        )

    # União dedup por RF/CPF; ordena por nome asc e corta em 10.
    candidatos: dict[str, str] = {}
    for aa in efetivos:
        prof = aa.cargo_base.professor
        candidatos.setdefault(prof.codigo_rf, get_nome(prof))
    for ae in externos:
        pessoa = ae.contrato_externo.pessoa
        candidatos.setdefault(pessoa.cpf, get_nome(pessoa))

    ordenados = sorted(candidatos.items(), key=lambda item: item[1])
    return [
        {"codigo_rf": rf, "nome_servidor": nome_servidor}
        for rf, nome_servidor in ordenados[:10]
    ]


def buscar_por_lista_rf(ano_letivo: int, lista_rf: list[str]) -> list[dict]:
    """Lista professores por RFs e ano letivo, um item por turma atribuída.

    Args:
        ano_letivo: Ano letivo usado no filtro de atribuições.
        lista_rf: Lista de registros funcionais pesquisados.

    Returns:
        Lista de ``{codigo_rf, nome}`` com um item por turma vigente.
        O mesmo professor aparece N vezes se tiver N turmas.
    """
    qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf__in=lista_rf,
        ano_atribuicao=ano_letivo,
        dt_cancelamento__isnull=True,
    ).select_related("cargo_base__professor")
    vistas: set[tuple] = set()
    resultado = []
    for aa in qs:
        prof = aa.cargo_base.professor
        chave = (prof.codigo_rf, aa.codigo_turma_escola)
        if chave not in vistas:
            vistas.add(chave)
            resultado.append(
                {"codigo_rf": prof.codigo_rf, "nome": get_nome(prof)}
            )
    # NOSONAR # TODO: evitar retorno de dados por turma do professor.
    return resultado


def verificar_validade(rf: str) -> bool:
    """Verifica se o professor possui vínculo ativo.

    Args:
        rf: Registro funcional do professor.

    Returns:
        ``True`` quando existe cargo ativo para o professor.
    """
    return bool(
        CargoBaseServidor.objects.filter(
            professor__codigo_rf=rf,
            dt_fim_nomeacao__isnull=True,
        ).exists()
    )


_CD_CARGO_PROF_INFANTIL_FUND_I = 3239


def unidades_com_atribuicao_valida(codigo_rf: str) -> list[str]:
    """Lista as UEs onde o professor tem atribuição válida.

    Considera cargo 3239 (PROF.ED.INF.E ENS.FUND.I), atribuição não
    cancelada e nomeação vigente.

    Args:
        codigo_rf: Registro funcional do professor.

    Returns:
        Códigos EOL das unidades com atribuição válida, sem repetição.
    """
    return list(
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            cargo_base__codigo_cargo=_CD_CARGO_PROF_INFANTIL_FUND_I,
            dt_cancelamento__isnull=True,
            cargo_base__dt_fim_nomeacao__isnull=True,
        )
        .values_list("codigo_unidade_educacao", flat=True)
        .distinct()
    )


def atribuicao_status(codigo_rf: str, codigo_turma: int) -> dict:
    """Retorna status de atribuição do professor na turma.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_turma: CodigoEOL da turma.

    Returns:
        Dados de status da atribuição mais recente na turma.
    """
    aa = (
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
        )
        .filter(_filtro_turma(codigo_turma))
        .filter(
            Q(dt_disponibilizacao_aulas__isnull=True)
            | Q(dt_disponibilizacao_aulas__gte=date.today())
        )
        .order_by("-dt_atribuicao_aula")
        .first()
    )
    if not aa:
        return {
            "ano_atribuicao": None,
            "data_cancelamento": None,
            "data_disponibilizacao": None,
            "data_fim_turma": None,
            "codigo_motivo_disponibilizacao": None,
        }
    return {
        "ano_atribuicao": aa.ano_atribuicao,
        "data_cancelamento": fmt_iso(aa.dt_cancelamento),
        "data_disponibilizacao": fmt_iso(aa.dt_disponibilizacao_aulas),
        "data_fim_turma": fmt_iso(aa.dt_fim_turma),
        "codigo_motivo_disponibilizacao": aa.codigo_motivo_disponibilizacao,
    }


def atribuicao_verificar_data(
    codigo_rf: str,
    codigo_turma: int,
    data_consulta: date | None = None,
) -> bool:
    """Verifica atribuição do professor em uma data.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_turma: CodigoEOL da turma.
        data_consulta: Data opcional usada para validar vigência.

    Returns:
        ``True`` quando existe atribuição compatível com os filtros.
    """
    qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
    ).filter(_filtro_turma(codigo_turma))
    if data_consulta:
        qs = _vigentes_em(qs, data_consulta)
    return bool(qs.exists())


def atribuicao_disciplina_data(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_consulta: date | None = None,
    territorio_saber: bool = False,
) -> bool:
    """Verifica atribuição do professor em turma e disciplina.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_turma: CodigoEOL da turma.
        disciplina_id: Código do componente curricular.
        data_consulta: Data opcional usada para validar vigência.
        territorio_saber: Indica consulta em território do saber.

    Returns:
        ``True`` quando existe atribuição para turma e disciplina.
    """
    if territorio_saber:
        qs = AgrupamentoAtribuicaoTerritorioSaber.objects.filter(
            rf_professor=codigo_rf,
            codigo_turma=codigo_turma,
        )
        if data_consulta:
            qs = qs.filter(dt_inicio_atribuicao__lte=data_consulta)
        return bool(qs.exists())

    qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_componente_curricular=disciplina_id,
    ).filter(_filtro_turma(codigo_turma))
    if data_consulta:
        qs = _vigentes_em(qs, data_consulta)
    return bool(qs.exists())


def atribuicao_disciplina_datatick(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_tick: int | None = None,
) -> bool:
    """Verifica atribuição usando data em ticks.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_turma: CodigoEOL da turma.
        disciplina_id: Código do componente curricular.
        data_tick: Data opcional em ticks.

    Returns:
        ``True`` quando existe atribuição vigente na data informada.

    Raises:
        OverflowError: Quando os ticks informados excedem uma data válida.
    """
    data = ticks_to_date(data_tick) if data_tick else None
    return atribuicao_disciplina_data(
        codigo_rf, codigo_turma, disciplina_id, data
    )


def atribuicao_recorrencia_datas(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_ticks: list[int],
) -> list[dict]:
    """Lista resultados de atribuição para datas recorrentes.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_turma: CodigoEOL da turma.
        disciplina_id: Código do componente curricular.
        data_ticks: Lista de datas em ticks para validação.

    Returns:
        Lista com o resultado de persistência para cada data.

    Raises:
        OverflowError: Quando algum tick informado excede uma data válida.
    """
    return [
        {
            "data": ticks_to_datetime_str(tick),
            "pode_persistir": atribuicao_disciplina_data(
                codigo_rf, codigo_turma, disciplina_id, ticks_to_date(tick)
            ),
        }
        for tick in data_ticks
    ]


def atribuicao_turmas_lista(
    codigo_rf: str, disciplina_id: int, codigos_turma: list[int]
) -> list[dict]:
    """Lista status de atribuição para turmas informadas.

    Args:
        codigo_rf: Registro funcional do professor.
        disciplina_id: Código do componente curricular.
        codigos_turma: Lista de códigos EOL das turmas.

    Returns:
        Lista de períodos de atribuição por turma encontrada.
    """
    codigos = [int(codigo_turma) for codigo_turma in codigos_turma]

    resultado = []

    aa = (
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            codigo_componente_curricular=disciplina_id,
            codigo_turma_escola__in=codigos,
        )
        .filter(
            Q(dt_disponibilizacao_aulas__isnull=False)
            | (
                Q(dt_cancelamento__isnull=True)
                & Q(dt_disponibilizacao_aulas__isnull=True)
            )
        )
        .filter(codigo_motivo_disponibilizacao=_CD_MOTIVO_DISPONIBILIZACAO)
        .order_by("dt_disponibilizacao_aulas")
    )

    if aa:
        for atribuicao in aa:
            resultado.append(
                {
                    "codigo_turma": str(atribuicao.codigo_turma_escola),
                    "data_disponibilizacao_aulas": fmt_iso(
                        atribuicao.dt_disponibilizacao_aulas
                    ),
                    "data_atribuicao_aula": fmt_iso(
                        atribuicao.dt_atribuicao_aula
                    ),
                }
            )

    ae = (
        AtribuicaoExterno.objects.filter(
            contrato_externo__pessoa__cpf=codigo_rf,
            codigo_componente_curricular=disciplina_id,
            codigo_turma_escola__in=codigos,
        )
        .filter(
            Q(dt_disponibilizacao__isnull=False)
            | (
                Q(dt_cancelamento__isnull=True)
                & Q(dt_disponibilizacao__isnull=True)
            )
        )
        .filter(
            codigo_motivo_disponibilizacao_externo=(
                _CD_MOTIVO_DISPONIBILIZACAO_EXTERNO_FIM_ANO_LETIVO
            )
        )
        .order_by("dt_disponibilizacao")
    )

    for atribuicao in ae:
        resultado.append(
            {
                "codigo_turma": str(atribuicao.codigo_turma_escola),
                "data_disponibilizacao_aulas": fmt_iso(
                    atribuicao.dt_disponibilizacao
                ),
                "data_atribuicao_aula": fmt_iso(atribuicao.dt_atribuicao),
            }
        )

    return resultado


def atribuicao_periodo(
    codigo_rf: str,
    codigo_turma: int,
    componente_id: int,
    dt_inicio: date,
    dt_fim: date,
) -> bool:
    """Verifica atribuição do professor em período.

    Args:
        codigo_rf: Registro funcional do professor.
        codigo_turma: CodigoEOL da turma.
        componente_id: Código do componente curricular.
        dt_inicio: Data inicial do período consultado.
        dt_fim: Data final do período consultado.

    Returns:
        ``True`` quando existe atribuição sobreposta ao período.
    """
    base = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_componente_curricular=componente_id,
        dt_atribuicao_aula__lte=dt_fim,
    ).filter(_filtro_turma(codigo_turma))
    return bool(
        base.filter(dt_disponibilizacao_aulas__gte=dt_inicio).exists()
        or base.filter(dt_disponibilizacao_aulas__isnull=True).exists()
    )


def professores_atribuidos_turma_disc(
    codigo_turma: int,
    disciplina_id: int,
    data_tick: int | None = None,
) -> list[dict]:
    """Lista professores atribuídos à turma e disciplina.

    Args:
        codigo_turma: CodigoEOL da turma.
        disciplina_id: Código do componente curricular.
        data_tick: Data opcional em ticks usada para validar vigência.

    Returns:
        Lista de professores efetivos e externos atribuídos.

    Raises:
        OverflowError: Quando os ticks informados excedem uma data válida.
    """
    data = ticks_to_date(data_tick) if data_tick else None
    efetivas = (
        AtribuicaoAula.objects.filter(
            codigo_componente_curricular=disciplina_id,
        )
        .filter(_filtro_turma(codigo_turma))
        .select_related("cargo_base__professor")
    )
    if data:
        efetivas = _vigentes_em(efetivas, data)

    resultado = []
    for aa in efetivas:
        prof = aa.cargo_base.professor
        resultado.append(
            {
                "codigo_turma": str(codigo_turma),
                "ano_letivo": None,
                "nome_turma": None,
                "data_inicio_atribuicao": fmt_iso(aa.dt_atribuicao_aula),
                "data_fim_atribuicao": fmt_iso(aa.dt_disponibilizacao_aulas),
                "data_fim_turma": fmt_iso(aa.dt_fim_turma),
                "ano_atribuicao": aa.ano_atribuicao,
                "codigo_rf": prof.codigo_rf,
                "disciplina_id": str(disciplina_id),
                "disciplina_nome": None,
                "disciplinas_agrupadas_ids": None,
                "nome_professor": get_nome(prof),
            }
        )
    externas = AtribuicaoExterno.objects.filter(
        codigo_componente_curricular=disciplina_id,
        codigo_turma_escola=codigo_turma,
    ).select_related("contrato_externo__pessoa")
    if data:
        externas = externas.filter(
            dt_cancelamento__isnull=True,
            dt_atribuicao__lte=data,
        ).filter(
            Q(dt_disponibilizacao__isnull=True)
            | Q(dt_disponibilizacao__gte=data)
        )

    for ae in externas:
        pessoa = ae.contrato_externo.pessoa
        resultado.append(
            {
                "codigo_turma": str(codigo_turma),
                "ano_letivo": None,
                "nome_turma": None,
                "data_inicio_atribuicao": fmt_iso(ae.dt_atribuicao),
                "data_fim_atribuicao": fmt_iso(ae.dt_disponibilizacao),
                "data_fim_turma": fmt_iso(ae.dt_fim_turma),
                "ano_atribuicao": ae.ano_atribuicao,
                "codigo_rf": pessoa.cpf,
                "disciplina_id": str(disciplina_id),
                "disciplina_nome": None,
                "disciplinas_agrupadas_ids": None,
                "nome_professor": get_nome(pessoa),
                "atribuicao_externa": True,
            }
        )
    return resultado


def titular_por_turma_disciplina(
    codigo_turma: int, codigo_componente: int
) -> dict | None:
    """Retorna professor titular por turma e componente.

    Args:
        codigo_turma: CodigoEOL da turma.
        codigo_componente: Código do componente curricular.

    Returns:
        Dados do professor titular encontrado ou ``None``.
    """
    aa = (
        AtribuicaoAula.objects.filter(
            codigo_componente_curricular=codigo_componente,
        )
        .filter(_filtro_turma(codigo_turma))
        .select_related("cargo_base__professor")
        .order_by("-dt_atribuicao_aula")
        .first()
    )
    if not aa:
        return None
    prof = aa.cargo_base.professor
    return {
        "professor_rf": prof.codigo_rf,
        "nome_professor": get_nome(prof),
        "disciplina": None,
        "disciplina_id": str(codigo_componente),
        "disciplinas_id": None,
        "turma_id": codigo_turma,
    }


def titulares_por_turmas(codigos_turmas: list[int]) -> list[dict]:
    """Lista professores titulares por turmas.

    Args:
        codigos_turmas: Lista de códigos EOL das turmas.

    Returns:
        Lista de professores titulares das turmas informadas.
    """
    qs = (
        _vigentes_em(AtribuicaoAula.objects, date.today())
        .select_related("cargo_base__professor")
        .order_by("-dt_atribuicao_aula")
    )
    filtro = Q()
    for codigo_turma in codigos_turmas:
        filtro |= _filtro_turma(codigo_turma)
    qs = qs.filter(filtro) if filtro else qs.none()
    resultado = []
    for aa in qs:
        prof = aa.cargo_base.professor
        comp = (
            str(aa.codigo_componente_curricular)
            if aa.codigo_componente_curricular
            else None
        )
        resultado.append(
            {
                "professor_rf": prof.codigo_rf,
                "nome_professor": get_nome(prof),
                "disciplina": None,
                "disciplina_id": comp,
                "disciplinas_id": comp,
                "turma_id": 0,
            }
        )
    return resultado


def titulares_por_turma_agrupamento(
    codigo_turma: int,
    realiza_agrupamento: bool,
    codigo_rf: str | None = None,
    data_referencia: date | None = None,
) -> list[dict]:
    """Lista titulares por turma com opção de agrupamento.

    Args:
        codigo_turma: CodigoEOL da turma.
        realiza_agrupamento: Indica se deve consultar agrupamentos.
        codigo_rf: Registro funcional opcional do professor.
        data_referencia: Data opcional usada para validar vigência.

    Returns:
        Lista de professores titulares conforme os filtros informados.
    """
    if realiza_agrupamento:
        qs = AgrupamentoAtribuicaoTerritorioSaber.objects.filter(
            codigo_turma=codigo_turma
        )
        if codigo_rf:
            qs = qs.filter(rf_professor=codigo_rf)
        if data_referencia:
            qs = qs.filter(dt_inicio_atribuicao__lte=data_referencia)
        resultado = []
        for ag in qs:
            componentes = (
                [
                    c.strip()
                    for c in ag.codigos_componentes_curriculares.split(",")
                    if c.strip()
                ]
                if ag.codigos_componentes_curriculares
                else [None]
            )
            for comp in componentes:
                resultado.append(
                    {
                        "professor_rf": ag.rf_professor,
                        "nome_professor": None,
                        "disciplina": None,
                        "disciplina_id": None,
                        "disciplinas_id": comp,
                        "turma_id": 0,
                    }
                )
        return resultado

    aa_qs = (
        _vigentes_em(
            AtribuicaoAula.objects,
            data_referencia or date.today(),
        )
        .filter(_filtro_turma(codigo_turma))
        .select_related("cargo_base__professor")
    )
    return [
        {
            "professor_rf": aa.cargo_base.professor.codigo_rf,
            "nome_professor": get_nome(aa.cargo_base.professor),
            "disciplina": None,
            "disciplina_id": None,
            "disciplinas_id": str(aa.codigo_componente_curricular),
            "turma_id": 0,
        }
        for aa in aa_qs
    ]


def titulares_por_ue(
    ue_codigo: str,
    data_referencia: date,
) -> list[dict]:
    """Lista titulares por unidade educacional.

    Args:
        ue_codigo: CodigoEOL da unidade educacional.
        data_referencia: Data usada para validar atribuições.

    Returns:
        Lista de professores titulares da unidade educacional.
    """
    qs = AtribuicaoAula.objects.filter(
        codigo_unidade_educacao=ue_codigo,
        dt_cancelamento__isnull=True,
        dt_atribuicao_aula__lte=data_referencia,
    ).select_related("cargo_base__professor")
    return [
        {
            "professor_rf": aa.cargo_base.professor.codigo_rf,
            "nome_professor": get_nome(aa.cargo_base.professor),
            "disciplina": None,
            "disciplina_id": str(aa.codigo_componente_curricular),
            "disciplinas_id": str(aa.codigo_componente_curricular),
            "turma_id": _codigo_turma(aa) or 0,
        }
        for aa in qs
    ]
