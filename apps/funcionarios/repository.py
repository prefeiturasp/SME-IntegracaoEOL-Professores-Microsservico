"""Queries do domínio de funcionários."""

from typing import Any

from apps.core.utils import fmt_iso, get_nome
from apps.professores.models import (
    AtribuicaoAula,
    CargoBaseServidor,
    ContratoExterno,
    FuncaoAtividadeCargoServidor,
    FuncionarioUnidadeEducacional,
    LotacaoServidor,
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
    """Verifica se o perfil informado é um placeholder inválido."""
    return id_perfil.strip().lower() == _GUID_VAZIO


def _dre_de_ue(ue_codigo: str | None) -> str | None:
    if not ue_codigo:
        return None
    if ue_codigo not in _UE_DRE_CACHE:
        ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
        _UE_DRE_CACHE[ue_codigo] = ue.codigo_dre if ue else None
    return _UE_DRE_CACHE[ue_codigo]


def _nome_funcionario(funcionario: FuncionarioUnidadeEducacional) -> str:
    nome_social = funcionario.nome_social
    if nome_social and nome_social.strip():
        return str(nome_social)
    return str(funcionario.nome)


def _fmt_data_funcionario(valor: Any) -> str | None:
    if valor is None:
        return None
    return str(valor.strftime("%d/%m/%Y 00:00:00"))


def _func_row(funcionario: FuncionarioUnidadeEducacional) -> dict:
    return {
        "codigo_rf": funcionario.codigo_rf,
        "nome": _nome_funcionario(funcionario),
        "data_inicio": _fmt_data_funcionario(funcionario.data_inicio),
        "data_fim": _fmt_data_funcionario(funcionario.data_fim),
        "cargo": funcionario.cargo,
        "codigo_tipo_funcao_atividade": (
            funcionario.codigo_tipo_funcao_atividade or 0
        ),
        "esta_afastado": funcionario.esta_afastado,
        "funcao_externo": funcionario.funcao_externo,
        "tipo_funcao_externo": funcionario.tipo_funcao_externo,
    }


def _lotacoes_ativas() -> Any:
    return LotacaoServidor.objects.filter(dt_fim__isnull=True)


def funcionarios_por_ue(
    codigo_ue: str, filtros: dict[str, Any] | None = None
) -> list[dict]:
    """Lista funcionários ativos de uma unidade educacional."""
    qs = FuncionarioUnidadeEducacional.objects.filter(
        codigo_ue=codigo_ue,
        data_fim__isnull=True,
    )
    filtros = filtros or {}
    if cargos := filtros.get("cargos"):
        qs = qs.filter(codigo_cargo__in=[str(cargo) for cargo in cargos])
    if funcoes_atividades := filtros.get("funcoes_atividades"):
        qs = qs.filter(
            codigo_tipo_funcao_atividade__in=funcoes_atividades
        )
    if funcoes_externas := filtros.get("funcoes_externas"):
        qs = qs.filter(funcao_externo__in=funcoes_externas)
    return sorted(
        (_func_row(funcionario) for funcionario in qs),
        key=lambda item: item["nome"],
    )


def funcionarios_por_ue_cargo(codigo_ue: str, codigo_cargo: int) -> list[dict]:
    """Lista funcionários ativos de uma unidade por cargo."""
    return funcionarios_por_ue(
        codigo_ue,
        filtros={"cargos": [codigo_cargo]},
    )


def funcionarios_por_lista_cargos(
    codigo_ue: str, cargos: list[int]
) -> list[dict]:
    """Lista funcionários de uma unidade por cargos informados."""
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


def funcionarios_por_funcao_atividade(
    codigo_ue: str, codigo_funcao_atividade: int
) -> list[dict]:
    """Lista funcionários de uma unidade por função de atividade."""
    qs = FuncaoAtividadeCargoServidor.objects.filter(
        codigo_unidade_local_servico=codigo_ue
    ).select_related("cargo_base__professor")
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


def funcionarios_por_lista_funcoes_atividade(
    codigo_ue: str, _funcoes: list[int]
) -> list[dict]:
    """Lista funcionários de uma unidade por funções de atividade."""
    qs = FuncaoAtividadeCargoServidor.objects.filter(
        codigo_unidade_local_servico=codigo_ue
    ).select_related("cargo_base__professor")
    return [
        {
            "funcionario_rf": fa.cargo_base.professor.codigo_rf,
            "funcionario_nome": None,
            "funcao_atividade_id": _funcoes[0] if _funcoes else 0,
        }
        for fa in qs
    ]


def funcionarios_por_funcao_externa(
    codigo_ue: str,
    codigo_funcao_externa: int,
) -> list[dict]:
    """Lista funcionários externos de uma unidade por função."""
    qs = ContratoExterno.objects.filter(
        codigo_unidade_educacao=codigo_ue,
        codigo_tipo_funcao=codigo_funcao_externa,
        dt_cancelamento__isnull=True,
        codigo_motivo_desligamento__isnull=True,
    ).select_related("pessoa")
    return [
        {
            "cpf": contrato.pessoa.cpf,
            "nome_servidor": get_nome(contrato.pessoa),
            "codigo_escola": contrato.codigo_unidade_educacao,
            "data_inicio": None,
        }
        for contrato in qs
    ]


def funcionarios_por_lista_funcoes_externas(
    codigo_ue: str,
    funcoes: list[int],
) -> list[dict]:
    """Lista funcionários externos de uma unidade por funções."""
    if not funcoes:
        return []
    qs = ContratoExterno.objects.filter(
        codigo_unidade_educacao=codigo_ue,
        codigo_tipo_funcao__in=funcoes,
        dt_cancelamento__isnull=True,
        codigo_motivo_desligamento__isnull=True,
    ).select_related("pessoa")
    return [
        {
            "cpf": contrato.pessoa.cpf,
            "nome_servidor": get_nome(contrato.pessoa),
            "codigo_escola": contrato.codigo_unidade_educacao,
            "data_inicio": None,
        }
        for contrato in qs
    ]


def cargos_funcionario(registro_funcional: str) -> list[dict]:
    """Lista cargos vinculados ao funcionário."""
    qs = (
        CargoBaseServidor.objects.filter(
            professor__codigo_rf=registro_funcional
        )
        .filter(dt_fim_nomeacao__isnull=True)
        .select_related("professor")
        .prefetch_related(
            "cargos_sobrepostos", "funcoes_atividade", "lotacoes"
        )
    )
    resultado = []
    for cbs in qs:
        prof = cbs.professor
        lotacao = next(
            (item for item in cbs.lotacoes.all() if item.dt_fim is None),
            None,
        )
        ue_cargo = lotacao.codigo_unidade_educacao if lotacao else None
        dre_cargo = _dre_de_ue(ue_cargo)

        sobreposto = next(iter(cbs.cargos_sobrepostos.all()), None)
        ue_sob = (
            sobreposto.codigo_unidade_local_servico if sobreposto else None
        )
        dre_sob = _dre_de_ue(ue_sob)

        funcao = next(iter(cbs.funcoes_atividade.all()), None)
        ue_func = funcao.codigo_unidade_local_servico if funcao else None
        dre_func = _dre_de_ue(ue_func)

        resultado.append(
            {
                "rf": int(prof.codigo_rf),
                "cpf": prof.cpf,
                "cd_cargo_base": cbs.codigo_cargo,
                "cargo_base": None,
                "cd_dre_cargo_base": dre_cargo,
                "cd_ue_cargo_base": ue_cargo,
                "ue_cargo_base": None,
                "tipo_vinculo_cargo_base": None,
                "data_inicio_cargo_base": fmt_iso(cbs.dt_posse),
                "cd_cargo_sobreposto": (
                    sobreposto.codigo_cargo if sobreposto else None
                ),
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
            }
        )
    return resultado


def funcionario_externo_por_cpf(cpf: str) -> list[dict] | None:
    """Retorna dados de funcionário externo por CPF."""
    qs = ContratoExterno.objects.filter(pessoa__cpf=cpf).select_related(
        "pessoa"
    )
    if not qs.exists():
        return None
    resultado = []
    for ce in qs:
        p = ce.pessoa
        resultado.append(
            {
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
            }
        )
    return resultado


def nome_cpf_servidor(registro_funcional: str) -> dict | None:
    """Retorna nome e CPF do servidor."""
    func = FuncionarioUnidadeEducacional.objects.filter(
        codigo_rf=registro_funcional,
        funcao_externo=0,
    ).first()
    if func:
        return {"nome": get_nome(func), "cpf": func.cpf}

    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return {"nome": get_nome(prof), "cpf": prof.cpf}


def nome_servidor(registro_funcional: str) -> str | None:
    """Retorna nome do funcionário."""
    func = FuncionarioUnidadeEducacional.objects.filter(
        codigo_rf=registro_funcional,
        funcao_externo=0,
    ).first()
    if func:
        return get_nome(func)

    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return get_nome(prof)


def servidor_ativo(registro_funcional: str) -> bool:
    """Verifica se o servidor possui cargo ativo."""
    return bool(
        CargoBaseServidor.objects.filter(
            professor__codigo_rf=registro_funcional,
            dt_fim_nomeacao__isnull=True,
        ).exists()
    )


def dre_ue_cargo(registro_funcional: str, codigo_cargo: int) -> list[dict]:
    """Lista DRE e UE do funcionário por cargo."""
    qs = (
        CargoBaseServidor.objects.filter(
            professor__codigo_rf=registro_funcional,
            codigo_cargo=codigo_cargo,
            dt_fim_nomeacao__isnull=True,
        )
        .select_related("professor")
        .prefetch_related("lotacoes")
    )
    resultado = []
    for cbs in qs:
        lotacao = next(
            (item for item in cbs.lotacoes.all() if item.dt_fim is None),
            None,
        )
        ue_codigo = lotacao.codigo_unidade_educacao if lotacao else None
        dre_codigo = None
        if ue_codigo:
            ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
            dre_codigo = ue.codigo_dre if ue else None
        resultado.append(
            {
                "codigo_rf": cbs.professor.codigo_rf,
                "codigo_dre": dre_codigo,
                "codigo_ue": ue_codigo,
                "cargo": None,
            }
        )
    return resultado


def usuarios_sgp_por_perfil(  # NOSONAR
    _id_perfil: str,
    codigo_dre: str | None = None,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
) -> list[dict]:
    """Lista usuários SGP por perfil e filtros opcionais."""
    qs = LotacaoServidor.objects.filter(dt_fim__isnull=True).select_related(
        "cargo_base__professor"
    )
    if codigo_dre and not codigo_ue:
        ues = UnidadeEducacional.objects.filter(
            codigo_dre=codigo_dre
        ).values_list("codigo_ue", flat=True)
        qs = qs.filter(codigo_unidade_educacao__in=ues)
    if codigo_ue:
        qs = qs.filter(codigo_unidade_educacao=codigo_ue)
    if codigo_rf:
        qs = qs.filter(cargo_base__professor__codigo_rf=codigo_rf)
    if nome_servidor_param:
        qs = qs.filter(
            cargo_base__professor__nome__icontains=nome_servidor_param
        )
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


def funcionarios_sgp_dre(  # NOSONAR
    _id_perfil: str,
    codigo_dre: str,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
    codigo_funcao_atividade: int | None = None,  # NOSONAR
) -> list[dict]:
    """Lista funcionários SGP por DRE e filtros opcionais."""
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
        qs = qs.filter(
            cargo_base__professor__nome__icontains=nome_servidor_param
        )
    return [
        {
            "codigo_rf": ls.cargo_base.professor.codigo_rf,
            "nome_servidor": get_nome(ls.cargo_base.professor),
            "codigo_dre": codigo_dre,
            "codigo_ue": ls.codigo_unidade_educacao,
        }
        for ls in qs
    ]


def acesso_sondagem(codigo_rf: str) -> bool:
    """Verifica se o servidor possui acesso à sondagem."""
    return bool(
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
        ).exists()
    )


def buscar_por_lista_rf_func(lista: list[str]) -> list[dict]:
    """Lista funcionários por registros funcionais."""
    return [
        {"nome": get_nome(p), "codigo_rf": p.codigo_rf}
        for p in FuncionarioUnidadeEducacional.objects.filter(
            codigo_rf__in=lista
        ).distinct("codigo_rf")
    ]


def buscar_por_lista_login(lista: list[str]) -> list[dict]:
    """Lista funcionários por logins."""
    return [
        {
            "login": p.codigo_rf,
            "nome_servidor": get_nome(p),
            "perfil": _GUID_VAZIO,
        }
        for p in Professor.objects.filter(codigo_rf__in=lista)
    ]
