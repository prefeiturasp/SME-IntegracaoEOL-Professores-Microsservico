"""Views mock do domínio Professores (EP-01 a EP-23)."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mock_data import PROFESSOR_MOCK

_TAG_PROF = ["Professores"]
_TAG_TITULAR = ["Professores Titulares"]

_NOME_MARIA_SILVA = "Maria Silva"
_NOME_CARLOS_PEREIRA = "Carlos Pereira"
_CARGO_PROFESSOR_FUNDAMENTAL_MEDIO = (
    "Professor de Ensino Fundamental II e Médio"
)
_TURMA_1A_MANHA = "1A - Manhã"
_CODIGO_RF_MARIA = "7654321"
_CODIGO_RF_CARLOS = "1234567"

_MOCK_PROFESSOR_LIST = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nome": _NOME_MARIA_SILVA,
        "componenteCurricular": "Língua Portuguesa",
        "codigoComponenteCurricular": 138,
        "cargo": _CARGO_PROFESSOR_FUNDAMENTAL_MEDIO,
        "cpf": "123.456.789-00",
        "dataInicioAtribuicao": "2024-02-01",
        "dataFimAtribuicao": "2024-12-20",
        "dataInicioExercicio": "2010-03-01",
        "nomeTurma": _TURMA_1A_MANHA,
        "codigoTurma": 2112345,
        "turno": "M",
        "tipoTurma": 1,
    },
    {
        "codigoRf": _CODIGO_RF_CARLOS,
        "nome": _NOME_CARLOS_PEREIRA,
        "componenteCurricular": "Matemática",
        "codigoComponenteCurricular": 139,
        "cargo": _CARGO_PROFESSOR_FUNDAMENTAL_MEDIO,
        "cpf": "111.222.333-44",
        "dataInicioAtribuicao": "2024-02-01",
        "dataFimAtribuicao": "2024-12-20",
        "dataInicioExercicio": "2015-02-15",
        "nomeTurma": "2B - Tarde",
        "codigoTurma": 2112346,
        "turno": "T",
        "tipoTurma": 1,
    },
]

_MOCK_TURMAS_LIST = [
    {
        "codigoTurma": 2112345,
        "nomeTurma": _TURMA_1A_MANHA,
        "codigoEscola": "000532",
        "dataInicioAtribuicao": "2024-02-01",
        "dataFimAtribuicao": "2024-12-20",
        "codigoComponenteCurricular": 138,
        "codigoGrade": 2070,
        "codigoSerieGrade": 41005,
        "anoAtribuicao": 2024,
    }
]

_MOCK_PROF_TURMA = {
    "codigoRf": _CODIGO_RF_MARIA,
    "nome": _NOME_MARIA_SILVA,
    "cpf": "123.456.789-00",
    "codigoEscola": "000532",
    "nomeTurma": _TURMA_1A_MANHA,
    "codigoTurma": 2112345,
    "cargo": _CARGO_PROFESSOR_FUNDAMENTAL_MEDIO,
    "dataInicio": "2024-02-01",
    "dataFim": "2024-12-20",
}

_MOCK_ATRIB_TURMA_DISC = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nome": _NOME_MARIA_SILVA,
        "cpf": "123.456.789-00",
        "codigoComponenteCurricular": 138,
        "dataAtribuicao": "2024-02-01",
        "dataDisponibilizacao": "2024-12-20",
        "atribuicaoExterna": False,
    }
]

_MOCK_TITULAR = {
    "codigoRf": _CODIGO_RF_MARIA,
    "nome": _NOME_MARIA_SILVA,
    "cpf": "123.456.789-00",
}

_MOCK_TITULARES_LIST = [
    {
        "codigoTurma": 2112345,
        "codigoRf": _CODIGO_RF_MARIA,
        "nome": _NOME_MARIA_SILVA,
    }
]

_MOCK_TITULARES_TURMA = [
    {
        "codigoRf": _CODIGO_RF_MARIA,
        "nome": _NOME_MARIA_SILVA,
        "codigoComponenteCurricular": 138,
        "codigoTerritorioSaber": 0,
        "codigoExperienciaPedagogica": 0,
    }
]

_MOCK_AUTOCOMPLETE = [
    {"codigoRf": _CODIGO_RF_MARIA, "nomeServidor": _NOME_MARIA_SILVA},
    {"codigoRf": _CODIGO_RF_CARLOS, "nomeServidor": _NOME_CARLOS_PEREIRA},
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

_MOCK_ATRIB_PERIODO = [
    {"data": "2024-02-05", "possuiAtribuicao": True},
    {"data": "2024-03-10", "possuiAtribuicao": True},
]

_MOCK_VERIF_TURMAS = [
    {"codigoTurma": 2112345, "possuiAtribuicao": True},
    {"codigoTurma": 2112346, "possuiAtribuicao": False},
]


# ---------------------------------------------------------------------------
# EP-01 / EP-02 — Professores de escola / Turmas atribuídas (escola+ano)
# ---------------------------------------------------------------------------


class BuscaProfessoresView(APIView):
    """EP-01 — Buscar professores de uma escola por ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-01 | Buscar professores de uma escola por ano letivo",
        parameters=[
            OpenApiParameter("codigoEolEscola", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
        ano_letivo: int | None = None,
    ) -> Response:
        """Retorna lista mock de professores da escola."""
        return Response(_MOCK_PROFESSOR_LIST)


class BuscaTurmasAtribuidasEscolaView(APIView):
    """EP-02 — Turmas atribuídas ao professor em uma escola e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-02 | Turmas atribuídas ao professor (escola + ano)",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoEolEscola", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
        ano_letivo: int,
        codigo_rf: str | None = None,
    ) -> Response:
        """Retorna lista mock de turmas atribuídas."""
        return Response(_MOCK_TURMAS_LIST)


# ---------------------------------------------------------------------------
# EP-03 / EP-04 — Turmas do professor (todas / por ano)
# ---------------------------------------------------------------------------


class BuscarTurmasAtribuidasView(APIView):
    """EP-03/04 — Todas as turmas atribuídas ao professor."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-03 | Turmas atribuídas ao professor (todas)",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        ano_letivo: int | None = None,
    ) -> Response:
        """Retorna lista mock de turmas atribuídas."""
        return Response(_MOCK_TURMAS_LIST)


# ---------------------------------------------------------------------------
# EP-05 — Nome pelo RF
# ---------------------------------------------------------------------------


class ObterNomePeloRFView(APIView):
    """EP-05 — Obter nome do professor pelo RF."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-05 | Obter nome do professor pelo RF",
        parameters=[
            OpenApiParameter("rfProfessor", str, OpenApiParameter.PATH),
        ],
        responses={200: dict},
    )
    def get(self, request: Request, rf_professor: str) -> Response:
        """Retorna nome mock do professor."""
        return Response(
            {"codigoRf": rf_professor, "nome": PROFESSOR_MOCK["nome"]}
        )


# ---------------------------------------------------------------------------
# EP-06 / EP-07 — BuscarPorRf e BuscarPorRfDreUe
# ---------------------------------------------------------------------------


class BuscarPorRfAnoLetivoView(APIView):
    """EP-06 — Buscar professor por RF e ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-06 | Buscar professor por RF e ano letivo",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "buscarOutrosCargos",
                bool,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        """Retorna dados mock do professor."""
        return Response(_MOCK_PROF_TURMA)


class BuscarPorRfDreUeView(APIView):
    """EP-07 — Buscar professor por RF, DRE e UE."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-07 | Buscar professor por RF, DRE e UE",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dreId", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "ueId", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "buscarOutrosCargos",
                bool,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        """Retorna dados mock do professor filtrado por DRE/UE."""
        return Response(_MOCK_PROF_TURMA)


# ---------------------------------------------------------------------------
# EP-08 — AutoComplete
# ---------------------------------------------------------------------------


class AutoCompleteView(APIView):
    """EP-08 — AutoComplete de professores por DRE e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-08 | AutoComplete de professores por DRE e ano",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter("dreId", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "ueId", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "nome", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: list},
    )
    def get(
        self, request: Request, ano_letivo: int, dre_id: str
    ) -> Response:
        """Retorna lista mock de professores para autocomplete."""
        return Response(_MOCK_AUTOCOMPLETE)


# ---------------------------------------------------------------------------
# EP-09 — BuscarPorListaRF (POST)
# ---------------------------------------------------------------------------


class BuscarPorListaRFView(APIView):
    """EP-09 — Buscar professores por lista de RF e ano."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-09 | Buscar professores por lista de RF e ano (POST)",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        request=list,
        responses={200: list},
    )
    def post(self, request: Request, ano_letivo: int) -> Response:
        """Retorna lista mock de professores."""
        return Response(_MOCK_RESUMO)


# ---------------------------------------------------------------------------
# EP-10 — Validade do professor
# ---------------------------------------------------------------------------


class VerificarValidadeView(APIView):
    """EP-10 — Verificar validade do professor."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-10 | Verificar validade do professor",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
        ],
        responses={200: bool},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        """Retorna true (professor válido)."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-11 — EhEmei
# ---------------------------------------------------------------------------


class EhEmeiView(APIView):
    """EP-11 — Verificar se professor é EMEI."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-11 | Verificar se professor é EMEI",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
        ],
        responses={200: bool, 400: dict},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        """Retorna false (professor não é EMEI no mock)."""
        return Response(False)


# ---------------------------------------------------------------------------
# EP-12 — Status de atribuição na turma
# ---------------------------------------------------------------------------


class AtribuicaoStatusView(APIView):
    """EP-12 — Verificar atribuição na turma (status)."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-12 | Verificar status de atribuição na turma",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
        ],
        responses={200: dict, 422: dict, 500: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, codigo_turma: int
    ) -> Response:
        """Retorna status de atribuição mock."""
        return Response(
            {
                "possuiAtribuicao": True,
                "codigoRf": codigo_rf,
                "codigoTurma": codigo_turma,
            }
        )


# ---------------------------------------------------------------------------
# EP-13 — Atribuição na turma em data
# ---------------------------------------------------------------------------


class AtribuicaoVerificarDataView(APIView):
    """EP-13 — Verificar atribuição na turma em uma data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-13 | Verificar atribuição na turma em data",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataConsulta",
                str,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: bool, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, codigo_turma: int
    ) -> Response:
        """Retorna true (possui atribuição) no mock."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-14 — Atribuição na disciplina/turma em data
# ---------------------------------------------------------------------------


class AtribuicaoDisciplinaDataView(APIView):
    """EP-14 — Verificar atribuição na disciplina/turma em data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-14 | Verificar atribuição na disciplina/turma em data",
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataConsulta",
                str,
                OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                "territorioSaber",
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
        """Retorna true (possui atribuição) no mock."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-15 — Atribuição via dataTick
# ---------------------------------------------------------------------------


class AtribuicaoDisciplinaDataTickView(APIView):
    """EP-15 — Verificar atribuição na disciplina/turma via dataTick."""

    @extend_schema(
        tags=_TAG_PROF,
        summary=(
            "EP-15 | Verificar atribuição na disciplina/turma via dataTick"
        ),
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataConsultaTick",
                int,
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
        """Retorna true (possui atribuição) no mock."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-16 — Recorrência de datas (array de ticks)
# ---------------------------------------------------------------------------


class AtribuicaoRecorrenciaDatasView(APIView):
    """EP-16 — Verificar atribuição em recorrência de datas."""

    @extend_schema(
        tags=_TAG_PROF,
        summary=(
            "EP-16 | Verificar atribuição na disciplina/turma"
            " em recorrência de datas"
        ),
        parameters=[
            OpenApiParameter("codigoRF", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataTicks",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ],
        responses={200: list, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: int,
        disciplina_id: int,
    ) -> Response:
        """Retorna lista mock de datas com status de atribuição."""
        return Response(_MOCK_ATRIB_PERIODO)


# ---------------------------------------------------------------------------
# EP-17 — Verificar atribuição em lista de turmas (POST)
# ---------------------------------------------------------------------------


class AtribuicaoTurmasListaView(APIView):
    """EP-17 — Verificar atribuição em turmas por disciplina (POST)."""

    @extend_schema(
        tags=_TAG_PROF,
        summary=(
            "EP-17 | Verificar atribuição em turmas por disciplina (POST)"
        ),
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
        ],
        request=list,
        responses={200: list},
    )
    def post(
        self, request: Request, codigo_rf: str, disciplina_id: int
    ) -> Response:
        """Retorna lista mock de turmas com status de atribuição."""
        return Response(_MOCK_VERIF_TURMAS)


# ---------------------------------------------------------------------------
# EP-18 — Atribuição em período (POST)
# ---------------------------------------------------------------------------


class AtribuicaoPeriodoView(APIView):
    """EP-18 — Verificar atribuição do professor em período."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="EP-18 | Verificar atribuição do professor em período (POST)",
        parameters=[
            OpenApiParameter("codigoRf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "componenteCurricularId", int, OpenApiParameter.PATH
            ),
            OpenApiParameter(
                "dataInicioPeriodo", str, OpenApiParameter.PATH
            ),
            OpenApiParameter("dataFimPeriodo", str, OpenApiParameter.PATH),
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
        """Retorna true (possui atribuição no período) no mock."""
        return Response(True)


# ---------------------------------------------------------------------------
# EP-19 — Professores atribuídos a turma/disciplina em data
# ---------------------------------------------------------------------------


class ObterProfessoresAtribuidosTurmaDiscView(APIView):
    """EP-19 — Obter professores atribuídos a turma/disciplina em data."""

    @extend_schema(
        tags=_TAG_PROF,
        summary=(
            "EP-19 | Obter professores atribuídos a turma/disciplina em data"
        ),
        parameters=[
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplinaId", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "dataTicks",
                int,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: list, 400: dict, 422: dict, 500: dict},
    )
    def get(
        self, request: Request, codigo_turma: int, disciplina_id: int
    ) -> Response:
        """Retorna lista mock de professores atribuídos."""
        return Response(_MOCK_ATRIB_TURMA_DISC)


# ---------------------------------------------------------------------------
# EP-20 — Titular por turma e disciplina
# ---------------------------------------------------------------------------


class TitularPorTurmaDisciplinaView(APIView):
    """EP-20 — Buscar professor titular por turma e disciplina."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="EP-20 | Buscar professor titular por turma e disciplina",
        parameters=[
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigoComponenteCurricular", int, OpenApiParameter.PATH
            ),
        ],
        responses={200: dict},
    )
    def get(
        self,
        request: Request,
        codigo_turma: int,
        codigo_componente_curricular: int,
    ) -> Response:
        """Retorna titular mock."""
        return Response(_MOCK_TITULAR)


# ---------------------------------------------------------------------------
# EP-21 — Titulares por lista de turmas
# ---------------------------------------------------------------------------


class TitularesPorTurmasView(APIView):
    """EP-21 — Buscar professores titulares por lista de turmas."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="EP-21 | Buscar professores titulares por lista de turmas",
        parameters=[
            OpenApiParameter(
                "codigosTurmas",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ],
        responses={200: list},
    )
    def get(self, request: Request) -> Response:
        """Retorna lista mock de titulares."""
        return Response(_MOCK_TITULARES_LIST)


# ---------------------------------------------------------------------------
# EP-22 — Titulares por turma com agrupamento
# ---------------------------------------------------------------------------


class TitularesPorTurmaAgrupamentoView(APIView):
    """EP-22 — Buscar professores titulares por turma com agrupamento."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary=(
            "EP-22 | Buscar professores titulares por turma com agrupamento"
        ),
        parameters=[
            OpenApiParameter("codigoTurma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "realizaAgrupamento", str, OpenApiParameter.PATH
            ),
            OpenApiParameter(
                "codigoRF",
                str,
                OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                "dataReferencia",
                str,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        codigo_turma: int,
        realiza_agrupamento: str,
    ) -> Response:
        """Retorna lista mock de titulares com componentes."""
        return Response(_MOCK_TITULARES_TURMA)


# ---------------------------------------------------------------------------
# EP-23 — Titulares por UE e data de referência
# ---------------------------------------------------------------------------


class TitularesPorUeView(APIView):
    """EP-23 — Buscar professores titulares por UE e data de referência."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary=(
            "EP-23 | Buscar professores titulares por UE e data de referência"
        ),
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
        responses={200: list},
    )
    def get(
        self,
        request: Request,
        ue_codigo: str,
        data_referencia: str,
    ) -> Response:
        """Retorna lista mock de titulares da UE."""
        return Response(_MOCK_TITULARES_TURMA)
