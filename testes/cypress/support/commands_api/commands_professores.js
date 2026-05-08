const getBaseUrl = () => {
  const apiUrl = Cypress.env('API_URL')
  const prefix = Cypress.env('APP_PREFIX')

  if (!apiUrl || !prefix) {
    throw new Error('API_URL ou APP_PREFIX não definidos')
  }

  return `${apiUrl}${prefix}`
}

Cypress.Commands.add('getProfessoresPorEscola', () => {
  const base = getBaseUrl()

  return cy.request({
    method: 'GET',
    url: `${base}/api/v1/professores/escolas/${Cypress.env('CODIGO_EOL_ESCOLA')}/professores/${Cypress.env('ANO_LETIVO')}/`,
    headers: {
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getTurmasPorEscola', () => {
  const base = getBaseUrl()

  return cy.request({
    method: 'GET',
    url: `${base}/api/v1/professores/escolas/${Cypress.env('CODIGO_EOL_ESCOLA')}/turmas/anos_letivos/${Cypress.env('ANO_LETIVO')}/`,
    headers: {
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('getProfessorPorRf', () => {
  const base = getBaseUrl()

  return cy.request({
    method: 'GET',
    url: `${base}/api/v1/professores/${Cypress.env('CODIGO_RF')}/`,
    headers: {
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('postBuscarListaRF', () => {
  const base = getBaseUrl()

  return cy.request({
    method: 'POST',
    url: `${base}/api/v1/professores/${Cypress.env('ANO_LETIVO')}/BuscarPorListaRF/`,
    headers: {
      [Cypress.env('API_KEY_HEADER')]: Cypress.env('API_KEY'),
    },
    body: ["7979533", "8145130", "6736548"],
    failOnStatusCode: false,
  })
})