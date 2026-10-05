"""Testes dos services do dominio de funcionarios."""

import pytest

from apps.funcionarios import services


def test_funcionarios_por_lista_cargos_sem_cargos_usa_ue(monkeypatch):
    """Verifica consulta da unidade quando cargos não são informados."""
    chamadas = {}

    def fake(codigo_ue):
        chamadas["codigo_ue"] = codigo_ue
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repositories, "funcionarios_por_ue", fake)

    resultado = services.funcionarios_por_lista_cargos("000532", [])

    assert resultado == [{"codigo_rf": "7654321"}]
    assert chamadas["codigo_ue"] == "000532"


def test_supervisores_dres_delega_repository(monkeypatch):
    """Verifica delegacao da busca de supervisores consolidados."""
    chamadas = {}

    def fake(codigo_dre):
        chamadas["codigo_dre"] = codigo_dre
        return [{"codigo_rf": "1111111", "nome_servidor": "Supervisor"}]

    monkeypatch.setattr(
        services.repositories,
        "supervisores_dres",
        fake,
    )

    resultado = services.supervisores_dres("108100")

    assert resultado == [
        {"codigo_rf": "1111111", "nome_servidor": "Supervisor"}
    ]
    assert chamadas["codigo_dre"] == "108100"


def test_cargos_funcionario_delega_repository(monkeypatch):
    """Verifica delegação da busca de vínculos funcionais."""
    chamadas = {}

    def fake(registro_funcional):
        chamadas["registro_funcional"] = registro_funcional
        return ["vinculo"]

    monkeypatch.setattr(
        services.repositories,
        "cargos_funcionario",
        fake,
    )

    resultado = services.cargos_funcionario("7654321")

    assert resultado == ["vinculo"]
    assert chamadas["registro_funcional"] == "7654321"


def test_funcionarios_conecta_formacao_delega_repository(monkeypatch):
    """Verifica delegação da busca do Conecta Formação."""
    chamadas = {}

    def fake(filtros):
        chamadas["filtros"] = filtros
        return [{"rf": "7654321"}]

    monkeypatch.setattr(
        services.repositories,
        "funcionarios_conecta_formacao",
        fake,
    )

    resultado = services.funcionarios_conecta_formacao(
        {"codigos_cargos": [1]}
    )

    assert resultado == [{"rf": "7654321"}]
    assert chamadas["filtros"] == {"codigos_cargos": [1]}


def test_usuarios_conecta_formacao_retorna_resultado(monkeypatch):
    """Verifica retorno de usuários do Conecta Formação."""
    monkeypatch.setattr(
        services.repositories,
        "usuarios_conecta_formacao",
        lambda _perfis: [{"login": "0000001"}],
    )

    resultado = services.usuarios_conecta_formacao(["perfil"])

    assert resultado == [{"login": "0000001"}]


def test_usuarios_conecta_formacao_sem_resultado_retorna_lista_vazia(
    monkeypatch,
):
    """Verifica lista vazia quando usuários do Conecta não são encontrados."""
    monkeypatch.setattr(
        services.repositories,
        "usuarios_conecta_formacao",
        lambda _perfis: [],
    )

    resultado = services.usuarios_conecta_formacao(["perfil"])

    assert resultado == []


@pytest.mark.parametrize(
    ("funcao", "metodo"),
    [
        (
            services.funcionarios_por_lista_funcoes_atividade,
            "funcionarios_por_lista_funcoes_atividade",
        ),
        (
            services.funcionarios_por_lista_funcoes_externas,
            "funcionarios_por_lista_funcoes_externas",
        ),
    ],
)
def test_funcoes_query_converte_lista(monkeypatch, funcao, metodo):
    """Verifica conversao de funcoes recebidas por query string."""
    chamadas = {}

    def fake(codigo_ue, funcoes):
        chamadas["args"] = (codigo_ue, funcoes)
        return [{"ok": True}]

    monkeypatch.setattr(services.repositories, metodo, fake)

    resultado = funcao("000532", ["1", "2"])

    assert resultado == [{"ok": True}]
    assert chamadas["args"] == ("000532", [1, 2])


def test_perfil_placeholder_invalido_retorna_resultado(monkeypatch):
    """Verifica validação de perfil placeholder."""
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: True,
    )

    resultado = services.perfil_placeholder_invalido("perfil")

    assert resultado is True


def test_usuarios_sgp_sem_resultado_retorna_lista_vazia(monkeypatch):
    """Verifica lista vazia quando perfil nao retorna usuarios."""
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )
    monkeypatch.setattr(
        services.repositories,
        "usuarios_sgp_por_perfil",
        lambda *args, **kwargs: [],
    )

    resultado = services.usuarios_sgp_por_perfil("perfil")

    assert resultado == []


def test_usuarios_sgp_com_dre_sem_resultado_retorna_200(monkeypatch):
    """Verifica resposta legada quando consulta por DRE vem vazia."""
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )
    monkeypatch.setattr(
        services.repositories,
        "usuarios_sgp_por_perfil",
        lambda *args, **kwargs: [],
    )

    resultado = services.usuarios_sgp_por_perfil(
        "perfil",
        codigo_dre="108100",
    )

    assert resultado == []


def test_funcionarios_sgp_dre_converte_funcao(monkeypatch):
    """Verifica conversao de funcao de atividade opcional."""
    chamadas = {}
    monkeypatch.setattr(
        services.repositories,
        "perfil_placeholder_invalido",
        lambda id_perfil: False,
    )

    def fake(*args, **kwargs):
        chamadas["kwargs"] = kwargs
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repositories, "funcionarios_sgp_dre", fake)

    resultado = services.funcionarios_sgp_dre(
        "perfil",
        "108100",
        codigo_funcao_atividade="1",
    )

    assert resultado == [{"codigo_rf": "7654321"}]
    assert chamadas["kwargs"]["codigo_funcao_atividade"] == 1


@pytest.mark.parametrize(
    ("funcao", "metodo"),
    [
        (services.buscar_por_lista_rf, "buscar_por_lista_rf_func"),
        (services.buscar_por_lista_login, "buscar_por_lista_login"),
    ],
)
def test_payload_invalido_usa_lista_vazia(monkeypatch, funcao, metodo):
    """Verifica retorno vazio para entrada inválida."""
    chamadas = {}

    def fake(lista):
        chamadas["lista"] = lista
        return []

    monkeypatch.setattr(services.repositories, metodo, fake)

    resultado = funcao({"invalido": True})

    assert resultado == []
    assert chamadas["lista"] == []


def test_buscar_funcionarios_mapeia_filtros_do_payload(monkeypatch):
    """Verifica mapeamento dos filtros do payload para o repositories."""
    chamadas = {}

    def fake(codigo_rf, codigo_ue, nome_servidor):
        chamadas["kwargs"] = {
            "codigo_rf": codigo_rf,
            "codigo_ue": codigo_ue,
            "nome_servidor": nome_servidor,
        }
        return [{"codigo_rf": "7654321"}]

    monkeypatch.setattr(services.repositories, "buscar_funcionarios", fake)

    resultado = services.buscar_funcionarios(
        {
            "codigo_rf": "7654321",
            "codigo_ue": "000532",
            "nome_servidor": "Ana",
        }
    )

    assert resultado == [{"codigo_rf": "7654321"}]
    assert chamadas["kwargs"] == {
        "codigo_rf": "7654321",
        "codigo_ue": "000532",
        "nome_servidor": "Ana",
    }


def test_buscar_funcionarios_payload_invalido_usa_dict_vazio(monkeypatch):
    """Payload não-dict resulta em filtros vazios."""
    chamadas = {}

    def fake(codigo_rf, codigo_ue, nome_servidor):
        chamadas["kwargs"] = (codigo_rf, codigo_ue, nome_servidor)
        return []

    monkeypatch.setattr(services.repositories, "buscar_funcionarios", fake)

    resultado = services.buscar_funcionarios(None)

    assert resultado == []
    assert chamadas["kwargs"] == (None, None, None)


def test_funcionarios_por_unidade_perfis_vazio_retorna_lista_vazia(
    monkeypatch,
):
    """Verifica lista vazia para perfis não informados por unidade."""
    monkeypatch.setattr(
        services.repositories,
        "funcionarios_por_unidade_perfis",
        lambda *_args: [{"login": "0000001"}],
    )

    resultado = services.funcionarios_por_unidade_perfis("108100", [])

    assert resultado == []


def test_funcionarios_por_unidade_perfis_sem_resultado_retorna_lista_vazia(
    monkeypatch,
):
    """Verifica lista vazia quando unidade e perfis não retornam dados."""
    monkeypatch.setattr(
        services.repositories,
        "funcionarios_por_unidade_perfis",
        lambda *_args: [],
    )

    resultado = services.funcionarios_por_unidade_perfis("108100", ["perfil"])

    assert resultado == []


def test_logins_admins_sme_por_perfis_retorna_resultado(monkeypatch):
    """Verifica retorno de admins SME por perfis."""
    monkeypatch.setattr(
        services.repositories,
        "logins_admins_sme_por_perfis",
        lambda _perfis: ["0000001"],
    )

    resultado = services.logins_admins_sme_por_perfis(["perfil"])

    assert resultado == ["0000001"]


def test_logins_admins_sme_por_perfis_vazio_retorna_lista_vazia(
    monkeypatch,
):
    """Verifica lista vazia para perfis admins SME não informados."""
    monkeypatch.setattr(
        services.repositories,
        "logins_admins_sme_por_perfis",
        lambda _perfis: ["0000001"],
    )

    resultado = services.logins_admins_sme_por_perfis([])

    assert resultado == []


def test_dados_sigpae_sem_dados_retorna_601(monkeypatch):
    """Verifica erro legado quando SIGPAE nao encontra dados."""
    monkeypatch.setattr(
        services.repositories,
        "dados_sigpae_por_rf",
        lambda _codigo_rf: None,
    )

    resultado = services.dados_sigpae("0000001")

    assert resultado is None
