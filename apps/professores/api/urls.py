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
    BuscaProfessoresAnoLetivoView,
    AutoCompleteView,
    BuscaProfessoresView,
    BuscarPorListaRFView,
    BuscarPorRfAnoLetivoView,
    BuscarPorRfDreUeView,
    BuscaTurmasAtribuidasProfessorEscolaView,
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
    # EP-01 — Professores da escola (sem e com ano_letivo)
    path(
        f"{_BASE_PROF}/{_BASE_ESC}/<str:codigo_eol_escola>/{_BASE_PROF}/",
        BuscaProfessoresView.as_view(),
        name="professores-escola",
    ),
    path(
        f"{_BASE_PROF}/{_BASE_ESC}/<str:codigo_eol_escola>/"
        f"{_BASE_PROF}/<int:ano_letivo>/",
        BuscaProfessoresAnoLetivoView.as_view(),
        name="professores-escola-ano",
    ),
    # EP-02 — Turmas atribuídas (escola + ano, sem RF no path)
    path(
        f"{_BASE_PROF}/escolas/<str:codigo_eol_escola>"
        "/turmas/anos_letivos/<int:ano_letivo>/",
        BuscaTurmasAtribuidasEscolaView.as_view(),
        name="turmas-atribuidas-escola",
    ),
    # EP-02 — Turmas atribuídas (escola + RF + ano)
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/escolas/<str:codigo_eol_escola>"
        "/turmas/anos_letivos/<int:ano_letivo>/",
        BuscaTurmasAtribuidasProfessorEscolaView.as_view(),
        name="turmas-atribuidas-rf-escola-ano",
    ),
    # EP-03 — Todas as turmas atribuídas
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/",
        BuscarTurmasAtribuidasView.as_view(),
        name="turmas-atribuidas-todas",
    ),
    # EP-04 — Turmas por ano letivo
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/anos_letivos/<int:ano_letivo>/",
        BuscarTurmasAtribuidasView.as_view(),
        name="turmas-atribuidas-ano",
    ),
    # EP-06 — BuscarPorRf
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/BuscarPorRf/<int:ano_letivo>/",
        BuscarPorRfAnoLetivoView.as_view(),
        name="professor-buscar-por-rf-ano",
    ),
    # EP-07 — BuscarPorRfDreUe
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/BuscarPorRfDreUe/<int:ano_letivo>/",
        BuscarPorRfDreUeView.as_view(),
        name="professor-buscar-por-rf-dre-ue",
    ),
    # EP-08 — AutoComplete
    path(
        f"{_BASE_PROF}/<int:ano_letivo>/AutoComplete/<str:dre_id>/",
        AutoCompleteView.as_view(),
        name="professor-autocomplete",
    ),
    # EP-09 — BuscarPorListaRF (POST)
    path(
        f"{_BASE_PROF}/<int:ano_letivo>/BuscarPorListaRF/",
        BuscarPorListaRFView.as_view(),
        name="professor-buscar-lista-rf",
    ),
    # EP-10 — Validade
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/validade/",
        VerificarValidadeView.as_view(),
        name="professor-validade",
    ),
    # EP-11 — EhEmei
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/ehEmei/",
        EhEmeiView.as_view(),
        name="professor-eh-emei",
    ),
    # EP-12 — Status de atribuição
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/<int:codigo_turma>"
        "/atribuicao/status/",
        AtribuicaoStatusView.as_view(),
        name="professor-atribuicao-status",
    ),
    # EP-13 — Verificar atribuição em data
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/<int:codigo_turma>"
        "/atribuicao/verificar/data/",
        AtribuicaoVerificarDataView.as_view(),
        name="professor-atribuicao-verificar-data",
    ),
    # EP-14 — Verificar atribuição disciplina em data
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/<int:codigo_turma>"
        "/disciplinas/<int:disciplina_id>/atribuicao/verificar/data/",
        AtribuicaoDisciplinaDataView.as_view(),
        name="professor-atribuicao-disciplina-data",
    ),
    # EP-15 — Verificar atribuição disciplina via datatick
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/<int:codigo_turma>"
        "/disciplinas/<int:disciplina_id>/atribuicao/verificar/datatick/",
        AtribuicaoDisciplinaDataTickView.as_view(),
        name="professor-atribuicao-disciplina-datatick",
    ),
    # EP-16 — Verificar recorrência de datas
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/<int:codigo_turma>"
        "/disciplinas/<int:disciplina_id>"
        "/atribuicao/recorrencia/verificar/datas/",
        AtribuicaoRecorrenciaDatasView.as_view(),
        name="professor-atribuicao-recorrencia-datas",
    ),
    # EP-17 — Verificar atribuição em lista de turmas (POST)
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/disciplina/<int:disciplina_id>/turmas/",
        AtribuicaoTurmasListaView.as_view(),
        name="professor-atribuicao-turmas-lista",
    ),
    # EP-18 — Atribuição em período (POST)
    path(
        f"{_BASE_PROF}/<str:codigo_rf>/turmas/<int:codigo_turma>"
        "/componentes/<int:componente_curricular_id>"
        "/atribuicao/periodo/inicio/<str:data_inicio_periodo>"
        "/fim/<str:data_fim_periodo>/",
        AtribuicaoPeriodoView.as_view(),
        name="professor-atribuicao-periodo",
    ),
    # EP-19 — Professores atribuídos turma/disciplina em data
    path(
        f"{_BASE_PROF}/<int:codigo_turma>"
        "/disciplinas/<int:disciplina_id>/atribuicao/data/",
        ObterProfessoresAtribuidosTurmaDiscView.as_view(),
        name="professores-atribuidos-turma-disc",
    ),
    # EP-20 — Titular por turma e disciplina
    path(
        f"{_BASE_PROF}/titular/turmas/<int:codigo_turma>"
        "/componentes-curriculares/<int:codigo_componente_curricular>/",
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
        f"{_BASE_PROF}/<int:codigo_turma>"
        "/titulares/realizaAgrupamentoComponente/<str:realiza_agrupamento>/",
        TitularesPorTurmaAgrupamentoView.as_view(),
        name="professores-titulares-turma",
    ),
    # EP-23 — Titulares por UE e data de referência
    path(
        f"{_BASE_PROF}/titulares/ue/<str:ue_codigo>/<str:data_referencia>/",
        TitularesPorUeView.as_view(),
        name="professores-titulares-ue",
    ),
    # EP-05 — Nome pelo RF (deve vir após todas as rotas com literal)
    path(
        f"{_BASE_PROF}/<str:rf_professor>/",
        ObterNomePeloRFView.as_view(),
        name="professor-nome-rf",
    ),
]
