"""Testes das views do domínio de funcionários."""

import pytest

pytestmark = pytest.mark.django_db

_BASE = "/api/v1/professores"


class TestEP25FuncionariosPorUE:
    def test_retorna_funcionario_lotado(self, client, lotacao):
        res = client.get(f"{_BASE}/escolas/000532/funcionarios/")
        assert res.status_code == 200
        assert any(f["codigo_rf"] == "7654321" for f in res.data)

    def test_ue_sem_lotacao_retorna_vazio(self, client, db):
        res = client.get(f"{_BASE}/escolas/000532/funcionarios/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/escolas/000532/funcionarios/")
        assert res.status_code == 403


class TestEP26FuncionariosPorUECargo:
    def test_cargo_correto_retorna_funcionario(self, client, lotacao):
        res = client.get(f"{_BASE}/escolas/000532/funcionarios/cargos/3379/")
        assert res.status_code == 200
        assert any(f["codigo_rf"] == "7654321" for f in res.data)

    def test_cargo_errado_retorna_vazio(self, client, lotacao):
        res = client.get(f"{_BASE}/escolas/000532/funcionarios/cargos/9999/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/escolas/000532/funcionarios/cargos/3379/")
        assert res.status_code == 403


class TestEP26BFuncionariosCargosQuery:
    def test_cargo_na_lista_retorna_funcionario(self, client, lotacao):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/cargos/?cargos=3379&cargos=3085"
        )
        assert res.status_code == 200
        assert any(f["funcionario_rf"] == "7654321" for f in res.data)

    def test_sem_cargos_retorna_todos_da_ue(self, client, lotacao):
        res = client.get(f"{_BASE}/escolas/000532/funcionarios/cargos/")
        assert res.status_code == 200
        assert any(f["codigo_rf"] == "7654321" for f in res.data)

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/escolas/000532/funcionarios/cargos/?cargos=3379"
        )
        assert res.status_code == 403


class TestEP27FuncionariosFuncaoAtividade:
    def test_retorna_funcionario_com_funcao(self, client, funcao_atividade):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-atividades/1/"
        )
        assert res.status_code == 200
        assert any(f["codigo_rf"] == "7654321" for f in res.data)

    def test_sem_funcao_retorna_vazio(self, client, db):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-atividades/1/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-atividades/1/"
        )
        assert res.status_code == 403


class TestEP27BFuncionariosFuncoesAtividadesQuery:
    def test_retorna_funcionario_com_funcao(self, client, funcao_atividade):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-atividades/"
            "?funcoes_atividades=1&funcoes_atividades=2"
        )
        assert res.status_code == 200
        assert any(f["funcionario_rf"] == "7654321" for f in res.data)

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-atividades/"
        )
        assert res.status_code == 403


class TestEP28FuncionariosFuncaoExterna:
    def test_funcao_correta_retorna_externo(self, client, contrato_externo):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-externas/5/"
        )
        assert res.status_code == 200
        assert res.data[0]["cpf"] == "98765432100"
        assert res.data[0]["nome_servidor"] == "João Ext"
        assert res.data[0]["codigo_escola"] == "000532"

    def test_funcao_errada_retorna_vazio(self, client, contrato_externo):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-externas/999/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-externas/5/"
        )
        assert res.status_code == 403


class TestEP28BFuncionariosFuncoesExternasQuery:
    def test_funcao_na_lista_retorna_externo(self, client, contrato_externo):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-externas/?funcoes=5&funcoes=6"
        )
        assert res.status_code == 200
        assert res.data[0]["cpf"] == "98765432100"
        assert res.data[0]["nome_servidor"] == "João Ext"
        assert res.data[0]["codigo_escola"] == "000532"

    def test_lista_sem_match_retorna_vazio(self, client, contrato_externo):
        res = client.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-externas/?funcoes=999"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/escolas/000532/funcionarios/funcoes-externas/"
        )
        assert res.status_code == 403


class TestEP29CargosFuncionario:
    def test_retorna_cargo_do_servidor(self, client, cargo_base):
        res = client.get(f"{_BASE}/funcionarios/cargo/7654321/")
        assert res.status_code == 200
        assert len(res.data) >= 1
        assert res.data[0]["rf"] == 7654321

    def test_sem_cargo_retorna_lista_vazia(self, client, db):
        res = client.get(f"{_BASE}/funcionarios/cargo/7654321/")
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/funcionarios/cargo/7654321/")
        assert res.status_code == 403


class TestEP30FuncionarioExternoPorCpf:
    def test_encontrado_retorna_dados(self, client, contrato_externo):
        res = client.get(
            f"{_BASE}/funcionarios/funcionario-externo/98765432100/"
        )
        assert res.status_code == 200
        assert res.data[0]["cpf"] == "98765432100"

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(
            f"{_BASE}/funcionarios/funcionario-externo/00000000000/"
        )
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/funcionarios/funcionario-externo/98765432100/"
        )
        assert res.status_code == 403


class TestEP31NomeServidor:
    def test_encontrado_retorna_nome_e_cpf(self, client, professor):
        res = client.get(f"{_BASE}/funcionarios/nome-servidor/7654321/")
        assert res.status_code == 200
        assert res.data["nome"] == "Ana Silva"
        assert res.data["cpf"] == "12345678900"

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(f"{_BASE}/funcionarios/nome-servidor/0000000/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/funcionarios/nome-servidor/7654321/")
        assert res.status_code == 403


class TestEP32DreUeAtribuicao:
    def test_com_lotacao_retorna_dre_e_ue(self, client, lotacao, ue):
        res = client.get(f"{_BASE}/funcionarios/nome-usuario-eol/7654321/")
        assert res.status_code == 200
        assert res.content.decode() == "Ana Silva"

    def test_sem_lotacao_retorna_campos_nulos(self, client, professor):
        res = client.get(f"{_BASE}/funcionarios/nome-usuario-eol/7654321/")
        assert res.status_code == 200
        assert "text/plain" in res["Content-Type"]

    def test_nao_encontrado_retorna_404(self, client, db):
        res = client.get(f"{_BASE}/funcionarios/nome-usuario-eol/0000000/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/funcionarios/nome-usuario-eol/7654321/")
        assert res.status_code == 403


class TestEP33ServidorAtivo:
    def test_cargo_sem_fim_retorna_true(self, client, cargo_base):
        # dt_fim_nomeacao=None → servidor ativo
        res = client.get(f"{_BASE}/acessos/funcionario-ativo/7654321/")
        assert res.status_code == 200
        assert res.data is True

    def test_sem_cargo_retorna_false(self, client, db):
        res = client.get(f"{_BASE}/acessos/funcionario-ativo/7654321/")
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/acessos/funcionario-ativo/7654321/")
        assert res.status_code == 403


class TestEP34DreUeAtribuicaoCargo:
    def test_cargo_com_lotacao_retorna_dre_ue(self, client, lotacao):
        res = client.get(
            f"{_BASE}/funcionarios/atribuicao/7654321/cargo/3379/"
        )
        assert res.status_code == 200
        assert res.data[0]["codigo_rf"] == "7654321"
        assert res.data[0]["codigo_ue"] == "000532"

    def test_cargo_sem_lotacao_retorna_ue_nula(self, client, cargo_base):
        res = client.get(
            f"{_BASE}/funcionarios/atribuicao/7654321/cargo/3379/"
        )
        assert res.status_code == 200
        assert res.data[0]["codigo_ue"] is None

    def test_cargo_inexistente_retorna_404(self, client, db):
        res = client.get(
            f"{_BASE}/funcionarios/atribuicao/0000000/cargo/3379/"
        )
        assert res.status_code == 200
        assert res.data == []

    def test_repository_none_retorna_404(self, client, monkeypatch):
        from apps.funcionarios.api import views

        monkeypatch.setattr(
            views.repository,
            "dre_ue_cargo",
            lambda registro_funcional, codigo_cargo: None,
        )

        res = client.get(
            f"{_BASE}/funcionarios/atribuicao/7654321/cargo/3379/"
        )

        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/funcionarios/atribuicao/7654321/cargo/3379/")
        assert res.status_code == 403


class TestEP35UsuariosSGP:
    def test_guid_vazio_sem_dre_ou_rf_retorna_400_como_legado(self, client):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/"
            "00000000-0000-0000-0000-000000000000/"
        )
        assert res.status_code == 400
        assert res.data == (
            "O código da Dre ou código rf/login deve ser informados."
        )

    def test_guid_vazio_com_codigo_rf_retorna_funcionario(
        self, client, lotacao
    ):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/"
            "00000000-0000-0000-0000-000000000000/?codigo_rf=7654321"
        )
        assert res.status_code == 200
        assert len(res.data) == 1
        assert res.data[0]["codigo_rf"] == "7654321"

    def test_guid_vazio_com_codigo_dre_retorna_400_como_legado(self, client):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/"
            "00000000-0000-0000-0000-000000000000/?codigo_dre=108100"
        )
        assert res.status_code == 400
        assert res.data == (
            "Houve um comportamento inesperado do sistema. "
            "Por favor, contate a SME."
        )

    def test_retorna_funcionario_com_lotacao_ativa(self, client, lotacao):
        res = client.get(f"{_BASE}/funcionarios/perfis/perfil-guid-123/")
        assert res.status_code == 200
        assert any(u["codigo_rf"] == "7654321" for u in res.data)

    def test_filtro_ue_retorna_apenas_da_ue(self, client, lotacao):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/perfil-guid-123/?codigo_ue=000532"
        )
        assert res.status_code == 200
        assert any(u["codigo_rf"] == "7654321" for u in res.data)

    def test_filtro_ue_errada_retorna_404(self, client, lotacao):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/perfil-guid-123/?codigo_ue=999999"
        )
        assert res.status_code == 404

    def test_sem_lotacao_ativa_retorna_404(self, client, db):
        res = client.get(f"{_BASE}/funcionarios/perfis/perfil-guid-123/")
        assert res.status_code == 404

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(f"{_BASE}/funcionarios/perfis/perfil-guid-123/")
        assert res.status_code == 403


class TestEP36FuncionariosSGPDre:
    def test_guid_vazio_retorna_400_como_legado(self, client):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/"
            "00000000-0000-0000-0000-000000000000/dres/108100/"
        )
        assert res.status_code == 400
        assert res.data == (
            "Houve um comportamento inesperado do sistema. "
            "Por favor, contate a SME."
        )

    def test_retorna_funcionario_da_dre(self, client, lotacao, ue):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/perfil-guid-123/dres/108100/"
        )
        assert res.status_code == 200
        assert any(u["codigo_rf"] == "7654321" for u in res.data)

    def test_dre_sem_funcionarios_retorna_404(self, client, db):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/perfil-guid-123/dres/108100/"
        )
        assert res.status_code == 404

    def test_filtro_rf_retorna_especifico(self, client, lotacao, ue):
        res = client.get(
            f"{_BASE}/funcionarios/perfis/perfil-guid-123/dres/108100/"
            "?codigo_rf=7654321"
        )
        assert res.status_code == 200
        assert len(res.data) == 1
        assert res.data[0]["codigo_rf"] == "7654321"

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/funcionarios/perfis/perfil-guid-123/dres/108100/"
        )
        assert res.status_code == 403


class TestEP37AcessoSondagem:
    def test_com_atribuicao_retorna_true(self, client, atribuicao):
        res = client.get(
            f"{_BASE}/perfis/servidores/7654321"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        assert res.status_code == 200
        assert res.data is True

    def test_sem_atribuicao_retorna_false(self, client, db):
        res = client.get(
            f"{_BASE}/perfis/servidores/7654321"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        assert res.status_code == 200
        assert res.data is False

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.get(
            f"{_BASE}/perfis/servidores/7654321"
            "/VerificaSeProfessorTemAcessoAhSondagem/"
        )
        assert res.status_code == 403


class TestEP38BuscarPorListaRF:
    def test_rf_existente_retorna_funcionario(self, client, professor):
        res = client.post(
            f"{_BASE}/funcionarios/BuscarPorListaRF/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 200
        assert any(f["codigo_rf"] == "7654321" for f in res.data)

    def test_rf_inexistente_retorna_vazio(self, client, db):
        res = client.post(
            f"{_BASE}/funcionarios/BuscarPorListaRF/",
            ["0000000"],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_lista_vazia_retorna_vazio(self, client, db):
        res = client.post(
            f"{_BASE}/funcionarios/BuscarPorListaRF/",
            [],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_corpo_invalido_usa_lista_vazia(self, client, db):
        res = client.post(
            f"{_BASE}/funcionarios/BuscarPorListaRF/",
            {"invalido": True},
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.post(
            f"{_BASE}/funcionarios/BuscarPorListaRF/",
            [],
            format="json",
        )
        assert res.status_code == 403


class TestEP39BuscarPorListaLogin:
    def test_login_existente_retorna_funcionario(self, client, professor):
        res = client.post(
            f"{_BASE}/funcionarios/BuscarPorListaLogin/",
            ["7654321"],
            format="json",
        )
        assert res.status_code == 200
        assert any(f["login"] == "7654321" for f in res.data)

    def test_login_inexistente_retorna_vazio(self, client, db):
        res = client.post(
            f"{_BASE}/funcionarios/BuscarPorListaLogin/",
            ["0000000"],
            format="json",
        )
        assert res.status_code == 200
        assert res.data == []

    def test_sem_api_key_retorna_403(self, anon):
        res = anon.post(
            f"{_BASE}/funcionarios/BuscarPorListaLogin/",
            [],
            format="json",
        )
        assert res.status_code == 403
