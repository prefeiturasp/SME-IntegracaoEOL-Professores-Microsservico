"""Testes das views mock do domínio Turmas (EP-24)."""

import json

from django.test import Client, SimpleTestCase, override_settings

API_KEY = "test-key"
HEADERS = {"HTTP_X_API_KEY": API_KEY}

_URL = (
    "/api/turmas/anos-letivos/{ano}/professor/{rf}"
    "/turmas-historicas-geral/"
)


def _json(response):
    return json.loads(response.content)


# ---------------------------------------------------------------------------
# EP-24 — Turmas históricas do professor por ano
# ---------------------------------------------------------------------------


@override_settings(API_KEY=API_KEY)
class TestEP24TurmasHistoricas(SimpleTestCase):
    def _get(self, ano=2024, rf="7654321"):
        return self.client.get(
            _URL.format(ano=ano, rf=rf), **HEADERS
        )

    def test_retorna_lista(self):
        resp = self._get()
        self.assertEqual(resp.status_code, 200)
        data = _json(resp)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_campos_presentes(self):
        item = _json(self._get())[0]
        for campo in (
            "codigoTurma",
            "nomeTurma",
            "codigoEscola",
            "anoLetivo",
            "status",
        ):
            self.assertIn(campo, item)

    def test_inclui_turmas_extintas(self):
        statuses = [t["status"] for t in _json(self._get())]
        self.assertIn("E", statuses)

    def test_inclui_turmas_ativas(self):
        statuses = [t["status"] for t in _json(self._get())]
        self.assertIn("A", statuses)

    def test_rf_diferente_retorna_200(self):
        resp = self._get(ano=2023, rf="9999999")
        self.assertEqual(resp.status_code, 200)

    def test_sem_api_key_retorna_403(self):
        resp = Client().get(_URL.format(ano=2024, rf="7654321"))
        self.assertEqual(resp.status_code, 403)
