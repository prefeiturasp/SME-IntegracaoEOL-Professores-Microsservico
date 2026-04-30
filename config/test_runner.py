"""Test runner customizado para o MS Professores."""

from django.apps import apps
from django.db import connections
from django.test.runner import DiscoverRunner


class ProfessoresTestRunner(DiscoverRunner):
    """Cria tabelas managed=False no banco de testes antes de executar os testes."""

    def setup_databases(self, **kwargs):
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
