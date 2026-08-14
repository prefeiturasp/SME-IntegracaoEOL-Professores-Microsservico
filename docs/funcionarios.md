# Funcionários

Os contratos de funcionários preservam a leitura de vínculos ativos de
servidores e funcionários externos por unidade, cargo, perfil e filtros de
busca.

## Identificação do usuário

Alguns contratos expõem o campo `login` para indicar o usuário associado ao
funcionário. No legado, esse valor é preenchido a partir da Identidade
corporativa; quando não há usuário associado, o campo pode ser nulo mesmo que o
funcionário exista no EOL.

Enquanto essa integração não estiver disponível neste microsserviço, o
Transition Gateway é responsável por manter o formato de resposta esperado
pelos consumidores. O microsserviço retorna os dados funcionais conhecidos e
não infere ausência de usuário sem uma fonte de Identidade.

## Usuários por perfil

Em `GET /api/v1/professores/funcionarios/perfis/{id_perfil}/`, a presença de
`codigo_dre` indica a consulta por vínculos de funcionários na DRE. Nesse
fluxo, os dados de cargo, função e vínculo são preservados.

Quando a consulta recebe apenas `codigo_rf`, o legado busca o usuário por login
na Identidade corporativa. Nesse fluxo, o retorno traz os dados básicos do
usuário e os campos de vínculo permanecem com os valores padrão.

## Cargos por registro funcional

A consulta de cargos por registro funcional retorna os vínculos funcionais
ativos associados ao servidor. O retorno é consolidado para preservar os
dados de cargo base, cargo sobreposto e função atividade sem recompor essas
relações em tempo de resposta.

## Conecta Formação

Os contratos do Conecta Formação usam os perfis do sistema correspondente no
CoreSSO. Os contratos já existentes do SGP continuam filtrando os perfis do
sistema SGP para evitar misturar usuários de sistemas diferentes na mesma
resposta.

## Professores por escola e ano

A consulta de professores por escola e ano retorna a visão materializada das
atribuições da unidade educacional. Quando a origem possui mais de uma
atribuição ativa para a mesma turma e componente, a escolha do professor é
resolvida pela carga de referência para manter estabilidade no retorno.

Essa estabilização evita que o microsserviço replique variações ocasionais da
origem quando não há desempate explícito entre atribuições concorrentes.
