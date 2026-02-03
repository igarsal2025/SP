# Guía para Corregir Entorno Virtual con Python Incorrecto

**Problema**: El entorno virtual apunta a una ubicación incorrecta de Python.

---

## 🔍 Diagnóstico

Si ves este error:
```
did not find executable at 'D:\Users\...\python.exe': El dispositivo no está listo.
```

Significa que el entorno virtual está configurado con una ruta de Python que no existe o no es accesible.

---

## 🔧 Solución Rápida

### Opción 1: Script Automatizado (Recomendado)

```powershell
# Desde la raíz del proyecto
.\scripts\corregir_entorno_virtual.ps1
```

Este script:
1. Busca Python instalado en tu sistema
2. Elimina el entorno virtual existente (si lo deseas)
3. Crea un nuevo entorno virtual con Python correcto
4. Instala las dependencias

### Opción 2: Manual

#### Paso 1: Encontrar Python Correcto

```powershell
# Probar diferentes comandos
python --version
py --version

# Buscar Python instalado
Get-Command python
Get-Command py
```

#### Paso 2: Eliminar Entorno Virtual Existente

```powershell
# Si existe .venv
Remove-Item -Recurse -Force .venv

# O si existe venv
Remove-Item -Recurse -Force venv
```

#### Paso 3: Crear Nuevo Entorno Virtual

```powershell
# Usar el Python encontrado
python -m venv .venv

# O especificar ruta completa
C:\Users\inti.garcia\AppData\Local\Programs\Python\Python3.14\python.exe -m venv .venv
```

#### Paso 4: Activar y Verificar

```powershell
.\.venv\Scripts\Activate.ps1

# Verificar que funciona
python --version
which python  # Debería mostrar la ruta dentro de .venv
```

#### Paso 5: Instalar Dependencias

```powershell
cd backend
pip install -r ..\requirements.txt
```

---

## 🎯 Ubicaciones Comunes de Python

En Windows, Python suele estar en:

1. **Python 3.14**:
   - `C:\Users\<usuario>\AppData\Local\Programs\Python\Python3.14\python.exe`
   - `C:\Python3.14\python.exe`

2. **Python 3.13**:
   - `C:\Users\<usuario>\AppData\Local\Programs\Python\Python3.13\python.exe`
   - `C:\Python3.13\python.exe`

3. **Python Launcher (py)**:
   - `C:\Windows\py.exe` (si está en PATH)

---

## ✅ Verificación

Después de corregir, verifica:

```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Verificar Python
python --version
python -c "import sys; print(sys.executable)"

# 3. Verificar Django
python -c "import django; print(django.__version__)"

# 4. Ejecutar tests
cd backend
python manage.py test apps.ai.tests_throttling --verbosity=2
```

---

## 🐛 Troubleshooting

### Error: "python no se reconoce como comando"

**Solución**: Agregar Python al PATH o usar `py` launcher:

```powershell
# Usar py launcher
py -3.14 -m venv .venv
```

### Error: "No se puede crear entorno virtual"

**Solución**: Verificar permisos y espacio en disco:

```powershell
# Verificar permisos
Test-Path . -IsValid

# Verificar espacio
Get-PSDrive C
```

### Error: "pip no se encuentra"

**Solución**: Instalar pip o usar Python con pip incluido:

```powershell
# Actualizar pip
python -m ensurepip --upgrade
```

---

## 📝 Notas Importantes

1. **No mover el entorno virtual**: Una vez creado, no lo muevas a otra ubicación
2. **Ruta absoluta**: El entorno virtual guarda la ruta absoluta de Python
3. **Recrear si es necesario**: Si cambias de ubicación de Python, recrea el entorno virtual

---

**Última actualización**: 2026-01-18
