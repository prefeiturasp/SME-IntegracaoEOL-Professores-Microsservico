"""Serializers do domínio de professores."""

from rest_framework import serializers


class ProfessorEscolaSerializer(serializers.Serializer):
    """Serializa dados de professor em unidade educacional."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    componente_curricular = serializers.CharField(allow_null=True)
    codigo_componente_curricular = serializers.IntegerField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)
    cpf = serializers.CharField(allow_null=True)
    data_inicio_atribuicao = serializers.DateField(allow_null=True)
    data_fim_atribuicao = serializers.DateField(allow_null=True)
    data_inicio_exercicio = serializers.DateField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    codigo_turma = serializers.IntegerField(allow_null=True)
    turno = serializers.CharField(allow_null=True)
    tipo_turma = serializers.IntegerField(allow_null=True)


class TurmaAtribuidaSerializer(serializers.Serializer):
    """Serializa dados de turma atribuída ao professor."""

    codigo_turma = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    codigo_escola = serializers.CharField(allow_null=True)
    data_inicio_atribuicao = serializers.DateField(allow_null=True)
    data_fim_atribuicao = serializers.DateField(allow_null=True)
    data_inicio_turma = serializers.DateField(allow_null=True)
    codigo_componente_curricular = serializers.IntegerField(allow_null=True)
    componente_curricular = serializers.CharField(allow_null=True)
    codigo_grade = serializers.IntegerField(allow_null=True)
    codigo_serie_grade = serializers.IntegerField(allow_null=True)
    ano_atribuicao = serializers.IntegerField(allow_null=True)
    ano_letivo = serializers.CharField(allow_null=True)
    codigo_rf = serializers.CharField(allow_null=True)
    disciplina_id = serializers.CharField(allow_null=True)
    disciplina_nome = serializers.CharField(allow_null=True)
    disciplinas_agrupadas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
    )
    nome_professor = serializers.CharField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)
    ano = serializers.CharField(allow_null=True)
    etapa_ensino = serializers.IntegerField(allow_null=True)


class TurmaAtribuidaUeSerializer(serializers.Serializer):
    """Serializa turma atribuída por vínculo com UE."""

    codigo_escola = serializers.CharField()
    codigo_turma = serializers.IntegerField()
    ano_letivo = serializers.IntegerField()
    modalidade = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField(allow_null=True)
    codigo_modalidade = serializers.IntegerField(allow_null=True)
    codigo_dre = serializers.CharField(allow_null=True)
    dre = serializers.CharField(allow_null=True)
    dre_abreviacao = serializers.CharField(allow_null=True)
    ue = serializers.CharField(allow_null=True)
    ue_abreviacao = serializers.CharField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    ano = serializers.CharField(allow_null=True)
    tipo_ue = serializers.CharField(allow_null=True)
    codigo_tipo_ue = serializers.IntegerField(allow_null=True)
    codigo_tipo_escola = serializers.IntegerField(allow_null=True)
    tipo_escola = serializers.CharField(allow_null=True)
    duracao_turno = serializers.IntegerField(allow_null=True)
    tipo_turno = serializers.IntegerField(allow_null=True)


class DisciplinaTurmaAtribuidaUeSerializer(serializers.Serializer):
    """Serializa disciplina atribuída por vínculo com UE."""

    codigo = serializers.IntegerField(source="codigo_componente_curricular")
    descricao = serializers.CharField(source="descricao_componente_curricular")
    codigo_componente_curricular_pai = serializers.IntegerField(
        allow_null=True
    )
    regencia = serializers.BooleanField()
    codigo_componente_territorio_saber = serializers.IntegerField(
        allow_null=True
    )
    territorio_saber = serializers.BooleanField()
    tipo_escola = serializers.CharField(allow_null=True)
    turma_codigo = serializers.IntegerField(source="codigo_turma")
    ano_letivo = serializers.IntegerField()
    professor = serializers.CharField(source="usuario_rf")


class NomePorRFSerializer(serializers.Serializer):
    """Serializa dados de identificação do professor."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()


class ProfessorPerfilSerializer(serializers.Serializer):
    """Serializa dados de perfil do professor."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
    codigo_escola = serializers.CharField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    codigo_turma = serializers.IntegerField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)
    data_fim = serializers.DateField(allow_null=True)


class AutoCompleteSerializer(serializers.Serializer):
    """Serializa dados resumidos para busca de professores."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()


class ResumoSerializer(serializers.Serializer):
    """Serializa dados resumidos de servidor."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class AtribuicaoStatusSerializer(serializers.Serializer):
    """Serializa o status de atribuição na turma."""

    possui_atribuicao = serializers.BooleanField()
    codigo_rf = serializers.CharField()
    codigo_turma = serializers.IntegerField()


class AtribuicaoDataSerializer(serializers.Serializer):
    """Serializa o status de atribuição em uma data."""

    data = serializers.DateField()
    possui_atribuicao = serializers.BooleanField()


class AtribuicaoTurmaSerializer(serializers.Serializer):
    """Serializa o status de atribuição por turma."""

    codigo_turma = serializers.BigIntegerField()
    data_disponibilizacao_aulas = serializers.DateField(allow_null=True)
    data_atribuicao_aula = serializers.DateField(allow_null=True)


class AtribuicaoTurmasListaRequestSerializer(serializers.ListSerializer):
    """Valida a lista de códigos de turma para consulta."""

    child = serializers.RegexField(
        regex=r"^\d+$",
        error_messages={"invalid": "Informe apenas códigos de turma."},
    )
    allow_empty = False


class ProfessorAtribuicaoTurmaDiscSerializer(serializers.Serializer):
    """Serializa a atribuição de professor a uma turma e disciplina."""

    codigo_turma = serializers.CharField(allow_null=True)
    ano_letivo = serializers.CharField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    data_inicio_atribuicao = serializers.CharField(allow_null=True)
    data_fim_atribuicao = serializers.CharField(allow_null=True)
    data_fim_turma = serializers.CharField(allow_null=True)
    ano_atribuicao = serializers.IntegerField(allow_null=True)
    codigo_rf = serializers.CharField(allow_null=True)
    disciplina_id = serializers.CharField(allow_null=True)
    disciplina_nome = serializers.CharField(allow_null=True)
    disciplinas_agrupadas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
        required=False,
    )
    nome_professor = serializers.CharField(allow_null=True)
    atribuicao_externa = serializers.BooleanField(required=False)


class TitularSerializer(serializers.Serializer):
    """Serializa dados de professor titular."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class TitularPorTurmaSerializer(serializers.Serializer):
    """Serializa professor titular por turma."""

    professor_rf = serializers.CharField()
    nome_professor = serializers.CharField()
    disciplina = serializers.CharField(allow_null=True)
    disciplina_id = serializers.CharField(allow_null=True)
    disciplinas_id = serializers.CharField(allow_null=True)
    turma_id = serializers.IntegerField()


class TitularAgrupamentoSerializer(serializers.Serializer):
    """Serializa professor titular com dados de agrupamento."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    codigo_componente_curricular = serializers.IntegerField(allow_null=True)
    codigo_territorio_saber = serializers.IntegerField(allow_null=True)
    codigo_experiencia_pedagogica = serializers.IntegerField(allow_null=True)


class TitularTurmaSerializer(serializers.Serializer):
    """Serializa professor titular com dados de turma."""

    professor_rf = serializers.CharField()
    nome_professor = serializers.CharField()
    disciplina = serializers.CharField(allow_null=True)
    disciplina_id = serializers.IntegerField(allow_null=True)
    disciplinas_id = serializers.CharField()
    turma_id = serializers.IntegerField()
