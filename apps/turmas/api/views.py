"""Views do domínio Turmas (EP-24)."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.turmas import repository
from apps.turmas.serializers import TurmaHistoricaSerializer

_TAG_TURMAS = ["Turmas"]


class TurmasHistoricasAnoProfessorView(APIView):
    """EP-24 — Buscar turmas históricas do professor por ano."""

    @extend_schema(
        tags=_TAG_TURMAS,
        summary="Buscar turmas históricas do professor por ano",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter("professorRf", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaHistoricaSerializer(many=True), 400: dict, 404: dict},
    )
    def get(
        self,
        request: Request,
        ano_letivo: int,
        professor_rf: str,
    ) -> Response:
        resultado = repository.turmas_historicas_professor(ano_letivo, professor_rf)
        return Response(resultado)
