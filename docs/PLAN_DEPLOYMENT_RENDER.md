# Plan de Implementación: Deployment en Render.com

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: 📋 **PLAN DE IMPLEMENTACIÓN**

---

## 📊 Resumen Ejecutivo

Este documento presenta un plan detallado para implementar el sistema SITEC en producción usando **Render.com** como plataforma de hosting. Incluye evaluación de viabilidad, requisitos, pasos de implementación y consideraciones técnicas.

---

## ✅ Evaluación de Viabilidad en Render

### Viabilidad: ✅ **VIABLE CON MODIFICACIONES**

Render.com es **viable** para desplegar SITEC, pero requiere algunas adaptaciones:

| Requisito | Estado Actual | Render | Acción Requerida |
|-----------|---------------|--------|------------------|
| **Base de Datos** | SQLite | PostgreSQL ✅ | Migrar a PostgreSQL |
| **Python** | 3.10+ | ✅ Soportado | Ninguna |
| **Django** | 5.0 | ✅ Soportado | Ninguna |
| **Redis** | Opcional | ✅ Disponible | Configurar servicio Redis |
| **Celery** | Opcional | ✅ Soportado | Configurar workers |
| **Archivos Estáticos** | Django | WhiteNoise ✅ | Agregar WhiteNoise |
| **HTTPS/SSL** | Manual | ✅ Automático | Ninguna |
| **Variables de Entorno** | .env | ✅ Soportado | Configurar en dashboard |
| **Build Process** | Manual | ✅ Script | Crear build.sh |

### Ventajas de Render

1. ✅ **PostgreSQL gestionado**: Base de datos PostgreSQL incluida
2. ✅ **Redis gestionado**: Servicio Redis disponible
3. ✅ **SSL automático**: Certificados SSL/TLS gratuitos
4. ✅ **Deploy automático**: Integración con Git
5. ✅ **Escalado fácil**: Aumentar recursos según necesidad
6. ✅ **Monitoreo integrado**: Logs y métricas incluidas
7. ✅ **Backups automáticos**: Backups de base de datos incluidos

### Limitaciones a Considerar

1. ⚠️ **Costo**: Plan gratuito limitado, planes pagos según uso
2. ⚠️ **Cold starts**: Servicios gratuitos pueden tener cold starts
3. ⚠️ **Storage**: Archivos estáticos limitados (usar CDN para grandes volúmenes)
4. ⚠️ **Celery Workers**: Requieren servicio separado (costo adicional)

---

## 📋 Requisitos Previos

### 1. Cuenta en Render.com

- Crear cuenta en [render.com](https://render.com)
- Verificar email
- Conectar cuenta de Git (GitHub, GitLab, Bitbucket)

### 2. Repositorio Git

- Código en repositorio Git (GitHub recomendado)
- Branch `main` o `master` estable
- `.gitignore` configurado correctamente

### 3. Dependencias a Agregar

```txt
# Agregar a requirements.txt
psycopg2-binary>=2.9.0,<3.0  # PostgreSQL adapter
dj-database-url>=2.1.0,<3.0  # DATABASE_URL support
whitenoise>=6.6.0,<7.0       # Static files serving
gunicorn>=21.2.0,<22.0       # WSGI server
```

---

## 🚀 Plan de Implementación

### Fase 1: Preparación del Código (1-2 días)

#### 1.1. Actualizar Dependencias

**Archivo**: `requirements.txt`

```txt
Django>=5.0,<6.0
djangorestframework>=3.15,<4.0
celery>=5.3,<6.0
reportlab>=4.0,<5.0
django-otp>=1.2.0,<2.0
qrcode>=7.4.2,<8.0
pyotp>=2.9.0,<3.0
# Agregar para Render
psycopg2-binary>=2.9.0,<3.0
dj-database-url>=2.1.0,<3.0
whitenoise>=6.6.0,<7.0
gunicorn>=21.2.0,<22.0
```

#### 1.2. Configurar Settings para Producción

**Archivo**: `backend/config/settings.py`

Modificaciones necesarias:

```python
import dj_database_url
from pathlib import Path
import os

# ... código existente ...

# Base de datos - usar DATABASE_URL si está disponible
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Archivos estáticos - WhiteNoise
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise middleware (después de SecurityMiddleware)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Agregar aquí
    # ... resto del middleware ...
]

# WhiteNoise configuración
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Secret Key desde variable de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "replace-me-in-env")

# Debug desde variable de entorno
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Allowed hosts desde variable de entorno
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Cache - usar Redis si está disponible
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    }
} if os.getenv("REDIS_URL") else {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sitec-cache",
    }
}

# Celery - usar Redis si está disponible
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
```

#### 1.3. Crear Script de Build

**Archivo**: `build.sh` (en raíz del proyecto)

```bash
#!/usr/bin/env bash
# Build script para Render

set -o errexit  # Exit on error

echo "Building SITEC application..."

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar migraciones
cd backend
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

echo "Build completed successfully!"
```

Hacer ejecutable:
```bash
chmod +x build.sh
```

#### 1.4. Crear Script de Inicio

**Archivo**: `start.sh` (en raíz del proyecto)

```bash
#!/usr/bin/env bash
# Start script para Render

cd backend
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

Hacer ejecutable:
```bash
chmod +x start.sh
```

#### 1.5. Crear Render Blueprint (Opcional)

**Archivo**: `render.yaml` (en raíz del proyecto)

```yaml
services:
  - type: web
    name: sitec-web
    env: python
    buildCommand: ./build.sh
    startCommand: ./start.sh
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: sitec.onrender.com
      - key: DATABASE_URL
        fromDatabase:
          name: sitec-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: sitec-redis
          type: redis
          property: connectionString
      - key: RATE_LIMIT_ENABLED
        value: true
      - key: RATE_LIMIT_REQUESTS
        value: 100
      - key: RATE_LIMIT_WINDOW
        value: 60
      - key: CSP_ENABLED
        value: true

  - type: worker
    name: sitec-celery-worker
    env: python
    buildCommand: ./build.sh
    startCommand: cd backend && celery -A config worker -l info
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: sitec-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: sitec-redis
          type: redis
          property: connectionString

  - type: worker
    name: sitec-celery-beat
    env: python
    buildCommand: ./build.sh
    startCommand: cd backend && celery -A config beat -l info
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: sitec-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: sitec-redis
          type: redis
          property: connectionString

databases:
  - name: sitec-db
    databaseName: sitec
    user: sitec_user
    plan: starter  # o free, starter, standard, etc.

services:
  - type: redis
    name: sitec-redis
    plan: starter  # o free, starter, standard, etc.
```

---

### Fase 2: Configuración en Render (1 día)

#### 2.1. Crear Base de Datos PostgreSQL

1. En Render Dashboard, ir a **"New +"** → **"PostgreSQL"**
2. Configurar:
   - **Name**: `sitec-db`
   - **Database**: `sitec`
   - **User**: `sitec_user`
   - **Plan**: Seleccionar según necesidades (Free para pruebas)
3. Guardar y copiar **Internal Database URL**

#### 2.2. Crear Servicio Redis (Opcional)

1. En Render Dashboard, ir a **"New +"** → **"Redis"**
2. Configurar:
   - **Name**: `sitec-redis`
   - **Plan**: Seleccionar según necesidades (Free para pruebas)
3. Guardar y copiar **Internal Redis URL**

#### 2.3. Crear Web Service

1. En Render Dashboard, ir a **"New +"** → **"Web Service"**
2. Conectar repositorio Git
3. Configurar:
   - **Name**: `sitec-web`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: Seleccionar según necesidades

#### 2.4. Configurar Variables de Entorno

En el Web Service, agregar variables de entorno:

**Obligatorias**:
```
SECRET_KEY=<generar-secret-key-seguro>
DEBUG=false
ALLOWED_HOSTS=sitec.onrender.com,tu-dominio.com
DATABASE_URL=<desde-postgres-service>
```

**Opcionales (según necesidades)**:
```
REDIS_URL=<desde-redis-service>
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_USER_REQUESTS=200
RATE_LIMIT_USER_WINDOW=60
CSP_ENABLED=true
CSP_DEFAULT_SRC='self'
CSP_SCRIPT_SRC='self' 'unsafe-inline'
CSP_STYLE_SRC='self' 'unsafe-inline'
CSP_IMG_SRC='self' data: https:
CSP_FONT_SRC='self' data:
CSP_CONNECT_SRC='self'
```

**Proveedores Externos (opcionales)**:
```
NOM151_PROVIDER_URL=
NOM151_API_KEY=
AI_TRAIN_PROVIDER_URL=
AI_TRAIN_API_KEY=
```

#### 2.5. Crear Celery Workers (Opcional)

1. **Celery Worker**:
   - **"New +"** → **"Background Worker"**
   - **Name**: `sitec-celery-worker`
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd backend && celery -A config worker -l info`
   - Conectar a misma base de datos y Redis

2. **Celery Beat**:
   - **"New +"** → **"Background Worker"**
   - **Name**: `sitec-celery-beat`
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd backend && celery -A config beat -l info`
   - Conectar a misma base de datos y Redis

---

### Fase 3: Migración de Datos (1 día)

#### 3.1. Backup de Datos Actuales

```bash
# Si tienes datos en SQLite
python manage.py dumpdata > backup.json
```

#### 3.2. Migrar a PostgreSQL

1. Conectar a base de datos PostgreSQL en Render
2. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```
3. Cargar datos de backup (si aplica):
   ```bash
   python manage.py loaddata backup.json
   ```

#### 3.3. Seed de Datos Iniciales

```bash
python manage.py seed_sitec
```

#### 3.4. Crear Usuario Administrador

```bash
python manage.py createsuperuser
```

---

### Fase 4: Validación y Testing (1 día)

#### 4.1. Health Checks

```bash
# Health check básico
curl https://sitec.onrender.com/health/

# Health check detallado
curl https://sitec.onrender.com/health/detailed/
```

#### 4.2. Validar Funcionalidades

- [ ] Login funciona
- [ ] MFA funciona
- [ ] API endpoints responden
- [ ] Archivos estáticos se sirven
- [ ] Rate limiting funciona
- [ ] Celery workers procesan tareas (si configurado)

#### 4.3. Tests Automatizados

```bash
# Ejecutar tests en entorno de staging
python manage.py test
```

---

### Fase 5: Configuración de Dominio Personalizado (Opcional)

#### 5.1. Agregar Dominio en Render

1. En Web Service → **Settings** → **Custom Domains**
2. Agregar dominio: `tu-dominio.com`
3. Render proporcionará registros DNS

#### 5.2. Configurar DNS

1. En tu proveedor DNS, agregar registros proporcionados por Render
2. Esperar propagación DNS (puede tardar hasta 48 horas)

#### 5.3. Actualizar ALLOWED_HOSTS

```
ALLOWED_HOSTS=sitec.onrender.com,tu-dominio.com,www.tu-dominio.com
```

---

## 📊 Estimación de Costos (Render)

### Plan Gratuito (Para Pruebas)

- **Web Service**: Gratis (con limitaciones)
- **PostgreSQL**: Gratis (90 días, luego $7/mes)
- **Redis**: Gratis (25MB, luego $10/mes)
- **Celery Workers**: Gratis (con limitaciones)

**Total**: $0 por 90 días, luego ~$17/mes mínimo

### Plan Starter (Recomendado para Producción)

- **Web Service**: $7/mes
- **PostgreSQL**: $7/mes
- **Redis**: $10/mes
- **Celery Workers**: $7/mes cada uno (2 workers = $14/mes)

**Total**: ~$38/mes

### Plan Standard (Alto Tráfico)

- **Web Service**: $25/mes
- **PostgreSQL**: $20/mes
- **Redis**: $15/mes
- **Celery Workers**: $25/mes cada uno

**Total**: ~$85/mes

---

## ✅ Checklist de Implementación

### Pre-Deployment

- [ ] Código en repositorio Git
- [ ] Dependencias actualizadas (`requirements.txt`)
- [ ] Settings configurados para producción
- [ ] `build.sh` creado y probado
- [ ] `start.sh` creado y probado
- [ ] WhiteNoise configurado
- [ ] `render.yaml` creado (opcional)

### Deployment

- [ ] Cuenta Render creada
- [ ] Repositorio conectado
- [ ] Base de datos PostgreSQL creada
- [ ] Servicio Redis creado (opcional)
- [ ] Web Service creado
- [ ] Variables de entorno configuradas
- [ ] Build exitoso
- [ ] Servicio funcionando

### Post-Deployment

- [ ] Migraciones ejecutadas
- [ ] Seed de datos ejecutado
- [ ] Usuario administrador creado
- [ ] Health checks pasando
- [ ] Funcionalidades validadas
- [ ] Tests pasando
- [ ] Dominio personalizado configurado (opcional)
- [ ] Monitoreo configurado

---

## 🔒 Consideraciones de Seguridad

### 1. Secret Key

- **Nunca** commitear `SECRET_KEY` al repositorio
- Generar nuevo `SECRET_KEY` para producción
- Usar variable de entorno en Render

### 2. Variables de Entorno

- Todas las variables sensibles en Render Dashboard
- No usar valores por defecto en producción
- Rotar credenciales periódicamente

### 3. Rate Limiting

- Habilitar en producción: `RATE_LIMIT_ENABLED=true`
- Configurar límites apropiados
- Monitorear eventos de rate limit

### 4. CSP Headers

- Habilitar en producción: `CSP_ENABLED=true`
- Ajustar políticas según necesidades
- Probar en staging antes de producción

### 5. HTTPS

- Render proporciona SSL automático
- Forzar HTTPS en settings (si necesario)
- Verificar certificados válidos

---

## 📝 Notas Técnicas

### Archivos Estáticos

- WhiteNoise sirve archivos estáticos en producción
- No requiere CDN para volúmenes pequeños
- Para grandes volúmenes, considerar CDN (Cloudflare, etc.)

### Base de Datos

- PostgreSQL gestionado por Render
- Backups automáticos incluidos
- Escalado fácil según necesidades

### Redis

- Opcional pero recomendado para:
  - Rate limiting avanzado
  - Cache de Django
  - Celery broker
- Plan gratuito limitado a 25MB

### Celery

- Workers separados para tareas async
- Beat scheduler para tareas periódicas
- Requiere Redis como broker

---

## 🎯 Conclusión

**Render.com es viable** para desplegar SITEC con las siguientes consideraciones:

✅ **Ventajas**:
- Setup rápido y fácil
- PostgreSQL y Redis gestionados
- SSL automático
- Deploy automático desde Git
- Escalado fácil

⚠️ **Consideraciones**:
- Requiere migración de SQLite a PostgreSQL
- Costos según plan seleccionado
- Celery workers requieren servicios separados

**Recomendación**: ✅ **Proceder con implementación en Render**

---

**Última actualización**: 2026-01-23
