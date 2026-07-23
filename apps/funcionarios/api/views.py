"""Views do domínio de funcionários."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.funcionarios import services
from apps.funcionarios.serializers import (
    DreUeCargoSerializer,
    FuncionarioExternoCpfSerializer,
    FuncionarioFuncaoExternaSerializer,
    FuncionariosUEFiltroSerializer,
    FuncionariosUEQuerySerializer,
    FuncionarioUESerializer,
    NomeCPFServidorSerializer,
    ResumoFuncionarioSerializer,
    SupervisoresFiltroSerializer,
    SupervisorSerializer,
    UsuarioSGPSerializer,
)

_TAG_FUNC = ["Funcionarios"]
_TAG_ESCOLA_FUNC = ["FuncionariosUnidadeEducacional"]
_TAG_PERFIL = ["Perfis SGP"]
_TAG_ACESSO = ["Acessos"]


class FuncionariosPorUEView(APIView):
    """Lista funcionários de uma unidade educacional."""

    @extend_schema(
        tags=_TAG_ESCOLA_FUNC,
        summary="Funcionarios de uma UE",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "cargos",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "funcoes_atividades",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "funcoes_externas",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ],
        responses={200: FuncionarioUESerializer(many=True), 400: dict},
    )
    def get(self, request: Request, codigo_ue: str) -> Response:
        """Lista funcionários de uma unidade educacional.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_ue: Código EOL da unidade educacional consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        serializer = FuncionariosUEQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        resultado = services.funcionarios_por_ue(
            codigo_ue,
            filtros=serializer.validated_data,
        )
        return Response(resultado)


class FuncionariosUEView(APIView):
    """Lista funcionários ativos de uma unidade educacional."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Funcionários ativos de uma UE",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
        ],
        request=FuncionariosUEFiltroSerializer,
        responses={200: FuncionarioUESerializer(many=True), 400: dict},
    )
    def post(self, request: Request, codigo_ue: str) -> Response:
        """Lista funcionários ativos de uma unidade educacional.

        O campo de login depende da Identidade para indicar se o
        funcionário possui usuário vinculado.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_ue: Código EOL da unidade educacional consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        serializer = FuncionariosUEFiltroSerializer(data=request.data or {})
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        resultado = services.funcionarios_ue(
            codigo_ue,
            filtros={},
            codigos_rfs=serializer.validated_data["codigosRfs"],
            filtro=serializer.validated_data["filtro"],
        )
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
        """Lista funcionários de uma unidade por cargos.

        Args:
            request: Requisição HTTP recebida pela API.
            ue_codigo: Código EOL da unidade educacional consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionarios_por_lista_cargos(
            ue_codigo,
            request.query_params.getlist("cargos"),
        )
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
        """Lista funcionários de uma unidade por função de atividade.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_ue: Código EOL da unidade educacional consultada.
            codigo_funcao_atividade: Código da função de atividade filtrada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionarios_por_funcao_atividade(
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
        """Lista funcionários por funções de atividade.

        Args:
            request: Requisição HTTP recebida pela API.
            ue_codigo: Código EOL da unidade educacional consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionarios_por_lista_funcoes_atividade(
            ue_codigo,
            request.query_params.getlist("funcoes_atividades"),
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
        """Lista funcionários externos de uma unidade por função.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_ue: Código EOL da unidade educacional consultada.
            codigo_funcao_externa: Código da função externa usada no filtro.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionarios_por_funcao_externa(
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
        """Lista funcionários externos de uma unidade por funções.

        Args:
            request: Requisição HTTP recebida pela API.
            ue_codigo: Código EOL da unidade educacional consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionarios_por_lista_funcoes_externas(
            ue_codigo,
            request.query_params.getlist("funcoes"),
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
        """Lista cargos do funcionário por registro funcional.

        Args:
            request: Requisição HTTP recebida pela API.
            registro_funcional: Registro funcional do servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.cargos_funcionario(registro_funcional))


class FuncionariosPorCargoView(APIView):
    """Lista funcionários ativos por cargo."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Funcionários ativos por cargo",
        parameters=[
            OpenApiParameter("codigo_cargo", int, OpenApiParameter.PATH),
        ],
        responses={200: FuncionarioUESerializer(many=True)},
    )
    def get(self, request: Request, codigo_cargo: int) -> Response:
        """Lista funcionários ativos por cargo.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_cargo: Código do cargo consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.funcionarios_por_cargo(codigo_cargo))


class SupervisoresPorDreView(APIView):
    """Lista supervisores vinculados à DRE."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Supervisores por DRE",
        parameters=[
            OpenApiParameter("codigo_dre", str, OpenApiParameter.PATH),
        ],
        request=SupervisoresFiltroSerializer,
        responses={200: SupervisorSerializer(many=True), 400: dict},
    )
    def post(self, request: Request, codigo_dre: str) -> Response:
        """Lista supervisores vinculados à DRE.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_dre: Código EOL da DRE consultada.

        Returns:
            Resposta HTTP com os supervisores encontrados.
        """
        serializer = SupervisoresFiltroSerializer(
            data={"codigos_rfs": request.data or []}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            services.supervisores_por_dre(
                codigo_dre,
                serializer.validated_data["codigos_rfs"],
            )
        )


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
        """Retorna funcionário externo por CPF.

        Args:
            request: Requisição HTTP recebida pela API.
            cpf: CPF do funcionário externo consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionario_externo_por_cpf(cpf)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class NomeCPFServidorView(APIView):
    """Retorna nome e CPF do servidor por registro funcional."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter nome e CPF do servidor por RF",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
        ],
        responses={200: NomeCPFServidorSerializer, 400: dict, 404: dict},
    )
    def get(self, request: Request, registro_funcional: str) -> Response:
        """Retorna nome e CPF do servidor por registro funcional.

        Args:
            request: Requisição HTTP recebida pela API.
            registro_funcional: Registro funcional do servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.nome_cpf_servidor(registro_funcional)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class NomeUsuarioEOLView(APIView):
    """Retorna nome usuario EOL do servidor."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Obter nome usuario EOL do servidor por RF",
        parameters=[
            OpenApiParameter("registro_funcional", str, OpenApiParameter.PATH),
        ],
        responses={200: str, 400: dict, 404: dict},
    )
    def get(self, request: Request, registro_funcional: str) -> Response:
        """Retorna nome usuario EOL do servidor.

        Args:
            request: Requisição HTTP recebida pela API.
            registro_funcional: Registro funcional do servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        nome = services.nome_servidor(registro_funcional)
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
        """Verifica se o servidor está ativo.

        Args:
            request: Requisição HTTP recebida pela API.
            registro_funcional: Registro funcional do servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.servidor_ativo(registro_funcional))


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
        """Retorna unidade do funcionário por cargo.

        Args:
            request: Requisição HTTP recebida pela API.
            registro_funcional: Registro funcional do servidor consultado.
            codigo_cargo: Código do cargo usado para localizar a atribuição.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.dre_ue_cargo(registro_funcional, codigo_cargo)
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
        """Lista usuários SGP por perfil.

        Args:
            request: Requisição HTTP recebida pela API.
            id_perfil: Identificador do perfil SGP usado na consulta.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.usuarios_sgp_por_perfil(
            id_perfil,
            codigo_dre=request.query_params.get("codigo_dre"),
            codigo_ue=request.query_params.get("codigo_ue"),
            codigo_rf=request.query_params.get("codigo_rf"),
            nome_servidor=request.query_params.get("nome_servidor"),
        )
        if resultado.status_code == status.HTTP_404_NOT_FOUND:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado.payload, status=resultado.status_code)


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
        """Lista funcionários SGP por DRE e perfil.

        Args:
            request: Requisição HTTP recebida pela API.
            id_perfil: Identificador do perfil SGP usado na consulta.
            codigo_dre: Código EOL da DRE usada para filtrar funcionários.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.funcionarios_sgp_dre(
            id_perfil,
            codigo_dre,
            codigo_ue=request.query_params.get("codigo_ue"),
            codigo_rf=request.query_params.get("codigo_rf"),
            nome_servidor=request.query_params.get("nome_servidor"),
            codigo_funcao_atividade=request.query_params.get(
                "codigo_funcao_atividade"
            ),
        )
        if resultado.status_code == status.HTTP_404_NOT_FOUND:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado.payload, status=resultado.status_code)


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
        """Verifica se o professor tem acesso à sondagem.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.acesso_sondagem(codigo_rf))


class BuscarPorListaRFView(APIView):
    """Lista resumos de funcionários por registros funcionais."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar resumo de funcionários por lista de RF",
        request=list[str],
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Lista resumos de funcionários por registros funcionais.

        Args:
            request: Requisição HTTP recebida pela API.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.buscar_por_lista_rf(request.data))


class BuscarPorListaLoginView(APIView):
    """Lista resumos de funcionários por logins."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar resumo de funcionários por lista de login",
        request=list,
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Lista resumos de funcionários por logins.

        Args:
            request: Requisição HTTP recebida pela API.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.buscar_por_lista_login(request.data))


class BuscarFuncionariosView(APIView):
    """Lista funcionários por filtros básicos."""

    @extend_schema(
        tags=_TAG_FUNC,
        summary="Buscar funcionários por filtros básicos",
        request=dict,
        responses={200: ResumoFuncionarioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Lista funcionários por filtros básicos.

        Args:
            request: Requisição HTTP recebida pela API.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.buscar_funcionarios(request.data))
