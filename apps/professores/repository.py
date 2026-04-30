"""Queries do domínio Professores (EP-01 a EP-23).

Cada função executa um SELECT simples no PROFESSORES_DB e retorna
uma lista de dicts ou um dict. Sem regras de negócio, sem chamadas externas.
Campos não disponíveis no banco são retornados como None.
"""

from datetime import date

from apps.core.utils import get_nome, ticks_to_date
from apps.professores.models import (
    AgrupamentoAtribuicaoTerritorioSaber,
    AtribuicaoAula,
    AtribuicaoExterno,
    CargoBaseServidor,
    ContratoExterno,
    LotacaoServidor,
    Pessoa,
    Professor,
    TurmaEscola,
    UnidadeEducacional,
)


def _filtrar_localizacao(qs, ue_id: str | None, dre_id: str | None):
    """Aplica filtro de UE ou, quando apenas DRE informada, expande para as UEs da DRE."""
    if ue_id:
        return qs.filter(codigo_unidade_educacao=ue_id)
    if dre_id:
        ues = UnidadeEducacional.objects.filter(
            codigo_dre=dre_id
        ).values_list("codigo_ue", flat=True)
        return qs.filter(codigo_unidade_educacao__in=ues)
    return qs


# ---------------------------------------------------------------------------
# EP-01 — Buscar professores de uma escola por ano letivo
# ---------------------------------------------------------------------------

def buscar_professores_escola(codigo_ue: str, ano_letivo: int) -> list[dict]:
    qs = (
        AtribuicaoAula.objects
        .filter(codigo_unidade_educacao=codigo_ue, ano_atribuicao=ano_letivo)
        .select_related("cargo_base__professor")
    )
    resultado = []
    for aa in qs:
        prof = aa.cargo_base.professor
        resultado.append({
            "codigoRf": prof.codigo_rf,
            "nome": get_nome(prof),
            "componenteCurricular": None,
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "cargo": None,
            "cpf": prof.cpf,
            "dataInicioAtribuicao": aa.dt_atribuicao_aula,
            "dataFimAtribuicao": aa.dt_disponibilizacao_aulas,
            "dataInicioExercicio": aa.cargo_base.dt_posse,
            "nomeTurma": None,
            "codigoTurma": aa.codigo_turma_escola,
            "turno": None,
            "tipoTurma": None,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-02 — Turmas atribuídas ao professor por escola e ano
# ---------------------------------------------------------------------------

def buscar_turmas_professor_escola_ano(
    codigo_rf: str, codigo_ue: str, ano_letivo: int
) -> list[dict]:
    efetivas = (
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            codigo_unidade_educacao=codigo_ue,
            ano_atribuicao=ano_letivo,
        )
        .select_related("cargo_base__professor")
    )
    externas = (
        AtribuicaoExterno.objects
        .filter(
            contrato_externo__pessoa__cpf=codigo_rf,
            codigo_unidade_educacao=codigo_ue,
            ano_atribuicao=ano_letivo,
        )
    )
    resultado = []
    for aa in efetivas:
        resultado.append({
            "codigoTurma": aa.codigo_turma_escola,
            "nomeTurma": None,
            "codigoEscola": aa.codigo_unidade_educacao,
            "dataInicioAtribuicao": aa.dt_atribuicao_aula,
            "dataFimAtribuicao": aa.dt_disponibilizacao_aulas,
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "codigoGrade": aa.codigo_grade,
            "codigoSerieGrade": aa.codigo_serie_grade,
            "anoAtribuicao": aa.ano_atribuicao,
        })
    for ae in externas:
        resultado.append({
            "codigoTurma": None,
            "nomeTurma": None,
            "codigoEscola": ae.codigo_unidade_educacao,
            "dataInicioAtribuicao": ae.dt_atribuicao,
            "dataFimAtribuicao": ae.dt_disponibilizacao,
            "codigoComponenteCurricular": ae.codigo_componente_curricular,
            "codigoGrade": ae.codigo_grade,
            "codigoSerieGrade": ae.codigo_serie_grade,
            "anoAtribuicao": ae.ano_atribuicao,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-03 — Todas as turmas atribuídas ao professor (sem filtro de escola/ano)
# ---------------------------------------------------------------------------

def buscar_turmas_professor(codigo_rf: str) -> list[dict]:
    efetivas = (
        AtribuicaoAula.objects
        .filter(cargo_base__professor__codigo_rf=codigo_rf)
        .select_related("cargo_base__professor")
    )
    externas = AtribuicaoExterno.objects.filter(
        contrato_externo__pessoa__cpf=codigo_rf
    )
    resultado = []
    for aa in efetivas:
        resultado.append({
            "codigoTurma": aa.codigo_turma_escola,
            "nomeTurma": None,
            "codigoEscola": aa.codigo_unidade_educacao,
            "dataInicioAtribuicao": aa.dt_atribuicao_aula,
            "dataFimAtribuicao": aa.dt_disponibilizacao_aulas,
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "anoAtribuicao": aa.ano_atribuicao,
        })
    for ae in externas:
        resultado.append({
            "codigoTurma": None,
            "nomeTurma": None,
            "codigoEscola": ae.codigo_unidade_educacao,
            "dataInicioAtribuicao": ae.dt_atribuicao,
            "dataFimAtribuicao": ae.dt_disponibilizacao,
            "codigoComponenteCurricular": ae.codigo_componente_curricular,
            "anoAtribuicao": ae.ano_atribuicao,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-04 — Turmas atribuídas ao professor por ano
# ---------------------------------------------------------------------------

def buscar_turmas_professor_ano(codigo_rf: str, ano_letivo: int) -> list[dict]:
    efetivas = (
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            ano_atribuicao=ano_letivo,
        )
        .select_related("cargo_base__professor")
    )
    externas = AtribuicaoExterno.objects.filter(
        contrato_externo__pessoa__cpf=codigo_rf,
        ano_atribuicao=ano_letivo,
    )
    resultado = []
    for aa in efetivas:
        resultado.append({
            "codigoTurma": aa.codigo_turma_escola,
            "nomeTurma": None,
            "codigoEscola": aa.codigo_unidade_educacao,
            "dataInicioAtribuicao": aa.dt_atribuicao_aula,
            "dataFimAtribuicao": aa.dt_disponibilizacao_aulas,
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "anoAtribuicao": aa.ano_atribuicao,
        })
    for ae in externas:
        resultado.append({
            "codigoTurma": None,
            "nomeTurma": None,
            "codigoEscola": ae.codigo_unidade_educacao,
            "dataInicioAtribuicao": ae.dt_atribuicao,
            "dataFimAtribuicao": ae.dt_disponibilizacao,
            "codigoComponenteCurricular": ae.codigo_componente_curricular,
            "anoAtribuicao": ae.ano_atribuicao,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-05 — Obter nome do professor pelo RF
# ---------------------------------------------------------------------------

def obter_nome_rf(rf: str) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    return {"codigoRf": prof.codigo_rf, "nome": get_nome(prof)}


# ---------------------------------------------------------------------------
# EP-06 — Buscar professor por RF e ano letivo
# ---------------------------------------------------------------------------

def buscar_por_rf_ano(rf: str, ano_letivo: int) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    aa = (
        AtribuicaoAula.objects
        .filter(cargo_base__professor__codigo_rf=rf, ano_atribuicao=ano_letivo)
        .select_related("cargo_base")
        .first()
    )
    lotacao = (
        LotacaoServidor.objects
        .filter(cargo_base__professor__codigo_rf=rf, dt_fim__isnull=True)
        .first()
    )
    return {
        "codigoRf": prof.codigo_rf,
        "nome": get_nome(prof),
        "cpf": prof.cpf,
        "codigoEscola": lotacao.codigo_unidade_educacao if lotacao else None,
        "nomeTurma": None,
        "codigoTurma": aa.codigo_turma_escola if aa else None,
        "cargo": None,
        "dataInicio": aa.dt_atribuicao_aula if aa else None,
        "dataFim": aa.dt_disponibilizacao_aulas if aa else None,
    }


# ---------------------------------------------------------------------------
# EP-07 — Buscar professor por RF, DRE e UE
# ---------------------------------------------------------------------------

def buscar_por_rf_dre_ue(
    rf: str,
    ano_letivo: int,
    dre_id: str | None = None,
    ue_id: str | None = None,
) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=rf).first()
    if not prof:
        return None
    aa_qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=rf, ano_atribuicao=ano_letivo
    )
    aa_qs = _filtrar_localizacao(aa_qs, ue_id, dre_id)
    aa = aa_qs.select_related("cargo_base").first()

    lotacao_qs = LotacaoServidor.objects.filter(
        cargo_base__professor__codigo_rf=rf, dt_fim__isnull=True
    )
    lotacao_qs = _filtrar_localizacao(lotacao_qs, ue_id, dre_id)
    lotacao = lotacao_qs.first()

    return {
        "codigoRf": prof.codigo_rf,
        "nome": get_nome(prof),
        "cpf": prof.cpf,
        "codigoEscola": lotacao.codigo_unidade_educacao if lotacao else None,
        "nomeTurma": None,
        "codigoTurma": aa.codigo_turma_escola if aa else None,
        "cargo": None,
        "dataInicio": aa.dt_atribuicao_aula if aa else None,
        "dataFim": aa.dt_disponibilizacao_aulas if aa else None,
    }


# ---------------------------------------------------------------------------
# EP-08 — AutoComplete de professores por DRE e ano
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
    resultado = []
    for aa in qs:
        prof = aa.cargo_base.professor
        if prof.codigo_rf not in seen:
            seen.add(prof.codigo_rf)
            resultado.append({
                "codigoRf": prof.codigo_rf,
                "nomeServidor": get_nome(prof),
            })
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
        cpf = pessoa.cpf
        if cpf not in seen:
            seen.add(cpf)
            resultado.append({
                "codigoRf": cpf,
                "nomeServidor": get_nome(pessoa),
            })

    return resultado


# ---------------------------------------------------------------------------
# EP-09 — Buscar professores por lista de RF e ano
# ---------------------------------------------------------------------------

def buscar_por_lista_rf(ano_letivo: int, lista_rf: list[str]) -> list[dict]:
    rfs_com_atribuicao = set(
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf__in=lista_rf,
            ano_atribuicao=ano_letivo,
        )
        .values_list("cargo_base__professor__codigo_rf", flat=True)
    )
    professores = Professor.objects.filter(codigo_rf__in=rfs_com_atribuicao)
    return [
        {"codigoRf": p.codigo_rf, "nome": get_nome(p), "cpf": p.cpf}
        for p in professores
    ]


# ---------------------------------------------------------------------------
# EP-10 — Verificar validade do professor
# ---------------------------------------------------------------------------

def verificar_validade(rf: str) -> bool:
    return CargoBaseServidor.objects.filter(
        professor__codigo_rf=rf, situacao_funcional=6
    ).exists()


# ---------------------------------------------------------------------------
# EP-11 — Verificar se professor é EMEI
# ---------------------------------------------------------------------------

# Tipos de escola EMEI na rede municipal (confirmar com DBA se necessário)
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
    possui = (
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            codigo_turma_escola=codigo_turma,
        ).exists()
        or AtribuicaoExterno.objects.filter(
            contrato_externo__pessoa__cpf=codigo_rf,
            codigo_turma_escola_grade_programa__in=(
                AtribuicaoAula.objects
                .filter(codigo_turma_escola=codigo_turma)
                .values_list("codigo_turma_escola_grade_programa", flat=True)
            ),
        ).exists()
    )
    return {
        "possuiAtribuicao": possui,
        "codigoRf": codigo_rf,
        "codigoTurma": codigo_turma,
    }


# ---------------------------------------------------------------------------
# EP-13 — Verificar atribuição na turma em uma data
# ---------------------------------------------------------------------------

def atribuicao_verificar_data(
    codigo_rf: str,
    codigo_turma: int,
    data_consulta: date | None = None,
) -> bool:
    qs = AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_turma_escola=codigo_turma,
    )
    if data_consulta:
        qs = qs.filter(dt_atribuicao_aula__lte=data_consulta)
    return qs.exists()


# ---------------------------------------------------------------------------
# EP-14 — Verificar atribuição na disciplina/turma em uma data
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
        codigo_turma_escola=codigo_turma,
        codigo_componente_curricular=disciplina_id,
    )
    if data_consulta:
        qs = qs.filter(dt_atribuicao_aula__lte=data_consulta)
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
# EP-16 — Verificar atribuição em recorrência de datas
# ---------------------------------------------------------------------------

def atribuicao_recorrencia_datas(
    codigo_rf: str,
    codigo_turma: int,
    disciplina_id: int,
    data_ticks: list[int],
) -> list[dict]:
    return [
        {
            "data": ticks_to_date(tick),
            "possuiAtribuicao": atribuicao_disciplina_data(
                codigo_rf, codigo_turma, disciplina_id, ticks_to_date(tick)
            ),
        }
        for tick in data_ticks
    ]


# ---------------------------------------------------------------------------
# EP-17 — Verificar atribuição em lista de turmas por disciplina (POST)
# ---------------------------------------------------------------------------

def atribuicao_turmas_lista(
    codigo_rf: str, disciplina_id: int, codigos_turma: list[int]
) -> list[dict]:
    turmas_com_atribuicao = set(
        AtribuicaoAula.objects
        .filter(
            cargo_base__professor__codigo_rf=codigo_rf,
            codigo_componente_curricular=disciplina_id,
            codigo_turma_escola__in=codigos_turma,
        )
        .values_list("codigo_turma_escola", flat=True)
    )
    return [
        {
            "codigoTurma": turma,
            "possuiAtribuicao": turma in turmas_com_atribuicao,
        }
        for turma in codigos_turma
    ]


# ---------------------------------------------------------------------------
# EP-18 — Atribuição do professor em período (POST)
# ---------------------------------------------------------------------------

def atribuicao_periodo(
    codigo_rf: str,
    codigo_turma: int,
    componente_id: int,
    dt_inicio: date,
    dt_fim: date,
) -> bool:
    return AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_turma_escola=codigo_turma,
        codigo_componente_curricular=componente_id,
        dt_atribuicao_aula__lte=dt_fim,
    ).filter(
        dt_disponibilizacao_aulas__gte=dt_inicio
    ).exists() or AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
        codigo_turma_escola=codigo_turma,
        codigo_componente_curricular=componente_id,
        dt_atribuicao_aula__lte=dt_fim,
        dt_disponibilizacao_aulas__isnull=True,
    ).exists()


# ---------------------------------------------------------------------------
# EP-19 — Professores atribuídos a turma/disciplina em data
# ---------------------------------------------------------------------------

def professores_atribuidos_turma_disc(
    codigo_turma: int,
    disciplina_id: int,
    data_tick: int | None = None,
) -> list[dict]:
    data = ticks_to_date(data_tick) if data_tick else None
    efetivas = AtribuicaoAula.objects.filter(
        codigo_turma_escola=codigo_turma,
        codigo_componente_curricular=disciplina_id,
    ).select_related("cargo_base__professor")
    if data:
        efetivas = efetivas.filter(dt_atribuicao_aula__lte=data)

    externas = AtribuicaoExterno.objects.filter(
        codigo_componente_curricular=disciplina_id,
    ).select_related("contrato_externo__pessoa")
    if data:
        externas = externas.filter(dt_atribuicao__lte=data)

    resultado = []
    for aa in efetivas:
        prof = aa.cargo_base.professor
        resultado.append({
            "codigoRf": prof.codigo_rf,
            "nome": get_nome(prof),
            "cpf": prof.cpf,
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "dataAtribuicao": aa.dt_atribuicao_aula,
            "dataDisponibilizacao": aa.dt_disponibilizacao_aulas,
            "atribuicaoExterna": False,
        })
    for ae in externas:
        pessoa = ae.contrato_externo.pessoa
        resultado.append({
            "codigoRf": pessoa.cpf,
            "nome": get_nome(pessoa),
            "cpf": pessoa.cpf,
            "codigoComponenteCurricular": ae.codigo_componente_curricular,
            "dataAtribuicao": ae.dt_atribuicao,
            "dataDisponibilizacao": ae.dt_disponibilizacao,
            "atribuicaoExterna": True,
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
            codigo_turma_escola=codigo_turma,
            codigo_componente_curricular=codigo_componente,
        )
        .select_related("cargo_base__professor")
        .order_by("-dt_atribuicao_aula")
        .first()
    )
    if not aa:
        return None
    prof = aa.cargo_base.professor
    return {"codigoRf": prof.codigo_rf, "nome": get_nome(prof), "cpf": prof.cpf}


# ---------------------------------------------------------------------------
# EP-21 — Titulares por lista de turmas
# ---------------------------------------------------------------------------

def titulares_por_turmas(codigos_turmas: list[int]) -> list[dict]:
    qs = (
        AtribuicaoAula.objects
        .filter(codigo_turma_escola__in=codigos_turmas)
        .select_related("cargo_base__professor")
        .order_by("codigo_turma_escola", "-dt_atribuicao_aula")
    )
    seen: set[int] = set()
    resultado = []
    for aa in qs:
        if aa.codigo_turma_escola not in seen:
            seen.add(aa.codigo_turma_escola)
            prof = aa.cargo_base.professor
            resultado.append({
                "codigoTurma": aa.codigo_turma_escola,
                "codigoRf": prof.codigo_rf,
                "nome": get_nome(prof),
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
                [int(c.strip()) for c in ag.codigos_componentes_curriculares.split(",") if c.strip()]
                if ag.codigos_componentes_curriculares
                else [None]
            )
            for comp in componentes:
                resultado.append({
                    "codigoRf": ag.rf_professor,
                    "nome": None,
                    "codigoComponenteCurricular": comp,
                    "codigoTerritorioSaber": ag.codigo_territorio_saber,
                    "codigoExperienciaPedagogica": ag.codigo_experiencia_pedagogica,
                })
        return resultado

    aa_qs = AtribuicaoAula.objects.filter(
        codigo_turma_escola=codigo_turma,
    ).select_related("cargo_base__professor")
    if codigo_rf:
        aa_qs = aa_qs.filter(cargo_base__professor__codigo_rf=codigo_rf)
    if data_referencia:
        aa_qs = aa_qs.filter(dt_atribuicao_aula__lte=data_referencia)
    return [
        {
            "codigoRf": aa.cargo_base.professor.codigo_rf,
            "nome": get_nome(aa.cargo_base.professor),
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "codigoTerritorioSaber": None,
            "codigoExperienciaPedagogica": None,
        }
        for aa in aa_qs
    ]


# ---------------------------------------------------------------------------
# EP-23 — Titulares por UE e data de referência
# ---------------------------------------------------------------------------

def titulares_por_ue(
    ue_codigo: str,
    data_referencia: date,
    realiza_agrupamento: bool = False,  # NOSONAR — agrupamento por UE não implementado; reservado para compatibilidade com a view
) -> list[dict]:
    qs = AtribuicaoAula.objects.filter(
        codigo_unidade_educacao=ue_codigo,
        dt_atribuicao_aula__lte=data_referencia,
    ).select_related("cargo_base__professor")
    return [
        {
            "codigoRf": aa.cargo_base.professor.codigo_rf,
            "nome": get_nome(aa.cargo_base.professor),
            "codigoComponenteCurricular": aa.codigo_componente_curricular,
            "codigoTerritorioSaber": None,
            "codigoExperienciaPedagogica": None,
        }
        for aa in qs
    ]
