from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configura o app de utilitários compartilhados."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
