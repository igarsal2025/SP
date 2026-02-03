# Solución de Bucle Infinito - Error 403

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema

El sistema entraba en un bucle infinito cuando el usuario estaba autenticado pero no tenía permisos para acceder a ciertos endpoints:

1. Usuario autenticado accede a `/api/wizard/validate/`
2. El endpoint devuelve `403 Forbidden` (sin permisos)
3. El código JavaScript detecta el 403 y redirige a `/`
4. La página se recarga y vuelve a intentar validar
5. El ciclo se repite infinitamente

---

## ✅ Solución Implementada

### Cambio Principal: Diferenciar 401 vs 403

**Antes:**
- Cualquier error 403 o 401 → Redirigir a login

**Ahora:**
- **401 (Unauthorized)**: Usuario no autenticado → Redirigir a login
- **403 (Forbidden)**: Usuario autenticado pero sin permisos → NO redirigir, solo mostrar advertencia

### Archivos Modificados

#### `backend/static/frontend/js/wizard.js`

1. **`getCurrentProfile()`**:
```javascript
if (response.status === 401) {
  // Usuario no autenticado, redirigir al login
  console.warn("[Wizard] Sesión expirada, redirigiendo al login");
  window.location.href = "/";
  return null;
}
// 403 u otros errores: usuario autenticado pero sin permisos
// No redirigir para evitar bucles infinitos
```

2. **`validateStep()`**:
```javascript
if (response.status === 401) {
  // Usuario no autenticado, redirigir al login
  console.warn("[Wizard] Sesión expirada, redirigiendo al login");
  window.location.href = "/";
  return;
} else if (response.status === 403) {
  // Usuario autenticado pero sin permisos - no redirigir
  console.warn("[Wizard] Usuario no tiene permisos para validar");
  updateServerValidationStatus(false);
  return;
}
```

#### `backend/static/frontend/js/sync.js`

**`syncRequest()`**:
```javascript
if (response.status === 401) {
  // Usuario no autenticado, redirigir al login
  window.location.href = "/";
  throw new Error("Sesión expirada");
} else if (response.status === 403) {
  // Usuario autenticado pero sin permisos - no redirigir
  throw new Error("Sin permisos para sincronizar");
}
```

---

## 🔧 Verificación de Permisos

Si el usuario sigue recibiendo 403, verificar:

1. **Políticas ABAC**: Asegurarse de que existan políticas que permitan `wizard.validate`:
   ```python
   {"action": "wizard.*", "conditions": {"role": "tecnico"}, "priority": 5}
   ```

2. **Rol del usuario**: Verificar que el usuario tenga un rol válido:
   ```bash
   python manage.py shell
   >>> from apps.accounts.models import UserProfile
   >>> UserProfile.objects.filter(user__username="demo").values("role", "company__name")
   ```

3. **Políticas activas**: Verificar que las políticas estén activas:
   ```bash
   >>> from apps.accounts.models import AccessPolicy
   >>> AccessPolicy.objects.filter(action__startswith="wizard", is_active=True).values("action", "effect", "priority")
   ```

---

## 📋 Comportamiento Esperado

### Escenario 1: Usuario no autenticado (401)
- ✅ Redirige a `/` (página de login)
- ✅ Muestra formulario de login

### Escenario 2: Usuario autenticado sin permisos (403)
- ✅ NO redirige
- ✅ Muestra advertencia en consola
- ✅ Continúa funcionando con funcionalidades permitidas
- ✅ Omite la funcionalidad bloqueada

### Escenario 3: Usuario autenticado con permisos (200)
- ✅ Funciona normalmente
- ✅ Sin errores

---

## ⚠️ Notas Importantes

1. **No redirigir en 403**: Esto evita bucles infinitos cuando el usuario está autenticado pero no tiene permisos.

2. **Mensajes claros**: Los mensajes de consola ayudan a identificar el problema sin interrumpir la experiencia del usuario.

3. **Funcionalidad degradada**: Si el usuario no tiene permisos para validar, el wizard sigue funcionando pero sin validación del servidor.

---

## 🔄 Próximos Pasos

Si el problema persiste:

1. Verificar que las políticas ABAC estén correctamente configuradas
2. Ejecutar `python manage.py seed_sitec` para recrear las políticas
3. Verificar que el usuario tenga un `UserProfile` con rol válido
4. Revisar los logs del servidor para más detalles

---

**Última actualización**: 2026-01-18
