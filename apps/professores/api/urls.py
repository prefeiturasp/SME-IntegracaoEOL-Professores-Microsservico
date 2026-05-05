"""Rotas da API do domínio Professores."""

from django.urls import path

from apps.professores.api.views import (
    AtribuicaoDisciplinaDataTickView,
    AtribuicaoDisciplinaDataView,
    AtribuicaoPeriodoView,
    AtribuicaoRecorrenciaDatasView,
    AtribuicaoStatusView,
    AtribuicaoTurmasListaView,
    AtribuicaoVerificarDataView,
    AutoCompleteView,
    BuscaProfessoresView,
    BuscarPorListaRFView,
    BuscarPorRfAnoLetivoView,
    BuscarPorRfDreUeView,
    BuscarTurmasAtribuidasView,
    BuscaTurmasAtribuidasEscolaView,
    EhEmeiView,
    ObterNomePeloRFView,
    ObterProfessoresAtribuidosTurmaDiscView,
    TitularesPorTurmaAgrupamentoView,
    TitularesPorTurmasView,
    TitularesPorUeView,
    TitularPorTurmaDisciplinaView,
    VerificarValidadeView,
)

_BASE_PROF = "professores"
_BASE_ESC = "escolas"

urlpatterns = [
    # EP-01 — Professores da escola (sem e com anoLetivo)
    path(
        f"{_BASE_PROF}/{_BASE_ESC}/<str:codigoEolEscola>/{_BASE_PROF}/",
        BuscaProfessoresView.as_view(),
        name="professores-escola",
    ),
    path(
        f"{_BASE_PROF}/{_BASE_ESC}/<str:codigoEolEscola>/"
        f"{_BASE_PROF}/<int:anoLetivo>/",
        BuscaProfessoresView.as_view(),
        name="professores-escola-ano",
    ),
    # EP-02 — Turmas atribuídas (escola + ano, sem RF no path)
    path(
        f"{_BASE_PROF}/escolas/<str:codigoEolEscola>"
        "/turmas/anos_letivos/<int:anoLetivo>/",
        BuscaTurmasAtribuidasEscolaView.as_view(),
        name="turmas-atribuidas-escola",
    ),
    # EP-02 — Turmas atribuídas (escola + RF + ano)
    path(
        f"{_BASE_PROF}/<str:codigoRF>/escolas/<str:codigoEolEscola>"
        "/turmas/anos_letivos/<int:anoLetivo>/",
        BuscaTurmasAtribuidasEscolaView.as_view(),
        name="turmas-atribuidas-rf-escola-ano",
    ),
    # EP-03 — Todas as turmas atribuídas
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/",
        BuscarTurmasAtribuidasView.as_view(),
        name="turmas-atribuidas-todas",
    ),
    # EP-04 — Turmas por ano letivo
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/anos_letivos/<int:anoLetivo>/",
        BuscarTurmasAtribuidasView.as_view(),
        name="turmas-atribuidas-ano",
    ),
    # EP-06 — BuscarPorRf
    path(
        f"{_BASE_PROF}/<str:codigoRf>/BuscarPorRf/<int:anoLetivo>/",
        BuscarPorRfAnoLetivoView.as_view(),
        name="professor-buscar-por-rf-ano",
    ),
    # EP-07 — BuscarPorRfDreUe
    path(
        f"{_BASE_PROF}/<str:codigoRf>/BuscarPorRfDreUe/<int:anoLetivo>/",
        BuscarPorRfDreUeView.as_view(),
        name="professor-buscar-por-rf-dre-ue",
    ),
    # EP-08 — AutoComplete
    path(
        f"{_BASE_PROF}/<int:anoLetivo>/AutoComplete/<str:dreId>/",
        AutoCompleteView.as_view(),
        name="professor-autocomplete",
    ),
    # EP-09 — BuscarPorListaRF (POST)
    path(
        f"{_BASE_PROF}/<int:anoLetivo>/BuscarPorListaRF/",
        BuscarPorListaRFView.as_view(),
        name="professor-buscar-lista-rf",
    ),
    # EP-10 — Validade
    path(
        f"{_BASE_PROF}/<str:codigoRf>/validade/",
        VerificarValidadeView.as_view(),
        name="professor-validade",
    ),
    # EP-11 — EhEmei
    path(
        f"{_BASE_PROF}/<str:codigoRF>/ehEmei/",
        EhEmeiView.as_view(),
        name="professor-eh-emei",
    ),
    # EP-12 — Status de atribuição
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/<int:codigoTurma>"
        "/atribuicao/status/",
        AtribuicaoStatusView.as_view(),
        name="professor-atribuicao-status",
    ),
    # EP-13 — Verificar atribuição em data
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/<int:codigoTurma>"
        "/atribuicao/verificar/data/",
        AtribuicaoVerificarDataView.as_view(),
        name="professor-atribuicao-verificar-data",
    ),
    # EP-14 — Verificar atribuição disciplina em data
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/<int:codigoTurma>"
        "/disciplinas/<int:disciplinaId>/atribuicao/verificar/data/",
        AtribuicaoDisciplinaDataView.as_view(),
        name="professor-atribuicao-disciplina-data",
    ),
    # EP-15 — Verificar atribuição disciplina via datatick
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/<int:codigoTurma>"
        "/disciplinas/<int:disciplinaId>/atribuicao/verificar/datatick/",
        AtribuicaoDisciplinaDataTickView.as_view(),
        name="professor-atribuicao-disciplina-datatick",
    ),
    # EP-16 — Verificar recorrência de datas
    path(
        f"{_BASE_PROF}/<str:codigoRF>/turmas/<int:codigoTurma>"
        "/disciplinas/<int:disciplinaId>"
        "/atribuicao/recorrencia/verificar/datas/",
        AtribuicaoRecorrenciaDatasView.as_view(),
        name="professor-atribuicao-recorrencia-datas",
    ),
    # EP-17 — Verificar atribuição em lista de turmas (POST)
    path(
        f"{_BASE_PROF}/<str:codigoRf>/disciplina/<int:disciplinaId>/turmas/",
        AtribuicaoTurmasListaView.as_view(),
        name="professor-atribuicao-turmas-lista",
    ),
    # EP-18 — Atribuição em período (POST)
    path(
        f"{_BASE_PROF}/<str:codigoRf>/turmas/<int:codigoTurma>"
        "/componentes/<int:componenteCurricularId>"
        "/atribuicao/periodo/inicio/<str:dataInicioPeriodo>"
        "/fim/<str:dataFimPeriodo>/",
        AtribuicaoPeriodoView.as_view(),
        name="professor-atribuicao-periodo",
    ),
    # EP-19 — Professores atribuídos turma/disciplina em data
    path(
        f"{_BASE_PROF}/<int:codigoTurma>"
        "/disciplinas/<int:disciplinaId>/atribuicao/data/",
        ObterProfessoresAtribuidosTurmaDiscView.as_view(),
        name="professores-atribuidos-turma-disc",
    ),
    # EP-20 — Titular por turma e disciplina
    path(
        f"{_BASE_PROF}/titular/turmas/<int:codigoTurma>"
        "/componentes-curriculares/<int:codigoComponenteCurricular>/",
        TitularPorTurmaDisciplinaView.as_view(),
        name="professor-titular-turma-disciplina",
    ),
    # EP-21 — Titulares por lista de turmas
    path(
        f"{_BASE_PROF}/titulares/",
        TitularesPorTurmasView.as_view(),
        name="professores-titulares",
    ),
    # EP-22 — Titulares por turma com agrupamento
    path(
        f"{_BASE_PROF}/<int:codigoTurma>"
        "/titulares/realizaAgrupamentoComponente/<str:realizaAgrupamento>/",
        TitularesPorTurmaAgrupamentoView.as_view(),
        name="professores-titulares-turma",
    ),
    # EP-23 — Titulares por UE e data de referência
    path(
        f"{_BASE_PROF}/titulares/ue/<str:ueCodigo>/<str:dataReferencia>/",
        TitularesPorUeView.as_view(),
        name="professores-titulares-ue",
    ),
    # EP-05 — Nome pelo RF (deve vir após todas as rotas com literal)
    path(
        f"{_BASE_PROF}/<str:rfProfessor>/",
        ObterNomePeloRFView.as_view(),
        name="professor-nome-rf",
    ),
]
