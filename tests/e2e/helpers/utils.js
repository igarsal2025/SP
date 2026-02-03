/**
 * Utilidades para pruebas E2E
 */

/**
 * Obtiene la URL base desde la configuración de Playwright
 * @param {import('@playwright/test').Page} page
 * @returns {string}
 */
function getBaseURL(page) {
  // Intentar obtener baseURL de diferentes formas
  const context = page.context();
  const baseURL = 
    context._options?.baseURL || 
    process.env.BASE_URL || 
    'http://localhost:8000';
  
  // Asegurar que no termine con /
  return baseURL.replace(/\/$/, '');
}

/**
 * Navega a una URL relativa usando baseURL
 * @param {import('@playwright/test').Page} page
 * @param {string} path - Ruta relativa (ej: '/', '/wizard/1/')
 * @param {object} options - Opciones para page.goto
 */
async function goto(page, path, options = {}) {
  const baseURL = getBaseURL(page);
  const url = path.startsWith('http') ? path : baseURL + path;
  return await page.goto(url, options);
}

module.exports = {
  getBaseURL,
  goto,
};
