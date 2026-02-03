# Resumen: Generación de Datos de Prueba P0

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: ✅ Comando Creado

---

## 📋 Resumen

Se ha creado un comando de Django para generar datos de prueba que permiten validar manualmente todas las funcionalidades P0 implementadas.

---

## ✅ Comando Creado

**Archivo**: `backend/apps/frontend/management/commands/generate_test_data_p0.py`

**Funcionalidad**:
- Crea usuarios de prueba con diferentes roles
- Crea proyectos en diferentes estados
- Crea reportes en diferentes estados (draft, submitted, approved, rejected)
- Genera datos variados para cubrir todos los escenarios de prueba

---

## 🚀 Uso del Comando

### Comando Básico

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py generate_test_data_p0
```

### Limpiar y Regenerar

```powershell
python manage.py generate_test_data_p0 --clear
```

---

## 📊 Datos Generados

### Usuarios (4 usuarios)

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `test_pm` | `test123` | PM |
| `test_supervisor` | `test123` | Supervisor |
| `test_tecnico` | `test123` | Técnico |
| `test_admin` | `test123` | Admin |

### Proyectos (4 proyectos)

1. **[TEST P0] Proyecto En Progreso** - Estado: En Progreso, 45%
2. **[TEST P0] Proyecto Planificación** - Estado: Planificación, 0%
3. **[TEST P0] Proyecto Completado** - Estado: Completado, 100%
4. **[TEST P0] Proyecto En Pausa** - Estado: En Pausa, 25%

### Reportes (5 reportes)

- **2 reportes enviados** (submitted) - Para probar aprobación/rechazo
- **1 reporte aprobado** (approved) - Para verificar que no se puede rechazar
- **1 reporte rechazado** (rejected) - Para ver historial
- **1 reporte borrador** (draft) - Para verificar que no se puede rechazar

---

## 📝 Documentación

**Guía Completa**: `docs/GUIA_DATOS_PRUEBA_P0.md`

Incluye:
- Instrucciones detalladas de uso
- Escenarios de prueba paso a paso
- URLs de prueba
- Cómo limpiar datos

---

## ⚠️ Nota sobre Error de I/O

Si aparece un error `disk I/O error` al ejecutar el comando:

1. **Verificar que la base de datos no esté bloqueada**:
   - Cerrar cualquier proceso que esté usando la base de datos
   - Verificar que el servidor Django no esté corriendo

2. **Verificar permisos del archivo**:
   - Asegurarse de tener permisos de escritura en `backend/db.sqlite3`

3. **Reintentar**:
   - Esperar unos segundos y volver a ejecutar el comando

4. **Alternativa**: Crear datos manualmente usando Django shell:
   ```python
   python manage.py shell
   # Luego ejecutar el código del comando manualmente
   ```

---

## ✅ Estado

- ✅ Comando creado
- ✅ Documentación completa
- ⚠️ Pendiente: Ejecutar comando (requiere base de datos disponible)

---

**Última actualización**: 2026-01-23
