# language: pt

Funcionalidade: Professores

  Como consumidor da API
  Quero consultar informações de professores
  Para garantir que a API retorna sucesso

  Background:
    Dado que possuo acesso à API de professores por RF

  Cenário: Consultar professor por RF e ano letivo com sucesso
    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

  Cenário: Repetir consulta de professor por RF e ano letivo para validar consistência
    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

  Cenário: Validar professor por RF com sucesso
    Dado que possuo acesso à API de validação de professor
    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

  Cenário: Repetir validação de professor por RF para validar consistência
    Dado que possuo acesso à API de validação de professor

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

  Cenário: Consultar nome do professor por RF com sucesso
    Dado que possuo acesso à API de consulta de nome do professor
    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

  Cenário: Repetir consulta do nome do professor por RF para validar consistência
    Dado que possuo acesso à API de consulta de nome do professor

    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

  Cenário: Validar múltiplas consultas sequenciais de professor
    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

  Cenário: Validar estabilidade da API em múltiplas chamadas consecutivas
    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

  Cenário: Validar estabilidade da consulta por RF em chamadas repetidas
    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

  Cenário: Validar estabilidade do endpoint BuscarPorRf
    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

  Cenário: Validar comportamento sequencial entre endpoints
    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

  Cenário: Validar consistência geral da API de professores
    Quando envio uma requisição GET para consultar nome do professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200

    Quando envio uma requisição GET para buscar professor por RF e ano letivo
    Então a API deve responder com status 200

    Quando envio uma requisição GET para validar professor por RF
    Então a API deve responder com status 200