# Plan de Implementación Priorizado - SITEC

**Fecha**: 2026-01-23  
**Versión**: 2.0  
**Para**: Presentación Mesa Directiva  
**Última Actualización**: 2026-01-23

---

## 📋 Resumen Ejecutivo

Este documento presenta un plan de implementación detallado de los pendientes del sistema SITEC, organizado por prioridad y dependencias, con estimaciones de tiempo y recursos necesarios.

---

## 🎯 Matriz de Priorización

| Prioridad | Descripción | Impacto | Urgencia | Esfuerzo |
|-----------|-------------|---------|----------|----------|
| **P0 - Crítico** | Bloquea funcionalidad básica | Alto | Alta | 2-3 semanas |
| **P1 - Importante** | Mejora significativa | Alto | Media | 7-10 semanas |
| **P2 - Opcional** | Mejora incremental | Medio | Baja | 9-12 semanas |

---

## 📊 Estado Actual del Plan

### ✅ Completado (Actualizado 2026-01-23)

- ✅ **Navegación Básica P0**: Completada (Fases 1-5 del frontend)
- ✅ **MFA**: Backend + Frontend completados
- ✅ **Rate Limiting Avanzado**: Completado
- ✅ **Deployment**: Preparado para Render.com
- ✅ **Git/GitHub**: Organización completa

### ⏳ Pendiente

- ⏳ **Vistas de Detalle y Edición**: Pendiente (P0)
- ⏳ **Integraciones Externas**: Pendiente (P1 - requiere proveedores)
- ⏳ **WebAuthn**: Pendiente (P1)
- ⏳ **Go Live**: Pendiente (P1)

---

## 🔴 PRIORIDAD P0: Crítico (2-3 semanas)

### Objetivo
Completar navegación básica del frontend para que los usuarios puedan acceder a detalles y editar recursos.

### ✅ Completado Previamente

- ✅ Navegación por secciones (Dashboard, Proyectos, Reportes, Aprobaciones)
- ✅ UI basada en roles
- ✅ Filtros avanzados
- ✅ Wizard contextual

### Tareas Detalladas

#### 1. Vista de Detalle de Proyecto
**Esfuerzo**: 1 semana  
**Dependencias**: Ninguna  
**Archivos a Crear/Modificar**:
- `backend/apps/frontend/views.py` - Agregar `ProjectDetailView`
- `backend/apps/frontend/templates/frontend/projects/detail.html` - Template nuevo
- `backend/apps/frontend/urls.py` - Agregar ruta `/projects/<id>/`
- `backend/static/frontend/js/sections-projects.js` - Implementar navegación (línea 75)

**Criterios de Aceptación**:
- [ ] Usuario puede ver detalles completos del proyecto
- [ ] Información se carga desde API `/api/projects/proyectos/<id>/`
- [ ] Botón "Ver" en lista funciona correctamente
- [ ] Permisos ABAC se respetan (solo usuarios autorizados)

---

#### 2. Vista de Detalle de Reporte
**Esfuerzo**: 1 semana  
**Dependencias**: Ninguna  
**Archivos a Crear/Modificar**:
- `backend/apps/frontend/views.py` - Agregar `ReportDetailView`
- `backend/apps/frontend/templates/frontend/reports/detail.html` - Template nuevo
- `backend/apps/frontend/urls.py` - Agregar ruta `/reports/<id>/`
- `backend/static/frontend/js/sections-reports.js` - Implementar navegación
- `backend/static/frontend/js/sections-approvals.js` - Implementar navegación (línea 103)

**Criterios de Aceptación**:
- [ ] Usuario puede ver detalles completos del reporte
- [ ] Información se carga desde API `/api/reports/reportes/<id>/`
- [ ] Botones "Ver" en listas funcionan correctamente
- [ ] Permisos ABAC se respetan

---

#### 3. Vista de Edición de Proyecto
**Esfuerzo**: 1 semana  
**Dependencias**: Vista de detalle (opcional, puede ser independiente)  
**Archivos a Crear/Modificar**:
- `backend/apps/frontend/views.py` - Agregar `ProjectEditView`
- `backend/apps/frontend/templates/frontend/projects/edit.html` - Template nuevo
- `backend/apps/frontend/urls.py` - Agregar ruta `/projects/<id>/edit/`
- `backend/static/frontend/js/sections-projects.js` - Implementar navegación (línea 86)
- `backend/static/frontend/js/project-edit.js` - JavaScript para edición (nuevo)

**Criterios de Aceptación**:
- [ ] Usuario puede editar proyecto existente
- [ ] Formulario pre-cargado con datos actuales
- [ ] Validación en frontend y backend
- [ ] Botón "Editar" en lista funciona correctamente
- [ ] Permisos ABAC se respetan (solo PM, Admin pueden editar)

---

#### 4. Modal/Página de Creación de Proyecto
**Esfuerzo**: 1 semana  
**Dependencias**: Ninguna  
**Archivos a Crear/Modificar**:
- `backend/apps/frontend/views.py` - Agregar `ProjectCreateView`
- `backend/apps/frontend/templates/frontend/projects/create.html` - Template nuevo
- `backend/apps/frontend/urls.py` - Agregar ruta `/projects/create/`
- `backend/static/frontend/js/sections-projects.js` - Implementar creación (línea 213)
- `backend/static/frontend/js/project-create.js` - JavaScript para creación (nuevo)

**Criterios de Aceptación**:
- [ ] Usuario puede crear nuevo proyecto
- [ ] Formulario completo con validación
- [ ] Botón "Crear Proyecto" funciona correctamente
- [ ] Permisos ABAC se respetan (solo PM, Admin pueden crear)
- [ ] Redirección a detalle después de crear

---

#### 5. Endpoint de Rechazo de Reportes
**Esfuerzo**: 2 días  
**Dependencias**: Ninguna  
**Archivos a Crear/Modificar**:
- `backend/apps/reports/views.py` - Agregar método `reject()` o `ReportRejectView`
- `backend/apps/reports/urls.py` - Agregar ruta `POST /api/reports/reportes/<id>/reject/`
- `backend/static/frontend/js/sections-approvals.js` - Usar nuevo endpoint (línea 74)

**Criterios de Aceptación**:
- [ ] Endpoint acepta razón de rechazo
- [ ] Cambia estado del reporte a "rejected"
- [ ] Registra evento de auditoría
- [ ] Botón "Rechazar" en aprobaciones funciona correctamente
- [ ] Permisos ABAC se respetan (solo Supervisor, PM, Admin)

---

### Cronograma P0

```
Semana 1:
  Día 1-2: Vista detalle proyecto
  Día 3-4: Vista detalle reporte
  Día 5:   Endpoint rechazo reportes

Semana 2:
  Día 1-3: Vista edición proyecto
  Día 4-5: Modal/página creación proyecto

Semana 3:
  Día 1-2: Testing y refinamiento
  Día 3-5: Documentación y validación
```

**Total**: 2-3 semanas con 1-2 desarrolladores

---

## 🟡 PRIORIDAD P1: Importante (7-10 semanas)

### Objetivo
Completar integraciones externas, seguridad avanzada y preparación para Go Live.

---

### Fase 2.1: Integraciones con Proveedores (2-3 semanas)

#### 2.1.1. Sello NOM-151 Real
**Esfuerzo**: 1-2 semanas (después de seleccionar proveedor)  
**Dependencias**: Selección de proveedor de timbrado  
**Estado Actual**: 30% (código completo, falta proveedor)

**Tareas**:
- [ ] Investigar y seleccionar proveedor (Facturama, SW, etc.)
- [ ] Configurar `NOM151_PROVIDER_URL` en settings
- [ ] Configurar credenciales (API key, usuario, contraseña)
- [ ] Probar integración end-to-end
- [ ] Validar sello NOM-151 en PDFs generados
- [ ] Documentar proceso de configuración

**Criterios de Aceptación**:
- [ ] PDFs generados tienen sello NOM-151 válido
- [ ] Manejo de errores del proveedor funciona
- [ ] Reintentos automáticos funcionan
- [ ] Documentación completa de configuración

---

#### 2.1.2. IA Real ML
**Esfuerzo**: 1 semana (después de seleccionar proveedor)  
**Dependencias**: Selección de proveedor ML  
**Estado Actual**: 80% (pipeline completo, falta proveedor)

**Tareas**:
- [ ] Investigar y seleccionar proveedor ML (OpenAI, Azure AI, etc.)
- [ ] Configurar `AI_TRAIN_PROVIDER_URL` en settings
- [ ] Configurar credenciales (API key)
- [ ] Probar integración end-to-end
- [ ] Validar respuestas del chatbot
- [ ] Monitorear costos y throttling

**Criterios de Aceptación**:
- [ ] Chatbot IA funciona con proveedor externo
- [ ] Throttling y costos se registran correctamente
- [ ] Respuestas son relevantes y útiles
- [ ] Manejo de errores funciona

---

### Fase 2.2: Seguridad Avanzada (3-4 semanas)

#### 2.2.1. MFA (Multi-Factor Authentication) ✅ COMPLETADO
**Esfuerzo**: 1 semana  
**Dependencias**: Ninguna  
**Estado**: ✅ **COMPLETADO** (2026-01-23)

**Tareas Completadas**:
- [x] Instalar y configurar `django-otp` ✅
- [x] Crear modelos para dispositivos TOTP ✅
- [x] Crear UI para configuración MFA ✅
- [x] Integrar en flujo de login ✅
- [x] Tests de MFA (47 tests: 46 ✅, 1 ⏭️) ✅

**Criterios de Aceptación**:
- [x] Usuarios pueden configurar MFA ✅
- [x] Login requiere código TOTP si MFA está activo ✅
- [ ] Códigos de respaldo funcionan ⏳ (Pendiente menor)
- [x] UI es intuitiva ✅

**Documentación**: 
- `docs/security/IMPLEMENTACION_MFA.md`
- `docs/security/IMPLEMENTACION_UI_MFA.md`
- `docs/security/RESUMEN_COMPLETO_MFA.md`

---

#### 2.2.2. WebAuthn (Autenticación sin contraseña)
**Esfuerzo**: 1 semana  
**Dependencias**: Ninguna

**Tareas**:
- [ ] Instalar y configurar `django-webauthn`
- [ ] Crear modelos para llaves de seguridad
- [ ] Crear UI para registro de dispositivos
- [ ] Integrar en flujo de login
- [ ] Soporte para llaves de seguridad físicas
- [ ] Tests de WebAuthn

**Criterios de Aceptación**:
- [ ] Usuarios pueden registrar llaves de seguridad
- [ ] Login con WebAuthn funciona
- [ ] Soporte para múltiples dispositivos
- [ ] UI es intuitiva

---

#### 2.2.3. Rate Limiting Avanzado ✅ COMPLETADO
**Esfuerzo**: 3 días  
**Dependencias**: Ninguna (ya existe básico)  
**Estado**: ✅ **COMPLETADO** (2026-01-23)

**Tareas Completadas**:
- [x] Rate limiting por usuario (además de por IP) ✅
- [x] Rate limiting por endpoint específico ✅
- [ ] Dashboard de monitoreo de rate limits ⏳ (Opcional)
- [x] Configuración granular por endpoint ✅
- [x] Tests de rate limiting (11 tests ✅) ✅

**Criterios de Aceptación**:
- [x] Rate limiting por usuario funciona ✅
- [x] Rate limiting por endpoint funciona ✅
- [ ] Dashboard muestra métricas ⏳ (Opcional)
- [x] Configuración es flexible ✅

**Documentación**: 
- `docs/security/IMPLEMENTACION_RATE_LIMITING_AVANZADO.md`
- `docs/security/RESUMEN_RATE_LIMITING_AVANZADO.md`

---

#### 2.2.4. CSP Headers Avanzados
**Esfuerzo**: 2 días  
**Dependencias**: Ninguna

**Tareas**:
- [ ] Configurar Content Security Policy
- [ ] Implementar nonces para scripts inline
- [ ] Configurar reporte de violaciones
- [ ] Testing de CSP
- [ ] Documentación de configuración

**Criterios de Aceptación**:
- [ ] CSP headers están configurados
- [ ] Scripts inline funcionan con nonces
- [ ] Violaciones se reportan correctamente
- [ ] No hay errores en consola

---

### Fase 2.3: Go Live (2-3 semanas)

#### 2.3.1. Migración de Datos
**Esfuerzo**: 1 semana  
**Dependencias**: Fases 1, 2.1, 2.2

**Tareas**:
- [ ] Crear scripts de migración de datos existentes
- [ ] Validar integridad de datos
- [ ] Crear plan de rollback
- [ ] Probar migración en ambiente de staging
- [ ] Documentar proceso de migración

**Criterios de Aceptación**:
- [ ] Todos los datos se migran correctamente
- [ ] Integridad referencial se mantiene
- [ ] Rollback funciona si es necesario
- [ ] Proceso está documentado

---

#### 2.3.2. Training de Usuarios
**Esfuerzo**: 1 semana  
**Dependencias**: Sistema completo

**Tareas**:
- [ ] Crear guías de usuario por perfil (5 guías)
- [ ] Preparar sesiones de entrenamiento
- [ ] Crear material de apoyo (videos, screenshots)
- [ ] Realizar sesiones de entrenamiento
- [ ] Recopilar feedback

**Criterios de Aceptación**:
- [ ] Guías de usuario están completas
- [ ] Sesiones de entrenamiento realizadas
- [ ] Material de apoyo disponible
- [ ] Usuarios pueden usar el sistema

---

#### 2.3.3. Documentación Operativa
**Esfuerzo**: 3 días  
**Dependencias**: Sistema completo

**Tareas**:
- [ ] Crear runbooks operativos
- [ ] Documentar procedimientos de soporte
- [ ] Definir escalación de problemas
- [ ] Crear checklist de operación diaria
- [ ] Documentar procedimientos de backup/restore

**Criterios de Aceptación**:
- [ ] Runbooks están completos
- [ ] Procedimientos están documentados
- [ ] Escalación está definida
- [ ] Checklist está disponible

---

#### 2.3.4. Soporte Inicial
**Esfuerzo**: 3 días  
**Dependencias**: Documentación operativa

**Tareas**:
- [ ] Preparar equipo de soporte
- [ ] Configurar canales de comunicación
- [ ] Definir SLA
- [ ] Crear sistema de tickets
- [ ] Capacitar equipo de soporte

**Criterios de Aceptación**:
- [ ] Equipo de soporte está preparado
- [ ] Canales de comunicación funcionan
- [ ] SLA está definido
- [ ] Sistema de tickets funciona

---

#### 2.3.5. Monitoreo Post-Lanzamiento
**Esfuerzo**: 3 días  
**Dependencias**: Sistema en producción

**Tareas**:
- [ ] Configurar dashboards de monitoreo
- [ ] Configurar alertas
- [ ] Definir métricas de uso
- [ ] Crear reportes de uso
- [ ] Configurar notificaciones

**Criterios de Aceptación**:
- [ ] Dashboards muestran métricas relevantes
- [ ] Alertas funcionan correctamente
- [ ] Métricas de uso se recopilan
- [ ] Reportes están disponibles

---

### Cronograma P1 (Actualizado 2026-01-23)

```
Semana 1-2: Integraciones (NOM-151, IA ML) ⏳
Semana 3:   Seguridad Avanzada (WebAuthn, CSP) ⏳
            (MFA ✅, Rate Limiting ✅ ya completados)
Semana 4-5: Go Live (Migración, Training, Documentación, Soporte, Monitoreo) ⏳
```

**Total**: 5-7 semanas con 1-2 desarrolladores (reducido de 7-10 semanas)

**Nota**: MFA y Rate Limiting Avanzado ya están completados, reduciendo el tiempo estimado.

---

## 🟢 PRIORIDAD P2: Opcional (9-12 semanas)

### Objetivo
Mejorar performance, observabilidad e infraestructura para operación a largo plazo.

---

### Fase 3.1: Optimizaciones de Performance (3-4 semanas)

#### 3.1.1. Vistas Materializadas
**Esfuerzo**: 1 semana  
**Dependencias**: PostgreSQL

**Tareas**:
- [ ] Crear vistas materializadas para dashboards
- [ ] Configurar refresh automático
- [ ] Crear migraciones de vistas
- [ ] Optimizar queries usando vistas
- [ ] Tests de performance

---

#### 3.1.2. Full Text Search
**Esfuerzo**: 1 semana  
**Dependencias**: PostgreSQL

**Tareas**:
- [ ] Configurar índices de búsqueda de texto completo
- [ ] Implementar búsqueda en español
- [ ] Crear UI de búsqueda avanzada
- [ ] Optimizar queries de búsqueda
- [ ] Tests de búsqueda

---

#### 3.1.3. Particionado de Tablas
**Esfuerzo**: 1 semana  
**Dependencias**: PostgreSQL

**Tareas**:
- [ ] Particionar tablas por fecha (audit logs, reports)
- [ ] Migrar datos existentes
- [ ] Optimizar queries para particiones
- [ ] Configurar mantenimiento automático
- [ ] Tests de particionado

---

#### 3.1.4. Compresión de Datos
**Esfuerzo**: 3 días  
**Dependencias**: Ninguna

**Tareas**:
- [ ] Implementar compresión en sync offline
- [ ] Implementar compresión de respuestas API grandes
- [ ] Configurar compresión
- [ ] Tests de compresión

---

### Fase 3.2: Observabilidad (2-3 semanas)

#### 3.2.1. Prometheus Metrics
**Esfuerzo**: 1 semana  
**Dependencias**: Infraestructura (opcional)

**Tareas**:
- [ ] Instalar y configurar exportador Prometheus
- [ ] Crear métricas personalizadas
- [ ] Configurar dashboard Grafana
- [ ] Documentar métricas
- [ ] Tests de métricas

---

#### 3.2.2. OpenTelemetry Traces
**Esfuerzo**: 1 semana  
**Dependencias**: Infraestructura (opcional)

**Tareas**:
- [ ] Instrumentar aplicación con OpenTelemetry
- [ ] Configurar exportación de traces
- [ ] Configurar visualización (Jaeger/Zipkin)
- [ ] Documentar traces
- [ ] Tests de traces

---

#### 3.2.3. Health Checks Avanzados
**Esfuerzo**: 2 días  
**Dependencias**: Ninguna (ya existe básico)

**Tareas**:
- [ ] Agregar health checks de base de datos
- [ ] Agregar health checks de servicios externos
- [ ] Mejorar endpoint `/health/detailed/`
- [ ] Tests de health checks

---

### Fase 3.3: Infraestructura (4-6 semanas)

#### 3.3.1. Migración a PostgreSQL
**Esfuerzo**: 2 semanas  
**Dependencias**: Infraestructura

**Tareas**:
- [ ] Configurar PostgreSQL
- [ ] Crear scripts de migración SQLite → PostgreSQL
- [ ] Migrar datos
- [ ] Validar integridad
- [ ] Optimizar configuración PostgreSQL
- [ ] Tests post-migración

---

#### 3.3.2. CI/CD Profesional
**Esfuerzo**: 2 semanas  
**Dependencias**: Repositorio Git

**Tareas**:
- [ ] Configurar pipeline CI/CD (GitHub Actions / GitLab CI)
- [ ] Configurar tests automatizados en CI
- [ ] Configurar deployment automático
- [ ] Configurar rollback automático
- [ ] Documentar pipeline
- [ ] Tests de CI/CD

---

#### 3.3.3. Replicación y Backup
**Esfuerzo**: 1 semana  
**Dependencias**: PostgreSQL

**Tareas**:
- [ ] Configurar replicación de base de datos
- [ ] Configurar backup automático
- [ ] Crear Disaster Recovery Plan
- [ ] Probar restauración de backups
- [ ] Documentar procedimientos

---

#### 3.3.4. Tests de Carga
**Esfuerzo**: 1 semana  
**Dependencias**: Sistema completo

**Tareas**:
- [ ] Configurar herramientas (Locust, JMeter)
- [ ] Crear scripts de carga
- [ ] Ejecutar tests de carga
- [ ] Analizar resultados
- [ ] Optimizar basado en resultados
- [ ] Documentar resultados

---

### Cronograma P2

```
Semana 1-4: Optimizaciones (Vistas, Búsqueda, Particionado, Compresión)
Semana 5-7: Observabilidad (Prometheus, OpenTelemetry, Health Checks)
Semana 8-13: Infraestructura (PostgreSQL, CI/CD, Backup, Tests de Carga)
```

**Total**: 9-12 semanas con 1-2 desarrolladores

---

## 📊 Diagrama de Dependencias

```
P0: Navegación Frontend (2-3 semanas)
  ↓
P1: Integraciones (2-3 semanas) ──┐
  ↓                                │
P1: Seguridad (3-4 semanas) ──────┼──→ P1: Go Live (2-3 semanas)
  ↓                                │
P2: Optimizaciones (3-4 semanas) ─┘
  ↓
P2: Observabilidad (2-3 semanas)
  ↓
P2: Infraestructura (4-6 semanas)
```

---

## 🎯 Recomendación Final

### Opción Recomendada: Lanzamiento Incremental ⭐

**Fases Pre-Lanzamiento (5-7 semanas)** - Actualizado 2026-01-23:
1. ⏳ P0: Vistas Detalle/Edición (2-3 semanas) - Pendiente
2. ✅ P1: Seguridad Avanzada (MFA ✅, Rate Limiting ✅, WebAuthn ⏳, CSP ⏳) - 60% completado
3. ⏳ P1: Go Live (2-3 semanas) - Pendiente

**Fases Post-Lanzamiento (11-15 semanas)**:
1. ⏳ P1: Integraciones (cuando se seleccionen proveedores)
2. ⏳ P2: Optimizaciones
3. ⏳ P2: Observabilidad
4. ⏳ P2: Infraestructura

**Ventajas**:
- ✅ Lanzamiento rápido (2.5-3 meses)
- ✅ Sistema funcional y seguro
- ✅ Optimizaciones continuas
- ✅ Menor riesgo inicial

---

**Última actualización**: 2026-01-23
