# Guía Rápida - Instalar Python en Windows

## 🚀 Instalación Rápida (5 minutos)

### Paso 1: Descargar Python

1. Abre tu navegador
2. Ve a: **https://www.python.org/downloads/**
3. Haz clic en el botón grande **"Download Python 3.12.x"**
4. Se descargará un archivo `.exe`

### Paso 2: Instalar Python

1. **Ejecuta el archivo descargado** (ej: `python-3.12.0-amd64.exe`)
2. **⚠️ IMPORTANTE**: Marca la casilla **"Add Python to PATH"** ✅
   - Esta casilla está en la parte inferior de la ventana
   - Es CRÍTICA para que funcione desde la terminal
3. Haz clic en **"Install Now"**
4. Espera a que termine (1-2 minutos)
5. Haz clic en **"Close"**

### Paso 3: Verificar Instalación

1. **Cierra todas las ventanas de terminal/PowerShell abiertas**
2. Abre una **nueva** terminal PowerShell
3. Escribe:
   ```powershell
   python --version
   ```
4. Deberías ver: `Python 3.12.0` (o similar)

✅ **Si ves la versión, Python está instalado correctamente**

## 📦 Instalar Dependencias del Proyecto

Una vez que Python esté instalado:

```powershell
# 1. Ir al directorio del proyecto
cd D:\SeguimientoProyectos

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar Django
cd backend
python manage.py --version
```

## ✅ Verificación Completa

Ejecuta estos comandos para verificar todo:

```powershell
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Django (después de instalar dependencias)
python -c "import django; print(django.__version__)"
```

## 🎯 Siguiente Paso: Crear Migraciones

Una vez que todo esté instalado:

```powershell
cd D:\SeguimientoProyectos\backend
python manage.py makemigrations sync reports projects
python manage.py migrate
python manage.py test
```

## ⚠️ Problemas Comunes

### "python no se reconoce como comando"

**Solución:**
1. Reinicia la terminal (ciérrala y ábrela de nuevo)
2. Si persiste, Python no se agregó al PATH
3. Reinstala Python y asegúrate de marcar "Add Python to PATH"

### "pip no se reconoce"

**Solución:**
```powershell
python -m ensurepip --upgrade
```

### "Permission denied"

**Solución:**
```powershell
pip install --user -r requirements.txt
```

## 📋 Checklist

- [ ] Python descargado desde python.org
- [ ] Python instalado con "Add to PATH" ✅
- [ ] Terminal reiniciada
- [ ] `python --version` funciona
- [ ] `pip --version` funciona
- [ ] Dependencias instaladas
- [ ] Django funciona

## 🎉 ¡Listo!

Una vez completado, podrás:
- ✅ Crear migraciones
- ✅ Ejecutar tests
- ✅ Ejecutar el servidor Django
- ✅ Usar todas las funcionalidades del proyecto

---

**Tiempo estimado**: 5-10 minutos
**Dificultad**: Fácil
