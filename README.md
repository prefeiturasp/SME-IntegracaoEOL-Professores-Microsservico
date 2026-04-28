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

Acesse em: http://localhost:[PORT_WEB]/api/docs/

---

## Rodar com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: http://localhost:[PORT_WEB]/api/docs/

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
curl -H "X-API-Key: dev-key-default" http://localhost:[PORT_WEB]/api/professores/7654321/
```

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 (JSON/YAML) |

---

## Endpoints implementados

### Professores (EP-01 a EP-23)

| ID | Método | Path |
|----|--------|------|
| EP-01 | GET | `/api/escolas/{codigoEolEscola}/professores/{anoLetivo}/` |
| EP-02 | GET | `/api/professores/{codigoRF}/escolas/{codigoEolEscola}/turmas/anos_letivos/{anoLetivo}/` |
| EP-03 | GET | `/api/professores/{codigoRF}/turmas/` |
| EP-04 | GET | `/api/professores/{codigoRF}/turmas/anos_letivos/{anoLetivo}/` |
| EP-05 | GET | `/api/professores/{rfProfessor}/` |
| EP-06 | GET | `/api/professores/{codigoRf}/BuscarPorRf/{anoLetivo}/` |
| EP-07 | GET | `/api/professores/{codigoRf}/BuscarPorRfDreUe/{anoLetivo}/` |
| EP-08 | GET | `/api/professores/{anoLetivo}/AutoComplete/{dreId}/` |
| EP-09 | POST | `/api/professores/{anoLetivo}/BuscarPorListaRF/` |
| EP-10 | GET | `/api/professores/{codigoRf}/validade/` |
| EP-11 | GET | `/api/professores/{codigoRF}/ehEmei/` |
| EP-12 | GET | `/api/professores/{codigoRF}/turmas/{codigoTurma}/atribuicao/status/` |
| EP-13 | GET | `/api/professores/{codigoRF}/turmas/{codigoTurma}/atribuicao/verificar/data/` |
| EP-14 | GET | `/api/professores/{codigoRF}/turmas/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/verificar/data/` |
| EP-15 | GET | `/api/professores/{codigoRF}/turmas/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/verificar/datatick/` |
| EP-16 | GET | `/api/professores/{codigoRF}/turmas/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/recorrencia/verificar/datas/` |
| EP-17 | POST | `/api/professores/{codigoRf}/disciplina/{disciplinaId}/turmas/` |
| EP-18 | POST | `/api/professores/{codigoRf}/turmas/{codigoTurma}/componentes/{componenteCurricularId}/atribuicao/periodo/inicio/{dataInicioPeriodo}/fim/{dataFimPeriodo}/` |
| EP-19 | GET | `/api/professores/{codigoTurma}/disciplinas/{disciplinaId}/atribuicao/data/` |
| EP-20 | GET | `/api/professores/titular/turmas/{codigoTurma}/componentes-curriculares/{codigoComponenteCurricular}/` |
| EP-21 | GET | `/api/professores/titulares/` |
| EP-22 | GET | `/api/professores/{codigoTurma}/titulares/realizaAgrupamentoComponente/{realizaAgrupamento}/` |
| EP-23 | GET | `/api/professores/titulares/ue/{ueCodigo}/{dataReferencia}/` |

### Turmas (EP-24)

| ID | Método | Path |
|----|--------|------|
| EP-24 | GET | `/api/turmas/anos-letivos/{anoLetivo}/professor/{professorRf}/turmas-historicas-geral/` |

### Funcionários (EP-25 a EP-39)

| ID | Método | Path |
|----|--------|------|
| EP-25 | GET | `/api/escolas/{codigoUE}/funcionarios/` |
| EP-26 | GET | `/api/escolas/{codigoUE}/funcionarios/cargos/{codigoCargo}/` |
| EP-26-B | GET | `/api/escolas/{ueCodigo}/funcionarios/cargos/` |
| EP-27 | GET | `/api/escolas/{codigoUE}/funcionarios/funcoes-atividades/{codigoFuncaoAtividade}/` |
| EP-27-B | GET | `/api/escolas/{ueCodigo}/funcionarios/funcoes-atividades/` |
| EP-28 | GET | `/api/escolas/{codigoUE}/funcionarios/funcoes-externas/{codigoFuncaoExterna}/` |
| EP-28-B | GET | `/api/escolas/{ueCodigo}/funcionarios/funcoes-externas/` |
| EP-29 | GET | `/api/funcionarios/cargo/{registroFuncional}/` |
| EP-30 | GET | `/api/funcionarios/funcionario-externo/{cpf}/` |
| EP-31 | GET | `/api/funcionarios/nome-servidor/{registroFuncional}/` |
| EP-32 | GET | `/api/funcionarios/nome-usuario-eol/{registroFuncional}/` |
| EP-33 | GET | `/api/acessos/funcionario-ativo/{registroFuncional}/` |
| EP-34 | GET | `/api/funcionarios/atribuicao/{registroFuncional}/cargo/{codigoCargo}/` |
| EP-35 | GET | `/api/funcionarios/perfis/{idPerfil}/` |
| EP-36 | GET | `/api/funcionarios/perfis/{idPerfil}/dres/{codigoDre}/` |
| EP-37 | GET | `/api/perfis/servidores/{codigoRF}/VerificaSeProfessorTemAcessoAhSondagem/` |
| EP-38 | POST | `/api/funcionarios/BuscarPorListaRF/` |
| EP-39 | POST | `/api/funcionarios/BuscarPorListaLogin/` |

---

## Referências

- Contrato completo: `../swagger_contrato_microsservico.md`
- Projeto ETL de referência: `../SME-SGP-MS-ETL/`