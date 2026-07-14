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
    Quando envio uma requisição POST para buscar turmas atribuídas da UE "019362"
    Então a API de funcionários deve responder com status 200

  Cenário: Turmas atribuídas da UE 019283
    Quando envio uma requisição POST para buscar turmas atribuídas da UE "019283"
    Então a API de funcionários deve responder com status 200

  Cenário: Turmas atribuídas da UE 092932
    Quando envio uma requisição POST para buscar turmas atribuídas da UE "092932"
    Então a API de funcionários deve responder com status 200

  # ======================================================
  # BUSCAR TURMAS ELEGÍVEIS
  # ======================================================

  Cenário: RF 7118601 - turma 3020441 - componente 512
    Quando envio uma requisição POST para buscar turmas elegíveis do RF "7118601" turma 3020441 componente 512
    Então a API de funcionários deve responder com status 200 ou 204

  Cenário: RF 8366888 - turma 3020571 - componente 513
    Quando envio uma requisição POST para buscar turmas elegíveis do RF "8366888" turma 3020571 componente 513
    Então a API de funcionários deve responder com status 200 ou 204

  Cenário: RF 9349910 - turma 3082265 - componente 513
    Quando envio uma requisição POST para buscar turmas elegíveis do RF "9349910" turma 3082265 componente 513
    Então a API de funcionários deve responder com status 200 ou 204

  Cenário: RF 8956952 - turma 3020441 - componente 513
    Quando envio uma requisição POST para buscar turmas elegíveis do RF "8956952" turma 3020441 componente 513
    Então a API de funcionários deve responder com status 200 ou 204

  Cenário: RF 9336711 - turma 3020384 - componente 513
    Quando envio uma requisição POST para buscar turmas elegíveis do RF "9336711" turma 3020384 componente 513
    Então a API de funcionários deve responder com status 200 ou 204

  # ======================================================
  # FUNCIONÁRIOS POR RF, UE E NOME
  # ======================================================

  Cenário: Funcionário 8093024 na UE 093301
    Quando envio uma requisição POST para buscar funcionário RF "8093024" UE "093301" nome "MARCELO GERACE MELLO"
    Então a API de funcionários deve responder com status 200

  Cenário: Funcionário 8081450 na UE 019487
    Quando envio uma requisição POST para buscar funcionário RF "8081450" UE "019487" nome "UELTON SA GONCALVES"
    Então a API de funcionários deve responder com status 200

  Cenário: Funcionário 8415927 na UE 094421
    Quando envio uma requisição POST para buscar funcionário RF "8415927" UE "094421" nome "SONIA REGINA DONAIRE ANDRIANI"
    Então a API de funcionários deve responder com status 200

  # ======================================================
  # DISCIPLINAS DA TURMA
  # ======================================================

  Cenário: Disciplinas da turma 2859172
    Quando envio uma requisição GET para buscar disciplinas da turma 2859172
    Então a API de funcionários deve responder com status 200

  Cenário: Disciplinas da turma 3041962
    Quando envio uma requisição GET para buscar disciplinas da turma 3041962
    Então a API de funcionários deve responder com status 200

  Cenário: Disciplinas da turma 3136772
    Quando envio uma requisição GET para buscar disciplinas da turma 3136772
    Então a API de funcionários deve responder com status 200

  # ======================================================
  # SWITCH ABRANGÊNCIA DE TURMAS
  # ======================================================

  Cenário: Abrangência UE - RF 2304503
    Quando envio uma requisição GET para buscar turmas com abrangência UE do RF "2304503" perfil "46e1e074-37d6-e911-abd6-f81654fe895d"
    Então a API de funcionários deve responder com status 200

  Cenário: Abrangência UE Turmas Disciplinas - RF 1168991
    Quando envio uma requisição GET para buscar turmas com abrangência UE Turmas Disciplinas do RF "1168991" perfil "cf181fd4-dd30-47cf-a97d-57e602fd8d10"
    Então a API de funcionários deve responder com status 200

  Cenário: Abrangência DRE - RF 1168991
    Quando envio uma requisição GET para buscar turmas com abrangência DRE do RF "1168991" perfil "4fe1e074-37d6-e911-abd6-f81654fe895d"
    Então a API de funcionários deve responder com status 200

  Cenário: Abrangência DRE Escolas Atribuídas - RF 1168991
    Quando envio uma requisição GET para buscar turmas com abrangência DRE Escolas Atribuídas do RF "1168991" perfil "4ee1e074-37d6-e911-abd6-f81654fe895d"
    Então a API de funcionários deve responder com status 200
