"""Views do domínio de funcionários."""

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


class FuncionariosPorUEView(APIView):
    """Lista funcionários de uma unidade educacional."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE (todos ou por cargo)",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        codigo_cargo: int | None = None,
    ) -> Response:
        if codigo_cargo is not None:
            resultado = repository.funcionarios_por_ue_cargo(
                codigo_ue, codigo_cargo
            )
        else:
            resultado = repository.funcionarios_por_ue(codigo_ue)
        return Response(resultado)


class FuncionariosCargosQueryView(APIView):
    """Lista funcionários de uma unidade por cargos."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE por lista de cargos (query)",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "cargos",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "dre_codigo", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        cargos = [int(c) for c in request.query_params.getlist("cargos")]
        if cargos:
            resultado = repository.funcionarios_por_lista_cargos(
                ue_codigo, cargos
            )
        else:
            resultado = repository.funcionarios_por_ue(ue_codigo)
        return Response(resultado)


class FuncionariosFuncaoAtividadeView(APIView):
    """Lista funcionários de uma unidade por função de atividade."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE por função de atividade",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigo_funcao_atividade", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        codigo_funcao_atividade: int | None = None,
    ) -> Response:
        resultado = repository.funcionarios_por_funcao_atividade(
            codigo_ue, codigo_funcao_atividade or 0
        )
        return Response(resultado)


class FuncionariosFuncoesAtividadesQueryView(APIView):
    """Lista funcionários por funções de atividade."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de UE por lista de funções de atividade",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "funcoes_atividades",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "dre_codigo", str, OpenApiParameter.QUERY, required=True
            ),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        funcoes = [
            int(f) for f in request.query_params.getlist("funcoes_atividades")
        ]
        resultado = repository.funcionarios_por_lista_funcoes_atividade(
            ue_codigo, funcoes
        )
        return Response(resultado)


class FuncionariosFuncaoExternaView(APIView):
    """Lista funcionários externos de uma unidade por função."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de uma UE por função externa",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigo_funcao_externa", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: FuncionarioFuncaoExternaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        codigo_funcao_externa: int | None = None,
    ) -> Response:
        resultado = repository.funcionarios_por_funcao_externa(
            codigo_ue, codigo_funcao_externa or 0
        )
        return Response(resultado)


class FuncionariosFuncoesExternasQueryView(APIView):
    """Lista funcionários externos de uma unidade por funções."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionários de UE por lista de funções externas",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "funcoes",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "dre_codigo", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: FuncionarioFuncaoExternaSerializer(many=True)},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        funcoes = [int(f) for f in request.query_params.getlist("funcoes")]
        resultado = repository.funcionarios_por_lista_funcoes_externas(
            ue_codigo, funcoes
        )
        return Response(resultado)


class CargosFuncionarioView(APIView):
    """Lista cargos do funcionário por registro funcional."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter cargos do funcionário por RF",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
        ],
        responses={
            200: FuncionarioUESerializer(many=True),
            400: dict,
            404: dict,
        },
    )
    def get(self, request: Request, registro_funcional: str) -> Response:
        return Response(repository.cargos_funcionario(registro_funcional))


class FuncionarioExternoPorCpfView(APIView):
    """Retorna funcionário externo por CPF."""

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


class NomeServidorView(APIView):
    """Retorna nome e CPF do servidor por registro funcional."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter nome e CPF do servidor por RF",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
        ],
        responses={200: NomeServidorSerializer, 400: dict, 404: dict},
    )
    def get(self, request: Request, registro_funcional: str) -> Response:
        resultado = repository.nome_servidor(registro_funcional)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class DreUeAtribuicaoFuncionarioView(APIView):
    """Retorna unidade de atribuição do funcionário."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter DRE/UE de atribuição do funcionário",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
        ],
        responses={200: DreUeAtribuicaoSerializer, 400: dict, 404: dict},
    )
    def get(self, request: Request, registro_funcional: str) -> Response:
        nome = repository.dre_ue_atribuicao(registro_funcional)
        if nome is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        from django.http import HttpResponse

        return HttpResponse(nome, content_type="text/plain")


class ServidorAtivoView(APIView):
    """Verifica se o servidor está ativo."""

    @extend_schema(
        tags=_TAG_ACESSO,
        summary="Verificar se servidor está ativo",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict, 404: dict},
    )
    def get(self, request: Request, registro_funcional: str) -> Response:
        return Response(repository.servidor_ativo(registro_funcional))


class DreUeAtribuicaoCargoView(APIView):
    """Retorna unidade do funcionário por cargo."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter DRE/UE do funcionário por cargo específico",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_cargo", int, OpenApiParameter.PATH),
        ],
        responses={200: DreUeCargoSerializer, 400: dict, 404: dict},
    )
    def get(
        self,
        request: Request,
        registro_funcional: str,
        codigo_cargo: int,
    ) -> Response:
        resultado = repository.dre_ue_cargo(registro_funcional, codigo_cargo)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class UsuariosSGPView(APIView):
    """Lista usuários SGP por perfil."""

    @extend_schema(
        tags=_TAG_PERFIL,
        summary="Buscar usuários SGP por perfil",
        parameters=[
            OpenApiParameter("id_perfil", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigo_dre", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "codigo_ue", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "codigo_rf", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "nome_servidor", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: UsuarioSGPSerializer(many=True), 400: dict, 404: dict},
    )
    def get(self, request: Request, id_perfil: str) -> Response:
        codigo_dre = request.query_params.get("codigo_dre")
        codigo_ue = request.query_params.get("codigo_ue")
        codigo_rf = request.query_params.get("codigo_rf")
        if repository.perfil_placeholder_invalido(id_perfil) and not codigo_rf:
            mensagem = (
                repository.MENSAGEM_ERRO_LEGADO
                if codigo_dre
                else repository.MENSAGEM_ERRO_PERFIL_SEM_DRE_RF
            )
            return Response(
                mensagem,
                status=status.HTTP_400_BAD_REQUEST,
            )
        resultado = repository.usuarios_sgp_por_perfil(
            id_perfil,
            codigo_dre=codigo_dre,
            codigo_ue=codigo_ue,
            codigo_rf=codigo_rf,
            nome_servidor_param=request.query_params.get("nome_servidor"),
        )
        if not resultado:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class FuncionariosSGPDreView(APIView):
    """Lista funcionários SGP por DRE e perfil."""

    @extend_schema(
        tags=_TAG_PERFIL,
        summary="Buscar funcionários SGP por DRE e perfil",
        parameters=[
            OpenApiParameter("id_perfil", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_dre", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigo_ue", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "codigo_rf", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "nome_servidor", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "codigo_funcao_atividade",
                int,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: UsuarioSGPSerializer(many=True), 400: dict, 404: dict},
    )
    def get(
        self, request: Request, id_perfil: str, codigo_dre: str
    ) -> Response:
        if repository.perfil_placeholder_invalido(id_perfil):
            return Response(
                repository.MENSAGEM_ERRO_LEGADO,
                status=status.HTTP_400_BAD_REQUEST,
            )
        funcao_str = request.query_params.get("codigo_funcao_atividade")
        resultado = repository.funcionarios_sgp_dre(
            id_perfil,
            codigo_dre,
            codigo_ue=request.query_params.get("codigo_ue"),
            codigo_rf=request.query_params.get("codigo_rf"),
            nome_servidor_param=request.query_params.get("nome_servidor"),
            codigo_funcao_atividade=int(funcao_str) if funcao_str else None,
        )
        if not resultado:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class AcessoSondagemView(APIView):
    """Verifica se o professor tem acesso à sondagem."""

    @extend_schema(
        tags=_TAG_ACESSO,
        summary="Verificar se professor tem acesso à sondagem",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: bool},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        return Response(repository.acesso_sondagem(codigo_rf))


class BuscarPorListaRFView(APIView):
    """Lista resumos de funcionários por registros funcionais."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar resumo de funcionários por lista de RF",
        request=list[str],
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        lista = request.data if isinstance(request.data, list) else []
        return Response(repository.buscar_por_lista_rf_func(lista))


class BuscarPorListaLoginView(APIView):
    """Lista resumos de funcionários por logins."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar resumo de funcionários por lista de login",
        request=list,
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        lista = request.data if isinstance(request.data, list) else []
        return Response(repository.buscar_por_lista_login(lista))
