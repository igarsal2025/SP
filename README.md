# SITEC - Sistema de Seguimiento de Proyectos

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

Sistema web profesional para seguimiento y gestión de proyectos con autenticación avanzada, control de acceso basado en atributos (ABAC), y múltiples funcionalidades de gestión.

---

## 📋 Tabla de Contenidos

- [Características](#-características-principales)
- [Inicio Rápido](#-inicio-rápido)
- [Instalación](#instalación)
- [Documentación](#-documentación)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Configuración](#-configuración)
- [Estado del Proyecto](#-estado-del-proyecto)
- [Contribuir](#-contribuir)
- [Soporte](#-soporte)

---

## 🚀 Inicio Rápido

### Requisitos

- Python 3.10+
- PostgreSQL (producción) o SQLite (desarrollo)
- Redis (opcional, para cache y Celery)

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/igarsal2025/SP.git
cd SeguimientoProyectos

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# o
source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
cd backend
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Seed de datos iniciales
python manage.py seed_sitec

# 7. Ejecutar servidor
python manage.py runserver
```

Acceder a: `http://localhost:8000`

---

## 📚 Documentación

Ver `docs/README.md` para documentación completa organizada por categorías.

### Documentación Principal

- **Inicio Rápido**: `docs/GUIA_INICIO_RAPIDO.md`
- **Instalación**: `docs/INSTALACION_BASICA.md`
- **Deployment**: `docs/PLAN_DEPLOYMENT_RENDER.md`
- **Testing**: `docs/TESTING.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

---

## ✨ Características Principales

### 🔐 Seguridad

- ✅ **MFA (Multi-Factor Authentication)** - Autenticación de dos factores con TOTP
- ✅ **Rate Limiting Avanzado** - Por IP, usuario y endpoint
- ✅ **ABAC (Attribute-Based Access Control)** - Control de acceso granular
- ✅ **Security Headers** - CSP, XSS protection, etc.

### 📊 Gestión de Proyectos

- ✅ Dashboard con visualizaciones
- ✅ Reportes semanales
- ✅ ROI tracking
- ✅ Filtros avanzados
- ✅ Wizard contextual

### 🎨 Frontend

- ✅ Diseño responsive
- ✅ UI basada en roles
- ✅ Navegación por secciones
- ✅ PWA (Progressive Web App)
- ✅ Offline support

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test apps.accounts.tests_mfa
python manage.py test apps.accounts.tests_rate_limit_advanced
python manage.py test apps.frontend.tests_p0_navigation
```

Ver `docs/TESTING.md` para más información.

---

## 🚀 Deployment

### Render.com

El sistema está preparado para deployment en Render.com:

1. Ver `docs/PLAN_DEPLOYMENT_RENDER.md` para plan completo
2. Ver `docs/GUIA_RAPIDA_RENDER.md` para guía rápida
3. Archivos de configuración:
   - `build.sh` - Script de build
   - `start.sh` - Script de inicio
   - `render.yaml` - Blueprint (opcional)

---

## 📁 Estructura del Proyecto

```
SeguimientoProyectos/
├── backend/                    # Aplicación Django
│   ├── apps/                  # Módulos de la aplicación
│   │   ├── accounts/         # Autenticación, MFA, ABAC
│   │   ├── projects/          # Gestión de proyectos
│   │   ├── reports/           # Reportes semanales
│   │   ├── dashboard/         # Dashboard y visualizaciones
│   │   ├── roi/               # Tracking de ROI
│   │   ├── frontend/          # Vistas y templates
│   │   └── ...
│   ├── config/                # Configuración Django
│   │   ├── settings.py        # Configuración principal
│   │   ├── urls.py            # URLs principales
│   │   └── wsgi.py            # WSGI config
│   └── static/                # Archivos estáticos
├── docs/                      # Documentación completa
│   ├── deployment/            # Guías de deployment
│   ├── security/              # Seguridad, MFA, Rate Limiting
│   ├── testing/               # Tests y resultados
│   ├── implementation/         # Implementaciones
│   ├── guides/                # Guías de uso
│   └── troubleshooting/       # Solución de problemas
├── scripts/                   # Scripts de utilidad
├── build.sh                   # Build script (Render)
├── start.sh                   # Start script (Render)
├── render.yaml                # Render blueprint
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

---

## 🔧 Configuración

### Variables de Entorno

El sistema funciona con valores por defecto. Para personalizar, crear archivo `.env` en `backend/`:

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/sitec

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100

# CSP Headers
CSP_ENABLED=true
```

Ver `docs/CONFIGURACION_SEGURIDAD.md` para más opciones.

---

## 👥 Usuarios Demo


---

## 📊 Estado del Proyecto

### ✅ Completado

- ✅ Rediseño frontend (Fases 1-5)
- ✅ MFA (Backend + Frontend)
- ✅ Rate Limiting Avanzado
- ✅ Navegación P0
- ✅ Tests automatizados

### 🚧 En Progreso

- ⏳ Deployment en producción
- ⏳ Integraciones externas (NOM-151, IA ML)

### 📋 Pendiente

Ver `docs/PLAN_IMPLEMENTACION_PRIORIZADO.md` para plan completo.

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es de propiedad privada. Todos los derechos reservados.

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.0, Django REST Framework
- **Base de Datos**: PostgreSQL (producción), SQLite (desarrollo)
- **Autenticación**: Django OTP (TOTP), MFA
- **Cache**: Redis (opcional)
- **Task Queue**: Celery
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: Render.com, Gunicorn, WhiteNoise

---

## 📞 Soporte

Para problemas o preguntas:
- 📖 Ver `docs/TROUBLESHOOTING.md` para problemas comunes
- 🐛 Crear un [issue](https://github.com/igarsal2025/SP/issues) en el repositorio
- 📧 Contactar al equipo de desarrollo

---

## 📊 Estadísticas del Proyecto

- **Versión**: 1.0.0
- **Última actualización**: 2026-01-23
- **Estado**: En desarrollo activo
- **Tests**: ✅ 50+ tests automatizados

---

## 🙏 Agradecimientos

Desarrollado para SITEC - Sistema de Seguimiento de Proyectos.

---

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub**
