"""Repositórios do domínio de cargos."""

from django.db.models import QuerySet

from apps.cargos.models import Cargo


def listar_cargos() -> QuerySet[Cargo]:
    """Lista cargos ativos cadastrados no EOL."""
    return Cargo.objects.filter(dt_cancelamento__isnull=True).order_by(
        "codigo_cargo"
    )
