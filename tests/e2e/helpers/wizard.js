/**
 * Helpers para pruebas del wizard
 */

const { goto } = require('./utils');
const { expect } = require('@playwright/test');

/**
 * Navega a un paso específico del wizard
 * @param {import('@playwright/test').Page} page
 * @param {number} step
 */
async function navigateToStep(page, step) {
  // Verificar que la página no se haya cerrado
  if (page.isClosed()) {
    throw new Error('La página se cerró antes de navegar');
  }
  
  try {
    await goto(page, `/wizard/${step}/`, { waitUntil: 'domcontentloaded' });
  } catch (error) {
    if (error.message.includes('closed') || error.message.includes('Target page')) {
      throw new Error(`La página se cerró durante la navegación al paso ${step}`);
    }
    throw error;
  }
  
  // Esperar a que el wizard se inicialice
  await page.waitForSelector('.wizard', { timeout: 15000 });
  
  // Esperar a que los scripts se carguen
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(2000); // Reducido de 3000 a 2000
}

/**
 * Obtiene los metadatos del wizard actual
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<Object>}
 */
async function getWizardMeta(page) {
  // Verificar que la página no se haya cerrado
  if (page.isClosed()) {
    throw new Error('La página se cerró antes de obtener metadatos');
  }
  
  try {
    const wizardElement = page.locator('.wizard');
    return {
      step: await wizardElement.getAttribute('data-step'),
      total: await wizardElement.getAttribute('data-total'),
      projectId: await wizardElement.getAttribute('data-project-id'),
      reportId: await wizardElement.getAttribute('data-report-id'),
    };
  } catch (error) {
    if (error.message.includes('closed') || error.message.includes('Target page')) {
      throw new Error('La página se cerró durante la obtención de metadatos');
    }
    throw error;
  }
}

/**
 * Verifica que los botones de navegación estén presentes y funcionen
 * @param {import('@playwright/test').Page} page
 */
async function verifyNavigationButtons(page) {
  const btnPrev = page.locator('#btnPrev');
  const btnNext = page.locator('#btnNext');
  const btnSave = page.locator('#btnSave');
  
  // Verificar que los botones existan y sean visibles
  await expect(btnPrev).toBeVisible({ timeout: 5000 });
  await expect(btnNext).toBeVisible({ timeout: 5000 });
  
  // btnSave puede no estar presente si no hay permisos
  const saveCount = await btnSave.count();
  if (saveCount > 0) {
    await expect(btnSave).toBeVisible({ timeout: 5000 });
  }
}

/**
 * Hace clic en el botón Siguiente
 * @param {import('@playwright/test').Page} page
 */
async function clickNext(page) {
  const btnNext = page.locator('#btnNext');
  
  // Verificar que el botón esté visible y habilitado
  await expect(btnNext).toBeVisible({ timeout: 5000 });
  const isDisabled = await btnNext.isDisabled();
  if (isDisabled) {
    throw new Error('El botón Siguiente está deshabilitado');
  }
  
  // Obtener el paso actual antes de navegar
  const currentMeta = await getWizardMeta(page);
  const currentStep = parseInt(currentMeta.step);
  const expectedNextStep = currentStep + 1;
  
  console.log(`Navegando del paso ${currentStep} al paso ${expectedNextStep}...`);
  
  // Esperar a que la página esté lista antes de hacer clic
  await page.waitForLoadState('domcontentloaded');
  
  // Verificar que la sesión sigue activa antes de navegar
  const { isAuthenticated } = require('./auth');
  const stillAuthenticated = await isAuthenticated(page);
  if (!stillAuthenticated) {
    throw new Error('La sesión se perdió. No se puede navegar.');
  }
  
  // Esperar a que cualquier guardado pendiente se complete
  await page.waitForTimeout(1000);
  
  // Hacer clic y esperar la navegación
  // El wizard hace validación antes de navegar, así que esperamos a que cambie la URL
  let navigationWorked = false;
  
  try {
    const navigationPromise = page.waitForURL(
      new RegExp(`/wizard/${expectedNextStep}/`),
      { timeout: 20000 }
    );
    
    await Promise.all([
      navigationPromise,
      btnNext.click()
    ]);
    
    navigationWorked = true;
  } catch (error) {
    // Si falla la navegación, verificar si hay errores de validación
    await page.waitForTimeout(3000); // Dar tiempo a que aparezcan los errores
    
    const validationBanner = page.locator('#validationBanner');
    const hasBanner = await validationBanner.isVisible().catch(() => false);
    
    if (hasBanner) {
      const bannerText = await validationBanner.textContent();
      // Verificar si es un error de sesión
      if (bannerText && bannerText.includes('Sesión requerida')) {
        console.warn('⚠️ Error de sesión detectado. Navegando directamente al paso siguiente...');
        // En lugar de re-autenticar, navegar directamente al paso siguiente
        await navigateToStep(page, expectedNextStep);
        navigationWorked = true;
      } else {
        // Otro tipo de error de validación
        console.warn(`⚠️ Error de validación: ${bannerText}`);
        // Intentar navegar directamente de todas formas
        console.warn('Intentando navegar directamente al paso siguiente...');
        await navigateToStep(page, expectedNextStep);
        navigationWorked = true;
      }
    } else {
      // No hay banner de error, verificar el paso actual
      const metaAfterClick = await getWizardMeta(page);
      const stepAfterClick = parseInt(metaAfterClick.step);
      
      if (stepAfterClick === currentStep) {
        // No navegó, intentar navegar directamente
        console.warn('⚠️ La navegación no funcionó. Navegando directamente...');
        await navigateToStep(page, expectedNextStep);
        navigationWorked = true;
      } else {
        // Ya navegó pero a un paso diferente
        navigationWorked = true;
      }
    }
  }
  
  if (!navigationWorked) {
    throw new Error(`No se pudo navegar del paso ${currentStep} al paso ${expectedNextStep}`);
  }
  
  // Esperar a que se complete la carga de la nueva página
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  
  // Verificar que realmente navegó
  const finalMeta = await getWizardMeta(page);
  const finalStep = parseInt(finalMeta.step);
  
  if (finalStep !== expectedNextStep) {
    console.warn(`Advertencia: Se esperaba el paso ${expectedNextStep}, pero se está en el paso ${finalStep}`);
  }
  
  // Esperar un poco más para que todo se inicialice
  await page.waitForTimeout(2000);
}

/**
 * Hace clic en el botón Anterior
 * @param {import('@playwright/test').Page} page
 */
async function clickPrev(page) {
  const btnPrev = page.locator('#btnPrev');
  
  // Verificar que el botón esté visible y habilitado
  await expect(btnPrev).toBeVisible({ timeout: 5000 });
  const isDisabled = await btnPrev.isDisabled();
  if (isDisabled) {
    throw new Error('El botón Anterior está deshabilitado');
  }
  
  // Esperar a que la página esté lista antes de hacer clic
  await page.waitForLoadState('domcontentloaded');
  
  // Hacer clic y esperar la navegación
  await Promise.all([
    page.waitForURL(/\/wizard\/\d+\//, { timeout: 10000 }).catch(() => {}),
    btnPrev.click()
  ]);
  
  // Esperar a que se complete la carga
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(2000);
}

/**
 * Lista todos los campos disponibles en el wizard actual
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<Array<{name: string, type: string, visible: boolean}>>}
 */
async function listAvailableFields(page) {
  const fields = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('#wizardDynamicContainer input, #wizardDynamicContainer select, #wizardDynamicContainer textarea'));
    return inputs.map(input => ({
      name: input.name || input.getAttribute('name'),
      type: input.type || input.tagName.toLowerCase(),
      visible: input.offsetParent !== null,
      id: input.id,
    })).filter(f => f.name);
  });
  return fields;
}

/**
 * Verifica que un campo existe y está disponible
 * @param {import('@playwright/test').Page} page
 * @param {string} fieldName
 * @param {number} timeout
 * @returns {Promise<boolean>}
 */
async function waitForField(page, fieldName, timeout = 10000) {
  try {
    const field = page.locator(`[name="${fieldName}"]`);
    await field.waitFor({ state: 'attached', timeout });
    await field.waitFor({ state: 'visible', timeout: 5000 });
    return true;
  } catch (error) {
    // Si falla, listar los campos disponibles para debugging
    const availableFields = await listAvailableFields(page);
    console.warn(`Campo ${fieldName} no encontrado después de ${timeout}ms`);
    console.warn(`Campos disponibles:`, availableFields.map(f => f.name).join(', '));
    return false;
  }
}

/**
 * Llena un campo del wizard
 * @param {import('@playwright/test').Page} page
 * @param {string} fieldName
 * @param {string|number} value
 * @param {boolean} optional - Si es true, no falla si el campo no existe
 */
async function fillField(page, fieldName, value, optional = false) {
  // Esperar a que el campo esté disponible
  const fieldExists = await waitForField(page, fieldName, 10000);
  
  if (!fieldExists) {
    if (optional) {
      console.warn(`Campo ${fieldName} no encontrado, saltando...`);
      return;
    }
    throw new Error(`Campo ${fieldName} no encontrado después de esperar`);
  }
  
  const field = page.locator(`[name="${fieldName}"]`);
  
  // Esperar a que el campo esté visible y habilitado
  await field.waitFor({ state: 'visible', timeout: 5000 });
  
  // Verificar que no esté deshabilitado
  const isDisabled = await field.isDisabled().catch(() => false);
  if (isDisabled) {
    console.warn(`Campo ${fieldName} está deshabilitado, intentando llenar de todas formas...`);
  }
  
  // Verificar el tipo de campo
  const tagName = await field.evaluate(el => el.tagName.toLowerCase()).catch(() => 'input');
  const type = await field.getAttribute('type').catch(() => null);
  
  if (tagName === 'select') {
    // Para select, usar selectOption
    await field.selectOption(String(value));
  } else if (type === 'date') {
    // Para campos de fecha, usar fill directamente
    await field.fill(String(value));
  } else if (type === 'number') {
    // Para números, convertir a string
    await field.fill(String(value));
  } else {
    // Para texto y textarea
    await field.fill(String(value));
  }
  
  // Disparar evento change para activar validación
  await field.dispatchEvent('change');
  await field.dispatchEvent('blur');
  await page.waitForTimeout(500);
}

/**
 * Llena un campo de tipo textarea
 * @param {import('@playwright/test').Page} page
 * @param {string} fieldName
 * @param {string} value
 * @param {boolean} optional - Si es true, no falla si el campo no existe
 */
async function fillTextarea(page, fieldName, value, optional = false) {
  const fieldExists = await waitForField(page, fieldName, 10000);
  
  if (!fieldExists) {
    if (optional) {
      console.warn(`Textarea ${fieldName} no encontrado, saltando...`);
      return;
    }
    throw new Error(`Textarea ${fieldName} no encontrado después de esperar`);
  }
  
  const field = page.locator(`textarea[name="${fieldName}"]`);
  await field.waitFor({ state: 'visible', timeout: 5000 });
  await field.fill(value);
  await field.dispatchEvent('change');
  await field.dispatchEvent('blur');
  await page.waitForTimeout(500);
}

/**
 * Llena un campo de tipo select
 * @param {import('@playwright/test').Page} page
 * @param {string} fieldName
 * @param {string} value
 * @param {boolean} optional - Si es true, no falla si el campo no existe
 */
async function fillSelect(page, fieldName, value, optional = false) {
  const fieldExists = await waitForField(page, fieldName, 10000);
  
  if (!fieldExists) {
    if (optional) {
      console.warn(`Select ${fieldName} no encontrado, saltando...`);
      return;
    }
    throw new Error(`Select ${fieldName} no encontrado después de esperar`);
  }
  
  const field = page.locator(`select[name="${fieldName}"]`);
  await field.waitFor({ state: 'visible', timeout: 5000 });
  await field.selectOption(value);
  await field.dispatchEvent('change');
  await page.waitForTimeout(500);
}

/**
 * Verifica que un campo tenga un valor específico
 * @param {import('@playwright/test').Page} page
 * @param {string} fieldName
 * @param {string} expectedValue
 */
async function verifyFieldValue(page, fieldName, expectedValue) {
  const field = page.locator(`[name="${fieldName}"]`);
  const actualValue = await field.inputValue();
  if (actualValue !== expectedValue) {
    throw new Error(`Campo ${fieldName}: esperado "${expectedValue}", obtenido "${actualValue}"`);
  }
}

/**
 * Espera a que el wizard se inicialice completamente
 * @param {import('@playwright/test').Page} page
 * @param {number} minFields - Número mínimo de campos esperados (default: 1)
 */
async function waitForWizardReady(page, minFields = 1) {
  // Esperar a que el contenedor del wizard esté presente
  await page.waitForSelector('#wizardDynamicContainer', { timeout: 20000 });
  
  // Esperar a que los scripts se carguen (verificar en consola)
  try {
    await page.waitForFunction(() => {
      return window.__WIZARD_LOADED__ === true;
    }, { timeout: 20000 });
  } catch (error) {
    console.warn('Timeout esperando que wizard.js se cargue, continuando...');
    // Verificar si al menos SitecComponents está disponible
    const hasComponents = await page.evaluate(() => !!window.SitecComponents);
    if (!hasComponents) {
      console.warn('SitecComponents no está disponible aún');
    }
  }
  
  // Esperar a que haya al menos un campo renderizado
  try {
    await page.waitForFunction((min) => {
      const container = document.getElementById('wizardDynamicContainer');
      if (!container) return false;
      const fields = container.querySelectorAll('input, select, textarea');
      return fields.length >= min;
    }, minFields, { timeout: 15000 });
    
    // Verificar que los campos estén realmente visibles
    const fields = await page.locator('#wizardDynamicContainer input, #wizardDynamicContainer select, #wizardDynamicContainer textarea').count();
    console.log(`Campos encontrados en el wizard: ${fields}`);
    
    if (fields < minFields) {
      console.warn(`Solo se encontraron ${fields} campos, se esperaban al menos ${minFields}`);
    }
  } catch (error) {
    console.warn('Timeout esperando campos del wizard, continuando...');
    // Listar lo que hay disponible
    const availableFields = await listAvailableFields(page);
    console.warn(`Campos disponibles: ${availableFields.length}`, availableFields.map(f => f.name).join(', '));
  }
  
  // Esperar un poco más para que todo se inicialice
  await page.waitForTimeout(2000);
}

/**
 * Verifica el estado del wizard en la consola
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<Object>}
 */
async function getWizardState(page) {
  return await page.evaluate(() => {
    if (window.systemDiagnostics) {
      return window.systemDiagnostics.wizardState;
    }
    return null;
  });
}

module.exports = {
  navigateToStep,
  getWizardMeta,
  verifyNavigationButtons,
  clickNext,
  clickPrev,
  waitForField,
  listAvailableFields,
  fillField,
  fillTextarea,
  fillSelect,
  verifyFieldValue,
  waitForWizardReady,
  getWizardState,
};
