"""Views do domínio Funcionários (EP-25 a EP-39)."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.funcionarios import repository
from apps.funcionarios.serializers import (
    DreUeAtribuicaoSerializer,
    DreUeCargoSerializer,
    FuncionarioExternoCpfSerializer,
    FuncionarioFuncaoExternaSerializer,
    FuncionarioUESerializer,
    NomeServidorSerializer,
    ResumoFuncionarioSerializer,
    UsuarioSGPSerializer,
)

_TAG_FUNC = ["Funcionários"]
_TAG_ESCOLA_FUNC = ["Funcionários por Escola"]
_TAG_PERFIL = ["Perfis SGP"]
_TAG_ACESSO = ["Acessos"]


# ---------------------------------------------------------------------------
# EP-25 / EP-26 — Funcionários por UE (todos / por cargo)
# ---------------------------------------------------------------------------


class FuncionariosPorUEView(APIView):
    """EP-25/26 — Funcionários de uma UE (todos ou por cargo)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE (todos ou por cargo)",
        parameters=[
            OpenApiParameter("codigoUE", str, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoUE: str,
        codigoCargo: int | None = None,
    ) -> Response:
        if codigoCargo is not None:
            resultado = repository.funcionarios_por_ue_cargo(codigoUE, codigoCargo)
        else:
            resultado = repository.funcionarios_por_ue(codigoUE)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-26-B — Funcionários por lista de cargos (query)
# ---------------------------------------------------------------------------


class FuncionariosCargosQueryView(APIView):
    """EP-26-B — Funcionários de uma UE por lista de cargos (query param)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE por lista de cargos (query)",
        parameters=[
            OpenApiParameter("ueCodigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "cargos", int, OpenApiParameter.QUERY, required=False, many=True
            ),
            OpenApiParameter(
                "dreCodigo", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(self, request: Request, ueCodigo: str) -> Response:
        cargos = [int(c) for c in request.query_params.getlist("cargos")]
        if cargos:
            resultado = repository.funcionarios_por_lista_cargos(ueCodigo, cargos)
        else:
            resultado = repository.funcionarios_por_ue(ueCodigo)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-27 — Funcionários por função de atividade
# ---------------------------------------------------------------------------


class FuncionariosFuncaoAtividadeView(APIView):
    """EP-27 — Funcionários de uma UE por função de atividade."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE por função de atividade",
        parameters=[
            OpenApiParameter("codigoUE", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoFuncaoAtividade", int, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoUE: str,
        codigoFuncaoAtividade: int | None = None,
    ) -> Response:
        resultado = repository.funcionarios_por_funcao_atividade(
            codigoUE, codigoFuncaoAtividade or 0
        )
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-27-B — Funcionários por lista de funções de atividade (query)
# ---------------------------------------------------------------------------


class FuncionariosFuncoesAtividadesQueryView(APIView):
    """EP-27-B — Funcionários por lista de funções de atividade (query)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de UE por lista de funções de atividade",
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
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(self, request: Request, ueCodigo: str) -> Response:
        funcoes = [int(f) for f in request.query_params.getlist("funcoesAtividades")]
        resultado = repository.funcionarios_por_lista_funcoes_atividade(ueCodigo, funcoes)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-28 — Funcionários por função externa
# ---------------------------------------------------------------------------


class FuncionariosFuncaoExternaView(APIView):
    """EP-28 — Funcionários de uma UE por função externa."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE por função externa",
        parameters=[
            OpenApiParameter("codigoUE", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoFuncaoExterna", int, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioFuncaoExternaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoUE: str,
        codigoFuncaoExterna: int | None = None,
    ) -> Response:
        resultado = repository.funcionarios_por_funcao_externa(
            codigoUE, codigoFuncaoExterna or 0
        )
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-28-B — Funcionários por lista de funções externas (query)
# ---------------------------------------------------------------------------


class FuncionariosFuncoesExternasQueryView(APIView):
    """EP-28-B — Funcionários de UE por lista de funções externas (query)."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de UE por lista de funções externas",
        parameters=[
            OpenApiParameter("ueCodigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "funcoes", int, OpenApiParameter.QUERY, required=False, many=True
            ),
            OpenApiParameter(
                "dreCodigo", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: FuncionarioFuncaoExternaSerializer(many=True)},
    )
    def get(self, request: Request, ueCodigo: str) -> Response:
        funcoes = [int(f) for f in request.query_params.getlist("funcoes")]
        resultado = repository.funcionarios_por_lista_funcoes_externas(ueCodigo, funcoes)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-29 — Cargos do funcionário por RF
# ---------------------------------------------------------------------------


class CargosFuncionarioView(APIView):
    """EP-29 — Obter cargos do funcionário por RF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter cargos do funcionário por RF",
        parameters=[
            OpenApiParameter("registroFuncional", str, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioUESerializer(many=True), 400: dict, 404: dict},
    )
    def get(self, request: Request, registroFuncional: str) -> Response:
        return Response(repository.cargos_funcionario(registroFuncional))


# ---------------------------------------------------------------------------
# EP-30 — Funcionário externo por CPF
# ---------------------------------------------------------------------------


class FuncionarioExternoPorCpfView(APIView):
    """EP-30 — Buscar funcionário externo por CPF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar funcionário externo por CPF",
        parameters=[
            OpenApiParameter("cpf", str, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioExternoCpfSerializer, 400: dict, 404: dict},
    )
    def get(self, request: Request, cpf: str) -> Response:
        resultado = repository.funcionario_externo_por_cpf(cpf)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-31 — Nome e CPF do servidor por RF
# ---------------------------------------------------------------------------


class NomeServidorView(APIView):
    """EP-31 — Obter nome e CPF do servidor por RF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter nome e CPF do servidor por RF",
        parameters=[
            OpenApiParameter("registroFuncional", str, OpenApiParameter.PATH),
        ],
        responses={200: NomeServidorSerializer, 400: dict, 404: dict},
    )
    def get(self, request: Request, registroFuncional: str) -> Response:
        resultado = repository.nome_servidor(registroFuncional)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-32 — DRE/UE do funcionário (nome-usuario-eol)
# ---------------------------------------------------------------------------


class DreUeAtribuicaoFuncionarioView(APIView):
    """EP-32 — Obter DRE/UE de atribuição do funcionário."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter DRE/UE de atribuição do funcionário",
        parameters=[
            OpenApiParameter("registroFuncional", str, OpenApiParameter.PATH),
        ],
        responses={200: DreUeAtribuicaoSerializer, 400: dict, 404: dict},
    )
    def get(self, request: Request, registroFuncional: str) -> Response:
        nome = repository.dre_ue_atribuicao(registroFuncional)
        if nome is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        from django.http import HttpResponse
        return HttpResponse(nome, content_type="text/plain")


# ---------------------------------------------------------------------------
# EP-33 — Servidor ativo
# ---------------------------------------------------------------------------


class ServidorAtivoView(APIView):
    """EP-33 — Verificar se servidor está ativo."""

    @extend_schema(
        tags=_TAG_ACESSO,
        summary="Verificar se servidor está ativo",
        parameters=[
            OpenApiParameter("registroFuncional", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict, 404: dict},
    )
    def get(self, request: Request, registroFuncional: str) -> Response:
        return Response(repository.servidor_ativo(registroFuncional))


# ---------------------------------------------------------------------------
# EP-34 — DRE/UE do funcionário por cargo específico
# ---------------------------------------------------------------------------


class DreUeAtribuicaoCargoView(APIView):
    """EP-34 — Obter DRE/UE do funcionário por cargo."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter DRE/UE do funcionário por cargo específico",
        parameters=[
            OpenApiParameter("registroFuncional", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoCargo", int, OpenApiParameter.PATH),
        ],
        responses={200: DreUeCargoSerializer, 400: dict, 404: dict},
    )
    def get(
        self,
        request: Request,
        registroFuncional: str,
        codigoCargo: int,
    ) -> Response:
        resultado = repository.dre_ue_cargo(registroFuncional, codigoCargo)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-35 — Usuários SGP por perfil
# ---------------------------------------------------------------------------


class UsuariosSGPView(APIView):
    """EP-35 — Buscar usuários SGP por perfil."""

    @extend_schema(
        tags=_TAG_PERFIL,
        summary="Buscar usuários SGP por perfil",
        parameters=[
            OpenApiParameter("idPerfil", str, OpenApiParameter.PATH),
            OpenApiParameter("CodigoDre", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("CodigoUe", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("CodigoRf", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter(
                "NomeServidor", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: UsuarioSGPSerializer(many=True), 400: dict, 404: dict},
    )
    def get(self, request: Request, idPerfil: str) -> Response:
        resultado = repository.usuarios_sgp_por_perfil(
            idPerfil,
            codigo_dre=request.query_params.get("CodigoDre"),
            codigo_ue=request.query_params.get("CodigoUe"),
            codigo_rf=request.query_params.get("CodigoRf"),
            nome_servidor_param=request.query_params.get("NomeServidor"),
        )
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-36 — Funcionários SGP por DRE/perfil
# ---------------------------------------------------------------------------


class FuncionariosSGPDreView(APIView):
    """EP-36 — Buscar funcionários SGP por DRE e perfil."""

    @extend_schema(
        tags=_TAG_PERFIL,
        summary="Buscar funcionários SGP por DRE e perfil",
        parameters=[
            OpenApiParameter("idPerfil", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoDre", str, OpenApiParameter.PATH),
            OpenApiParameter("CodigoUe", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("CodigoRF", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter(
                "NomeServidor", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "CodigoFuncaoAtividade", int, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: UsuarioSGPSerializer(many=True), 400: dict, 404: dict},
    )
    def get(self, request: Request, idPerfil: str, codigoDre: str) -> Response:
        funcao_str = request.query_params.get("CodigoFuncaoAtividade")
        resultado = repository.funcionarios_sgp_dre(
            idPerfil,
            codigoDre,
            codigo_ue=request.query_params.get("CodigoUe"),
            codigo_rf=request.query_params.get("CodigoRF"),
            nome_servidor_param=request.query_params.get("NomeServidor"),
            codigo_funcao_atividade=int(funcao_str) if funcao_str else None,
        )
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-37 — Acesso à sondagem
# ---------------------------------------------------------------------------


class AcessoSondagemView(APIView):
    """EP-37 — Verificar se professor tem acesso à sondagem."""

    @extend_schema(
        tags=_TAG_ACESSO,
        summary="Verificar se professor tem acesso à sondagem",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
        ],
        responses={200: bool},
    )
    def get(self, request: Request, codigoRF: str) -> Response:
        return Response(repository.acesso_sondagem(codigoRF))


# ---------------------------------------------------------------------------
# EP-38 — Buscar por lista de RF (POST)
# ---------------------------------------------------------------------------


class BuscarPorListaRFView(APIView):
    """EP-38 — Buscar resumo de funcionários por lista de RF."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar resumo de funcionários por lista de RF (POST)",
        request=list,
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        lista = request.data if isinstance(request.data, list) else []
        return Response(repository.buscar_por_lista_rf_func(lista))


# ---------------------------------------------------------------------------
# EP-39 — Buscar por lista de login (POST)
# ---------------------------------------------------------------------------


class BuscarPorListaLoginView(APIView):
    """EP-39 — Buscar resumo de funcionários por lista de login."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar resumo de funcionários por lista de login (POST)",
        request=list,
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        lista = request.data if isinstance(request.data, list) else []
        return Response(repository.buscar_por_lista_login(lista))
