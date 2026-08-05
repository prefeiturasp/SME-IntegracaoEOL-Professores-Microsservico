"""Queries do domínio de funcionários."""

from typing import Any

from django.db.models import Case, F, IntegerField, Q, Value, When, Window
from django.db.models.functions import RowNumber
from django.utils import timezone

from apps.core.utils import fmt_iso, get_nome
from apps.professores.models import (
    AtribuicaoAula,
    CargoBaseServidor,
    ContratoExterno,
    FuncaoAtividadeCargoServidor,
    FuncionarioCargo,
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
_CODIGO_CARGO_SUPERVISOR = 3352
_ChaveFuncionarioExterno = tuple[int | None, str]


def perfil_placeholder_invalido(id_perfil: str) -> bool:
    """Verifica se o perfil informado é um placeholder inválido.

    Args:
        id_perfil: Identificador do perfil a validar.

    Returns:
        ``True`` quando o perfil corresponde ao GUID vazio.
    """
    return id_perfil.strip().lower() == _GUID_VAZIO


def _dre_de_ue(ue_codigo: str | None) -> str | None:
    """Obtém a DRE vinculada a uma unidade educacional.

    Args:
        ue_codigo: Código EOL da unidade educacional consultada.

    Returns:
        Código EOL da DRE vinculada à UE, ou ``None`` quando não encontrada.
    """
    if not ue_codigo:
        return None
    if ue_codigo not in _UE_DRE_CACHE:
        ue = UnidadeEducacional.objects.filter(codigo_ue=ue_codigo).first()
        _UE_DRE_CACHE[ue_codigo] = ue.codigo_dre if ue else None
    return _UE_DRE_CACHE[ue_codigo]


def _nome_funcionario(funcionario: FuncionarioUnidadeEducacional) -> str:
    """Obtém o nome exibido do funcionário.

    Args:
        funcionario: Funcionário usado para extração do nome.

    Returns:
        Nome social quando preenchido; caso contrário, nome civil.
    """
    nome_social = funcionario.nome_social
    if nome_social and nome_social.strip():
        return str(nome_social)
    return str(funcionario.nome)


def _fmt_data_funcionario(valor: Any) -> str | None:
    """Formata data no contrato legado de funcionários.

    Args:
        valor: Data a ser formatada.

    Returns:
        Data no formato legado, ou ``None`` quando ausente.
    """
    if valor is None:
        return None
    return str(valor.strftime("%m/%d/%Y 00:00:00"))


def _func_row(
    funcionario: FuncionarioUnidadeEducacional,
    usar_nome_social: bool = True,
) -> dict:
    """Monta a representação de funcionário da UE.

    Args:
        funcionario: Funcionário usado para montar os dados.
        usar_nome_social: Indica se o nome social deve ter prioridade.

    Returns:
        Dicionário no formato de funcionários da UE.
    """
    return {
        "codigo_rf": funcionario.codigo_rf,
        "nome": (
            _nome_funcionario(funcionario)
            if usar_nome_social
            else str(funcionario.nome)
        ),
        "cpf": funcionario.cpf,
        "data_inicio": _fmt_data_funcionario(funcionario.data_inicio),
        "data_fim": _fmt_data_funcionario(funcionario.data_fim),
        "cargo": funcionario.cargo or "",
        "codigo_cargo": funcionario.codigo_cargo,
        "codigo_tipo_funcao_atividade": (
            funcionario.codigo_tipo_funcao_atividade or 0
        ),
        "esta_afastado": funcionario.esta_afastado,
        "funcao_externo": funcionario.funcao_externo,
        "tipo_funcao_externo": funcionario.tipo_funcao_externo,
    }


def _usuario_sgp_row(
    funcionario: FuncionarioUnidadeEducacional,
    codigo_dre: str | None = None,
    codigo_funcao_atividade: int | None = None,
) -> dict:
    """Monta funcionário SGP a partir do vínculo consolidado.

    Args:
        funcionario: Funcionário usado para montar os dados.
        codigo_dre: DRE usada na consulta.
        codigo_funcao_atividade: Função usada quando encontrada no conjunto.

    Returns:
        Dicionário de funcionário SGP.
    """
    if codigo_funcao_atividade is None:
        codigo_funcao_atividade = 0
        if funcionario.origem_vinculo == "funcao_atividade":
            codigo_funcao_atividade = (
                funcionario.codigo_tipo_funcao_atividade or 0
            )
    return {
        "codigo_rf": funcionario.codigo_rf,
        "login": funcionario.codigo_rf,
        "nome_servidor": str(funcionario.nome),
        "codigo_dre": codigo_dre or funcionario.codigo_dre,
        "codigo_ue": funcionario.codigo_ue,
        "cd_cargo": funcionario.codigo_cargo,
        "codigo_funcao_atividade": codigo_funcao_atividade,
        "funcao_externo": funcionario.funcao_externo or 0,
        "tipo_funcao_externo": funcionario.tipo_funcao_externo or 0,
    }


def _funcionarios_sgp_por_dre_qs(
    codigo_dre: str,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor_param: str | None = None,
    busca_por_prefixo_ue: bool = False,
) -> Any:
    """Filtra vínculos consolidados por DRE.

    Args:
        codigo_dre: Código EOL da DRE usada no filtro.
        codigo_ue: Código EOL da unidade usada no filtro.
        codigo_rf: RF usado no filtro.
        nome_servidor_param: Trecho do nome usado no filtro.
        busca_por_prefixo_ue: Indica busca por unidades do agrupamento da DRE.

    Returns:
        Vínculos compatíveis com os filtros.
    """
    qs = FuncionarioUnidadeEducacional.objects.all()
    if codigo_ue:
        qs = qs.filter(codigo_ue=codigo_ue)
    elif busca_por_prefixo_ue:
        qs = qs.filter(codigo_ue__startswith=codigo_dre[:4])
    else:
        qs = qs.filter(codigo_dre=codigo_dre)

    if codigo_rf:
        return qs.filter(codigo_rf=codigo_rf)
    if nome_servidor_param:
        return qs.filter(nome__icontains=nome_servidor_param)
    return qs.filter(data_fim__isnull=True)


def _lotacoes_ativas() -> Any:
    """Retorna lotações ativas.

    Returns:
        Lotações sem data de fim.
    """
    return LotacaoServidor.objects.filter(dt_fim__isnull=True)


def _deduplicar_funcionarios_por_rf(rows: list[dict]) -> list[dict]:
    """Remove funcionários duplicados pelo RF.

    Args:
        rows: Funcionários ordenados para deduplicação.

    Returns:
        Lista com a primeira ocorrência de cada RF.
    """
    resultado = []
    vistos = set()
    for item in rows:
        codigo_rf = item["codigo_rf"]
        if codigo_rf in vistos:
            continue
        vistos.add(codigo_rf)
        resultado.append(item)
    return resultado


def _deduplicar_modelos_por_rf(
    funcionarios: Any,
) -> list[FuncionarioUnidadeEducacional]:
    """Remove modelos duplicados pelo RF."""
    resultado = []
    vistos = set()
    for funcionario in funcionarios:
        if funcionario.codigo_rf in vistos:
            continue
        vistos.add(funcionario.codigo_rf)
        resultado.append(funcionario)
    return resultado


def _funcionarios_ativos() -> Any:
    """Retorna funcionários sem data de fim de vínculo."""
    return FuncionarioUnidadeEducacional.objects.filter(
        data_fim__isnull=True,
        dt_fim_nomeacao__isnull=True,
        dt_fim_funcao_atividade__isnull=True,
    )


def _chave_funcionario_externo(
    pessoa_id: int | None,
    codigo_ue: str,
) -> _ChaveFuncionarioExterno:
    """Monta chave entre contrato externo e unidade educacional."""
    return (pessoa_id, codigo_ue)


def _funcionarios_externos_por_contrato(
    contratos: list[ContratoExterno],
) -> dict[_ChaveFuncionarioExterno, FuncionarioUnidadeEducacional]:
    """Indexa vinculos externos compativeis com os contratos."""
    pessoas_id = {contrato.pessoa_id for contrato in contratos}
    codigos_ue = {contrato.codigo_unidade_educacao for contrato in contratos}
    funcionarios = FuncionarioUnidadeEducacional.objects.filter(
        pessoa_id__in=pessoas_id,
        codigo_ue__in=codigos_ue,
    )
    return {
        _chave_funcionario_externo(
            funcionario.pessoa_id,
            funcionario.codigo_ue,
        ): funcionario
        for funcionario in funcionarios
    }


def _funcionarios_ue_legado() -> Any:
    """Retorna vínculos conforme a consulta legada por UE."""
    return FuncionarioUnidadeEducacional.objects.filter(
        Q(origem_vinculo="lotacao")
        | Q(origem_vinculo="cargo_sobreposto", dt_fim_nomeacao__isnull=True)
        | Q(origem_vinculo="atribuicao_aula", dt_fim_nomeacao__isnull=True)
        | Q(
            origem_vinculo="funcao_atividade",
            dt_fim_nomeacao__isnull=True,
            dt_fim_funcao_atividade__isnull=True,
        )
        | Q(origem_vinculo="externo", data_fim__isnull=True)
        | Q(
            origem_vinculo__isnull=True,
            data_fim__isnull=True,
            dt_fim_nomeacao__isnull=True,
            dt_fim_funcao_atividade__isnull=True,
        )
    )


def funcionarios_por_ue(
    codigo_ue: str,
    filtros: dict[str, Any] | None = None,
    somente_professores: bool = True,
    codigos_rfs: list[str] | None = None,
    filtro: str | None = None,
) -> list[dict]:
    """Lista funcionários de uma unidade educacional.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        filtros: Filtros opcionais. Chaves aceitas: ``cargos``,
            ``funcoes_atividades`` e ``funcoes_externas``.
        somente_professores: Indica se a consulta deve limitar professores.
        codigos_rfs: Registros funcionais usados na busca direta.
        filtro: Texto usado na busca por nome ou RF.

    Returns:
        Funcionários da unidade, ordenados por nome.
    """
    base_qs = (
        _funcionarios_ativos()
        if somente_professores
        else (_funcionarios_ue_legado())
    )
    qs = base_qs.filter(codigo_ue=codigo_ue)
    if somente_professores:
        qs = qs.filter(eh_professor=True)
    filtros = filtros or {}
    if cargos := filtros.get("cargos"):
        qs = qs.filter(codigo_cargo__in=[str(cargo) for cargo in cargos])
    if funcoes_atividades := filtros.get("funcoes_atividades"):
        qs = qs.filter(codigo_tipo_funcao_atividade__in=funcoes_atividades)
    if funcoes_externas := filtros.get("funcoes_externas"):
        qs = qs.filter(funcao_externo__in=funcoes_externas)
    if codigos_rfs:
        qs = qs.filter(codigo_rf__in=codigos_rfs)
    elif filtro:
        qs = qs.filter(
            Q(nome__icontains=filtro) | Q(codigo_rf__icontains=filtro),
        )
    rows = sorted(
        (
            _func_row(
                funcionario,
                usar_nome_social=somente_professores,
            )
            for funcionario in qs
        ),
        key=lambda item: item["nome"],
    )
    if somente_professores:
        return rows
    return _deduplicar_funcionarios_por_rf(rows)


def funcionarios_por_ue_cargo(codigo_ue: str, codigo_cargo: int) -> list[dict]:
    """Lista funcionários ativos de uma unidade por cargo.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        codigo_cargo: Código do cargo usado no filtro.

    Returns:
        Funcionários ativos da unidade no cargo informado.
    """
    return funcionarios_por_ue(
        codigo_ue,
        filtros={"cargos": [codigo_cargo]},
    )


def funcionarios_por_cargo(codigo_cargo: int) -> list[dict]:
    """Lista funcionários ativos por cargo.

    Args:
        codigo_cargo: Código do cargo consultado.

    Returns:
        Funcionários ativos vinculados ao cargo informado.
    """
    qs = FuncionarioCargo.objects.filter(
        codigo_cargo=codigo_cargo,
        data_fim__isnull=True,
    )
    resultado = []
    vistos = set()
    for funcionario in qs:
        item = {
            "codigo_rf": funcionario.codigo_rf,
            "nome": funcionario.nome,
            "cpf": None,
            "data_inicio": _fmt_data_funcionario(funcionario.data_inicio),
            "data_fim": _fmt_data_funcionario(funcionario.data_fim),
            "cargo": funcionario.cargo,
            "codigo_cargo": funcionario.codigo_cargo,
            "codigo_tipo_funcao_atividade": 0,
            "esta_afastado": False,
            "funcao_externo": 0,
            "tipo_funcao_externo": 0,
        }
        chave = (
            item["codigo_rf"],
            item["codigo_cargo"],
            item["data_inicio"],
            item["data_fim"],
            item["cargo"],
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        resultado.append(item)
    return sorted(resultado, key=lambda item: item["nome"])


def supervisores_por_dre(
    codigo_dre: str,
    codigos_rfs: list[str],
) -> list[dict]:
    """Lista supervisores vinculados à DRE.

    Args:
        codigo_dre: Código EOL da DRE consultada.
        codigos_rfs: Registros funcionais considerados na busca.

    Returns:
        Supervisores encontrados para a DRE informada.
    """
    hoje = timezone.localdate()
    qs = (
        CargoBaseServidor.objects.filter(
            professor__codigo_rf__in=codigos_rfs,
            dt_fim_nomeacao__isnull=True,
            lotacoes__codigo_dre=codigo_dre,
        )
        .filter(
            Q(codigo_cargo=_CODIGO_CARGO_SUPERVISOR)
            | (
                Q(cargos_sobrepostos__codigo_cargo=_CODIGO_CARGO_SUPERVISOR)
                & (
                    Q(cargos_sobrepostos__dt_fim_cargo_sobreposto__isnull=True)
                    | Q(cargos_sobrepostos__dt_fim_cargo_sobreposto__gt=hoje)
                )
            )
        )
        .select_related("professor")
        .order_by("professor__nome", "professor__codigo_rf")
        .distinct()
    )
    resultado = []
    vistos = set()
    for cargo_base in qs:
        funcionario = cargo_base.professor
        chave = (funcionario.codigo_rf, funcionario.nome)
        if chave in vistos:
            continue
        vistos.add(chave)
        resultado.append(
            {
                "codigo_rf": funcionario.codigo_rf,
                "nome_servidor": funcionario.nome,
            }
        )
    return resultado


def supervisores_dres(codigo_dre: str) -> list[dict]:
    """Lista supervisores da DRE.

    Args:
        codigo_dre: Codigo EOL da DRE consultada.

    Returns:
        Supervisores para a DRE informada.
    """
    qs = FuncionarioUnidadeEducacional.objects.filter(
        codigo_dre=codigo_dre,
        supervisor_dre=True,
    ).order_by("nome")
    resultado = []
    vistos = set()
    for funcionario in qs:
        if funcionario.codigo_rf in vistos:
            continue
        vistos.add(funcionario.codigo_rf)
        resultado.append(
            {
                "codigo_rf": funcionario.codigo_rf,
                "nome_servidor": _nome_funcionario(funcionario),
            }
        )
    return resultado


def funcionarios_por_lista_cargos(
    codigo_ue: str, cargos: list[int]
) -> list[dict]:
    """Lista funcionários de uma unidade por cargos informados.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        cargos: Códigos de cargo usados no filtro.

    Returns:
        Funcionários com lotação ativa nos cargos informados.
    """
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
    """Lista funcionários de uma unidade por função de atividade.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        codigo_funcao_atividade: Código da função de atividade consultada.

    Returns:
        Funcionários da unidade na função de atividade informada.
    """
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
    """Lista funcionários de uma unidade por funções de atividade.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        _funcoes: Funções de atividade consultadas; apenas a primeira é
            refletida no retorno.

    Returns:
        Funcionários da unidade vinculados às funções de atividade.
    """
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
    """Lista funcionários externos de uma unidade por função.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        codigo_funcao_externa: Código do tipo de função externa.

    Returns:
        Funcionários externos ativos da unidade na função informada.
    """
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
    """Lista funcionários externos de uma unidade por funções.

    Args:
        codigo_ue: CodigoEOL da unidade educacional.
        funcoes: Códigos de função externa; lista vazia retorna ``[]``.

    Returns:
        Funcionários externos ativos da unidade nas funções informadas.
    """
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
    """Lista cargos vinculados ao funcionário.

    Args:
        registro_funcional: RF do funcionário consultado.

    Returns:
        Cargos ativos do funcionário com lotação, sobreposição e função.
    """
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
    """Retorna dados de funcionário externo por CPF.

    Args:
        cpf: CPF do funcionário externo.

    Returns:
        Contratos externos do funcionário, ou ``None`` quando não houver.
    """
    contratos = list(
        ContratoExterno.objects.filter(pessoa__cpf=cpf)
        .select_related("pessoa")
        .order_by("codigo_contrato")
    )
    if not contratos:
        return None
    funcionarios = _funcionarios_externos_por_contrato(contratos)
    resultado = []
    for ce in contratos:
        p = ce.pessoa
        funcionario = funcionarios.get(
            _chave_funcionario_externo(
                ce.pessoa_id,
                ce.codigo_unidade_educacao,
            )
        )
        nome_ue = funcionario.nome_ue if funcionario else None
        funcao = funcionario.dc_funcao_externo if funcionario else None
        tipo_funcionario = (
            funcionario.tipo_funcionario_externo if funcionario else None
        )
        resultado.append(
            {
                "nome_pessoa": get_nome(p),
                "nome_pai": p.nome_pai,
                "nome_mae": p.nome_mae,
                "data_nascimento": fmt_iso(p.data_nascimento),
                "rg": p.rg,
                "cpf": p.cpf,
                "titulo_eleitoral": p.titulo_eleitoral,
                "pis_pasep": p.pis_pasep,
                "codigo_contrato_externo": ce.codigo_contrato,
                "codigo_ue": ce.codigo_unidade_educacao,
                "nome_ue": nome_ue,
                "funcao": funcao,
                "tipo_funcionario": tipo_funcionario,
            }
        )
    return resultado


def nome_cpf_servidor(registro_funcional: str) -> dict | None:
    """Retorna nome e CPF do servidor.

    Args:
        registro_funcional: RF do servidor consultado.

    Returns:
        Nome e CPF do servidor, ou ``None`` quando não encontrado.
    """
    func = (
        _funcionarios_ativos()
        .filter(
            codigo_rf=registro_funcional,
            funcao_externo=0,
        )
        .first()
    )
    if func:
        return {"nome": get_nome(func), "cpf": func.cpf}

    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return {"nome": get_nome(prof), "cpf": prof.cpf}


def nome_servidor(registro_funcional: str) -> str | None:
    """Retorna nome do funcionário.

    Args:
        registro_funcional: RF do funcionário consultado.

    Returns:
        Nome do funcionário, ou ``None`` quando não encontrado.
    """
    func = (
        _funcionarios_ativos()
        .filter(
            codigo_rf=registro_funcional,
            funcao_externo=0,
        )
        .first()
    )
    if func:
        return get_nome(func)

    prof = Professor.objects.filter(codigo_rf=registro_funcional).first()
    if not prof:
        return None
    return get_nome(prof)


def servidor_ativo(registro_funcional: str) -> bool:
    """Verifica se o servidor possui cargo ativo.

    Args:
        registro_funcional: RF do servidor consultado.

    Returns:
        ``True`` quando existe cargo ativo para o servidor.
    """
    return bool(
        CargoBaseServidor.objects.filter(
            professor__codigo_rf=registro_funcional,
            dt_fim_nomeacao__isnull=True,
        ).exists()
    )


def dre_ue_cargo(registro_funcional: str, codigo_cargo: int) -> list[dict]:
    """Lista DRE e UE do funcionário por cargo.

    Args:
        registro_funcional: RF do funcionário consultado.
        codigo_cargo: Código do cargo usado no filtro.

    Returns:
        DRE e UE de cada cargo ativo do funcionário.
    """
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
    """Lista usuários SGP por perfil e filtros opcionais.

    Quando recebe apenas RF, retorna dados básicos do usuário para preservar
    o contrato do legado.

    Args:
        _id_perfil: Identificador de perfil; mantido por compatibilidade
            de contrato, sem efeito na consulta.
        codigo_dre: Código da DRE usado como filtro opcional.
        codigo_ue: CodigoEOL da unidade usado como filtro opcional.
        codigo_rf: RF usado como filtro opcional.
        nome_servidor_param: Trecho do nome usado como filtro opcional.

    Returns:
        Usuários com lotação ativa compatíveis com os filtros.
    """
    if codigo_dre:
        return funcionarios_sgp_dre(
            _id_perfil,
            codigo_dre,
            codigo_ue=codigo_ue,
            codigo_rf=codigo_rf,
            nome_servidor_param=nome_servidor_param,
            busca_por_prefixo_ue=False,
        )
    if codigo_rf:
        qs = FuncionarioUnidadeEducacional.objects.filter(codigo_rf=codigo_rf)
        if codigo_ue:
            qs = qs.filter(codigo_ue=codigo_ue)
        funcionario = qs.order_by("codigo_rf").first()
        if not funcionario:
            return []
        # O legado consulta CoreSSO neste fluxo e não preenche vínculo.
        return [
            {
                **_usuario_sgp_row(funcionario),
                "cd_cargo": 0,
                "codigo_funcao_atividade": 0,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            }
        ]

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
    busca_por_prefixo_ue: bool = True,
) -> list[dict]:
    """Lista funcionários SGP por DRE e filtros opcionais.

    Args:
        _id_perfil: Identificador de perfil; mantido por compatibilidade
            de contrato, sem efeito na consulta.
        codigo_dre: Código da DRE usado no filtro.
        codigo_ue: CodigoEOL da unidade usado como filtro opcional.
        codigo_rf: RF usado como filtro opcional.
        nome_servidor_param: Trecho do nome usado como filtro opcional.
        codigo_funcao_atividade: Mantido por compatibilidade de contrato,
            sem efeito na consulta.
        busca_por_prefixo_ue: Indica busca por unidades do agrupamento da DRE.

    Returns:
        Funcionários com lotação ativa na DRE compatíveis com os filtros.
    """
    qs = _funcionarios_sgp_por_dre_qs(
        codigo_dre,
        codigo_ue=codigo_ue,
        codigo_rf=codigo_rf,
        nome_servidor_param=nome_servidor_param,
        busca_por_prefixo_ue=busca_por_prefixo_ue,
    )
    if codigo_funcao_atividade:
        qs = qs.filter(codigo_tipo_funcao_atividade=codigo_funcao_atividade)
    funcoes_por_rf = {
        item["codigo_rf"]: item["codigo_tipo_funcao_atividade"]
        for item in qs.filter(
            origem_vinculo="funcao_atividade",
        )
        .exclude(codigo_tipo_funcao_atividade__isnull=True)
        .exclude(codigo_tipo_funcao_atividade=0)
        .order_by("codigo_rf")
        .values("codigo_rf", "codigo_tipo_funcao_atividade")
    }
    funcionarios = qs.annotate(
        ordem_vinculo=Case(
            When(
                origem_vinculo="cargo_sobreposto",
                codigo_cargo="3351",
                then=Value(0),
            ),
            When(origem_vinculo="lotacao", then=Value(1)),
            When(origem_vinculo="cargo_sobreposto", then=Value(2)),
            When(origem_vinculo="atribuicao_aula", then=Value(3)),
            When(origem_vinculo="funcao_atividade", then=Value(4)),
            When(origem_vinculo="externo", then=Value(5)),
            default=Value(6),
            output_field=IntegerField(),
        ),
        ordem_rf=Window(
            expression=RowNumber(),
            partition_by=[F("codigo_rf")],
            order_by=[
                F("codigo_rf").asc(),
                F("ordem_vinculo").asc(),
                F("codigo_ue").asc(nulls_last=True),
            ],
        ),
    ).filter(ordem_rf=1)
    return [
        _usuario_sgp_row(
            funcionario,
            codigo_dre,
            funcoes_por_rf.get(funcionario.codigo_rf),
        )
        for funcionario in funcionarios
    ]


def acesso_sondagem(codigo_rf: str) -> bool:
    """Verifica se o servidor possui acesso à sondagem.

    Args:
        codigo_rf: RF do servidor consultado.

    Returns:
        ``True`` quando o servidor possui atribuição de aula.
    """
    return bool(
        AtribuicaoAula.objects.filter(
            cargo_base__professor__codigo_rf=codigo_rf,
        ).exists()
    )


def buscar_por_lista_rf_func(lista: list[str]) -> list[dict]:
    """Lista funcionários por registros funcionais.

    Args:
        lista: RFs dos funcionários consultados.

    Returns:
        Funcionários distintos encontrados para os RFs informados.
    """
    return [
        {"nome": get_nome(p), "codigo_rf": p.codigo_rf}
        for p in _deduplicar_modelos_por_rf(
            _funcionarios_ativos().filter(codigo_rf__in=lista)
        )
    ]


def buscar_por_lista_login(lista: list[str]) -> list[dict]:
    """Lista funcionários por logins.

    Args:
        lista: Logins (RF) dos funcionários consultados.

    Returns:
        Funcionários encontrados para os logins informados.
    """
    return [
        {
            "login": p.codigo_rf,
            "nome_servidor": get_nome(p),
            "perfil": _GUID_VAZIO,
        }
        for p in _deduplicar_modelos_por_rf(
            _funcionarios_ativos().filter(
                codigo_rf__in=lista,
                funcao_externo=0
            )
        )
    ]


def buscar_funcionarios(
    codigo_rf: str | None = None,
    codigo_ue: str | None = None,
    nome_servidor: str | None = None,
) -> list[dict]:
    """Lista funcionários por filtros básicos.

    Args:
        codigo_rf: RF usado no filtro.
        codigo_ue: Código EOL da unidade usado no filtro.
        nome_servidor: Trecho do nome usado no filtro.

    Returns:
        Funcionários encontrados para os filtros informados.
    """
    qs = _funcionarios_ativos()
    if codigo_rf:
        qs = qs.filter(codigo_rf=codigo_rf)
    if codigo_ue:
        qs = qs.filter(codigo_ue=codigo_ue)
    if nome_servidor:
        qs = qs.filter(nome__icontains=nome_servidor)
    return [
        {
            "codigo_rf": funcionario.codigo_rf,
            "nome": get_nome(funcionario),
            "cpf": funcionario.cpf,
            "codigo_cargo": funcionario.codigo_cargo or 0,
            "codigo_funcao_atividade": (
                funcionario.codigo_tipo_funcao_atividade or 0
            ),
            "funcao_externo": funcionario.funcao_externo or 0,
            "tipo_funcao_externo": funcionario.tipo_funcao_externo or 0,
        }
        for funcionario in _deduplicar_modelos_por_rf(qs)
    ]
