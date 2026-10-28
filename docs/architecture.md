# Cache das consultas de Professores

As representações de funcionários por cargo e Conecta Formação podem ser
reutilizadas neste microsserviço. A consulta e o contrato de cada operação
permanecem no fluxo existente.

Titulares por UE/data (P19) conserva o comportamento anterior: o MS consulta
diretamente os dados, e o Gateway mantém seu cache preexistente do resultado
completo por 240 minutos, incluindo os enriquecimentos. Essa operação não usa
o novo cache deste microsserviço.

## Integridade das fontes

O ETL governa a tabela `controle_carga_professores`, criada pela migration
`professores.0031_controlecargaprofessores`. O model neste serviço é
`managed=False`.

O ETL registra cada carga antes da primeira escrita, troca a geração e mantém
suas execuções ativas. Atualizações desse registro usam bloqueio de linha. Ao
concluir ou falhar, remove somente sua execução e troca novamente a geração.
Falhas mantêm as fontes bloqueadas para preenchimento até uma carga completa
bem-sucedida. Uma execução concorrente ainda ativa também mantém o bloqueio.
Uma carga amostral, inclusive `compat_professores --rodar-etl` ou uma execução
limitada por `EOL_LOTE_MAXIMO`, deixa o preenchimento bloqueado até uma carga
completa; uma amostra não comprova a integridade de todas as fontes.

O MS consulta esse registro antes de cada lookup. Essa consulta adicional ao
banco é intencional: a validade não depende de um TTL de metadados ou de um
evento de invalidação que possa ser perdido. Em miss, consulta novamente a
geração antes de preencher o cache. Carga ativa, falha, tabela ausente ou estado
desconhecido levam ao fluxo normal, sem armazenar a resposta.

Quando a requisição já participa de uma transação, a leitura do controle usa
um savepoint. Assim, uma tabela indisponível não deixa a transação PostgreSQL
abortada antes da consulta normal. Fora de uma transação, o hit mantém uma
única consulta ao controle.

Uma interrupção abrupta pode deixar uma execução ativa no registro. Nesse caso,
a API continua consultando a origem. Confirmar o encerramento dos processos e
reconciliar o registro antes de uma nova carga completa; não remover marcadores
automaticamente por idade ou por expiração de um lock.

## Armazenamento

O backend Redis/KeyDB é compartilhado entre workers e réplicas. Usar capacidade
isolada do broker do ETL. As chaves contêm ambiente, operação, versão, geração
e um HMAC dos parâmetros validados. Credenciais, parâmetros pessoais e corpos
de respostas não são registrados em logs.

São armazenados bytes JSON do payload final, sem objetos ORM, `Response`, headers
ou IDs de requisição. Autenticação e validação acontecem antes do lookup. TTL
padrão: 300 segundos; limite por entrada: 16 MiB. Valores vazios legítimos são
distintos de entradas ausentes. Erros das consultas não são cacheados.

Um marcador compartilhado de construção dura 30 segundos. Requisições
concorrentes esperam no máximo 100 ms por um resultado; depois seguem a consulta
normal. O marcador expira sozinho para não permitir que um construtor atrasado
remova o marcador de outro. Essa espera reduz reconstruções simultâneas sem
transformar o armazenamento em dependência de disponibilidade da API.

## Configuração

O `.env.example` é um modelo versionado para configuração local. Ele mantém
somente a ativação e a conexão do cache; as opções de ajuste usam os padrões
abaixo quando não forem definidas no ambiente.

| Variável | Padrão | Uso |
| --- | --- | --- |
| `PROFESSORES_CACHE_ENABLED` | `0` | `1` ativa o cache após a preparação das fontes pelo ETL. |
| `PROFESSORES_CACHE_URL` | Vazio | URL de conexão com o Redis/KeyDB; obrigatória quando o cache está ativo. |
| `PROFESSORES_CACHE_TTL` | `300` | Validade das respostas em segundos; deve ser positiva. |
| `PROFESSORES_CACHE_MAX_BYTES` | `16777216` | Limite positivo por resposta em bytes, equivalente a 16 MiB. |
| `SME_ENVIRONMENT` | `local` | Identifica o ambiente no prefixo das chaves. |

Para ativar o cache, configure a URL fornecida pela infraestrutura, o ambiente
correto e `PROFESSORES_CACHE_ENABLED=1`, seguindo a ordem de publicação abaixo.
Para manter os padrões, não é necessário definir TTL ou limite de tamanho.
As réplicas devem compartilhar o backend, o ambiente e `DJANGO_SECRET_KEY`,
usada no HMAC dos parâmetros. Valores reais e credenciais ficam nas variáveis
do ambiente ou no `.env` local, que não deve ser versionado.

## Publicação

1. Aplicar a migration e publicar o ETL com o registro de cargas antes de ativar
   o cache do MS. Processos antigos do ETL não atualizam esse controle.
2. Executar uma carga completa pelo novo ETL. Para dados já conferidos, o comando
   `inicializar_cache_professores --confirmar-fontes-completas` exige auditoria
   concluída e ausência de cargas ativas; ele não executa uma carga de dados.
3. Configurar `PROFESSORES_CACHE_URL`, `SME_ENVIRONMENT` e
   `PROFESSORES_CACHE_ENABLED=1` no MS. O padrão é desabilitado. Ajustar
   `PROFESSORES_CACHE_TTL` e `PROFESSORES_CACHE_MAX_BYTES` se necessário.

Esta entrega não altera o Gateway. O fluxo e a consulta em lote do Pedagógico
usados em P19 permanecem como estavam.

Para desativar a reutilização, definir `PROFESSORES_CACHE_ENABLED=0`; a API
continua pelo fluxo normal. Não executar `FLUSHDB` para invalidar respostas:
trocas de geração tornam as entradas anteriores inacessíveis, e elas expiram.
Desativar o cache do MS antes de reverter o ETL para uma versão que não registra
cargas. A tabela técnica pode permanecer no banco durante essa reversão.
