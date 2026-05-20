"""Views do domínio de professores."""

from datetime import date

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.professores import repository
from apps.professores.serializers import (
    AtribuicaoDataSerializer,
    AtribuicaoStatusSerializer,
    AtribuicaoTurmaSerializer,
    AutoCompleteSerializer,
    NomePorRFSerializer,
    ProfessorAtribuidoTurmaDiscSerializer,
    ProfessorEscolaSerializer,
    ProfessorPerfilSerializer,
    ResumoSerializer,
    TitularAgrupamentoSerializer,
    TitularPorTurmaSerializer,
    TitularSerializer,
    TurmaAtribuidaSerializer,
)

_TAG_PROF = ["Professores"]
_TAG_TITULAR = ["Professores Titulares"]


class BuscaProfessoresView(APIView):
    """Lista professores de uma escola."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professores de uma escola sem ano letivo",
        parameters=[
            OpenApiParameter("codigo_eol_escola", str, OpenApiParameter.PATH),
        ],
        responses={200: ProfessorEscolaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
    ) -> Response:
        resultado = repository.buscar_professores_escola(codigo_eol_escola, 0)
        return Response(resultado)


class BuscaProfessoresAnoLetivoView(APIView):
    """Lista professores de uma escola por ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professores de uma escola por ano letivo",
        parameters=[
            OpenApiParameter("codigo_eol_escola", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        responses={200: ProfessorEscolaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
        ano_letivo: int,
    ) -> Response:
        resultado = repository.buscar_professores_escola(
            codigo_eol_escola, ano_letivo
        )
        return Response(resultado)


class BuscaTurmasAtribuidasEscolaView(APIView):
    """Lista turmas atribuídas em uma escola e ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas por escola e ano",
        parameters=[
            OpenApiParameter("codigo_eol_escola", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        responses={200: TurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
        ano_letivo: int,
    ) -> Response:
        resultado = repository.buscar_turmas_professor_escola_ano(
            "", codigo_eol_escola, ano_letivo
        )
        return Response(resultado)


class BuscaTurmasAtribuidasProfessorEscolaView(APIView):
    """Lista turmas atribuídas ao professor em uma escola."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas ao professor (escola + ano)",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_eol_escola", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        responses={200: TurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
        ano_letivo: int,
        codigo_rf: str | None = None,
    ) -> Response:
        resultado = repository.buscar_turmas_professor_escola_ano(
            codigo_rf or "", codigo_eol_escola, ano_letivo
        )
        return Response(resultado)


class BuscarTurmasAtribuidasView(APIView):
    """Lista turmas atribuídas ao professor."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas ao professor (todas)",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        ano_letivo: int | None = None,
    ) -> Response:
        if ano_letivo is not None:
            resultado = repository.buscar_turmas_professor_ano(
                codigo_rf, ano_letivo
            )
        else:
            resultado = repository.buscar_turmas_professor(codigo_rf)
        return Response(resultado)


class ObterNomePeloRFView(APIView):
    """Retorna o nome do professor pelo registro funcional."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Obter nome do professor pelo RF",
        parameters=[
            OpenApiParameter("rf_professor", str, OpenApiParameter.PATH),
        ],
        responses={200: NomePorRFSerializer, 404: dict},
    )
    def get(self, request: Request, rf_professor: str) -> Response:
        nome = repository.obter_nome_rf(rf_professor)
        if nome is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        from django.http import HttpResponse

        return HttpResponse(nome, content_type="text/plain")


class BuscarPorRfAnoLetivoView(APIView):
    """Retorna dados do professor por registro funcional e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor por RF e ano letivo",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "buscar_outros_cargos",
                bool,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: ProfessorPerfilSerializer, 404: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        resultado = repository.buscar_por_rf_ano(codigo_rf, ano_letivo)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class BuscarPorRfDreUeView(APIView):
    """Retorna dados do professor por registro funcional."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor por RF, DRE e UE",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dre_id", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "ue_id", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "buscar_outros_cargos",
                bool,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: ProfessorPerfilSerializer, 404: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        resultado = repository.buscar_por_rf_dre_ue(codigo_rf)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class AutoCompleteView(APIView):
    """Lista professores para autocomplete por DRE e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="AutoComplete de professores por DRE e ano",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("dre_id", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "ue_id", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "nome", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: AutoCompleteSerializer(many=True)},
    )
    def get(self, request: Request, ano_letivo: int, dre_id: str) -> Response:
        resultado = repository.autocomplete_professores(
            ano_letivo,
            dre_id,
            ue_id=request.query_params.get("ue_id"),
            nome=request.query_params.get("nome"),
        )
        return Response(resultado)


class BuscarPorListaRFView(APIView):
    """Lista professores por registros funcionais e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professores por lista de RF e ano",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        request=list[str],
        responses={200: ResumoSerializer(many=True)},
    )
    def post(self, request: Request, ano_letivo: int) -> Response:
        lista_rf: list[str] = request.data if isinstance(request.data, list) else []
        resultado = repository.buscar_por_lista_rf(ano_letivo, lista_rf)
        return Response(resultado)


class VerificarValidadeView(APIView):
    """Verifica se o professor possui vínculo válido."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar validade do professor",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: bool},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        return Response(repository.verificar_validade(codigo_rf))


class EhEmeiView(APIView):
    """Verifica se o professor está vinculado a EMEI."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar se professor é EMEI",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        return Response(repository.eh_emei(codigo_rf))


class AtribuicaoStatusView(APIView):
    """Verifica atribuição do professor na turma."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar status de atribuição na turma",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
        ],
        responses={200: AtribuicaoStatusSerializer, 422: dict, 500: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, codigo_turma: int
    ) -> Response:
        return Response(repository.atribuicao_status(codigo_rf, codigo_turma))


class AtribuicaoVerificarDataView(APIView):
    """Verifica atribuição do professor na turma em uma data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição na turma em data",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_consulta", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, codigo_turma: int
    ) -> Response:
        data_str = request.query_params.get("data_consulta")
        data: date | None = date.fromisoformat(data_str) if data_str else None
        return Response(
            repository.atribuicao_verificar_data(codigo_rf, codigo_turma, data)
        )


class AtribuicaoDisciplinaDataView(APIView):
    """Verifica atribuição do professor na disciplina em uma data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição na disciplina/turma em data",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_consulta", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "territorio_saber",
                bool,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: int,
        disciplina_id: int,
    ) -> Response:
        data_str = request.query_params.get("data_consulta")
        data: date | None = date.fromisoformat(data_str) if data_str else None
        territorio = (
            request.query_params.get("territorio_saber", "").lower() == "true"
        )
        return Response(
            repository.atribuicao_disciplina_data(
                codigo_rf, codigo_turma, disciplina_id, data, territorio
            )
        )


class AtribuicaoDisciplinaDataTickView(APIView):
    """Verifica atribuição do professor usando data em ticks."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição na disciplina/turma via dataTick",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_consulta_tick",
                int,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: int,
        disciplina_id: int,
    ) -> Response:
        tick_str = request.query_params.get("data_consulta_tick")
        if not tick_str:
            return Response(
                {"detail": "Deve ser informada uma data valida"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            repository.atribuicao_disciplina_datatick(
                codigo_rf, codigo_turma, disciplina_id, int(tick_str)
            )
        )


class AtribuicaoRecorrenciaDatasView(APIView):
    """Lista resultados de atribuição para datas recorrentes."""

    @extend_schema(
        tags=_TAG_PROF,
        summary=(
            "Verificar atribuição na disciplina/turma"
            " em recorrência de datas"
        ),
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_ticks",
                int,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
            ),
        ],
        responses={
            200: AtribuicaoDataSerializer(many=True),
            400: dict,
            422: dict,
            500: dict,
        },
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: int,
        disciplina_id: int,
    ) -> Response:
        ticks = [int(t) for t in request.query_params.getlist("data_ticks")]
        if not ticks:
            return Response(
                {"detail": "É necessário informar as datas em ticks!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            repository.atribuicao_recorrencia_datas(
                codigo_rf, codigo_turma, disciplina_id, ticks
            )
        )


class AtribuicaoTurmasListaView(APIView):
    """Lista resultados de atribuição em turmas por disciplina."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição em turmas por disciplina",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
        ],
        request=list,
        responses={200: AtribuicaoTurmaSerializer(many=True)},
    )
    def post(
        self, request: Request, codigo_rf: str, disciplina_id: int
    ) -> Response:
        codigos_turma = request.data if isinstance(request.data, list) else []
        return Response(
            repository.atribuicao_turmas_lista(
                codigo_rf, disciplina_id, codigos_turma
            )
        )


class AtribuicaoPeriodoView(APIView):
    """Verifica atribuição do professor em período."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição do professor em período",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "componente_curricular_id", int, OpenApiParameter.PATH
            ),
            OpenApiParameter(
                "data_inicio_periodo", str, OpenApiParameter.PATH
            ),
            OpenApiParameter("data_fim_periodo", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def post(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: int,
        componente_curricular_id: int,
        data_inicio_periodo: str,
        data_fim_periodo: str,
    ) -> Response:
        return Response(
            repository.atribuicao_periodo(
                codigo_rf,
                codigo_turma,
                componente_curricular_id,
                date.fromisoformat(data_inicio_periodo),
                date.fromisoformat(data_fim_periodo),
            )
        )


class ObterProfessoresAtribuidosTurmaDiscView(APIView):
    """Lista professores atribuídos a turma e disciplina em data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Obter professores atribuídos a turma/disciplina em data",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_ticks", int, OpenApiParameter.QUERY, required=True
            ),
        ],
        responses={
            200: ProfessorAtribuidoTurmaDiscSerializer(many=True),
            400: dict,
            422: dict,
            500: dict,
        },
    )
    def get(
        self, request: Request, codigo_turma: int, disciplina_id: int
    ) -> Response:
        tick_str = request.query_params.get("data_ticks")
        if not tick_str:
            return Response(
                {"detail": "Deve ser informada uma data válida"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            repository.professores_atribuidos_turma_disc(
                codigo_turma, disciplina_id, int(tick_str)
            )
        )


class TitularPorTurmaDisciplinaView(APIView):
    """Retorna professor titular por turma e disciplina."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professor titular por turma e disciplina",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigo_componente_curricular", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: TitularSerializer, 404: dict},
    )
    def get(
        self,
        request: Request,
        codigo_turma: int,
        codigo_componente_curricular: int,
    ) -> Response:
        resultado = repository.titular_por_turma_disciplina(
            codigo_turma, codigo_componente_curricular
        )
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class TitularesPorTurmasView(APIView):
    """Lista professores titulares por turmas."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por lista de turmas",
        parameters=[
            OpenApiParameter(
                "codigos_turmas",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ],
        responses={200: TitularPorTurmaSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        codigos = [
            int(c) for c in request.query_params.getlist("codigos_turmas")
        ]
        return Response(repository.titulares_por_turmas(codigos))


class TitularesPorTurmaAgrupamentoView(APIView):
    """Lista professores titulares por turma com agrupamento."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por turma com agrupamento",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "realiza_agrupamento", str, OpenApiParameter.PATH
            ),
            OpenApiParameter(
                "codigo_rf", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "data_referencia", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: TitularAgrupamentoSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_turma: int,
        realiza_agrupamento: str,
    ) -> Response:
        agrupamento = realiza_agrupamento.lower() == "true"
        data_str = request.query_params.get("data_referencia")
        data: date | None = date.fromisoformat(data_str) if data_str else None
        return Response(
            repository.titulares_por_turma_agrupamento(
                codigo_turma,
                agrupamento,
                codigo_rf=request.query_params.get("codigo_rf"),
                data_referencia=data,
            )
        )


class TitularesPorUeView(APIView):
    """Lista professores titulares por unidade e data de referência."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por UE e data de referência",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter("data_referencia", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "realiza_agrupamento",
                bool,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: TitularAgrupamentoSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        ue_codigo: str,
        data_referencia: str,
    ) -> Response:
        return Response(
            repository.titulares_por_ue(
                ue_codigo,
                date.fromisoformat(data_referencia),
            )
        )
