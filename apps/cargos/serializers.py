"""Serializers do domínio de cargos."""

from rest_framework import serializers


class CargoSerializer(serializers.Serializer):
    """Serializa cargo no contrato legado."""

    codigo_cargo = serializers.IntegerField()  # noqa: N815
    nome_cargo = serializers.CharField()  # noqa: N815
