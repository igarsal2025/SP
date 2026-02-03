# Instrucciones para Crear Migraciones - Módulo 2

## 📋 Apps Creadas

Se han creado 3 nuevas apps que requieren migraciones:

1. ✅ `apps/sync`
2. ✅ `apps/reports`
3. ✅ `apps/projects`

## 🚀 Crear Migraciones

### Paso 1: Crear Migraciones

```bash
cd backend
python manage.py makemigrations sync
python manage.py makemigrations reports
python manage.py makemigrations projects
```

O todas juntas:

```bash
python manage.py makemigrations sync reports projects
```

### Paso 2: Aplicar Migraciones

```bash
python manage.py migrate
```

### Paso 3: Verificar

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Verificar que las tablas se crearon
python manage.py dbshell
# Luego en SQLite:
# .tables
# Deberías ver: sync_syncsession, sync_syncitem, reports_reportesemanal, etc.
```

## 📊 Modelos que se Crearán

### App `sync`
- `sync_syncsession` - Sesiones de sincronización
- `sync_syncitem` - Items sincronizados

### App `reports`
- `reports_reportesemanal` - Reportes semanales
- `reports_evidencia` - Evidencias
- `reports_incidente` - Incidentes

### App `projects`
- `projects_proyecto` - Proyectos
- `projects_tarea` - Tareas
- `projects_riesgo` - Riesgos
- `projects_presupuesto` - Presupuestos
- `projects_proyecto_technicians` - Tabla M2M para técnicos

## ⚠️ Notas Importantes

### Dependencias entre Apps

Las apps tienen relaciones:
- `reports.ReporteSemanal` → `projects.Proyecto` (FK opcional)
- Asegúrate de crear migraciones en orden o Django las manejará automáticamente

### Índices

Los modelos tienen índices compuestos para optimización:
- Filtrado por company/sitec
- Búsquedas por fechas
- Relaciones con usuarios

### Campos JSON

Varios modelos usan `JSONField`:
- `wizard_data` en ReporteSemanal
- `metadata` en varios modelos
- `sugerencias_ia` y `predicciones` para IA

Estos campos requieren PostgreSQL en producción, pero SQLite los soporta en desarrollo.

## ✅ Verificación Post-Migración

Después de aplicar migraciones, verifica:

1. **Tablas creadas**:
   ```bash
   python manage.py dbshell
   .tables
   ```

2. **Admin funcionando**:
   - Acceder a `/admin/`
   - Verificar que aparecen las apps: Sync, Reports, Projects

3. **API funcionando**:
   ```bash
   # Probar endpoints
   curl http://localhost:8000/api/sync/sessions/
   curl http://localhost:8000/api/reports/reportes/
   curl http://localhost:8000/api/projects/proyectos/
   ```

## 🔧 Troubleshooting

### Error: "No such table"

Si hay errores de tablas no encontradas:
```bash
# Eliminar migraciones (solo en desarrollo)
rm apps/sync/migrations/0*.py
rm apps/reports/migrations/0*.py
rm apps/projects/migrations/0*.py

# Recrear
python manage.py makemigrations sync reports projects
python manage.py migrate
```

### Error: "Circular dependency"

Si hay dependencias circulares:
- Django las maneja automáticamente
- Si persiste, revisar imports en models.py

### Error: "Field doesn't have a default"

Si hay campos sin default:
- Revisar que todos los campos opcionales tengan `null=True, blank=True`
- O proporcionar `default` en el modelo

## 📝 Próximos Pasos Después de Migraciones

1. ✅ Ejecutar tests
2. ✅ Probar endpoints en Postman/curl
3. ✅ Configurar datos de prueba (fixtures)
4. ✅ Integrar con wizard (conectar wizard → ReporteSemanal)
