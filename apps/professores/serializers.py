"""Serializers do domínio Professores — definem o schema do Swagger."""

from rest_framework import serializers


class ProfessorEscolaSerializer(serializers.Serializer):
    """EP-01 — Professor de uma escola por ano letivo."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    componenteCurricular = serializers.CharField(allow_null=True)
    codigoComponenteCurricular = serializers.IntegerField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)
    cpf = serializers.CharField(allow_null=True)
    dataInicioAtribuicao = serializers.DateField(allow_null=True)
    dataFimAtribuicao = serializers.DateField(allow_null=True)
    dataInicioExercicio = serializers.DateField(allow_null=True)
    nomeTurma = serializers.CharField(allow_null=True)
    codigoTurma = serializers.IntegerField(allow_null=True)
    turno = serializers.CharField(allow_null=True)
    tipoTurma = serializers.IntegerField(allow_null=True)


class TurmaAtribuidaSerializer(serializers.Serializer):
    """EP-02, EP-03, EP-04 — Turmas atribuídas ao professor."""

    codigoTurma = serializers.IntegerField(allow_null=True)
    nomeTurma = serializers.CharField(allow_null=True)
    codigoEscola = serializers.CharField(allow_null=True)
    dataInicioAtribuicao = serializers.DateField(allow_null=True)
    dataFimAtribuicao = serializers.DateField(allow_null=True)
    codigoComponenteCurricular = serializers.IntegerField(allow_null=True)
    codigoGrade = serializers.IntegerField(allow_null=True)
    codigoSerieGrade = serializers.IntegerField(allow_null=True)
    anoAtribuicao = serializers.IntegerField(allow_null=True)


class NomePorRFSerializer(serializers.Serializer):
    """EP-05 — Nome e RF do professor."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()


class ProfessorPerfilSerializer(serializers.Serializer):
    """EP-06, EP-07 — Perfil do professor por RF e ano letivo."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
    codigoEscola = serializers.CharField(allow_null=True)
    nomeTurma = serializers.CharField(allow_null=True)
    codigoTurma = serializers.IntegerField(allow_null=True)
    cargo = serializers.CharField(allow_null=True)
    dataInicio = serializers.DateField(allow_null=True)
    dataFim = serializers.DateField(allow_null=True)


class AutoCompleteSerializer(serializers.Serializer):
    """EP-08 — AutoComplete de professores."""

    codigoRf = serializers.CharField()
    nomeServidor = serializers.CharField()


class ResumoSerializer(serializers.Serializer):
    """EP-09, EP-38, EP-39 — Resumo básico de professor/funcionário."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class AtribuicaoStatusSerializer(serializers.Serializer):
    """EP-12 — Status de atribuição na turma."""

    possuiAtribuicao = serializers.BooleanField()
    codigoRf = serializers.CharField()
    codigoTurma = serializers.IntegerField()


class AtribuicaoDataSerializer(serializers.Serializer):
    """EP-16 — Atribuição por data (recorrência)."""

    data = serializers.DateField()
    possuiAtribuicao = serializers.BooleanField()


class AtribuicaoTurmaSerializer(serializers.Serializer):
    """EP-17 — Atribuição por turma."""

    codigoTurma = serializers.IntegerField()
    possuiAtribuicao = serializers.BooleanField()


class ProfessorAtribuidoTurmaDiscSerializer(serializers.Serializer):
    """EP-19 — Professores atribuídos a turma/disciplina em data."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)
    codigoComponenteCurricular = serializers.IntegerField(allow_null=True)
    dataAtribuicao = serializers.DateField(allow_null=True)
    dataDisponibilizacao = serializers.DateField(allow_null=True)
    atribuicaoExterna = serializers.BooleanField()


class TitularSerializer(serializers.Serializer):
    """EP-20 — Professor titular por turma e disciplina."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    cpf = serializers.CharField(allow_null=True)


class TitularPorTurmaSerializer(serializers.Serializer):
    """EP-21 — Titulares por lista de turmas."""

    codigoTurma = serializers.IntegerField()
    codigoRf = serializers.CharField()
    nome = serializers.CharField()


class TitularAgrupamentoSerializer(serializers.Serializer):
    """EP-22, EP-23 — Titulares por turma com agrupamento."""

    codigoRf = serializers.CharField()
    nome = serializers.CharField()
    codigoComponenteCurricular = serializers.IntegerField(allow_null=True)
    codigoTerritorioSaber = serializers.IntegerField(allow_null=True)
    codigoExperienciaPedagogica = serializers.IntegerField(allow_null=True)
