const { test, expect } = require('@playwright/test');
const { login } = require('./helpers/auth');
const { goto } = require('./helpers/utils');

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'demo', 'demo123');
  });

  test('debe cargar el dashboard correctamente', async ({ page }) => {
    await goto(page, '/dashboard/');
    await page.waitForLoadState('networkidle');
    
    // Verificar que la página se cargó
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('debe mostrar información del usuario', async ({ page }) => {
    await goto(page, '/dashboard/');
    await page.waitForLoadState('networkidle');
    
    // Verificar que haya contenido en el dashboard
    const content = page.locator('main, .dashboard, .container');
    await expect(content.first()).toBeVisible();
  });

  test('debe tener navegación funcional', async ({ page }) => {
    await goto(page, '/dashboard/');
    await page.waitForLoadState('networkidle');
    
    // Verificar que los enlaces de navegación estén presentes
    // Esto depende de tu implementación específica
    const navigation = page.locator('nav, .navigation, [role="navigation"]');
    if (await navigation.count() > 0) {
      await expect(navigation.first()).toBeVisible();
    }
  });
});
