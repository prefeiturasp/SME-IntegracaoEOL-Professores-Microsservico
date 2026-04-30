"""Utilitários compartilhados entre os apps do MS Professores."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

# Época base do .NET DateTime.Ticks: 0001-01-01 00:00:00 UTC
_DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=timezone.utc)


def ticks_to_date(ticks: int) -> date:
    """Converte .NET DateTime.Ticks (100-nanosecond intervals) para date."""
    return (_DOTNET_EPOCH + timedelta(microseconds=ticks // 10)).date()


def ticks_to_datetime_str(ticks: int) -> str:
    """Converte .NET Ticks para string ISO datetime preservando o horário."""
    dt = _DOTNET_EPOCH + timedelta(microseconds=ticks // 10)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def fmt_br(d: Any) -> str | None:
    """Formata date/datetime no padrão MM/DD/YYYY HH:mm:ss do legado EOL."""
    if d is None:
        return None
    return d.strftime("%m/%d/%Y 00:00:00")


def fmt_iso(d: Any) -> str | None:
    """Formata date como ISO datetime YYYY-MM-DDTHH:mm:ss."""
    if d is None:
        return None
    return d.strftime("%Y-%m-%dT00:00:00")


def get_nome(obj: Any) -> str:
    """Retorna nome_social quando preenchido, caso contrário retorna nome (P9)."""
    nome_social = getattr(obj, "nome_social", None)
    if nome_social and nome_social.strip():
        return nome_social
    return obj.nome
