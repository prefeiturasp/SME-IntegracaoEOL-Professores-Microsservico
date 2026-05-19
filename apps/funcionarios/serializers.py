"""Serializers do domínio de funcionários."""

from rest_framework import serializers


class FuncionarioUESerializer(serializers.Serializer):
    """Serializa dados de funcionário em unidade educacional."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()
    cargo = serializers.CharField(allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)
    data_fim = serializers.DateField(allow_null=True)


class FuncionarioFuncaoExternaSerializer(serializers.Serializer):
    """Serializa dados de funcionário externo por função."""

    cpf = serializers.CharField()
    nome_servidor = serializers.CharField()
    codigo_escola = serializers.CharField(allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)


class FuncionarioExternoCpfSerializer(serializers.Serializer):
    """Serializa dados de funcionário externo."""

    cpf = serializers.CharField()
    nome = serializers.CharField()
    codigo_ue = serializers.CharField(allow_null=True)
    codigo_tipo_funcao = serializers.IntegerField(allow_null=True)


class NomeServidorSerializer(serializers.Serializer):
    """Serializa dados de identificação do servidor."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class DreUeAtribuicaoSerializer(serializers.Serializer):
    """Serializa dados de atribuição do funcionário."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)


class DreUeCargoSerializer(serializers.Serializer):
    """Serializa dados de cargo do funcionário."""

    codigo_rf = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)


class UsuarioSGPSerializer(serializers.Serializer):
    """Serializa dados de usuário SGP."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)


class ResumoFuncionarioSerializer(serializers.Serializer):
    """Serializa dados resumidos de funcionário."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
