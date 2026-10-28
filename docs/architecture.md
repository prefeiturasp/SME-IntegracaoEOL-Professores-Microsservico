# Cache das consultas de Professores

Conecta Formação e funcionários por cargo usam cache compartilhado em
Redis/KeyDB. A resposta é armazenada após autenticação e validação dos filtros.
As chaves consideram o ambiente, a operação, os parâmetros e a geração da carga.

## Invalidação

O ETL atualiza `controle_carga_professores` no início e no fim de cada carga.
O MS verifica esse controle antes de usar o cache e antes de gravar uma resposta.
A troca de geração invalida as entradas anteriores, que expiram pelo TTL.

Com carga ativa, falha ou controle indisponível, a API consulta a origem sem
usar ou preencher o cache. Cargas amostrais ou com falha bloqueiam o cache até
uma carga completa bem-sucedida. Falhas no Redis/KeyDB também levam à consulta
direta; erros das consultas não são armazenados.

Se uma carga for interrompida e deixar um registro ativo, confirme o encerramento
dos processos e reconcilie o controle no ETL antes de liberar o cache.

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

1. Aplicar `professores.0031_controlecargaprofessores` e publicar o ETL com o
   controle de cargas.
2. Executar uma carga completa. Para uma base já conferida, usar
   `inicializar_cache_professores --confirmar-fontes-completas`, que exige
   auditoria concluída e ausência de cargas ativas.
3. Configurar a URL, o ambiente e `PROFESSORES_CACHE_ENABLED=1` no MS.

Para desativar, definir `PROFESSORES_CACHE_ENABLED=0`. Faça isso antes de
reverter o ETL para uma versão sem controle de cargas.
