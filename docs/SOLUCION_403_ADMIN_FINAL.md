# Solución Final para Errores 403 con Usuario Admin

**Fecha**: 2026-01-18  
**Versión**: 1.1

---

## 🔍 Problema

El usuario `admin` con rol `admin_empresa` está recibiendo errores 403 en:
- `/api/wizard/validate/`
- `/api/wizard/analytics/`
- `/api/wizard/sync/`

A pesar de que:
- El usuario tiene rol `admin_empresa`
- El código debería permitir acceso completo
- Las pruebas con `client.force_login()` funcionan (200)

---

## ✅ Cambios Implementados

### 1. Logs de Depuración en `evaluate_access_policy()`

Se agregaron logs detallados para identificar exactamente dónde se está denegando el acceso:

```python
def evaluate_access_policy(request, action_name):
    import logging
    logger = logging.getLogger(__name__)
    
    # Logs en cada punto de decisión
    if not user:
        logger.debug(f"[ABAC] No user found for action: {action_name}")
        return PolicyDecision(allowed=False)
    
    if not is_authenticated:
        logger.debug(f"[ABAC] User {user.username} is not authenticated for action: {action_name}")
        return PolicyDecision(allowed=False)
    
    if not profile:
        logger.debug(f"[ABAC] No profile found for user {user.username}")
        return PolicyDecision(allowed=False)
    
    if profile.role == "admin_empresa":
        logger.debug(f"[ABAC] Admin empresa {user.username} granted access to {action_name}")
        return PolicyDecision(allowed=True, ...)
```

### 2. Configuración de Logging en `settings.py`

Se agregó configuración de logging para que los logs de depuración se muestren en la consola:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "apps.accounts.services": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "apps.accounts.permissions": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}
```

---

## 🔍 Diagnóstico

### Verificar Logs del Servidor

1. **Reinicia el servidor Django** para que los cambios surtan efecto
2. **Intenta acceder al wizard** con el usuario admin
3. **Revisa los logs en la consola** del servidor. Deberías ver mensajes como:
   - `[ABAC] No user found for action: wizard.validate`
   - `[ABAC] User admin is not authenticated for action: wizard.validate`
   - `[ABAC] No profile found for user admin`
   - `[ABAC] Admin empresa admin granted access to wizard.validate`

### Posibles Causas

Basado en los logs, el problema podría ser:

1. **Usuario no autenticado**: `IsAuthenticated` está retornando `False`
   - **Solución**: Verificar que las cookies de sesión se están enviando correctamente
   - **Verificar**: En DevTools → Network → Request Headers → `Cookie: sessionid=...`

2. **Perfil no encontrado**: El `UserProfile` no existe o no está asociado a una company
   - **Solución**: Ejecutar `python manage.py seed_sitec` para recrear los perfiles

3. **Company no encontrada**: El perfil existe pero no tiene company asociada
   - **Solución**: Verificar que el usuario admin tiene un perfil con company

---

## 📋 Pasos para Resolver

### 1. Verificar Estado del Usuario

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from apps.accounts.models import UserProfile
>>> User = get_user_model()
>>> admin = User.objects.get(username="admin")
>>> profile = UserProfile.objects.get(user=admin)
>>> print(f"Usuario: {admin.username}")
>>> print(f"Autenticado: {admin.is_authenticated}")
>>> print(f"Perfil: {profile.role}")
>>> print(f"Company: {profile.company.name if profile.company else None}")
```

### 2. Verificar Cookies en el Navegador

1. Abre DevTools (F12)
2. Ve a **Application** → **Cookies** → `http://127.0.0.1:8000`
3. Verifica que existan:
   - `sessionid` (cookie de sesión de Django)
   - `csrftoken` (token CSRF)

### 3. Verificar Request Headers

1. Abre DevTools (F12)
2. Ve a **Network**
3. Busca una llamada a `/api/wizard/validate/`
4. Haz clic en la llamada
5. Ve a **Headers** → **Request Headers**
6. Verifica que exista: `Cookie: sessionid=...`

### 4. Limpiar Cookies y Volver a Iniciar Sesión

1. Cierra sesión
2. Limpia todas las cookies del sitio (`http://127.0.0.1:8000`)
3. Recarga la página con `Ctrl + Shift + R`
4. Inicia sesión nuevamente con `admin` / `admin123`

### 5. Recrear Perfiles y Políticas

```bash
python manage.py seed_sitec
```

---

## 🔧 Soluciones Alternativas

Si el problema persiste después de verificar los logs:

### Opción 1: Verificar Orden de Middleware

El orden de middleware en `settings.py` debe ser:
```python
MIDDLEWARE = [
    ...
    "django.contrib.sessions.middleware.SessionMiddleware",
    ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.CompanySitecMiddleware",
    ...
]
```

### Opción 2: Verificar Configuración de Sesiones

Agregar a `settings.py`:
```python
SESSION_COOKIE_SECURE = False  # En desarrollo
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
```

### Opción 3: Verificar que el Usuario Está Activo

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.get(username="admin")
>>> admin.is_active = True
>>> admin.save()
```

---

## 📝 Notas

- Los logs de depuración solo se muestran cuando `DEBUG = True`
- Los logs aparecerán en la consola donde se ejecuta `python manage.py runserver`
- Si no ves logs, verifica que el nivel de logging esté configurado correctamente

---

**Última actualización**: 2026-01-18
