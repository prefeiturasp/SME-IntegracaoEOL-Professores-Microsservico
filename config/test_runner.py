"""Executor de testes customizado do microsserviço."""

from typing import Any

from django.apps import apps
from django.db import connections
from django.test.runner import DiscoverRunner


class ProfessoresTestRunner(DiscoverRunner):
    """Prepara tabelas externas antes de executar os testes."""

    def setup_databases(self, **kwargs: Any) -> Any:
        """Configura bancos de teste e cria tabelas externas.

        Args:
            **kwargs: Opções repassadas ao runner do Django.

        Returns:
            Configuração dos bancos criada pelo runner.
        """
        result = super().setup_databases(**kwargs)
        with connections["default"].schema_editor() as editor:
            criadas: set[str] = set()
            for model in apps.get_models():
                if not model._meta.managed:
                    table = model._meta.db_table
                    if table not in criadas:
                        editor.create_model(model)
                        criadas.add(table)
        return result
