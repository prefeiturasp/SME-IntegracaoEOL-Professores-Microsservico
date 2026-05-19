"""Serializers do domínio de turmas."""

from rest_framework import serializers


class TurmaHistoricaSerializer(serializers.Serializer):
    """Serializa dados de turma histórica do professor."""

    codigo_turma = serializers.IntegerField()
    nome_turma = serializers.CharField(allow_null=True)
    codigo_escola = serializers.CharField()
    ano_letivo = serializers.IntegerField()
    status = serializers.CharField()
