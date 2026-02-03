# Guía de Inicio Rápido - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🚀 Inicio Rápido del Sistema

### 1. Activar Entorno Virtual

```powershell
# Windows PowerShell
cd G:\SeguimientoProyectos
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### 2. Aplicar Migraciones

```bash
cd backend
python manage.py migrate
```

**Resultado esperado**: Todas las migraciones aplicadas, incluyendo:
- ✅ `projects.0003_add_performance_indexes`
- ✅ `reports.0004_add_performance_indexes`

### 3. Configurar Datos Iniciales (Primera vez)

```bash
python manage.py seed_sitec
```

**Esto crea**:
- Company y Sitec por defecto
- Usuario administrador
- ~70 políticas ABAC
- Reglas base

### 4. Iniciar Servidor

```bash
python manage.py runserver
```

**Servidor disponible en**: `http://localhost:8000`

---

## ✅ Verificación del Sistema

### Health Check Básico

```bash
curl http://localhost:8000/health/
```

**Respuesta esperada**:
```json
{
  "status": "ok",
  "service": "SITEC",
  "version": "1.0.0"
}
```

### Health Check Detallado

```bash
curl http://localhost:8000/health/detailed/
```

**Verifica**:
- ✅ Base de datos
- ✅ Cache
- ✅ Proveedores opcionales (NOM-151, IA)

---

## 📊 Endpoints Principales

### API

- **Health**: `GET /health/` (sin autenticación)
- **Health Detallado**: `GET /health/detailed/` (sin autenticación)
- **Métricas**: `GET /api/metrics/` (requiere autenticación)
- **Dashboard KPIs**: `GET /api/dashboard/kpi/` (requiere autenticación)
- **Dashboard Tendencias**: `GET /api/dashboard/trends/` (requiere autenticación)
- **ROI**: `GET /api/roi/` (requiere autenticación)
- **Wizard**: `POST /api/wizard/steps/save/` (requiere autenticación)
- **Sync**: `POST /api/sync/` (requiere autenticación)

### Frontend

- **Dashboard**: `http://localhost:8000/`
- **Wizard**: `http://localhost:8000/wizard/`
- **Admin**: `http://localhost:8000/admin/`

---

## 🔐 Acceso Inicial

### Usuario Administrador

Después de ejecutar `seed_sitec`:

- **Username**: `admin` (o el configurado)
- **Password**: Verificar en el comando `seed_sitec`

### Crear Usuario Manualmente

```bash
python manage.py createsuperuser
```

---

## ⚙️ Configuración Opcional

### Variables de Entorno

Crear archivo `.env` en `backend/` (opcional):

```bash
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Observabilidad
OBSERVABILITY_ENABLED=true

# Security Headers
CSP_ENABLED=false

# IA Throttling
AI_THROTTLE_ENABLED=false
AI_COST_TRACKING_ENABLED=false

# NOM-151 (Opcional)
NOM151_PROVIDER_URL=
NOM151_API_KEY=

# IA Real (Opcional)
AI_TRAIN_PROVIDER_URL=
AI_TRAIN_API_KEY=
```

**Nota**: El sistema funciona completamente sin estas configuraciones.

---

## 🧪 Verificar Funcionamiento

### 1. Health Check

```bash
curl http://localhost:8000/health/
```

### 2. Verificar Base de Datos

```bash
python manage.py shell -c "from apps.companies.models import Company, Sitec; print(f'Companies: {Company.objects.count()}, Sitecs: {Sitec.objects.count()}')"
```

### 3. Ejecutar Tests

```bash
python manage.py test apps.frontend.tests_e2e --verbosity=1
```

---

## 📝 Estado del Sistema

### Funcionalidades Disponibles

✅ **Wizard completo** (12 pasos)
✅ **Dashboard con KPIs y tendencias**
✅ **ROI con comparativos y análisis**
✅ **Sync offline-first**
✅ **ABAC completo** (~70 políticas)
✅ **Throttling y costos de IA**
✅ **Seguridad** (rate limiting, headers)
✅ **Health checks**
✅ **Métricas de observabilidad**
✅ **71 tests pasando**

### Pendiente (Opcional)

⏳ **NOM-151 Real** - Requiere proveedor externo
⏳ **IA Real ML** - Requiere proveedor ML externo

---

## 🐛 Solución de Problemas

### Error: "Configuracion SITEC incompleta"

**Solución**: Ejecutar `python manage.py seed_sitec`

### Error: "ModuleNotFoundError"

**Solución**: Activar entorno virtual y verificar dependencias

### Error: "Port 8000 already in use"

**Solución**: Usar otro puerto: `python manage.py runserver 8001`

### Error: "Database locked"

**Solución**: Cerrar otras conexiones a la base de datos

---

## 📚 Documentación Adicional

- `docs/ESTADO_ACTUAL_PROYECTO.md` - Estado completo del proyecto
- `docs/GUIA_DEPLOYMENT.md` - Guía de deployment
- `docs/TROUBLESHOOTING.md` - Solución de problemas
- `docs/PROVEEDORES_OPCIONALES.md` - Proveedores opcionales

---

**Última actualización**: 2026-01-18  
**Estado**: ✅ **SISTEMA LISTO PARA USO**
