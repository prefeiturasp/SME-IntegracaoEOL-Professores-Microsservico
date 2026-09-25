"""Views do domínio de cargos."""

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cargos import services
from apps.cargos.serializers import CargoSerializer

_TAG_CARGOS = ["Cargos"]


class CargosView(APIView):
    """Lista cargos ativos cadastrados no EOL."""

    @extend_schema(
        tags=_TAG_CARGOS,
        summary="Listar cargos",
        description="Lista cargos ativos cadastrados no EOL.",
        responses={200: CargoSerializer(many=True)},
    )
    def get(self, _request: object) -> Response:
        """Lista cargos ativos cadastrados no EOL.

        Args:
            _request: Requisição HTTP recebida pela API.

        Returns:
            Cargos ativos cadastrados no EOL.
        """
        cargos = services.listar_cargos()
        return Response(CargoSerializer(cargos, many=True).data)
