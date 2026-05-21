"""Rotas da API do domínio de funcionários."""

from django.urls import path

from apps.funcionarios.api.views import (
    AcessoSondagemView,
    BuscarPorListaLoginView,
    BuscarPorListaRFView,
    CargosFuncionarioView,
    DreUeAtribuicaoCargoView,
    NomeUsuarioEOLView,
    FuncionarioExternoPorCpfView,
    FuncionariosPorUEView,
    FuncionariosSGPDreView,
    NomeCPFServidorView,
    ServidorAtivoView,
    UsuariosSGPView,
)

_BASE_ACESSOS = "professores/acessos"
_BASE_ESCOLAS = "professores/escolas"
_BASE_FUNCIONARIOS = "professores/funcionarios"
_BASE_PERFIS = "professores/perfis"

urlpatterns = [
    path(
        f"{_BASE_ESCOLAS}/<str:codigo_ue>/funcionarios/",
        FuncionariosPorUEView.as_view(),
        name="funcionarios-ue",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/cargo/<str:registro_funcional>/",
        CargosFuncionarioView.as_view(),
        name="funcionarios-cargos-rf",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/funcionario-externo/<str:cpf>/",
        FuncionarioExternoPorCpfView.as_view(),
        name="funcionario-externo-cpf",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/nome-servidor/<str:registro_funcional>/",
        NomeCPFServidorView.as_view(),
        name="funcionario-nome-servidor",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/nome-usuario-eol/<str:registro_funcional>/",
        NomeUsuarioEOLView.as_view(),
        name="funcionario-nome-usuario-eol",
    ),
    path(
        f"{_BASE_ACESSOS}/funcionario-ativo/<str:registro_funcional>/",
        ServidorAtivoView.as_view(),
        name="funcionario-ativo",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/atribuicao/<str:registro_funcional>/"
        "cargo/<int:codigo_cargo>/",
        DreUeAtribuicaoCargoView.as_view(),
        name="funcionario-atribuicao-cargo",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/perfis/<str:id_perfil>/",
        UsuariosSGPView.as_view(),
        name="funcionarios-perfil",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/perfis/<str:id_perfil>/dres/<str:codigo_dre>/",
        FuncionariosSGPDreView.as_view(),
        name="funcionarios-perfil-dre",
    ),
    path(
        f"{_BASE_PERFIS}/servidores/<str:codigo_rf>/"
        "VerificaSeProfessorTemAcessoAhSondagem/",
        AcessoSondagemView.as_view(),
        name="professor-acesso-sondagem",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaRF/",
        BuscarPorListaRFView.as_view(),
        name="funcionarios-buscar-lista-rf",
    ),
    path(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaLogin/",
        BuscarPorListaLoginView.as_view(),
        name="funcionarios-buscar-lista-login",
    ),
]
