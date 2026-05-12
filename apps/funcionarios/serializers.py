"""Serializers do domínio Funcionários — definem o schema do Swagger."""

from rest_framework import serializers


class FuncionarioUESerializer(serializers.Serializer):
    """EP-25, EP-26, EP-27, EP-29 — Funcionário por UE."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()
    cargo = serializers.CharField(allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)
    data_fim = serializers.DateField(allow_null=True)


class FuncionarioFuncaoExternaSerializer(serializers.Serializer):
    """EP-28 — Funcionário externo por UE e função externa."""

    cpf = serializers.CharField()
    nome_servidor = serializers.CharField()
    codigo_escola = serializers.CharField(allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)


class FuncionarioExternoCpfSerializer(serializers.Serializer):
    """EP-30 — Funcionário externo por CPF."""

    cpf = serializers.CharField()
    nome = serializers.CharField()
    codigo_ue = serializers.CharField(allow_null=True)
    codigo_tipo_funcao = serializers.IntegerField(allow_null=True)


class NomeServidorSerializer(serializers.Serializer):
    """EP-31 — Nome e CPF do servidor por RF."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class DreUeAtribuicaoSerializer(serializers.Serializer):
    """EP-32 — DRE/UE de atribuição do funcionário."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)


class DreUeCargoSerializer(serializers.Serializer):
    """EP-34 — DRE/UE do funcionário por cargo específico."""

    codigo_rf = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)


class UsuarioSGPSerializer(serializers.Serializer):
    """EP-35, EP-36 — Usuário SGP."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)


class ResumoFuncionarioSerializer(serializers.Serializer):
    """EP-38, EP-39 — Resumo de funcionário por lista de RF/login."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
