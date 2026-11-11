"""Compara a busca unificada com os contratos atuais sobre os mesmos dados."""

import pytest
from drf_spectacular.generators import SchemaGenerator

BASE = "/api/v1/professores"
ROTAS = {"rf": "BuscarPorRf", "rf_dre_ue": "BuscarPorRfDreUe"}


@pytest.mark.django_db
class TestBuscaProfessorPorRf:
    """Preserva o resultado das consultas sem modificar suas regras."""

    @pytest.mark.parametrize(
        "tipo,ano,filtros",
        [
            ("rf", 2024, {}),
            ("rf", 2023, {}),
            ("rf", 2024, {"buscar_outros_cargos": "true"}),
            ("rf", 2024, {"dre_id": "outra", "ue_id": "outra"}),
            ("rf_dre_ue", 2024, {}),
            ("rf_dre_ue", 2023, {}),
            ("rf_dre_ue", 2024, {"ue_id": "000532"}),
            ("rf_dre_ue", 2024, {"ue_id": "outra"}),
            ("rf_dre_ue", 2024, {"dre_id": "outra", "ue_id": "000532"}),
            (
                "rf_dre_ue",
                2024,
                {"ue_id": "outra", "buscar_outros_cargos": "true"},
            ),
        ],
    )
    def test_equivalencia_com_atribuicao(
        self, client, atribuicao, tipo, ano, filtros
    ):
        """A seleção explícita mantém o status e corpo da rota antiga."""
        rf = atribuicao.cargo_base.professor.codigo_rf
        antiga = client.get(f"{BASE}/{rf}/{ROTAS[tipo]}/{ano}/", filtros)
        nova = client.get(
            f"{BASE}/{rf}/anos_letivos/{ano}/", {**filtros, "tipo_busca": tipo}
        )
        assert nova.status_code == antiga.status_code
        assert nova.data == antiga.data

    @pytest.mark.parametrize("tipo", ["rf", "rf_dre_ue"])
    def test_fallback_externo_preserva_diferenca(
        self, client, contrato_externo, tipo
    ):
        """Fallback por CPF continua exclusivo do caminho que já o possuía."""
        cpf = contrato_externo.pessoa.cpf
        filtros = {"ue_id": "outra", "buscar_outros_cargos": "true"}
        antiga = client.get(f"{BASE}/{cpf}/{ROTAS[tipo]}/2024/", filtros)
        nova = client.get(
            f"{BASE}/{cpf}/anos_letivos/2024/", {**filtros, "tipo_busca": tipo}
        )
        assert nova.status_code == antiga.status_code
        assert nova.data == antiga.data
        assert nova.status_code == (204 if tipo == "rf" else 200)

    def test_selecao_automatica_e_tipo_explicito(self, client, atribuicao):
        """O tipo explícito prevalece sobre a seleção pela localização."""
        rf = atribuicao.cargo_base.professor.codigo_rf
        url = f"{BASE}/{rf}/anos_letivos/2023/"
        assert client.get(url).status_code == 200
        assert client.get(url, {"dre_id": "108100"}).status_code == 204
        assert client.get(url, {"tipo_busca": "rf_dre_ue"}).status_code == 204
        assert (
            client.get(
                url, {"tipo_busca": "rf", "dre_id": "108100"}
            ).status_code
            == 200
        )

    def test_outros_cargos_nao_acrescenta_regra_nova(
        self, client, criar_funcionario_ue
    ):
        """Servidor sem aula não passa a ser incluído no caminho simples."""
        funcionario = criar_funcionario_ue()
        rf = funcionario.codigo_rf
        filtros = {"buscar_outros_cargos": "true"}
        antiga = client.get(f"{BASE}/{rf}/BuscarPorRf/2024/", filtros)
        nova = client.get(f"{BASE}/{rf}/anos_letivos/2024/", filtros)
        assert nova.status_code == antiga.status_code == 204

    def test_nome_e_contrato_resumido(self, client, atribuicao):
        """Reutiliza a escolha de nome existente e retorna só RF e nome."""
        professor = atribuicao.cargo_base.professor
        professor.nome_social = "Nome social"
        professor.save()
        resposta = client.get(
            f"{BASE}/{professor.codigo_rf}/anos_letivos/2024/"
        )
        assert resposta.json() == {
            "codigo_rf": professor.codigo_rf,
            "nome": "Nome social",
        }

    @pytest.mark.parametrize(
        "sufixo",
        [
            "2024/?tipo_busca=invalido",
            "2024/?buscar_outros_cargos=invalido",
            "0/",
        ],
    )
    def test_validacao(self, client, sufixo):
        """Rejeita filtros inválidos ou ano zero antes da consulta."""
        assert (
            client.get(f"{BASE}/000001/anos_letivos/{sufixo}").status_code
            == 400
        )

    def test_autenticacao_e_ausencia(self, client, anon):
        """Mantém autenticação e resultado vazio quando não há professor."""
        url = f"{BASE}/000001/anos_letivos/2024/"
        assert anon.get(url).status_code in (401, 403)
        assert client.get(url).status_code == 204


def test_schema_indica_migracao():
    """As rotas antigas indicam o tipo de busca que mantém seu fluxo."""
    paths = SchemaGenerator().get_schema(public=True)["paths"]
    for tipo, rota in ROTAS.items():
        operacao = paths[f"{BASE}/{{codigo_rf}}/{rota}/{{ano_letivo}}/"]["get"]
        assert operacao["deprecated"] is True
        assert f"tipo_busca={tipo}" in operacao["description"]
    operacao = paths[f"{BASE}/{{codigo_rf}}/anos_letivos/{{ano_letivo}}/"][
        "get"
    ]
    assert not operacao.get("deprecated", False)
    assert {"dre_id", "ue_id", "buscar_outros_cargos", "tipo_busca"} <= {
        parametro["name"] for parametro in operacao["parameters"]
    }
