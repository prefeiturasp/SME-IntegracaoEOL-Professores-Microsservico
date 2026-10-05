"""Models do domínio de cargos."""

from django.db import models


class Cargo(models.Model):
    """Representa cargo cadastrado no EOL."""

    codigo_cargo = models.IntegerField(primary_key=True)
    nome_cargo = models.CharField(max_length=100)
    dt_cancelamento = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "cargos"
        db_table = "cargo"
        managed = False
