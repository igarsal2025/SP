# Solución de Permisos para Usuario Admin

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema

El usuario `admin` con rol `admin_empresa` está recibiendo errores 403 al intentar:
- Validar pasos del wizard (`/api/wizard/validate/`)
- Guardar preferencias (`/api/users/me/`)

A pesar de que:
- El usuario tiene rol `admin_empresa`
- El código debería permitir acceso completo a usuarios con rol `admin_empresa`
- Las políticas ABAC están configuradas correctamente

---

## ✅ Solución Implementada

### 1. Mejora en `evaluate_access_policy()`

Se mejoró la función para que retorne información más detallada cuando un usuario `admin_empresa` tiene acceso:

```python
if profile.role == "admin_empresa":
    return PolicyDecision(
        allowed=True,
        policy_action="admin_empresa",
        policy_effect="allow",
    )
```

### 2. Agregado `credentials: "include"` en fetch requests

Se agregó `credentials: "include"` en todas las llamadas fetch para asegurar que las cookies de sesión se envíen correctamente:

- `saveFieldModePreference()`: Ahora incluye `credentials: "include"`
- Mejor manejo de errores 401 vs 403

---

## 🔧 Cambios Realizados

### `backend/apps/accounts/services.py`

**Función `evaluate_access_policy()`**:
- Mejorado el retorno para usuarios `admin_empresa` con información de política
- Separación más clara de las validaciones

### `backend/static/frontend/js/wizard.js`

**Función `saveFieldModePreference()`**:
- Agregado `credentials: "include"` en la llamada fetch
- Mejor manejo de errores 401 vs 403

---

## 📋 Verificación

Para verificar que el usuario admin tiene acceso:

1. **Verificar perfil**:
```bash
python manage.py shell
>>> from apps.accounts.models import UserProfile
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.get(username="admin")
>>> profile = UserProfile.objects.get(user=admin)
>>> print(f"Rol: {profile.role}, Company: {profile.company.name}")
```

2. **Probar evaluación de políticas**:
```bash
>>> from apps.accounts.services import evaluate_access_policy
>>> from django.test import RequestFactory
>>> factory = RequestFactory()
>>> request = factory.post("/api/wizard/validate/")
>>> request.user = admin
>>> decision = evaluate_access_policy(request, "wizard.validate")
>>> print(f"Allowed: {decision.allowed}")
```

3. **Probar endpoint real**:
```bash
>>> from django.test import Client
>>> client = Client()
>>> client.force_login(admin)
>>> response = client.post("/api/wizard/validate/", {"step": 1, "data": {}}, content_type="application/json")
>>> print(f"Status: {response.status_code}")
```

---

## ⚠️ Posibles Causas del Problema

Si el problema persiste, verificar:

1. **Cookies de sesión**: Asegurarse de que las cookies se están enviando correctamente
2. **Autenticación**: Verificar que el usuario está realmente autenticado en el request
3. **Middleware**: Verificar que `CompanySitecMiddleware` está configurando correctamente `request.company` y `request.sitec`
4. **Cache del navegador**: Limpiar cache y recargar la página

---

## 🔄 Próximos Pasos

Si el problema persiste después de estos cambios:

1. **Verificar logs del servidor**: Revisar los logs para ver qué está causando el 403
2. **Verificar autenticación**: Asegurarse de que el usuario está autenticado correctamente
3. **Probar con otros usuarios**: Verificar si el problema es específico del usuario admin o afecta a todos

---

**Última actualización**: 2026-01-18
