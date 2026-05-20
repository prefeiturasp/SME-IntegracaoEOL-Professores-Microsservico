# SME-IntegracaoEOL Professores

O microsserviço `SME-IntegracaoEOL-Professores-Microsservico` é uma aplicação Django/DRF que expõe os contratos legados do EOL (SGP) relativos a Professores, Turmas históricas e Funcionários.

O serviço garante a compatibilidade com os consumidores da API (como o SGP e o Transition Gateway), preservando caminhos, parâmetros, códigos de status e cabeçalhos (autenticação por `X-API-Key`).

## Escopo e Arquitetura

Este microsserviço não realiza processos de ETL. Ele lê diretamente do banco de dados relacional (populado e de-normalizado por um ETL externo de referência) e responde aos contratos definidos pela SME.

A documentação é gerada automaticamente pelo Sphinx a partir das docstrings do código e está estruturada da seguinte forma:

```{toctree}
:maxdepth: 2
:caption: Referência de código

api
```
