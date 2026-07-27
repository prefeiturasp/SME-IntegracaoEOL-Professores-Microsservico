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
