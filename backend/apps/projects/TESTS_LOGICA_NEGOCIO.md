# Tests Estrictos de Lógica de Negocio - Sistema de Seguimiento de Proyectos

**Fecha:** 2026-01-26  
**Auditor:** Sistema de Auditoría Automatizada  
**Versión:** 1.0

## Descripción

Este documento describe los tests estrictos que validan la lógica de negocio del sistema de seguimiento de proyectos. Cada test valida una regla específica y **FALLA** ante cualquier inconsistencia.

### Reglas de Auditoría

- ✅ No asumir comportamientos implícitos
- ✅ Ante cualquier inconsistencia, el test debe fallar
- ✅ No permitir estados inválidos o intermedios no documentados

---

## Tests de Coherencia entre Estados de Proyecto y Tareas

### Test 1: Proyecto Completado debe tener todas las tareas completadas

**Nombre del test:** `test_01_proyecto_completed_debe_tener_todas_tareas_completed`

**Entidad evaluada:** `Proyecto`, `Tarea`

**Regla de negocio exacta:** 
Si un proyecto está en estado `"completed"`, **TODAS** sus tareas deben estar en estado `"completed"`. Si hay alguna tarea con estado `"pending"`, `"in_progress"` o `"blocked"`, el proyecto **NO puede estar completado**.

**Condición de fallo:** 
Proyecto con `status="completed"` tiene al menos una tarea con estado diferente a `"completed"`.

**Severidad:** 🔴 **Crítica**

---

### Test 2: Proyecto Cancelado debe mantener estado de tareas

**Nombre del test:** `test_02_proyecto_cancelled_debe_mantener_estado_tareas`

**Entidad evaluada:** `Proyecto`, `Tarea`

**Regla de negocio exacta:** 
Si un proyecto está en estado `"cancelled"`, las tareas pueden mantener su estado actual (no se completan automáticamente). Sin embargo, **no se pueden crear nuevas tareas** ni **cambiar el estado de tareas existentes** en un proyecto cancelado.

**Condición de fallo:** 
Se pueden crear o modificar tareas en un proyecto con `status="cancelled"`.

**Severidad:** 🟠 **Alta**

---

### Test 3: Proyecto en Pausa no debe permitir nuevas tareas en progreso

**Nombre del test:** `test_03_proyecto_on_hold_no_debe_permitir_nuevas_tareas_in_progress`

**Entidad evaluada:** `Proyecto`, `Tarea`

**Regla de negocio exacta:** 
Si un proyecto está en estado `"on_hold"`, no se deben poder iniciar nuevas tareas (cambiar a `"in_progress"`). Las tareas existentes pueden mantenerse en su estado actual.

**Condición de fallo:** 
Se puede cambiar una tarea a `"in_progress"` cuando el proyecto tiene `status="on_hold"`.

**Severidad:** 🟡 **Media**

---

## Tests de Reglas de Transición de Estados

### Test 4: Transición de Planning a In Progress requiere Project Manager

**Nombre del test:** `test_04_transicion_planning_a_in_progress_requiere_project_manager`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto solo puede transicionar de `"planning"` a `"in_progress"` si tiene un `project_manager` asignado. Sin `project_manager`, debe permanecer en `"planning"`.

**Condición de fallo:** 
Proyecto con `project_manager=None` puede cambiar a `status="in_progress"`.

**Severidad:** 🔴 **Crítica**

---

### Test 5: Transición a Completed requiere progress_pct = 100

**Nombre del test:** `test_05_transicion_completed_requiere_progress_100`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto solo puede estar en estado `"completed"` si `progress_pct = 100`. Si `progress_pct < 100`, no puede estar completado (a menos que se use el endpoint `/complete/` que establece ambos simultáneamente).

**Condición de fallo:** 
Proyecto con `status="completed"` tiene `progress_pct < 100` (sin usar endpoint `/complete/`).

**Severidad:** 🔴 **Crítica**

---

### Test 6: Transición a Cancelled no permite volver a otros estados

**Nombre del test:** `test_06_transicion_cancelled_no_permite_volver_a_otros_estados`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto en estado `"cancelled"` **NO puede cambiar a ningún otro estado** (`"planning"`, `"in_progress"`, `"on_hold"`, `"completed"`). El estado `"cancelled"` es **terminal e irreversible**.

**Condición de fallo:** 
Proyecto con `status="cancelled"` puede cambiar a cualquier otro estado.

**Severidad:** 🔴 **Crítica**

---

### Test 7: Transición a Completed no permite volver a otros estados

**Nombre del test:** `test_07_transicion_completed_no_permite_volver_a_otros_estados`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto en estado `"completed"` **NO puede cambiar a ningún otro estado** excepto quizás `"cancelled"` (depende de reglas específicas). El estado `"completed"` es **terminal**.

**Condición de fallo:** 
Proyecto con `status="completed"` puede cambiar a `"planning"`, `"in_progress"` o `"on_hold"`.

**Severidad:** 🟠 **Alta**

---

### Test 8: Transición a On Hold requiere razón o metadata

**Nombre del test:** `test_08_transicion_on_hold_requiere_razon_o_metadata`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto solo puede cambiar a `"on_hold"` si se proporciona una razón en `metadata` o campo específico. No se puede pausar sin justificación documentada.

**Condición de fallo:** 
Proyecto puede cambiar a `status="on_hold"` sin razón documentada en `metadata`.

**Severidad:** 🟡 **Media**

---

## Tests de Cálculo Correcto del Avance

### Test 9: progress_pct debe estar entre 0 y 100

**Nombre del test:** `test_09_progress_pct_debe_estar_entre_0_y_100`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
El campo `progress_pct` **DEBE estar siempre entre 0 y 100 (inclusive)**. Valores fuera de este rango son inválidos y deben ser rechazados por el sistema.

**Condición de fallo:** 
Proyecto tiene `progress_pct < 0` o `progress_pct > 100`.

**Severidad:** 🔴 **Crítica**

---

### Test 10: progress_pct de proyecto completed debe ser 100

**Nombre del test:** `test_10_progress_pct_completed_debe_ser_100`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto tiene `status="completed"`, `progress_pct` **DEBE ser exactamente 100**. No puede haber proyecto completado con `progress_pct < 100`.

**Condición de fallo:** 
Proyecto con `status="completed"` tiene `progress_pct != 100`.

**Severidad:** 🔴 **Crítica**

---

### Test 11: progress_pct de proyecto planning debe ser 0

**Nombre del test:** `test_11_progress_pct_planning_debe_ser_0`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto tiene `status="planning"`, `progress_pct` **DEBE ser 0**. Un proyecto en planificación no puede tener avance.

**Condición de fallo:** 
Proyecto con `status="planning"` tiene `progress_pct > 0`.

**Severidad:** 🟠 **Alta**

---

### Test 12: progress_pct debe ser coherente con tareas completadas

**Nombre del test:** `test_12_progress_pct_debe_ser_coherente_con_tareas_completadas`

**Entidad evaluada:** `Proyecto`, `Tarea`

**Regla de negocio exacta:** 
El `progress_pct` del proyecto **DEBE reflejar el porcentaje de tareas completadas**. Si hay 10 tareas y 7 están completadas, `progress_pct` debe ser aproximadamente 70% (puede haber redondeo de ±1%).

**Condición de fallo:** 
`progress_pct` no coincide con el porcentaje de tareas completadas (diferencia > 1%).

**Severidad:** 🔴 **Crítica**

---

## Tests de Dependencias entre Tareas

### Test 13: Tarea no puede iniciarse si dependencias no completadas

**Nombre del test:** `test_13_tarea_no_puede_iniciarse_si_dependencias_no_completadas`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Si una tarea tiene dependencias (tareas que deben completarse antes), **NO puede cambiar a `"in_progress"`** hasta que todas sus dependencias estén `"completed"`. Si no hay campo de dependencias en el modelo, este test verifica que el sistema no permite estados inconsistentes.

**Condición de fallo:** 
Tarea puede cambiar a `status="in_progress"` cuando tiene dependencias con estado diferente a `"completed"`.

**Severidad:** 🟠 **Alta**

---

## Tests de Reglas de Cierre, Pausa y Cancelación

### Test 14: Proyecto completed debe tener completed_at

**Nombre del test:** `test_14_proyecto_completed_debe_tener_completed_at`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto tiene `status="completed"`, el campo `completed_at` **DEBE estar establecido (no puede ser None)**. Indica cuándo se completó el proyecto.

**Condición de fallo:** 
Proyecto con `status="completed"` tiene `completed_at=None`.

**Severidad:** 🔴 **Crítica**

---

### Test 15: Proyecto cancelled no debe tener completed_at

**Nombre del test:** `test_15_proyecto_cancelled_no_debe_tener_completed_at`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto tiene `status="cancelled"`, el campo `completed_at` **DEBE ser None**. Un proyecto cancelado no se completó.

**Condición de fallo:** 
Proyecto con `status="cancelled"` tiene `completed_at` establecido (no es None).

**Severidad:** 🟠 **Alta**

---

### Test 16: Proyecto on_hold no debe avanzar progress

**Nombre del test:** `test_16_proyecto_on_hold_no_debe_avanzar_progress`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto está en estado `"on_hold"`, el `progress_pct` **NO debe aumentar**. Un proyecto pausado no puede avanzar.

**Condición de fallo:** 
`progress_pct` aumenta mientras el proyecto tiene `status="on_hold"`.

**Severidad:** 🟡 **Media**

---

### Test 17: Proyecto cancelled debe tener progress 0 o mantener último valor

**Nombre del test:** `test_17_proyecto_cancelled_debe_tener_progress_0_o_mantener_ultimo`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto está en estado `"cancelled"`, el `progress_pct` puede ser 0 (si se cancela antes de iniciar) o mantener el último valor (si se cancela durante ejecución). Debe ser **consistente** según la regla de negocio específica.

**Condición de fallo:** 
`progress_pct` de proyecto cancelado es inconsistente (no es 0 ni mantiene último valor según regla).

**Severidad:** 🟡 **Media**

---

## Tests de Reglas de Asignación y Reasignación

### Test 18: Proyecto debe tener project_manager para in_progress

**Nombre del test:** `test_18_proyecto_debe_tener_project_manager_para_in_progress`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto **NO puede estar en estado `"in_progress"` sin un `project_manager` asignado**. El `project_manager` es obligatorio para proyectos en ejecución.

**Condición de fallo:** 
Proyecto con `status="in_progress"` tiene `project_manager=None`.

**Severidad:** 🔴 **Crítica**

---

### Test 19: Reasignación de project_manager debe mantener estado válido

**Nombre del test:** `test_19_reasignacion_project_manager_debe_mantener_estado_valido`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si se reasigna el `project_manager` de un proyecto en `"in_progress"`, el proyecto debe mantener su estado o cambiar a `"planning"` si el nuevo PM no está disponible. No puede quedar en estado inválido.

**Condición de fallo:** 
Reasignación de `project_manager` deja proyecto en estado inconsistente (sin PM en `in_progress`).

**Severidad:** 🟠 **Alta**

---

### Test 20: Tarea completed debe tener completed_at

**Nombre del test:** `test_20_tarea_completed_debe_tener_completed_at`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Si una tarea tiene `status="completed"`, el campo `completed_at` **DEBE estar establecido (no puede ser None)**. Indica cuándo se completó la tarea.

**Condición de fallo:** 
Tarea con `status="completed"` tiene `completed_at=None`.

**Severidad:** 🔴 **Crítica**

---

### Test 21: Tarea pending no debe tener completed_at

**Nombre del test:** `test_21_tarea_pending_no_debe_tener_completed_at`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Si una tarea tiene `status="pending"` o `"in_progress"`, el campo `completed_at` **DEBE ser None**. Solo tareas completadas tienen `completed_at`.

**Condición de fallo:** 
Tarea con `status="pending"` o `"in_progress"` tiene `completed_at` establecido (no es None).

**Severidad:** 🟠 **Alta**

---

### Test 22: Reasignación de tarea debe mantener estado válido

**Nombre del test:** `test_22_reasignacion_tarea_debe_mantener_estado_valido`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Si se reasigna una tarea a otro usuario, el estado de la tarea debe mantenerse válido. Una tarea `"completed"` **no puede cambiar a otro estado** al reasignarse.

**Condición de fallo:** 
Reasignación de tarea cambia estado inválidamente (tarea completada cambia a otro estado).

**Severidad:** 🟡 **Media**

---

### Test 23: Tarea blocked no puede cambiar a completed directamente

**Nombre del test:** `test_23_tarea_blocked_no_puede_cambiar_a_completed_directamente`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Una tarea en estado `"blocked"` **NO puede cambiar directamente a `"completed"`**. Debe pasar primero por `"pending"` o `"in_progress"` para desbloquearse.

**Condición de fallo:** 
Tarea con `status="blocked"` puede cambiar directamente a `status="completed"`.

**Severidad:** 🟠 **Alta**

---

## Tests de Validación de Fechas

### Test 24: end_date debe ser posterior a start_date

**Nombre del test:** `test_24_end_date_debe_ser_posterior_a_start_date`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Si un proyecto tiene `end_date` establecido, **DEBE ser posterior a `start_date`**. No puede haber `end_date` anterior o igual a `start_date`.

**Condición de fallo:** 
Proyecto tiene `end_date <= start_date`.

**Severidad:** 🔴 **Crítica**

---

### Test 25: due_date de tarea debe ser válida

**Nombre del test:** `test_25_due_date_tarea_debe_ser_valida`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Si una tarea tiene `due_date` establecido, debe ser una fecha válida y coherente con el proyecto. **No puede ser anterior a `start_date` del proyecto**.

**Condición de fallo:** 
Tarea tiene `due_date` anterior a `start_date` del proyecto.

**Severidad:** 🟡 **Media**

---

## Tests de Integridad de Datos

### Test 26: Proyecto debe pertenecer a company y sitec

**Nombre del test:** `test_26_proyecto_debe_pertenecer_a_company_y_sitec`

**Entidad evaluada:** `Proyecto`

**Regla de negocio exacta:** 
Un proyecto **SIEMPRE debe tener `company` y `sitec` asignados**. No puede existir un proyecto sin `company` o sin `sitec`. Además, el `sitec` debe pertenecer a la misma `company` del proyecto.

**Condición de fallo:** 
Proyecto tiene `company=None`, `sitec=None`, o `sitec.company != proyecto.company`.

**Severidad:** 🔴 **Crítica**

---

### Test 27: Tarea debe pertenecer a proyecto

**Nombre del test:** `test_27_tarea_debe_pertenecer_a_proyecto`

**Entidad evaluada:** `Tarea`

**Regla de negocio exacta:** 
Una tarea **SIEMPRE debe tener un `project` asignado**. No puede existir una tarea sin proyecto.

**Condición de fallo:** 
Tarea tiene `project=None`.

**Severidad:** 🔴 **Crítica**

---

## Resumen de Tests

| Categoría | Cantidad | Severidad Crítica | Severidad Alta | Severidad Media |
|-----------|----------|-------------------|----------------|-----------------|
| Coherencia Estados | 3 | 1 | 1 | 1 |
| Transición Estados | 5 | 3 | 1 | 1 |
| Cálculo Avance | 4 | 3 | 1 | 0 |
| Dependencias | 1 | 0 | 1 | 0 |
| Cierre/Pausa/Cancelación | 4 | 1 | 1 | 2 |
| Asignación/Reasignación | 6 | 1 | 2 | 3 |
| Validación Fechas | 2 | 1 | 0 | 1 |
| Integridad Datos | 2 | 2 | 0 | 0 |
| **TOTAL** | **27** | **12** | **7** | **8** |

---

## Ejecución de Tests

Para ejecutar los tests de lógica de negocio:

```bash
# Activar entorno virtual
cd g:\SeguimientoProyectos
.\.venv\Scripts\Activate.ps1

# Ejecutar tests
cd backend
python manage.py test apps.projects.tests_business_logic --verbosity=2
```

---

## Notas Importantes

1. **Tests Estrictos**: Estos tests están diseñados para **FALLAR** ante cualquier inconsistencia. No asumen comportamientos implícitos.

2. **Estados Terminales**: Los estados `"completed"` y `"cancelled"` son terminales y no deben permitir transiciones a otros estados.

3. **Coherencia de Datos**: Todos los campos relacionados deben ser coherentes (ej: `completed_at` solo para proyectos/tareas completadas).

4. **Validaciones de Negocio**: Las validaciones deben aplicarse tanto en el modelo como en los serializers y views.

5. **Integridad Referencial**: Las relaciones entre entidades deben mantenerse siempre válidas.

---

**Última actualización:** 2026-01-26
