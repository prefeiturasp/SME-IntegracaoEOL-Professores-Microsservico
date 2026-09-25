"""Testes das views do domínio de cargos."""

from datetime import date

import pytest

from apps.cargos.models import Cargo

pytestmark = pytest.mark.django_db

_BASE = "/api/v1/professores"


class TestCargosView:
    def test_retorna_cargos_ativos(self, client):
        Cargo.objects.create(codigo_cargo=3360, nome_cargo="DIRETOR")
        Cargo.objects.create(
            codigo_cargo=9999,
            nome_cargo="CANCELADO",
            dt_cancelamento=date(2024, 1, 1),
        )

        res = client.get(f"{_BASE}/cargos/")

        assert res.status_code == 200
        assert res.data == [
            {"codigoCargo": 3360, "nomeCargo": "DIRETOR"},
        ]

    def test_sem_cargos_retorna_lista_vazia(self, client):
        res = client.get(f"{_BASE}/cargos/")

        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/cargos/")

        assert res.status_code == 403
