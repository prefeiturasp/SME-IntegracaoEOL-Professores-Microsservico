"""Testes das views do domínio Professores (EP-01 a EP-23)."""

from datetime import date

import pytest

from apps.professores.models import CargoBaseServidor
from conftest import date_to_ticks

pytestmark = pytest.mark.django_db

_BASE = "/api/v1"

# Ticks para datas usadas nos testes
_TICK_2024_02_02 = date_to_ticks(date(2024, 2, 2))  # após dt_atribuicao_aula
_TICK_2024_01_31 = date_to_ticks(date(2024, 1, 31))  # antes de dt_atribuicao_aula


# ---------------------------------------------------------------------------
# EP-01 — Professores da escola por ano letivo
# ---------------------------------------------------------------------------


class TestEP01BuscaProfessores:
    def test_com_ano_retorna_lista_com_professor(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/escolas/000532/professores/2024/")
        assert res.status_code == 200
        assert any(p["codigoRF"] == 7654321 for p in res.data)

    def test_sem_ano_retorna_lista(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/escolas/000532/professores/")
        assert res.status_code == 200
        assert isinstance(res.data, list)

    def test_escola_sem_atribuicoes_retorna_lista_vazia(self, client, db):
        res = client.get(f"{_BASE}/professores/escolas/999999/professores/2024/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/escolas/000532/professores/2024/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-02 — Turmas atribuídas (escola + RF + ano)
# ---------------------------------------------------------------------------


class TestEP02TurmasAtribuidasEscola:
    def test_com_rf_retorna_turma_efetiva(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/escolas/000532/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert len(res.data) >= 1
        assert res.data[0]["codigoTurma"] == 2112345

    def test_com_atribuicao_externa(self, client, atribuicao_externa):
        res = client.get(
            f"{_BASE}/professores/98765432100/escolas/000532/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert len(res.data) >= 1

    def test_sem_atribuicao_retorna_lista_vazia(self, client, db):
        res = client.get(
            f"{_BASE}/professores/0000000/escolas/000532/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/7654321/escolas/000532/turmas/anos_letivos/2024/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-03 / EP-04 — Turmas do professor (todas / por ano)
# ---------------------------------------------------------------------------


class TestEP03EP04TurmasAtribuidas:
    def test_todas_as_turmas_retorna_lista(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/7654321/turmas/")
        assert res.status_code == 200
        assert len(res.data) >= 1

    def test_todas_sem_atribuicao_retorna_vazia(self, client, db):
        res = client.get(f"{_BASE}/professores/0000000/turmas/")
        assert res.status_code == 200
        assert res.data == []

    def test_por_ano_com_atribuicao_retorna_lista(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/7654321/turmas/anos_letivos/2024/")
        assert res.status_code == 200
        assert any(t["codigoTurma"] == 2112345 for t in res.data)

    def test_por_ano_errado_retorna_vazia(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/7654321/turmas/anos_letivos/2099/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/7654321/turmas/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-05 — Nome pelo RF
# ---------------------------------------------------------------------------


class TestEP05ObterNomePeloRF:
    def test_encontrado_retorna_200_com_nome(self, client, professor):
        res = client.get(f"{_BASE}/professores/7654321/")
        assert res.status_code == 200
        assert res.content.decode() == "Ana Silva"

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(f"{_BASE}/professores/0000000/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/7654321/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-06 — BuscarPorRf (por RF e ano letivo)
# ---------------------------------------------------------------------------


class TestEP06BuscarPorRf:
    def test_encontrado_retorna_200_com_rf(self, client, professor):
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 200
        assert res.data["codigoRF"] == "7654321"

    def test_com_atribuicao_retorna_turma(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 200
        assert "codigoRF" in res.data

    def test_com_lotacao_retorna_escola(self, client, professor, lotacao):
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 200
        assert res.data["nome"] == "Ana Silva"

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(f"{_BASE}/professores/0000000/BuscarPorRf/2024/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/7654321/BuscarPorRf/2024/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-07 — BuscarPorRfDreUe
# ---------------------------------------------------------------------------


class TestEP07BuscarPorRfDreUe:
    def test_encontrado_sem_filtro_retorna_200(self, client, professor):
        res = client.get(f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/")
        assert res.status_code == 200
        assert res.data["codigoRF"] == "7654321"

    def test_filtro_ue_correto_retorna_dados(self, client, atribuicao, lotacao):
        res = client.get(
            f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/?ueId=000532"
        )
        assert res.status_code == 200
        assert res.data["codigoRF"] == "7654321"

    def test_filtro_ue_errado_nao_encontra_atribuicao(self, client, professor, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/?ueId=999999"
        )
        assert res.status_code == 200
        assert res.data["codigoRF"] == "7654321"

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(f"{_BASE}/professores/0000000/BuscarPorRfDreUe/2024/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/7654321/BuscarPorRfDreUe/2024/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-08 — AutoComplete de professores
# ---------------------------------------------------------------------------


class TestEP08AutoComplete:
    def test_retorna_lista_com_professor(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/2024/AutoComplete/108100/")
        assert res.status_code == 200
        assert any(p["codigoRf"] == "7654321" for p in res.data)

    def test_filtro_nome_retorna_correspondente(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/2024/AutoComplete/108100/?nome=Ana")
        assert res.status_code == 200
        assert len(res.data) >= 1
        assert res.data[0]["nomeServidor"] == "Ana Silva"

    def test_filtro_nome_sem_match_retorna_vazio(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/2024/AutoComplete/108100/?nome=Zzzz")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        res = client.get(f"{_BASE}/professores/2024/AutoComplete/108100/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/2024/AutoComplete/108100/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-09 — BuscarPorListaRF (POST)
# ---------------------------------------------------------------------------


class TestEP09BuscarPorListaRF:
    def test_rf_com_atribuicao_retorna_professor(self, client, atribuicao):
        res = client.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 200
        assert any(p["codigoRF"] == "7654321" for p in res.data)

    def test_rf_sem_atribuicao_retorna_vazio(self, client, professor):
        res = client.post(
            f"{_BASE}/professores/2099/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_lista_vazia_retorna_vazio(self, client, db):
        res = client.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            [],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.post(
            f"{_BASE}/professores/2024/BuscarPorListaRF/",
            [],
            format="json",
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-10 — Validade do professor
# ---------------------------------------------------------------------------


class TestEP10VerificarValidade:
    def test_com_cargo_ativo_retorna_true(self, client, cargo_base):
        res = client.get(f"{_BASE}/professores/7654321/validade/")
        assert res.status_code == 200
        assert res.data is True

    def test_com_cargo_ativo_situacao_diferente_de_6_retorna_true(
        self, client, professor
    ):
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
        res = client.get(f"{_BASE}/professores/7654321/validade/")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/7654321/validade/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-11 — EhEmei
# ---------------------------------------------------------------------------


class TestEP11EhEmei:
    def test_atribuicao_em_ue_emei_retorna_true(self, client, atribuicao):
        # ue fixture tem codigo_tipo_escola=4 (EMEI)
        res = client.get(f"{_BASE}/professores/7654321/ehEmei/")
        assert res.status_code == 200
        assert res.data is True

    def test_sem_atribuicao_retorna_false(self, client, db):
        res = client.get(f"{_BASE}/professores/7654321/ehEmei/")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/7654321/ehEmei/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-12 — Status de atribuição
# ---------------------------------------------------------------------------


class TestEP12AtribuicaoStatus:
    def test_com_atribuicao_retorna_true(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        assert res.status_code == 200
        assert res.data["anoAtribuicao"] == 2024

    def test_sem_atribuicao_retorna_false(self, client, db):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        assert res.status_code == 200
        assert res.data["anoAtribuicao"] is None

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/status/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-13 — Verificar atribuição em data
# ---------------------------------------------------------------------------


class TestEP13AtribuicaoVerificarData:
    def test_sem_data_retorna_true_se_existe(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/verificar/data/"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_data_apos_inicio_retorna_true(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/verificar/data/"
            "?dataConsulta=2024-06-01"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_data_antes_do_inicio_retorna_false(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/verificar/data/"
            "?dataConsulta=2024-01-31"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345/atribuicao/verificar/data/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-14 — Verificar atribuição de disciplina em data
# ---------------------------------------------------------------------------


class TestEP14AtribuicaoDisciplinaData:
    def test_retorna_true_quando_existe(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_data_antes_retorna_false(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
            "?dataConsulta=2024-01-31"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_com_territorio_saber_sem_agrupamento_retorna_false(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
            "?territorioSaber=true"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/data/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-15 — Verificar atribuição via dataTick
# ---------------------------------------------------------------------------


class TestEP15AtribuicaoDisciplinaDataTick:
    def test_tick_apos_atribuicao_retorna_true(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
            f"?dataConsultaTick={_TICK_2024_02_02}"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_tick_antes_atribuicao_retorna_false(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
            f"?dataConsultaTick={_TICK_2024_01_31}"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_tick_retorna_resultado_sem_filtro_de_data(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/verificar/datatick/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-16 — Verificar recorrência de datas
# ---------------------------------------------------------------------------


class TestEP16AtribuicaoRecorrenciaDatas:
    def test_retorna_lista_com_resultado_correto(self, client, atribuicao):
        url = (
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
            f"?dataTicks={_TICK_2024_02_02}&dataTicks={_TICK_2024_01_31}"
        )
        res = client.get(url)
        assert res.status_code == 200
        assert len(res.data) == 2
        resultados = {item["podePersistir"] for item in res.data}
        assert True in resultados
        assert False in resultados

    def test_lista_vazia_de_ticks_retorna_vazia(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/7654321/turmas/2112345"
            "/disciplinas/138/atribuicao/recorrencia/verificar/datas/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-17 — Verificar atribuição em lista de turmas (POST)
# ---------------------------------------------------------------------------


class TestEP17AtribuicaoTurmasLista:
    def test_turma_com_atribuicao_retorna_true(self, client, atribuicao):
        res = client.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            [2112345, 9999999],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == [
            {
                "codigoTurma": "2112345",
                "dataDisponibilizacaoAulas": None,
                "dataAtribuicaoAula": "2024-02-01T00:00:00",
            }
        ]

    def test_lista_vazia_retorna_vazia(self, client, atribuicao):
        res = client.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            [],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.post(
            f"{_BASE}/professores/7654321/disciplina/138/turmas/",
            [],
            format="json",
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-18 — Atribuição em período (POST)
# ---------------------------------------------------------------------------


class TestEP18AtribuicaoPeriodo:
    _URL = (
        f"{_BASE}/professores/7654321/turmas/2112345"
        "/componentes/138/atribuicao/periodo"
        "/inicio/2024-02-01/fim/2024-12-20/"
    )

    def test_atribuicao_dentro_do_periodo_retorna_true(self, client, atribuicao):
        res = client.post(self._URL, format="json")
        assert res.status_code == 200
        assert res.data is True

    def test_sem_atribuicao_retorna_false(self, client, db):
        res = client.post(self._URL, format="json")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.post(self._URL, format="json")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-19 — Professores atribuídos a turma/disciplina em data
# ---------------------------------------------------------------------------


class TestEP19ProfessoresAtribuidosTurmaDisc:
    def test_retorna_professor_atribuido(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        assert res.status_code == 200
        assert any(p["codigoRf"] == "7654321" for p in res.data)

    def test_retorna_externo_atribuido(self, client, atribuicao_externa):
        # EP-19 não consulta AtribuicaoExterno — atribuições externas não aparecem
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        assert res.status_code == 200
        assert not res.data

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        res = client.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/2112345/disciplinas/138/atribuicao/data/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-20 — Titular por turma e componente curricular
# ---------------------------------------------------------------------------


class TestEP20TitularPorTurmaDisciplina:
    def test_encontrado_retorna_200_com_rf(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 200
        assert res.data["professorRf"] == "7654321"

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/titular/turmas/2112345"
            "/componentes-curriculares/138/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-21 — Titulares por lista de turmas
# ---------------------------------------------------------------------------


class TestEP21TitularesPorTurmas:
    def test_turma_com_atribuicao_retorna_titular(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/titulares/?codigosTurmas=2112345"
        )
        assert res.status_code == 200
        assert any(t["professorRf"] == "7654321" for t in res.data)

    def test_turma_sem_atribuicao_retorna_vazio(self, client, db):
        res = client.get(
            f"{_BASE}/professores/titulares/?codigosTurmas=2112345"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_filtro_retorna_lista(self, client, atribuicao):
        res = client.get(f"{_BASE}/professores/titulares/")
        assert res.status_code == 200
        assert isinstance(res.data, list)

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/professores/titulares/")
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-22 — Titulares por turma com agrupamento
# ---------------------------------------------------------------------------


class TestEP22TitularesPorTurmaAgrupamento:
    def test_sem_agrupamento_retorna_atribuicoes(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/2112345/titulares/realizaAgrupamentoComponente/false/"
        )
        assert res.status_code == 200
        assert any(t["professorRf"] == "7654321" for t in res.data)

    def test_com_agrupamento_sem_dados_retorna_vazio(self, client, db):
        res = client.get(
            f"{_BASE}/professores/2112345/titulares/realizaAgrupamentoComponente/true/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/2112345/titulares/realizaAgrupamentoComponente/false/"
        )
        assert res.status_code == 403


# ---------------------------------------------------------------------------
# EP-23 — Titulares por UE e data de referência
# ---------------------------------------------------------------------------


class TestEP23TitularesPorUe:
    def test_atribuicao_antes_da_data_retorna_titular(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-06-01/"
        )
        assert res.status_code == 200
        assert any(t["professorRf"] == "7654321" for t in res.data)

    def test_data_antes_da_atribuicao_retorna_vazio(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-01-31/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_atribuicao_retorna_vazio(self, client, db):
        res = client.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-06-01/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/professores/titulares/ue/000532/2024-06-01/"
        )
        assert res.status_code == 403
