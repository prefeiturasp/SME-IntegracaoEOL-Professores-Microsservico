"""Views do domínio Professores (EP-01 a EP-23)."""

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


# ---------------------------------------------------------------------------
# EP-01 / EP-02 — Professores de escola / Turmas atribuídas (escola+ano)
# ---------------------------------------------------------------------------


class BuscaProfessoresView(APIView):
    """EP-01 — Buscar professores de uma escola por ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professores de uma escola por ano letivo",
        parameters=[
            OpenApiParameter("codigoEolEscola", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        responses={200: ProfessorEscolaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoEolEscola: str,
        anoLetivo: int | None = None,
    ) -> Response:
        resultado = repository.buscar_professores_escola(
            codigoEolEscola, anoLetivo or 0
        )
        return Response(resultado)


class BuscaTurmasAtribuidasEscolaView(APIView):
    """EP-02 — Turmas atribuídas ao professor em uma escola e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas ao professor (escola + ano)",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoEolEscola", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        responses={200: TurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoEolEscola: str,
        anoLetivo: int,
        codigoRF: str | None = None,
    ) -> Response:
        resultado = repository.buscar_turmas_professor_escola_ano(
            codigoRF or "", codigoEolEscola, anoLetivo
        )
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-03 / EP-04 — Turmas do professor (todas / por ano)
# ---------------------------------------------------------------------------


class BuscarTurmasAtribuidasView(APIView):
    """EP-03/04 — Todas as turmas atribuídas ao professor."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas ao professor (todas)",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoRF: str,
        anoLetivo: int | None = None,
    ) -> Response:
        if anoLetivo is not None:
            resultado = repository.buscar_turmas_professor_ano(codigoRF, anoLetivo)
        else:
            resultado = repository.buscar_turmas_professor(codigoRF)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-05 — Nome pelo RF
# ---------------------------------------------------------------------------


class ObterNomePeloRFView(APIView):
    """EP-05 — Obter nome do professor pelo RF."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Obter nome do professor pelo RF",
        parameters=[
            OpenApiParameter("rfProfessor", str, OpenApiParameter.PATH),
        ],
        responses={200: NomePorRFSerializer, 404: dict},
    )
    def get(self, request: Request, rfProfessor: str) -> Response:
        nome = repository.obter_nome_rf(rfProfessor)
        if nome is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        from django.http import HttpResponse
        return HttpResponse(nome, content_type="text/plain")


# ---------------------------------------------------------------------------
# EP-06 / EP-07 — BuscarPorRf e BuscarPorRfDreUe
# ---------------------------------------------------------------------------


class BuscarPorRfAnoLetivoView(APIView):
    """EP-06 — Buscar professor por RF e ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor por RF e ano letivo",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "buscarOutrosCargos", bool, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: ProfessorPerfilSerializer, 404: dict},
    )
    def get(self, request: Request, codigoRf: str, anoLetivo: int) -> Response:
        resultado = repository.buscar_por_rf_ano(codigoRf, anoLetivo)
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


class BuscarPorRfDreUeView(APIView):
    """EP-07 — Buscar professor por RF, DRE e UE."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor por RF, DRE e UE",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter("dreId", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("ueId", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter(
                "buscarOutrosCargos", bool, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: ProfessorPerfilSerializer, 404: dict},
    )
    def get(self, request: Request, codigoRf: str, anoLetivo: int) -> Response:
        resultado = repository.buscar_por_rf_dre_ue(
            codigoRf,
            anoLetivo,
            dre_id=request.query_params.get("dreId"),
            ue_id=request.query_params.get("ueId"),
        )
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-08 — AutoComplete
# ---------------------------------------------------------------------------


class AutoCompleteView(APIView):
    """EP-08 — AutoComplete de professores por DRE e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="AutoComplete de professores por DRE e ano",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter("dreId", str, OpenApiParameter.PATH),
            OpenApiParameter("ueId", str, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("nome", str, OpenApiParameter.QUERY, required=False),
        ],
        responses={200: AutoCompleteSerializer(many=True)},
    )
    def get(self, request: Request, anoLetivo: int, dreId: str) -> Response:
        resultado = repository.autocomplete_professores(
            anoLetivo,
            dreId,
            ue_id=request.query_params.get("ueId"),
            nome=request.query_params.get("nome"),
        )
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-09 — BuscarPorListaRF (POST)
# ---------------------------------------------------------------------------


class BuscarPorListaRFView(APIView):
    """EP-09 — Buscar professores por lista de RF e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professores por lista de RF e ano (POST)",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        request=list,
        responses={200: ResumoSerializer(many=True)},
    )
    def post(self, request: Request, anoLetivo: int) -> Response:
        lista_rf = request.data if isinstance(request.data, list) else []
        resultado = repository.buscar_por_lista_rf(anoLetivo, lista_rf)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-10 — Validade do professor
# ---------------------------------------------------------------------------


class VerificarValidadeView(APIView):
    """EP-10 — Verificar validade do professor."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar validade do professor",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
        ],
        responses={200: bool},
    )
    def get(self, request: Request, codigoRf: str) -> Response:
        return Response(repository.verificar_validade(codigoRf))


# ---------------------------------------------------------------------------
# EP-11 — EhEmei
# ---------------------------------------------------------------------------


class EhEmeiView(APIView):
    """EP-11 — Verificar se professor é EMEI."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar se professor é EMEI",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict},
    )
    def get(self, request: Request, codigoRF: str) -> Response:
        return Response(repository.eh_emei(codigoRF))


# ---------------------------------------------------------------------------
# EP-12 — Status de atribuição na turma
# ---------------------------------------------------------------------------


class AtribuicaoStatusView(APIView):
    """EP-12 — Verificar atribuição na turma (status)."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar status de atribuição na turma",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
        ],
        responses={200: AtribuicaoStatusSerializer, 422: dict, 500: dict},
    )
    def get(self, request: Request, codigoRF: str, codigoTurma: int) -> Response:
        return Response(repository.atribuicao_status(codigoRF, codigoTurma))


# ---------------------------------------------------------------------------
# EP-13 — Atribuição na turma em data
# ---------------------------------------------------------------------------


class AtribuicaoVerificarDataView(APIView):
    """EP-13 — Verificar atribuição na turma em uma data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição na turma em data",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataConsulta", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(self, request: Request, codigoRF: str, codigoTurma: int) -> Response:
        data_str = request.query_params.get("dataConsulta")
        data: date | None = date.fromisoformat(data_str) if data_str else None
        return Response(
            repository.atribuicao_verificar_data(codigoRF, codigoTurma, data)
        )


# ---------------------------------------------------------------------------
# EP-14 — Atribuição na disciplina/turma em data
# ---------------------------------------------------------------------------


class AtribuicaoDisciplinaDataView(APIView):
    """EP-14 — Verificar atribuição na disciplina/turma em data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição na disciplina/turma em data",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataConsulta", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "territorioSaber", bool, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self,
        request: Request,
        codigoRF: str,
        codigoTurma: int,
        disciplinaId: int,
    ) -> Response:
        data_str = request.query_params.get("dataConsulta")
        data: date | None = date.fromisoformat(data_str) if data_str else None
        territorio = request.query_params.get("territorioSaber", "").lower() == "true"
        return Response(
            repository.atribuicao_disciplina_data(
                codigoRF, codigoTurma, disciplinaId, data, territorio
            )
        )


# ---------------------------------------------------------------------------
# EP-15 — Atribuição via dataTick
# ---------------------------------------------------------------------------


class AtribuicaoDisciplinaDataTickView(APIView):
    """EP-15 — Verificar atribuição na disciplina/turma via dataTick."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição na disciplina/turma via dataTick",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataConsultaTick", int, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self,
        request: Request,
        codigoRF: str,
        codigoTurma: int,
        disciplinaId: int,
    ) -> Response:
        tick_str = request.query_params.get("dataConsultaTick")
        tick = int(tick_str) if tick_str else None
        return Response(
            repository.atribuicao_disciplina_datatick(
                codigoRF, codigoTurma, disciplinaId, tick
            )
        )


# ---------------------------------------------------------------------------
# EP-16 — Recorrência de datas (array de ticks)
# ---------------------------------------------------------------------------


class AtribuicaoRecorrenciaDatasView(APIView):
    """EP-16 — Verificar atribuição em recorrência de datas."""

    @extend_schema(
        tags=_TAG_PROF,
        summary=(
            "Verificar atribuição na disciplina/turma"
            " em recorrência de datas"
        ),
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataTicks", int, OpenApiParameter.QUERY, required=False, many=True
            ),
        ],
        responses={200: AtribuicaoDataSerializer(many=True), 400: dict, 422: dict, 500: dict},
    )
    def get(
        self,
        request: Request,
        codigoRF: str,
        codigoTurma: int,
        disciplinaId: int,
    ) -> Response:
        ticks = [int(t) for t in request.query_params.getlist("dataTicks")]
        return Response(
            repository.atribuicao_recorrencia_datas(
                codigoRF, codigoTurma, disciplinaId, ticks
            )
        )


# ---------------------------------------------------------------------------
# EP-17 — Verificar atribuição em lista de turmas (POST)
# ---------------------------------------------------------------------------


class AtribuicaoTurmasListaView(APIView):
    """EP-17 — Verificar atribuição em turmas por disciplina (POST)."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição em turmas por disciplina (POST)",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
        ],
        request=list,
        responses={200: AtribuicaoTurmaSerializer(many=True)},
    )
    def post(self, request: Request, codigoRf: str, disciplinaId: int) -> Response:
        codigos_turma = request.data if isinstance(request.data, list) else []
        return Response(
            repository.atribuicao_turmas_lista(codigoRf, disciplinaId, codigos_turma)
        )


# ---------------------------------------------------------------------------
# EP-18 — Atribuição em período (POST)
# ---------------------------------------------------------------------------


class AtribuicaoPeriodoView(APIView):
    """EP-18 — Verificar atribuição do professor em período."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição do professor em período (POST)",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("componenteCurricularId", int, OpenApiParameter.PATH),
            OpenApiParameter("dataInicioPeriodo", str, OpenApiParameter.PATH),
            OpenApiParameter("dataFimPeriodo", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def post(
        self,
        request: Request,
        codigoRf: str,
        codigoTurma: int,
        componenteCurricularId: int,
        dataInicioPeriodo: str,
        dataFimPeriodo: str,
    ) -> Response:
        return Response(
            repository.atribuicao_periodo(
                codigoRf,
                codigoTurma,
                componenteCurricularId,
                date.fromisoformat(dataInicioPeriodo),
                date.fromisoformat(dataFimPeriodo),
            )
        )


# ---------------------------------------------------------------------------
# EP-19 — Professores atribuídos a turma/disciplina em data
# ---------------------------------------------------------------------------


class ObterProfessoresAtribuidosTurmaDiscView(APIView):
    """EP-19 — Obter professores atribuídos a turma/disciplina em data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Obter professores atribuídos a turma/disciplina em data",
        parameters=[
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataTicks", int, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={
            200: ProfessorAtribuidoTurmaDiscSerializer(many=True),
            400: dict,
            422: dict,
            500: dict,
        },
    )
    def get(self, request: Request, codigoTurma: int, disciplinaId: int) -> Response:
        tick_str = request.query_params.get("dataTicks")
        tick = int(tick_str) if tick_str else None
        return Response(
            repository.professores_atribuidos_turma_disc(
                codigoTurma, disciplinaId, tick
            )
        )


# ---------------------------------------------------------------------------
# EP-20 — Titular por turma e disciplina
# ---------------------------------------------------------------------------


class TitularPorTurmaDisciplinaView(APIView):
    """EP-20 — Buscar professor titular por turma e disciplina."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professor titular por turma e disciplina",
        parameters=[
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigoComponenteCurricular", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: TitularSerializer, 404: dict},
    )
    def get(
        self,
        request: Request,
        codigoTurma: int,
        codigoComponenteCurricular: int,
    ) -> Response:
        resultado = repository.titular_por_turma_disciplina(
            codigoTurma, codigoComponenteCurricular
        )
        if resultado is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(resultado)


# ---------------------------------------------------------------------------
# EP-21 — Titulares por lista de turmas
# ---------------------------------------------------------------------------


class TitularesPorTurmasView(APIView):
    """EP-21 — Buscar professores titulares por lista de turmas."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por lista de turmas",
        parameters=[
            OpenApiParameter(
                "codigosTurmas",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ],
        responses={200: TitularPorTurmaSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        codigos = [int(c) for c in request.query_params.getlist("codigosTurmas")]
        return Response(repository.titulares_por_turmas(codigos))


# ---------------------------------------------------------------------------
# EP-22 — Titulares por turma com agrupamento
# ---------------------------------------------------------------------------


class TitularesPorTurmaAgrupamentoView(APIView):
    """EP-22 — Buscar professores titulares por turma com agrupamento."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por turma com agrupamento",
        parameters=[
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("realizaAgrupamento", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigoRF", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "dataReferencia", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: TitularAgrupamentoSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigoTurma: int,
        realizaAgrupamento: str,
    ) -> Response:
        agrupamento = realizaAgrupamento.lower() == "true"
        data_str = request.query_params.get("dataReferencia")
        data: date | None = date.fromisoformat(data_str) if data_str else None
        return Response(
            repository.titulares_por_turma_agrupamento(
                codigoTurma,
                agrupamento,
                codigo_rf=request.query_params.get("codigoRF"),
                data_referencia=data,
            )
        )


# ---------------------------------------------------------------------------
# EP-23 — Titulares por UE e data de referência
# ---------------------------------------------------------------------------


class TitularesPorUeView(APIView):
    """EP-23 — Buscar professores titulares por UE e data de referência."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por UE e data de referência",
        parameters=[
            OpenApiParameter("ueCodigo", str, OpenApiParameter.PATH),
            OpenApiParameter("dataReferencia", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "realizaAgrupamento",
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
        ueCodigo: str,
        dataReferencia: str,
    ) -> Response:
        agrupamento = (
            request.query_params.get("realizaAgrupamento", "").lower() == "true"
        )
        return Response(
            repository.titulares_por_ue(
                ueCodigo,
                date.fromisoformat(dataReferencia),
                realiza_agrupamento=agrupamento,
            )
        )
