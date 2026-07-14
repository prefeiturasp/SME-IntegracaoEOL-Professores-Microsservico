# language: pt

Funcionalidade: Funcionários

  Como consumidor da API
  Quero consultar informações de funcionários
  Para garantir que a API retorna sucesso

  Background:
    Dado que possuo acesso à API de funcionários

  # ======================================================
  # TURMAS ATRIBUÍDAS DA UE
  # ======================================================

  Cenário: Turmas atribuídas da UE 019362
    Quando envio uma requisição POST para buscar turmas atribuídas da UE definida em "FUNCIONARIOS_UE_1"
    Então a API de funcionários deve responder com status 200

  Cenário: Turmas atribuídas da UE 019283
    Quando envio uma requisição POST para buscar turmas atribuídas da UE definida em "FUNCIONARIOS_UE_2"
    Então a API de funcionários deve responder com status 200

  Cenário: Turmas atribuídas da UE 092932
    Quando envio uma requisição POST para buscar turmas atribuídas da UE definida em "FUNCIONARIOS_UE_3"
    Então a API de funcionários deve responder com status 200

  # ======================================================
  # FUNCIONÁRIOS POR RF, UE E NOME
  # ======================================================

  Cenário: Funcionário 8093024 na UE 093301
    Quando envio uma requisição POST para buscar funcionário definido em "FUNCIONARIOS_RF_UE_NOME_1"
    Então a API de funcionários deve responder com status 200

  Cenário: Funcionário 8081450 na UE 019487
    Quando envio uma requisição POST para buscar funcionário definido em "FUNCIONARIOS_RF_UE_NOME_2"
    Então a API de funcionários deve responder com status 200

  Cenário: Funcionário 8415927 na UE 094421
    Quando envio uma requisição POST para buscar funcionário definido em "FUNCIONARIOS_RF_UE_NOME_3"
    Então a API de funcionários deve responder com status 200

  # ======================================================
  # DISCIPLINAS DA TURMA
  # ======================================================

  Cenário: Disciplinas da turma 2859172
    Quando envio uma requisição GET para buscar disciplinas da turma definida em "FUNCIONARIOS_TURMA_DISCIPLINAS_1"
    Então a API de funcionários deve responder com status 200

  Cenário: Disciplinas da turma 3041962
    Quando envio uma requisição GET para buscar disciplinas da turma definida em "FUNCIONARIOS_TURMA_DISCIPLINAS_2"
    Então a API de funcionários deve responder com status 200

  Cenário: Disciplinas da turma 3136772
    Quando envio uma requisição GET para buscar disciplinas da turma definida em "FUNCIONARIOS_TURMA_DISCIPLINAS_3"
    Então a API de funcionários deve responder com status 200

  # ======================================================
  # SWITCH ABRANGÊNCIA DE TURMAS
  # ======================================================

  Cenário: Abrangência UE - RF 2304503
    Quando envio uma requisição GET para buscar turmas com abrangência UE definida em "FUNCIONARIOS_ABRANGENCIA_UE"
    Então a API de funcionários deve responder com status 200

  Cenário: Abrangência UE Turmas Disciplinas - RF 1168991
    Quando envio uma requisição GET para buscar turmas com abrangência UE Turmas Disciplinas definida em "FUNCIONARIOS_ABRANGENCIA_UE_TURMAS_DISCIPLINAS"
    Então a API de funcionários deve responder com status 200

  Cenário: Abrangência DRE - RF 1168991
    Quando envio uma requisição GET para buscar turmas com abrangência DRE definida em "FUNCIONARIOS_ABRANGENCIA_DRE"
    Então a API de funcionários deve responder com status 200

  Cenário: Abrangência DRE Escolas Atribuídas - RF 1168991
    Quando envio uma requisição GET para buscar turmas com abrangência DRE Escolas Atribuídas definida em "FUNCIONARIOS_ABRANGENCIA_DRE_ESCOLAS"
    Então a API de funcionários deve responder com status 200
