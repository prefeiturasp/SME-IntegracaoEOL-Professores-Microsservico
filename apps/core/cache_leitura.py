"""Reutiliza representações de consultas com fontes completas."""

import hashlib
import hmac
import json
import logging
import time
from collections.abc import Callable
from contextlib import nullcontext
from typing import Any, cast

from django.conf import settings
from django.core.cache import caches
from django.db import DatabaseError, connections, transaction

from apps.professores.models import ControleCargaProfessores

logger = logging.getLogger(__name__)
_AUSENTE = object()


def _registrar(operacao: str, evento: str) -> None:
    logger.info(
        "cache_leitura", extra={"operacao": operacao, "evento": evento}
    )


def _geracao_pronta() -> str | None:
    try:
        consulta = ControleCargaProfessores.objects.filter(pk=1).values_list(
            "geracao", "cargas_ativas", "falha"
        )
        banco = consulta.db
        protecao = (
            transaction.atomic(using=banco)
            if connections[banco].in_atomic_block
            else nullcontext()
        )
        with protecao:
            estado = consulta.first()
    except DatabaseError:
        return None
    if estado is None or estado[1] != [] or estado[2]:
        return None
    return str(estado[0])


def _ler(backend: Any, chave: str) -> Any:
    texto = backend.get(chave, _AUSENTE)
    if texto is _AUSENTE:
        return _AUSENTE
    if not isinstance(texto, bytes):
        return _AUSENTE
    if len(texto) > settings.PROFESSORES_CACHE_MAX_BYTES:
        return _AUSENTE
    try:
        payload = json.loads(texto)
    except ValueError:
        return _AUSENTE
    return payload if isinstance(payload, list) else _AUSENTE


def obter_ou_calcular(
    operacao: str,
    parametros: dict[str, Any],
    calcular: Callable[[], list],
) -> list:
    """Retorna a representação produzida para os parâmetros informados.

    Args:
        operacao: Identificador estável da consulta.
        parametros: Entradas já validadas e específicas da consulta.
        calcular: Função que produz a representação atual.

    Returns:
        Lista correspondente aos parâmetros, preservando tipos e duplicatas.
    """
    if not settings.PROFESSORES_CACHE_ENABLED:
        return calcular()
    geracao = _geracao_pronta()
    if geracao is None:
        _registrar(operacao, "fontes_indisponiveis")
        return calcular()

    identidade = json.dumps(
        parametros,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    digest = hmac.new(
        settings.SECRET_KEY.encode(), identidade, hashlib.sha256
    ).hexdigest()
    chave = f"leitura:v1:{operacao}:{geracao}:{digest}"

    try:
        backend = caches["professores"]
        encontrado = _ler(backend, chave)
        if encontrado is not _AUSENTE:
            _registrar(operacao, "hit")
            return cast(list, encontrado)
        dono = backend.add(
            chave + ":construcao",
            True,
            timeout=settings.PROFESSORES_CACHE_LOCK_SECONDS,
        )
        if not dono:
            limite = time.monotonic() + settings.PROFESSORES_CACHE_WAIT_SECONDS
            while time.monotonic() < limite:
                time.sleep(0.02)
                encontrado = _ler(backend, chave)
                if encontrado is not _AUSENTE:
                    _registrar(operacao, "hit_apos_espera")
                    return cast(list, encontrado)
    except Exception:
        _registrar(operacao, "falha_backend")
        return calcular()

    if not dono:
        _registrar(operacao, "construcao_concorrente")
        return calcular()

    _registrar(operacao, "miss")
    resultado = calcular()
    if _geracao_pronta() != geracao:
        _registrar(operacao, "geracao_alterada")
        return resultado
    try:
        texto = json.dumps(
            resultado,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        if len(texto) > settings.PROFESSORES_CACHE_MAX_BYTES:
            _registrar(operacao, "limite_tamanho")
            return resultado
        backend.set(chave, texto, timeout=settings.PROFESSORES_CACHE_TTL)
    except Exception:
        _registrar(operacao, "falha_preenchimento")
    return resultado
