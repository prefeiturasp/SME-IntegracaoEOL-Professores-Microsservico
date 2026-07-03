"""Regras de negocio do dominio de funcionarios."""

from dataclasses import dataclass
from typing import Any

from apps.funcionarios import repository


@dataclass(frozen=True)
class ResultadoServico:
    """Representa o resultado produzido pela camada de serviço."""

    payload: Any
    status_code: int = 200


def funcionarios_por_ue(
    codigo_ue: str,
    filtros: dict[str, Any],
) -> list[dict]:
    """Lista funcionarios de uma unidade educacional."""
    return repository.funcionarios_por_ue(codigo_ue, filtros=filtros)


def funcionarios_por_lista_cargos(
    ue_codigo: str,
    cargos_param: list[str],
) -> list[dict]:
    """Lista funcionarios de uma unidade por cargos.

    Args:
        ue_codigo: Codigo da unidade educacional.
        cargos_param: Codigos de cargos recebidos como texto.

    Returns:
        Funcionarios encontrados para os cargos informados.
    """
    cargos = [int(cargo) for cargo in cargos_param]
    if cargos:
        return repository.funcionarios_por_lista_cargos(ue_codigo, cargos)
    return repository.funcionarios_por_ue(ue_codigo)


def funcionarios_por_funcao_atividade(
    codigo_ue: str,
    codigo_funcao_atividade: int | None = None,
) -> list[dict]:
    """Lista funcionarios de uma unidade por funcao de atividade."""
    return repository.funcionarios_por_funcao_atividade(
        codigo_ue,
        codigo_funcao_atividade or 0,
    )


def funcionarios_por_lista_funcoes_atividade(
    ue_codigo: str,
    funcoes_param: list[str],
) -> list[dict]:
    """Lista funcionarios por funcoes de atividade."""
    funcoes = [int(funcao) for funcao in funcoes_param]
    return repository.funcionarios_por_lista_funcoes_atividade(
        ue_codigo,
        funcoes,
    )


def funcionarios_por_funcao_externa(
    codigo_ue: str,
    codigo_funcao_externa: int | None = None,
) -> list[dict]:
    """Lista funcionarios externos de uma unidade por funcao."""
    return repository.funcionarios_por_funcao_externa(
        codigo_ue,
        codigo_funcao_externa or 0,
    )


def funcionarios_por_lista_funcoes_externas(
    ue_codigo: str,
    funcoes_param: list[str],
) -> list[dict]:
    """Lista funcionarios externos de uma unidade por funcoes."""
    funcoes = [int(funcao) for funcao in funcoes_param]
    return repository.funcionarios_por_lista_funcoes_externas(
        ue_codigo,
        funcoes,
    )


def cargos_funcionario(registro_funcional: str) -> list[dict]:
    """Lista cargos do funcionario por registro funcional."""
    return repository.cargos_funcionario(registro_funcional)


def funcionario_externo_por_cpf(cpf: str) -> list[dict] | None:
    """Retorna funcionario externo por CPF."""
    return repository.funcionario_externo_por_cpf(cpf)


def nome_cpf_servidor(registro_funcional: str) -> dict | None:
    """Retorna nome e CPF do servidor por registro funcional."""
    return repository.nome_cpf_servidor(registro_funcional)


def nome_servidor(registro_funcional: str) -> str | None:
    """Retorna nome usuario EOL do servidor."""
    return repository.nome_servidor(registro_funcional)


def servidor_ativo(registro_funcional: str) -> bool:
    """Verifica se o servidor esta ativo."""
    return repository.servidor_ativo(registro_funcional)


def dre_ue_cargo(
    registro_funcional: str,
    codigo_cargo: int,
) -> list[dict] | None:
    """Retorna unidade do funcionario por cargo."""
    return repository.dre_ue_cargo(registro_funcional, codigo_cargo)


def usuarios_sgp_por_perfil(
    id_perfil: str,
    codigo_dre: str | None = None,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor: str | None = None,
) -> ResultadoServico:
    """Lista usuarios SGP por perfil.

    Args:
        id_perfil: Identificador do perfil SGP.
        codigo_dre: Codigo da DRE usado como filtro.
        codigo_ue: Codigo da unidade educacional usado como filtro.
        codigo_rf: Registro funcional usado como filtro.
        nome_servidor: Nome do servidor usado como filtro.

    Returns:
        Resultado da consulta conforme as regras de serviço.
    """
    if repository.perfil_placeholder_invalido(id_perfil) and not codigo_rf:
        mensagem = (
            repository.MENSAGEM_ERRO_LEGADO
            if codigo_dre
            else repository.MENSAGEM_ERRO_PERFIL_SEM_DRE_RF
        )
        return ResultadoServico(mensagem, 400)

    resultado = repository.usuarios_sgp_por_perfil(
        id_perfil,
        codigo_dre=codigo_dre,
        codigo_ue=codigo_ue,
        codigo_rf=codigo_rf,
        nome_servidor_param=nome_servidor,
    )
    if not resultado:
        return ResultadoServico(None, 404)
    return ResultadoServico(resultado)


def funcionarios_sgp_dre(
    id_perfil: str,
    codigo_dre: str,
    codigo_ue: str | None = None,
    codigo_rf: str | None = None,
    nome_servidor: str | None = None,
    codigo_funcao_atividade: str | None = None,
) -> ResultadoServico:
    """Lista funcionarios SGP por DRE e perfil.

    Args:
        id_perfil: Identificador do perfil SGP.
        codigo_dre: Codigo da DRE.
        codigo_ue: Codigo da unidade educacional usado como filtro.
        codigo_rf: Registro funcional usado como filtro.
        nome_servidor: Nome do servidor usado como filtro.
        codigo_funcao_atividade: Codigo de funcao de atividade como texto.

    Returns:
        Resultado da consulta conforme as regras de serviço.
    """
    if repository.perfil_placeholder_invalido(id_perfil):
        return ResultadoServico(repository.MENSAGEM_ERRO_LEGADO, 400)

    resultado = repository.funcionarios_sgp_dre(
        id_perfil,
        codigo_dre,
        codigo_ue=codigo_ue,
        codigo_rf=codigo_rf,
        nome_servidor_param=nome_servidor,
        codigo_funcao_atividade=(
            int(codigo_funcao_atividade) if codigo_funcao_atividade else None
        ),
    )
    if not resultado:
        return ResultadoServico(None, 404)
    return ResultadoServico(resultado)


def acesso_sondagem(codigo_rf: str) -> bool:
    """Verifica se o professor tem acesso a sondagem."""
    return repository.acesso_sondagem(codigo_rf)


def buscar_por_lista_rf(payload: Any) -> list[dict]:
    """Lista resumos de funcionarios por registros funcionais."""
    lista = payload if isinstance(payload, list) else []
    return repository.buscar_por_lista_rf_func(lista)


def buscar_por_lista_login(payload: Any) -> list[dict]:
    """Lista resumos de funcionarios por logins."""
    lista = payload if isinstance(payload, list) else []
    return repository.buscar_por_lista_login(lista)
