# Plan de Acción: Rediseño Frontend SITEC

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: 🚀 Listo para Ejecución

---

## 📋 Resumen Ejecutivo

Este documento complementa el **Diagnóstico y Planeación** (`DIAGNOSTICO_REDISEÑO_FRONTEND.md`) con un plan de acción ejecutable, dividido en tareas concretas con estimaciones, dependencias y criterios de aceptación.

**Tiempo estimado total**: 5 semanas  
**Prioridad**: Alta  
**Riesgo**: Medio

---

## 🎯 Objetivos del Rediseño

1. ✅ Personalizar interfaz según perfil de usuario
2. ✅ Reducir sobrecarga cognitiva (menos información visible)
3. ✅ Mejorar navegación y organización
4. ✅ Mantener compatibilidad con funcionalidad existente
5. ✅ Mejorar experiencia de usuario general

---

## 📅 Cronograma de Implementación

### Fase 1: Preparación y Base (Semana 1)
**Duración**: 5 días  
**Prioridad**: Crítica

#### Día 1-2: Infraestructura Backend
- [ ] **Tarea 1.1**: Crear endpoint `/api/user/context/`
  - **Archivo**: `backend/apps/accounts/views.py`
  - **Estimación**: 4 horas
  - **Criterios**: Devuelve contexto completo con permisos y UI config
  - **Tests**: `backend/apps/accounts/tests_context.py`

- [ ] **Tarea 1.2**: Crear middleware de contexto frontend
  - **Archivo**: `backend/apps/frontend/middleware.py`
  - **Estimación**: 3 horas
  - **Criterios**: Agrega `user_context` a `request` para usuarios autenticados
  - **Tests**: Integración con views

- [ ] **Tarea 1.3**: Crear template tags para roles
  - **Archivo**: `backend/apps/frontend/templatetags/role_tags.py`
  - **Estimación**: 4 horas
  - **Criterios**: Tags `show_for_role`, `dashboard_section`, `has_permission`
  - **Tests**: Tests de template tags

#### Día 3-4: Infraestructura Frontend
- [ ] **Tarea 1.4**: Crear `role-based-ui.js`
  - **Archivo**: `backend/static/frontend/js/role-based-ui.js`
  - **Estimación**: 6 horas
  - **Funcionalidad**:
    - `getUserContext()`: Obtiene contexto del usuario
    - `showForRole(element, roles)`: Muestra/oculta elementos por rol
    - `initializeRoleBasedUI()`: Inicializa UI según rol
  - **Tests**: Tests unitarios en JS

- [ ] **Tarea 1.5**: Crear sistema de navegación base
  - **Archivo**: `backend/static/frontend/js/navigation.js`
  - **Estimación**: 5 horas
  - **Funcionalidad**:
    - `NavigationManager`: Gestiona navegación principal
    - `showNavigationForRole(role)`: Muestra solo navegación permitida
    - `navigateToSection(section)`: Navega a sección
  - **Tests**: Tests de navegación

#### Día 5: Testing y Validación
- [ ] **Tarea 1.6**: Tests unitarios e integración
  - **Estimación**: 4 horas
  - **Criterios**: > 80% cobertura, todos los tests pasando

- [ ] **Tarea 1.7**: Documentación Fase 1
  - **Estimación**: 2 horas
  - **Entregable**: Documentación de API y uso de componentes

**Total Fase 1**: ~28 horas

---

### Fase 2: Dashboard Personalizado (Semana 2)
**Duración**: 5 días  
**Prioridad**: Alta

#### Día 1-2: Templates de Dashboard
- [ ] **Tarea 2.1**: Crear `dashboard/admin.html`
  - **Estimación**: 3 horas
  - **Contenido**: Todos los paneles (KPIs, ROI, tendencias, comparativos, proyectos, reportes)
  - **Criterios**: Renderiza correctamente, todos los componentes funcionan

- [ ] **Tarea 2.2**: Crear `dashboard/pm.html`
  - **Estimación**: 3 horas
  - **Contenido**: KPIs, ROI, tendencias, comparativos, proyectos, reportes (sin configuración)
  - **Criterios**: Renderiza correctamente, sin secciones de admin

- [ ] **Tarea 2.3**: Crear `dashboard/supervisor.html`
  - **Estimación**: 3 horas
  - **Contenido**: Dashboard básico (proyectos supervisados, alertas, reportes pendientes)
  - **Criterios**: Solo muestra información relevante para supervisor

- [ ] **Tarea 2.4**: Crear `dashboard/tecnico.html`
  - **Estimación**: 3 horas
  - **Contenido**: Dashboard operativo (proyectos asignados, reportes recientes, tareas)
  - **Criterios**: Enfoque en operación, sin métricas gerenciales

- [ ] **Tarea 2.5**: Crear `dashboard/cliente.html`
  - **Estimación**: 3 horas
  - **Contenido**: Vista cliente (estado de proyectos, documentos disponibles)
  - **Criterios**: Solo lectura, sin opciones de edición

#### Día 3-4: JavaScript Específico
- [ ] **Tarea 2.6**: Crear `dashboard/dashboard-admin.js`
  - **Estimación**: 4 horas
  - **Funcionalidad**: Lógica específica para admin (exportar, configurar, etc.)

- [ ] **Tarea 2.7**: Crear `dashboard/dashboard-pm.js`
  - **Estimación**: 4 horas
  - **Funcionalidad**: Lógica para PM (filtros, análisis, etc.)

- [ ] **Tarea 2.8**: Crear `dashboard/dashboard-supervisor.js`
  - **Estimación**: 3 horas
  - **Funcionalidad**: Lógica para supervisor (aprobaciones, alertas)

- [ ] **Tarea 2.9**: Crear `dashboard/dashboard-tecnico.js`
  - **Estimación**: 3 horas
  - **Funcionalidad**: Lógica para técnico (tareas, reportes rápidos)

- [ ] **Tarea 2.10**: Crear `dashboard/dashboard-cliente.js`
  - **Estimación**: 2 horas
  - **Funcionalidad**: Lógica para cliente (solo lectura, descargas)

#### Día 5: Integración y Testing
- [ ] **Tarea 2.11**: Crear vista que redirige según rol
  - **Archivo**: `backend/apps/frontend/views.py`
  - **Estimación**: 3 horas
  - **Funcionalidad**: `DashboardView` que renderiza template correcto según rol

- [ ] **Tarea 2.12**: Tests de integración por dashboard
  - **Estimación**: 4 horas
  - **Criterios**: Cada dashboard renderiza correctamente, muestra solo contenido permitido

- [ ] **Tarea 2.13**: Migrar lógica de `dashboard.js` existente
  - **Estimación**: 4 horas
  - **Criterios**: Funcionalidad existente se mantiene en nuevos dashboards

**Total Fase 2**: ~40 horas

---

### Fase 3: Navegación y Estructura (Semana 3)
**Duración**: 5 días  
**Prioridad**: Alta

#### Día 1-2: Actualizar Base Template
- [ ] **Tarea 3.1**: Actualizar `base.html` con navegación principal
  - **Estimación**: 4 horas
  - **Cambios**:
    - Agregar barra de navegación superior
    - Integrar `navigation.js`
    - Agregar indicador de perfil
  - **Criterios**: Navegación visible y funcional

- [ ] **Tarea 3.2**: Implementar sistema de rutas frontend
  - **Archivo**: `backend/static/frontend/js/routing.js`
  - **Estimación**: 5 horas
  - **Funcionalidad**: Router simple para SPA-like navigation
  - **Criterios**: Navegación sin recargar página (opcional, puede ser tradicional)

#### Día 3-4: Crear Vistas de Secciones
- [ ] **Tarea 3.3**: Crear vista de Proyectos
  - **Archivo**: `backend/apps/frontend/templates/frontend/projects/list.html`
  - **Estimación**: 4 horas
  - **Funcionalidad**: Lista de proyectos con filtros según rol

- [ ] **Tarea 3.4**: Crear vista de Reportes
  - **Archivo**: `backend/apps/frontend/templates/frontend/reports/list.html`
  - **Estimación**: 4 horas
  - **Funcionalidad**: Lista de reportes con acciones según rol

- [ ] **Tarea 3.5**: Crear vista de Aprobaciones (supervisor/pm)
  - **Archivo**: `backend/apps/frontend/templates/frontend/reports/approvals.html`
  - **Estimación**: 4 horas
  - **Funcionalidad**: Lista de reportes pendientes de aprobación

- [ ] **Tarea 3.6**: Crear vista de Documentos
  - **Archivo**: `backend/apps/frontend/templates/frontend/documents/list.html`
  - **Estimación**: 3 horas
  - **Funcionalidad**: Lista de documentos disponibles

#### Día 5: Integración y Migración
- [ ] **Tarea 3.7**: Migrar contenido de `dashboard.html` actual
  - **Estimación**: 4 horas
  - **Criterios**: Contenido migrado sin pérdida de funcionalidad

- [ ] **Tarea 3.8**: Implementar lógica de visibilidad de navegación
  - **Estimación**: 3 horas
  - **Criterios**: Solo se muestran secciones permitidas por rol

- [ ] **Tarea 3.9**: Tests E2E de navegación
  - **Estimación**: 4 horas
  - **Criterios**: Flujos completos funcionan para cada perfil

**Total Fase 3**: ~35 horas

---

### Fase 4: Wizard Contextual (Semana 4)
**Duración**: 5 días  
**Prioridad**: Media

#### Día 1-2: Templates de Wizard
- [ ] **Tarea 4.1**: Crear `wizard/wizard_readonly.html`
  - **Estimación**: 4 horas
  - **Contenido**: Vista de solo lectura del wizard para clientes
  - **Criterios**: Sin opciones de edición, solo visualización

- [ ] **Tarea 4.2**: Refactorizar `wizard.html` para usar template tags
  - **Estimación**: 3 horas
  - **Criterios**: Componentes se muestran/ocultan según rol

#### Día 3-4: Lógica de Visibilidad
- [ ] **Tarea 4.3**: Adaptar `wizard.js` para respetar permisos
  - **Estimación**: 5 horas
  - **Cambios**:
    - Ocultar botones de guardar para clientes
    - Ocultar modo campo para no-técnicos
    - Ocultar chatbot para roles sin permisos
  - **Criterios**: Solo se muestran opciones permitidas

- [ ] **Tarea 4.4**: Implementar lógica de componentes avanzados
  - **Estimación**: 3 horas
  - **Criterios**: Risk matrix, Gantt, Kanban solo para roles permitidos

#### Día 5: Testing y Validación
- [ ] **Tarea 4.5**: Tests para wizard por rol
  - **Estimación**: 4 horas
  - **Criterios**: Cada rol ve solo opciones permitidas

- [ ] **Tarea 4.6**: Validación con usuarios reales
  - **Estimación**: 3 horas
  - **Criterios**: Feedback positivo de usuarios

**Total Fase 4**: ~22 horas

---

### Fase 5: Optimización y Refinamiento (Semana 5)
**Duración**: 5 días  
**Prioridad**: Baja

#### Día 1-2: Optimizaciones
- [ ] **Tarea 5.1**: Implementar lazy loading de componentes
  - **Estimación**: 4 horas
  - **Criterios**: Carga inicial más rápida

- [ ] **Tarea 5.2**: Optimizar carga de datos
  - **Estimación**: 3 horas
  - **Criterios**: Menos requests, mejor caching

- [ ] **Tarea 5.3**: Mejorar responsive design
  - **Estimación**: 4 horas
  - **Criterios**: Funciona bien en móvil y tablet

#### Día 3: Mejoras de UX
- [ ] **Tarea 5.4**: Agregar animaciones y transiciones
  - **Estimación**: 3 horas
  - **Criterios**: Transiciones suaves, sin lag

- [ ] **Tarea 5.5**: Mejorar feedback visual
  - **Estimación**: 2 horas
  - **Criterios**: Loading states, mensajes de error claros

#### Día 4-5: Documentación y Validación
- [ ] **Tarea 5.6**: Crear guías de usuario por perfil
  - **Estimación**: 6 horas
  - **Entregables**: 5 guías (una por perfil)

- [ ] **Tarea 5.7**: Documentación técnica
  - **Estimación**: 4 horas
  - **Entregables**: Arquitectura, componentes, navegación

- [ ] **Tarea 5.8**: Tests de rendimiento
  - **Estimación**: 3 horas
  - **Criterios**: Performance igual o mejor que antes

- [ ] **Tarea 5.9**: Validación final con usuarios
  - **Estimación**: 4 horas
  - **Criterios**: Satisfacción > 80%

**Total Fase 5**: ~33 horas

---

## 📊 Resumen de Esfuerzo

| Fase | Horas | Días | Prioridad |
|------|-------|------|-----------|
| Fase 1: Preparación | 28h | 5 | Crítica |
| Fase 2: Dashboard | 40h | 5 | Alta |
| Fase 3: Navegación | 35h | 5 | Alta |
| Fase 4: Wizard | 22h | 5 | Media |
| Fase 5: Optimización | 33h | 5 | Baja |
| **TOTAL** | **158h** | **25 días** | - |

**Tiempo estimado**: 5 semanas (1 desarrollador full-time)  
**Tiempo con 2 desarrolladores**: 2.5 semanas

---

## 🔄 Dependencias entre Tareas

```
Fase 1 (Infraestructura)
  ↓
Fase 2 (Dashboard) ──┐
  ↓                   │
Fase 3 (Navegación) ──┼──→ Fase 5 (Optimización)
  ↓                   │
Fase 4 (Wizard) ──────┘
```

**Bloqueadores críticos**:
- Fase 2 depende de Fase 1 (endpoint de contexto)
- Fase 3 depende de Fase 1 (navegación base)
- Fase 4 puede empezar en paralelo con Fase 3
- Fase 5 depende de todas las anteriores

---

## ✅ Criterios de Aceptación Globales

### Funcionalidad
- [ ] Cada perfil ve solo contenido permitido
- [ ] Navegación funciona correctamente
- [ ] No hay regresiones en funcionalidad existente
- [ ] Permisos ABAC se respetan en frontend

### Performance
- [ ] Tiempo de carga < 2s para dashboard
- [ ] No hay degradación de performance
- [ ] Lazy loading funciona correctamente

### Usabilidad
- [ ] Navegación intuitiva
- [ ] Reducción de scroll necesario
- [ ] Feedback visual claro

### Calidad
- [ ] Cobertura de tests > 80%
- [ ] Documentación completa
- [ ] Code review aprobado

---

## 🚨 Plan de Rollback

Si algo sale mal durante la implementación:

1. **Feature Flags**: Mantener código antiguo activable con flags
2. **Branching**: Implementar en branch separado, merge solo cuando esté listo
3. **Rollback de BD**: No hay cambios de BD, solo frontend
4. **Cache**: Limpiar cache del navegador si hay problemas de renderizado

**Procedimiento de rollback**:
```bash
# 1. Revertir cambios en Git
git revert <commit-hash>

# 2. Limpiar cache estático
python manage.py collectstatic --clear

# 3. Reiniciar servidor
# (si es necesario)
```

---

## 📝 Notas de Implementación

### Mejores Prácticas
1. **Incremental**: Implementar cambios pequeños y probar frecuentemente
2. **Backward Compatible**: Mantener URLs y funcionalidad antigua funcionando
3. **Testing**: Escribir tests antes o durante implementación
4. **Documentation**: Documentar mientras se implementa

### Consideraciones Técnicas
- Usar template tags de Django para lógica de presentación
- JavaScript modular y reutilizable
- CSS organizado por componentes
- Mantener compatibilidad con navegadores modernos

### Consideraciones de Negocio
- Comunicar cambios a usuarios antes del release
- Proporcionar entrenamiento si es necesario
- Monitorear feedback y ajustar según necesidad

---

## 🎯 Próximos Pasos Inmediatos

1. **Revisar y aprobar este plan** con stakeholders
2. **Asignar recursos** (desarrolladores, tiempo)
3. **Crear issues/tickets** en sistema de gestión
4. **Configurar branch** para desarrollo
5. **Iniciar Fase 1** (Preparación y Base)

---

**Última actualización**: 2026-01-23  
**Autor**: Sistema de Planeación SITEC  
**Estado**: 🚀 Listo para Ejecución
