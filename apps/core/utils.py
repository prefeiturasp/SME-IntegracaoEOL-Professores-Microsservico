"""Utilitários compartilhados entre os apps do microsserviço."""

from datetime import UTC, date, datetime, timedelta
from typing import Any

_DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=UTC)


def ticks_to_date(ticks: int) -> date:
    """Retorna data a partir de ticks do .NET DateTime."""
    return (_DOTNET_EPOCH + timedelta(microseconds=ticks // 10)).date()


def ticks_to_datetime_str(ticks: int) -> str:
    """Retorna string ISO datetime a partir de ticks do .NET."""
    dt = _DOTNET_EPOCH + timedelta(microseconds=ticks // 10)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def fmt_br(d: Any) -> str | None:
    """Formata date ou datetime no padrão MM/DD/YYYY HH:mm:ss."""
    if d is None:
        return None
    return str(d.strftime("%m/%d/%Y 00:00:00"))


def fmt_iso(d: Any) -> str | None:
    """Formata date como ISO datetime YYYY-MM-DDTHH:mm:ss."""
    if d is None:
        return None
    return str(d.strftime("%Y-%m-%dT00:00:00"))


def get_nome(obj: Any) -> str:
    """Retorna nome social preenchido ou nome cadastral."""
    nome_social = getattr(obj, "nome_social", None)
    if nome_social and nome_social.strip():
        return str(nome_social)
    return str(obj.nome)
