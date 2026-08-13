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

Given('que possuo acesso à API de funcionários', () => {

  getEnvOrFail('API_URL_NOVA')
  getEnvOrFail('API_KEY_NOVA')

})

// ======================================================
// TURMAS ATRIBUÍDAS DA UE
// ======================================================

When('envio uma requisição POST para buscar turmas atribuídas da UE definida em {string}', (envKey) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const codigoUe = getEnvOrFail(envKey)

  const endpoint = `${apiUrl}/api/funcionarios/turmas/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'POST',
    url: endpoint,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    body: [codigoUe],
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    logBody(res.body)

  })

})

// ======================================================
// FUNCIONÁRIOS POR RF, UE E NOME
// ======================================================

When('envio uma requisição POST para buscar funcionário definido em {string}', (prefix) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const codigoRf = getEnvOrFail(`${prefix}_RF`)
  const codigoUe = getEnvOrFail(`${prefix}_UE`)
  const nomeServidor = getEnvOrFail(`${prefix}_NOME`)

  const endpoint = `${apiUrl}/api/funcionarios/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'POST',
    url: endpoint,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    body: {
      CodigoRF: codigoRf,
      CodigoUE: codigoUe,
      NomeServidor: nomeServidor,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    logBody(res.body)

  })

})

// ======================================================
// DISCIPLINAS DA TURMA
// ======================================================

When('envio uma requisição GET para buscar disciplinas da turma definida em {string}', (envKey) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const turmaCodigo = getEnvOrFail(envKey)

  const endpoint = `${apiUrl}/api/funcionarios/turmas/${turmaCodigo}/disciplinas/`

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
// SWITCH ABRANGÊNCIA DE TURMAS
// ======================================================

When('envio uma requisição GET para buscar turmas com abrangência UE definida em {string}', (prefix) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const login = getEnvOrFail(`${prefix}_LOGIN`)
  const perfil = getEnvOrFail(`${prefix}_PERFIL`)

  const endpoint = `${apiUrl}/api/funcionarios/${login}/perfis/${perfil}/turmas/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    qs: {
      abrangencia: 1,
      grupo: 12,
      ehPerfilManual: false,
      cargos: [3360],
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

When('envio uma requisição GET para buscar turmas com abrangência UE Turmas Disciplinas definida em {string}', (prefix) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const login = getEnvOrFail(`${prefix}_LOGIN`)
  const perfil = getEnvOrFail(`${prefix}_PERFIL`)

  const endpoint = `${apiUrl}/api/funcionarios/${login}/perfis/${perfil}/turmas/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    qs: {
      abrangencia: 3,
      grupo: 57,
      ehPerfilManual: false,
      cargos: [
        3131, 3212, 3213, 3220, 3239, 3247, 3255, 3263, 3271, 3280,
        3298, 3301, 3310, 3336, 3344, 3395, 3425, 3433, 3450, 3816,
        3840, 3859, 3867, 3874, 3875, 3877, 3880, 3883, 3884,
      ],
      funcoesId: [1045, 1050],
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

When('envio uma requisição GET para buscar turmas com abrangência DRE definida em {string}', (prefix) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const login = getEnvOrFail(`${prefix}_LOGIN`)
  const perfil = getEnvOrFail(`${prefix}_PERFIL`)
  const dreCodigo = getEnvOrFail(`${prefix}_CODIGO`)

  const endpoint = `${apiUrl}/api/funcionarios/${login}/perfis/${perfil}/turmas/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    qs: {
      abrangencia: 4,
      grupo: 21,
      ehPerfilManual: false,
      cargos: [434, 3351],
      dreCodigo,
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

When('envio uma requisição GET para buscar turmas com abrangência DRE Escolas Atribuídas definida em {string}', (prefix) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')
  const login = getEnvOrFail(`${prefix}_LOGIN`)
  const perfil = getEnvOrFail(`${prefix}_PERFIL`)
  const dreCodigo = getEnvOrFail(`${prefix}_CODIGO`)

  const endpoint = `${apiUrl}/api/funcionarios/${login}/perfis/${perfil}/turmas/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'GET',
    url: endpoint,
    qs: {
      abrangencia: 5,
      grupo: 20,
      ehPerfilManual: false,
      cargos: [3352],
      dreCodigo,
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
// THEN
// ======================================================

Then('a API de funcionários deve responder com status 200', () => {

  expect(response, 'response não pode ser undefined').to.exist

  expect(response.status).to.eq(200)

})
