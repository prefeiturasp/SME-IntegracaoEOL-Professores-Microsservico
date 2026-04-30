"""Serializers do domínio Turmas — definem o schema do Swagger."""

from rest_framework import serializers


class TurmaHistoricaSerializer(serializers.Serializer):
    """EP-24 — Turma histórica do professor por ano."""

    codigoTurma = serializers.IntegerField()
    nomeTurma = serializers.CharField(allow_null=True)
    codigoEscola = serializers.CharField()
    anoLetivo = serializers.IntegerField()
    status = serializers.CharField()
