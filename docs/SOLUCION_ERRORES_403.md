# Solución de Errores 403 (Forbidden)

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema

Al acceder al sistema sin autenticación, se producen errores 403 en múltiples endpoints:

- `/api/wizard/validate/` - 403
- `/api/users/me/` - 403
- `/api/wizard/analytics/` - 403
- `/api/wizard/sync/` - 403

---

## ✅ Solución Implementada

### 1. Verificación de Autenticación en JavaScript

Se agregó verificación de autenticación antes de inicializar el wizard:

```javascript
document.addEventListener("DOMContentLoaded", async () => {
  // Verificar si el usuario está autenticado antes de inicializar
  const wizardSection = document.querySelector(".wizard");
  if (!wizardSection) {
    // Usuario no autenticado, wizard no inicializado
    console.log("[Wizard] Usuario no autenticado, wizard no inicializado");
    return;
  }
  // ... resto del código
});
```

### 2. Manejo de Errores 403/401

Se agregó manejo centralizado de errores de autenticación en todas las llamadas API:

- **`getCurrentProfile()`**: Redirige al login si el usuario no está autenticado
- **`validateStep()`**: Verifica autenticación antes de validar
- **`syncSteps()`**: Maneja errores 403/401 y redirige al login
- **`SyncManager.syncRequest()`**: Maneja errores de autenticación

### 3. Formulario de Login Mejorado

Se mejoró el formulario de login para:
- Mostrar credenciales demo disponibles
- Redirigir correctamente después del login
- Usar la ruta actual como `next` parameter

---

## 🔐 Credenciales Demo

El formulario de login ahora muestra las credenciales demo disponibles:

- **Usuario**: `demo` / **Contraseña**: `demo123` (Técnico)
- **Usuario**: `pm` / **Contraseña**: `pm123` (Project Manager)
- **Usuario**: `supervisor` / **Contraseña**: `supervisor123` (Supervisor)
- **Usuario**: `admin` / **Contraseña**: `admin123` (Administrador)

---

## 📋 Pasos para Resolver

1. **Iniciar sesión**: Acceder a `http://localhost:8000/` y usar una de las credenciales demo
2. **Verificar autenticación**: Después del login, el sistema debería funcionar correctamente
3. **Si persisten errores**: Verificar que las cookies de sesión estén habilitadas en el navegador

---

## 🔧 Archivos Modificados

- `backend/static/frontend/js/wizard.js`: Verificación de autenticación y manejo de errores 403
- `backend/static/frontend/js/sync.js`: Manejo de errores de autenticación en sync
- `backend/static/frontend/js/analytics.js`: Manejo silencioso de errores 403 en analytics
- `backend/apps/frontend/templates/frontend/wizard.html`: Formulario de login mejorado con credenciales demo

---

## ✅ Verificación

Después de iniciar sesión, verificar que:

1. ✅ No aparezcan errores 403 en la consola
2. ✅ El wizard se inicialice correctamente
3. ✅ Las llamadas API funcionen sin errores
4. ✅ El sync funcione correctamente

---

**Última actualización**: 2026-01-18
