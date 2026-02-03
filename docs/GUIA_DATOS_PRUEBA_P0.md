# Guía de Datos de Prueba P0

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 📋 Resumen

Este documento describe cómo generar y usar los datos de prueba para validar manualmente las funcionalidades P0 (navegación y rechazo de reportes).

---

## 🚀 Generar Datos de Prueba

### Comando

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py generate_test_data_p0
```

### Opciones

```powershell
# Generar datos (mantiene existentes)
python manage.py generate_test_data_p0

# Limpiar y regenerar datos
python manage.py generate_test_data_p0 --clear
```

---

## 👥 Usuarios de Prueba Creados

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `test_pm` | `test123` | PM | Project Manager - Puede crear/editar proyectos |
| `test_supervisor` | `test123` | Supervisor | Puede aprobar/rechazar reportes |
| `test_tecnico` | `test123` | Técnico | Crea reportes semanales |
| `test_admin` | `test123` | Admin | Administrador de empresa |

**Nota**: Si los usuarios ya existen, se actualizarán sus perfiles pero no se cambiarán las contraseñas.

---

## 📁 Proyectos de Prueba Creados

### 1. [TEST P0] Proyecto En Progreso
- **Código**: `TEST-P0-001`
- **Estado**: En Progreso
- **Progreso**: 45%
- **Prioridad**: Alta
- **Presupuesto**: $500,000 MXN (estimado) / $225,000 MXN (actual)
- **Uso**: Probar detalle, edición, y reportes asociados

### 2. [TEST P0] Proyecto Planificación
- **Código**: `TEST-P0-002`
- **Estado**: Planificación
- **Progreso**: 0%
- **Prioridad**: Media
- **Presupuesto**: $300,000 MXN (estimado)
- **Uso**: Probar creación y edición de proyectos nuevos

### 3. [TEST P0] Proyecto Completado
- **Código**: `TEST-P0-003`
- **Estado**: Completado
- **Progreso**: 100%
- **Prioridad**: Alta
- **Presupuesto**: $750,000 MXN (estimado) / $720,000 MXN (actual)
- **Uso**: Ver historial de proyectos completados

### 4. [TEST P0] Proyecto En Pausa
- **Código**: `TEST-P0-004`
- **Estado**: En Pausa
- **Progreso**: 25%
- **Prioridad**: Media
- **Presupuesto**: $400,000 MXN (estimado) / $100,000 MXN (actual)
- **Uso**: Probar diferentes estados de proyecto

---

## 📄 Reportes de Prueba Creados

### Reportes Enviados (submitted) - 2 reportes

Estos reportes están listos para aprobar o rechazar:

1. **Reporte Reciente** (hace 12 horas)
   - Semana: Esta semana
   - Progreso: 48%
   - Estado: `submitted`
   - **Uso**: Probar rechazo con razón

2. **Reporte Antiguo** (hace 2 días)
   - Semana: Semana pasada
   - Progreso: 45%
   - Estado: `submitted`
   - **Uso**: Probar aprobación/rechazo

### Reporte Aprobado - 1 reporte

- Semana: Hace 2 semanas
- Progreso: 40%
- Estado: `approved`
- **Uso**: Verificar que no se puede rechazar un reporte ya aprobado

### Reporte Rechazado - 1 reporte

- Semana: Hace 3 semanas
- Progreso: 35%
- Estado: `rejected`
- Razón: "Falta información en la sección de incidentes"
- **Uso**: Ver historial de rechazos y razón guardada

### Reporte Borrador - 1 reporte

- Semana: Esta semana
- Progreso: 50%
- Estado: `draft`
- **Uso**: Verificar que no se puede rechazar un borrador

---

## 🧪 Escenarios de Prueba

### Escenario 1: Ver Detalle de Proyecto

**Pasos**:
1. Iniciar sesión como `test_pm` / `test123`
2. Ir a `/projects/`
3. Hacer clic en "Ver" del proyecto `[TEST P0] Proyecto En Progreso`
4. Verificar que se muestre toda la información

**Resultado Esperado**: ✅ Página de detalle muestra todos los campos

---

### Escenario 2: Editar Proyecto

**Pasos**:
1. Iniciar sesión como `test_pm` / `test123`
2. Ir a `/projects/`
3. Hacer clic en "Editar" del proyecto `[TEST P0] Proyecto Planificación`
4. Modificar algunos campos (ej: descripción, progreso)
5. Guardar cambios
6. Verificar que se redirija a detalle y los cambios se reflejen

**Resultado Esperado**: ✅ Formulario funciona, guarda y redirige

---

### Escenario 3: Crear Proyecto

**Pasos**:
1. Iniciar sesión como `test_pm` / `test123`
2. Ir a `/projects/`
3. Hacer clic en "Crear Proyecto"
4. Completar formulario con datos válidos
5. Crear proyecto
6. Verificar que se redirija a detalle del nuevo proyecto

**Resultado Esperado**: ✅ Proyecto se crea y redirige a detalle

---

### Escenario 4: Ver Detalle de Reporte

**Pasos**:
1. Iniciar sesión como cualquier usuario
2. Ir a `/reports/` o `/reports/approvals/`
3. Hacer clic en "Ver" de un reporte enviado
4. Verificar que se muestre toda la información

**Resultado Esperado**: ✅ Página de detalle muestra información completa

---

### Escenario 5: Rechazar Reporte

**Pasos**:
1. Iniciar sesión como `test_supervisor` / `test123`
2. Ir a `/reports/approvals/`
3. Hacer clic en "Rechazar" del reporte reciente
4. Ingresar razón: "Información incompleta en sección técnica"
5. Confirmar rechazo
6. Verificar que:
   - El reporte cambie a estado "rejected"
   - Se guarde la razón en metadata
   - Se establezca `rejected_at`

**Resultado Esperado**: ✅ Reporte se rechaza correctamente

---

### Escenario 6: Intentar Rechazar Borrador

**Pasos**:
1. Iniciar sesión como `test_supervisor` / `test123`
2. Ir a `/reports/`
3. Buscar reporte en estado "draft"
4. Verificar que NO aparezca botón "Rechazar"

**Resultado Esperado**: ✅ No se puede rechazar un borrador

---

### Escenario 7: Intentar Rechazar Aprobado

**Pasos**:
1. Iniciar sesión como `test_supervisor` / `test123`
2. Ir a `/reports/`
3. Buscar reporte en estado "approved"
4. Si aparece botón "Rechazar", intentar rechazarlo
5. Verificar que muestre error

**Resultado Esperado**: ✅ No se puede rechazar un reporte ya aprobado

---

### Escenario 8: Permisos ABAC

**Pasos**:
1. Iniciar sesión como `test_tecnico` / `test123`
2. Ir a `/projects/`
3. Verificar que:
   - NO aparezca botón "Crear Proyecto"
   - NO aparezca botón "Editar"
   - SÍ aparezca botón "Ver"
4. Ir a `/reports/approvals/`
5. Verificar que NO aparezcan botones "Aprobar" o "Rechazar"

**Resultado Esperado**: ✅ Permisos se respetan correctamente

---

## 🔗 URLs de Prueba

| URL | Descripción |
|-----|-------------|
| `/projects/` | Lista de proyectos |
| `/projects/create/` | Crear nuevo proyecto |
| `/projects/{id}/` | Detalle de proyecto |
| `/projects/{id}/edit/` | Editar proyecto |
| `/reports/` | Lista de reportes |
| `/reports/{id}/` | Detalle de reporte |
| `/reports/approvals/` | Reportes pendientes de aprobación |

---

## 🧹 Limpiar Datos de Prueba

### Opción 1: Usar flag --clear

```powershell
python manage.py generate_test_data_p0 --clear
```

### Opción 2: Eliminar manualmente

```python
# En Django shell
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

Proyecto.objects.filter(name__startswith="[TEST P0]").delete()
ReporteSemanal.objects.filter(project_name__startswith="[TEST P0]").delete()
```

---

## 📝 Notas

- Los datos de prueba se identifican con el prefijo `[TEST P0]` en el nombre
- Los usuarios de prueba tienen la contraseña `test123`
- Si los usuarios ya existen, se actualizarán sus perfiles pero no se cambiarán las contraseñas
- Los proyectos y reportes se crean asociados a la primera Company y Sitec encontrados
- Si no existe Company/Sitec, ejecutar primero: `python manage.py seed_sitec`

---

**Última actualización**: 2026-01-23
