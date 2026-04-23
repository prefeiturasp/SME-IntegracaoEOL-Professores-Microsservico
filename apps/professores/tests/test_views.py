"""Testes das views mock do domínio Professores (EP-01 a EP-23)."""

import json

from django.test import Client, SimpleTestCase, override_settings

API_KEY = "test-key"
HEADERS = {"HTTP_X_API_KEY": API_KEY}


def _json(response):
    return json.loads(response.content)


class _AuthedMixin:
    """Mixin que fornece client autenticado e helper de requisição."""

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
# Autenticação
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestAutenticacaoEndpoints(SimpleTestCase):
    def test_sem_api_key_retorna_403(self):
        resp = self.client.get("/api/professores/7654321/")
        self.assertEqual(resp.status_code, 403)

    def test_com_api_key_invalida_retorna_403(self):
        resp = self.client.get(
            "/api/professores/7654321/", HTTP_X_API_KEY="errada"
        )
        self.assertEqual(resp.status_code, 403)

    def test_com_api_key_valida_retorna_200(self):
        resp = self.client.get(
            "/api/professores/7654321/", **HEADERS
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-01 — Professores da escola
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP01BuscaProfessores(_AuthedMixin, SimpleTestCase):
    def test_sem_ano_retorna_lista(self):
        resp = self.authed.get("/api/escolas/000532/professores/")
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_com_ano_retorna_lista(self):
        resp = self.authed.get("/api/escolas/000532/professores/2024/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        resp = self.authed.get("/api/escolas/000532/professores/2024/")
        item = _json(resp)[0]
        for campo in ("codigoRf", "nome", "cpf", "cargo", "codigoTurma"):
            self.assertIn(campo, item)


# ---------------------------------------------------------------------------
# EP-02 — Turmas atribuídas (escola + ano)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP02TurmasAtribuidasEscola(_AuthedMixin, SimpleTestCase):
    def test_sem_rf_retorna_lista(self):
        resp = self.authed.get(
            "/api/professores/escolas/000532/turmas/anos_letivos/2024/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_rf_retorna_lista(self):
        resp = self.authed.get(
            "/api/professores/7654321/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_campos_atribuicao_presentes(self):
        resp = self.authed.get(
            "/api/professores/7654321/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        item = _json(resp)[0]
        for campo in ("codigoTurma", "codigoEscola", "anoAtribuicao"):
            self.assertIn(campo, item)


# ---------------------------------------------------------------------------
# EP-03 / EP-04 — Turmas do professor
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP03EP04TurmasAtribuidas(_AuthedMixin, SimpleTestCase):
    def test_todas_turmas(self):
        resp = self.authed.get("/api/professores/7654321/turmas/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_turmas_por_ano(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/anos_letivos/2024/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)


# ---------------------------------------------------------------------------
# EP-05 — Nome pelo RF
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP05NomePeloRF(_AuthedMixin, SimpleTestCase):
    def test_retorna_codigoRf_e_nome(self):
        resp = self.authed.get("/api/professores/7654321/")
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        self.assertEqual(data["codigoRf"], "7654321")
        self.assertIn("nome", data)

    def test_rf_diferente_ainda_retorna_200(self):
        resp = self.authed.get("/api/professores/9999999/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(_json(resp)["codigoRf"], "9999999")


# ---------------------------------------------------------------------------
# EP-06 — BuscarPorRf
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP06BuscarPorRf(_AuthedMixin, SimpleTestCase):
    def test_retorna_200(self):
        resp = self.authed.get("/api/professores/7654321/BuscarPorRf/2024/")
        self.assertEqual(resp.status_code, 200)

    def test_campos_presentes(self):
        resp = self.authed.get("/api/professores/7654321/BuscarPorRf/2024/")
        data = _json(resp)
        for campo in ("codigoRf", "nome", "cpf", "codigoTurma"):
            self.assertIn(campo, data)

    def test_query_param_buscarOutrosCargos(self):
        resp = self.authed.get(
            "/api/professores/7654321/BuscarPorRf/2024/"
            "?buscarOutrosCargos=true"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-07 — BuscarPorRfDreUe
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP07BuscarPorRfDreUe(_AuthedMixin, SimpleTestCase):
    def test_retorna_200(self):
        resp = self.authed.get(
            "/api/professores/7654321/BuscarPorRfDreUe/2024/"
        )
        self.assertEqual(resp.status_code, 200)

    def test_com_filtros_retorna_200(self):
        resp = self.authed.get(
            "/api/professores/7654321/BuscarPorRfDreUe/2024/"
            "?dreId=108100&ueId=000532"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-08 — AutoComplete
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP08AutoComplete(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get("/api/professores/2024/AutoComplete/108100/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        resp = self.authed.get("/api/professores/2024/AutoComplete/108100/")
        item = _json(resp)[0]
        self.assertIn("codigoRf", item)
        self.assertIn("nomeServidor", item)

    def test_com_filtro_nome(self):
        resp = self.authed.get(
            "/api/professores/2024/AutoComplete/108100/?nome=Maria"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-09 — BuscarPorListaRF (POST)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP09BuscarPorListaRF(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.post(
            "/api/professores/2024/BuscarPorListaRF/",
            ["7654321", "1234567"],
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_retornados(self):
        resp = self.authed.post(
            "/api/professores/2024/BuscarPorListaRF/",
            ["7654321"],
        )
        item = _json(resp)[0]
        for campo in ("codigoRf", "nome", "cpf"):
            self.assertIn(campo, item)

    def test_lista_vazia_retorna_200(self):
        resp = self.authed.post(
            "/api/professores/2024/BuscarPorListaRF/", []
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-10 — Validade
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP10Validade(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.get("/api/professores/7654321/validade/")
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)


# ---------------------------------------------------------------------------
# EP-11 — EhEmei
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP11EhEmei(_AuthedMixin, SimpleTestCase):
    def test_retorna_false(self):
        resp = self.authed.get("/api/professores/7654321/ehEmei/")
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), False)


# ---------------------------------------------------------------------------
# EP-12 — Status de atribuição
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP12AtribuicaoStatus(_AuthedMixin, SimpleTestCase):
    def test_retorna_possui_atribuicao(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        self.assertIs(data["possuiAtribuicao"], True)
        self.assertEqual(data["codigoRf"], "7654321")
        self.assertEqual(data["codigoTurma"], 2112345)


# ---------------------------------------------------------------------------
# EP-13 — Verificar atribuição em data
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP13AtribuicaoVerificarData(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/atribuicao/verificar/data/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)

    def test_com_data_consulta(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/atribuicao/verificar/data/?dataConsulta=2024-06-01"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-14 — Verificar atribuição disciplina em data
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP14AtribuicaoDisciplinaData(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)

    def test_com_territorio_saber(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
            "?territorioSaber=true"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-15 — Verificar atribuição disciplina via datatick
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP15AtribuicaoDisciplinaDataTick(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)

    def test_com_tick(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
            "?dataConsultaTick=638000000000000000"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-16 — Recorrência de datas
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP16AtribuicaoRecorrenciaDatas(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_por_data(self):
        resp = self.authed.get(
            "/api/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
        )
        item = _json(resp)[0]
        self.assertIn("data", item)
        self.assertIn("possuiAtribuicao", item)


# ---------------------------------------------------------------------------
# EP-17 — Verificar atribuição em lista de turmas (POST)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP17AtribuicaoTurmasLista(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.post(
            "/api/professores/7654321/disciplina/138/turmas/",
            [2112345, 2112346],
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_turma(self):
        resp = self.authed.post(
            "/api/professores/7654321/disciplina/138/turmas/",
            [2112345],
        )
        item = _json(resp)[0]
        self.assertIn("codigoTurma", item)
        self.assertIn("possuiAtribuicao", item)


# ---------------------------------------------------------------------------
# EP-18 — Atribuição em período (POST)
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP18AtribuicaoPeriodo(_AuthedMixin, SimpleTestCase):
    def test_retorna_true(self):
        resp = self.authed.post(
            "/api/professores/7654321/turmas/2112345"
            "/componentes/138/atribuicao/periodo"
            "/inicio/2024-02-01/fim/2024-12-20/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIs(_json(resp), True)


# ---------------------------------------------------------------------------
# EP-19 — Professores atribuídos turma/disciplina em data
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP19ProfessoresAtribuidosTurmaDisc(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_campos_presentes(self):
        resp = self.authed.get(
            "/api/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        item = _json(resp)[0]
        for campo in (
            "codigoRf",
            "nome",
            "cpf",
            "codigoComponenteCurricular",
            "atribuicaoExterna",
        ):
            self.assertIn(campo, item)

    def test_com_datatick(self):
        resp = self.authed.get(
            "/api/professores/2112345/disciplinas/138/atribuicao/data/"
            "?dataTicks=638000000000000000"
        )
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# EP-20 — Titular por turma e disciplina
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP20TitularPorTurmaDisciplina(_AuthedMixin, SimpleTestCase):
    def test_retorna_titular(self):
        resp = self.authed.get(
            "/api/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        for campo in ("codigoRf", "nome", "cpf"):
            self.assertIn(campo, data)


# ---------------------------------------------------------------------------
# EP-21 — Titulares por lista de turmas
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP21TitularesPorTurmas(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get("/api/professores/titulares/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_query_turmas(self):
        resp = self.authed.get(
            "/api/professores/titulares/"
            "?codigosTurmas=2112345&codigosTurmas=2112346"
        )
        self.assertEqual(resp.status_code, 200)

    def test_campos_presentes(self):
        resp = self.authed.get("/api/professores/titulares/")
        item = _json(resp)[0]
        self.assertIn("codigoTurma", item)
        self.assertIn("codigoRf", item)


# ---------------------------------------------------------------------------
# EP-22 — Titulares por turma com agrupamento
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP22TitularesPorTurmaAgrupamento(_AuthedMixin, SimpleTestCase):
    def test_sem_agrupamento(self):
        resp = self.authed.get(
            "/api/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/false/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_agrupamento(self):
        resp = self.authed.get(
            "/api/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/true/"
        )
        self.assertEqual(resp.status_code, 200)

    def test_campos_presentes(self):
        resp = self.authed.get(
            "/api/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/true/"
        )
        item = _json(resp)[0]
        self.assertIn("codigoRf", item)
        self.assertIn("codigoComponenteCurricular", item)


# ---------------------------------------------------------------------------
# EP-23 — Titulares por UE e data de referência
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP23TitularesPorUe(_AuthedMixin, SimpleTestCase):
    def test_retorna_lista(self):
        resp = self.authed.get(
            "/api/professores/titulares/ue/000532/2024-06-01/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(_json(resp), list)

    def test_com_agrupamento_query(self):
        resp = self.authed.get(
            "/api/professores/titulares/ue/000532/2024-06-01/"
            "?realizaAgrupamento=true"
        )
        self.assertEqual(resp.status_code, 200)
