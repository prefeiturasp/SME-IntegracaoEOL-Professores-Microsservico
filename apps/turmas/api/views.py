"""Views do domínio de turmas."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.turmas import repository

_TAG_TURMAS = ["Turmas"]


class TurmasHistoricasAnoProfessorView(APIView):
    """Lista códigos de turma históricos do professor por ano."""

    @extend_schema(
        tags=_TAG_TURMAS,
        summary="Buscar códigos de turma históricos do professor por ano",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("professor_rf", str, OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def get(
        self,
        request: Request,
        ano_letivo: int,
        professor_rf: str,
    ) -> Response:
        """Lista códigos de turma históricos do professor por ano.

        Args:
            request: Requisição HTTP recebida pela API.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
            professor_rf: Registro funcional do professor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        codigos = repository.turmas_historicas_professor(
            ano_letivo, professor_rf
        )
        if not codigos:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(codigos)
