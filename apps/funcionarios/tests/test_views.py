"""Testes das views mock do domínio Funcionários (EP-25 a EP-39)."""

import json

import pytest
from django.test import Client

API_KEY = "test-key"
HEADERS = {"HTTP_X_API_KEY": API_KEY}

_URL_FUNCIONARIOS_UE = "/api/escolas/000532/funcionarios/"
_URL_CARGO_RF = "/api/funcionarios/cargo/7654321/"
_URL_NOME_SERVIDOR = "/api/funcionarios/nome-servidor/7654321/"
_URL_NOME_USUARIO_EOL = "/api/funcionarios/nome-usuario-eol/7654321/"
_URL_FUNCIONARIO_ATIVO = "/api/acessos/funcionario-ativo/7654321/"
_PERFIL_UUID = "550e8400-e29b-41d4-a716-446655440000"
_DRE_CODIGO = "108100"


@pytest.fixture()
def authed(settings):
    """Cliente HTTP autenticado com API_KEY para os testes."""
    settings.API_KEY = API_KEY
    c = Client()

    class _Authed:
        def get(self, url, **kwargs):
            return c.get(url, **{**HEADERS, **kwargs})

        def post(self, url, data=None, **kwargs):
            body = json.dumps(data or [])
            return c.post(
                url,
                body,
                content_type="application/json",
                **{**HEADERS, **kwargs},
            )

    return _Authed()


def _json(response):
    return json.loads(response.content)


# ---------------------------------------------------------------------------
# EP-25 — Funcionários de uma UE (todos)
# ---------------------------------------------------------------------------



class TestEP25FuncionariosPorUE:
    def test_retorna_lista(self, authed):
        resp = authed.get(_URL_FUNCIONARIOS_UE)
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_campos_presentes(self, authed):
        resp = authed.get(_URL_FUNCIONARIOS_UE)
        item = _json(resp)[0]
        for campo in ("codigoRf", "nomeServidor", "cargo"):
            assert campo in item

    def test_sem_api_key_retorna_403(self, settings):
        settings.API_KEY = API_KEY
        resp = Client().get(_URL_FUNCIONARIOS_UE)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# EP-26 — Funcionários por cargo específico
# ---------------------------------------------------------------------------



class TestEP26FuncionariosPorCargo:
    def test_retorna_lista(self, authed):
        resp = authed.get("/api/escolas/000532/funcionarios/cargos/3239/")
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_cargo_diferente_retorna_200(self, authed):
        resp = authed.get("/api/escolas/000532/funcionarios/cargos/3247/")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-26-B — Funcionários por lista de cargos (query)
# ---------------------------------------------------------------------------



class TestEP26BFuncionariosCargosQuery:
    def test_retorna_lista(self, authed):
        resp = authed.get("/api/escolas/000532/funcionarios/cargos/")
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_com_query_cargos(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/cargos/?cargos=3239&cargos=3247"
        )
        assert resp.status_code == 200

    def test_com_dre(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/cargos/?dreCodigo=108100"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-27 — Funcionários por função de atividade específica
# ---------------------------------------------------------------------------



class TestEP27FuncaoAtividade:
    def test_retorna_lista(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/funcoes-atividades/5/"
        )
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)


# ---------------------------------------------------------------------------
# EP-27-B — Funcionários por lista de funções de atividade (query)
# ---------------------------------------------------------------------------



class TestEP27BFuncoesAtividadesQuery:
    def test_retorna_lista(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/funcoes-atividades/"
            "?dreCodigo=108100"
        )
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_com_funcoes_e_dre(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/funcoes-atividades/"
            "?funcoesAtividades=1&funcoesAtividades=2&dreCodigo=108100"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-28 — Funcionários por função externa específica
# ---------------------------------------------------------------------------



class TestEP28FuncaoExterna:
    def test_retorna_lista(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/funcoes-externas/10/"
        )
        assert resp.status_code == 200
        data = _json(resp)
        assert isinstance(data, list)

    def test_campos_externos(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/funcoes-externas/10/"
        )
        item = _json(resp)[0]
        for campo in ("cpf", "nomeServidor", "codigoEscola"):
            assert campo in item


# ---------------------------------------------------------------------------
# EP-28-B — Funcionários por lista de funções externas (query)
# ---------------------------------------------------------------------------



class TestEP28BFuncoesExternasQuery:
    def test_retorna_lista(self, authed):
        resp = authed.get("/api/escolas/000532/funcionarios/funcoes-externas/")
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_com_funcoes_query(self, authed):
        resp = authed.get(
            "/api/escolas/000532/funcionarios/funcoes-externas/"
            "?funcoes=10&funcoes=11"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-29 — Cargos do funcionário por RF
# ---------------------------------------------------------------------------



class TestEP29CargosFuncionario:
    def test_retorna_lista(self, authed):
        resp = authed.get(_URL_CARGO_RF)
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_campos_cargo(self, authed):
        resp = authed.get(_URL_CARGO_RF)
        item = _json(resp)[0]
        for campo in ("codigoRf", "nomeServidor", "cargo", "dataInicio"):
            assert campo in item

    def test_rf_diferente_retorna_200(self, authed):
        resp = authed.get("/api/funcionarios/cargo/9999999/")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-30 — Funcionário externo por CPF
# ---------------------------------------------------------------------------



class TestEP30FuncionarioExternoPorCpf:
    def test_retorna_dados(self, authed):
        resp = authed.get(
            "/api/funcionarios/funcionario-externo/987.654.321-00/"
        )
        assert resp.status_code == 200
        data = _json(resp)
        for campo in ("cpf", "nome", "codigoUe"):
            assert campo in data

    def test_cpf_diferente_retorna_200(self, authed):
        resp = authed.get(
            "/api/funcionarios/funcionario-externo/000.000.000-00/"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-31 — Nome e CPF do servidor por RF
# ---------------------------------------------------------------------------



class TestEP31NomeServidor:
    def test_retorna_nome_e_cpf(self, authed):
        resp = authed.get(_URL_NOME_SERVIDOR)
        assert resp.status_code == 200
        data = _json(resp)
        for campo in ("codigoRf", "nome", "cpf"):
            assert campo in data

    def test_rf_diferente_retorna_200(self, authed):
        resp = authed.get("/api/funcionarios/nome-servidor/9999999/")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-32 — DRE/UE de atribuição do funcionário
# ---------------------------------------------------------------------------



class TestEP32DreUeAtribuicao:
    def test_retorna_dre_ue(self, authed):
        resp = authed.get(_URL_NOME_USUARIO_EOL)
        assert resp.status_code == 200
        data = _json(resp)
        for campo in ("codigoRf", "nome", "codigoDre", "codigoUe"):
            assert campo in data


# ---------------------------------------------------------------------------
# EP-33 — Servidor ativo
# ---------------------------------------------------------------------------



class TestEP33ServidorAtivo:
    def test_retorna_true(self, authed):
        resp = authed.get(_URL_FUNCIONARIO_ATIVO)
        assert resp.status_code == 200
        assert _json(resp) is True

    def test_rf_qualquer_retorna_200(self, authed):
        resp = authed.get("/api/acessos/funcionario-ativo/9999999/")
        assert resp.status_code == 200

    def test_sem_api_key_retorna_403(self, settings):
        settings.API_KEY = API_KEY
        resp = Client().get(_URL_FUNCIONARIO_ATIVO)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# EP-34 — DRE/UE do funcionário por cargo
# ---------------------------------------------------------------------------



class TestEP34DreUeAtribuicaoCargo:
    def test_retorna_dre_ue_cargo(self, authed):
        resp = authed.get(
            "/api/funcionarios/atribuicao/7654321/cargo/3239/"
        )
        assert resp.status_code == 200
        data = _json(resp)
        for campo in ("codigoRf", "codigoDre", "codigoUe", "cargo"):
            assert campo in data

    def test_cargo_diferente_retorna_200(self, authed):
        resp = authed.get(
            "/api/funcionarios/atribuicao/7654321/cargo/3247/"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-35 — Usuários SGP por perfil
# ---------------------------------------------------------------------------



class TestEP35UsuariosSGP:
    def test_retorna_lista(self, authed):
        resp = authed.get(f"/api/funcionarios/perfis/{_PERFIL_UUID}/")
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_campos_presentes(self, authed):
        resp = authed.get(f"/api/funcionarios/perfis/{_PERFIL_UUID}/")
        item = _json(resp)[0]
        for campo in ("codigoRf", "nomeServidor", "codigoDre", "codigoUe"):
            assert campo in item

    def test_com_filtros_query(self, authed):
        resp = authed.get(
            f"/api/funcionarios/perfis/{_PERFIL_UUID}/"
            "?CodigoDre=108100&CodigoUe=000532"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-36 — Funcionários SGP por DRE e perfil
# ---------------------------------------------------------------------------



class TestEP36FuncionariosSGPDre:
    def test_retorna_lista(self, authed):
        resp = authed.get(
            f"/api/funcionarios/perfis/{_PERFIL_UUID}/dres/{_DRE_CODIGO}/"
        )
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_campos_presentes(self, authed):
        resp = authed.get(
            f"/api/funcionarios/perfis/{_PERFIL_UUID}/dres/{_DRE_CODIGO}/"
        )
        item = _json(resp)[0]
        for campo in ("codigoRf", "nomeServidor"):
            assert campo in item

    def test_com_filtros(self, authed):
        resp = authed.get(
            f"/api/funcionarios/perfis/{_PERFIL_UUID}/dres/{_DRE_CODIGO}/"
            "?CodigoUe=000532&NomeServidor=Maria"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-37 — Acesso à sondagem
# ---------------------------------------------------------------------------



class TestEP37AcessoSondagem:
    def test_retorna_true(self, authed):
        resp = authed.get(
            "/api/perfis/servidores/7654321"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        assert resp.status_code == 200
        assert _json(resp) is True

    def test_rf_diferente_retorna_200(self, authed):
        resp = authed.get(
            "/api/perfis/servidores/9999999"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-38 — Buscar por lista de RF (POST)
# ---------------------------------------------------------------------------



class TestEP38BuscarPorListaRF:
    def test_retorna_lista(self, authed):
        resp = authed.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["7654321", "1234567"],
        )
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_campos_presentes(self, authed):
        resp = authed.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["7654321"],
        )
        item = _json(resp)[0]
        for campo in ("codigoRf", "nome", "cpf"):
            assert campo in item

    def test_lista_vazia_retorna_200(self, authed):
        resp = authed.post("/api/funcionarios/BuscarPorListaRF/", [])
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# EP-39 — Buscar por lista de login (POST)
# ---------------------------------------------------------------------------



class TestEP39BuscarPorListaLogin:
    def test_retorna_lista(self, authed):
        resp = authed.post(
            "/api/funcionarios/BuscarPorListaLogin/",
            ["login1", "login2"],
        )
        assert resp.status_code == 200
        assert isinstance(_json(resp), list)

    def test_campos_presentes(self, authed):
        resp = authed.post(
            "/api/funcionarios/BuscarPorListaLogin/",
            ["login1"],
        )
        item = _json(resp)[0]
        for campo in ("codigoRf", "nome", "cpf"):
            assert campo in item

    def test_lista_vazia_retorna_200(self, authed):
        resp = authed.post("/api/funcionarios/BuscarPorListaLogin/", [])
        assert resp.status_code == 200

    def test_sem_api_key_retorna_403(self, settings):
        settings.API_KEY = API_KEY
        resp = Client().post(
            "/api/funcionarios/BuscarPorListaLogin/",
            json.dumps(["login1"]),
            content_type="application/json",
        )
        assert resp.status_code == 403
