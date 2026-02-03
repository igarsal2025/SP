# Guía Rápida - Pruebas E2E con Playwright

## Instalación Rápida

```bash
# 1. Instalar dependencias de Node.js
npm install

# 2. Instalar navegadores de Playwright
npm run test:e2e:install
# O directamente:
npx playwright install
```

## Comandos Principales

### Ejecutar todas las pruebas
```bash
npm run test:e2e
```

### Ejecutar pruebas específicas
```bash
# Solo pruebas del wizard
npm run test:e2e:wizard

# Solo pruebas de autenticación
npm run test:e2e:auth

# Prueba específica
npx playwright test wizard.spec.js
```

### Modos de ejecución

```bash
# Modo UI (interactivo)
npm run test:e2e:ui

# Modo debug (paso a paso)
npm run test:e2e:debug

# Modo headed (ver el navegador)
npm run test:e2e:headed
```

### Ver reportes
```bash
npm run test:e2e:report
```

## Usando Scripts

### Windows (PowerShell)
```powershell
.\scripts\run_e2e_tests.ps1
.\scripts\run_e2e_tests.ps1 -TestFile "wizard.spec.js"
.\scripts\run_e2e_tests.ps1 -UI
.\scripts\run_e2e_tests.ps1 -Debug
.\scripts\run_e2e_tests.ps1 -Headed
```

### Linux/Mac (Bash)
```bash
chmod +x scripts/run_e2e_tests.sh
./scripts/run_e2e_tests.sh
./scripts/run_e2e_tests.sh wizard.spec.js
./scripts/run_e2e_tests.sh --ui
```

## Estructura de Pruebas

### Helpers Disponibles

#### Autenticación (`helpers/auth.js`)
- `login(page, username, password, otpToken?)` - Hacer login
- `logout(page)` - Hacer logout
- `isAuthenticated(page)` - Verificar si está autenticado
- `getUserContext(page)` - Obtener contexto del usuario
- `createAuthenticatedContext(context, username, password)` - Crear contexto autenticado

#### Wizard (`helpers/wizard.js`)
- `navigateToStep(page, step)` - Navegar a un paso
- `getWizardMeta(page)` - Obtener metadatos del wizard
- `verifyNavigationButtons(page)` - Verificar botones
- `clickNext(page)` - Clic en Siguiente
- `clickPrev(page)` - Clic en Anterior
- `fillField(page, fieldName, value)` - Llenar campo
- `verifyFieldValue(page, fieldName, expectedValue)` - Verificar valor
- `waitForWizardReady(page)` - Esperar inicialización

## Ejemplo de Prueba

```javascript
const { test, expect } = require('@playwright/test');
const { login } = require('./helpers/auth');
const { navigateToStep, clickNext } = require('./helpers/wizard');

test('mi prueba personalizada', async ({ page }) => {
  // Login
  await login(page, 'demo', 'demo123');
  
  // Navegar al wizard paso 1
  await navigateToStep(page, 1);
  
  // Verificar que esté en el paso correcto
  const meta = await getWizardMeta(page);
  expect(meta.step).toBe('1');
  
  // Avanzar al siguiente paso
  await clickNext(page);
  
  // Verificar navegación
  const newMeta = await getWizardMeta(page);
  expect(newMeta.step).toBe('2');
});
```

## Configuración

### Variables de Entorno

```bash
# URL base del servidor
export BASE_URL=http://127.0.0.1:8000

# Comando para iniciar Django
export DJANGO_COMMAND="python manage.py runserver"
```

### Credenciales de Prueba

Edita los archivos de prueba para usar tus credenciales:
- `wizard.spec.js`
- `auth.spec.js`
- `dashboard.spec.js`
- `projects.spec.js`

Busca `TEST_USER` y ajusta según tu configuración.

## Troubleshooting

### Error: "Servidor no responde"
- Asegúrate de que Django esté corriendo: `cd backend && python manage.py runserver`
- Verifica que esté en el puerto 8000

### Error: "Navegadores no instalados"
```bash
npx playwright install
```

### Error: "Scripts del wizard no se cargan"
- Aumenta el timeout en `waitForWizardReady`
- Verifica que los archivos estáticos se estén sirviendo

### Las pruebas son lentas
- Ejecuta solo las pruebas necesarias
- Usa `--project=chromium` para un solo navegador
- Reduce el número de workers: `--workers=1`

## Recursos

- [Documentación de Playwright](https://playwright.dev)
- [API de Playwright](https://playwright.dev/docs/api/class-playwright)
- [Mejores Prácticas](https://playwright.dev/docs/best-practices)
