"""Utilitários compartilhados entre os apps do microsserviço."""

from datetime import UTC, date, datetime, timedelta
from typing import Any

_DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=UTC)


def ticks_to_date(ticks: int) -> date:
    """Retorna data a partir de ticks do .NET DateTime.

    Args:
        ticks: Valor de data no formato ticks .NET.

    Returns:
        Data correspondente aos ticks informados.

    Raises:
        OverflowError: Quando os ticks excedem uma data válida.
    """
    return (_DOTNET_EPOCH + timedelta(microseconds=ticks // 10)).date()


def ticks_to_datetime_str(ticks: int) -> str:
    """Retorna datetime ISO a partir de ticks do .NET.

    Args:
        ticks: Valor de data e hora no formato ticks .NET.

    Returns:
        Data e hora correspondente em formato ISO.

    Raises:
        OverflowError: Quando os ticks excedem uma data válida.
    """
    dt = _DOTNET_EPOCH + timedelta(microseconds=ticks // 10)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def fmt_br(d: Any) -> str | None:
    """Formata data no padrão esperado pelo contrato.

    Args:
        d: Valor de data ou data e hora.

    Returns:
        Data formatada ou ``None`` quando não houver valor.
    """
    if d is None:
        return None
    return str(d.strftime("%m/%d/%Y 00:00:00"))


def fmt_iso(d: Any) -> str | None:
    """Formata data no padrão ISO usado pelo contrato.

    Args:
        d: Valor de data ou data e hora.

    Returns:
        Data formatada ou ``None`` quando não houver valor.
    """
    if d is None:
        return None
    return str(d.strftime("%Y-%m-%dT00:00:00"))


def get_nome(obj: Any) -> str:
    """Retorna nome social preenchido ou nome cadastral.

    Args:
        obj: Objeto com campos de nome.

    Returns:
        Nome preferencial do objeto.
    """
    nome_social = getattr(obj, "nome_social", None)
    if nome_social and nome_social.strip():
        return str(nome_social)
    return str(obj.nome)
