"""Serviços do domínio de cargos."""

from django.db.models import QuerySet

from apps.cargos import repositories
from apps.cargos.models import Cargo


def listar_cargos() -> QuerySet[Cargo]:
    """Lista cargos ativos cadastrados no EOL."""
    return repositories.listar_cargos()
