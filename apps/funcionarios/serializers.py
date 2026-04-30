"""Serializers do domínio Funcionários — definem o schema do Swagger."""

from rest_framework import serializers


class FuncionarioUESerializer(serializers.Serializer):
    """EP-25, EP-26, EP-27, EP-29 — Funcionário por UE."""

    codigoRf = serializers.CharField()
    nomeServidor = serializers.CharField()
    cargo = serializers.CharField(allow_null=True)
    dataInicio = serializers.DateField(allow_null=True)
    dataFim = serializers.DateField(allow_null=True)


class FuncionarioFuncaoExternaSerializer(serializers.Serializer):
    """EP-28 — Funcionário externo por UE e função externa."""

    cpf = serializers.CharField()
    nomeServidor = serializers.CharField()
    codigoEscola = serializers.CharField(allow_null=True)
    dataInicio = serializers.DateField(allow_null=True)


class FuncionarioExternoCpfSerializer(serializers.Serializer):
    """EP-30 — Funcionário externo por CPF."""

    cpf = serializers.CharField()
    nome = serializers.CharField()
    codigoUe = serializers.CharField(allow_null=True)
    codigoTipoFuncao = serializers.IntegerField(allow_null=True)


class NomeServidorSerializer(serializers.Serializer):
    """EP-31 — Nome e CPF do servidor por RF."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class DreUeAtribuicaoSerializer(serializers.Serializer):
    """EP-32 — DRE/UE de atribuição do funcionário."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    codigoDre = serializers.CharField(allow_null=True)
    codigoUe = serializers.CharField(allow_null=True)


class DreUeCargoSerializer(serializers.Serializer):
    """EP-34 — DRE/UE do funcionário por cargo específico."""

    codigoRf = serializers.CharField()
    codigoDre = serializers.CharField(allow_null=True)
    codigoUe = serializers.CharField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)


class UsuarioSGPSerializer(serializers.Serializer):
    """EP-35, EP-36 — Usuário SGP."""

    codigoRf = serializers.CharField()
    nomeServidor = serializers.CharField()
    codigoDre = serializers.CharField(allow_null=True)
    codigoUe = serializers.CharField(allow_null=True)


class ResumoFuncionarioSerializer(serializers.Serializer):
    """EP-38, EP-39 — Resumo de funcionário por lista de RF/login."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
