"""Utilitários compartilhados entre os apps do MS Professores."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

# Época base do .NET DateTime.Ticks: 0001-01-01 00:00:00 UTC
_DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=timezone.utc)


def ticks_to_date(ticks: int) -> date:
    """Converte .NET DateTime.Ticks (100-nanosecond intervals) para date."""
    return (_DOTNET_EPOCH + timedelta(microseconds=ticks // 10)).date()


def get_nome(obj: Any) -> str:
    """Retorna nome_social quando preenchido, caso contrário retorna nome (P9)."""
    nome_social = getattr(obj, "nome_social", None)
    if nome_social and nome_social.strip():
        return nome_social
    return obj.nome
