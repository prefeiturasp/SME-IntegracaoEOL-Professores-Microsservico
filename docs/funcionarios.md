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
