# Validación P0 - Pruebas de Pendientes Críticos

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 📋 Resumen

Este documento describe las pruebas realizadas para validar la implementación de los pendientes críticos (P0): navegación frontend y endpoint de rechazo de reportes.

---

## ✅ Tests Automatizados Creados

### 1. Tests de Vistas Frontend

**Archivo**: `backend/apps/frontend/tests_p0_navigation.py`

**Tests Incluidos**:
- ✅ `test_project_detail_page_renders` - Verifica que la vista de detalle de proyecto renderiza
- ✅ `test_project_detail_requires_authentication` - Verifica que requiere autenticación
- ✅ `test_project_detail_with_invalid_id` - Verifica manejo de ID inválido
- ✅ `test_project_edit_page_renders` - Verifica que la vista de edición renderiza
- ✅ `test_project_edit_requires_authentication` - Verifica que requiere autenticación
- ✅ `test_project_create_page_renders` - Verifica que la vista de creación renderiza
- ✅ `test_project_create_requires_authentication` - Verifica que requiere autenticación
- ✅ `test_report_detail_page_renders` - Verifica que la vista de detalle de reporte renderiza
- ✅ `test_report_detail_requires_authentication` - Verifica que requiere autenticación
- ✅ `test_report_detail_with_invalid_id` - Verifica manejo de ID inválido

**Total**: 10 tests

---

### 2. Tests de Endpoint de Rechazo

**Archivo**: `backend/apps/reports/tests_reject.py`

**Tests Incluidos**:
- ✅ `test_supervisor_can_reject_report` - Supervisor puede rechazar
- ✅ `test_pm_can_reject_report` - PM puede rechazar
- ✅ `test_cannot_reject_draft_report` - No se puede rechazar borrador
- ✅ `test_cannot_reject_already_approved_report` - No se puede rechazar aprobado
- ✅ `test_reject_without_reason` - Puede rechazar sin razón
- ✅ `test_reject_sets_timestamp` - Establece rejected_at
- ✅ `test_reject_requires_authentication` - Requiere autenticación
- ✅ `test_technician_cannot_reject` - Técnico no puede rechazar

**Total**: 8 tests

---

## 🧪 Ejecutar Tests

### Activar Entorno Virtual

```powershell
cd G:\SeguimientoProyectos\backend
.venv\Scripts\Activate.ps1
```

### Ejecutar Tests de Navegación

```bash
python manage.py test apps.frontend.tests_p0_navigation --verbosity=2
```

### Ejecutar Tests de Rechazo

```bash
python manage.py test apps.reports.tests_reject --verbosity=2
```

### Ejecutar Todos los Tests P0

```bash
python manage.py test apps.frontend.tests_p0_navigation apps.reports.tests_reject --verbosity=2
```

---

## 📊 Resultados Esperados

### Tests de Navegación (10 tests)

```
test_project_detail_page_renders ... ok
test_project_detail_requires_authentication ... ok
test_project_detail_with_invalid_id ... ok
test_project_edit_page_renders ... ok
test_project_edit_requires_authentication ... ok
test_project_create_page_renders ... ok
test_project_create_requires_authentication ... ok
test_report_detail_page_renders ... ok
test_report_detail_requires_authentication ... ok
test_report_detail_with_invalid_id ... ok

----------------------------------------------------------------------
Ran 10 tests in X.XXXs

OK
```

### Tests de Rechazo (8 tests)

```
test_supervisor_can_reject_report ... ok
test_pm_can_reject_report ... ok
test_cannot_reject_draft_report ... ok
test_cannot_reject_already_approved_report ... ok
test_reject_without_reason ... ok
test_reject_sets_timestamp ... ok
test_reject_requires_authentication ... ok
test_technician_cannot_reject ... ok

----------------------------------------------------------------------
Ran 8 tests in X.XXXs

OK
```

---

## 🔍 Pruebas Manuales Recomendadas

### 1. Navegación a Detalle de Proyecto

**Pasos**:
1. Iniciar sesión como PM o Admin
2. Ir a `/projects/`
3. Hacer clic en "Ver" de un proyecto
4. Verificar que se muestre:
   - Nombre del proyecto
   - Código
   - Descripción
   - Fechas
   - Presupuesto
   - Botón "Editar" (si tiene permisos)
   - Botón "Volver"

**Resultado Esperado**: ✅ Página carga correctamente con toda la información

---

### 2. Navegación a Detalle de Reporte

**Pasos**:
1. Iniciar sesión como cualquier usuario
2. Ir a `/reports/` o `/reports/approvals/`
3. Hacer clic en "Ver" de un reporte
4. Verificar que se muestre:
   - Nombre del proyecto
   - Semana
   - Información general
   - Datos técnicos
   - Incidentes (si hay)
   - Fechas
   - Botón "Volver"

**Resultado Esperado**: ✅ Página carga correctamente con toda la información

---

### 3. Edición de Proyecto

**Pasos**:
1. Iniciar sesión como PM o Admin
2. Ir a `/projects/`
3. Hacer clic en "Editar" de un proyecto
4. Verificar que el formulario esté pre-cargado
5. Modificar algunos campos
6. Guardar cambios
7. Verificar que se redirija a detalle y los cambios se reflejen

**Resultado Esperado**: ✅ Formulario funciona correctamente, guarda y redirige

---

### 4. Creación de Proyecto

**Pasos**:
1. Iniciar sesión como PM o Admin
2. Ir a `/projects/`
3. Hacer clic en "Crear Proyecto"
4. Completar formulario con datos válidos
5. Crear proyecto
6. Verificar que se redirija a detalle del nuevo proyecto

**Resultado Esperado**: ✅ Proyecto se crea correctamente y se redirige a detalle

---

### 5. Rechazo de Reporte

**Pasos**:
1. Iniciar sesión como Supervisor, PM o Admin
2. Ir a `/reports/approvals/`
3. Hacer clic en "Rechazar" de un reporte enviado
4. Ingresar razón de rechazo (opcional)
5. Confirmar rechazo
6. Verificar que:
   - El reporte cambie a estado "rejected"
   - Se guarde la razón en metadata
   - Se establezca rejected_at

**Resultado Esperado**: ✅ Reporte se rechaza correctamente con todos los datos

---

### 6. Permisos ABAC

**Pasos**:
1. Iniciar sesión como Técnico
2. Ir a `/projects/`
3. Verificar que NO aparezca botón "Crear Proyecto"
4. Verificar que NO aparezca botón "Editar"
5. Verificar que SÍ aparezca botón "Ver"

**Resultado Esperado**: ✅ Permisos se respetan correctamente

---

## 📝 Checklist de Validación

### Funcionalidad
- [ ] Vista de detalle de proyecto funciona
- [ ] Vista de detalle de reporte funciona
- [ ] Vista de edición de proyecto funciona
- [ ] Vista de creación de proyecto funciona
- [ ] Endpoint de rechazo funciona

### Navegación
- [ ] Botones "Ver" navegan correctamente
- [ ] Botones "Editar" navegan correctamente
- [ ] Botón "Crear Proyecto" navega correctamente
- [ ] Botón "Rechazar" funciona correctamente
- [ ] Botones "Volver" funcionan correctamente

### Permisos
- [ ] Solo usuarios con permisos ven botones de acción
- [ ] Solo usuarios autorizados pueden editar/crear
- [ ] Solo usuarios autorizados pueden rechazar

### UI/UX
- [ ] Skeleton screens aparecen mientras carga
- [ ] Mensajes de error son claros
- [ ] Mensajes de éxito aparecen
- [ ] Formularios tienen validación

---

## 🐛 Problemas Conocidos / Pendientes

### Mejoras Futuras (No Críticas)

1. **Confirmaciones Elegantes**: Reemplazar `confirm()` y `prompt()` con modales
2. **Tooltips**: Agregar tooltips a botones
3. **Validación Mejorada**: Validación más robusta en frontend
4. **Mensajes de Error**: Mejorar mensajes de error del backend

---

## ✅ Conclusión

Se han creado **18 tests automatizados** (10 de navegación + 8 de rechazo) para validar la implementación de los pendientes críticos (P0).

**Próximo Paso**: Ejecutar los tests y realizar pruebas manuales según el checklist.

---

**Última actualización**: 2026-01-23
