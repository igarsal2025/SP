# Credenciales Demo - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔐 Usuarios Demo Disponibles

### Usuario Técnico (Demo)

- **Usuario**: `demo`
- **Contraseña**: `demo123`
- **Email**: `demo@sitec.mx`
- **Rol**: `tecnico`
- **Permisos**: Acceso completo al wizard, puede guardar y enviar reportes

---

### Usuario Project Manager

- **Usuario**: `pm`
- **Contraseña**: `pm123`
- **Email**: `pm@sitec.mx`
- **Rol**: `pm`
- **Permisos**: Acceso a dashboard, ROI, aprobación de reportes, creación de proyectos

---

### Usuario Supervisor

- **Usuario**: `supervisor`
- **Contraseña**: `supervisor123`
- **Email**: `supervisor@sitec.mx`
- **Rol**: `supervisor`
- **Permisos**: Acceso a dashboard, aprobación de reportes, supervisión

---

### Usuario Administrador

- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Email**: `admin@sitec.mx`
- **Rol**: `admin_empresa`
- **Permisos**: Acceso completo a todas las funcionalidades

---

## 🚀 Crear/Actualizar Usuarios Demo

### Comando

```bash
cd backend
python manage.py create_demo_users
```

Este comando:
- ✅ Crea los usuarios demo si no existen
- ✅ Actualiza las contraseñas si ya existen
- ✅ Asigna los roles correctos
- ✅ Asocia los usuarios a la company y sitec

---

## 📋 Tabla Resumen

| Usuario | Contraseña | Rol | Funcionalidades Principales |
|---------|------------|-----|----------------------------|
| `demo` | `demo123` | técnico | Wizard completo, guardar/enviar reportes |
| `pm` | `pm123` | pm | Dashboard, ROI, aprobaciones, proyectos |
| `supervisor` | `supervisor123` | supervisor | Dashboard, aprobaciones, supervisión |
| `admin` | `admin123` | admin_empresa | Acceso completo al sistema |

---

## 🔒 Seguridad

**⚠️ IMPORTANTE**: Estas credenciales son solo para desarrollo y pruebas.

**Para producción**:
1. Cambiar todas las contraseñas
2. Usar contraseñas seguras
3. Habilitar autenticación de dos factores (MFA) cuando esté disponible
4. Revisar y ajustar políticas ABAC según necesidades

---

## 📝 Notas

- Todos los usuarios están asociados a la Company "SITEC" y Sitec "sitec"
- Las políticas ABAC permiten acceso según el rol
- Los usuarios pueden tener múltiples roles (configurable en UserProfile)

---

**Última actualización**: 2026-01-18
