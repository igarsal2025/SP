/**
 * Fixtures personalizados para Playwright
 */

const { test as base } = require('@playwright/test');
const { login } = require('./helpers/auth');

/**
 * Extender el test base con fixtures personalizados
 */
const test = base.extend({
  // Página autenticada
  authenticatedPage: async ({ page }, use) => {
    await login(page, 'demo', 'demo123');
    await use(page);
  },
  
  // Contexto con usuario específico
  userPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await login(page, 'demo', 'demo123');
    await use(page);
    await context.close();
  },
});

module.exports = { test };
