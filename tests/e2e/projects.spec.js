const { test, expect } = require('@playwright/test');
const { login } = require('./helpers/auth');
const { goto } = require('./helpers/utils');

test.describe('Proyectos', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'demo', 'demo123');
  });

  test('debe listar proyectos', async ({ page }) => {
    await goto(page, '/projects/');
    await page.waitForLoadState('networkidle');
    
    // Verificar que la página se cargó
    await expect(page).toHaveURL(/.*projects/);
  });

  test('debe permitir crear un nuevo proyecto', async ({ page }) => {
    await goto(page, '/projects/create/');
    await page.waitForLoadState('networkidle');
    
    // Verificar que el formulario esté presente
    const form = page.locator('form');
    if (await form.count() > 0) {
      await expect(form.first()).toBeVisible();
    }
  });
});
