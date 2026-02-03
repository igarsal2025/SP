# Instrucciones para Recrear Entorno Virtual

## Problema

El entorno virtual apunta a una ubicación incorrecta de Python:
```
did not find executable at 'D:\Users\...\python.exe': El dispositivo no está listo.
```

## Solución Rápida

### Opción 1: Comandos Manuales (Recomendado)

```powershell
# 1. Eliminar entorno virtual existente
Remove-Item -Recurse -Force .venv

# 2. Crear nuevo entorno virtual con Python correcto
python -m venv .venv

# 3. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 4. Verificar Python
python --version
python -c "import sys; print(sys.executable)"

# 5. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 6. Navegar a backend y ejecutar tests
cd backend
python manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration --verbosity=2
```

### Opción 2: Script Automatizado

```powershell
.\scripts\recrear_venv.ps1
```

## Verificación

Después de recrear, verifica:

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Verificar Python (debe mostrar ruta dentro de .venv)
python -c "import sys; print(sys.executable)"

# Debe mostrar algo como:
# G:\SeguimientoProyectos\.venv\Scripts\python.exe

# Verificar Django
python -c "import django; print(django.__version__)"
```

## Si el Script Falla

Ejecuta los comandos manualmente uno por uno:

```powershell
# 1. Eliminar
Remove-Item -Recurse -Force .venv

# 2. Crear
python -m venv .venv

# 3. Activar
.\.venv\Scripts\Activate.ps1

# 4. Instalar
pip install -r requirements.txt
```
