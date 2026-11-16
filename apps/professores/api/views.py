"""Views do domínio de professores."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.professores import services
from apps.professores.serializers import (
    AtribuicaoDataSerializer,
    AtribuicaoStatusSerializer,
    AtribuicaoTurmaSerializer,
    AutoCompleteSerializer,
    BuscaProfessorPorRfQuerySerializer,
    DisciplinaTurmaAtribuidaUeSerializer,
    NomePorRFSerializer,
    ProfessorAtribuicaoTurmaDiscSerializer,
    ProfessorEscolaSerializer,
    ProfessorPerfilSerializer,
    ResumoSerializer,
    TitularPorTurmaSerializer,
    TitularSerializer,
    TitularTurmaSerializer,
    TurmaAtribuidaSerializer,
    TurmaAtribuidaUeSerializer,
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
        """Lista professores de uma escola.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_eol_escola: Código EOL da escola consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_professores_escola(codigo_eol_escola)
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
        """Lista professores de uma escola por ano letivo.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_eol_escola: Código EOL da escola consultada.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_professores_escola(
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
        """Lista turmas atribuídas em uma escola e ano letivo.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_eol_escola: Código EOL da escola consultada.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_turmas_professor_escola_ano(
            codigo_eol_escola, ano_letivo
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
        """Lista turmas atribuídas ao professor em uma escola.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_eol_escola: Código EOL da escola consultada.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
            codigo_rf: Registro funcional do professor ou servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_turmas_professor_escola_ano(
            codigo_eol_escola, ano_letivo, codigo_rf
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
        """Lista turmas atribuídas ao professor.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_turmas_professor(codigo_rf, ano_letivo)
        return Response(resultado)


class BuscarTurmasAtribuidasTodosAnosView(APIView):
    """Lista turmas atribuídas ao professor em todos os anos letivos."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas ao professor sem filtro de ano letivo",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaAtribuidaSerializer(many=True)},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        """Lista turmas atribuídas sem restringir o ano letivo.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional ou CPF do professor.

        Returns:
            Resposta HTTP com as atribuições encontradas.
        """
        resultado = services.buscar_turmas_professor_todos_anos(codigo_rf)
        return Response(resultado)


class BuscarAbrangenciaFuncionarioPerfilView(APIView):
    """Lista abrangência de turmas do funcionário."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Abrangência de turmas por funcionário e perfil",
        parameters=[
            OpenApiParameter("login", str, OpenApiParameter.PATH),
            OpenApiParameter("id_perfil", str, OpenApiParameter.PATH),
        ],
        responses={200: dict},
    )
    def get(self, request: Request, login: str, id_perfil: str) -> Response:
        """Lista abrangência de turmas do funcionário.

        Args:
            request: Requisição HTTP recebida pela API.
            login: Login do funcionário usado para buscar abrangência.
            id_perfil: Identificador do perfil SGP usado na consulta.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_abrangencia_funcionario_perfil(
            login,
            id_perfil,
        )
        return Response(resultado)


class TurmasAtribuidasUeView(APIView):
    """Lista turmas atribuídas por vínculo com UE."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Turmas atribuídas por vínculo com UE",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter(
                "cargos", OpenApiTypes.STR, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "codigo_dre", OpenApiTypes.STR, OpenApiParameter.QUERY
            ),
        ],
        responses={200: TurmaAtribuidaUeSerializer(many=True)},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        """Lista turmas atribuídas por vínculo com UE.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        cargos = [
            int(cargo)
            for cargo in request.query_params.getlist("cargos")
            if cargo.isdigit()
        ]
        codigo_dre = request.query_params.get("codigo_dre")
        resultado = services.turmas_atribuidas_ue(
            codigo_rf,
            cargos or None,
            codigo_dre,
        )
        return Response(resultado)


class DisciplinasTurmasAtribuidasUeView(APIView):
    """Lista disciplinas atribuídas por vínculo com UE."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Disciplinas atribuídas por vínculo com UE",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "cargos", OpenApiTypes.STR, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "codigo_dre", OpenApiTypes.STR, OpenApiParameter.QUERY
            ),
        ],
        responses={200: DisciplinaTurmaAtribuidaUeSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: int,
    ) -> Response:
        """Lista disciplinas atribuídas por vínculo com UE.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        cargos = [
            int(cargo)
            for cargo in request.query_params.getlist("cargos")
            if cargo.isdigit()
        ]
        codigo_dre = request.query_params.get("codigo_dre")
        resultado = services.disciplinas_turmas_atribuidas_ue(
            codigo_rf,
            codigo_turma,
            cargos or None,
            codigo_dre,
        )
        return Response(resultado)


class ObterNomePeloRFView(APIView):
    """Retorna o nome do professor pelo registro funcional."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Obter nome do professor pelo RF",
        parameters=[
            OpenApiParameter("rf_professor", str, OpenApiParameter.PATH),
        ],
        responses={200: NomePorRFSerializer, 204: None},
    )
    def get(self, request: Request, rf_professor: str) -> Response:
        """Retorna o nome do professor pelo registro funcional.

        Args:
            request: Requisição HTTP recebida pela API.
            rf_professor: Registro funcional do professor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        nome = services.obter_nome_rf(rf_professor)
        if nome is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        from django.http import HttpResponse

        return HttpResponse(nome, content_type="text/plain")


class BuscaProfessorPorRfView(APIView):
    """Expõe um contrato único para as consultas existentes por RF."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor por RF e ano letivo",
        description=(
            "Localiza uma pessoa pelo RF informado e devolve somente seu "
            "identificador e nome quando ela atende aos critérios da busca. "
            "Mesmo que existam várias atribuições, retorna um único objeto; "
            "não lista turmas, cargos ou unidades.\n\n"
            "**Busca simples (`tipo_busca=rf`):** exige atribuição de aula "
            "não cancelada, iniciada até hoje, cuja disponibilização esteja "
            "em aberto ou tenha ocorrido no ano informado. O ano se refere "
            "à disponibilização, não ao ano da atribuição. Não aplica DRE, "
            "UE ou outros cargos e não busca contratos externos.\n\n"
            "**Busca com localização (`tipo_busca=rf_dre_ue`):** exige "
            "atribuição não cancelada no ano informado e, se preenchida, na "
            "UE indicada. Com `buscar_outros_cargos=true`, ignora o filtro "
            "de UE; isso não inclui automaticamente servidores sem aula. "
            "Se não encontrar atribuição, trata o identificador como CPF "
            "e procura contrato externo não cancelado, sem filtro de ano "
            "ou localização. A DRE é aceita, mas não filtra a consulta.\n\n"
            "O tipo explícito prevalece. Sem tipo, DRE ou UE selecionam a "
            "busca com localização; sem ambos, usa a busca simples. "
            "Retorna 200 com `codigo_rf` e `nome`, ou 204 sem corpo quando "
            "não há correspondência. Substitui BuscarPorRf e BuscarPorRfDreUe "
            "preservando os comportamentos atuais."
        ),
        parameters=[BuscaProfessorPorRfQuerySerializer],
        responses={200: NomePorRFSerializer, 204: None, 400: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        """Localiza um professor pelos critérios de atribuição da busca.

        Recebe um RF e devolve somente identificador e nome, uma única vez,
        mesmo quando há várias atribuições. Não retorna cargos, turmas ou UEs.

        No tipo ``rf``, exige aula não cancelada e iniciada até hoje, com
        disponibilização nula ou no ano informado. O ano não restringe o ano
        de atribuição. Localização e outros cargos não alteram essa busca.

        No tipo ``rf_dre_ue``, exige aula não cancelada no ano de atribuição
        informado. Filtra UE, exceto com ``buscar_outros_cargos=true``, que
        retira esse recorte sem passar a incluir servidores sem aula. Se não
        encontrar atribuição, procura contrato externo não cancelado pelo CPF,
        sem exigir ano ou localização. A DRE não é aplicada pela consulta.

        O tipo explícito prevalece. Se omitido, a presença de DRE ou UE escolhe
        ``rf_dre_ue``; sem localização, usa ``rf``. Ausência de correspondência
        retorna 204 sem corpo; correspondência retorna 200 com RF/CPF e nome.

        Args:
            request: Requisição com localização, outros cargos e tipo de busca.
            codigo_rf: Registro funcional ou CPF recebido na consulta.
            ano_letivo: Ano letivo positivo.

        Returns:
            Resultado, ausência de conteúdo ou erro de validação.
        """
        if not codigo_rf.strip() or ano_letivo < 1:
            return Response(
                {"detail": "É necessário informar o RF e o ano letivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        filtros = BuscaProfessorPorRfQuerySerializer(data=request.query_params)
        filtros.is_valid(raise_exception=True)
        resultado = services.buscar_professor_por_rf(
            codigo_rf, ano_letivo, **filtros.validated_data
        )
        if resultado is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(resultado)


class BuscarPorRfAnoLetivoView(APIView):
    """Retorna dados do professor com atribuicao de aula por ano letivo."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor com atribuicao de aula por ano letivo.",
        deprecated=True,
        description=(
            "Depreciado. Use GET /api/v1/professores/{codigo_rf}/"
            "anos_letivos/{ano_letivo}/?tipo_busca=rf. O contrato novo reúne "
            "as buscas com filtros opcionais e reutiliza a mesma consulta, "
            "preservando suas regras. Esta rota continua compatível."
        ),
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        responses={200: ProfessorPerfilSerializer, 204: None},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        """Busca identificador e nome do professor com atribuição de aula.

        Consulta atribuições não canceladas, iniciadas até a data atual e com
        disponibilização nula ou no ano informado. Esta busca não filtra pelo
        ano da atribuição, por DRE, por UE ou pelo parâmetro de outros cargos.
        Não executa fallback de contrato externo quando não encontra aula.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            ano_letivo: Ano de referência para a disponibilização das aulas.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.buscar_professor_com_atribuicao_aula_ano_letivo(
            codigo_rf, ano_letivo
        )
        if resultado is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(resultado)


class BuscarPorRfDreUeView(APIView):
    """Retorna dados do professor por registro funcional."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Buscar professor por RF, DRE e UE",
        deprecated=True,
        description=(
            "Depreciado. Use GET /api/v1/professores/{codigo_rf}/"
            "anos_letivos/{ano_letivo}/?tipo_busca=rf_dre_ue, inclusive sem "
            "DRE/UE. O contrato novo reúne as buscas e reutiliza a mesma "
            "consulta, preservando suas regras. Esta rota continua compatível."
        ),
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
        responses={200: ProfessorPerfilSerializer, 204: None, 400: dict},
    )
    def get(
        self, request: Request, codigo_rf: str, ano_letivo: int
    ) -> Response:
        """Busca identificador e nome por RF e ano de atribuição.

        Restringe atribuições não canceladas à UE informada, exceto quando
        ``buscar_outros_cargos=true`` remove esse recorte. A DRE recebida não
        é aplicada pela consulta atual. Na ausência de atribuição, busca um
        contrato externo não cancelado pelo CPF, sem filtro de ano ou
        localização.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: RF do professor ou CPF usado no fallback externo.
            ano_letivo: Ano usado no filtro de atribuições de aula.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        if ano_letivo == 0:
            return Response(
                {"detail": "É necessário informar o ano letivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        buscar_outros_cargos = (
            request.query_params.get("buscar_outros_cargos", "").lower()
            == "true"
        )
        resultado = services.buscar_por_rf_dre_ue(
            codigo_rf,
            ano_letivo,
            ue_id=request.query_params.get("ue_id"),
            buscar_outros_cargos=buscar_outros_cargos,
        )
        if resultado is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
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
        """Lista professores para autocomplete por DRE e ano.

        Args:
            request: Requisição HTTP recebida pela API.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.
            dre_id: Código EOL da DRE usada para filtrar professores.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.autocomplete_professores(
            ano_letivo,
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
        responses={200: ResumoSerializer(many=True), 400: dict},
    )
    def post(self, request: Request, ano_letivo: int) -> Response:
        """Lista professores por registros funcionais e ano.

        Args:
            request: Requisição HTTP recebida pela API.
            ano_letivo: Ano letivo usado para filtrar vínculos e atribuições.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        if ano_letivo == 0:
            return Response(
                {"detail": "É necessário informar o ano letivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resultado = services.buscar_por_lista_rf(ano_letivo, request.data)
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
        """Verifica se o professor possui vínculo válido.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.verificar_validade(codigo_rf))


class UnidadesAtribuicaoValidaView(APIView):
    """Lista as UEs onde o professor tem atribuição válida."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Listar UEs com atribuição válida do professor",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request: Request, codigo_rf: str) -> Response:
        """Lista as UEs onde o professor tem atribuição válida.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            {
                "codigo_rf": codigo_rf,
                "codigos_ue": services.unidades_com_atribuicao_valida(
                    codigo_rf
                ),
            }
        )


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
        """Verifica atribuição do professor na turma.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(services.atribuicao_status(codigo_rf, codigo_turma))


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
        """Verifica atribuição do professor na turma em uma data.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.atribuicao_verificar_data(
                codigo_rf,
                codigo_turma,
                request.query_params.get("data_consulta"),
            )
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
        """Verifica atribuição do professor na disciplina em uma data.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.
            disciplina_id: Identificador do componente curricular/disciplina.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.atribuicao_disciplina_data(
                codigo_rf,
                codigo_turma,
                disciplina_id,
                request.query_params.get("data_consulta"),
            )
        )


class AtribuicaoDisciplinaDataTickView(APIView):
    """Verifica atribuição do professor usando data em ticks."""

    @extend_schema(
        tags=_TAG_PROF,
        deprecated=True,
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
        """Verifica atribuição do professor usando data em ticks.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.
            disciplina_id: Identificador do componente curricular/disciplina.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.atribuicao_disciplina_datatick(
            codigo_rf,
            codigo_turma,
            disciplina_id,
            request.query_params.get("data_consulta_tick"),
        )
        return Response(resultado.payload, status=resultado.status_code)


class AtribuicaoRecorrenciaDatasView(APIView):
    """Lista resultados de atribuição para datas recorrentes."""

    @extend_schema(
        tags=_TAG_PROF,
        deprecated=True,
        summary=(
            "Verificar atribuição na disciplina/turma em recorrência de datas"
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
        """Lista resultados de atribuição para datas recorrentes.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.
            disciplina_id: Identificador do componente curricular/disciplina.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.atribuicao_recorrencia_datas(
            codigo_rf,
            codigo_turma,
            disciplina_id,
            request.query_params.getlist("data_ticks"),
        )
        return Response(resultado.payload, status=resultado.status_code)


class AtribuicaoTurmasListaView(APIView):
    """Lista resultados de atribuição em turmas por disciplina."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Verificar atribuição em turmas por disciplina",
        parameters=[
            OpenApiParameter("codigo_rf", str, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
        ],
        request=list[int],
        responses={200: AtribuicaoTurmaSerializer(many=True), 400: dict},
    )
    def post(
        self, request: Request, codigo_rf: str, disciplina_id: int
    ) -> Response:
        """Lista resultados de atribuição em turmas por disciplina.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            disciplina_id: Identificador do componente curricular/disciplina.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.atribuicao_turmas_lista(
            codigo_rf,
            disciplina_id,
            request.data,
        )
        return Response(resultado.payload, status=resultado.status_code)


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
        """Verifica atribuição do professor em período.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_rf: Registro funcional do professor ou servidor consultado.
            codigo_turma: Código EOL da turma consultada.
            componente_curricular_id: ID do componente curricular consultado.
            data_inicio_periodo: Data inicial do período consultado.
            data_fim_periodo: Data final do período de atribuição consultado.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.atribuicao_periodo(
                codigo_rf,
                codigo_turma,
                componente_curricular_id,
                data_inicio_periodo,
                data_fim_periodo,
            )
        )


class ObterProfessoresAtribuidosTurmaDiscView(APIView):
    """Lista professores atribuídos a turma e disciplina em data."""

    @extend_schema(
        tags=_TAG_PROF,
        deprecated=True,
        summary="Obter professores atribuídos a turma/disciplina em data",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_ticks", int, OpenApiParameter.QUERY, required=True
            ),
        ],
        responses={
            200: ProfessorAtribuicaoTurmaDiscSerializer(many=True),
            400: dict,
            422: dict,
            500: dict,
        },
    )
    def get(
        self, request: Request, codigo_turma: int, disciplina_id: int
    ) -> Response:
        """Lista professores atribuídos a turma e disciplina em data.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_turma: Código EOL da turma consultada.
            disciplina_id: Identificador do componente curricular/disciplina.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.professores_atribuidos_turma_disc(
            codigo_turma,
            disciplina_id,
            request.query_params.get("data_ticks"),
        )
        return Response(resultado.payload, status=resultado.status_code)


class ProfessoresAtribuidosTurmaDiscDataView(APIView):
    """Lista professores atribuídos a turma e disciplina em data ISO."""

    @extend_schema(
        tags=_TAG_PROF,
        summary="Obter professores atribuídos a turma/disciplina em data ISO",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("disciplina_id", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={
            200: ProfessorAtribuicaoTurmaDiscSerializer(many=True),
            400: dict,
            422: dict,
            500: dict,
        },
    )
    def get(
        self, request: Request, codigo_turma: int, disciplina_id: int
    ) -> Response:
        """Lista professores atribuídos a turma e disciplina em data ISO.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_turma: Código EOL da turma consultada.
            disciplina_id: Identificador do componente curricular/disciplina.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.professores_atribuidos_turma_disc_data(
                codigo_turma,
                disciplina_id,
                request.query_params.get("data"),
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
        responses={200: TitularSerializer, 204: None},
    )
    def get(
        self,
        request: Request,
        codigo_turma: int,
        codigo_componente_curricular: int,
    ) -> Response:
        """Retorna professor titular por turma e disciplina.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_turma: Código EOL da turma consultada.
            codigo_componente_curricular: Código do componente curricular.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        resultado = services.titular_por_turma_disciplina(
            codigo_turma, codigo_componente_curricular
        )
        if resultado is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
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
        """Lista professores titulares por turmas.

        Args:
            request: Requisição HTTP recebida pela API.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.titulares_por_turmas(
                request.query_params.getlist("codigos_turmas")
            )
        )


class TitularesPorTurmaView(APIView):
    """Lista professores titulares por turma."""

    @extend_schema(
        tags=_TAG_TITULAR,
        summary="Buscar professores titulares por turma",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigo_rf", str, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: TitularTurmaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        codigo_turma: int,
    ) -> Response:
        """Lista professores titulares por turma.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_turma: Código EOL da turma consultada.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.titulares_por_turma(
                codigo_turma,
                codigo_rf=request.query_params.get("codigo_rf"),
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
        ],
        responses={200: TitularPorTurmaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        ue_codigo: str,
        data_referencia: str,
    ) -> Response:
        """Lista professores titulares por unidade e data de referência.

        Args:
            request: Requisição HTTP recebida pela API.
            ue_codigo: Código EOL da unidade educacional consultada.
            data_referencia: Data de referência usada para consultar titulares.

        Returns:
            Resposta HTTP com o resultado da operação.
        """
        return Response(
            services.titulares_por_ue(
                ue_codigo,
                data_referencia,
            )
        )


class AdministradorSgpEscolaView(APIView):
    """Retorna RFs dos administradores SGP de uma escola."""

    @extend_schema(
        tags=["Escolas"],
        operation_id="E01_administrador_sgp",
        summary="Lista administradores SGP da escola",
        description=(
            "Retorna lista de RFs/logins de administradores SGP da escola. "
            "Inclui administradores da UE e da DRE associada. "
            "Dados sincronizados do CoreSSO via ETL."
        ),
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request: Request, codigo_ue: str) -> Response:
        """Busca administradores.

        Args:
            request: Requisição HTTP.
            codigo_ue: Código EOL da unidade educacional.

        Returns:
            Lista de RFs.
        """
        from apps.professores.models import AdministradorEscola

        administradores = AdministradorEscola.objects.filter(
            codigo_ue=codigo_ue
        ).values_list("rf_login", flat=True)

        return Response(list(administradores), status=status.HTTP_200_OK)
