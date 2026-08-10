"""Testes das views do domínio de professores."""

from datetime import date

import pytest

from apps.professores.models import (
    AtribuicaoAula,
    CargoBaseServidor,
)
from conftest import date_to_ticks

pytestmark = pytest.mark.django_db

_BASE = "/api/v1"

_TICK_2024_02_02 = date_to_ticks(date(2024, 2, 2))
_TICK_2024_01_31 = date_to_ticks(date(2024, 1, 31))


class TestEP01BuscaProfessores:
    def test_com_ano_retorna_lista_com_professor(self, client, atribuicao):
        """Verifica com ano retorna lista com professor."""
        res = client.get(
            f"{_BASE}/professores/escolas/000532/professores/2024/"
        )
        assert res.status_code == 200
        assert any(p["codigo_rf"] == 7654321 for p in res.data)

    def test_sem_ano_retorna_lista(self, client, atribuicao):
        """Verifica sem ano retorna lista."""
        res = client.get(f"{_BASE}/professores/escolas/000532/professores/")
        assert res.status_code == 200
        assert isinstance(res.data, list)

    def test_escola_sem_atribuicoes_retorna_lista_vazia(self, client, db):
        """Verifica escola sem atribuicoes retorna lista vazia."""
        res = client.get(
            f"{_BASE}/professores/escolas/999999/professores/2024/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/escolas/000532/professores/2024/")
        assert res.status_code == 403


class TestEP02TurmasAtribuidasEscola:
    def test_sem_rf_retorna_turma_efetiva(self, client, atribuicao):
        """Verifica sem RF retorna turma efetiva."""
        res = client.get(
            f"{_BASE}/professores/escolas/000532/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "codigo_turma": 2112345,
                "nome_turma": "1A",
                "componente_curricular": "Matematica",
                "data_inicio_atribuicao": "02/01/2024 00:00:00",
                "data_fim_atribuicao": None,
                "data_inicio_turma": None,
                "ano": "1",
                "etapa_ensino": 1,
            }
        ]

    def test_com_rf_retorna_turma_efetiva(self, client, atribuicao):
        """Verifica com RF retorna turma efetiva."""
        res = client.get(
            f"{_BASE}/professores/7654321/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "codigo_turma": 2112345,
                "nome_turma": "1A",
                "componente_curricular": "Matematica",
                "data_inicio_atribuicao": "02/01/2024 00:00:00",
                "data_fim_atribuicao": None,
                "data_inicio_turma": None,
                "ano": "1",
                "etapa_ensino": 1,
            }
        ]

    def test_com_atribuicao_externa(self, client, atribuicao_externa):
        """Verifica com atribuicao externa."""
        res = client.get(
            f"{_BASE}/professores/98765432100/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "codigo_turma": 2112345,
                "nome_turma": "1A",
                "componente_curricular": "Matematica",
                "data_inicio_atribuicao": "02/01/2024 00:00:00",
                "data_fim_atribuicao": None,
                "data_inicio_turma": None,
                "ano": "1",
                "etapa_ensino": 1,
            }
        ]

    def test_sem_atribuicao_retorna_lista_vazia(self, client, db):
        """Verifica sem atribuicao retorna lista vazia."""
        res = client.get(
            f"{_BASE}/professores/0000000/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/7654321/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 403


class TestEP03EP04TurmasAtribuidas:
    def test_todas_as_turmas_retorna_lista(
        self, client, atribuicao_ano_corrente
    ):
        """Verifica todas as turmas retorna lista."""
        res = client.get(f"{_BASE}/professores/7654321/turmas/")
        assert res.status_code == 200
        assert res.data == [
            {
                "codigo_turma": 2112345,
                "nome_turma": "1A",
                "codigo_serie_grade": None,
                "componente_curricular": "Matematica",
                "codigo_unidade_educacao": "000532",
                "ano": "1",
                "etapa_ensino": 1,
                "data_atribuicao": (f"01/01/{date.today().year} 00:00:00"),
                "data_disponibilizacao": None,
                "data_inicio_turma": None,
            }
        ]

    def test_todas_sem_atribuicao_retorna_vazia(self, client, db):
        """Verifica todas sem atribuicao retorna vazia."""
        res = client.get(f"{_BASE}/professores/0000000/turmas/")
        assert res.status_code == 200
        assert res.data == []

    def test_por_ano_com_atribuicao_retorna_lista(self, client, atribuicao):
        """Verifica por ano com atribuicao retorna lista."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "codigo_turma": 2112345,
                "nome_turma": "1A",
                "codigo_serie_grade": None,
                "componente_curricular": "Matematica",
                "codigo_unidade_educacao": "000532",
                "ano": "1",
                "etapa_ensino": 1,
                "data_atribuicao": "02/01/2024 00:00:00",
                "data_disponibilizacao": None,
                "data_inicio_turma": None,
                "ano_letivo": "2024",
                "data_inicio_atribuicao": "2024-02-01T00:00:00",
                "data_fim_atribuicao": None,
                "data_fim_turma": None,
                "ano_atribuicao": 2024,
                "codigo_rf": "7654321",
                "disciplina_id": "138",
                "disciplina_nome": "Matematica",
                "disciplinas_agrupadas_ids": None,
                "nome_professor": "Ana Silva",
            }
        ]

    def test_por_ano_errado_retorna_vazia(self, client, atribuicao):
        """Verifica por ano errado retorna vazia."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/anos_letivos/2099/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_todos_anos_retorna_atribuicao_sem_filtrar_ano(
        self, client, atribuicao
    ):
        """Verifica consulta detalhada sem recorte de ano letivo."""
        res = client.get(f"{_BASE}/professores/7654321/turmas/anos_letivos/")

        assert res.status_code == 200
        assert len(res.data) == 1
        assert res.data[0]["ano_letivo"] == "2024"
        assert res.data[0]["ano_atribuicao"] == 2024

    def test_todos_anos_sem_api_key_retorna_403(self, anon):
        """Verifica autenticação na consulta sem recorte anual."""
        res = anon.get(f"{_BASE}/professores/7654321/turmas/anos_letivos/")

        assert res.status_code == 403

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/7654321/turmas/")
        assert res.status_code == 403


class TestEP05ObterNomePeloRF:
    def test_encontrado_retorna_200_com_nome(self, client, professor):
        """Verifica retorno do nome quando professor existe."""
        res = client.get(f"{_BASE}/professores/7654321/")
        assert res.status_code == 200
        assert res.content.decode() == "Ana Silva"

    def test_nao_encontrado_retorna_204(self, client, db):
        """Verifica ausência de professor."""
        res = client.get(f"{_BASE}/professores/0000000/")
        assert res.status_code == 204

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/7654321/")
        assert res.status_code == 403


class TestEP06BuscarPorRf:
    def test_sem_atribuicao_retorna_404(self, client, professor):
        """Verifica que professor sem atribuicao no ano retorna 404."""
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 404

    def test_com_atribuicao_retorna_turma(self, client, atribuicao):
        """Verifica com atribuicao retorna turma."""
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 200
        assert "codigo_rf" in res.data

    def test_com_atribuicao_retorna_nome(self, client, atribuicao):
        """Verifica que atribuicao no ano retorna nome."""
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 200
        assert res.data["nome"] == "Ana Silva"

    def test_nao_encontrado_retorna_404(self, client, db):
        """Verifica ausência de professor."""
        res = client.get(f"{_BASE}/professores/0000000/BuscarPorRf/2024/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 403


class TestEP07BuscarPorRfDreUe:
    def test_encontrado_sem_filtro_retorna_200(self, client, atribuicao):
        """Com atribuição no ano e sem filtro, retorna o professor."""
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/")
        assert res.status_code == 200
        assert res.data["codigo_rf"] == "7654321"

    def test_filtro_ue_correto_retorna_dados(
        self, client, atribuicao, lotacao
    ):
        """Verifica filtro UE correto retorna dados."""
        res = client.get(
            f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/?ue_id=000532"
        )
        assert res.status_code == 200
        assert res.data["codigo_rf"] == "7654321"

    def test_filtro_ue_errado_nao_encontra_atribuicao(
        self, client, professor, atribuicao
    ):
        """UE errada (sem outros cargos) não encontra atribuição → 404."""
        res = client.get(
            f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/?ue_id=999999"
        )
        assert res.status_code == 404

    def test_buscar_outros_cargos_ignora_filtro_ue(
        self, client, professor, atribuicao
    ):
        """Com buscar_outros_cargos, o escopo de UE é ignorado."""
        res = client.get(
            f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/"
            "?ue_id=999999&buscar_outros_cargos=true"
        )
        assert res.status_code == 200
        assert res.data["codigo_rf"] == "7654321"

    def test_fallback_externo_por_cpf(self, client, contrato_externo):
        """Sem atribuição efetiva, cai no contrato externo por CPF."""
        res = client.get(
            f"{_BASE}/professores/98765432100/BuscarPorRfDreUe/2024/"
        )
        assert res.status_code == 200
        assert res.data["codigo_rf"] == "98765432100"

    def test_ano_zero_retorna_400(self, client, db):
        """Ano letivo igual a zero retorna 400."""
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRfDreUe/0/")
        assert res.status_code == 400

    def test_nao_encontrado_retorna_404(self, client, db):
        """Verifica ausência de professor."""
        res = client.get(f"{_BASE}/professores/0000000/BuscarPorRfDreUe/2024/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/")
        assert res.status_code == 403


class TestEP08AutoComplete:
    def test_retorna_lista_com_professor(self, client, atribuicao):
        """Verifica retorna lista com professor."""
        res = client.get(f"{_BASE}/professores/2024/AutoComplete/108100/")
        assert res.status_code == 200
        assert any(p["codigo_rf"] == "7654321" for p in res.data)

    def test_filtro_nome_retorna_correspondente(self, client, atribuicao):
        """Verifica filtro nome retorna correspondente."""
        res = client.get(
            f"{_BASE}/professores/2024/AutoComplete/108100/?nome=Ana"
        )
        assert res.status_code == 200
        assert len(res.data) >= 1
        assert res.data[0]["nome_servidor"] == "Ana Silva"

    def test_filtro_nome_sem_match_retorna_vazio(self, client, atribuicao):
        """Verifica filtro nome sem match retorna vazio."""
        res = client.get(
            f"{_BASE}/professores/2024/AutoComplete/108100/?nome=Zzzz"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        """Verifica sem atribuicao retorna vazio."""
        res = client.get(f"{_BASE}/professores/2024/AutoComplete/108100/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/2024/AutoComplete/108100/")
        assert res.status_code == 403


class TestEP09BuscarPorListaRF:
    def test_rf_com_atribuicao_retorna_professor(self, client, atribuicao):
        """Verifica RF com atribuicao retorna professor."""
        res = client.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 200
        assert any(p["codigo_rf"] == "7654321" for p in res.data)

    def test_uma_entrada_por_turma_e_ignora_cancelada(self, client, professor):
        """Verifica deduplicacao de turma e exclusao de cancelada."""
        cargo = CargoBaseServidor.objects.create(
            professor=professor,
            codigo_cargo=3379,
            descricao_cargo="Professor",
            dt_posse=date(2020, 1, 1),
        )
        AtribuicaoAula.objects.create(
            cargo_base=cargo,
            codigo_unidade_educacao="000532",
            codigo_turma_escola=2112345,
            codigo_grade=100,
            codigo_componente_curricular=138,
            ano_atribuicao=2024,
            dt_atribuicao_aula=date(2024, 2, 1),
        )
        AtribuicaoAula.objects.create(
            cargo_base=cargo,
            codigo_unidade_educacao="000532",
            codigo_turma_escola=2112345,
            codigo_grade=100,
            codigo_componente_curricular=139,
            ano_atribuicao=2024,
            dt_atribuicao_aula=date(2024, 2, 1),
        )
        AtribuicaoAula.objects.create(
            cargo_base=cargo,
            codigo_unidade_educacao="000999",
            codigo_turma_escola=2112346,
            codigo_grade=100,
            codigo_componente_curricular=138,
            ano_atribuicao=2024,
            dt_atribuicao_aula=date(2024, 2, 1),
            dt_cancelamento=date(2024, 6, 1),
        )

        res = client.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )

        assert res.status_code == 200
        entradas = [p for p in res.data if p["codigo_rf"] == "7654321"]
        assert len(entradas) == 1
        assert set(entradas[0].keys()) == {"codigo_rf", "nome"}

    def test_rf_sem_atribuicao_retorna_vazio(self, client, professor):
        """Verifica RF sem atribuicao retorna vazio."""
        res = client.post(
            f"{_BASE}/professores/2099/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_lista_vazia_retorna_vazio(self, client, db):
        """Verifica lista vazia retorna vazio."""
        res = client.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            [],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_ano_zero_retorna_400(self, client, db):
        """Ano letivo igual a zero retorna 400."""
        res = client.post(
            f"{_BASE}/professores/0/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 400

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            [],
            format="json",
        )
        assert res.status_code == 403


class TestEP10VerificarValidade:
    def test_com_cargo_ativo_retorna_true(self, client, cargo_base):
        """Verifica com cargo ativo retorna true."""
        res = client.get(f"{_BASE}/professores/7654321/validade/")
        assert res.status_code == 200
        assert res.data is True

    def test_com_cargo_ativo_situacao_diferente_de_6_retorna_true(
        self, client, professor
    ):
        """Verifica com cargo ativo situacao diferente de 6 retorna true."""
        CargoBaseServidor.objects.create(
            professor=professor,
            codigo_cargo=3379,
            situacao_funcional=1,
            dt_posse=date(2020, 1, 1),
        )

        res = client.get(f"{_BASE}/professores/7654321/validade/")

        assert res.status_code == 200
        assert res.data is True

    def test_com_cargo_encerrado_retorna_false(self, client, professor):
        """Verifica com cargo encerrado retorna false."""
        CargoBaseServidor.objects.create(
            professor=professor,
            codigo_cargo=3379,
            situacao_funcional=6,
            dt_posse=date(2020, 1, 1),
            dt_fim_nomeacao=date(2024, 1, 1),
        )

        res = client.get(f"{_BASE}/professores/7654321/validade/")

        assert res.status_code == 200
        assert res.data is False

    def test_sem_cargo_retorna_false(self, client, db):
        """Verifica sem cargo retorna false."""
        res = client.get(f"{_BASE}/professores/7654321/validade/")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/7654321/validade/")
        assert res.status_code == 403


class TestEP11UnidadesAtribuicaoValida:
    _URL = f"{_BASE}/professores/7654321/unidades-atribuicao/"

    @staticmethod
    def _atribuir_cargo_3239(
        professor,
        *,
        dt_fim_nomeacao=None,
        dt_cancelamento=None,
        codigo_ue="000532",
    ):
        cargo = CargoBaseServidor.objects.create(
            professor=professor,
            codigo_cargo=3239,
            situacao_funcional=6,
            dt_posse=date(2020, 1, 1),
            dt_fim_nomeacao=dt_fim_nomeacao,
        )
        return AtribuicaoAula.objects.create(
            cargo_base=cargo,
            codigo_unidade_educacao=codigo_ue,
            codigo_turma_escola=2112345,
            codigo_grade=100,
            codigo_componente_curricular=138,
            ano_atribuicao=2024,
            dt_atribuicao_aula=date(2024, 2, 1),
            dt_cancelamento=dt_cancelamento,
        )

    def test_cargo_3239_valido_retorna_ue(self, client, professor):
        """Atribuição cargo 3239 vigente retorna a UE."""
        self._atribuir_cargo_3239(professor)
        res = client.get(self._URL)
        assert res.status_code == 200
        assert res.data["codigo_rf"] == "7654321"
        assert res.data["codigos_ue"] == ["000532"]

    def test_cargo_diferente_de_3239_nao_retorna(self, client, atribuicao):
        """Atribuição em cargo != 3239 (fixture cargo 3379) não entra."""
        res = client.get(self._URL)
        assert res.status_code == 200
        assert res.data["codigos_ue"] == []

    def test_atribuicao_cancelada_nao_retorna(self, client, professor):
        """Atribuição cancelada não entra (paridade com dt_cancelamento)."""
        self._atribuir_cargo_3239(professor, dt_cancelamento=date(2024, 6, 1))
        res = client.get(self._URL)
        assert res.status_code == 200
        assert res.data["codigos_ue"] == []

    def test_nomeacao_encerrada_nao_retorna(self, client, professor):
        """Nomeação encerrada não entra (paridade com dt_fim_nomeacao)."""
        self._atribuir_cargo_3239(professor, dt_fim_nomeacao=date(2024, 1, 1))
        res = client.get(self._URL)
        assert res.status_code == 200
        assert res.data["codigos_ue"] == []

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        """Sem atribuição retorna lista vazia."""
        res = client.get(self._URL)
        assert res.status_code == 200
        assert res.data["codigos_ue"] == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(self._URL)
        assert res.status_code == 403


class TestEP12AtribuicaoStatus:
    def test_com_atribuicao_retorna_true(self, client, atribuicao):
        """Verifica com atribuicao retorna true."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        assert res.status_code == 200
        assert res.data["ano_atribuicao"] == 2024

    def test_sem_atribuicao_retorna_false(self, client, db):
        """Verifica sem atribuicao retorna false."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        assert res.status_code == 200
        assert res.data["ano_atribuicao"] is None

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        assert res.status_code == 403


class TestEP13AtribuicaoVerificarData:
    def test_sem_data_retorna_true_se_existe(self, client, atribuicao):
        """Verifica sem data retorna true se existe."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/atribuicao/verificar/data/"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_data_apos_inicio_retorna_true(self, client, atribuicao):
        """Verifica data apos inicio retorna true."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/atribuicao/verificar/data/"
            "?data_consulta=2024-06-01"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_data_antes_do_inicio_retorna_false(self, client, atribuicao):
        """Verifica data antes do inicio retorna false."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/atribuicao/verificar/data/"
            "?data_consulta=2024-01-31"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/atribuicao/verificar/data/"
        )
        assert res.status_code == 403


class TestEP14AtribuicaoDisciplinaData:
    def test_retorna_true_quando_existe(self, client, atribuicao):
        """Verifica retorna true quando existe."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_data_antes_retorna_false(self, client, atribuicao):
        """Verifica data antes retorna false."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
            "?data_consulta=2024-01-31"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
        )
        assert res.status_code == 403


class TestEP15AtribuicaoDisciplinaDataTick:
    def test_tick_apos_atribuicao_retorna_true(self, client, atribuicao):
        """Verifica tick apos atribuicao retorna true."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
            f"?data_consulta_tick={_TICK_2024_02_02}"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_tick_antes_atribuicao_retorna_false(self, client, atribuicao):
        """Verifica tick antes atribuicao retorna false."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
            f"?data_consulta_tick={_TICK_2024_01_31}"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_tick_retorna_400(self, client, atribuicao):
        """Verifica validação de tick obrigatório."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
        )
        assert res.status_code == 400

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
        )
        assert res.status_code == 403


class TestEP16AtribuicaoRecorrenciaDatas:
    def test_retorna_lista_com_resultado_correto(self, client, atribuicao):
        """Verifica retorna lista com resultado correto."""
        url = (
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
            f"?data_ticks={_TICK_2024_02_02}&data_ticks={_TICK_2024_01_31}"
        )
        res = client.get(url)
        assert res.status_code == 200
        assert len(res.data) == 2
        resultados = {item["pode_persistir"] for item in res.data}
        assert True in resultados
        assert False in resultados

    def test_sem_ticks_retorna_400(self, client, atribuicao):
        """Verifica validação de ticks obrigatórios."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
        )
        assert res.status_code == 400

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
        )
        assert res.status_code == 403


class TestEP17AtribuicaoTurmasLista:
    def test_turma_com_atribuicao_retorna_true(self, client, atribuicao):
        """Verifica turma com atribuicao retorna true."""
        atribuicao.codigo_motivo_disponibilizacao = 34
        atribuicao.save(update_fields=["codigo_motivo_disponibilizacao"])

        res = client.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            [2112345, 9999999],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "codigo_turma": "2112345",
                "data_disponibilizacao_aulas": None,
                "data_atribuicao_aula": "2024-02-01T00:00:00",
            }
        ]

    def test_lista_vazia_retorna_vazia(self, client, atribuicao):
        """Verifica lista vazia retorna vazia."""
        res = client.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            [],
            format="json",
        )
        assert res.status_code == 400

    def test_atribuicao_externa_sem_codigo_turma_direto_retorna_vazio(
        self,
        client,
        atribuicao_externa,
    ):
        """Verifica externo sem turma direta nao retorna periodo."""
        atribuicao_externa.codigo_turma_escola = None
        atribuicao_externa.codigo_serie_grade = 1040353
        atribuicao_externa.save(
            update_fields=["codigo_turma_escola", "codigo_serie_grade"]
        )

        res = client.post(
            f"{_BASE}/professores/98765432100/disciplina/138/turmas/",
            [2112345],
            format="json",
        )

        assert res.status_code == 200
        assert res.data == []

    def test_codigo_turma_invalido_retorna_lista_vazia(
        self,
        client,
        atribuicao,
    ):
        """Verifica codigo_turma invalido retorna lista vazia."""
        res = client.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            ["string"],
            format="json",
        )

        assert res.status_code == 200
        assert res.data == []

    def test_payload_nao_lista_retorna_lista_vazia(self, client, atribuicao):
        """Verifica retorno vazio para entrada fora do formato esperado."""
        res = client.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            {"codigo_turma": 2112345},
            format="json",
        )

        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            [],
            format="json",
        )
        assert res.status_code == 403


class TestEP18AtribuicaoPeriodo:
    _URL = (
        f"{_BASE}/professores/7654321/turmas/2112345"
        "/componentes/138/atribuicao/periodo"
        "/inicio/2024-02-01/fim/2024-12-20/"
    )

    def test_atribuicao_dentro_do_periodo_retorna_true(
        self, client, atribuicao
    ):
        """Verifica atribuicao dentro do periodo retorna true."""
        res = client.post(self._URL, format="json")
        assert res.status_code == 200
        assert res.data is True

    def test_sem_atribuicao_retorna_false(self, client, db):
        """Verifica sem atribuicao retorna false."""
        res = client.post(self._URL, format="json")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.post(self._URL, format="json")
        assert res.status_code == 403


class TestEP19ProfessoresAtribuidosTurmaDisc:
    def test_retorna_professor_atribuido(self, client, atribuicao):
        """Verifica retorna professor atribuido."""
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
            f"?data_ticks={_TICK_2024_02_02}"
        )
        assert res.status_code == 200
        assert any(p["codigo_rf"] == "7654321" for p in res.data)

    def test_retorna_externo_atribuido(self, client, atribuicao_externa):
        """Verifica retorna externo atribuido."""
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
            f"?data_ticks={_TICK_2024_02_02}"
        )

        assert res.status_code == 200
        assert any(p["codigo_rf"] == "98765432100" for p in res.data)
        assert any(p["atribuicao_externa"] is True for p in res.data)

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        """Verifica sem atribuicao retorna vazio."""
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
            f"?data_ticks={_TICK_2024_02_02}"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_data_ticks_retorna_400(self, client):
        """Verifica validação de data em ticks obrigatória."""
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        assert res.status_code == 400

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        assert res.status_code == 403


class TestEP20TitularPorTurmaDisciplina:
    def test_encontrado_retorna_200_com_rf(self, client, atribuicao):
        """Verifica payload do titular por turma e disciplina."""
        atribuicao.descricao_componente_curricular = "Matematica   "
        atribuicao.save(update_fields=["descricao_componente_curricular"])

        res = client.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 200
        assert res.data == {
            "professor_rf": "7654321",
            "nome_professor": "Ana Silva",
            "disciplina": "Matematica",
            "disciplina_id": "138",
            "disciplinas_id": "138",
            "turma_id": 2112345,
        }

    def test_nao_encontrado_retorna_404(self, client, db):
        """Verifica ausência de professor."""
        res = client.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 403


class TestEP21TitularesPorTurmas:
    def test_turma_com_atribuicao_retorna_titular(self, client, atribuicao):
        """Verifica payload dos titulares das turmas."""
        atribuicao.descricao_componente_curricular = "Matematica   "
        atribuicao.save(update_fields=["descricao_componente_curricular"])

        res = client.get(
            f"{_BASE}/professores/titulares/?codigos_turmas=2112345"
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "professor_rf": "7654321",
                "nome_professor": "Ana Silva",
                "disciplina": "Matematica",
                "disciplina_id": "138",
                "disciplinas_id": "138",
                "turma_id": 2112345,
            }
        ]

    def test_turma_sem_atribuicao_retorna_vazio(self, client, db):
        """Verifica turma sem atribuicao retorna vazio."""
        res = client.get(
            f"{_BASE}/professores/titulares/?codigos_turmas=2112345"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_filtro_retorna_lista(self, client, atribuicao):
        """Verifica sem filtro retorna lista."""
        res = client.get(f"{_BASE}/professores/titulares/")
        assert res.status_code == 200
        assert isinstance(res.data, list)

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/titulares/")
        assert res.status_code == 403


class TestEP22TitularesPorTurma:
    def test_openapi_nao_documenta_data_referencia(self, anon):
        """Verifica remoção da data de referência do OpenAPI."""
        res = anon.get(
            f"{_BASE}/schema/",
            HTTP_ACCEPT="application/json",
        )

        assert res.status_code == 200
        endpoint = res.json()["paths"][
            "/api/v1/professores/{codigo_turma}/titulares/"
        ]["get"]
        assert {parameter["name"] for parameter in endpoint["parameters"]} == {
            "codigo_turma",
            "codigo_rf",
        }

    def test_retorna_atribuicoes(self, client, atribuicao_ano_corrente):
        """Verifica retorno das atribuições da turma."""
        res = client.get(f"{_BASE}/professores/2112345/titulares/")
        assert res.status_code == 200
        assert res.data == [
            {
                "professor_rf": "7654321",
                "nome_professor": "Ana Silva",
                "disciplina": "Matematica",
                "disciplina_id": 138,
                "disciplinas_id": "138",
                "turma_id": 2112345,
            }
        ]

    def test_rf_diferente_retorna_vazio(self, client, atribuicao_ano_corrente):
        """Verifica filtro opcional por RF."""
        res = client.get(
            f"{_BASE}/professores/2112345/titulares/?codigo_rf=0000000"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_retorna_atribuicao_externa(self, client, atribuicao_externa):
        """Verifica retorno de titular externo ativo no ano corrente."""
        atribuicao_externa.ano_atribuicao = date.today().year
        atribuicao_externa.save(update_fields=["ano_atribuicao"])

        res = client.get(f"{_BASE}/professores/2112345/titulares/")

        assert res.status_code == 200
        assert res.data == [
            {
                "professor_rf": "98765432100",
                "nome_professor": "João Ext",
                "disciplina": "Matematica",
                "disciplina_id": 138,
                "disciplinas_id": "138",
                "turma_id": 2112345,
            }
        ]

    def test_rota_antiga_nao_existe(self, client, atribuicao):
        """Verifica remoção da rota com parâmetro de agrupamento."""
        res = client.get(
            f"{_BASE}/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/false/"
        )
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/2112345/titulares/")
        assert res.status_code == 403


class TestEP23TitularesPorUe:
    def test_openapi_documenta_contrato_do_endpoint(self, anon):
        """Verifica campos e parâmetros publicados no OpenAPI."""
        res = anon.get(
            f"{_BASE}/schema/",
            HTTP_ACCEPT="application/json",
        )

        assert res.status_code == 200
        schema = res.json()
        endpoint = schema["paths"][
            "/api/v1/professores/titulares/ue/"
            "{ue_codigo}/{data_referencia}/"
        ]["get"]
        response_items = endpoint["responses"]["200"]["content"][
            "application/json"
        ]["schema"]["items"]

        assert response_items == {
            "$ref": "#/components/schemas/TitularPorTurma"
        }
        assert {parameter["name"] for parameter in endpoint["parameters"]} == {
            "ue_codigo",
            "data_referencia",
        }
        assert set(
            schema["components"]["schemas"]["TitularPorTurma"]["properties"]
        ) == {
            "professor_rf",
            "nome_professor",
            "disciplina",
            "disciplina_id",
            "disciplinas_id",
            "turma_id",
        }

    def test_atribuicao_antes_da_data_retorna_titular(
        self, client, atribuicao
    ):
        """Verifica payload do titular da UE na data informada."""
        atribuicao.descricao_componente_curricular = "Matematica   "
        atribuicao.save(update_fields=["descricao_componente_curricular"])

        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-06-01/"
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "professor_rf": "7654321",
                "nome_professor": "Ana Silva",
                "disciplina": "Matematica",
                "disciplina_id": "138",
                "disciplinas_id": "138",
                "turma_id": 2112345,
            }
        ]

    def test_data_antes_da_atribuicao_retorna_vazio(self, client, atribuicao):
        """Verifica data antes da atribuicao retorna vazio."""
        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-01-31/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        """Verifica sem atribuicao retorna vazio."""
        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-06-01/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/titulares/ue/000532/2024-06-01/")
        assert res.status_code == 403
