# Problema con Base de Datos - Soluciones

**Fecha**: 2026-01-23  
**Problema**: Error `disk I/O error` al generar datos de prueba

---

## ⚠️ Problema Detectado

El comando `generate_test_data_p0` y el script alternativo están fallando con error `disk I/O error` al intentar acceder a la base de datos SQLite.

---

## 🔍 Diagnóstico

**Base de datos**: `G:\SeguimientoProyectos\backend\db.sqlite3`
- **Tamaño**: 1,204,224 bytes (~1.2 MB)
- **Última modificación**: 2026-01-23 11:16:23
- **Solo lectura**: False

**Error**: `sqlite3.OperationalError: disk I/O error`

---

## 🔧 Soluciones Recomendadas

### Solución 1: Verificar Procesos

```powershell
# Verificar procesos Python
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object ProcessName, Id, Path

# Si hay procesos, cerrarlos
Stop-Process -Name python -Force
```

### Solución 2: Verificar Integridad de la Base de Datos

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py dbshell
```

En el shell de SQLite:
```sql
PRAGMA integrity_check;
```

Si hay errores, la base de datos puede estar corrupta.

### Solución 3: Hacer Backup y Recrear (Último Recurso)

```powershell
cd G:\SeguimientoProyectos\backend

# Backup
Copy-Item db.sqlite3 db.sqlite3.backup_$(Get-Date -Format "yyyyMMdd_HHmmss")

# Verificar si hay datos importantes antes de recrear
# Si es necesario, exportar datos primero
```

**⚠️ ADVERTENCIA**: Esto eliminará todos los datos existentes.

### Solución 4: Usar Django Shell Manualmente

Si el problema persiste, crear los datos manualmente usando Django shell:

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py shell
```

Luego copiar y pegar el código de `docs/INSTRUCCIONES_DATOS_PRUEBA_ALTERNATIVA.md` (Método 1).

---

## 📝 Alternativa: Usar Datos Existentes

Si la generación de datos no es crítica en este momento, puedes:

1. **Usar usuarios demo existentes**:
   - `demo` / `demo123` (Técnico)
   - `pm` / `pm123` (PM)
   - `supervisor` / `supervisor123` (Supervisor)
   - `admin` / `admin123` (Admin)

2. **Crear proyectos/reportes manualmente** desde la interfaz web

3. **Usar datos de producción** (si están disponibles) para pruebas

---

## ✅ Estado Actual

- ✅ **Implementación P0**: 100% completada
- ✅ **Tests automatizados**: 18/18 pasan
- ✅ **Migración**: Aplicada
- ✅ **Documentación**: Completa
- ⚠️ **Datos de prueba**: Pendiente (problema de I/O)

---

## 🎯 Recomendación

**Para continuar con las pruebas manuales**:

1. Usar usuarios demo existentes (`demo`, `pm`, `supervisor`, `admin`)
2. Crear proyectos/reportes manualmente desde la interfaz
3. O resolver el problema de I/O de la base de datos primero

**Para resolver el problema de I/O**:

1. Verificar que no haya procesos bloqueando la BD
2. Verificar integridad de la base de datos
3. Si es necesario, hacer backup y recrear

---

**Última actualización**: 2026-01-23
