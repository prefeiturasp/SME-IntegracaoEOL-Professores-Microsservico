import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

function getEnvOrFail(key) {
  const value = Cypress.env(key)

  expect(value, `Variável ${key} não definida`).to.exist
  expect(String(value).trim(), `${key} vazia`).to.not.be.empty

  return value
}

function logBody(body) {
  const serialized = JSON.stringify(body)
  const maxLength = 2000

  if (serialized && serialized.length > maxLength) {
    cy.log(`BODY (truncado, ${serialized.length} caracteres) => ${serialized.slice(0, maxLength)}...`)
    return
  }

  cy.log(`BODY => ${serialized}`)
}

// ======================================================
// PROFESSOR POR RF E ANO LETIVO
// ======================================================

Given('que possuo acesso à API de professores por RF', () => {

  getEnvOrFail('API_URL_NOVA')
  getEnvOrFail('API_KEY_NOVA')
  getEnvOrFail('CODIGO_RF')
  getEnvOrFail('ANO_LETIVO')

})

When('envio uma requisição GET para buscar professor por RF e ano letivo', () => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

  const codigoRf = getEnvOrFail('CODIGO_RF')
  const anoLetivo = getEnvOrFail('ANO_LETIVO')

  const endpoint =
    `${apiUrl}/api/professores/${codigoRf}/BuscarPorRf/${anoLetivo}/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    qs: {
      buscar_outros_cargos: false,
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    logBody(res.body)

  })

})

// ======================================================
// VALIDAR PROFESSOR POR RF
// ======================================================

Given('que possuo acesso à API de validação de professor', () => {

  getEnvOrFail('API_URL_NOVA')
  getEnvOrFail('API_KEY_NOVA')
  getEnvOrFail('CODIGO_RF')

})

When('envio uma requisição GET para validar professor por RF', () => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const codigoRf = getEnvOrFail('CODIGO_RF')

  const endpoint =
    `${apiUrl}/api/professores/${codigoRf}/validade/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    logBody(res.body)

  })

})

// ======================================================
// CONSULTAR NOME DO PROFESSOR POR RF
// ======================================================

Given('que possuo acesso à API de consulta de nome do professor', () => {

  getEnvOrFail('API_URL_NOVA')
  getEnvOrFail('API_KEY_NOVA')
  getEnvOrFail('CODIGO_RF')

})

When('envio uma requisição GET para consultar nome do professor por RF', () => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const codigoRf = getEnvOrFail('CODIGO_RF')

  const endpoint =
    `${apiUrl}/api/professores/${codigoRf}/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    logBody(res.body)

  })

})

// ======================================================
// THEN
// ======================================================

Then('a API deve responder com status 200', () => {

  expect(response, 'response não pode ser undefined').to.exist

  expect(response.status).to.eq(200)

})