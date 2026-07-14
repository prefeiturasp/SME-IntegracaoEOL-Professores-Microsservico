import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

function getEnvOrFail(key) {
  const value = Cypress.env(key)

  expect(value, `Variável ${key} não definida`).to.exist
  expect(String(value).trim(), `${key} vazia`).to.not.be.empty

  return value
}

Given('que possuo acesso à API de funcionários', () => {

  getEnvOrFail('API_URL_NOVA')
  getEnvOrFail('API_KEY_NOVA')

})

// ======================================================
// TURMAS ATRIBUÍDAS DA UE
// ======================================================

When('envio uma requisição POST para buscar turmas atribuídas da UE {string}', (codigoUe) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

// ======================================================
// BUSCAR TURMAS ELEGÍVEIS
// ======================================================

When('envio uma requisição POST para buscar turmas elegíveis do RF {string} turma {int} componente {int}', (codigoRf, codigoTurma, componenteCurricular) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

  const endpoint = `${apiUrl}/api/funcionarios/BuscarTurmasElegiveis/`

  cy.log(`Endpoint => ${endpoint}`)

  return cy.request({
    method: 'POST',
    url: endpoint,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    body: {
      CodigoRf: codigoRf,
      CodigoTurma: codigoTurma,
      ComponenteCurricular: componenteCurricular,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

// ======================================================
// FUNCIONÁRIOS POR RF, UE E NOME
// ======================================================

When('envio uma requisição POST para buscar funcionário RF {string} UE {string} nome {string}', (codigoRf, codigoUe, nomeServidor) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

// ======================================================
// DISCIPLINAS DA TURMA
// ======================================================

When('envio uma requisição GET para buscar disciplinas da turma {int}', (turmaCodigo) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

// ======================================================
// SWITCH ABRANGÊNCIA DE TURMAS
// ======================================================

When('envio uma requisição GET para buscar turmas com abrangência UE do RF {string} perfil {string}', (login, perfil) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

When('envio uma requisição GET para buscar turmas com abrangência UE Turmas Disciplinas do RF {string} perfil {string}', (login, perfil) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

When('envio uma requisição GET para buscar turmas com abrangência DRE do RF {string} perfil {string}', (login, perfil) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
      dreCodigo: '108600',
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

When('envio uma requisição GET para buscar turmas com abrangência DRE Escolas Atribuídas do RF {string} perfil {string}', (login, perfil) => {

  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

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
      dreCodigo: '108600',
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {

    response = res

    cy.log(`STATUS => ${res.status}`)
    cy.log(`BODY => ${JSON.stringify(res.body)}`)

  })

})

// ======================================================
// THEN
// ======================================================

Then('a API de funcionários deve responder com status 200', () => {

  expect(response, 'response não pode ser undefined').to.exist

  expect(response.status).to.eq(200)

})

Then('a API de funcionários deve responder com status 200 ou 204', () => {

  expect(response, 'response não pode ser undefined').to.exist

  expect([200, 204]).to.include(response.status)

})
