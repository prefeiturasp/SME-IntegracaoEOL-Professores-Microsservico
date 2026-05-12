"""Rotas da API do domínio Funcionários."""

from django.urls import path

from apps.funcionarios.api.views import (
    AcessoSondagemView,
    BuscarPorListaLoginView,
    BuscarPorListaRFView,
    CargosFuncionarioView,
    DreUeAtribuicaoCargoView,
    DreUeAtribuicaoFuncionarioView,
    FuncionarioExternoPorCpfView,
    FuncionariosCargosQueryView,
    FuncionariosFuncaoAtividadeView,
    FuncionariosFuncaoExternaView,
    FuncionariosFuncoesAtividadesQueryView,
    FuncionariosFuncoesExternasQueryView,
    FuncionariosPorUEView,
    FuncionariosSGPDreView,
    NomeServidorView,
    ServidorAtivoView,
    UsuariosSGPView,
)

_BASE_ACESSOS = "professores/acessos"
_BASE_ESCOLAS = "professores/escolas"
_BASE_FUNCIONARIOS = "professores/funcionarios"
_BASE_PERFIS = "professores/perfis"

urlpatterns = [
    # EP-25 — Todos os funcionários de uma UE
    path(
        f"{_BASE_ESCOLAS}/<str:codigo_ue>/funcionarios/",
        FuncionariosPorUEView.as_view(),
        name="funcionarios-ue",
    ),
    # EP-26 — Funcionários de uma UE por cargo específico
    path(
        f"{_BASE_ESCOLAS}/<str:codigo_ue>/funcionarios/"
        "cargos/<int:codigo_cargo>/",
        FuncionariosPorUEView.as_view(),
        name="funcionarios-ue-cargo",
    ),
    # EP-26-B — Funcionários de uma UE por lista de cargos (query)
    path(
        f"{_BASE_ESCOLAS}/<str:ue_codigo>/funcionarios/cargos/",
        FuncionariosCargosQueryView.as_view(),
        name="funcionarios-ue-cargos-lista",
    ),
    # EP-27 — Funcionários de uma UE por função de atividade específica
    path(
        f"{_BASE_ESCOLAS}/<str:codigo_ue>/funcionarios/"
        "funcoes-atividades/<int:codigo_funcao_atividade>/",
        FuncionariosFuncaoAtividadeView.as_view(),
        name="funcionarios-ue-funcao-atividade",
    ),
    # EP-27-B — Funcionários de uma UE por lista de funções de atividade
    path(
        f"{_BASE_ESCOLAS}/<str:ue_codigo>/funcionarios/funcoes-atividades/",
        FuncionariosFuncoesAtividadesQueryView.as_view(),
        name="funcionarios-ue-funcoes-atividades-lista",
    ),
    # EP-28 — Funcionários de uma UE por função externa específica
    path(
        f"{_BASE_ESCOLAS}/<str:codigo_ue>/funcionarios/"
        "funcoes-externas/<int:codigo_funcao_externa>/",
        FuncionariosFuncaoExternaView.as_view(),
        name="funcionarios-ue-funcao-externa",
    ),
    # EP-28-B — Funcionários de uma UE por lista de funções externas (query)
    path(
        f"{_BASE_ESCOLAS}/<str:ue_codigo>/funcionarios/funcoes-externas/",
        FuncionariosFuncoesExternasQueryView.as_view(),
        name="funcionarios-ue-funcoes-externas-lista",
    ),
    # EP-29 — Cargos do funcionário por RF
    path(
        f"{_BASE_FUNCIONARIOS}/cargo/<str:registro_funcional>/",
        CargosFuncionarioView.as_view(),
        name="funcionarios-cargos-rf",
    ),
    # EP-30 — Funcionário externo por CPF
    path(
        f"{_BASE_FUNCIONARIOS}/funcionario-externo/<str:cpf>/",
        FuncionarioExternoPorCpfView.as_view(),
        name="funcionario-externo-cpf",
    ),
    # EP-31 — Nome e CPF do servidor por RF
    path(
        f"{_BASE_FUNCIONARIOS}/nome-servidor/<str:registro_funcional>/",
        NomeServidorView.as_view(),
        name="funcionario-nome-servidor",
    ),
    # EP-32 — DRE/UE de atribuição do funcionário (nome-usuario-eol)
    path(
        f"{_BASE_FUNCIONARIOS}/nome-usuario-eol/<str:registro_funcional>/",
        DreUeAtribuicaoFuncionarioView.as_view(),
        name="funcionario-nome-usuario-eol",
    ),
    # EP-33 — Servidor ativo
    path(
        f"{_BASE_ACESSOS}/funcionario-ativo/<str:registro_funcional>/",
        ServidorAtivoView.as_view(),
        name="funcionario-ativo",
    ),
    # EP-34 — DRE/UE do funcionário por cargo
    path(
        f"{_BASE_FUNCIONARIOS}/atribuicao/<str:registro_funcional>/"
        "cargo/<int:codigo_cargo>/",
        DreUeAtribuicaoCargoView.as_view(),
        name="funcionario-atribuicao-cargo",
    ),
    # EP-35 — Usuários SGP por perfil
    path(
        f"{_BASE_FUNCIONARIOS}/perfis/<str:id_perfil>/",
        UsuariosSGPView.as_view(),
        name="funcionarios-perfil",
    ),
    # EP-36 — Funcionários SGP por DRE e perfil
    path(
        f"{_BASE_FUNCIONARIOS}/perfis/<str:id_perfil>/dres/<str:codigo_dre>/",
        FuncionariosSGPDreView.as_view(),
        name="funcionarios-perfil-dre",
    ),
    # EP-37 — Acesso à sondagem
    path(
        f"{_BASE_PERFIS}/servidores/<str:codigo_rf>/"
        "VerificaSeProfessorTemAcessoAhSondagem/",
        AcessoSondagemView.as_view(),
        name="professor-acesso-sondagem",
    ),
    # EP-38 — Buscar por lista de RF (POST)
    path(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaRF/",
        BuscarPorListaRFView.as_view(),
        name="funcionarios-buscar-lista-rf",
    ),
    # EP-39 — Buscar por lista de login (POST)
    path(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaLogin/",
        BuscarPorListaLoginView.as_view(),
        name="funcionarios-buscar-lista-login",
    ),
]
