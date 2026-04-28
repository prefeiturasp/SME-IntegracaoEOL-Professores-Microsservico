"""Views mock do domínio Funcionários (EP-25 a EP-39)."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mock_data import PROFESSOR_EXTERNO_MOCK

_TAG_FUNC = ["Funcionários"]
_TAG_ESCOLA_FUNC = ["Funcionários por Escola"]
_TAG_PERFIL = ["Perfis SGP"]
_TAG_ACESSO = ["Acessos"]

_NOME_MARIA_SILVA = "Maria Silva"
_NOME_CARLOS_PEREIRA = "Carlos Pereira"
_CARGO_PROFESSOR_FUNDAMENTAL_MEDIO = (
    "Professor de Ensino Fundamental II e Médio"
)
_CODIGO_RF_MARIA = "7654321"
_CODIGO_RF_CARLOS = "1234567"

_MOCK_FUNC_LIST = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nomeServidor": _NOME_MARIA_SILVA,
        "cargo": _CARGO_PROFESSOR_FUNDAMENTAL_MEDIO,
        "dataInicio": "2024-02-01",
        "dataFim": None,
    },
    {
        "codigoRf": _CODIGO_RF_CARLOS,
        "nomeServidor": _NOME_CARLOS_PEREIRA,
        "cargo": "Diretor de Escola",
        "dataInicio": "2023-01-15",
        "dataFim": None,
    },
]

_MOCK_FUNC_EXTERNO_LIST = [
    {
        "cpf": "987.654.321-00",
        "nomeServidor": "João Souza",
        "codigoEscola": "000532",
        "dataInicio": "2024-02-01",
    }
]

_MOCK_CARGOS = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nomeServidor": _NOME_MARIA_SILVA,
        "dataInicio": "2010-03-01",
        "dataFim": None,
        "cargo": _CARGO_PROFESSOR_FUNDAMENTAL_MEDIO,
    }
]

_MOCK_NOME_SERVIDOR = {
    "codigoRf": _CODIGO_RF_MARIA,
    "nome": _NOME_MARIA_SILVA,
    "cpf": "123.456.789-00",
}

_MOCK_DRE_UE = {
    "codigoRf": _CODIGO_RF_MARIA,
    "nome": _NOME_MARIA_SILVA,
    "codigoDre": "108100",
    "codigoUe": "000532",
}

_MOCK_DRE_UE_CARGO = {
    "codigoRf": _CODIGO_RF_MARIA,
    "codigoDre": "108100",
    "codigoUe": "000532",
    "cargo": _CARGO_PROFESSOR_FUNDAMENTAL_MEDIO,
}

_MOCK_USUARIOS_SGP = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nomeServidor": _NOME_MARIA_SILVA,
        "codigoDre": "108100",
        "codigoUe": "000532",
    },
    {
        "codigoRf": _CODIGO_RF_CARLOS,
        "nomeServidor": _NOME_CARLOS_PEREIRA,
        "codigoDre": "108100",
        "codigoUe": "000532",
    },
]

_MOCK_RESUMO = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nome": _NOME_MARIA_SILVA,
        "cpf": "123.456.789-00",
    },
    {
        "codigoRf": _CODIGO_RF_CARLOS,
        "nome": _NOME_CARLOS_PEREIRA,
        "cpf": "111.222.333-44",
    },
]


# ---------------------------------------------------------------------------
# EP-25 / EP-26 — Funcionários por UE (todos / por cargo)
# ---------------------------------------------------------------------------


class FuncionariosPorUEView(APIView):
    """EP-25/26 — Funcionários de uma UE (todos ou por cargo)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="EP-25/26 | Funcionários de uma UE (todos ou por cargo)",
        parameters=[
            OpenApiParameter("codigoUE", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        codigo_cargo: int | None = None,
    ) -> Response:
        """Retorna lista mock de funcionários."""
        return Response(_MOCK_FUNC_LIST)


# ---------------------------------------------------------------------------
# EP-26-B — Funcionários por lista de cargos (query)
# ---------------------------------------------------------------------------


class FuncionariosCargosQueryView(APIView):
    """EP-26-B — Funcionários de uma UE por lista de cargos (query param)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary=(
            "EP-26-B | Funcionários de uma UE por lista de cargos (query)"
        ),
        parameters=[
            OpenApiParameter("ueCodigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "cargos",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "dreCodigo", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: list},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        """Retorna lista mock de funcionários por cargos."""
        return Response(_MOCK_FUNC_LIST)


# ---------------------------------------------------------------------------
# EP-27 — Funcionários por função de atividade
# ---------------------------------------------------------------------------


class FuncionariosFuncaoAtividadeView(APIView):
    """EP-27 — Funcionários de uma UE por função de atividade."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="EP-27 | Funcionários de uma UE por função de atividade",
        parameters=[
            OpenApiParameter("codigoUE", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigoFuncaoAtividade", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        codigo_funcao_atividade: int | None = None,
    ) -> Response:
        """Retorna lista mock de funcionários por função de atividade."""
        return Response(_MOCK_FUNC_LIST)


# ---------------------------------------------------------------------------
# EP-27-B — Funcionários por lista de funções de atividade (query)
# ---------------------------------------------------------------------------


class FuncionariosFuncoesAtividadesQueryView(APIView):
    """EP-27-B — Funcionários por lista de funções de atividade (query)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary=(
            "EP-27-B | Funcionários de UE por lista de funções de atividade"
        ),
        parameters=[
            OpenApiParameter("ueCodigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "funcoesAtividades",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "dreCodigo", str, OpenApiParameter.QUERY, required=True
            ),
        ],
        responses={200: list},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        """Retorna lista mock de funcionários por funções de atividade."""
        return Response(_MOCK_FUNC_LIST)


# ---------------------------------------------------------------------------
# EP-28 — Funcionários por função externa
# ---------------------------------------------------------------------------


class FuncionariosFuncaoExternaView(APIView):
    """EP-28 — Funcionários de uma UE por função externa."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="EP-28 | Funcionários de uma UE por função externa",
        parameters=[
            OpenApiParameter("codigoUE", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigoFuncaoExterna", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        codigo_funcao_externa: int | None = None,
    ) -> Response:
        """Retorna lista mock de funcionários externos."""
        return Response(_MOCK_FUNC_EXTERNO_LIST)


# ---------------------------------------------------------------------------
# EP-28-B — Funcionários por lista de funções externas (query)
# ---------------------------------------------------------------------------


class FuncionariosFuncoesExternasQueryView(APIView):
    """EP-28-B — Funcionários de UE por lista de funções externas (query)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary=(
            "EP-28-B | Funcionários de UE por lista de funções externas"
        ),
        parameters=[
            OpenApiParameter("ueCodigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "funcoes",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "dreCodigo", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: list},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        """Retorna lista mock de funcionários externos por funções."""
        return Response(_MOCK_FUNC_EXTERNO_LIST)


# ---------------------------------------------------------------------------
# EP-29 — Cargos do funcionário por RF
# ---------------------------------------------------------------------------


class CargosFuncionarioView(APIView):
    """EP-29 — Obter cargos do funcionário por RF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="EP-29 | Obter cargos do funcionário por RF",
        parameters=[
            OpenApiParameter(
                "registroFuncional", str, OpenApiParameter.PATH
            ),
        ],
        responses={200: list, 400: dict, 404: dict},
    )
    def get(
        self, request: Request, registro_funcional: str
    ) -> Response:
        """Retorna lista mock de cargos do funcionário."""
        return Response(_MOCK_CARGOS)


# ---------------------------------------------------------------------------
# EP-30 — Funcionário externo por CPF
# ---------------------------------------------------------------------------


class FuncionarioExternoPorCpfView(APIView):
    """EP-30 — Buscar funcionário externo por CPF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="EP-30 | Buscar funcionário externo por CPF",
        parameters=[
            OpenApiParameter("cpf", str, OpenApiParameter.PATH),
        ],
        responses={200: dict, 400: dict, 404: dict},
    )
    def get(self, request: Request, cpf: str) -> Response:
        """Retorna dados mock do funcionário externo."""
        return Response(PROFESSOR_EXTERNO_MOCK)


# ---------------------------------------------------------------------------
# EP-31 — Nome e CPF do servidor por RF
# ---------------------------------------------------------------------------


class NomeServidorView(APIView):
    """EP-31 — Obter nome e CPF do servidor por RF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="EP-31 | Obter nome e CPF do servidor por RF",
        parameters=[
            OpenApiParameter(
                "registroFuncional", str, OpenApiParameter.PATH
            ),
        ],
        responses={200: dict, 400: dict, 404: dict},
    )
    def get(
        self, request: Request, registro_funcional: str
    ) -> Response:
        """Retorna nome e CPF mock do servidor."""
        return Response(_MOCK_NOME_SERVIDOR)


# ---------------------------------------------------------------------------
# EP-32 — DRE/UE do funcionário (nome-usuario-eol)
# ---------------------------------------------------------------------------


class DreUeAtribuicaoFuncionarioView(APIView):
    """EP-32 — Obter DRE/UE de atribuição do funcionário."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="EP-32 | Obter DRE/UE de atribuição do funcionário",
        parameters=[
            OpenApiParameter(
                "registroFuncional", str, OpenApiParameter.PATH
            ),
        ],
        responses={200: dict, 400: dict, 404: dict},
    )
    def get(
        self, request: Request, registro_funcional: str
    ) -> Response:
        """Retorna DRE/UE mock do funcionário."""
        return Response(_MOCK_DRE_UE)


# ---------------------------------------------------------------------------
# EP-33 — Servidor ativo
# ---------------------------------------------------------------------------


class ServidorAtivoView(APIView):
    """EP-33 — Verificar se servidor está ativo."""

    @extend_schema(
        tags=_TAG_ACESSO,
        summary="EP-33 | Verificar se servidor está ativo",
        parameters=[
            OpenApiParameter(
                "registroFuncional", str, OpenApiParameter.PATH
            ),
        ],
        responses={200: bool, 400: dict, 404: dict},
    )
    def get(
        self, request: Request, registro_funcional: str
    ) -> Response:
        """Retorna true (servidor ativo) no mock."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-34 — DRE/UE do funcionário por cargo específico
# ---------------------------------------------------------------------------


class DreUeAtribuicaoCargoView(APIView):
    """EP-34 — Obter DRE/UE do funcionário por cargo."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="EP-34 | Obter DRE/UE do funcionário por cargo específico",
        parameters=[
            OpenApiParameter(
                "registroFuncional", str, OpenApiParameter.PATH
            ),
            OpenApiParameter("codigoCargo", int, OpenApiParameter.PATH),
        ],
        responses={200: dict, 400: dict, 404: dict},
    )
    def get(
        self,
        request: Request,
        registro_funcional: str,
        codigo_cargo: int,
    ) -> Response:
        """Retorna DRE/UE/cargo mock do funcionário."""
        return Response(_MOCK_DRE_UE_CARGO)


# ---------------------------------------------------------------------------
# EP-35 — Usuários SGP por perfil
# ---------------------------------------------------------------------------


class UsuariosSGPView(APIView):
    """EP-35 — Buscar usuários SGP por perfil."""

    @extend_schema(
        tags=_TAG_PERFIL,
        summary="EP-35 | Buscar usuários SGP por perfil",
        parameters=[
            OpenApiParameter("idPerfil", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "CodigoDre", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "CodigoUe", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "CodigoRf", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "NomeServidor",
                str,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: list, 400: dict, 404: dict},
    )
    def get(self, request: Request, id_perfil: str) -> Response:
        """Retorna lista mock de usuários SGP."""
        return Response(_MOCK_USUARIOS_SGP)


# ---------------------------------------------------------------------------
# EP-36 — Funcionários SGP por DRE/perfil
# ---------------------------------------------------------------------------


class FuncionariosSGPDreView(APIView):
    """EP-36 — Buscar funcionários SGP por DRE e perfil."""

    @extend_schema(
        tags=_TAG_PERFIL,
        summary="EP-36 | Buscar funcionários SGP por DRE e perfil",
        parameters=[
            OpenApiParameter("idPerfil", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoDre", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "CodigoUe", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "CodigoRF", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "NomeServidor",
                str,
                OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                "CodigoFuncaoAtividade",
                int,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: list, 400: dict, 404: dict},
    )
    def get(
        self, request: Request, id_perfil: str, codigo_dre: str
    ) -> Response:
        """Retorna lista mock de funcionários SGP por DRE."""
        return Response(_MOCK_USUARIOS_SGP)


# ---------------------------------------------------------------------------
# EP-37 — Acesso à sondagem
# ---------------------------------------------------------------------------


class AcessoSondagemView(APIView):
    """EP-37 — Verificar se professor tem acesso à sondagem."""

    @extend_schema(
        tags=_TAG_ACESSO,
        summary="EP-37 | Verificar se professor tem acesso à sondagem",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
        ],
        responses={200: bool},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        """Retorna true (tem acesso à sondagem) no mock."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-38 — Buscar por lista de RF (POST)
# ---------------------------------------------------------------------------


class BuscarPorListaRFView(APIView):
    """EP-38 — Buscar resumo de funcionários por lista de RF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="EP-38 | Buscar resumo de funcionários por lista de RF (POST)",
        request=list,
        responses={200: list},
    )
    def post(self, request: Request) -> Response:
        """Retorna lista mock de funcionários."""
        return Response(_MOCK_RESUMO)


# ---------------------------------------------------------------------------
# EP-39 — Buscar por lista de login (POST)
# ---------------------------------------------------------------------------


class BuscarPorListaLoginView(APIView):
    """EP-39 — Buscar resumo de funcionários por lista de login."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary=(
            "EP-39 | Buscar resumo de funcionários por lista de login (POST)"
        ),
        request=list,
        responses={200: list},
    )
    def post(self, request: Request) -> Response:
        """Retorna lista mock de funcionários."""
        return Response(_MOCK_RESUMO)
