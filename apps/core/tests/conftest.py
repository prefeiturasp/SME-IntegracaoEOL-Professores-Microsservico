"""Configura armazenamento e relógio para testes das leituras."""

import time
from uuid import uuid4

import pytest


@pytest.fixture
def cache_ativo(settings):
    """Habilita armazenamento exclusivo para cada teste."""
    settings.PROFESSORES_CACHE_ENABLED = True
    settings.PROFESSORES_CACHE_TTL = 300
    settings.PROFESSORES_CACHE_MAX_BYTES = 16 * 1024 * 1024
    settings.PROFESSORES_CACHE_LOCK_SECONDS = 30
    settings.PROFESSORES_CACHE_WAIT_SECONDS = 0
    settings.CACHES = {
        "professores": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": str(uuid4()),
        },
    }


@pytest.fixture
def relogio(monkeypatch):
    """Permite avançar o horário sem aguardar a passagem do tempo."""
    agora = [time.time()]
    monkeypatch.setattr(time, "time", lambda: agora[0])
    return agora
