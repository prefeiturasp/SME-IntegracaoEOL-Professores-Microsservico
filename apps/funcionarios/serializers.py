"""Serializers do domínio de funcionários."""

from typing import Any

from rest_framework import serializers

from apps.core.utils import fmt_iso


def _campo(instance: Any, nome: str) -> Any:
    """Obtém campo de modelo ou dicionário.

    Args:
        instance: Instância usada para extrair o valor.
        nome: Nome do campo consultado.

    Returns:
        Valor encontrado para o campo.
    """
    if isinstance(instance, dict):
        return instance.get(nome)
    return getattr(instance, nome)


def _inteiro(valor: Any) -> int | None:
    """Converta valor numérico quando preenchido.

    Args:
        valor: Valor recebido da instância.

    Returns:
        Inteiro convertido, ou ``None`` quando ausente.
    """
    if valor is None:
        return None
    return int(valor)


def _funcao_atividade_ativa(instance: Any) -> bool:
    """Verifica se a função atividade está vigente.

    Args:
        instance: Vínculo funcional consolidado.

    Returns:
        ``True`` quando a função atividade pode compor o retorno.
    """
    return not (
        _campo(instance, "dt_cancelamento_funcao_atividade")
        or _campo(instance, "dt_fim_funcao_atividade")
    )


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


class ListaTextoSerializer(serializers.Serializer):
    """Valida uma lista de textos no corpo da requisição."""

    itens = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        allow_empty=True,
    )

    def to_internal_value(self, data: Any) -> dict[str, list[str]]:
        """Normaliza o corpo recebido como lista de textos.

        Args:
            data: Corpo enviado na requisição.

        Returns:
            Dados normalizados para validação.
        """
        if not isinstance(data, list):
            data = []
        return super().to_internal_value({"itens": data})


class ListaUUIDSerializer(serializers.Serializer):
    """Valida uma lista de identificadores no corpo da requisição."""

    itens = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )

    def to_internal_value(self, data: Any) -> dict[str, list[Any]]:
        """Normaliza o corpo recebido como lista de identificadores.

        Args:
            data: Corpo enviado na requisição.

        Returns:
            Dados normalizados para validação.
        """
        if not isinstance(data, list):
            data = []
        return super().to_internal_value({"itens": data})


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


class CargoFuncionarioSerializer(serializers.Serializer):
    """Serializa vínculos funcionais do funcionário."""

    rf = serializers.IntegerField()
    cpf = serializers.CharField(allow_null=True)
    cd_cargo_base = serializers.IntegerField(allow_null=True)
    cargo_base = serializers.CharField(allow_null=True)
    cd_dre_cargo_base = serializers.CharField(allow_null=True)
    cd_ue_cargo_base = serializers.CharField(allow_null=True)
    ue_cargo_base = serializers.CharField(allow_null=True)
    tipo_vinculo_cargo_base = serializers.IntegerField(allow_null=True)
    data_inicio_cargo_base = serializers.CharField(allow_null=True)
    cd_cargo_sobreposto = serializers.IntegerField(allow_null=True)
    cargo_sobreposto = serializers.CharField(allow_null=True)
    cd_dre_cargo_sobreposto = serializers.CharField(allow_null=True)
    cd_ue_cargo_sobreposto = serializers.CharField(allow_null=True)
    ue_cargo_sobreposto = serializers.CharField(allow_null=True)
    tipo_vinculo_cargo_sobreposto = serializers.IntegerField(allow_null=True)
    data_inicio_cargo_sobreposto = serializers.CharField(allow_null=True)
    cd_funcao_atividade = serializers.IntegerField(allow_null=True)
    funcao_atividade = serializers.CharField(allow_null=True)
    cd_dre_funcao_atividade = serializers.CharField(allow_null=True)
    cd_ue_funcao_atividade = serializers.CharField(allow_null=True)
    ue_funcao_atividade = serializers.CharField(allow_null=True)
    tipo_vinculo_funcao_atividade = serializers.IntegerField(allow_null=True)
    data_inicio_funcao_atividade = serializers.CharField(allow_null=True)

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Monta o contrato de cargos do funcionário.

        Args:
            instance: Vínculo funcional consolidado.

        Returns:
            Dados do vínculo no formato da API.
        """
        funcao_atividade_ativa = _funcao_atividade_ativa(instance)
        return {
            "rf": _inteiro(_campo(instance, "rf")),
            "cpf": _campo(instance, "cpf"),
            "cd_cargo_base": _campo(instance, "cd_cargo_base"),
            "cargo_base": _campo(instance, "cargo_base"),
            "cd_dre_cargo_base": _campo(instance, "cd_dre_cargo_base"),
            "cd_ue_cargo_base": _campo(instance, "cd_ue_cargo_base"),
            "ue_cargo_base": _campo(instance, "ue_cargo_base"),
            "tipo_vinculo_cargo_base": _campo(
                instance,
                "tipo_vinculo_cargo_base",
            ),
            "data_inicio_cargo_base": fmt_iso(
                _campo(instance, "data_inicio_cargo_base")
            ),
            "cd_cargo_sobreposto": _campo(
                instance,
                "cd_cargo_sobreposto",
            ),
            "cargo_sobreposto": _campo(instance, "cargo_sobreposto"),
            "cd_dre_cargo_sobreposto": _campo(
                instance,
                "cd_dre_cargo_sobreposto",
            ),
            "cd_ue_cargo_sobreposto": _campo(
                instance,
                "cd_ue_cargo_sobreposto",
            ),
            "ue_cargo_sobreposto": _campo(instance, "ue_cargo_sobreposto"),
            "tipo_vinculo_cargo_sobreposto": _campo(
                instance,
                "tipo_vinculo_cargo_sobreposto",
            ),
            "data_inicio_cargo_sobreposto": fmt_iso(
                _campo(instance, "data_inicio_cargo_sobreposto")
            ),
            "cd_funcao_atividade": (
                _campo(instance, "cd_funcao_atividade")
                if funcao_atividade_ativa
                else None
            ),
            "funcao_atividade": (
                _campo(instance, "funcao_atividade")
                if funcao_atividade_ativa
                else None
            ),
            "cd_dre_funcao_atividade": (
                _campo(
                    instance,
                    "cd_dre_funcao_atividade",
                )
                if funcao_atividade_ativa
                else None
            ),
            "cd_ue_funcao_atividade": (
                _campo(
                    instance,
                    "cd_ue_funcao_atividade",
                )
                if funcao_atividade_ativa
                else None
            ),
            "ue_funcao_atividade": (
                _campo(instance, "ue_funcao_atividade")
                if funcao_atividade_ativa
                else None
            ),
            "tipo_vinculo_funcao_atividade": (
                _campo(instance, "tipo_vinculo_funcao_atividade")
                if funcao_atividade_ativa
                else None
            ),
            "data_inicio_funcao_atividade": (
                fmt_iso(_campo(instance, "data_inicio_funcao_atividade"))
                if funcao_atividade_ativa
                else None
            ),
        }


class ConectaFormacaoFiltroSerializer(serializers.Serializer):
    """Valida filtros da consulta do Conecta Formação."""

    codigos_cargos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigos_funcoes = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigo_modalidade = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    anos_turma = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigos_dres = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigos_componentes_curriculares = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    eh_tipo_jornada_jeif = serializers.BooleanField(
        required=False,
        default=False,
    )


class ConectaFormacaoSerializer(serializers.Serializer):
    """Serializa funcionário elegível para o Conecta Formação."""

    rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
    cargo_codigo = serializers.CharField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)
    cargo_dre_codigo = serializers.CharField(allow_null=True)
    cargo_ue_codigo = serializers.CharField(allow_null=True)
    funcao_codigo = serializers.CharField(allow_null=True)
    funcao = serializers.CharField(allow_null=True)
    funcao_dre_codigo = serializers.CharField(allow_null=True)
    funcao_ue_codigo = serializers.CharField(allow_null=True)
    tipo_vinculo = serializers.IntegerField(allow_null=True)


class UsuariosConectaFormacaoFiltroSerializer(serializers.Serializer):
    """Valida perfis usados na busca de usuários do Conecta Formação."""

    perfis = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )


class UsuarioConectaFormacaoSerializer(serializers.Serializer):
    """Serializa usuário do Conecta Formação."""

    login = serializers.CharField()
    nome = serializers.CharField(allow_null=True)
    nome_social = serializers.CharField(allow_null=True)
    perfil = serializers.CharField()


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


class UsuariosSGPFiltroSerializer(serializers.Serializer):
    """Valida filtros da consulta de usuários SGP por perfil."""

    codigo_dre = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    codigo_ue = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    codigo_rf = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    nome_servidor = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida a combinação de filtros recebida.

        Args:
            attrs: Filtros normalizados para consulta.

        Returns:
            Filtros validados.

        Raises:
            ValidationError: Quando DRE e RF não forem informados.
        """
        if not attrs.get("codigo_dre") and not attrs.get("codigo_rf"):
            raise serializers.ValidationError(
                "Informe codigo_dre ou codigo_rf."
            )
        return attrs


class FuncionariosSGPDreFiltroSerializer(serializers.Serializer):
    """Valida filtros da consulta de funcionários SGP por DRE."""

    codigo_ue = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    codigo_rf = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    nome_servidor = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    codigo_funcao_atividade = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
    )


class BuscarFuncionariosFiltroSerializer(serializers.Serializer):
    """Valida filtros da busca básica de funcionários."""

    codigo_rf = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    codigo_ue = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )
    nome_servidor = serializers.CharField(
        required=False,
        allow_blank=True,
        default=None,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Normaliza o corpo recebido como filtros de busca.

        Args:
            data: Corpo enviado na requisição.

        Returns:
            Dados normalizados para validação.
        """
        if not isinstance(data, dict):
            data = {}
        return super().to_internal_value(data)


class ResumoFuncionarioSerializer(serializers.Serializer):
    """Serializa dados resumidos de funcionário."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
