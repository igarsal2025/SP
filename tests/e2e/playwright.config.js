// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Configuración de Playwright para pruebas E2E
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './tests/e2e',
  
  // Tiempo máximo para una prueba (aumentado para tests largos)
  timeout: 300 * 1000, // 5 minutos
  
  // Tiempo de espera para expect
  expect: {
    timeout: 10000
  },
  
  // Ejecutar pruebas en paralelo
  fullyParallel: true,
  
  // Fallar el build si dejaste test.only en el código
  forbidOnly: !!process.env.CI,
  
  // Reintentar en CI si falla
  retries: process.env.CI ? 2 : 0,
  
  // Número de workers en CI, o indefinido localmente
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter a usar
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  
  // Configuración compartida para todos los proyectos
  use: {
    // URL base para usar en navegación
    baseURL: process.env.BASE_URL || 'http://localhost:8000',
    
    // Recopilar trace cuando se repite una prueba
    trace: 'on-first-retry',
    
    // Screenshots solo cuando falla
    screenshot: 'only-on-failure',
    
    // Videos solo cuando falla
    video: 'retain-on-failure',
    
    // Headless mode
    headless: process.env.CI ? true : false,
    
    // Viewport
    viewport: { width: 1280, height: 720 },
    
    // Ignorar HTTPS errors
    ignoreHTTPSErrors: true,
  },

  // Configurar proyectos para diferentes navegadores
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Servidor de desarrollo local
  webServer: {
    command: process.env.DJANGO_COMMAND || 'python manage.py runserver',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    cwd: './backend',
    env: {
      ...process.env,
    },
  },
});
