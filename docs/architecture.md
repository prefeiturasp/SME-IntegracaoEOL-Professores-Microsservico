# Cache das consultas de Professores

Conecta Formação e funcionários por cargo usam cache compartilhado em
Redis/KeyDB. A resposta é armazenada após autenticação e validação dos filtros.
As chaves consideram o ambiente, a operação, os parâmetros e a versão do formato.

## Invalidação

Cada resposta expira 300 segundos após a gravação, por padrão. A leitura não
renova esse prazo. Após a expiração, a próxima chamada consulta o banco.

O acompanhamento das cargas permanece na auditoria do ETL. O MS não consulta
o estado das execuções. Durante uma carga, respostas anteriores ou parciais
podem ser reutilizadas até expirar. A rotina diária às 3h deve terminar antes
do horário de uso.

Falhas no Redis/KeyDB levam à consulta direta; erros das consultas não são
armazenados.

## Configuração

O `.env.example` contém a ativação e a URL. As demais opções usam os padrões:

| Variável | Padrão | Uso |
| --- | --- | --- |
| `PROFESSORES_CACHE_ENABLED` | `0` | `1` ativa o cache. |
| `PROFESSORES_CACHE_URL` | Vazio | Conexão Redis/KeyDB, obrigatória para ativação. |
| `PROFESSORES_CACHE_TTL` | `300` | Validade em segundos, maior que zero. |
| `PROFESSORES_CACHE_MAX_BYTES` | `16777216` | Limite por entrada: 16 MiB, maior que zero. |
| `SME_ENVIRONMENT` | `local` | Prefixo das chaves por ambiente. |

Use um backend separado do broker do ETL. As réplicas devem compartilhar a
conexão, o ambiente e `DJANGO_SECRET_KEY`, usada no HMAC dos parâmetros.

## Ativação

Configurar a URL, o ambiente e `PROFESSORES_CACHE_ENABLED=1` no MS.
A ativação não exige migration nem alteração no ETL.

Para desativar, definir `PROFESSORES_CACHE_ENABLED=0`.
