# Corrección de Errores 403 - Fase 5

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 🔍 Problema Identificado

El usuario `admin` con rol `admin_empresa` estaba recibiendo errores 403 en:
- `/api/wizard/validate/`
- `/api/wizard/sync/`
- `/api/wizard/analytics/`

Esto causaba:
- Bucles infinitos en `saveDraft()` que intentaba validar/sincronizar cada 30 segundos
- Mensajes de error repetitivos en consola
- Funcionalidad del wizard degradada

---

## ✅ Soluciones Implementadas

### 1. Verificación de Permisos en `saveDraft()`

**Archivo**: `backend/static/frontend/js/wizard.js`

Se agregó verificación de permisos antes de llamar a `validateStep()` y `syncSteps()`:

```javascript
// Verificar permisos antes de validar/sincronizar para evitar bucles infinitos
let canValidate = true;
let canSync = true;

if (window.RoleBasedUI) {
  try {
    const context = await window.RoleBasedUI.getUserContext();
    if (context && context.permissions) {
      canValidate = context.permissions["wizard.validate"] || false;
      canSync = context.permissions["wizard.sync"] || false;
    }
  } catch (e) {
    console.warn("[Wizard] Error obteniendo contexto para permisos:", e);
  }
}

// Solo validar/sincronizar si tiene permisos
if (canValidate) {
  try {
    await validateStep(step, payload);
  } catch (e) {
    console.warn("[Wizard] Error en validación:", e);
  }
} else {
  console.debug("[Wizard] Omitiendo validación: sin permisos");
}

if (canSync) {
  try {
    await syncSteps();
  } catch (e) {
    console.warn("[Wizard] Error en sincronización:", e);
    setSyncStatus("Error", payload.updatedAt);
  }
} else {
  console.debug("[Wizard] Omitiendo sincronización: sin permisos");
}
```

**Beneficios**:
- Evita bucles infinitos cuando el usuario no tiene permisos
- Reduce errores en consola
- Mejora la experiencia del usuario

### 2. Inclusión de Acciones del Wizard en Permisos

**Archivo**: `backend/apps/accounts/services.py`

Se agregaron las acciones del wizard a la lista de permisos por defecto:

```python
actions_to_check = [
    # ... otras acciones ...
    "wizard.save",
    "wizard.submit",
    "wizard.view",
    "wizard.validate",  # ✅ NUEVO
    "wizard.sync",      # ✅ NUEVO
    "wizard.analytics", # ✅ NUEVO
    # ... más acciones ...
]
```

**Beneficios**:
- El contexto del usuario ahora incluye permisos para estas acciones
- El frontend puede verificar permisos antes de hacer llamadas API
- Mejora la coherencia entre backend y frontend

### 3. Políticas ABAC Existentes

Las políticas `wizard.*` ya están configuradas en `seed_sitec.py` para todos los roles, incluyendo `admin_empresa`:

```python
{"action": "wizard.*", "conditions": {"role": "admin_empresa"}, "priority": 5}
```

Esto debería cubrir `wizard.validate`, `wizard.sync`, y `wizard.analytics` mediante el wildcard.

---

## 🔧 Verificaciones Necesarias

### 1. Verificar Rol del Usuario Admin

```bash
python manage.py shell
```

```python
from apps.accounts.models import UserProfile
from django.contrib.auth.models import User

admin_user = User.objects.get(username="admin")
profile = UserProfile.objects.filter(user=admin_user).first()
print(f"Rol: {profile.role if profile else 'Sin perfil'}")
print(f"Company: {profile.company if profile else 'Sin company'}")
```

### 2. Verificar Políticas ABAC

```python
from apps.accounts.models import AccessPolicy

# Verificar políticas para admin_empresa
policies = AccessPolicy.objects.filter(
    conditions__role="admin_empresa",
    action__startswith="wizard"
)
for p in policies:
    print(f"{p.action} - {p.conditions} - {p.effect} - {p.is_active}")
```

### 3. Verificar Permisos en Contexto del Usuario

```python
from apps.accounts.services import get_user_permissions
from django.test import RequestFactory
from django.contrib.auth.models import User

factory = RequestFactory()
admin_user = User.objects.get(username="admin")
request = factory.get("/")
request.user = admin_user

permissions = get_user_permissions(request, [
    "wizard.validate",
    "wizard.sync",
    "wizard.analytics"
])
print(permissions)
```

---

## 📋 Próximos Pasos

1. **Ejecutar seed_sitec** para asegurar que las políticas estén creadas:
   ```bash
   python manage.py seed_sitec
   ```

2. **Verificar que el usuario admin tenga el rol correcto**:
   - Si no tiene perfil, crearlo con rol `admin_empresa`
   - Si tiene perfil pero rol incorrecto, actualizarlo

3. **Probar el wizard**:
   - Iniciar sesión como admin
   - Abrir el wizard
   - Verificar que no aparezcan errores 403 en consola
   - Verificar que el autosave funcione sin bucles infinitos

---

## 🎯 Resultado Esperado

- ✅ No más errores 403 en consola
- ✅ No más bucles infinitos en `saveDraft()`
- ✅ Validación y sincronización funcionan correctamente para usuarios con permisos
- ✅ Usuarios sin permisos no intentan validar/sincronizar (evita errores)

---

**Última actualización**: 2026-01-23
