# Instrucciones: Ejecutar Generación de Datos de Prueba

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## ⚠️ Problema Detectado

El comando `generate_test_data_p0` está fallando con error `disk I/O error`. Esto indica que la base de datos SQLite está bloqueada o hay problemas de acceso.

---

## 🔧 Solución: Pasos para Ejecutar

### Paso 1: Verificar Servidor Django

**IMPORTANTE**: El servidor Django debe estar **cerrado** antes de ejecutar el comando.

```powershell
# Verificar procesos Python
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Si hay procesos, cerrarlos
Stop-Process -Name python -Force
```

### Paso 2: Verificar Base de Datos

```powershell
cd G:\SeguimientoProyectos\backend

# Verificar que existe
if (Test-Path "db.sqlite3") {
    Write-Host "Base de datos existe"
    Get-Item "db.sqlite3" | Select-Object Name, Length, LastWriteTime, IsReadOnly
} else {
    Write-Host "Base de datos no existe - ejecutar migraciones primero"
}
```

### Paso 3: Ejecutar Comando

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py generate_test_data_p0
```

---

## 🔄 Método Alternativo: Django Shell

Si el comando sigue fallando, usar Django shell:

### Paso 1: Abrir Shell

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py shell
```

### Paso 2: Ejecutar Código

Copiar y pegar el código completo de `docs/INSTRUCCIONES_DATOS_PRUEBA_ALTERNATIVA.md` (Método 1).

---

## ✅ Verificación

Después de generar los datos, verificar:

```python
# En Django shell
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal
from django.contrib.auth import get_user_model

User = get_user_model()

print(f"Usuarios test: {User.objects.filter(username__startswith='test_').count()}")
print(f"Proyectos TEST P0: {Proyecto.objects.filter(name__startswith='[TEST P0]').count()}")
print(f"Reportes TEST P0: {ReporteSemanal.objects.filter(project_name__startswith='[TEST P0]').count()}")
```

---

## 🐛 Troubleshooting

### Error: "disk I/O error"

**Causas posibles**:
1. Servidor Django corriendo
2. Otra instancia de Python accediendo a la BD
3. Problemas de permisos
4. Base de datos corrupta

**Soluciones**:
1. Cerrar todos los procesos Python
2. Esperar 5-10 segundos
3. Verificar permisos del archivo
4. Si persiste, hacer backup y recrear BD

### Error: "No module named django"

**Solución**: Activar entorno virtual correctamente

```powershell
cd G:\SeguimientoProyectos
.venv\Scripts\Activate.ps1
cd backend
python manage.py generate_test_data_p0
```

### Error: "Company/Sitec no encontrado"

**Solución**: Ejecutar primero seed

```powershell
python manage.py seed_sitec
python manage.py generate_test_data_p0
```

---

## 📝 Notas

- El comando es **idempotente**: puede ejecutarse múltiples veces sin duplicar datos
- Usa `--clear` para limpiar datos existentes antes de regenerar
- Los datos se identifican con prefijo `[TEST P0]`

---

**Última actualización**: 2026-01-23
