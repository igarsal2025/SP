/**
 * Helpers para autenticación en pruebas E2E
 */

const { goto } = require('./utils');

/**
 * Realiza login con credenciales
 * @param {import('@playwright/test').Page} page
 * @param {string} username
 * @param {string} password
 * @param {string} [otpToken] - Token OTP opcional para MFA
 */
async function login(page, username, password, otpToken = null) {
  // Navegar a la página de inicio (redirige al login si no está autenticado)
  await goto(page, '/', { waitUntil: 'domcontentloaded' });
  
  // Esperar a que aparezca el formulario de login (puede estar en la página de inicio)
  try {
    await page.waitForSelector('#loginUsername, .wizard', { timeout: 15000 });
  } catch (error) {
    // Si no aparece el login, puede que ya esté autenticado
    const wizard = page.locator('.wizard');
    if (await wizard.isVisible()) {
      return; // Ya está autenticado
    }
    throw error;
  }
  
  // Verificar si ya está autenticado (wizard visible)
  const wizard = page.locator('.wizard');
  if (await wizard.isVisible({ timeout: 1000 }).catch(() => false)) {
    return; // Ya está autenticado
  }
  
  // Esperar específicamente al formulario de login
  await page.waitForSelector('#loginUsername', { timeout: 10000 });
  
  // Llenar credenciales
  await page.fill('#loginUsername', username);
  await page.fill('#loginPassword', password);
  
  // Si hay token OTP, llenarlo
  if (otpToken) {
    const otpField = page.locator('#loginOTPToken');
    if (await otpField.isVisible({ timeout: 2000 }).catch(() => false)) {
      await otpField.fill(otpToken);
    }
  }
  
  // Esperar a que el botón esté habilitado
  await page.waitForSelector('#loginSubmit', { state: 'visible' });
  
  // Enviar formulario y esperar la respuesta
  const [response] = await Promise.all([
    page.waitForResponse(response => 
      response.url().includes('/api/auth/login/'), 
      { timeout: 15000 }
    ).catch(() => null),
    page.click('#loginSubmit')
  ]);
  
  // Esperar a que se complete el login
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(3000);
  
  // Verificar si hay error
  const errorElement = page.locator('#loginError');
  if (await errorElement.isVisible({ timeout: 2000 }).catch(() => false)) {
    const errorText = await errorElement.textContent();
    if (errorText && errorText.trim()) {
      throw new Error(`Error de login: ${errorText}`);
    }
  }
  
  // Verificar respuesta del servidor
  if (response && response.status() >= 400) {
    throw new Error(`Error de login: ${response.status()}`);
  }
  
  // Verificar que el login fue exitoso (wizard visible o redirección)
  try {
    await page.waitForSelector('.wizard, #wizardDynamicContainer, .dashboard', { timeout: 15000 });
  } catch (error) {
    // Si no aparece, verificar la URL y cookies
    const url = page.url();
    const cookies = await page.context().cookies();
    const hasSession = cookies.some(c => c.name.includes('session') || c.name.includes('csrftoken'));
    
    if (!hasSession && !url.includes('/wizard') && !url.includes('/dashboard')) {
      throw new Error('Login no completado - no se redirigió correctamente y no hay cookies de sesión');
    }
  }
}

/**
 * Realiza logout
 * @param {import('@playwright/test').Page} page
 */
async function logout(page) {
  // Buscar botón de logout o navegar a logout endpoint
  try {
    await goto(page, '/api/auth/logout/');
    await page.waitForLoadState('networkidle');
  } catch (error) {
    console.warn('Error al hacer logout:', error);
  }
}

/**
 * Verifica si el usuario está autenticado
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<boolean>}
 */
async function isAuthenticated(page) {
  try {
    const { getBaseURL } = require('./utils');
    const baseURL = getBaseURL(page);
    const url = `${baseURL}/api/users/me/`;
    const response = await page.request.get(url, {
      timeout: 5000,
    });
    return response.ok() && response.status() === 200;
  } catch (error) {
    // Si falla, verificar si hay cookies de sesión
    const cookies = await page.context().cookies();
    const hasSessionCookie = cookies.some(c => c.name.includes('session') || c.name.includes('csrftoken'));
    return hasSessionCookie;
  }
}

/**
 * Obtiene el contexto del usuario actual
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<Object>}
 */
async function getUserContext(page) {
  const { getBaseURL } = require('./utils');
  const baseURL = getBaseURL(page);
  const url = `${baseURL}/api/user/context/`;
  const response = await page.request.get(url, {
    timeout: 10000,
  });
  if (!response.ok()) {
    throw new Error(`Error obteniendo contexto: ${response.status()}`);
  }
  return await response.json();
}

/**
 * Crea un contexto de autenticación reutilizable
 * @param {import('@playwright/test').BrowserContext} context
 * @param {string} username
 * @param {string} password
 * @param {string} [otpToken]
 * @returns {Promise<import('@playwright/test').Page>}
 */
async function createAuthenticatedContext(context, username, password, otpToken = null) {
  const page = await context.newPage();
  await login(page, username, password, otpToken);
  return page;
}

module.exports = {
  login,
  logout,
  isAuthenticated,
  getUserContext,
  createAuthenticatedContext,
};
