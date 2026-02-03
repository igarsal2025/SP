# Test Completo de Ingreso de Datos en el Wizard

## Descripción

Este documento describe el test E2E completo que prueba el ingreso de datos en múltiples pasos del wizard SITEC.

## Test Implementado

El test `debe completar el flujo completo ingresando datos en múltiples pasos` se encuentra en `tests/e2e/wizard.spec.js` y realiza lo siguiente:

### Pasos del Test

1. **Paso 1: Datos generales**
   - Ingresa nombre del proyecto: "Proyecto de Prueba E2E"
   - Código del proyecto: "TEST-E2E-2026"
   - Fecha de inicio: "2026-01-26"
   - Dirección del sitio: "Av. Principal 123, Col. Centro"
   - Ciudad: "Ciudad de México"
   - Estado: "CDMX"
   - Técnico: "Juan Pérez García"
   - Cliente: "Cliente de Prueba S.A."
   - Contacto: "contacto@cliente.com"
   - Notas iniciales: "Notas iniciales del proyecto de prueba E2E"

2. **Paso 2: Planificación y estado**
   - Porcentaje de progreso: 45%
   - Estado del cronograma: "on_time"
   - Fecha planificada de inicio: "2026-01-01"
   - Fecha planificada de fin: "2026-03-31"
   - Fecha real de inicio: "2026-01-05"
   - Resumen de riesgos: "Riesgos identificados: retrasos menores en materiales"

3. **Paso 3: Cableado y nodos**
   - Total de nodos de cableado: 150
   - Nodos OK: 142
   - Tipo de cable: "Cat6 UTP"
   - Longitud de cable (m): 2500
   - Bandejas de cable OK: true
   - Etiquetado OK: true

4. **Paso 4: Gabinetes y racks**
   - Racks instalados: 3
   - Orden de racks OK: true
   - Unidades de rack usadas: 42
   - Enfriamiento OK: true
   - Energía OK: true

5. **Paso 5: Seguridad y audiovisual**
   - Dispositivos de seguridad: 8
   - Cámaras en línea: true
   - Cantidad de cámaras: 6
   - Control de acceso: 2
   - Sistemas AV: 3
   - Notas de seguridad: "Sistemas de seguridad instalados y funcionando correctamente"

6. **Paso 6: Sistemas especializados**
   - Sistemas especializados habilitados: true
   - Tipo de sistema: "Sistema de control de acceso biométrico"
   - Proveedor: "VendorTech Solutions"
   - Integración OK: true
   - Notas: "Sistema integrado exitosamente con la infraestructura existente"

7. **Paso 7: Materiales y herramientas**
   - Cantidad de materiales: 25
   - Lista de materiales: "Cables Cat6, conectores RJ45, patch panels, switches, routers"
   - Herramientas usadas: "Crimpeadora, tester de red, taladro, destornilladores"
   - Materiales faltantes: false

8. **Paso 8: Pruebas y verificación**
   - Pruebas pasadas: true
   - QA firmado: true
   - Notas de prueba: "Todas las pruebas de conectividad pasaron exitosamente"

### Verificaciones

El test verifica:
- Que los datos se ingresen correctamente en cada campo
- Que los valores se guarden y persistan al navegar entre pasos
- Que la navegación hacia adelante y hacia atrás funcione correctamente
- Que los datos se mantengan al volver a pasos anteriores

## Ejecución del Test

### Prerrequisitos

1. El servidor Django debe estar ejecutándose
2. La base de datos debe estar configurada
3. Debe existir un usuario de prueba con credenciales:
   - Usuario: `demo`
   - Contraseña: `demo123`

### Comando para ejecutar el test

```bash
npm run test:e2e:wizard -- -g "debe completar el flujo completo ingresando datos en múltiples pasos"
```

### Ejecutar con interfaz gráfica

```bash
npm run test:e2e:ui
```

Luego seleccionar el test específico desde la interfaz.

### Ejecutar en modo debug

```bash
npm run test:e2e:debug -- -g "debe completar el flujo completo ingresando datos en múltiples pasos"
```

### Ejecutar con navegador visible

```bash
npm run test:e2e:headed -- -g "debe completar el flujo completo ingresando datos en múltiples pasos"
```

## Funciones Helper Utilizadas

El test utiliza las siguientes funciones helper de `tests/e2e/helpers/wizard.js`:

- `navigateToStep(page, step)`: Navega a un paso específico del wizard
- `waitForWizardReady(page)`: Espera a que el wizard se inicialice completamente
- `fillField(page, fieldName, value)`: Llena un campo de texto, número o fecha
- `fillTextarea(page, fieldName, value)`: Llena un campo de tipo textarea
- `fillSelect(page, fieldName, value)`: Selecciona una opción en un campo select
- `verifyFieldValue(page, fieldName, expectedValue)`: Verifica que un campo tenga un valor específico
- `clickNext(page)`: Hace clic en el botón "Siguiente"
- `clickPrev(page)`: Hace clic en el botón "Anterior"
- `getWizardMeta(page)`: Obtiene los metadatos del wizard (paso actual, total de pasos, etc.)

## Mejoras Implementadas

Se agregaron nuevas funciones helper para manejar diferentes tipos de campos:

1. **`fillTextarea`**: Maneja específicamente campos de tipo textarea
2. **`fillSelect`**: Maneja campos de tipo select con mejor soporte
3. **`fillField` mejorado**: Ahora detecta automáticamente el tipo de campo y lo llena apropiadamente

## Resultados Esperados

Al ejecutar el test exitosamente, deberías ver:

- ✓ Paso 1 completado
- ✓ Paso 2 completado
- ✓ Paso 3 completado
- ✓ Paso 4 completado
- ✓ Paso 5 completado
- ✓ Paso 6 completado
- ✓ Paso 7 completado
- ✓ Paso 8 completado
- ✓ Datos del paso 1 se mantuvieron correctamente
- === Prueba completa finalizada ===

## Troubleshooting

### Error: "El botón Siguiente está deshabilitado"

Esto puede ocurrir si hay validaciones que no se cumplen. Verifica que:
- Los campos requeridos estén llenos
- Los valores cumplan con las validaciones (regex, min/max, etc.)

### Error: "Campo no encontrado"

Asegúrate de que:
- El wizard se haya inicializado completamente (usa `waitForWizardReady`)
- El campo esté visible (puede estar oculto por condiciones `show_if`)

### Los datos no se guardan

Verifica que:
- El servidor esté ejecutándose
- La API `/api/wizard/steps/save/` esté funcionando
- No haya errores en la consola del navegador

## Notas

- El test incluye esperas (`waitForTimeout`) para dar tiempo a que los datos se guarden
- Los campos condicionales (con `show_if`) se verifican antes de llenarse
- El test navega hacia atrás al final para verificar la persistencia de datos
