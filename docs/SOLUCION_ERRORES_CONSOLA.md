# Solución de Errores en Consola

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problemas Identificados

### 1. Error 403 en `/api/wizard/validate/`
**Causa**: La validación se ejecutaba antes de verificar la autenticación del usuario.

**Solución**: Se agregó verificación de autenticación antes de llamar a `validateStep()`.

---

### 2. Violación de Geolocalización
**Causa**: Se solicitaba geolocalización automáticamente sin un gesto del usuario, violando las políticas del navegador.

**Solución**: 
- Se deshabilitó la solicitud automática de geolocalización
- La función `shouldEnableFieldModeByLocation()` ahora retorna `false` por defecto
- La geolocalización solo se solicitará cuando el usuario interactúe explícitamente

---

### 3. ERR_BLOCKED_BY_CLIENT en Performance Metrics
**Causa**: Ad blockers o extensiones del navegador bloquean las solicitudes a `/api/wizard/performance/metrics/`.

**Solución**: 
- Se agregó manejo silencioso de errores de bloqueo
- Los errores de bloqueo por cliente se ignoran sin mostrar warnings
- Solo se muestran warnings para errores reales de red

---

### 4. Banner PWA no mostrado
**Causa**: Se llama a `preventDefault()` en el evento `beforeinstallprompt` pero no siempre se muestra el prompt.

**Solución**: 
- Se mejoró el manejo del prompt de instalación
- Se verifica que `deferredPrompt` exista antes de llamar a `prompt()`
- El warning es solo informativo y no afecta la funcionalidad

---

## ✅ Cambios Implementados

### `backend/static/frontend/js/wizard.js`

1. **Verificación de autenticación en `validateStep()`**:
```javascript
async function validateStep(step, payload) {
  // Verificar autenticación antes de validar
  const profile = await getCurrentProfile();
  if (!profile) {
    console.warn("[Wizard] Usuario no autenticado, omitiendo validación");
    return;
  }
  // ... resto del código
}
```

2. **Deshabilitación de geolocalización automática**:
```javascript
function shouldEnableFieldModeByLocation() {
  // No solicitar geolocalización automáticamente (requiere gesto del usuario)
  return Promise.resolve(false);
}
```

3. **Verificación de autenticación antes de validar en inicialización**:
```javascript
getCurrentProfile().then((profile) => {
  if (!profile) {
    console.warn("[Wizard] Usuario no autenticado, omitiendo validación inicial");
    return;
  }
  // ... validación
});
```

### `backend/static/frontend/js/performance.js`

**Manejo silencioso de errores de bloqueo**:
```javascript
try {
  const sent = navigator.sendBeacon("/api/wizard/performance/metrics/", blob);
  if (sent) {
    this.sent = true;
    return;
  }
} catch (error) {
  // Ignorar errores de bloqueo por cliente (ad blockers)
  if (!silent && error.name !== "NetworkError") {
    console.warn("[Performance] Error enviando métricas:", error);
  }
}
```

### `backend/static/frontend/js/pwa.js`

**Mejora del manejo del prompt de instalación**:
```javascript
if (deferredPrompt) {
  deferredPrompt.prompt();
  // ... manejo de respuesta
}
```

---

## 📋 Verificación

Después de estos cambios, verificar que:

1. ✅ No aparezcan errores 403 en la consola (después de iniciar sesión)
2. ✅ No aparezcan violaciones de geolocalización
3. ✅ Los errores de bloqueo por cliente se manejen silenciosamente
4. ✅ El wizard funcione correctamente después del login

---

## 🔧 Notas Adicionales

- **Geolocalización**: Si se necesita usar geolocalización en el futuro, debe solicitarse solo después de un gesto del usuario (click, touch, etc.)
- **Performance Metrics**: Los errores de bloqueo son normales cuando hay ad blockers y no afectan la funcionalidad
- **PWA Banner**: El warning es informativo y no afecta la funcionalidad de la PWA

---

**Última actualización**: 2026-01-18
