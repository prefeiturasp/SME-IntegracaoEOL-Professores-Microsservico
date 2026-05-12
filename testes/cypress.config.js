import { defineConfig } from 'cypress'
import allureWriter from '@shelex/cypress-allure-plugin/writer.js'
import { cloudPlugin } from 'cypress-cloud/plugin'
import dotenv from 'dotenv'
import cucumber from 'cypress-cucumber-preprocessor'
import preprocessor from '@cypress/webpack-preprocessor'
import postgreSQL from 'cypress-postgresql'
import pg from 'pg'
import fs from 'fs'
import FormData from 'form-data'
import axios from 'axios'

dotenv.config()

const dbConfig = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
}

const envKeys = [
  'USUARIO_HOMOL_ADMIN',
  'USUARIO_HOMOL_EXTERNO',
  'SENHA_HOMOL',

  'API_KEY',
  'API_KEY_HEADER',
  'API_URL',
  'APP_PREFIX',

  'FUNCIONARIO_CODIGO',
  'TURMA_CODIGO',
  'TURMA_PAP_CODIGO',
  'LOGIN_FUNCIONARIO',
  'TURMA_SEM_ATRIBUICAO',

  'DATA_BASE',
  'ANO_LETIVO',
  'COMPONENTE_CURRICULAR',
  'UE_CODIGO',
  'MODALIDADE',
  'ANO_LETIVO_GRADE',
  'ANO_ESCOLAR',
  'UE_TURMAS_CODIGO',
  'CODIGO_RF',
  'CODIGO_EOL_ESCOLA',
  'DRE_ID',
  'CODIGO_TURMA',
  'DISCIPLINA_ID',
  'DATA_REFERENCIA',
  'DATA_TICKS',
  'CODIGO_CARGO',
  'CODIGO_FUNCAO_ATIVIDADE',
  'ID_PERFIL',
  'CPF_EXTERNO',
]

export default defineConfig({
  e2e: {
    watchForFileChanges: true,

    supportFile: 'cypress/support/e2e.js',

    viewportWidth: 1920,
    viewportHeight: 1080,
    video: false,

    retries: { runMode: 2, openMode: 0 },

    screenshotOnRunFailure: false,
    chromeWebSecurity: false,
    experimentalRunAllSpecs: true,
    failOnStatusCode: false,

    specPattern: ['cypress/e2e/**/*.feature'],

    defaultCommandTimeout: 60000,
    requestTimeout: 60000,
    execTimeout: 60000,
    pageLoadTimeout: 60000,

    env: {
      allure: true,
    },

    async setupNodeEvents(on, config) {

      // Allure
      allureWriter(on, config)
      config.env.allure = true

      // Cucumber + Webpack
      const webpackConfig = {
        module: {
          rules: [
            {
              test: /\.js$/,
              exclude: [/node_modules/],
              use: {
                loader: 'babel-loader',
                options: {
                  plugins: ['@babel/plugin-transform-modules-commonjs'],
                },
              },
            },
          ],
        },
      }

      on('file:preprocessor', preprocessor({ webpackOptions: webpackConfig }))
      on('file:preprocessor', cucumber.default())

      // Banco
      const pool = new pg.Pool(dbConfig)
      const dbTasks = postgreSQL.loadDBPlugin(pool)

      on('task', {
        ...dbTasks,

        async uploadFile({ method = 'POST', url, headers = {}, filePath }) {
          const form = new FormData()

          if (filePath && filePath.trim() !== '') {
            form.append('file', fs.createReadStream(filePath))
          }

          const response = await axios({
            method,
            url,
            headers: { ...headers, ...form.getHeaders() },
            data: form,
            maxBodyLength: Infinity,
            validateStatus: () => true,
          })

          return {
            status: response.status,
            body: response.data,
          }
        },
      })

      // ENV DINÂMICO
      const customVariable = Object.fromEntries(
        envKeys.map((key) => [key, process.env[key] ?? ''])
      )

      config.env = {
        ...config.env,
        ...customVariable,
        db: dbConfig,
      }

      // Segurança contra undefined (SEMPRE resolve seu erro)
      if (!config.env.API_URL) {
        throw new Error(' API_URL não definida no .env')
      }

      if (!config.env.APP_PREFIX) {
        throw new Error('APP_PREFIX não definido no .env')
      }

      return await cloudPlugin(on, config)
    },
  },
})