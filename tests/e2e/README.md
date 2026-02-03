# Pruebas E2E con Playwright

Sistema de pruebas automatizadas end-to-end para SITEC usando Playwright.

## Instalación

```bash
# Instalar dependencias de Node.js
npm install

# Instalar navegadores de Playwright
npx playwright install
```

## Configuración

1. Asegúrate de que el servidor Django esté corriendo en `http://127.0.0.1:8000`
2. Ajusta las credenciales de prueba en los archivos de prueba si es necesario
3. Configura las variables de entorno si es necesario:
   ```bash
   export BASE_URL=http://127.0.0.1:8000
   export DJANGO_COMMAND="python manage.py runserver"
   ```

## Ejecutar pruebas

```bash
# Ejecutar todas las pruebas
npx playwright test

# Ejecutar pruebas específicas
npx playwright test wizard.spec.js
npx playwright test auth.spec.js

# Ejecutar en modo UI (interactivo)
npx playwright test --ui

# Ejecutar en modo debug
npx playwright test --debug

# Ejecutar con un navegador específico
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Ejecutar en modo headed (ver el navegador)
npx playwright test --headed

# Generar reporte HTML
npx playwright show-report
```

## Estructura de archivos

```
tests/e2e/
├── playwright.config.js      # Configuración de Playwright
├── helpers/
│   ├── auth.js              # Helpers para autenticación
│   └── wizard.js            # Helpers para el wizard
├── fixtures.js              # Fixtures personalizados
├── wizard.spec.js          # Pruebas del wizard
├── auth.spec.js            # Pruebas de autenticación
├── dashboard.spec.js       # Pruebas del dashboard
└── projects.spec.js        # Pruebas de proyectos
```

## Escribir nuevas pruebas

```javascript
const { test, expect } = require('@playwright/test');
const { login } = require('./helpers/auth');

test('mi nueva prueba', async ({ page }) => {
  await login(page, 'usuario', 'password');
  await page.goto('/mi-ruta/');
  
  await expect(page.locator('.mi-elemento')).toBeVisible();
});
```

## CI/CD

Las pruebas están configuradas para ejecutarse en CI con:
- Reintentos automáticos en caso de fallo
- Captura de screenshots y videos en fallos
- Reportes en formato JSON y HTML

## Troubleshooting

### Las pruebas fallan porque el servidor no está corriendo
- Asegúrate de que Django esté corriendo en el puerto 8000
- O configura `BASE_URL` en las variables de entorno

### Los scripts del wizard no se cargan
- Verifica que los archivos estáticos estén siendo servidos correctamente
- Aumenta el timeout en `waitForWizardReady` si es necesario

### Problemas con autenticación
- Verifica que las credenciales de prueba sean correctas
- Ajusta los selectores en `helpers/auth.js` si cambian
