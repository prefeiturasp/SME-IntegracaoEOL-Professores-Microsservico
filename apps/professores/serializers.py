"""Serializers do domínio Professores — definem o schema do Swagger."""

from rest_framework import serializers


class ProfessorEscolaSerializer(serializers.Serializer):
    """EP-01 — Professor de uma escola por ano letivo."""

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
    """EP-02, EP-03, EP-04 — Turmas atribuídas ao professor."""

    codigo_turma = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    codigo_escola = serializers.CharField(allow_null=True)
    data_inicio_atribuicao = serializers.DateField(allow_null=True)
    data_fim_atribuicao = serializers.DateField(allow_null=True)
    codigo_componente_curricular = serializers.IntegerField(allow_null=True)
    codigo_grade = serializers.IntegerField(allow_null=True)
    codigo_serie_grade = serializers.IntegerField(allow_null=True)
    ano_atribuicao = serializers.IntegerField(allow_null=True)


class NomePorRFSerializer(serializers.Serializer):
    """EP-05 — Nome e RF do professor."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()


class ProfessorPerfilSerializer(serializers.Serializer):
    """EP-06, EP-07 — Perfil do professor por RF e ano letivo."""

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
    """EP-08 — AutoComplete de professores."""

    codigo_rf = serializers.CharField()
    nome_servidor = serializers.CharField()


class ResumoSerializer(serializers.Serializer):
    """EP-09, EP-38, EP-39 — Resumo básico de professor/funcionário."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class AtribuicaoStatusSerializer(serializers.Serializer):
    """EP-12 — Status de atribuição na turma."""

    possui_atribuicao = serializers.BooleanField()
    codigo_rf = serializers.CharField()
    codigo_turma = serializers.IntegerField()


class AtribuicaoDataSerializer(serializers.Serializer):
    """EP-16 — Atribuição por data (recorrência)."""

    data = serializers.DateField()
    possui_atribuicao = serializers.BooleanField()


class AtribuicaoTurmaSerializer(serializers.Serializer):
    """EP-17 — Atribuição por turma."""

    codigo_turma = serializers.IntegerField()
    possui_atribuicao = serializers.BooleanField()


class ProfessorAtribuidoTurmaDiscSerializer(serializers.Serializer):
    """EP-19 — Professores atribuídos a turma/disciplina em data."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
    codigo_componente_curricular = serializers.IntegerField(allow_null=True)
    data_atribuicao = serializers.DateField(allow_null=True)
    data_disponibilizacao = serializers.DateField(allow_null=True)
    atribuicao_externa = serializers.BooleanField()


class TitularSerializer(serializers.Serializer):
    """EP-20 — Professor titular por turma e disciplina."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class TitularPorTurmaSerializer(serializers.Serializer):
    """EP-21 — Titulares por lista de turmas."""

    codigo_turma = serializers.IntegerField()
    codigo_rf = serializers.CharField()
    nome = serializers.CharField()


class TitularAgrupamentoSerializer(serializers.Serializer):
    """EP-22, EP-23 — Titulares por turma com agrupamento."""

    codigo_rf = serializers.CharField()
    nome = serializers.CharField()
    codigo_componente_curricular = serializers.IntegerField(allow_null=True)
    codigo_territorio_saber = serializers.IntegerField(allow_null=True)
    codigo_experiencia_pedagogica = serializers.IntegerField(allow_null=True)
