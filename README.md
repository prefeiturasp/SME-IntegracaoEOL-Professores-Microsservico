# SME-IntegracaoEOL-Professores-Microsservico

Microsserviço **mock** do domínio Professores para o SGP (Sistema de Gestão Pedagógica) da SME-SP.

Todos os endpoints retornam dados estáticos — sem banco de dados, sem regras de negócio — para uso em testes de integração, desenvolvimento de front-end e validação de contratos de API.

---

## Estrutura dos Apps

| App | Responsabilidade | Endpoints |
|-----|-----------------|-----------|
| `apps.professores` | Professor, atribuições, validações, titulares | EP-01 a EP-23 |
| `apps.turmas` | Turmas históricas do professor | EP-24 |
| `apps.funcionarios` | Funcionários por UE/cargo/função, perfis SGP, acessos | EP-25 a EP-39 |
| `apps.core` | Autenticação por API key, dados mock compartilhados | — |

Os modelos ETL que cada app cobre:

- **professores**: `Professor`, `CargoBaseServidor`, `LotacaoServidor`, `CargoSobrepostoServidor`, `LaudoMedico`, `AtribuicaoAula`, `AgrupamentoAtribuicaoTerritorioSaber`
- **turmas**: `TurmaEscola`, `SerieTurmaGrade`, `TurmaEscolaGradePrograma`, `TurmaGradeTerritorioExperiencia`
- **funcionarios**: `FuncaoAtividadeCargoServidor`, `AtribuicaoExterno`, `Pessoa`, `ContratoExterno`, `UnidadeEducacional`

---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (para rodar via container)

---

## Rodar localmente (sem Docker)

```bash
# 1. Copiar o .env
cp .env.example .env

# 2. Instalar dependências
pip install -r requirements/local.txt

# 3. Aplicar migrations (SQLite, apenas tabelas internas do Django)
python manage.py migrate

# 4. Rodar o servidor
python manage.py runserver 0.0.0.0:[PORT_WEB]
```

Acesse em: http://localhost:[PORT_WEB]/api/v1/docs/

---

## Rodar com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: http://localhost:[PORT_WEB]/api/v1/docs/

---

## Rodar com Docker (produção)

```bash
cp .env.example .env
# Edite .env: DJANGO_DEBUG=0, DJANGO_SECRET_KEY=...
docker compose up --build
```

---

## Autenticação

Todos os endpoints exigem o header `X-API-Key` com o valor configurado em `API_KEY` (`.env`).

Valor padrão em desenvolvimento: `dev-key-default`

```bash
curl -H "X-API-Key: dev-key-default" http://localhost:[PORT_WEB]/api/v1/professores/7654321/
```

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/v1/docs/` | Swagger UI interativo |
| `/api/v1/schema/` | Schema OpenAPI 3 (JSON/YAML) |

---

## Endpoints implementados

### Professores (EP-01 a EP-23)

| ID | Método | Path |
|----|--------|------|
| EP-01 | GET | `/api/v1/professores/escolas/{codigoEolEscola}/professores/{anoLetivo}/` |
| EP-02 | GET | `/api/v1/professores/{codigoRF}/escolas/{codigoEolEscola}/turmas/anos_letivos/{anoLetivo}/` |
| EP-03 | GET | `/api/v1/professores/{codigoRF}/turmas/` |
| EP-04 | GET | `/api/v1/professores/{codigoRF}/turmas/anos_letivos/{anoLetivo}/` |
| EP-05 | GET | `/api/v1/professores/{rfProfessor}/` |
| EP-06 | GET | `/api/v1/professores/{codigoRf}/BuscarPorRf/{anoLetivo}/` |
| EP-07 | GET | `/api/v1/professores/{codigoRf}/BuscarPorRfDreUe/{anoLetivo}/` |
| EP-08 | GET | `/api/v1/professores/{anoLetivo}/AutoComplete/{dreId}/` |
| EP-09 | POST | `/api/v1/professores/{anoLetivo}/BuscarPorListaRF/` |
| EP-10 | GET | `/api/v1/professores/{codigoRf}/validade/` |
| EP-11 | GET | `/api/v1/professores/{codigoRF}/ehEmei/` |
| EP-12 | GET | `/api/v1/professores/{codigoRF}/turmas/{codigoTurma}/atribuicao/status/` |
| EP-13 | GET | `/api/v1/professores/{codigoRF}/turmas/{codigoTurma}/atribuicao/verificar/data/` |
| EP-14 | GET | `/api/v1/professores/{codigoRF}/turmas/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/verificar/data/` |
| EP-15 | GET | `/api/v1/professores/{codigoRF}/turmas/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/verificar/datatick/` |
| EP-16 | GET | `/api/v1/professores/{codigoRF}/turmas/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/recorrencia/verificar/datas/` |
| EP-17 | POST | `/api/v1/professores/{codigoRf}/disciplina/{disciplinaId}/turmas/` |
| EP-18 | POST | `/api/v1/professores/{codigoRf}/turmas/{codigoTurma}/componentes/{componenteCurricularId}/atribuicao/periodo/inicio/{dataInicioPeriodo}/fim/{dataFimPeriodo}/` |
| EP-19 | GET | `/api/v1/professores/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/data/` |
| EP-20 | GET | `/api/v1/professores/titular/turmas/{codigoTurma}/componentes-curriculares/{codigoComponenteCurricular}/` |
| EP-21 | GET | `/api/v1/professores/titulares/` |
| EP-22 | GET | `/api/v1/professores/{codigoTurma}/titulares/realizaAgrupamentoComponente/{realizaAgrupamento}/` |
| EP-23 | GET | `/api/v1/professores/titulares/ue/{ueCodigo}/{dataReferencia}/` |

### Turmas (EP-24)

| ID | Método | Path |
|----|--------|------|
| EP-24 | GET | `/api/v1/professores/turmas/anos-letivos/{anoLetivo}/professor/{professorRf}/turmas-historicas-geral/` |

### Funcionários (EP-25 a EP-39)

| ID | Método | Path |
|----|--------|------|
| EP-25 | GET | `/api/v1/professores/escolas/{codigoUE}/funcionarios/` |
| EP-26 | GET | `/api/v1/professores/escolas/{codigoUE}/funcionarios/cargos/{codigoCargo}/` |
| EP-26-B | GET | `/api/v1/professores/escolas/{ueCodigo}/funcionarios/cargos/` |
| EP-27 | GET | `/api/v1/professores/escolas/{codigoUE}/funcionarios/funcoes-atividades/{codigoFuncaoAtividade}/` |
| EP-27-B | GET | `/api/v1/professores/escolas/{ueCodigo}/funcionarios/funcoes-atividades/` |
| EP-28 | GET | `/api/v1/professores/escolas/{codigoUE}/funcionarios/funcoes-externas/{codigoFuncaoExterna}/` |
| EP-28-B | GET | `/api/v1/professores/escolas/{ueCodigo}/funcionarios/funcoes-externas/` |
| EP-29 | GET | `/api/v1/professores/funcionarios/cargo/{registroFuncional}/` |
| EP-30 | GET | `/api/v1/professores/funcionarios/funcionario-externo/{cpf}/` |
| EP-31 | GET | `/api/v1/professores/funcionarios/nome-servidor/{registroFuncional}/` |
| EP-32 | GET | `/api/v1/professores/funcionarios/nome-usuario-eol/{registroFuncional}/` |
| EP-33 | GET | `/api/v1/professores/acessos/funcionario-ativo/{registroFuncional}/` |
| EP-34 | GET | `/api/v1/professores/funcionarios/atribuicao/{registroFuncional}/cargo/{codigoCargo}/` |
| EP-35 | GET | `/api/v1/professores/funcionarios/perfis/{idPerfil}/` |
| EP-36 | GET | `/api/v1/professores/funcionarios/perfis/{idPerfil}/dres/{codigoDre}/` |
| EP-37 | GET | `/api/v1/professores/perfis/servidores/{codigoRF}/VerificaSeProfessorTemAcessoAhSondagem/` |
| EP-38 | POST | `/api/v1/professores/funcionarios/BuscarPorListaRF/` |
| EP-39 | POST | `/api/v1/professores/funcionarios/BuscarPorListaLogin/` |

---

## Referências

- Contrato completo: `../swagger_contrato_microsservico.md`
- Projeto ETL de referência: `../SME-SGP-MS-ETL/`
