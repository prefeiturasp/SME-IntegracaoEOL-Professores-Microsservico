"""Views mock do domínio Turmas (EP-24)."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

_TAG_TURMAS = ["Turmas"]

_MOCK_TURMAS_HISTORICAS = [
    {
        "codigoTurma": 2112345,
        "nomeTurma": "1A - Manhã",
        "codigoEscola": "000532",
        "anoLetivo": 2024,
        "status": "A",
    },
    {
        "codigoTurma": 2112300,
        "nomeTurma": "2B - Tarde",
        "codigoEscola": "000532",
        "anoLetivo": 2023,
        "status": "E",
    },
]


class TurmasHistoricasAnoProfessorView(APIView):
    """EP-24 — Buscar turmas históricas do professor por ano."""

    @extend_schema(
        tags=_TAG_TURMAS,
        summary="EP-24 | Buscar turmas históricas do professor por ano",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter("professorRf", str, OpenApiParameter.PATH),
        ],
        responses={200: list, 400: dict, 404: dict},
    )
    def get(
        self,
        request: Request,
        ano_letivo: int,
        professor_rf: str,
    ) -> Response:
        """Retorna lista mock de turmas históricas."""
        return Response(_MOCK_TURMAS_HISTORICAS)
