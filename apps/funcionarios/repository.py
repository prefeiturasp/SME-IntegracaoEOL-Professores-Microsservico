"""Queries do domínio Funcionários (EP-25 a EP-39).

Importa models de apps.professores pois compartilham o mesmo banco.
"""

from apps.core.utils import get_nome
from apps.professores.models import (
    AtribuicaoAula,
    CargoBaseServidor,
    ContratoExterno,
    FuncaoAtividadeCargoServidor,
    LotacaoServidor,
    Pessoa,
    Professor,
    UnidadeEducacional,
)


# ---------------------------------------------------------------------------
# EP-25 — Funcionários de uma UE (sem filtro de cargo)
# ---------------------------------------------------------------------------

def funcionarios_por_ue(codigo_ue: str) -> list[dict]:
    qs = (
        LotacaoServidor.objects
        .filter(codigo_unidade_educacao=codigo_ue)
        .select_related("cargo_base__professor")
    )
    return [
        {
            "codigoRf": ls.cargo_base.professor.codigo_rf,
            "nomeServidor": get_nome(ls.cargo_base.professor),
            "cargo": None,
            "dataInicio": ls.dt_inicio,
            "dataFim": ls.dt_fim,
        }
        for ls in qs
    ]


# ---------------------------------------------------------------------------
# EP-26 — Funcionários de uma UE por cargo específico
# ---------------------------------------------------------------------------

def funcionarios_por_ue_cargo(codigo_ue: str, codigo_cargo: int) -> list[dict]:
    qs = (
        LotacaoServidor.objects
        .filter(
            codigo_unidade_educacao=codigo_ue,
            cargo_base__codigo_cargo=codigo_cargo,
        )
        .select_related("cargo_base__professor")
    )
    return [
        {
            "codigoRf": ls.cargo_base.professor.codigo_rf,
            "nomeServidor": get_nome(ls.cargo_base.professor),
            "cargo": None,
            "dataInicio": ls.dt_inicio,
            "dataFim": ls.dt_fim,
        }
        for ls in qs
    ]


# ---------------------------------------------------------------------------
# EP-26-B — Funcionários de uma UE por lista de cargos (query param)
# ---------------------------------------------------------------------------

def funcionarios_por_lista_cargos(
    codigo_ue: str, cargos: list[int]
) -> list[dict]:
    qs = (
        LotacaoServidor.objects
        .filter(
            codigo_unidade_educacao=codigo_ue,
            cargo_base__codigo_cargo__in=cargos,
        )
        .select_related("cargo_base__professor")
    )
    return [
        {
            "codigoRf": ls.cargo_base.professor.codigo_rf,
            "nomeServidor": get_nome(ls.cargo_base.professor),
            "cargo": None,
            "dataInicio": ls.dt_inicio,
            "dataFim": ls.dt_fim,
        }
        for ls in qs
    ]


# ---------------------------------------------------------------------------
# EP-27 — Funcionários de uma UE por função de atividade
# ---------------------------------------------------------------------------

def funcionarios_por_funcao_atividade(
    codigo_ue: str, codigo_funcao_atividade: int
) -> list[dict]:
    # Filtra por UE; o campo codigo_funcao_atividade não existe no model ETL
    # (coluna ausente na sincronização). Retorna todos com funcao_atividade na UE.
    qs = (
        FuncaoAtividadeCargoServidor.objects
        .filter(codigo_unidade_local_servico=codigo_ue)
        .select_related("cargo_base__professor")
    )
    return [
        {
            "codigoRf": fa.cargo_base.professor.codigo_rf,
            "nomeServidor": get_nome(fa.cargo_base.professor),
            "cargo": None,
            "dataInicio": None,
            "dataFim": fa.dt_fim_funcao_atividade,
        }
        for fa in qs
    ]


# ---------------------------------------------------------------------------
# EP-27-B — Funcionários de uma UE por lista de funções de atividade
# ---------------------------------------------------------------------------

def funcionarios_por_lista_funcoes_atividade(
    codigo_ue: str, _funcoes: list[int]
) -> list[dict]:
    return funcionarios_por_funcao_atividade(codigo_ue, 0)


# ---------------------------------------------------------------------------
# EP-28 — Funcionários de uma UE por função externa
# ---------------------------------------------------------------------------

def funcionarios_por_funcao_externa(
    codigo_ue: str, codigo_funcao_externa: int
) -> list[dict]:
    qs = (
        ContratoExterno.objects
        .filter(
            codigo_unidade_educacao=codigo_ue,
            codigo_tipo_funcao=codigo_funcao_externa,
        )
        .select_related("pessoa")
    )
    return [
        {
            "cpf": ce.pessoa.cpf,
            "nomeServidor": get_nome(ce.pessoa),
            "codigoEscola": ce.codigo_unidade_educacao,
            "dataInicio": None,
        }
        for ce in qs
    ]


# ---------------------------------------------------------------------------
# EP-28-B — Funcionários de uma UE por lista de funções externas
# ---------------------------------------------------------------------------

def funcionarios_por_lista_funcoes_externas(
    codigo_ue: str, funcoes: list[int]
) -> list[dict]:
    qs = (
        ContratoExterno.objects
        .filter(
            codigo_unidade_educacao=codigo_ue,
            codigo_tipo_funcao__in=funcoes,
        )
        .select_related("pessoa")
    )
    return [
        {
            "cpf": ce.pessoa.cpf,
            "nomeServidor": get_nome(ce.pessoa),
            "codigoEscola": ce.codigo_unidade_educacao,
            "dataInicio": None,
        }
        for ce in qs
    ]


# ---------------------------------------------------------------------------
# EP-29 — Cargos do funcionário por RF
# ---------------------------------------------------------------------------

def cargos_funcionario(registro_funcional: str) -> list[dict]:
    qs = (
        CargoBaseServidor.objects
        .filter(professor__codigo_rf=registro_funcional)
        .select_related("professor")
    )
    return [
        {
            "codigoRf": cbs.professor.codigo_rf,
            "nomeServidor": get_nome(cbs.professor),
            "dataInicio": cbs.dt_posse,
            "dataFim": cbs.dt_fim_nomeacao,
            "cargo": None,
        }
        for cbs in qs
    ]


# ---------------------------------------------------------------------------
# EP-30 — Funcionário externo por CPF
# ---------------------------------------------------------------------------

def funcionario_externo_por_cpf(cpf: str) -> dict | None:
    ce = (
        ContratoExterno.objects
        .filter(pessoa__cpf=cpf)
        .select_related("pessoa")
        .first()
    )
    if not ce:
        return None
    return {
        "cpf": ce.pessoa.cpf,
        "nome": get_nome(ce.pessoa),
        "codigoUe": ce.codigo_unidade_educacao,
        "codigoTipoFuncao": ce.codigo_tipo_funcao,
    }


# ---------------------------------------------------------------------------
# EP-31 — Nome e CPF do servidor por RF
# ---------------------------------------------------------------------------

def nome_servidor(registro_funcional: str) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return {
        "codigoRf": prof.codigo_rf,
        "nome": get_nome(prof),
        "cpf": prof.cpf,
    }


# ---------------------------------------------------------------------------
# EP-32 — DRE/UE de atribuição do funcionário (nome-usuario-eol)
# ---------------------------------------------------------------------------

def dre_ue_atribuicao(registro_funcional: str) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    lotacao = (
        LotacaoServidor.objects
        .filter(cargo_base__professor__codigo_rf=registro_funcional, dt_fim__isnull=True)
        .select_related("cargo_base__professor")
        .first()
    )
    ue_codigo = lotacao.codigo_unidade_educacao if lotacao else None
    dre_codigo = None
    if ue_codigo:
        ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
        dre_codigo = ue.codigo_dre if ue else None
    return {
        "codigoRf": prof.codigo_rf,
        "nome": get_nome(prof),
        "codigoDre": dre_codigo,
        "codigoUe": ue_codigo,
    }


# ---------------------------------------------------------------------------
# EP-33 — Verificar servidor ativo
# ---------------------------------------------------------------------------

def servidor_ativo(registro_funcional: str) -> bool:
    return CargoBaseServidor.objects.filter(
        professor__codigo_rf=registro_funcional,
        dt_fim_nomeacao__isnull=True,
    ).exists()


# ---------------------------------------------------------------------------
# EP-34 — DRE/UE do funcionário por cargo específico
# ---------------------------------------------------------------------------

def dre_ue_cargo(registro_funcional: str, codigo_cargo: int) -> dict | None:
    cbs = (
        CargoBaseServidor.objects
        .filter(
            professor__codigo_rf=registro_funcional,
            codigo_cargo=codigo_cargo,
        )
        .select_related("professor")
        .first()
    )
    if not cbs:
        return None
    lotacao = LotacaoServidor.objects.filter(cargo_base=cbs, dt_fim__isnull=True).first()
    ue_codigo = lotacao.codigo_unidade_educacao if lotacao else None
    dre_codigo = None
    if ue_codigo:
        ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
        dre_codigo = ue.codigo_dre if ue else None
    return {
        "codigoRf": cbs.professor.codigo_rf,
        "codigoDre": dre_codigo,
        "codigoUe": ue_codigo,
        "cargo": None,
    }


# ---------------------------------------------------------------------------
# EP-35 — Usuários SGP por perfil
# ---------------------------------------------------------------------------

def usuarios_sgp_por_perfil(
    _id_perfil: str,
    codigo_dre: str | None = None,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
) -> list[dict]:
    # Mapeamento de perfil SGP não está no PROFESSORES_DB.
    # Retorna professores com lotação ativa, aplicando filtros disponíveis.
    qs = LotacaoServidor.objects.filter(dt_fim__isnull=True).select_related(
        "cargo_base__professor"
    )
    if codigo_dre and not codigo_ue:
        ues_da_dre = UnidadeEducacional.objects.filter(
            codigo_dre=codigo_dre
        ).values_list("codigo_ue", flat=True)
        qs = qs.filter(codigo_unidade_educacao__in=ues_da_dre)
    if codigo_ue:
        qs = qs.filter(codigo_unidade_educacao=codigo_ue)
    if codigo_rf:
        qs = qs.filter(cargo_base__professor__codigo_rf=codigo_rf)
    if nome_servidor_param:
        qs = qs.filter(cargo_base__professor__nome__icontains=nome_servidor_param)
    lotacoes = list(qs)
    ues_map = {
        ue.codigo_ue: ue.codigo_dre
        for ue in UnidadeEducacional.objects.filter(
            codigo_ue__in={ls.codigo_unidade_educacao for ls in lotacoes}
        )
    }
    return [
        {
            "codigoRf": ls.cargo_base.professor.codigo_rf,
            "nomeServidor": get_nome(ls.cargo_base.professor),
            "codigoDre": ues_map.get(ls.codigo_unidade_educacao),
            "codigoUe": ls.codigo_unidade_educacao,
        }
        for ls in lotacoes
    ]


# ---------------------------------------------------------------------------
# EP-36 — Funcionários SGP por DRE/perfil
# ---------------------------------------------------------------------------

def funcionarios_sgp_dre(
    _id_perfil: str,
    codigo_dre: str,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
    codigo_funcao_atividade: int | None = None,  # NOSONAR — campo ausente no model ETL
) -> list[dict]:
    ues_dre = UnidadeEducacional.objects.filter(
        codigo_dre=codigo_dre
    ).values_list("codigo_ue", flat=True)
    qs = LotacaoServidor.objects.filter(
        codigo_unidade_educacao__in=ues_dre,
        dt_fim__isnull=True,
    ).select_related("cargo_base__professor")
    if codigo_ue:
        qs = qs.filter(codigo_unidade_educacao=codigo_ue)
    if codigo_rf:
        qs = qs.filter(cargo_base__professor__codigo_rf=codigo_rf)
    if nome_servidor_param:
        qs = qs.filter(cargo_base__professor__nome__icontains=nome_servidor_param)
    resultado = []
    for ls in qs:
        prof = ls.cargo_base.professor
        resultado.append({
            "codigoRf": prof.codigo_rf,
            "nomeServidor": get_nome(prof),
            "codigoDre": codigo_dre,
            "codigoUe": ls.codigo_unidade_educacao,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-37 — Verificar acesso à sondagem
# ---------------------------------------------------------------------------

def acesso_sondagem(codigo_rf: str) -> bool:
    return AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
    ).exists()


# ---------------------------------------------------------------------------
# EP-38 — Resumo de funcionários por lista de RF
# ---------------------------------------------------------------------------

def buscar_por_lista_rf_func(lista: list[str]) -> list[dict]:
    professores = Professor.objects.filter(codigo_rf__in=lista)
    resultado = [
        {"codigoRf": p.codigo_rf, "nome": get_nome(p), "cpf": p.cpf}
        for p in professores
    ]
    cpfs_nao_encontrados = set(lista) - {p.codigo_rf for p in professores}
    pessoas = Pessoa.objects.filter(cpf__in=cpfs_nao_encontrados)
    resultado += [
        {"codigoRf": p.cpf, "nome": get_nome(p), "cpf": p.cpf}
        for p in pessoas
    ]
    return resultado


# ---------------------------------------------------------------------------
# EP-39 — Resumo de funcionários por lista de login
# ---------------------------------------------------------------------------

def buscar_por_lista_login(lista: list[str]) -> list[dict]:
    professores = Professor.objects.filter(codigo_rf__in=lista)
    return [
        {"codigoRf": p.codigo_rf, "nome": get_nome(p), "cpf": p.cpf}
        for p in professores
    ]
