"""Testes dos serializers do domínio de professores."""

from apps.professores.serializers import TitularTurmaSerializer


def test_titular_turma_serializer_valida_payload():
    """Valida o contrato de resposta de titular por turma."""
    payload = {
        "professor_rf": "7654321",
        "nome_professor": "Ana Silva",
        "disciplina": "Matematica",
        "disciplina_id": 138,
        "disciplinas_id": "138",
        "turma_id": 2112345,
    }

    serializer = TitularTurmaSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == payload


def test_titular_turma_serializer_aceita_disciplina_nula():
    """Aceita os campos opcionais de disciplina como nulos."""
    payload = {
        "professor_rf": "7654321",
        "nome_professor": "Ana Silva",
        "disciplina": None,
        "disciplina_id": None,
        "disciplinas_id": "None",
        "turma_id": 2112345,
    }

    serializer = TitularTurmaSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors
