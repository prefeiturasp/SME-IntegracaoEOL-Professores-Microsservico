"""Serializers do domínio de funcionários."""

from rest_framework import serializers


class FuncionarioUESerializer(serializers.Serializer):
    """Serializa dados de funcionário em unidade educacional."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField()
    cargo = serializers.CharField(allow_null=True)
    codigo_cargo = serializers.CharField(allow_null=True)
    data_inicio = serializers.CharField(allow_null=True)
    data_fim = serializers.CharField(allow_null=True)
    codigo_tipo_funcao_atividade = serializers.IntegerField()
    esta_afastado = serializers.BooleanField()
    funcao_externo = serializers.IntegerField()
    tipo_funcao_externo = serializers.IntegerField()


class FuncionarioPerfilSerializer(serializers.Serializer):
    """Serializa funcionario associado a perfil de sistema."""

    login = serializers.CharField()
    nome_servidor = serializers.CharField(allow_null=True)
    perfil = serializers.CharField()


class CargoSigpaeSerializer(serializers.Serializer):
    """Serializa cargo retornado para o SIGPAE."""

    codigo_cargo = serializers.IntegerField(allow_null=True)
    descricao_cargo = serializers.CharField(allow_null=True)
    codigo_unidade = serializers.CharField(allow_null=True)
    descricao_unidade = serializers.CharField(allow_null=True)
    codigo_dre = serializers.CharField(allow_null=True)
    contrato_externo = serializers.BooleanField()


class DadosSigpaeSerializer(serializers.Serializer):
    """Serializa dados de funcionario retornados ao SIGPAE."""

    rf = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)
    cargos = CargoSigpaeSerializer(many=True, allow_null=True)
    nome = serializers.CharField(allow_null=True)
    inexistente_eol = serializers.BooleanField()


class FuncionariosUEQuerySerializer(serializers.Serializer):
    """Valida filtros de funcionarios em unidade educacional."""

    cargos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    funcoes_atividades = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    funcoes_externas = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )


class FuncionariosUEFiltroSerializer(serializers.Serializer):
    """Valida filtros de funcionários por UE no contrato legado."""

    codigosRfs = serializers.ListField(  # noqa: N815
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_empty=True,
        default=list,
    )
    filtro = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class SupervisoresFiltroSerializer(serializers.Serializer):
    """Valida RFs usados na busca de supervisores por DRE."""

    codigos_rfs = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        allow_empty=True,
    )


class SupervisorSerializer(serializers.Serializer):
    """Serializa supervisor vinculado à DRE."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()


class FuncionarioFuncaoExternaSerializer(serializers.Serializer):
    """Serializa dados de funcionário externo por função."""

    cpf = serializers.CharField()
    nome_servidor = serializers.CharField()
    codigo_escola = serializers.CharField(allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)


class FuncionarioExternoCpfSerializer(serializers.Serializer):
    """Serializa dados de funcionário externo."""

    nome_pessoa = serializers.CharField()
    nome_pai = serializers.CharField(allow_null=True)
    nome_mae = serializers.CharField(allow_null=True)
    data_nascimento = serializers.CharField(allow_null=True)
    rg = serializers.CharField(allow_null=True)
    cpf = serializers.CharField()
    titulo_eleitoral = serializers.CharField(allow_null=True)
    pis_pasep = serializers.CharField(allow_null=True)
    codigo_contrato_externo = serializers.IntegerField()
    codigo_ue = serializers.CharField(allow_null=True)
    nome_ue = serializers.CharField(allow_null=True)
    funcao = serializers.CharField(allow_null=True)
    tipo_funcionario = serializers.CharField(allow_null=True)


class NomeCPFServidorSerializer(serializers.Serializer):
    """Serializa dados de identificação do servidor."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class DreUeCargoSerializer(serializers.Serializer):
    """Serializa dados de cargo do funcionário."""

    codigo_rf = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)


class UsuarioSGPSerializer(serializers.Serializer):
    """Serializa dados de usuário SGP."""

    codigo_rf = serializers.CharField()
    login = serializers.CharField(allow_null=True, required=False)
    nome_servidor = serializers.CharField()
    codigo_dre = serializers.CharField(allow_null=True)
    codigo_ue = serializers.CharField(allow_null=True)
    cd_cargo = serializers.IntegerField(allow_null=True, required=False)
    codigo_funcao_atividade = serializers.IntegerField(required=False)
    funcao_externo = serializers.IntegerField(required=False)
    tipo_funcao_externo = serializers.IntegerField(required=False)


class ResumoFuncionarioSerializer(serializers.Serializer):
    """Serializa dados resumidos de funcionário."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
