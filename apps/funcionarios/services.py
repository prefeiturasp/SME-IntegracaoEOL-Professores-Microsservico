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
    """Lista funcionarios de uma unidade educacional.

    Args:
        codigo_ue: Código EOL da unidade educacional consultada.
        filtros: Filtros opcionais aplicados à consulta de funcionários.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.funcionarios_por_ue(codigo_ue, filtros=filtros)


def funcionarios_ue(
    codigo_ue: str,
    filtros: dict[str, Any],
    codigos_rfs: list[str] | None = None,
    filtro: str | None = None,
) -> list[dict]:
    """Lista funcionários ativos de uma unidade educacional.

    Args:
        codigo_ue: Código EOL da unidade educacional consultada.
        filtros: Filtros opcionais aplicados à consulta.
        codigos_rfs: Registros funcionais usados na busca direta.
        filtro: Texto usado na busca por nome ou RF.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.funcionarios_por_ue(
        codigo_ue,
        filtros=filtros,
        somente_professores=False,
        codigos_rfs=codigos_rfs,
        filtro=filtro,
    )


def funcionarios_por_cargo(codigo_cargo: int) -> list[dict]:
    """Lista funcionários ativos por cargo.

    Args:
        codigo_cargo: Código do cargo consultado.

    Returns:
        Lista de dados encontrados para o cargo informado.
    """
    return repository.funcionarios_por_cargo(codigo_cargo)


def supervisores_por_dre(
    codigo_dre: str,
    codigos_rfs: list[str],
) -> list[dict]:
    """Lista supervisores vinculados à DRE.

    Args:
        codigo_dre: Código EOL da DRE consultada.
        codigos_rfs: Registros funcionais considerados na busca.

    Returns:
        Lista de supervisores encontrados.
    """
    return repository.supervisores_por_dre(codigo_dre, codigos_rfs)


def funcionarios_por_lista_cargos(
    ue_codigo: str,
    cargos_param: list[str],
) -> list[dict]:
    """Lista funcionarios de uma unidade por cargos.

    Args:
        ue_codigo: Código EOL da unidade educacional consultada.
        cargos_param: Códigos de cargos recebidos como texto pela API.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    cargos = [int(cargo) for cargo in cargos_param]
    if cargos:
        return repository.funcionarios_por_lista_cargos(ue_codigo, cargos)
    return repository.funcionarios_por_ue(ue_codigo)


def funcionarios_por_funcao_atividade(
    codigo_ue: str,
    codigo_funcao_atividade: int | None = None,
) -> list[dict]:
    """Lista funcionarios de uma unidade por funcao de atividade.

    Args:
        codigo_ue: Código EOL da unidade educacional consultada.
        codigo_funcao_atividade: Código da função de atividade usada no filtro.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.funcionarios_por_funcao_atividade(
        codigo_ue,
        codigo_funcao_atividade or 0,
    )


def funcionarios_por_lista_funcoes_atividade(
    ue_codigo: str,
    funcoes_param: list[str],
) -> list[dict]:
    """Lista funcionarios por funcoes de atividade.

    Args:
        ue_codigo: Código EOL da unidade educacional consultada.
        funcoes_param: Códigos de funções recebidos como texto pela API.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    funcoes = [int(funcao) for funcao in funcoes_param]
    return repository.funcionarios_por_lista_funcoes_atividade(
        ue_codigo,
        funcoes,
    )


def funcionarios_por_funcao_externa(
    codigo_ue: str,
    codigo_funcao_externa: int | None = None,
) -> list[dict]:
    """Lista funcionarios externos de uma unidade por funcao.

    Args:
        codigo_ue: Código EOL da unidade educacional consultada.
        codigo_funcao_externa: Código da função externa usada no filtro.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.funcionarios_por_funcao_externa(
        codigo_ue,
        codigo_funcao_externa or 0,
    )


def funcionarios_por_lista_funcoes_externas(
    ue_codigo: str,
    funcoes_param: list[str],
) -> list[dict]:
    """Lista funcionarios externos de uma unidade por funcoes.

    Args:
        ue_codigo: Código EOL da unidade educacional consultada.
        funcoes_param: Códigos de funções recebidos como texto pela API.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    funcoes = [int(funcao) for funcao in funcoes_param]
    return repository.funcionarios_por_lista_funcoes_externas(
        ue_codigo,
        funcoes,
    )


def cargos_funcionario(registro_funcional: str) -> list[dict]:
    """Lista cargos do funcionario por registro funcional.

    Args:
        registro_funcional: Registro funcional do servidor consultado.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    return repository.cargos_funcionario(registro_funcional)


def funcionario_externo_por_cpf(cpf: str) -> list[dict] | None:
    """Retorna funcionario externo por CPF.

    Args:
        cpf: CPF do funcionário externo consultado.

    Returns:
        Lista de dados encontrados ou ``None`` quando não houver resultado.
    """
    return repository.funcionario_externo_por_cpf(cpf)


def nome_cpf_servidor(registro_funcional: str) -> dict | None:
    """Retorna nome e CPF do servidor por registro funcional.

    Args:
        registro_funcional: Registro funcional do servidor consultado.

    Returns:
        Dados encontrados ou ``None`` quando não houver resultado.
    """
    return repository.nome_cpf_servidor(registro_funcional)


def nome_servidor(registro_funcional: str) -> str | None:
    """Retorna nome usuario EOL do servidor.

    Args:
        registro_funcional: Registro funcional do servidor consultado.

    Returns:
        Texto encontrado ou ``None`` quando não houver resultado.
    """
    return repository.nome_servidor(registro_funcional)


def servidor_ativo(registro_funcional: str) -> bool:
    """Verifica se o servidor esta ativo.

    Args:
        registro_funcional: Registro funcional do servidor consultado.

    Returns:
        Resultado booleano da validação solicitada.
    """
    return repository.servidor_ativo(registro_funcional)


def dre_ue_cargo(
    registro_funcional: str,
    codigo_cargo: int,
) -> list[dict] | None:
    """Retorna unidade do funcionario por cargo.

    Args:
        registro_funcional: Registro funcional do servidor consultado.
        codigo_cargo: Código do cargo usado para filtrar atribuições.

    Returns:
        Lista de dados encontrados ou ``None`` quando não houver resultado.
    """
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
        id_perfil: Identificador do perfil SGP usado na consulta.
        codigo_dre: Código EOL da DRE usada na consulta.
        codigo_ue: Código EOL da unidade educacional consultada.
        codigo_rf: Registro funcional do professor ou servidor consultado.
        nome_servidor: Trecho do nome do servidor usado como filtro.

    Returns:
        Resultado do serviço com payload e status HTTP.
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
        id_perfil: Identificador do perfil SGP usado na consulta.
        codigo_dre: Código EOL da DRE usada na consulta.
        codigo_ue: Código EOL da unidade educacional consultada.
        codigo_rf: Registro funcional do professor ou servidor consultado.
        nome_servidor: Trecho do nome do servidor usado como filtro.
        codigo_funcao_atividade: Código da função de atividade usada no filtro.

    Returns:
        Resultado do serviço com payload e status HTTP.
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
    """Verifica se o professor tem acesso a sondagem.

    Args:
        codigo_rf: Registro funcional do professor ou servidor consultado.

    Returns:
        Resultado booleano da validação solicitada.
    """
    return repository.acesso_sondagem(codigo_rf)


def buscar_por_lista_rf(payload: Any) -> list[dict]:
    """Lista resumos de funcionarios por registros funcionais.

    Args:
        payload: Lista de registros funcionais recebida no corpo.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    lista = payload if isinstance(payload, list) else []
    return repository.buscar_por_lista_rf_func(lista)


def buscar_por_lista_login(payload: Any) -> list[dict]:
    """Lista resumos de funcionarios por logins.

    Args:
        payload: Lista de logins recebida no corpo.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    lista = payload if isinstance(payload, list) else []
    return repository.buscar_por_lista_login(lista)


def buscar_funcionarios(payload: Any) -> list[dict]:
    """Lista funcionários por filtros básicos.

    Args:
        payload: Filtros de RF, UE e nome recebidos no corpo.

    Returns:
        Lista de dados encontrados para os filtros informados.
    """
    filtros = payload if isinstance(payload, dict) else {}
    return repository.buscar_funcionarios(
        codigo_rf=filtros.get("CodigoRF") or filtros.get("codigoRF"),
        codigo_ue=filtros.get("CodigoUE") or filtros.get("codigoUE"),
        nome_servidor=(
            filtros.get("NomeServidor") or filtros.get("nomeServidor")
        ),
    )
