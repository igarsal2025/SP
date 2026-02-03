# Instalación Básica de SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Resumen

Esta guía describe la instalación básica de SITEC **sin proveedores externos**. El sistema funciona completamente sin configuración adicional.

---

## ✅ Requisitos Previos

- Python 3.9+
- PostgreSQL (recomendado) o SQLite (desarrollo)
- Redis (opcional, para Celery)
- Git

---

## 🚀 Instalación Rápida

### 1. Clonar Repositorio

```bash
git clone <repository-url>
cd SeguimientoProyectos
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

```bash
# Crear archivo .env (opcional - el sistema funciona con defaults)
# Ver backend/config/settings.py para defaults

# Ejecutar migraciones
python manage.py migrate
```

### 5. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 6. Ejecutar Servidor

```bash
python manage.py runserver
```

**¡Listo!** El sistema está funcionando en `http://localhost:8000`

---

## 🔧 Configuración Opcional

### Variables de Entorno (Opcional)

El sistema funciona sin configuración adicional. Si deseas personalizar:

```bash
# Crear archivo .env en backend/
# Todas estas variables son OPCIONALES

# Base de datos (si no usas defaults)
DATABASE_URL=postgresql://user:password@localhost:5432/sitec

# Secret key (generar uno nuevo para producción)
SECRET_KEY=tu-secret-key-aqui

# Debug (solo desarrollo)
DEBUG=True

# Proveedores externos (OPCIONALES - ver docs/PROVEEDORES_OPCIONALES.md)
# NOM151_PROVIDER_URL=
# NOM151_API_KEY=
# AI_TRAIN_PROVIDER_URL=
# AI_TRAIN_API_KEY=
```

---

## ✅ Verificación

### 1. Acceder al Admin

```
http://localhost:8000/admin/
```

### 2. Acceder al Wizard

```
http://localhost:8000/wizard/1/
```

### 3. Verificar API

```bash
# Obtener KPIs del dashboard
curl http://localhost:8000/api/dashboard/

# Evaluar permisos
curl -X POST http://localhost:8000/api/policies/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{"action": "wizard.save"}'
```

---

## 📊 Funcionalidades Disponibles (Sin Configuración)

| Funcionalidad | Estado | Notas |
|---------------|--------|-------|
| **Wizard** | ✅ Funciona | Todos los pasos funcionan |
| **Dashboard** | ✅ Funciona | KPIs y comparativos funcionan |
| **ABAC** | ✅ Funciona | Sistema de permisos funciona |
| **Generación de PDFs** | ✅ Funciona | PDFs se generan correctamente |
| **Sello NOM-151** | ⚠️ Pendiente | Se marca como "pendiente" (normal) |
| **Sugerencias IA** | ✅ Funciona | Usa proveedores locales |
| **Comparativos** | ✅ Funciona | Comparativos históricos funcionan |

---

## 🔍 Troubleshooting

### Error: "Django no está instalado"

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "No module named 'psycopg2'"

```bash
# Instalar psycopg2 (PostgreSQL)
pip install psycopg2-binary

# O usar SQLite (no requiere instalación adicional)
# Cambiar DATABASES en settings.py
```

### Error: "ModuleNotFoundError"

```bash
# Verificar que estás en el directorio correcto
cd backend

# Reinstalar dependencias
pip install -r requirements.txt
```

---

## 📚 Próximos Pasos

1. **Configurar proveedores externos** (opcional):
   - Ver `docs/PROVEEDORES_OPCIONALES.md`
   - Ver `docs/CONFIGURACION_NOM151.md`

2. **Configurar producción**:
   - Ver `docs/PLAN_ACCION_P0.md`
   - Configurar variables de entorno de producción

3. **Explorar funcionalidades**:
   - Wizard: `/wizard/1/`
   - Dashboard: `/api/dashboard/`
   - Admin: `/admin/`

---

## ✅ Checklist de Instalación

- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Base de datos configurada
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Servidor ejecutándose
- [ ] Admin accesible
- [ ] Wizard funcionando
- [ ] API respondiendo

---

**Última actualización**: 2026-01-18
