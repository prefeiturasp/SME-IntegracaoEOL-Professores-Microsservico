"""Dados mock compartilhados pelos endpoints do microsservico de Professores."""

PROFESSOR_MOCK = {
    "codigoRf": "7654321",
    "nome": "Maria Silva",
    "cpf": "123.456.789-00",
}

PROFESSOR_EXTERNO_MOCK = {
    "cpf": "987.654.321-00",
    "nome": "João Souza",
    "codigoUe": "000532",
    "codigoTipoFuncao": 10,
}

TURMA_MOCK = {
    "codigoTurma": 2112345,
    "nomeTurma": "1A - Manhã",
    "codigoEscola": "000532",
    "anoLetivo": 2024,
    "status": "A",
}

ESCOLA_MOCK = {
    "codigoEscola": "000532",
    "nomeEscola": "EMEF EXEMPLO",
    "siglaEscola": "EMEF EX",
    "codigoDre": "108100",
    "nomeDre": "DRE EXEMPLO",
    "siglaDre": "DRE-EX",
}

ATRIBUICAO_MOCK = {
    "codigoTurma": 2112345,
    "nomeTurma": "1A - Manhã",
    "codigoEscola": "000532",
    "dataInicioAtribuicao": "2024-02-01",
    "dataFimAtribuicao": "2024-12-20",
    "codigoComponenteCurricular": 138,
    "codigoGrade": 2070,
    "codigoSerieGrade": 41005,
    "anoAtribuicao": 2024,
}

ERRO_PADRAO = {
    "type": "https://tools.ietf.org/html/rfc7807",
    "title": "Recurso não encontrado",
    "status": 404,
    "detail": "O recurso solicitado não foi encontrado.",
    "instance": "/api/professores/mock",
}

ERRO_400 = {
    "type": "https://tools.ietf.org/html/rfc7807",
    "title": "Requisição inválida",
    "status": 400,
    "detail": "Parâmetros inválidos ou ausentes.",
    "instance": "/api/professores/mock",
}
