"""Queries do domínio Professores (EP-01 a EP-23).

Cada função executa um SELECT no PROFESSORES_DB e retorna o mesmo contrato
que o legado EOL retorna hoje. Sem regras de negócio, sem chamadas externas.
"""

from datetime import date

from django.db.models import Q

from apps.core.utils import fmt_br, fmt_iso, get_nome, ticks_to_date, ticks_to_datetime_str
from apps.professores.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoAula,
    AtribuicaoExterno,
    CargoBaseServidor,
    LotacaoServidor,
    Professor,
    SerieTurmaGrade,
    TurmaEscola,
    UnidadeEducacional,
)


def _filtrar_localizacao(qs, ue_id: str | None, dre_id: str | None):
    if ue_id:
        return qs.filter(codigo_unidade_educacao=ue_id)
    if dre_id:
        ues = UnidadeEducacional.objects.filter(
            codigo_dre=dre_id
        ).values_list("codigo_ue", flat=True)
        return qs.filter(codigo_unidade_educacao__in=ues)
    return qs


def _series_da_turma(codigo_turma: int):
    return SerieTurmaGrade.objects.filter(codigo_turma=codigo_turma).values(
        "codigo_serie_grade"
    )


def _filtro_turma(codigo_turma: int) -> Q:
    return Q(codigo_turma_escola=codigo_turma) | Q(
        codigo_serie_grade__in=_series_da_turma(codigo_turma)
    )


def _serie_turma_map(atribuicoes) -> dict[int, int]:
    codigos = {
        aa.codigo_serie_grade
        for aa in atribuicoes
        if getattr(aa, "codigo_serie_grade", None)
    }
    if not codigos:
        return {}
    return dict(
        SerieTurmaGrade.objects.filter(codigo_serie_grade__in=codigos).values_list(
            "codigo_serie_grade", "codigo_turma"
        )
    )


def _turma_map(codigos_turma) -> dict[int, TurmaEscola]:
    codigos = {codigo for codigo in codigos_turma if codigo}
    if not codigos:
        return {}
    return {
        turma.codigo_turma: turma
        for turma in TurmaEscola.objects.filter(codigo_turma__in=codigos)
    }


def _codigo_turma(atribuicao, serie_map: dict[int, int] | None = None) -> int | None:
    if atribuicao.codigo_turma_escola:
        return atribuicao.codigo_turma_escola
    if not atribuicao.codigo_serie_grade:
        return None
    if serie_map is not None:
        return serie_map.get(atribuicao.codigo_serie_grade)
    serie = SerieTurmaGrade.objects.filter(
        codigo_serie_grade=atribuicao.codigo_serie_grade
    ).first()
    return serie.codigo_turma if serie else None


def _fim_atribuicao_ou_turma(atribuicao, turma: TurmaEscola | None):
    return (
        atribuicao.dt_disponibilizacao_aulas
        or (turma.dt_fim_turma if turma else None)
        or (turma.dt_fim if turma else None)
    )


def _vigentes_em(qs, data_ref: date):
    return qs.filter(dt_cancelamento__isnull=True, dt_atribuicao_aula__lte=data_ref).filter(
        Q(dt_disponibilizacao_aulas__isnull=True)
        | Q(dt_disponibilizacao_aulas__gte=data_ref)
    )


def _turma_row(
    aa: AtribuicaoAula,
    serie_map: dict[int, int] | None = None,
    turmas_map: dict[int, TurmaEscola] | None = None,
) -> dict:
    codigo_turma = _codigo_turma(aa, serie_map)
    turma = (turmas_map or {}).get(codigo_turma)
    return {
        "codigo_turma": codigo_turma,
        "nome_turma": None,
        "componente_curricular": None,
        "data_inicio_atribuicao": fmt_br(aa.dt_atribuicao_aula),
        "data_fim_atribuicao": fmt_br(_fim_atribuicao_ou_turma(aa, turma)),
        "ano": None,
        "etapa_ensino": None,
    }


def _turma_row_externo(ae: AtribuicaoExterno) -> dict:
    return {
        "codigo_turma": None,
        "nome_turma": None,
        "componente_curricular": None,
        "data_inicio_atribuicao": fmt_br(ae.dt_atribuicao),
        "data_fim_atribuicao": fmt_br(ae.dt_disponibilizacao),
        "ano": None,
        "etapa_ensino": None,
    }


# ---------------------------------------------------------------------------
# EP-01 — Professores de uma escola por ano
# ---------------------------------------------------------------------------

def buscar_professores_escola(codigo_ue: str, ano_letivo: int) -> list[dict]:
    qs = (
        _vigentes_em(
            AtribuicaoAula.objects.filter(
                codigo_unidade_educacao=codigo_ue,
                ano_atribuicao=ano_letivo,
            ),
            date.today(),
        )
        .select_related("cargo_base__professor")
    )
    resultado = []
    for aa in qs:
        prof = aa.cargo_base.professor
        resultado.append({
            "codigo_rf": int(prof.codigo_rf),
            "nome": get_nome(prof),
            "cargo": None,
            "cpf": prof.cpf,
            "data_inicio_exercicio": fmt_iso(aa.cargo_base.dt_posse),
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-02 — Turmas do professor por escola e ano
# ---------------------------------------------------------------------------

def buscar_turmas_professor_escola_ano(
    codigo_rf: str, codigo_ue: str, ano_letivo: int
) -> list[dict]:
    efetivas_qs = AtribuicaoAula.objects.filter(
        codigo_unidade_educacao=codigo_ue,
        ano_atribuicao=ano_letivo,
    )
    if codigo_rf:
        efetivas_qs = efetivas_qs.filter(cargo_base__professor__codigo_rf=codigo_rf)
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
        externas_qs = externas_qs.filter(contrato_externo__pessoa__cpf=codigo_rf)
    serie_map = _serie_turma_map(efetivas)
    turmas_map = _turma_map(serie_map.values())
    return [_turma_row(aa, serie_map, turmas_map) for aa in efetivas] + [
        _turma_row_externo(ae) for ae in externas_qs
    ]


# ---------------------------------------------------------------------------
# EP-03 — Todas as turmas do professor (sem filtro — não existe no legado)
# ---------------------------------------------------------------------------

def buscar_turmas_professor(codigo_rf: str) -> list[dict]:
    efetivas = list(
        _vigentes_em(
            AtribuicaoAula.objects.filter(cargo_base__professor__codigo_rf=codigo_rf),
            date.today(),
        )
    )
    externas = AtribuicaoExterno.objects.filter(contrato_externo__pessoa__cpf=codigo_rf)
    serie_map = _serie_turma_map(efetivas)
    turmas_map = _turma_map(serie_map.values())
    return [_turma_row(aa, serie_map, turmas_map) for aa in efetivas] + [
        _turma_row_externo(ae) for ae in externas
    ]


# ---------------------------------------------------------------------------
# EP-04 — Turmas do professor por ano
# ---------------------------------------------------------------------------

def buscar_turmas_professor_ano(codigo_rf: str, ano_letivo: int) -> list[dict]:
    efetivas = list(
        _vigentes_em(
            AtribuicaoAula.objects.filter(
                cargo_base__professor__codigo_rf=codigo_rf,
                ano_atribuicao=ano_letivo,
            ),
            date.today(),
        )
    )
    externas = AtribuicaoExterno.objects.filter(
        contrato_externo__pessoa__cpf=codigo_rf,
        ano_atribuicao=ano_letivo,
    )
    serie_map = _serie_turma_map(efetivas)
    turmas_map = _turma_map(serie_map.values())
    return [_turma_row(aa, serie_map, turmas_map) for aa in efetivas] + [
        _turma_row_externo(ae) for ae in externas
    ]


# ---------------------------------------------------------------------------
# EP-05 — Nome do professor pelo RF (retorna string pura, igual ao legado)
# ---------------------------------------------------------------------------

def obter_nome_rf(rf: str) -> str | None:
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    return get_nome(prof)


# ---------------------------------------------------------------------------
# EP-06 — BuscarPorRf
# ---------------------------------------------------------------------------

def buscar_por_rf_ano(rf: str, ano_letivo: int) -> dict | None:  # NOSONAR
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    return {"codigo_rf": prof.codigo_rf, "nome": get_nome(prof)}


# ---------------------------------------------------------------------------
# EP-07 — BuscarPorRfDreUe
# ---------------------------------------------------------------------------

def buscar_por_rf_dre_ue(rf: str) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    return {"codigo_rf": prof.codigo_rf, "nome": get_nome(prof)}


# ---------------------------------------------------------------------------
# EP-08 — AutoComplete
# ---------------------------------------------------------------------------

def autocomplete_professores(
    ano_letivo: int,
    dre_id: str,
    ue_id: str | None = None,
    nome: str | None = None,
) -> list[dict]:
    qs = (
        AtribuicaoAula.objects
        .filter(ano_atribuicao=ano_letivo)
        .select_related("cargo_base__professor")
    )
    qs = _filtrar_localizacao(qs, ue_id, dre_id)
    if nome:
        qs = qs.filter(cargo_base__professor__nome__icontains=nome)

    seen: set[str] = set()
    resultado: list[dict] = []
    for aa in qs:
        prof = aa.cargo_base.professor
        if prof.codigo_rf not in seen:
            seen.add(prof.codigo_rf)
            resultado.append({"codigo_rf": prof.codigo_rf, "nome_servidor": get_nome(prof)})
        if len(resultado) >= 10:
            break

    externos = (
        AtribuicaoExterno.objects
        .filter(ano_atribuicao=ano_letivo)
        .select_related("contrato_externo__pessoa")
    )
    externos = _filtrar_localizacao(externos, ue_id, dre_id)
    if nome:
        externos = externos.filter(contrato_externo__pessoa__nome__icontains=nome)
    for ae in externos:
        if len(resultado) >= 10:
            break
        pessoa = ae.contrato_externo.pessoa
        if pessoa.cpf not in seen:
            seen.add(pessoa.cpf)
            resultado.append({"codigo_rf": pessoa.cpf, "nome_servidor": get_nome(pessoa)})

    return resultado


# ---------------------------------------------------------------------------
# EP-09 — BuscarPorListaRF
# ---------------------------------------------------------------------------

def buscar_por_lista_rf(ano_letivo: int, lista_rf: list[str]) -> list[dict]:
    rfs = set(
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf__in=lista_rf,
            ano_atribuicao=ano_letivo,
        )
        .values_list("cargo_base__professor__codigo_rf", flat=True)
    )
    return [
        {"codigo_rf": p.codigo_rf, "nome": get_nome(p)}
        for p in Professor.objects.filter(codigo_rf__in=rfs)
    ]


# ---------------------------------------------------------------------------
# EP-10 — Validade
# ---------------------------------------------------------------------------

def verificar_validade(rf: str) -> bool:
    return CargoBaseServidor.objects.filter(
        professor__codigo_rf=rf,
        dt_fim_nomeacao__isnull=True,
    ).exists()


# ---------------------------------------------------------------------------
# EP-11 — EhEmei
# ---------------------------------------------------------------------------

_TIPOS_EMEI = [4, 16, 48, 6]


def eh_emei(codigo_rf: str) -> bool:
    ues_emei = UnidadeEducacional.objects.filter(
        codigo_tipo_escola__in=_TIPOS_EMEI
    ).values_list("codigo_ue", flat=True)
    return AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_unidade_educacao__in=ues_emei,
    ).exists()


# ---------------------------------------------------------------------------
# EP-12 — Status de atribuição na turma
# ---------------------------------------------------------------------------

def atribuicao_status(codigo_rf: str, codigo_turma: int) -> dict:
    turma = TurmaEscola.objects.filter(codigo_turma=codigo_turma).first()
    aa = (
        AtribuicaoAula.objects
        .filter(
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
        "data_disponibilizacao": fmt_iso(_fim_atribuicao_ou_turma(aa, turma)),
        "data_fim_turma": fmt_iso(turma.dt_fim_turma if turma else None),
        "codigo_motivo_disponibilizacao": aa.codigo_motivo_disponibilizacao,
    }


# ---------------------------------------------------------------------------
# EP-13 — Verificar atribuição em data
# ---------------------------------------------------------------------------

def atribuicao_verificar_data(
    codigo_rf: str,
    codigo_turma: int,
    data_consulta: date | None = None,
) -> bool:
    qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
    ).filter(_filtro_turma(codigo_turma))
    if data_consulta:
        qs = _vigentes_em(qs, data_consulta)
    return qs.exists()


# ---------------------------------------------------------------------------
# EP-14 — Verificar atribuição disciplina em data
# ---------------------------------------------------------------------------

def atribuicao_disciplina_data(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_consulta: date | None = None,
    territorio_saber: bool = False,
) -> bool:
    if territorio_saber:
        qs = AgrupamentoAtribuicaoTerritorioSaber.objects.filter(
            rf_professor=codigo_rf,
            codigo_turma=codigo_turma,
        )
        if data_consulta:
            qs = qs.filter(dt_inicio_atribuicao__lte=data_consulta)
        return qs.exists()

    qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_componente_curricular=disciplina_id,
    ).filter(_filtro_turma(codigo_turma))
    if data_consulta:
        qs = _vigentes_em(qs, data_consulta)
    return qs.exists()


# ---------------------------------------------------------------------------
# EP-15 — Verificar atribuição via dataTick
# ---------------------------------------------------------------------------

def atribuicao_disciplina_datatick(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_tick: int | None = None,
) -> bool:
    data = ticks_to_date(data_tick) if data_tick else None
    return atribuicao_disciplina_data(codigo_rf, codigo_turma, disciplina_id, data)


# ---------------------------------------------------------------------------
# EP-16 — Recorrência de datas (campo pode_persistir, igual ao legado)
# ---------------------------------------------------------------------------

def atribuicao_recorrencia_datas(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_ticks: list[int],
) -> list[dict]:
    return [
        {
            "data": ticks_to_datetime_str(tick),
            "pode_persistir": atribuicao_disciplina_data(
                codigo_rf, codigo_turma, disciplina_id, ticks_to_date(tick)
            ),
        }
        for tick in data_ticks
    ]


# ---------------------------------------------------------------------------
# EP-17 — Atribuição em lista de turmas por disciplina
# ---------------------------------------------------------------------------

def atribuicao_turmas_lista(
    codigo_rf: str, disciplina_id: int, codigos_turma: list[int]
) -> list[dict]:
    resultado = []
    for codigo_turma in codigos_turma:
        turma = TurmaEscola.objects.filter(codigo_turma=int(codigo_turma)).first()
        aa = (
            AtribuicaoAula.objects.filter(
                cargo_base__professor__codigo_rf=codigo_rf,
                codigo_componente_curricular=disciplina_id,
            )
            .filter(_filtro_turma(int(codigo_turma)))
            .filter(
                Q(dt_disponibilizacao_aulas__isnull=True)
                | Q(dt_disponibilizacao_aulas__gte=date.today())
            )
            .order_by("-dt_atribuicao_aula")
            .first()
        )
        if aa:
            resultado.append({
                "codigo_turma": str(codigo_turma),
                "data_disponibilizacao_aulas": fmt_iso(
                    _fim_atribuicao_ou_turma(aa, turma)
                ),
                "data_atribuicao_aula": fmt_iso(aa.dt_atribuicao_aula),
            })
        ae = (
            AtribuicaoExterno.objects.filter(
                contrato_externo__pessoa__cpf=codigo_rf,
                codigo_componente_curricular=disciplina_id,
                codigo_serie_grade__in=_series_da_turma(int(codigo_turma)),
            )
            .filter(
                Q(dt_disponibilizacao__isnull=True)
                | Q(dt_disponibilizacao__gte=date.today())
            )
            .order_by("-dt_atribuicao")
            .first()
        )
        if ae:
            resultado.append({
                "codigo_turma": str(codigo_turma),
                "data_disponibilizacao_aulas": fmt_iso(ae.dt_disponibilizacao),
                "data_atribuicao_aula": fmt_iso(ae.dt_atribuicao),
            })
    return resultado


# ---------------------------------------------------------------------------
# EP-18 — Atribuição em período
# ---------------------------------------------------------------------------

def atribuicao_periodo(
    codigo_rf: str,
    codigo_turma: int,
    componente_id: int,
    dt_inicio: date,
    dt_fim: date,
) -> bool:
    base = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_componente_curricular=componente_id,
        dt_atribuicao_aula__lte=dt_fim,
    ).filter(_filtro_turma(codigo_turma))
    return (
        base.filter(dt_disponibilizacao_aulas__gte=dt_inicio).exists()
        or base.filter(dt_disponibilizacao_aulas__isnull=True).exists()
    )


# ---------------------------------------------------------------------------
# EP-19 — Professores atribuídos à turma/disciplina em data
# ---------------------------------------------------------------------------

def professores_atribuidos_turma_disc(
    codigo_turma: int,
    disciplina_id: int,
    data_tick: int | None = None,
) -> list[dict]:
    data = ticks_to_date(data_tick) if data_tick else None
    turma = TurmaEscola.objects.filter(codigo_turma=codigo_turma).first()
    efetivas = (
        AtribuicaoAula.objects
        .filter(
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
        resultado.append({
            "codigo_turma": str(codigo_turma),
            "ano_letivo": None,
            "nome_turma": None,
            "data_inicio_atribuicao": fmt_iso(aa.dt_atribuicao_aula),
            "data_fim_atribuicao": fmt_iso(_fim_atribuicao_ou_turma(aa, turma)),
            "data_fim_turma": fmt_iso(turma.dt_fim_turma if turma else None),
            "ano_atribuicao": aa.ano_atribuicao,
            "codigo_rf": prof.codigo_rf,
            "disciplina_id": str(disciplina_id),
            "disciplina_nome": None,
            "disciplinas_agrupadas_ids": None,
            "nome_professor": get_nome(prof),
        })
    externas = (
        AtribuicaoExterno.objects
        .filter(
            codigo_componente_curricular=disciplina_id,
            codigo_serie_grade__in=_series_da_turma(codigo_turma),
        )
        .select_related("contrato_externo__pessoa")
    )
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
        resultado.append({
            "codigo_turma": str(codigo_turma),
            "ano_letivo": None,
            "nome_turma": None,
            "data_inicio_atribuicao": fmt_iso(ae.dt_atribuicao),
            "data_fim_atribuicao": fmt_iso(ae.dt_disponibilizacao),
            "data_fim_turma": fmt_iso(turma.dt_fim_turma if turma else None),
            "ano_atribuicao": ae.ano_atribuicao,
            "codigo_rf": pessoa.cpf,
            "disciplina_id": str(disciplina_id),
            "disciplina_nome": None,
            "disciplinas_agrupadas_ids": None,
            "nome_professor": get_nome(pessoa),
            "atribuicao_externa": True,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-20 — Titular por turma e disciplina
# ---------------------------------------------------------------------------

def titular_por_turma_disciplina(
    codigo_turma: int, codigo_componente: int
) -> dict | None:
    aa = (
        AtribuicaoAula.objects
        .filter(
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


# ---------------------------------------------------------------------------
# EP-21 — Titulares por lista de turmas (GET ?codigosTurmas=)
# ---------------------------------------------------------------------------

def titulares_por_turmas(codigos_turmas: list[int]) -> list[dict]:
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
        comp = str(aa.codigo_componente_curricular) if aa.codigo_componente_curricular else None
        resultado.append({
            "professor_rf": prof.codigo_rf,
            "nome_professor": get_nome(prof),
            "disciplina": None,
            "disciplina_id": comp,
            "disciplinas_id": comp,
            "turma_id": 0,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-22 — Titulares por turma com agrupamento
# ---------------------------------------------------------------------------

def titulares_por_turma_agrupamento(
    codigo_turma: int,
    realiza_agrupamento: bool,
    codigo_rf: str | None = None,
    data_referencia: date | None = None,
) -> list[dict]:
    if realiza_agrupamento:
        qs = AgrupamentoAtribuicaoTerritorioSaber.objects.filter(codigo_turma=codigo_turma)
        if codigo_rf:
            qs = qs.filter(rf_professor=codigo_rf)
        if data_referencia:
            qs = qs.filter(dt_inicio_atribuicao__lte=data_referencia)
        resultado = []
        for ag in qs:
            componentes = (
                [c.strip() for c in ag.codigos_componentes_curriculares.split(",") if c.strip()]
                if ag.codigos_componentes_curriculares
                else [None]
            )
            for comp in componentes:
                resultado.append({
                    "professor_rf": ag.rf_professor,
                    "nome_professor": None,
                    "disciplina": None,
                    "disciplina_id": None,
                    "disciplinas_id": comp,
                    "turma_id": 0,
                })
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


# ---------------------------------------------------------------------------
# EP-23 — Titulares por UE e data de referência
# ---------------------------------------------------------------------------

def titulares_por_ue(
    ue_codigo: str,
    data_referencia: date,
) -> list[dict]:
    qs = (
        AtribuicaoAula.objects
        .filter(
            codigo_unidade_educacao=ue_codigo,
            dt_cancelamento__isnull=True,
            dt_atribuicao_aula__lte=data_referencia,
        )
        .select_related("cargo_base__professor")
    )
    atribuicoes = list(qs)
    serie_map = _serie_turma_map(atribuicoes)
    return [
        {
            "professor_rf": aa.cargo_base.professor.codigo_rf,
            "nome_professor": get_nome(aa.cargo_base.professor),
            "disciplina": None,
            "disciplina_id": str(aa.codigo_componente_curricular),
            "disciplinas_id": str(aa.codigo_componente_curricular),
            "turma_id": _codigo_turma(aa, serie_map) or 0,
        }
        for aa in atribuicoes
    ]
