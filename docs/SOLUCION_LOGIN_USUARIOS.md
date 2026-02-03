# Solución de Login para Todos los Usuarios

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema

Solo el usuario `demo` podía iniciar sesión. Los otros usuarios (`pm`, `supervisor`, `admin`) no podían iniciar sesión.

**Causa**: El formulario de login estaba usando `/admin/login/` que es el login del admin de Django, y Django admin solo permite que usuarios con `is_staff=True` inicien sesión. Solo el usuario `demo` tenía `is_staff=True`.

---

## ✅ Solución Implementada

### 1. Endpoint de Login Personalizado

Se creó un nuevo endpoint `/api/auth/login/` que:
- ✅ No requiere `is_staff=True` para iniciar sesión
- ✅ Funciona con formularios HTML y requests JSON
- ✅ Redirige correctamente después del login
- ✅ Valida credenciales correctamente

**Archivo**: `backend/apps/accounts/views_auth.py`

### 2. Actualización del Formulario de Login

El formulario ahora usa el nuevo endpoint:
```html
<form method="post" action="/api/auth/login/?next={{ request.path }}">
```

**Archivo**: `backend/apps/frontend/templates/frontend/wizard.html`

### 3. Actualización del Comando create_demo_users

El comando ahora establece `is_staff=True` para todos los usuarios demo:
```python
user.is_staff = True  # Asegurar que todos los usuarios demo puedan iniciar sesión
user.is_active = True
```

**Archivo**: `backend/apps/companies/management/commands/create_demo_users.py`

---

## 🔧 Cambios Realizados

### Nuevos Archivos

1. **`backend/apps/accounts/views_auth.py`**:
   - `LoginView`: Endpoint de login personalizado
   - `LogoutView`: Endpoint de logout personalizado

### Archivos Modificados

1. **`backend/config/urls.py`**:
   - Agregado `path("api/auth/login/", LoginView.as_view(), name="login")`
   - Agregado `path("api/auth/logout/", LogoutView.as_view(), name="logout")`

2. **`backend/apps/frontend/templates/frontend/wizard.html`**:
   - Cambiado `action="/admin/login/?next={{ request.path }}"` a `action="/api/auth/login/?next={{ request.path }}"`

3. **`backend/apps/companies/management/commands/create_demo_users.py`**:
   - Agregado `is_staff=True` al crear/actualizar usuarios

---

## 📋 Uso

### Iniciar Sesión

1. **Desde el formulario HTML**:
   - Ir a `http://localhost:8000/`
   - Ingresar usuario y contraseña
   - El sistema redirigirá automáticamente después del login

2. **Desde API (JSON)**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pm", "password": "pm123"}'
```

### Cerrar Sesión

```bash
curl -X POST http://localhost:8000/api/auth/logout/
```

---

## ✅ Verificación

Después de ejecutar `python manage.py create_demo_users`, todos los usuarios deberían tener:

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.all().values('username', 'is_staff', 'is_active')
```

**Resultado esperado**:
- `demo`: `is_staff=True`, `is_active=True`
- `pm`: `is_staff=True`, `is_active=True`
- `supervisor`: `is_staff=True`, `is_active=True`
- `admin`: `is_staff=True`, `is_active=True`

---

## 🔄 Actualizar Usuarios Existentes

Si ya tienes usuarios creados, ejecuta:

```bash
python manage.py create_demo_users
```

Esto actualizará todos los usuarios demo con `is_staff=True`.

---

## 📝 Notas

- El endpoint `/api/auth/login/` no requiere `is_staff=True`, pero el comando `create_demo_users` lo establece para compatibilidad con Django admin
- El endpoint `/admin/login/` sigue funcionando para usuarios con `is_staff=True`
- El nuevo endpoint `/api/auth/login/` es más flexible y permite login a cualquier usuario activo

---

**Última actualización**: 2026-01-18
