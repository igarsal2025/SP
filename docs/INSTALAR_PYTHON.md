# Guía de Instalación de Python - Windows

## 🎯 Objetivo

Instalar Python 3.11+ en Windows para poder ejecutar los tests y migraciones del proyecto SITEC Web.

## 📥 Opción 1: Instalación desde python.org (Recomendado)

### Paso 1: Descargar Python

1. Visita: https://www.python.org/downloads/
2. Haz clic en el botón grande "Download Python 3.12.x" (o la versión más reciente)
3. Se descargará un archivo `.exe` (ej: `python-3.12.0-amd64.exe`)

### Paso 2: Instalar Python

1. **Ejecuta el instalador** descargado
2. **IMPORTANTE**: Marca la casilla **"Add Python to PATH"** ✅
   - Esta es la opción más importante
   - Permite usar `python` desde cualquier terminal
3. Selecciona **"Install Now"** (instalación estándar)
   - O **"Customize installation"** si quieres personalizar
4. Espera a que termine la instalación
5. Haz clic en **"Close"**

### Paso 3: Verificar Instalación

Abre una **nueva** terminal PowerShell o CMD y ejecuta:

```powershell
python --version
```

Deberías ver algo como:
```
Python 3.12.0
```

Si ves esto, ¡Python está instalado correctamente!

## 📥 Opción 2: Instalación desde Microsoft Store

### Paso 1: Abrir Microsoft Store

1. Presiona `Win + S` y busca "Microsoft Store"
2. Abre la aplicación Microsoft Store

### Paso 2: Buscar e Instalar Python

1. Busca "Python 3.12" o "Python 3.11"
2. Selecciona la versión oficial de Python
3. Haz clic en "Obtener" o "Instalar"
4. Espera a que termine la instalación

### Paso 3: Verificar Instalación

Abre una **nueva** terminal y ejecuta:

```powershell
python --version
```

## 🔧 Opción 3: Usar py Launcher (Windows)

Windows incluye un launcher `py` que puede instalar Python automáticamente:

```powershell
# Esto abrirá Microsoft Store si Python no está instalado
py --version

# O instalar directamente
py -3.12
```

## ✅ Verificación Post-Instalación

### 1. Verificar Python

```powershell
python --version
# Debe mostrar: Python 3.11.x o superior
```

### 2. Verificar pip

```powershell
pip --version
# Debe mostrar: pip 23.x.x o superior
```

### 3. Verificar que está en PATH

```powershell
where.exe python
# Debe mostrar la ruta donde está instalado Python
```

## 🚀 Configurar el Proyecto

Una vez que Python esté instalado:

### Paso 1: Instalar Dependencias

```powershell
cd D:\SeguimientoProyectos
pip install -r requirements.txt
```

### Paso 2: Verificar Django

```powershell
cd backend
python manage.py --version
# Debe mostrar: 5.0.x o superior
```

### Paso 3: Crear Migraciones

```powershell
python manage.py makemigrations sync reports projects
python manage.py migrate
```

### Paso 4: Ejecutar Tests

```powershell
python manage.py test
```

## ⚠️ Troubleshooting

### Error: "python no se reconoce como comando"

**Solución:**
1. Python no está en PATH
2. Reinicia la terminal después de instalar
3. Si persiste, agrega manualmente a PATH:
   - Busca "Variables de entorno" en Windows
   - Edita PATH del sistema
   - Agrega: `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python312\`
   - O la ruta donde instalaste Python

### Error: "pip no se reconoce"

**Solución:**
```powershell
python -m ensurepip --upgrade
```

### Error: "Permission denied" al instalar paquetes

**Solución:**
```powershell
# Usar --user para instalar en el directorio del usuario
pip install --user -r requirements.txt
```

### Verificar Instalación Completa

```powershell
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar ubicación
where.exe python
where.exe pip

# Verificar módulos instalados
python -c "import django; print(django.__version__)"
```

## 📋 Checklist de Instalación

- [ ] Python 3.11+ descargado
- [ ] Python instalado con "Add to PATH" marcado
- [ ] Terminal reiniciada
- [ ] `python --version` funciona
- [ ] `pip --version` funciona
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Django funciona (`python manage.py --version`)
- [ ] Migraciones creadas
- [ ] Tests ejecutables

## 🎯 Siguiente Paso

Una vez que Python esté instalado y verificado:

1. Instalar dependencias: `pip install -r requirements.txt`
2. Crear migraciones: `python manage.py makemigrations`
3. Aplicar migraciones: `python manage.py migrate`
4. Ejecutar tests: `python manage.py test`

## 📚 Referencias

- **Python Official**: https://www.python.org/downloads/
- **Python Docs**: https://docs.python.org/3/
- **Django Docs**: https://docs.djangoproject.com/
