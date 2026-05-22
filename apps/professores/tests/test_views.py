"""Testes das views do domínio de professores."""

from datetime import date

import pytest

from apps.professores.models import CargoBaseServidor, SerieTurmaGrade
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
        assert len(res.data) >= 1
        assert res.data[0]["codigo_turma"] == 2112345

    def test_com_rf_retorna_turma_efetiva(self, client, atribuicao):
        """Verifica com RF retorna turma efetiva."""
        res = client.get(
            f"{_BASE}/professores/7654321/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert len(res.data) >= 1
        assert res.data[0]["codigo_turma"] == 2112345

    def test_com_atribuicao_externa(self, client, atribuicao_externa):
        """Verifica com atribuicao externa."""
        res = client.get(
            f"{_BASE}/professores/98765432100/escolas/000532"
            "/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert len(res.data) >= 1

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
    def test_todas_as_turmas_retorna_lista(self, client, atribuicao):
        """Verifica todas as turmas retorna lista."""
        res = client.get(f"{_BASE}/professores/7654321/turmas/")
        assert res.status_code == 200
        assert len(res.data) >= 1

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
        assert any(t["codigo_turma"] == 2112345 for t in res.data)

    def test_por_ano_errado_retorna_vazia(self, client, atribuicao):
        """Verifica por ano errado retorna vazia."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/anos_letivos/2099/"
        )
        assert res.status_code == 200
        assert res.data == []

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

    def test_nao_encontrado_retorna_404(self, client, db):
        """Verifica ausência de professor."""
        res = client.get(f"{_BASE}/professores/0000000/")
        assert res.status_code == 404

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
    def test_encontrado_sem_filtro_retorna_200(self, client, professor):
        """Verifica retorno do professor sem filtro opcional."""
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
        """Verifica filtro UE errado nao encontra atribuicao."""
        res = client.get(
            f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/?ue_id=999999"
        )
        assert res.status_code == 200
        assert res.data["codigo_rf"] == "7654321"

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


class TestEP11EhEmei:
    def test_atribuicao_em_ue_emei_retorna_true(self, client, atribuicao):
        # ue fixture tem codigo_tipo_escola=4 (EMEI)
        """Verifica atribuicao em UE EMEI retorna true."""
        res = client.get(f"{_BASE}/professores/7654321/ehEmei/")
        assert res.status_code == 200
        assert res.data is True

    def test_sem_atribuicao_retorna_false(self, client, db):
        """Verifica sem atribuicao retorna false."""
        res = client.get(f"{_BASE}/professores/7654321/ehEmei/")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(f"{_BASE}/professores/7654321/ehEmei/")
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

    def test_com_territorio_saber_sem_agrupamento_retorna_false(
        self, client, atribuicao
    ):
        """Verifica com territorio saber sem agrupamento retorna false."""
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
            "?territorio_saber=true"
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
        ue,
    ):
        """Verifica turma com atribuicao externa retorna periodo."""
        atribuicao_externa.codigo_serie_grade = 1040353
        atribuicao_externa.save()
        SerieTurmaGrade.objects.create(
            codigo_serie_grade=1040353,
            codigo_turma=2112345,
            codigo_escola=ue.codigo_ue,
            codigo_escola_grade=100,
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

    def test_retorna_externo_atribuido(self, client, atribuicao_externa, ue):
        """Verifica retorna externo atribuido."""
        atribuicao_externa.codigo_serie_grade = 1040353
        atribuicao_externa.save()
        SerieTurmaGrade.objects.create(
            codigo_serie_grade=1040353,
            codigo_turma=2112345,
            codigo_escola=ue.codigo_ue,
            codigo_escola_grade=100,
        )

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
        """Verifica retorno do RF quando registro existe."""
        res = client.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 200
        assert res.data["professor_rf"] == "7654321"

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
        """Verifica turma com atribuicao retorna titular."""
        res = client.get(
            f"{_BASE}/professores/titulares/?codigos_turmas=2112345"
        )
        assert res.status_code == 200
        assert any(t["professor_rf"] == "7654321" for t in res.data)

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


class TestEP22TitularesPorTurmaAgrupamento:
    def test_sem_agrupamento_retorna_atribuicoes(self, client, atribuicao):
        """Verifica sem agrupamento retorna atribuicoes."""
        res = client.get(
            f"{_BASE}/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/false/"
        )
        assert res.status_code == 200
        assert any(t["professor_rf"] == "7654321" for t in res.data)

    def test_com_agrupamento_sem_dados_retorna_vazio(self, client, db):
        """Verifica com agrupamento sem dados retorna vazio."""
        res = client.get(
            f"{_BASE}/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/true/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        """Verifica bloqueio sem API key."""
        res = anon.get(
            f"{_BASE}/professores/2112345/titulares"
            "/realizaAgrupamentoComponente/false/"
        )
        assert res.status_code == 403


class TestEP23TitularesPorUe:
    def test_atribuicao_antes_da_data_retorna_titular(
        self, client, atribuicao
    ):
        """Verifica atribuicao antes da data retorna titular."""
        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-06-01/"
        )
        assert res.status_code == 200
        assert any(t["professor_rf"] == "7654321" for t in res.data)

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
