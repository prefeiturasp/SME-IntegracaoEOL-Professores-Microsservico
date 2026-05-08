import '@shelex/cypress-allure-plugin'

// Seus comandos
import './commands_api/commands_professores'

// Evita quebra de teste
Cypress.on('uncaught:exception', () => false)