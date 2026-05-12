"""Serializers do domínio Turmas — definem o schema do Swagger."""

from rest_framework import serializers


class TurmaHistoricaSerializer(serializers.Serializer):
    """EP-24 — Turma histórica do professor por ano."""

    codigo_turma = serializers.IntegerField()
    nome_turma = serializers.CharField(allow_null=True)
    codigo_escola = serializers.CharField()
    ano_letivo = serializers.IntegerField()
    status = serializers.CharField()
