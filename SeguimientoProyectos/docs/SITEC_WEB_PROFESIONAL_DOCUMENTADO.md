# PROYECTO SITEC-WEB PROFESIONAL (VERSION DOCUMENTADA)

## Contexto y objetivo
SITEC-Web es una plataforma empresarial para gestion integral de proyectos de instalaciones IT en Mexico (2026). Esta version documenta mejoras arquitectonicas, de seguridad, escalabilidad y operacion para un despliegue corporativo con alta disponibilidad.

Objetivos clave:
- Automatizar procesos y reducir carga administrativa.
- Asegurar cumplimiento normativo mexicano (NOM, LGPD, NOM-151).
- Operar en condiciones offline con sincronizacion robusta.
- Mejorar precision de costos, tiempos y riesgos con IA.

## 1) Arquitectura de microservicios hibrida
Servicios principales:
- `web`: Django + Gunicorn con replicas para alta disponibilidad.
- `ai_service`: microservicio dedicado a ML/NLP/vision.
- `celery_worker`: workers por colas (reports, ai_tasks, notifications).
- `celery_beat`: scheduler de tareas.
- `nginx`: reverse proxy y balanceo.

Beneficios:
- Escalado horizontal por componente.
- Aislamiento de fallos.
- Desacoplamiento entre API y procesamiento pesado.

## 2) Patrones de diseno aplicados
Patrones implementados en backend:
- Repository: abstraccion de acceso a datos.
- Strategy: validaciones y modos de captura.
- Observer: notificaciones por eventos del dominio.
- Factory: construccion de documentos.
- CQRS: lecturas optimizadas vs escrituras consistentes.
- Event-driven: integracion por eventos y handlers.

## 3) Arquitectura hexagonal (Ports & Adapters)
Separacion por capas:
- `domain`: logica de negocio pura (entidades, VOs, servicios, eventos).
- `application`: casos de uso, comandos y queries.
- `infrastructure`: repositorios, servicios externos, mensajeria.
- `interfaces`: API, web y CLI.

Resultado:
- Facilidad de pruebas.
- Sustitucion segura de infraestructura sin tocar dominio.
- Escalabilidad del proyecto y del equipo.

## 4) CQRS para dashboards
Lecturas desacopladas:
- Read models con vistas materializadas/denormalizadas.
- Consultas optimizadas para KPIs y paneles.

Resultado:
- Respuesta rapida en dashboards.
- Menor contencion en BD transaccional.

## 5) Sistema de eventos asincronos
Eventos de dominio (ej. `ProjectCreated`, `BudgetExceeded`) publicados en Redis:
- Desencadenan handlers: alertas, notificaciones, reportes, audit.
- Permiten escalado independiente de consumidores.

## 6) Optimizaciones para entorno mexicano
Localizacion MX:
- Validacion de NOM-001-SCFI, LGPD, NOM-151 y otras.
- Formato de moneda MXN.
- Zona horaria Mexico.

## 7) Sistema de permisos avanzado (RBAC + ABAC)
Modelo hibrido:
- RBAC para permisos base por rol.
- ABAC para condiciones contextuales (departamento, empresa, horario, ubicacion).

**Implementacion actual**:
- Motor ABAC unificado para API/UI con endpoint `POST /api/policies/evaluate/`.
- Catalogo ABAC base por rol en `seed_sitec` (acciones `wizard.*`, `projects.*`, `reports.*`, `documents.*`, `dashboard.*`, `roi.*`, `sync.*`, `ai.*`).

## 8) Observabilidad profesional
Stack:
- Prometheus: metricas.
- OpenTelemetry: trazas distribuidas.
- Health checks con dependencias (DB, Redis, AI, storage).
 - Headers de trazabilidad: `X-Request-ID`, `X-Response-Time-ms`.
 - Auditoria de requests lentos via `request_metrics`.

## 9) CI/CD profesional
Pipeline recomendado:
- Tests con cobertura.
- Migraciones en entorno CI.
- Analisis SAST y security scanning.
- Deploy a ECS/EKS con smoke tests.
- Notificaciones post-deploy.

## 10) Cache estrategico
Niveles:
- Cache HTTP (vista).
- Cache aplicacion (decorator).
- Cache distribuido (Redis) para sesiones y datos frecuentes.

## 11) Seguridad reforzada
Medidas:
- Headers de seguridad (HSTS, CSP, X-Frame-Options, etc).
- Rate limiting por IP.
- WebAuthn para MFA/FIDO2.
- Auditoria de seguridad con alertas criticas.

## 12) Optimizacion de base de datos
Estrategia:
- Indices parciales y compuestos.
- Vistas materializadas para dashboards.
- Particionado por fecha.
- Full text search en español.

## 13) Notificaciones multicanal
Orquestador con canales:
- Email, push, SMS, Slack, WhatsApp.
- Fallback automatico si fallan canales principales.

## 14) Plan de implementacion
Fases:
- Setup: arquitectura, CI/CD, Docker/K8s.
- Core: auth, proyectos, reportes.
- Offline: PWA, sync, IndexedDB.
- IA: modelos ML/NLP.
- Avanzado: dashboard, integraciones.
- Seguridad: pentesting, compliance, auditoria.
- Optimizacion: performance, cache, DB.
- Go Live: migracion, training, soporte.

## 15) Metricas y alertas
Monitoreo de negocio:
- Salud de proyectos.
- Engagement de usuarios.
- Alertas por umbrales.

## 16) Estimacion de costos
Estimado mensual:
- Infraestructura: 1,200 - 3,000 USD.
- Servicios externos: 300 - 800 USD.
- Licencias y mantenimiento: 2,000 - 5,000 USD.
- Desarrollo continuo: 8,000 - 15,000 USD.

---

# Sistema completo por modulos (implementacion Django PWA)
Esta seccion desarrolla el sistema completo por modulos, alineado a la documentacion proporcionada, con un enfoque incremental y desacoplado.

## Estructura del repositorio
sitec-web/
- backend/
  - config/ (settings, urls, celery, channels)
  - domain/ (entidades, servicios de dominio, eventos)
  - application/ (use cases, comandos, queries, DTOs)
  - infrastructure/ (repositorios, mensajeria, cache, integraciones)
  - interfaces/ (API DRF, views, serializers)
  - apps/
    - accounts/
    - companies/
    - projects/
    - reports/
    - tasks/
    - risks/
    - budgets/
    - evidence/
    - notifications/
    - dashboard/
    - ai/
    - documents/
    - audit/
    - localization/
    - sync/
- frontend/
  - templates/
  - static/
  - pwa/ (manifest.json, sw.js)
- infrastructure/ (docker, nginx, k8s, terraform)
- ops/ (ci-cd, scripts, runbooks)
- docs/

## Modulos funcionales (0 a 10)

### Modulo 0 - Contexto general y objetivo
**Alcance**: sitio unico (SITEC), roles PM/tecnico/supervisor/cliente, cumplimiento mexicano, offline robusto.  
**Apps**: `companies`, `accounts`, `localization`, `audit`.  
**Entregables**:
- Modelo de empresa SITEC y politicas base.
- Zona horaria y formatos MX.
- Auditoria (bitacora de eventos y cambios).

**Detalle de implementacion (Modulo 0)**:
- **SITEC unico**: no se requiere multi-tenant. Se mantiene `schema_name` solo si se habilita aislamiento futuro.
- **Modelo base**:
  - `Company` (nombre, RFC, plan, timezone, locale).
  - `Sitec` (schema, company_id, estado, fecha_activacion).
  - `UserProfile` (rol, departamento, ubicacion, preferencias).
- **Roles iniciales**: `admin_empresa`, `pm`, `tecnico`, `supervisor`, `cliente`.
- **Politicas base**: RBAC inicial + ABAC por empresa, ubicacion, horario.
- **Localizacion MX**:
  - Timezone default: `America/Mexico_City`.
  - Formatos: `DD/MM/YYYY`, moneda `MXN`, separadores locales.
- **Auditoria**:
  - `AuditLog` (actor, accion, entidad, before/after, ip, user_agent, timestamp).
  - Almacenamiento append-only y retencion configurable.

**Modelos (campos clave)**:
- `Company`
  - `id` (UUID), `name`, `rfc`, `tax_regime`
  - `timezone` (default `America/Mexico_City`), `locale` (`es-MX`)
  - `plan` (starter/pro/enterprise), `status` (active/suspended)
  - `created_at`, `updated_at`
- `Sitec`
  - `id` (UUID), `schema_name`
  - `company` (FK a `Company`)
  - `status` (active/suspended), `activated_at`
  - `created_at`, `updated_at`
- `UserProfile`
  - `id` (UUID), `user` (OneToOne `auth.User`)
  - `company` (FK), `role` (admin_empresa/pm/tecnico/supervisor/cliente)
  - `department`, `location`, `phone`
  - `preferences` (JSON), `last_login_at`
  - `created_at`, `updated_at`
- `AccessPolicy`
  - `id` (UUID), `company` (FK)
  - `action` (string), `conditions` (JSON), `effect` (allow/deny)
  - `priority` (int), `is_active` (bool)
  - `created_at`, `updated_at`
- `AuditLog`
  - `id` (UUID), `company` (FK)
  - `actor` (FK `auth.User`, nullable)
  - `action`, `entity_type`, `entity_id`
  - `before` (JSON), `after` (JSON)
  - `ip_address`, `user_agent`
  - `created_at`

**Endpoints (URLs del Modulo 0)**:
- `GET /api/companies/` listar empresas (admin global).
- `POST /api/companies/` crear empresa.
- `GET /api/companies/{id}/` detalle empresa.
- `PATCH /api/companies/{id}/` actualizar empresa.
- `POST /api/sitec/` crear instancia SITEC y schema.
- `GET /api/sitec/{id}/` detalle instancia SITEC.
- `PATCH /api/sitec/{id}/status/` activar/suspender instancia SITEC.
- `GET /api/users/me/` perfil del usuario actual.
- `PATCH /api/users/me/` actualizar preferencias.
- `GET /api/policies/` listar politicas de acceso (por empresa).
- `POST /api/policies/` crear politica ABAC.
- `PATCH /api/policies/{id}/` actualizar politica.
- `GET /api/audit/` consultar auditoria (filtros por fecha, actor, entidad).

### Modulo 1 - UX y diseno web-first
**Apps**: `frontend`, `reports`, `projects`.  
**Entregables**:
- UI mobile-first con Bootstrap 5 + HTMX + Alpine.
- Wizard con 12 pasos (version compacta 10 pasos).
- FAB persistente y barra de progreso.
- Temas claro/oscuro + accesibilidad WCAG.

**Compatibilidad con Modulo 0 (SITEC unico)**:
- Todas las pantallas asumen una sola empresa `SITEC`, sin selector de tenant.
- Preferencias de UI (tema, modo campo, accesibilidad) se guardan en `UserProfile.preferences`.
- Los textos, formatos y timezone usan `localization` (MX) del Modulo 0.
- Auditoria registra eventos UX criticos (errores bloqueantes, cambios de modo) en `AuditLog`.
- Las politicas ABAC del Modulo 0 validan acciones del wizard (ej. bloquear firmas si rol no autorizado).
- Cada request expone `request.company` y `request.sitec` via middleware para usar en endpoints del Modulo 1.
- Los viewsets del Modulo 1 deben heredar `CompanySitecQuerysetMixin` para filtrar datos por `company/sitec`.

**Mejoras del Modulo 1 (documentadas)**:
- **Sistema de estados UI**: paleta consistente para error/alerta/info/exito, con iconografia y feedback visual uniforme.
- **Modo Campo**: toggle de alto contraste y controles 56-64px para uso con guantes y luz directa.
- **Errores criticos**: validaciones de compliance o seguridad bloquean avance; errores menores son no bloqueantes.
- **Indicador de sync**: estado fijo visible (Offline/En cola/Sincronizando/Error) con acciones rapidas.
- **Conflictos de datos**: vista de resolucion simple (local vs servidor) con decision rapida.
- **Performance budget**: limites de JS inicial (<100KB), FCP <1s y TTI <2.5s, medidos en CI.
- **Micro-interacciones**: feedback tactil/visual en acciones criticas (guardar, firmar, enviar).
- **Wizard mejorado**: barra de progreso con ETA real y pasos condicionales visibles.

**Reglas de diseno (tokens/variables CSS)**:
```css
:root {
  /* Tipografia */
  --font-family-base: "Inter", "Segoe UI", Arial, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 22px;
  --line-height-base: 1.5;

  /* Espaciado */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;

  /* Bordes y sombras */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 6px 18px rgba(0, 0, 0, 0.12);

  /* Colores base */
  --color-bg: #f7f8fb;
  --color-surface: #ffffff;
  --color-text: #1f2937;
  --color-muted: #6b7280;
  --color-border: #e5e7eb;

  /* Estados */
  --color-success: #16a34a;
  --color-warning: #f59e0b;
  --color-error: #dc2626;
  --color-info: #2563eb;

  /* Acciones */
  --color-primary: #0f4c81;
  --color-primary-hover: #0b3a63;
  --color-secondary: #334155;

  /* Accesibilidad */
  --focus-ring: 0 0 0 3px rgba(37, 99, 235, 0.35);
  --touch-target-min: 48px;
  --touch-target-field: 56px;
}

[data-theme="dark"] {
  --color-bg: #0f172a;
  --color-surface: #111827;
  --color-text: #f9fafb;
  --color-muted: #9ca3af;
  --color-border: #1f2937;
}

[data-mode="field"] {
  --font-size-md: 18px;
  --font-size-lg: 20px;
  --touch-target-min: 56px;
  --touch-target-field: 64px;
  --color-bg: #0b0f14;
  --color-surface: #111827;
  --color-text: #ffffff;
}
```

**Checklist de implementacion (Modulo 1)**:
- [ ] Activar Modo Campo (manual + automatico por horario/ubicacion).
- [ ] Targets tactiles >= 56px y controles criticos >= 64px.
- [ ] Feedback triple en acciones criticas (visual/vibracion/sonido).
- [ ] Validaciones bloqueantes vs no bloqueantes claramente separadas.
- [ ] Indicador de sync fijo (Offline/En cola/Sincronizando/Error).
- [ ] Auto-save con timestamp visible en cada paso.
- [ ] Resolucion de conflictos (local vs servidor) con accion por defecto.
- [ ] ETA por paso + progreso total del wizard.
- [ ] Pasos condicionales visibles y bloqueados hasta cumplir reglas.
- [ ] Re-autenticacion previa a firma o envio final.
- [ ] Auditoria de eventos UX criticos en `AuditLog`.
- [ ] Budget de performance (FCP/TTI/JS inicial) con verificacion en CI.

**Historias de usuario (Modulo 1)**:
- Como tecnico, quiero un modo campo de alto contraste para usar el wizard bajo sol.
- Como supervisor, quiero que los errores criticos bloqueen el avance para evitar reportes invalidos.
- Como PM, quiero ver el estado de sincronizacion para confirmar envio correcto.
- Como tecnico, quiero auto-guardado para no perder avances sin conexion.
- Como usuario, quiero pasos condicionales visibles para entender por que no avanzo.
- Como auditor, quiero que eventos UX criticos se registren en `AuditLog`.

**Criterios de aceptacion (Modulo 1)**:
- Modo Campo: activacion manual y automatica; controles >=56px; contraste AA.
- Wizard: ETA visible por paso; progreso total; pasos condicionales visibles y bloqueados.
- Validaciones: errores criticos bloquean avance; no criticos permiten continuar con aviso.
- Sync: indicador fijo con 4 estados y timestamp de ultimo guardado local.
- Offline: auto-guardado cada 30s; reintentos al reconectar; sin perdida de datos.
- Seguridad: re-autenticacion antes de firma/envio final.
- Auditoria: eventos UX criticos registrados con usuario, accion y timestamp.
- Performance: JS inicial <100KB; FCP <1s; TTI <2.5s en medicion CI.

**Reglas de validacion por paso (Wizard 12 pasos)**:
- **Paso 1 (Datos generales)**: `project_name`, `week_start`, `site_address`, `technician` son obligatorios.
- **Paso 2 (Planificacion/estado)**: `progress_pct` obligatorio y entre 0-100; `schedule_status` recomendado.
- **Paso 3 (Cableado y nodos)**: `cabling_nodes_total` obligatorio; `cabling_nodes_ok` recomendado.
- **Paso 4 (Gabinetes/racks)**: `racks_installed` obligatorio; `rack_order_ok` recomendado.
- **Paso 5 (Seguridad/audiovisual)**: `security_devices` obligatorio y no negativo; `cameras_online` recomendado.
- **Paso 6 (Sistemas especializados)**: si `special_systems_enabled` es true, `special_systems_notes` obligatorio.
- **Paso 7 (Materiales/herramientas)**: `materials_count` obligatorio; `materials_list` recomendado.
- **Paso 8 (Pruebas/verificaciones)**: si `tests_passed` es false, bloqueo; `qa_signed` recomendado.
- **Paso 9 (Evidencias)**: `evidence_photos` obligatorio; `evidence_geo` recomendado.
- **Paso 10 (Incidentes/observaciones)**: si hay `incidents`, `incidents_detail` obligatorio; si `incidents_severity` es high, `mitigation_plan` obligatorio.
- **Paso 11 (Firmas/aprobaciones)**: `signature_tech` obligatorio; si `signature_supervisor_required` es true, `signature_supervisor` obligatorio.
- **Paso 12 (Resumen/cierre)**: `final_review_ack` obligatorio; `report_summary` recomendado.

### Modulo 2 - Arquitectura tecnica y offline
**Apps**: `sync`, `reports`, `projects`.  
**Entregables**:
- Service Worker y manifest PWA.
- IndexedDB con cifrado y Outbox.
- Sync bidireccional con reintentos y circuit breaker.
- Estado de sincronizacion por registro.

### Modulo 3 - Modelo de datos profesional
**Apps**: `projects`, `reports`, `tasks`, `risks`, `budgets`, `evidence`.  
**Modelos clave**:
- Proyecto, ReporteSemanal, Tarea, Riesgo, Presupuesto, Evidencia, Firma, Incidente.  
**Entregables**:
- Indices compuestos y materialized views para dashboards.
- Campos IA: riesgo_score, sugerencias_ia, predicciones.

### Modulo 4 - Formulario SITEC (wizard 12 paginas)
**Apps**: `reports`, `evidence`, `documents`.  
**Entregables**:
- Wizard con validaciones client/server.
- Guardado automatico local + sync diferido.
- Flujos condicionales por riesgos/presupuesto.

### Modulo 5 - Captura inteligente e IA
**Apps**: `ai`, `reports`, `evidence`.  
**Entregables**:
- Pre-llenado por historial + GPS.
- NLP de incidencias y sugerencias.
- Vision QA para evidencias fotograficas.
- Servicios IA en Celery y/o microservicio separado.

**Avance IA real inicial**:
- Modelo ligero (`LightModelProvider`) con configuracion versionada para sugerencias basadas en datos.

### Modulo 6 - Validaciones y reglas
**Apps**: `projects`, `reports`, `risks`.  
**Entregables**:
- Validadores de negocio y compliance NOM/LGPD.
- Deteccion de outliers y alertas predictivas.
- Motor de reglas configurable por empresa.

### Modulo 7 - Componentes reutilizables
**Apps**: `frontend`, `reports`, `projects`.  
**Entregables**:
- Biblioteca de componentes (inputs tactiles, galerias, firma).
- Gantt/Kanban, matriz de riesgo, chatbot IA.

**Mejoras propuestas (alineadas a modulos 0-6)**:
- **Contrato de componentes**: props estandar (`value`, `onChange`, `errors`, `isBlocking`, `disabledReason`, `syncState`).
- **Accesibilidad y Modo Campo**: tamanos tactiles minimos (56-64px), contraste AA y adaptacion automatica por `data-mode="field"`.
- **Integracion con reglas**: cada componente acepta `validationSeverity` y `validationMessage` del motor de reglas (Modulo 6).
- **Offline/sync**: soporte de `isOffline`, `lastSavedAt` y estados `Offline/En cola/Sincronizando/Error`.
- **Componentes avanzados**: Gantt/Kanban lectura + drag-drop basico; RiskMatrix 5x5 con colores de tokens; Chatbot IA solo con contrato del Modulo 5.

**Checklist de implementacion (Modulo 7)**:
- [ ] Catalogo de componentes con proposito, estados y variantes.
- [ ] Tokens compartidos (colors, spacing, radius, focus) alineados a Modulo 1.
- [ ] Contrato de props y eventos estandar para inputs y widgets.
- [ ] Soporte completo para Modo Campo y accesibilidad AA.
- [ ] Integracion con motor de reglas (Modulo 6) y severidades.
- [ ] Estados offline/sync visibles y consistentes en UI.
- [ ] Libreria documentada con ejemplos y pautas de uso.

**Historias de usuario (Modulo 7)**:
- Como tecnico, quiero controles tactiles grandes y claros para capturar rapido en campo.
- Como supervisor, quiero ver errores y advertencias uniformes en todos los componentes.
- Como PM, quiero usar componentes estandar para mantener consistencia UX.
- Como auditor, quiero que los componentes registren eventos criticos en `AuditLog`.
- Como usuario offline, quiero ver estado de guardado y sincronizacion en cada captura.

**Criterios de aceptacion (Modulo 7)**:
- Todos los inputs usan el mismo contrato de props y estados.
- Controles criticos cumplen tamanos tactiles >=56px y contraste AA.
- Cada componente muestra errores del motor de reglas con severidad clara.
- Los componentes clave soportan `isOffline`, `lastSavedAt` y `syncState`.
- Gantt/Kanban y RiskMatrix se muestran sin romper el wizard y con data real.
- Chatbot IA solo consume el contrato definido en Modulo 5.

**Catalogo inicial de componentes (Modulo 7)**:
- **Inputs base**: `TextField`, `NumberField`, `SelectField`, `DateField`, `Textarea`.
- **Inputs avanzados**: `SignaturePad`, `PhotoGallery`, `EvidenceUploader`, `GeoPicker`.
- **Estado y sync**: `SyncStatusIndicator`, `OfflineBadge`, `LastSavedStamp`, `ConflictResolver`.
- **Wizard**: `StepProgress`, `StepHeader`, `StepSummary`, `InlineHelp`.
- **Visualizacion**: `RiskMatrix`, `GanttLite`, `KanbanBoard`.
- **IA**: `AiSuggestionCard`, `AiConfidenceBadge`, `AiChatAssistant` (solo contract-first).

**Contratos de datos (Modulo 7)**:
- **RiskMatrix**
  - **Input**: `project_id`, lista `riesgos[{id,title,severity,probability}]`.
  - **Output**: `levels[5]` + `matrix[5][5]` con conteos por celda.
- **GanttLite**
  - **Input**: `project_id`, lista `tareas[{id,title,status}]`.
  - **Output**: `rows[{name,progress_pct}]` derivado de `status`.
- **KanbanBoard**
  - **Input**: `project_id`, lista `tareas[{id,title,status}]`.
  - **Output**: columnas `Pendiente/En progreso/Hecho/Bloqueado` con tarjetas.

### Modulo 8 - PDF y firma digital
**Apps**: `documents`, `reports`, `evidence`.  
**Entregables**:
- Generacion PDF con ReportLab (async).
- Firmas multiple nivel (tecnico/supervisor/cliente).
- QR de verificacion y sellos NOM-151.
- Versionado y almacenamiento seguro.

**Implementacion inicial (Modulo 8)**:
- App `apps.documents` creada con modelo `Document` (versionado y estado de PDF).
- Servicio `generate_report_pdf` con ReportLab y QR de verificacion.
- Tarea Celery `generate_report_document` para ejecucion async.
- Endpoints:
  - `POST /api/documents/documents/report/` (solicitar generacion por `report_id`).
  - `GET /api/documents/documents/{id}/` (estado del documento).
  - `GET /api/documents/documents/{id}/download/` (descarga PDF).
  - `GET /api/documents/verify/{token}/` (verificacion QR).
- Storage local en `backend/storage/documents/{reporte}/`.

### Modulo 9 - Dashboard gerencial
**Apps**: `dashboard`, `projects`, `reports`, `budgets`, `risks`.  
**Entregables**:
- KPIs operativos y financieros en tiempo real.
- Alertas y comparativos por empresa/tecnico.
- Exportaciones Excel/PDF y filtros avanzados.

**Implementacion inicial (Modulo 9)**:
- Endpoint base `GET /api/dashboard/` con KPIs clave (proyectos, reportes, riesgos).

### Modulo 10 - KPIs, ROI y fases
**Apps**: `analytics`, `dashboard`.  
**Entregables**:
- KPIs con metas y umbrales.
- Reportes de ROI y productividad.
- Seguimiento de fases y entregables por etapa.

## Contratos de API (resumen)
- `GET /api/projects/` lista proyectos con filtros.
- `POST /api/reports/` crea reporte (offline-friendly).
- `POST /api/sync/` sincroniza outbox/inbox.
- `GET /api/dashboard/` KPIs y tendencias.
- `POST /api/ai/predict/` predicciones y sugerencias.
- `POST /api/documents/report/` genera PDF.

## Tareas asincronas (Celery)
- Generacion de PDF con evidencias.
- Analisis IA (NLP/vision/predicciones).
- Envio de notificaciones multicanal.
- Refresco de vistas materializadas.
- Backups programados y verificacion de integridad.

## PWA y offline (detalles clave)
- Cache de recursos criticos y assets estaticos.
- Cola de operaciones con prioridad y reintentos.
- Resolucion de conflictos por timestamps + regla IA.
- Indicadores visuales: Offline/En cola/Sincronizado/Error.

## Seguridad y cumplimiento
- MFA + WebAuthn, rate limiting, CSP.
- Auditoria de accesos y cambios.
- Cifrado en transito y reposo (AES-256).
- Politicas de retencion y minimizacion de datos.

## Roadmap modular por fases
- Fase 1 (MVP): Modulos 1-4.
- Fase 2: Modulos 5-6.
- Fase 3: Modulos 7-8.
- Fase 4: Modulos 9-10 y optimizaciones.

# Analisis profundo

## Fortalezas
- Arquitectura hibrida permite evolucionar de monolito a microservicios sin ruptura.
- CQRS reduce latencia de lectura en dashboards con alto volumen.
- Event-driven habilita escalado y desacople de procesos pesados.
- Seguridad avanzada cubre autenticacion moderna, rate limiting y auditoria.
- Observabilidad completa permite SLOs reales y operacion madura.

## Riesgos y mitigaciones
- **Complejidad operativa**: muchos componentes. Mitigar con IaC, runbooks y automatizacion.
- **Costos de IA**: inferencia puede disparar costos. Mitigar con colas, caching y limites de uso.
- **Consistencia eventual**: CQRS/eventos. Mitigar con politicas de reconciliacion y UI clara.
- **Compliance**: requiere validacion legal. Mitigar con asesoria juridica y auditorias periodicas.

## Gaps tecnicos a cerrar
- Definir contrato de eventos y versionado (schema registry).
- Formalizar politicas de retencion de datos y cifrado por tabla.
- Definir si en el futuro se habilitara aislamiento multi-tenant.
- Establecer SLO/SLI y umbrales de alertas por entorno.

## Contraste con modulos ya desarrollados
- **Modulos 0-6**: el analisis confirma la base ya implementada (modelos, wizard, offline, reglas y IA). No hay contradicciones; las recomendaciones apuntan a integracion y robustez, no a rehacer.
- **Permisos RBAC/ABAC**: motor unificado ya aplica en endpoints principales (AccessPolicyPermission) y evaluacion via `/api/policies/evaluate/`.
- **Reglas (Modulo 6)**: el motor existe y esta versionado; el pendiente real es su integracion con componentes reutilizables del Modulo 7.
- **Wizard dinamico (Modulo 4)**: el schema ya opera; la mejora debe enfocarse en compatibilidad y degradacion controlada, no en redisenar.
- **Brecha principal**: Modulo 7 no tiene definicion tecnica, contrato de componentes ni lineamientos de accesibilidad/sync; es el siguiente cuello de botella real.

## Dependencias criticas
- Redis, Postgres, broker de colas.
- Servicios externos: email/SMS/push, firma digital, Auth0/Keycloak.
- Observabilidad: OTLP collector, Prometheus, Grafana.

## Recomendaciones de implementacion
- Empezar con monolito modular + colas y extraer `ai_service`.
- Implementar read model para dashboards en una fase temprana.
- Priorizar seguridad (MFA, CSP, auditoria) antes de Go Live.
- Definir politicas de backup/DRP y pruebas de restauracion.

## Pruebas recomendadas
- Unitarias por dominio y servicios.
- Integracion con BD y cache.
- Carga para endpoints criticos (dashboards, reportes).
- Seguridad: SAST/DAST y pentesting previo a produccion.

**Notas de testing (proyecto actual)**:
- Se configuro un test runner para descubrir tests de `apps.*` sin pasar etiquetas.
- Ejecutar: `python backend/manage.py test`

**Avances recientes (Modulo 1)**:
- Wizard conectado a endpoints reales (guardar paso, validar, sync).
- Validaciones reales por 12 pasos y mensajes de error amigables.
- UI extendida por paso con secciones, grids y campos adicionales.
- Offline avanzado con IndexedDB + outbox + sync multiples pasos.
- Resolucion de conflictos con UI (usar local/servidor).
- Accesibilidad avanzada (skip link, aria, focus-visible, hints).
- Modo Campo automatico por horario/ubicacion.
- Telemetria UX base (eventos, sync, validacion, conflictos) via `/api/wizard/analytics/`.
- Snapshot UI tests base (wizard/dashboard).
- Tests del frontend ejecutados (OK).

**Pendientes sugeridos (proxima sesion)**:
- Persistir preferencia de Modo Campo (opt-out del automatico).
- Ajustar validaciones para nuevos campos opcionales si se desea.
- Añadir endpoints para PDF/firmas (Modulo 8) y enlazar desde wizard.
- Mejorar indicador de sync con timestamps y estados detallados.

**Avances recientes (Modulo 3)**:
- Agregado versionado de `wizard_data` en `ReporteSemanal` (`wizard_schema_version`, `wizard_updated_at`, `wizard_client_id`).
- Constraints de integridad en `ReporteSemanal` (rango `progress_pct`, no negativos).
- Constraints de lat/long en `Evidencia`.
- Constraints de integridad en `Proyecto` (rango `progress_pct`, presupuestos no negativos).
- Migraciones aplicadas para `projects` y `reports`.
- Suite completa verificada: **91 tests OK**.

**Avances recientes (Modulo 4)**:
- Wizard dinamico desde schema JSON (`wizard_schema_v1.json`).
- Renderer con secciones por paso (mejor UX y control de fatiga).
- Reglas condicionales avanzadas `show_if` y `required_if` en schema.
- Evaluacion dinamica de campos requeridos y visibilidad en UI.
- `schema_version` incluido en payload de autosave.
- Endpoint `/api/wizard/schema/` para servir el schema en produccion.
- Schema versionado por query param con fallback seguro.
- Soporte UI para `regex`/`min`/`max` desde schema y reglas AND/OR.
- Test de schema endpoint agregado.
- Auditoria de acceso al schema (`wizard_schema_viewed`) agregada.
- Tests frontend ejecutados: **37 OK**.

**Pendientes (Modulo 4)**:
- Sin pendientes criticos.

### Schema v1 del Wizard (resumen por paso)
- **Paso 1**: Identificacion, ubicacion y notas iniciales.
- **Paso 2**: Estado del proyecto, fechas y riesgos.
- **Paso 3**: Volumen de cableado y calidad/materiales.
- **Paso 4**: Racks, energia y enfriamiento.
- **Paso 5**: Seguridad y audiovisual.
- **Paso 6**: Sistemas especializados (condicional).
- **Paso 7**: Materiales, herramientas y faltantes (condicional).
- **Paso 8**: Pruebas, QA y notas.
- **Paso 9**: Evidencias y geolocalizacion.
- **Paso 10**: Incidentes y mitigacion (condicional).
- **Paso 11**: Firmas y metodo de firma.
- **Paso 12**: Resumen final y cierre.

## Propuesta final de modelo (Módulo 3) con ajustes
Esta propuesta integra **constraints**, **indices**, y **schema versionado** para `wizard_data`, garantizando compatibilidad con Módulos 0, 1 y 2.

### Principios clave
- **Compatibilidad Módulo 0**: todos los modelos llevan `company` y `sitec` (SITEC único) y se asignan en `perform_create`.
- **Compatibilidad Módulo 1**: campos usados en el wizard existen y están alineados con validaciones por paso.
- **Compatibilidad Módulo 2 (offline)**: `wizard_data` incluye `schema_version`, `updated_at` y `client_id` para sync confiable.

### Ajustes de modelo recomendados
#### ReporteSemanal (campos críticos + JSON versionado)
- **Constraints**:
  - `progress_pct` entre 0 y 100.
  - `cabling_nodes_total`, `materials_count`, `security_devices` >= 0.
- **wizard_data**:
  - `schema_version` (int)
  - `updated_at` (ISO string)
  - `client_id` (UUID/ID de dispositivo)
  - `steps` (dict por paso)
- **Indices**:
  - `(company, week_start)`
  - `(technician, week_start)`
  - `(status, created_at)`
  - `(project, week_start)`

#### Proyecto (consistencia y performance)
- **Constraints**:
  - `progress_pct` entre 0 y 100.
  - `budget_estimated`, `budget_actual` >= 0.
- **Indices**:
  - `(company, status)`
  - `(project_manager, created_at)`
  - `(code)` unique

#### Evidencia / Incidente
- **Constraints**:
  - `latitude/longitude` en rangos válidos si existen.
  - `severity` en valores permitidos.
- **Indices**:
  - `(reporte, created_at)`
  - `(reporte, severity)`

#### SyncSession / SyncItem (Módulo 2)
- **Indices**:
  - `(company, user, started_at)`
  - `(status, started_at)`
  - `(entity_type, entity_id)`
- **Campos clave**:
  - `client_timestamp`, `server_timestamp` para resolución de conflictos.

### JSON schema versionado (wizard_data)
Ejemplo mínimo:
```json
{
  "schema_version": 1,
  "updated_at": "2026-01-17T10:30:00Z",
  "client_id": "device-uuid-123",
  "steps": {
    "1": {"project_name": "...", "week_start": "..."},
    "2": {"progress_pct": 50}
  }
}
```

### Compatibilidad con módulos
- **Módulo 0**: `company/sitec` obligatorios y auditados.
- **Módulo 1**: campos del wizard existen y validan en backend.
- **Módulo 2**: versionado + timestamps permiten sync y resolución de conflictos.

## Módulo 4 - Validación de schema (pre-implementación)
### Schema propuesto (v1) - compatible con Módulos 0/1/2
```json
{
  "schema_version": 1,
  "steps": {
    "1": {
      "title": "Datos generales",
      "fields": [
        {"name": "project_name", "type": "text", "required": true},
        {"name": "week_start", "type": "date", "required": true},
        {"name": "site_address", "type": "text", "required": true},
        {"name": "technician", "type": "text", "required": true},
        {"name": "project_code", "type": "text", "required": false},
        {"name": "site_city", "type": "text", "required": false},
        {"name": "site_state", "type": "text", "required": false},
        {"name": "client_name", "type": "text", "required": false},
        {"name": "site_contact", "type": "text", "required": false},
        {"name": "initial_notes", "type": "textarea", "required": false}
      ]
    },
    "2": {
      "title": "Planificación y estado",
      "fields": [
        {"name": "progress_pct", "type": "number", "required": true, "min": 0, "max": 100},
        {"name": "schedule_status", "type": "text", "required": false},
        {"name": "planned_start", "type": "date", "required": false},
        {"name": "planned_end", "type": "date", "required": false},
        {"name": "actual_start", "type": "date", "required": false},
        {"name": "actual_end", "type": "date", "required": false},
        {"name": "risks_summary", "type": "textarea", "required": false}
      ]
    },
    "3": {
      "title": "Cableado y nodos",
      "fields": [
        {"name": "cabling_nodes_total", "type": "number", "required": true, "min": 0},
        {"name": "cabling_nodes_ok", "type": "number", "required": false, "min": 0},
        {"name": "cable_type", "type": "text", "required": false},
        {"name": "cable_length_m", "type": "number", "required": false, "min": 0},
        {"name": "cable_trays_ok", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "labeling_ok", "type": "select", "required": false, "options": ["true", "false"]}
      ]
    },
    "4": {
      "title": "Gabinetes y racks",
      "fields": [
        {"name": "racks_installed", "type": "number", "required": true, "min": 0},
        {"name": "rack_order_ok", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "rack_units_used", "type": "number", "required": false, "min": 0},
        {"name": "cooling_ok", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "power_ok", "type": "select", "required": false, "options": ["true", "false"]}
      ]
    },
    "5": {
      "title": "Seguridad y audiovisual",
      "fields": [
        {"name": "security_devices", "type": "number", "required": true, "min": 0},
        {"name": "cameras_online", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "camera_count", "type": "number", "required": false, "min": 0},
        {"name": "access_control_count", "type": "number", "required": false, "min": 0},
        {"name": "av_systems_count", "type": "number", "required": false, "min": 0},
        {"name": "security_notes", "type": "textarea", "required": false}
      ]
    },
    "6": {
      "title": "Sistemas especializados",
      "fields": [
        {"name": "special_systems_enabled", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "special_systems_type", "type": "text", "required": false},
        {"name": "special_systems_vendor", "type": "text", "required": false},
        {"name": "special_systems_integration_ok", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "special_systems_notes", "type": "textarea", "required": true, "required_if": {"special_systems_enabled": "true"}}
      ]
    },
    "7": {
      "title": "Materiales y herramientas",
      "fields": [
        {"name": "materials_count", "type": "number", "required": true, "min": 0},
        {"name": "tools_used", "type": "text", "required": false},
        {"name": "missing_materials", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "missing_materials_detail", "type": "text", "required": false, "required_if": {"missing_materials": "true"}},
        {"name": "materials_list", "type": "textarea", "required": false}
      ]
    },
    "8": {
      "title": "Pruebas y verificación",
      "fields": [
        {"name": "tests_passed", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "qa_signed", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "test_notes", "type": "textarea", "required": false}
      ]
    },
    "9": {
      "title": "Evidencias",
      "fields": [
        {"name": "evidence_photos", "type": "text", "required": true},
        {"name": "evidence_geo", "type": "text", "required": false},
        {"name": "evidence_ids", "type": "text", "required": false},
        {"name": "evidence_notes", "type": "textarea", "required": false}
      ]
    },
    "10": {
      "title": "Incidentes y observaciones",
      "fields": [
        {"name": "incidents", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "incidents_severity", "type": "select", "required": false, "options": ["low", "medium", "high"]},
        {"name": "incidents_count", "type": "number", "required": false, "min": 0},
        {"name": "incidents_detail", "type": "text", "required": true, "required_if": {"incidents": "true"}},
        {"name": "mitigation_plan", "type": "text", "required": true, "required_if": {"incidents_severity": "high"}}
      ]
    },
    "11": {
      "title": "Firmas y aprobaciones",
      "fields": [
        {"name": "signature_tech", "type": "text", "required": true},
        {"name": "signature_supervisor_required", "type": "select", "required": false, "options": ["true", "false"]},
        {"name": "signature_supervisor", "type": "text", "required": true, "required_if": {"signature_supervisor_required": "true"}},
        {"name": "signature_method", "type": "select", "required": false, "options": ["canvas", "webauthn"]},
        {"name": "signature_date", "type": "date", "required": false}
      ]
    },
    "12": {
      "title": "Resumen y cierre",
      "fields": [
        {"name": "report_summary", "type": "textarea", "required": false},
        {"name": "next_actions", "type": "textarea", "required": false},
        {"name": "final_review_ack", "type": "select", "required": true, "options": ["true", "false"]},
        {"name": "client_feedback", "type": "text", "required": false}
      ]
    }
  }
}
```

### Checklist de compatibilidad (100%)
- **Módulo 0**: ningún campo `company/sitec` editable en schema; se asigna en backend.
- **Módulo 1**: nombres de campo iguales a los actuales en UI y validaciones.
- **Módulo 2**: schema usa `schema_version` y `updated_at` para sync/conflitos.
- **Validaciones**: reglas `required_if` reflejan condiciones ya usadas en UI.

## Módulo 5 - Análisis para mejoramiento
### Checklist previo a implementación
- Definir **pipeline IA por niveles** (reglas -> modelo ligero -> Celery pesado).
- Establecer **timeouts y fallback** para evitar bloqueo en campo.
- Versionar modelos (campo `model_version`) y guardar `confidence_score`.
- Normalizar entradas (voz/texto) antes de IA.
- Registrar decisiones IA en `AuditLog` con trazabilidad.
- Definir **contrato de respuesta IA** (schema de salida).
- Definir comportamiento **offline-first** (IA local ligera + reintento).

### User stories
1) Como técnico, quiero sugerencias IA rápidas para completar campos críticos sin bloquear mi captura.
2) Como supervisor, quiero ver por qué la IA sugirió un valor para validar la decisión.
3) Como PM, quiero trazabilidad de predicciones IA con versión de modelo y confianza.
4) Como técnico en campo, quiero que el sistema funcione sin internet y sincronice luego.
5) Como auditor, quiero historial de recomendaciones IA para revisiones posteriores.

### Criterios de aceptación
- La IA responde en <2s para sugerencias rápidas; si no, muestra fallback.
- Cada sugerencia IA incluye `model_version` y `confidence_score`.
- Cuando el modo offline está activo, las sugerencias usan reglas locales.
- Las decisiones IA quedan registradas en `AuditLog`.
- El payload de IA sigue un schema estable (contract-first).

### Implementación inicial (scaffolding)
- App `apps.ai` creada con modelo `AiSuggestion` (trazabilidad IA).
- Endpoints:
  - `GET /api/ai/contract/` (contract-first).
  - `POST /api/ai/suggest/` (tiering quick/heavy + fallback).
- Registro en `AuditLog` con evento `ai_suggest`.
- Reglas rápidas (rule engine) para sugerencias críticas.
- Migración aplicada y tests básicos OK (3 tests).

### Avance adicional (tier heavy - Celery)
- Configuración base de Celery para ejecución asíncrona.
- Tarea `run_heavy_suggestion` para procesar sugerencias pesadas.
- `POST /api/ai/suggest/` en modo `heavy` encola tarea y marca estado `queued`.
- Se actualiza `AiSuggestion` con salida y latencia al completar.
- En pruebas, Celery usa broker `memory://` y modo eager.
- Endpoint de estado `GET /api/ai/suggestions/<id>/` para polling.
- Frontend con polling y aplicación automática de resultados heavy.
- Proveedores IA separados (`RuleProvider`, `HeavyProvider`) listos para reemplazo ML.
- Endpoint `POST /api/ai/assets/` y modelo `AiAsset` para hashes/embeddings.

## Módulo 6 - Análisis y mejoras (compatibilidad total)
### Compatibilidad garantizada con Módulos 0–5
- **Módulo 0**: reglas nunca permiten editar `company/sitec`; se heredan del request.
- **Módulo 1**: conserva nombres de campos actuales del wizard y esquema.
- **Módulo 2**: validaciones por paso no cambian formato de sync (`steps[]`).
- **Módulo 3**: constraints BD siguen vigentes; reglas no duplican con conflicto.
- **Módulo 4**: reglas usan schema del wizard (`wizard_schema_v1.json`).
- **Módulo 5**: reglas pueden usar sugerencias IA como *warning*, no como bloqueo.

### Checklist previo a implementación
- Definir **schema de reglas** (JSON/DB) con `code`, `severity`, `message`.
- Crear **motor de evaluación** reutilizable (UI + backend).
- Separar reglas **NOM** vs **negocio** vs **IA**.
- Versionar reglas (`rules_version`) y guardar en el reporte.
- Registrar validaciones críticas en `AuditLog`.
- Mapear reglas a pasos y campos del wizard sin renombrarlos.

### User stories
1) Como técnico, quiero mensajes claros y consistentes entre UI y backend.
2) Como supervisor, quiero saber qué reglas críticas fallaron y por qué.
3) Como auditor, quiero ver qué versión de reglas validó un reporte.
4) Como PM, quiero aplicar reglas NOM sin romper el flujo offline.

### Criterios de aceptación
- Las validaciones de Módulo 6 no cambian el payload de `steps[]`.
- Regla crítica bloquea avance; warning no bloquea.
- Cada regla devuelve `code`, `severity`, `message` y `field`.
- El reporte guarda `rules_version` usado en la validación.
- La UI sigue usando los mismos `name` de campo del wizard.

### Implementación inicial (scaffolding)
- App `apps.rules` con modelos `RuleSet` y `RuleItem`.
- Endpoint `POST /api/rules/evaluate/` para evaluar reglas por paso.
- Integración en `WizardValidateView` (agrega `rule_details` y `rules_version`).
- Tests del módulo rules y compatibilidad con wizard OK.

### Mejoras completadas (pendientes cerrados)
- Cache de reglas con `LocMemCache` y helper `get_active_ruleset`.
- Versionado de reglas guardado en `ReporteSemanal` (`rules_version`).
- Seed de reglas base (NOM/negocio) via `seed_rules`.

## Resumen global de avances y pendientes
### Avances implementados
- **Modulo 0**: modelos base (`Company`, `Sitec`, `UserProfile`, `AccessPolicy`, `AuditLog`), middleware `CompanySitecMiddleware`, permisos globales (`AccessPolicyPermission`), seed `seed_sitec`, auditoria funcional.
- **Modulo 1**: wizard 12 pasos con validaciones reales, autosave, offline + outbox, sync multiples pasos, resolucion de conflictos, UI extendida, accesibilidad avanzada.
- **Modulo 2**: sync core (`SyncSession`, `SyncItem`), endpoints de sync y pruebas OK; soporte de merge por entidad/campo con reglas especificas por entidad (modo `merge` y auto-merge wizard) y UI de conflictos por campo con diffs visuales.
- **Modulo 3**: constraints e indices en `ReporteSemanal`, `Proyecto`, `Evidencia` + versionado `wizard_data`.
- **Modulo 4**: wizard dinamico por schema, secciones, reglas condicionales, endpoint de schema, validaciones UI por regex/min/max, auditoria y tests OK.
- **Modulo 5**: app `ai` con contratos, sugerencias quick/heavy y **modelo ligero** (`LightModelProvider`) con configuracion versionada; pipeline IA real (dataset + job) y tests OK.
- **Modulo 7 (parcial)**: biblioteca base de componentes (`SitecComponents`), estilos compartidos, componentes avanzados (RiskMatrix, GanttLite, Kanban) integrados al wizard, con datos reales desde `/api/projects/proyectos/{id}/` y refresh configurable por flag HTML. **Nuevos**: firma canvas, uploader de evidencias, geolocalizacion, y Chatbot IA con aplicacion automatica de sugerencias.
- **Modulo 7 (parcial)**: mejora de evidencias con preview de imagenes y estado de firma (guardada/sin firma) en UI.
- **Modulo 7 (parcial)**: validacion avanzada de firma (canvas no vacio), export/descarga de firmas, autocompletado de metodo/fecha y estados unificados en componentes.
- **Modulo 8 (parcial)**: generacion PDF con ReportLab, versionado de documentos, endpoints de descarga/verificacion, UI de estado del PDF en wizard (estado, descarga y copia de enlace HTTPS), permisos por documento (tecnico/supervisor/PM/admin), flujo de firmas por rol (tecnico/supervisor/cliente) en UI+validacion y soporte de politicas `wizard.signature.require.*`, integracion con proveedor NOM-151 (configurable) con metricas de timbrado en `Document.metadata` y tarea async.
- **Modulo 8 (parcial)**: integracion NOM-151 real con modo `multipart` opcional (envio PDF) via settings.
- **Modulo 9 (parcial)**: endpoint base de KPIs (`GET /api/dashboard/`) con snapshots (jobs), comparativos extendidos por periodo (reportes/proyectos/riesgos), historico por periodo y agregados mensuales, **UI minima** de dashboard con KPIs, alertas y comparativos, tablas paginadas de proyectos/reportes, filtros por estado y enlaces a wizard.
- **Modulo 10 (parcial)**: KPIs ROI con snapshots por periodo (`/api/roi/`), job diario, historico/exports y panel en dashboard (ROI promedio, presupuestos y sobrecostos).

### Pendientes por modulo
- **Modulo 4**: sin pendientes criticos (opcional: tests UI snapshot si se requiere).
- **Modulo 5**: sin pendientes criticos (pipeline listo; proveedor ML real por definir).
- **Modulo 6**: sin pendientes criticos (reglas avanzadas pueden ampliarse).
- **Modulo 7**: sin pendientes criticos (flujos de firma y props unificados).
- **Modulo 8**: sin pendientes criticos (pendiente solo integracion de proveedor NOM-151 real si se define).
- **Modulo 9**: sin pendientes criticos (optimización y comparativos adicionales si se requieren).
- **Modulo 10**: sin pendientes criticos (reporting base listo; opcional: series extendidas).

## Backlog priorizado (tabla)
| Prioridad | Modulo | Entregable principal | Funcionalidades faltantes | Dependencias | Impacto |
| --- | --- | --- | --- | --- | --- |
| P0 | 8 | PDF y firmas digitales reales | Sello NOM-151 real | Proveedor de firma/timbrado | Alto |
| P0 | 9 | Dashboard gerencial | Comparativos historicos extendidos (si se requieren) | Modulo 3 (read models) | Medio |
| P0 | 0 | ABAC unificado | Motor de decision unico UI/API listo; catalogo base creado | N/A | Medio |
| P0 | 5 | IA real | Pipeline entrenamiento (listo), costos/throttling | Infra ML | Medio |
| P1 | 7 | Componentes reutilizables completos | Firma, galeria, evidencia, GeoPicker, Chatbot IA, props unificados | Modulo 8 (firma), Modulo 5 (IA) | Alto |
| P1 | 10 | KPIs/ROI | Metas y reportes ROI avanzados (opcional) | Modulo 9 | Medio |
| P1 | 2 | Sync avanzado | UX avanzada de conflictos (opcional: diffs visuales) | N/A | Alto |
| P2 | 4 | Compatibilidad de schema | Versionado v2/v3 y fallback seguro (completado) | N/A | Medio |
| P2 | 1 | UX operativa | Snapshot UI tests base (prod opcional) | Observabilidad | Medio |

## Roadmap sugerido (prioridades y tiempos)
### Prioridad P0 (2-3 semanas)
- Sello NOM-151 real (Modulo 8) si se integra proveedor externo.
- Comparativos historicos extendidos (Modulo 9) si se requiere.
- Motor ABAC unificado (Modulo 0) para UI/API.
- IA real inicial (Modulo 5) para habilitar Chatbot IA.

### Prioridad P1 (3-5 semanas)
- Componentes reutilizables completos (Modulo 7) y firma/galeria/evidencia.
- KPIs/ROI avanzados (Modulo 10) si se requiere.
- Sync avanzado (Modulo 2): merge por entidad y conflictos por campo (completado base + diffs).

## Resultados de pruebas recientes
- **Integridad, seguridad y funcionalidad**: 29 tests OK (`apps.frontend.tests`, `apps.frontend.tests_security`, `apps.frontend.tests_functional`).
- **Performance**: 9 tests OK (`apps.frontend.tests_performance`).
- **Fecha**: 2026-01-18.
- **Entorno**: Windows 10, Python en `.venv`, ejecución vía `manage.py test`.

### Prioridad P2 (4-6 semanas)
- UX operativa (tests snapshot base; prod opcional).
- Optimización performance + observabilidad avanzada.

## Resultado esperado
Una plataforma escalable y segura, con capacidad offline real, dashboards de alto rendimiento y cumplimiento normativo mexicano, lista para despliegue empresarial.

## Referencia rapida de endpoints y UI (nuevos)
**Endpoints API**
- `POST /api/policies/evaluate/` evaluar ABAC unificado.
- `GET /api/wizard/schema/?version=2` schema versionado con fallback seguro.
- `POST /api/wizard/analytics/` telemetria UX (eventos y tiempos).
- `POST /api/wizard/performance/metrics/` performance avanzada (FCP/LCP/CLS/TTFB).
- `GET /api/dashboard/` KPIs base para dashboard.
- `GET /api/dashboard/history/?period_days=30&limit=12` historico de snapshots.
- `GET /api/dashboard/aggregates/?limit=12` historico agregado mensual.
- `GET /api/roi/?period_days=30` KPIs ROI por periodo.
- `GET /api/roi/history/?period_days=30&limit=12` historico ROI.
- `GET /api/roi/export/?period_days=30&limit=50` export CSV.
- `POST /api/documents/documents/report/` generar PDF por `report_id`.
- `GET /api/documents/documents/{id}/` estado del documento.
- `GET /api/documents/documents/{id}/download/` descarga PDF.
- `GET /api/documents/verify/{token}/` verificacion por QR.

**Ejemplo `resolution` (sync con merge por entidad/campo)**
```json
{
  "resolution": {
    "123": {
      "mode": "merge",
      "fields": {
        "incidents_detail": "client",
        "status": "server"
      }
    },
    "11": "client"
  }
}
```

**Config NOM-151 (entorno)**
- `NOM151_PROVIDER_URL`
- `NOM151_API_KEY`
- `NOM151_TIMEOUT`
- `NOM151_VERIFY_SSL`
- `NOM151_RETRIES`
- `NOM151_BACKOFF_BASE`
- `NOM151_PROVIDER_MODE` (`json` o `multipart`)
- `NOM151_SEND_PDF` (true/false)

**Config dashboard snapshots (entorno)**
- `DASHBOARD_SNAPSHOT_TTL_MINUTES`
- `DASHBOARD_SNAPSHOT_PERIOD_DAYS` (ej: `7,30,90,180`)
- `DASHBOARD_AGGREGATE_MONTHS` (ej: `12`)

**Config ROI (entorno)**
- `ROI_SNAPSHOT_PERIOD_DAYS` (ej: `30,90,180`)

**Config IA real (entorno)**
- `AI_TRAIN_PROVIDER_URL`
- `AI_TRAIN_API_KEY`
- `AI_TRAIN_TIMEOUT`
- `AI_TRAIN_VERIFY_SSL`
- `AI_TRAIN_RETRIES`
- `AI_TRAIN_BACKOFF_BASE`
- `AI_TRAIN_SEND_FILE` (true/false)

**Comandos IA**
- `python manage.py run_ai_pipeline --since-days 180 --limit 5000`

**Politicas de firma (ABAC)**
- `wizard.signature.require.supervisor`
- `wizard.signature.require.client`
- `wizard.signature.require.tech`
 - Seed inicial en `seed_sitec` con condiciones por rol.
 - Reglas condicionales seed: `signature_supervisor_required=true` y `incidents=true`.

**URLs UI**
- `/dashboard/` dashboard gerencial (KPIs + tablas).
- `/wizard/1/?project=<uuid>` wizard con contexto de proyecto.
- `/wizard/1/?report=<uuid>` wizard con contexto de reporte.

---

## Pendientes para continuar mañana (por servicio)
**Auth/UI**
- Login publico opcional (actualmente se usa `/admin` con usuario `demo`).
- Confirmar que el wizard solo se renderiza cuando hay sesion activa.
- Limpiar cache del Service Worker si persisten 403 en wizard.

**Frontend Wizard**
- Validar que `GET /api/users/me/` y `GET /api/wizard/schema/` no regresan 403 tras login.
- Verificar que el nuevo mensaje de "Sesion requerida" se muestra sin errores JS.

**Performance/Observabilidad**
- Confirmar que `POST /api/wizard/performance/metrics/` responde 200 sin CSRF.
- Revisar que headers `X-Request-ID` y `X-Response-Time-ms` aparecen en respuestas API.

**NOM-151**
- Definir proveedor real: URL, API key, payload esperado.
- Decidir modo `json` vs `multipart` y si se envia PDF (`NOM151_SEND_PDF`).
- Ejecutar prueba end-to-end y revisar `Document.metadata.nom151`.

**IA real (pipeline)**
- Configurar `AI_TRAIN_PROVIDER_URL` y API key reales.
- Probar `python manage.py run_ai_pipeline --since-days 180 --limit 5000`.
- Verificar `AiTrainingJob` con `provider_job_id` y `status=submitted`.

**ABAC**
- Revisar y ajustar catalogo base por rol (si aplica a negocio real).
- Validar con `POST /api/policies/evaluate/` en acciones criticas.

**Infra/Jobs**
- Confirmar Redis activo y Celery worker/beat vivos.
- Verificar ejecucion de snapshots dashboard/ROI en logs.

**PWA**
- Verificar carga de iconos SVG (`icon-192.svg`, `icon-512.svg`).
