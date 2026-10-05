from django.apps import AppConfig


class FuncionariosConfig(AppConfig):
    """Configura o app de funcionários."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.funcionarios"
    label = "funcionarios"
