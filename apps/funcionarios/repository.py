"""Queries do domínio Funcionários (EP-25 a EP-39).

Importa models de apps.professores pois compartilham o mesmo banco.
"""

from apps.core.utils import fmt_iso, get_nome
from apps.professores.models import (
    AtribuicaoAula,
    CargoBaseServidor,
    CargoSobrepostoServidor,
    ContratoExterno,
    FuncaoAtividadeCargoServidor,
    LotacaoServidor,
    Pessoa,
    Professor,
    UnidadeEducacional,
)

_GUID_VAZIO = "00000000-0000-0000-0000-000000000000"
MENSAGEM_ERRO_LEGADO = (
    "Houve um comportamento inesperado do sistema. Por favor, contate a SME."
)
MENSAGEM_ERRO_PERFIL_SEM_DRE_RF = (
    "O código da Dre ou código rf/login deve ser informados."
)
_UE_DRE_CACHE: dict[str, str | None] = {}


def perfil_placeholder_invalido(id_perfil: str) -> bool:
    """Indica o GUID vazio que o legado rejeita como perfil inválido."""
    return id_perfil.strip().lower() == _GUID_VAZIO


def _dre_de_ue(ue_codigo: str | None) -> str | None:
    if not ue_codigo:
        return None
    if ue_codigo not in _UE_DRE_CACHE:
        ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
        _UE_DRE_CACHE[ue_codigo] = ue.codigo_dre if ue else None
    return _UE_DRE_CACHE[ue_codigo]


def _func_row(ls: LotacaoServidor) -> dict:
    """Linha padrão EP-25/26 — mesmo formato do legado."""
    return {
        "codigo_rf": ls.cargo_base.professor.codigo_rf,
        "nome_servidor": get_nome(ls.cargo_base.professor),
        "data_inicio": ls.dt_inicio.strftime("%m/%d/%Y 00:00:00") if ls.dt_inicio else None,
        "data_fim": ls.dt_fim.strftime("%m/%d/%Y 00:00:00") if ls.dt_fim else None,
        "cargo": None,
        "cd_tipo_funcao_atividade": 0,
        "esta_afastado": False,
        "funcao_externo": 0,
        "tipo_funcao_externo": 0,
    }


def _lotacoes_ativas():
    return LotacaoServidor.objects.filter(dt_fim__isnull=True)


# ---------------------------------------------------------------------------
# EP-25 — Todos os funcionários de uma UE
# ---------------------------------------------------------------------------

def funcionarios_por_ue(codigo_ue: str) -> list[dict]:
    qs = (
        _lotacoes_ativas()
        .filter(codigo_unidade_educacao=codigo_ue)
        .select_related("cargo_base__professor")
    )
    return [_func_row(ls) for ls in qs]


# ---------------------------------------------------------------------------
# EP-26 — Funcionários de uma UE por cargo específico
# ---------------------------------------------------------------------------

def funcionarios_por_ue_cargo(codigo_ue: str, codigo_cargo: int) -> list[dict]:
    qs = (
        _lotacoes_ativas()
        .filter(
            codigo_unidade_educacao=codigo_ue,
            cargo_base__codigo_cargo=codigo_cargo,
        )
        .select_related("cargo_base__professor")
    )
    return [_func_row(ls) for ls in qs]


# ---------------------------------------------------------------------------
# EP-26-B — Funcionários de uma UE por lista de cargos
# ---------------------------------------------------------------------------

def funcionarios_por_lista_cargos(codigo_ue: str, cargos: list[int]) -> list[dict]:
    qs = (
        _lotacoes_ativas()
        .filter(
            codigo_unidade_educacao=codigo_ue,
            cargo_base__codigo_cargo__in=cargos,
        )
        .select_related("cargo_base__professor")
    )
    return [
        {
            "funcionario_rf": ls.cargo_base.professor.codigo_rf,
            "funcionario_nome": None,
            "cargo_id": ls.cargo_base.codigo_cargo,
        }
        for ls in qs
    ]


# ---------------------------------------------------------------------------
# EP-27 — Funcionários de uma UE por função de atividade
# ---------------------------------------------------------------------------

def funcionarios_por_funcao_atividade(
    codigo_ue: str, codigo_funcao_atividade: int
) -> list[dict]:
    qs = (
        FuncaoAtividadeCargoServidor.objects
        .filter(codigo_unidade_local_servico=codigo_ue)
        .select_related("cargo_base__professor")
    )
    return [
        {
            "codigo_rf": fa.cargo_base.professor.codigo_rf,
            "login": None,
            "nome_servidor": get_nome(fa.cargo_base.professor),
            "cd_cargo": fa.cargo_base.codigo_cargo,
            "codigo_funcao_atividade": codigo_funcao_atividade,
            "funcao_externo": 0,
            "tipo_funcao_externo": 0,
        }
        for fa in qs
    ]


# ---------------------------------------------------------------------------
# EP-27-B — Funcionários de uma UE por lista de funções de atividade
# ---------------------------------------------------------------------------

def funcionarios_por_lista_funcoes_atividade(
    codigo_ue: str, _funcoes: list[int]
) -> list[dict]:
    qs = (
        FuncaoAtividadeCargoServidor.objects
        .filter(codigo_unidade_local_servico=codigo_ue)
        .select_related("cargo_base__professor")
    )
    return [
        {
            "funcionario_rf": fa.cargo_base.professor.codigo_rf,
            "funcionario_nome": None,
            "funcao_atividade_id": _funcoes[0] if _funcoes else 0,
        }
        for fa in qs
    ]


# ---------------------------------------------------------------------------
# EP-28 — Funcionários por função externa
# ---------------------------------------------------------------------------

def funcionarios_por_funcao_externa(
    codigo_ue: str,
    codigo_funcao_externa: int,
) -> list[dict]:
    qs = (
        ContratoExterno.objects
        .filter(
            codigo_unidade_educacao=codigo_ue,
            codigo_tipo_funcao=codigo_funcao_externa,
            dt_cancelamento__isnull=True,
            codigo_motivo_desligamento__isnull=True,
        )
        .select_related("pessoa")
    )
    return [
        {
            "cpf": contrato.pessoa.cpf,
            "nome_servidor": get_nome(contrato.pessoa),
            "codigo_escola": contrato.codigo_unidade_educacao,
            "data_inicio": None,
        }
        for contrato in qs
    ]


# ---------------------------------------------------------------------------
# EP-28-B — Funcionários por lista de funções externas
# ---------------------------------------------------------------------------

def funcionarios_por_lista_funcoes_externas(
    codigo_ue: str,
    funcoes: list[int],
) -> list[dict]:
    if not funcoes:
        return []
    qs = (
        ContratoExterno.objects
        .filter(
            codigo_unidade_educacao=codigo_ue,
            codigo_tipo_funcao__in=funcoes,
            dt_cancelamento__isnull=True,
            codigo_motivo_desligamento__isnull=True,
        )
        .select_related("pessoa")
    )
    return [
        {
            "cpf": contrato.pessoa.cpf,
            "nome_servidor": get_nome(contrato.pessoa),
            "codigo_escola": contrato.codigo_unidade_educacao,
            "data_inicio": None,
        }
        for contrato in qs
    ]


# ---------------------------------------------------------------------------
# EP-29 — Cargos do funcionário por RF (CargoFuncionarioConectaDTO)
# ---------------------------------------------------------------------------

def cargos_funcionario(registro_funcional: str) -> list[dict]:
    qs = (
        CargoBaseServidor.objects
        .filter(professor__codigo_rf=registro_funcional)
        .filter(dt_fim_nomeacao__isnull=True)
        .select_related("professor")
        .prefetch_related("cargos_sobrepostos", "funcoes_atividade", "lotacoes")
    )
    resultado = []
    for cbs in qs:
        prof = cbs.professor
        lotacao = next((l for l in cbs.lotacoes.all() if l.dt_fim is None), None)
        ue_cargo = lotacao.codigo_unidade_educacao if lotacao else None
        dre_cargo = _dre_de_ue(ue_cargo)

        sobreposto = next(iter(cbs.cargos_sobrepostos.all()), None)
        ue_sob = sobreposto.codigo_unidade_local_servico if sobreposto else None
        dre_sob = _dre_de_ue(ue_sob)

        funcao = next(iter(cbs.funcoes_atividade.all()), None)
        ue_func = funcao.codigo_unidade_local_servico if funcao else None
        dre_func = _dre_de_ue(ue_func)

        resultado.append({
            "rf": int(prof.codigo_rf),
            "cpf": prof.cpf,
            "cd_cargo_base": cbs.codigo_cargo,
            "cargo_base": None,
            "cd_dre_cargo_base": dre_cargo,
            "cd_ue_cargo_base": ue_cargo,
            "ue_cargo_base": None,
            "tipo_vinculo_cargo_base": None,
            "data_inicio_cargo_base": fmt_iso(cbs.dt_posse),
            "cd_cargo_sobreposto": sobreposto.codigo_cargo if sobreposto else None,
            "cargo_sobreposto": None,
            "cd_dre_cargo_sobreposto": dre_sob,
            "cd_ue_cargo_sobreposto": ue_sob,
            "ue_cargo_sobreposto": None,
            "tipo_vinculo_cargo_sobreposto": None,
            "data_inicio_cargo_sobreposto": None,
            "cd_funcao_atividade": None,
            "funcao_atividade": None,
            "cd_dre_funcao_atividade": dre_func,
            "cd_ue_funcao_atividade": ue_func,
            "ue_funcao_atividade": None,
            "tipo_vinculo_funcao_atividade": None,
            "data_inicio_funcao_atividade": None,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-30 — Funcionário externo por CPF (DadosFuncionarioExternoDTO — lista)
# ---------------------------------------------------------------------------

def funcionario_externo_por_cpf(cpf: str) -> list[dict] | None:
    qs = (
        ContratoExterno.objects
        .filter(pessoa__cpf=cpf)
        .select_related("pessoa")
    )
    if not qs.exists():
        return None
    resultado = []
    for ce in qs:
        p = ce.pessoa
        resultado.append({
            "nome_pessoa": get_nome(p),
            "nome_pai": None,
            "nome_mae": None,
            "data_nascimento": None,
            "rg": None,
            "cpf": p.cpf,
            "titulo_eleitoral": None,
            "pis_pasep": None,
            "codigo_contrato_externo": ce.codigo_contrato,
            "codigo_ue": ce.codigo_unidade_educacao,
            "nome_ue": None,
            "funcao": None,
            "tipo_funcionario": None,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-31 — Nome e CPF do servidor por RF
# ---------------------------------------------------------------------------

def nome_servidor(registro_funcional: str) -> dict | None:
    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return {"nome": get_nome(prof), "cpf": prof.cpf}


# ---------------------------------------------------------------------------
# EP-32 — Nome do funcionário (legado retorna texto puro)
# ---------------------------------------------------------------------------

def dre_ue_atribuicao(registro_funcional: str) -> str | None:
    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return get_nome(prof)


# ---------------------------------------------------------------------------
# EP-33 — Verificar servidor ativo
# ---------------------------------------------------------------------------

def servidor_ativo(registro_funcional: str) -> bool:
    return CargoBaseServidor.objects.filter(
        professor__codigo_rf=registro_funcional,
        dt_fim_nomeacao__isnull=True,
    ).exists()


# ---------------------------------------------------------------------------
# EP-34 — DRE/UE do funcionário por cargo
# ---------------------------------------------------------------------------

def dre_ue_cargo(registro_funcional: str, codigo_cargo: int) -> list[dict]:
    qs = (
        CargoBaseServidor.objects
        .filter(
            professor__codigo_rf=registro_funcional,
            codigo_cargo=codigo_cargo,
            dt_fim_nomeacao__isnull=True,
        )
        .select_related("professor")
        .prefetch_related("lotacoes")
    )
    resultado = []
    for cbs in qs:
        lotacao = next((l for l in cbs.lotacoes.all() if l.dt_fim is None), None)
        ue_codigo = lotacao.codigo_unidade_educacao if lotacao else None
        dre_codigo = None
        if ue_codigo:
            ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
            dre_codigo = ue.codigo_dre if ue else None
        resultado.append({
            "codigo_rf": cbs.professor.codigo_rf,
            "codigo_dre": dre_codigo,
            "codigo_ue": ue_codigo,
            "cargo": None,
        })
    return resultado


# ---------------------------------------------------------------------------
# EP-35 — Usuários SGP por perfil (aderência parcial)
# ---------------------------------------------------------------------------

def usuarios_sgp_por_perfil(  # NOSONAR
    _id_perfil: str,
    codigo_dre: str | None = None,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
) -> list[dict]:
    qs = LotacaoServidor.objects.filter(dt_fim__isnull=True).select_related(
        "cargo_base__professor"
    )
    if codigo_dre and not codigo_ue:
        ues = UnidadeEducacional.objects.filter(codigo_dre=codigo_dre).values_list("codigo_ue", flat=True)
        qs = qs.filter(codigo_unidade_educacao__in=ues)
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
            "codigo_rf": ls.cargo_base.professor.codigo_rf,
            "nome_servidor": get_nome(ls.cargo_base.professor),
            "codigo_dre": ues_map.get(ls.codigo_unidade_educacao),
            "codigo_ue": ls.codigo_unidade_educacao,
        }
        for ls in lotacoes
    ]


# ---------------------------------------------------------------------------
# EP-36 — Funcionários SGP por DRE/perfil (aderência parcial)
# ---------------------------------------------------------------------------

def funcionarios_sgp_dre(  # NOSONAR
    _id_perfil: str,
    codigo_dre: str,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
    codigo_funcao_atividade: int | None = None,  # NOSONAR
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
    return [
        {
            "codigo_rf": ls.cargo_base.professor.codigo_rf,
            "nome_servidor": get_nome(ls.cargo_base.professor),
            "codigo_dre": codigo_dre,
            "codigo_ue": ls.codigo_unidade_educacao,
        }
        for ls in qs
    ]


# ---------------------------------------------------------------------------
# EP-37 — Acesso à sondagem
# ---------------------------------------------------------------------------

def acesso_sondagem(codigo_rf: str) -> bool:
    return AtribuicaoAula.objects.filter(
        cargo_base__professor__codigo_rf=codigo_rf,
    ).exists()


# ---------------------------------------------------------------------------
# EP-38 — Buscar por lista de RF
# ---------------------------------------------------------------------------

def buscar_por_lista_rf_func(lista: list[str]) -> list[dict]:
    return [
        {"nome": get_nome(p), "codigo_rf": p.codigo_rf}
        for p in Professor.objects.filter(codigo_rf__in=lista)
    ]


# ---------------------------------------------------------------------------
# EP-39 — Buscar por lista de login
# ---------------------------------------------------------------------------

def buscar_por_lista_login(lista: list[str]) -> list[dict]:
    return [
        {
            "login": p.codigo_rf,
            "nome_servidor": get_nome(p),
            "perfil": _GUID_VAZIO,
        }
        for p in Professor.objects.filter(codigo_rf__in=lista)
    ]
