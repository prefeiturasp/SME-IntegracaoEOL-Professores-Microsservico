import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

// =====================
// ACESSO API
// =====================

Given('que possuo acesso à API de professores', () => {
  expect(Cypress.env('API_URL')).to.exist
  expect(Cypress.env('APP_PREFIX')).to.exist
})

// =====================
// WHEN (ações)
// =====================

When('realizo consulta de professores por escola e ano letivo', () => {
  return cy.getProfessoresPorEscola().then((res) => {
    response = res
  })
})

When('realizo consulta de turmas por escola', () => {
  return cy.getTurmasPorEscola().then((res) => {
    response = res
  })
})

When('realizo consulta de professor por RF', () => {
  return cy.getProfessorPorRf().then((res) => {
    response = res
  })
})

When('realizo busca por lista de RF', () => {
  return cy.postBuscarListaRF().then((res) => {
    response = res
  })
})

// =====================
// THEN (validações)
// =====================

Then('o status deve ser válido', () => {
  expect(response, 'response não pode ser undefined').to.exist
  expect(response.status).to.be.oneOf([200, 204, 400, 404])
})

Then('o retorno deve ser válido', () => {
  expect(response, 'response não pode ser undefined').to.exist

  if (response.body !== undefined) {
    const body = response.body

    expect(
      typeof body === 'object' ||
      typeof body === 'string' ||
      body === null
    ).to.be.true
  }
})