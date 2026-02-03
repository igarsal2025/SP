# Debug de Permisos para Usuario Admin

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema Reportado

El usuario `admin` con rol `admin_empresa` está recibiendo errores 403 al intentar:
- Validar pasos del wizard (`/api/wizard/validate/`)
- Guardar preferencias (`/api/users/me/`)

**Mensajes en consola**:
- `[Wizard] Usuario no tiene permisos para validar, omitiendo validación del servidor`
- `[Wizard] No se pudo guardar preferencia de Modo Campo`

---

## ✅ Verificaciones Realizadas

### 1. Estado del Usuario Admin

```bash
Usuario: admin
Rol: admin_empresa
Company: SITEC
Perfil: Existe y está asociado a la company
```

### 2. Políticas ABAC

Las políticas están correctamente configuradas:
- `wizard.*` con `{"role": "admin_empresa"}` - `allow` - priority: 5
- Política global `*` con `allow` - priority: 0

### 3. Código de Evaluación

El código en `evaluate_access_policy()` debería permitir acceso completo a usuarios con rol `admin_empresa`:

```python
if profile.role == "admin_empresa":
    return PolicyDecision(allowed=True, ...)
```

### 4. Prueba con Cliente de Prueba

Cuando se usa `client.force_login(admin_user)`, el endpoint funciona correctamente:
- Status: 200
- Respuesta: JSON válido con validaciones

---

## 🔧 Cambios Implementados

### 1. Mejora en `evaluate_access_policy()`

Se mejoró la verificación de autenticación para manejar correctamente la propiedad `is_authenticated`:

```python
# Verificar si es una propiedad o método
is_authenticated = user.is_authenticated
if callable(is_authenticated):
    is_authenticated = is_authenticated()

if not is_authenticated:
    return PolicyDecision(allowed=False)
```

### 2. Agregado `credentials: "include"` en fetch requests

Se agregó `credentials: "include"` en `saveFieldModePreference()` para asegurar que las cookies de sesión se envíen.

---

## 🔍 Posibles Causas

Dado que la prueba con `client.force_login()` funciona, el problema probablemente está en:

1. **Cookies de sesión no se están enviando**: El navegador no está enviando las cookies de sesión correctamente
2. **Usuario no está autenticado en el request real**: Aunque el login fue exitoso, la sesión no se está manteniendo
3. **Problema con el middleware**: Algún middleware está interfiriendo con la autenticación

---

## 📋 Pasos para Debug

### 1. Verificar Autenticación en el Navegador

Abre DevTools (F12) y verifica:

1. **Cookies**:
   - Ve a la pestaña **Application** → **Cookies** → `http://localhost:8000`
   - Verifica que existan cookies `sessionid` y `csrftoken`

2. **Network**:
   - Ve a la pestaña **Network**
   - Busca una llamada a `/api/wizard/validate/`
   - Verifica que en **Request Headers** se incluya `Cookie: sessionid=...`

### 2. Verificar Respuesta del Login

Después de hacer login, verifica:
- ¿Se redirige correctamente?
- ¿Las cookies se establecen?
- ¿El usuario está autenticado?

### 3. Probar Endpoint Manualmente

```bash
# Obtener sessionid después del login
curl -c cookies.txt -b cookies.txt -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Probar endpoint con cookies
curl -b cookies.txt -X POST http://localhost:8000/api/wizard/validate/ \
  -H "Content-Type: application/json" \
  -d '{"step": 1, "data": {}}'
```

---

## 🔄 Soluciones Alternativas

Si el problema persiste:

1. **Verificar configuración de sesiones en settings.py**:
   - Asegurarse de que `SESSION_COOKIE_SECURE = False` en desarrollo
   - Verificar `SESSION_COOKIE_SAMESITE = 'Lax'`

2. **Verificar que el middleware de autenticación esté activo**:
   - `django.contrib.auth.middleware.AuthenticationMiddleware` debe estar en `MIDDLEWARE`

3. **Limpiar cookies y volver a iniciar sesión**:
   - Cerrar sesión
   - Limpiar todas las cookies del sitio
   - Volver a iniciar sesión

---

## 📝 Notas

- El código de evaluación de políticas está correcto
- El problema parece estar en la autenticación/sesión del navegador
- Las pruebas unitarias funcionan correctamente

---

**Última actualización**: 2026-01-18
