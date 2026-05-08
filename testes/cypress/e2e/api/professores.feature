# language: pt

Funcionalidade: API - Professores

  Cenário: Consultar professores por escola e ano letivo
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professores por escola e ano letivo
    Então o status deve ser válido
    E o retorno deve ser válido

  Cenário: Consultar turmas por escola
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas por escola
    Então o status deve ser válido
    E o retorno deve ser válido

  Cenário: Consultar professor por RF
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF
    Então o status deve ser válido
    E o retorno deve ser válido

  Cenário: Buscar professores por lista de RF
    Dado que possuo acesso à API de professores
    Quando realizo busca por lista de RF
    Então o status deve ser válido
    E o retorno deve ser válido

  Cenário: Repetir consulta de professores (consistência)
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professores por escola e ano letivo
    Então o status deve ser válido

    Quando realizo consulta de professores por escola e ano letivo
    Então o status deve ser válido