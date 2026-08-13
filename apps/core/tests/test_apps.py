"""Testes da inicialização do app core."""

from unittest.mock import patch

import apps.core
from apps.core.apps import CoreConfig


def test_ready_configura_runtime_do_sdk() -> None:
    """Inicializa o runtime do SDK quando o app Django fica pronto."""
    app_config = CoreConfig("core", apps.core)

    with patch("sme_sidecar_sdk.runtime.configure") as configure:
        app_config.ready()

    configure.assert_called_once_with()
