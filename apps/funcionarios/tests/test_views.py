"""Testes das views mock do domínio Funcionários (EP-25 a EP-39)."""

import json

from django.test import Client, SimpleTestCase, override_settings

API_KEY = "test-key"
HEADERS = {"HTTP_X_API_KEY": API_KEY}


def _json(response):
    return json.loads(response.content)


class _AuthedMixin:
    def setUp(self):
        super().setUp()
        self.authed = _AuthedClient(self.client)


class _AuthedClient:
    def __init__(self, client: Client):
        self._c = client

    def get(self, url: str, **kwargs):
        return self._c.get(url, **{**HEADERS, **kwargs})

    def post(self, url: str, data=None, **kwargs):
        body = json.dumps(data or [])
        return self._c.post(
            url,
            body,
            content_type="application/json",
            **{**HEADERS, **kwargs},
        )


# ---------------------------------------------------------------------------
# EP-25 — Funcionários de uma UE (todos)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP25FuncionariosPorUE(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get("/api/escolas/000532/funcionarios/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        item = _json(self.authed.get("/api/escolas/000532/funcionarios/"))[0]
        for campo in ("codigoRf", "nomeServidor", "cargo"):
            self.assertIn(campo, item)

    def test_sem_api_key_retorna_403(self):
        resp = Client().get("/api/escolas/000532/funcionarios/")
        self.assertEqual(resp.status_code, 403)


# ---------------------------------------------------------------------------
# EP-26 — Funcionários por cargo específico
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP26FuncionariosPorCargo(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/cargos/3239/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_cargo_diferente_retorna_200(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/cargos/3247/"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-26-B — Funcionários por lista de cargos (query)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP26BFuncionariosCargosQuery(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get("/api/escolas/000532/funcionarios/cargos/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_query_cargos(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/cargos/"
            "?cargos=3239&cargos=3247"
        )
        self.assertEqual(resp.status_code, 200)

    def test_com_dre(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/cargos/?dreCodigo=108100"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-27 — Funcionários por função de atividade específica
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP27FuncaoAtividade(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/funcoes-atividades/5/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)


# ---------------------------------------------------------------------------
# EP-27-B — Funcionários por lista de funções de atividade (query)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP27BFuncoesAtividadesQuery(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/funcoes-atividades/"
            "?dreCodigo=108100"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_funcoes_e_dre(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/funcoes-atividades/"
            "?funcoesAtividades=1&funcoesAtividades=2&dreCodigo=108100"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-28 — Funcionários por função externa específica
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP28FuncaoExterna(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/funcoes-externas/10/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_externos(self):
        item = _json(
            self.authed.get(
                "/api/escolas/000532/funcionarios/funcoes-externas/10/"
            )
        )[0]
        for campo in ("cpf", "nomeServidor", "codigoEscola"):
            self.assertIn(campo, item)


# ---------------------------------------------------------------------------
# EP-28-B — Funcionários por lista de funções externas (query)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP28BFuncoesExternasQuery(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/funcoes-externas/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_funcoes_query(self):
        resp = self.authed.get(
            "/api/escolas/000532/funcionarios/funcoes-externas/"
            "?funcoes=10&funcoes=11"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-29 — Cargos do funcionário por RF
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP29CargosFuncionario(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get("/api/funcionarios/cargo/7654321/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_cargo(self):
        item = _json(self.authed.get("/api/funcionarios/cargo/7654321/"))[0]
        for campo in ("codigoRf", "nomeServidor", "cargo", "dataInicio"):
            self.assertIn(campo, item)

    def test_rf_diferente_retorna_200(self):
        resp = self.authed.get("/api/funcionarios/cargo/9999999/")
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-30 — Funcionário externo por CPF
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP30FuncionarioExternoPorCpf(_AuthedMixin, SimpleTestCase):
    def test_retorna_dados(self):
        resp = self.authed.get(
            "/api/funcionarios/funcionario-externo/987.654.321-00/"
        )
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        for campo in ("cpf", "nome", "codigoUe"):
            self.assertIn(campo, data)

    def test_cpf_diferente_retorna_200(self):
        resp = self.authed.get(
            "/api/funcionarios/funcionario-externo/000.000.000-00/"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-31 — Nome e CPF do servidor por RF
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP31NomeServidor(_AuthedMixin, SimpleTestCase):
    def test_retorna_nome_e_cpf(self):
        resp = self.authed.get("/api/funcionarios/nome-servidor/7654321/")
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        for campo in ("codigoRf", "nome", "cpf"):
            self.assertIn(campo, data)

    def test_rf_diferente_retorna_200(self):
        resp = self.authed.get("/api/funcionarios/nome-servidor/9999999/")
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-32 — DRE/UE de atribuição do funcionário
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP32DreUeAtribuicao(_AuthedMixin, SimpleTestCase):
    def test_retorna_dre_ue(self):
        resp = self.authed.get("/api/funcionarios/nome-usuario-eol/7654321/")
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        for campo in ("codigoRf", "nome", "codigoDre", "codigoUe"):
            self.assertIn(campo, data)


# ---------------------------------------------------------------------------
# EP-33 — Servidor ativo
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP33ServidorAtivo(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.get("/api/acessos/funcionario-ativo/7654321/")
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)

    def test_rf_qualquer_retorna_200(self):
        resp = self.authed.get("/api/acessos/funcionario-ativo/9999999/")
        self.assertEqual(resp.status_code, 200)

    def test_sem_api_key_retorna_403(self):
        resp = Client().get("/api/acessos/funcionario-ativo/7654321/")
        self.assertEqual(resp.status_code, 403)


# ---------------------------------------------------------------------------
# EP-34 — DRE/UE do funcionário por cargo
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP34DreUeAtribuicaoCargo(_AuthedMixin, SimpleTestCase):
    def test_retorna_dre_ue_cargo(self):
        resp = self.authed.get(
            "/api/funcionarios/atribuicao/7654321/cargo/3239/"
        )
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        for campo in ("codigoRf", "codigoDre", "codigoUe", "cargo"):
            self.assertIn(campo, data)

    def test_cargo_diferente_retorna_200(self):
        resp = self.authed.get(
            "/api/funcionarios/atribuicao/7654321/cargo/3247/"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-35 — Usuários SGP por perfil
# ---------------------------------------------------------------------------

_PERFIL = "550e8400-e29b-41d4-a716-446655440000"


@override_settings(API_KEY=API_KEY)
class TestEP35UsuariosSGP(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(f"/api/funcionarios/perfis/{_PERFIL}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        resp = self.authed.get(f"/api/funcionarios/perfis/{_PERFIL}/")
        item = _json(resp)[0]
        for campo in ("codigoRf", "nomeServidor", "codigoDre", "codigoUe"):
            self.assertIn(campo, item)

    def test_com_filtros_query(self):
        resp = self.authed.get(
            f"/api/funcionarios/perfis/{_PERFIL}/"
            "?CodigoDre=108100&CodigoUe=000532"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-36 — Funcionários SGP por DRE e perfil
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP36FuncionariosSGPDre(_AuthedMixin, SimpleTestCase):
    def _url(self, suffix=""):
        return f"/api/funcionarios/perfis/{_PERFIL}/dres/108100/{suffix}"

    def test_retorna_lista(self):
        resp = self.authed.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        item = _json(self.authed.get(self._url()))[0]
        for campo in ("codigoRf", "nomeServidor"):
            self.assertIn(campo, item)

    def test_com_filtros(self):
        resp = self.authed.get(
            self._url("?CodigoUe=000532&NomeServidor=Maria")
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-37 — Acesso à sondagem
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP37AcessoSondagem(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.get(
            "/api/perfis/servidores/7654321"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)

    def test_rf_diferente_retorna_200(self):
        resp = self.authed.get(
            "/api/perfis/servidores/9999999"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-38 — Buscar por lista de RF (POST)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP38BuscarPorListaRF(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["7654321", "1234567"],
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        item = _json(
            self.authed.post(
                "/api/funcionarios/BuscarPorListaRF/", ["7654321"]
            )
        )[0]
        for campo in ("codigoRf", "nome", "cpf"):
            self.assertIn(campo, item)

    def test_lista_vazia_retorna_200(self):
        resp = self.authed.post("/api/funcionarios/BuscarPorListaRF/", [])
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-39 — Buscar por lista de login (POST)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP39BuscarPorListaLogin(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.post(
            "/api/funcionarios/BuscarPorListaLogin/",
            ["login1", "login2"],
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        item = _json(
            self.authed.post(
                "/api/funcionarios/BuscarPorListaLogin/", ["login1"]
            )
        )[0]
        for campo in ("codigoRf", "nome", "cpf"):
            self.assertIn(campo, item)

    def test_lista_vazia_retorna_200(self):
        resp = self.authed.post(
            "/api/funcionarios/BuscarPorListaLogin/", []
        )
        self.assertEqual(resp.status_code, 200)

    def test_sem_api_key_retorna_403(self):
        resp = Client().post(
            "/api/funcionarios/BuscarPorListaLogin/",
            json.dumps(["login1"]),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)
