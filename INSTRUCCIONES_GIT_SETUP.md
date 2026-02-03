# Instrucciones: Configurar Repositorio Git para GitHub

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## ✅ Preparación Completada

El proyecto está listo para ser subido a GitHub. Se han creado:

- ✅ `.gitignore` - Configuración completa
- ✅ `README.md` - README principal
- ✅ `docs/README.md` - Índice de documentación
- ✅ Scripts de organización
- ✅ Guías de configuración

---

## 🚀 Pasos para Subir a GitHub

### Paso 1: Organizar Documentación (Opcional)

Si los archivos de documentación no están bloqueados:

```powershell
# Ejecutar script de organización
.\scripts\organizar_documentacion.ps1
```

**Nota**: Si los archivos están abiertos en el editor, ciérralos primero o organízalos manualmente después.

### Paso 2: Verificar .gitignore

```bash
# Verificar que .gitignore existe y está completo
cat .gitignore
```

Asegúrate de que incluya:
- `.venv/` - Entorno virtual
- `*.sqlite3` - Base de datos
- `.env` - Variables de entorno
- `__pycache__/` - Archivos Python compilados

### Paso 3: Inicializar Repositorio Git

```bash
# En la raíz del proyecto
cd G:\SeguimientoProyectos

# Inicializar Git
git init

# Verificar estado
git status
```

### Paso 4: Agregar Archivos

```bash
# Agregar todos los archivos (respetando .gitignore)
git add .

# Ver qué se agregará
git status

# Verificar que NO se agreguen archivos sensibles:
# - .env
# - db.sqlite3
# - .venv/
# - *.pyc
```

### Paso 5: Primer Commit

```bash
# Commit inicial
git commit -m "Initial commit: SITEC sistema completo

- Rediseño frontend (Fases 1-5)
- MFA (Backend + Frontend)
- Rate Limiting Avanzado
- Navegación P0
- Tests automatizados
- Preparado para deployment en Render.com"
```

### Paso 6: Crear Repositorio en GitHub

1. Ir a [github.com](https://github.com)
2. Click en **"+"** → **"New repository"**
3. Configurar:
   - **Repository name**: `SeguimientoProyectos` o `sitec`
   - **Description**: "Sistema de Seguimiento de Proyectos SITEC"
   - **Visibility**: Private (recomendado) o Public
   - **NO** marcar "Initialize with README" (ya tenemos uno)
   - **NO** agregar .gitignore (ya tenemos uno)
   - **NO** agregar licencia (por ahora)
4. Click **"Create repository"**

### Paso 7: Conectar y Subir

```bash
# Agregar remote (reemplazar USERNAME y REPO_NAME)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Verificar
git remote -v

# Renombrar branch a main (si es necesario)
git branch -M main

# Subir código
git push -u origin main
```

---

## ✅ Verificación Post-Setup

### Verificar en GitHub

1. ✅ README.md se muestra correctamente
2. ✅ Estructura de directorios es correcta
3. ✅ No hay archivos sensibles visibles
4. ✅ Documentación está accesible

### Verificar Localmente

```bash
# Ver estado
git status

# Ver historial
git log

# Ver remotes
git remote -v
```

---

## 📝 Comandos Git Útiles

### Trabajo Diario

```bash
# Ver cambios
git status
git diff

# Agregar cambios
git add .
git add archivo_especifico.py

# Commit
git commit -m "Descripción del cambio"

# Push
git push origin main

# Pull (actualizar)
git pull origin main
```

### Branches

```bash
# Crear branch
git checkout -b feature/nueva-funcionalidad

# Ver branches
git branch

# Cambiar branch
git checkout main

# Merge
git merge feature/nueva-funcionalidad
```

---

## 🔒 Seguridad - Checklist

Antes de cada commit, verificar:

- [ ] No hay `.env` en el commit
- [ ] No hay `db.sqlite3` en el commit
- [ ] No hay `SECRET_KEY` hardcodeado
- [ ] No hay credenciales en el código
- [ ] `.gitignore` está actualizado

### Verificar antes de push

```bash
# Ver qué archivos se van a subir
git ls-files

# Buscar archivos sensibles
git ls-files | grep -E "\.env|\.key|\.pem|db\.sqlite"
```

---

## 📚 Documentación Relacionada

- `docs/GUIA_GIT_GITHUB.md` - Guía completa de Git/GitHub
- `docs/ESTRUCTURA_DOCUMENTACION.md` - Estructura de documentación
- `docs/RESUMEN_ORGANIZACION_GIT.md` - Resumen de organización

---

## 🎯 Próximos Pasos

1. ✅ Organizar documentación (cuando archivos no estén bloqueados)
2. ✅ Inicializar Git
3. ✅ Crear repositorio en GitHub
4. ✅ Subir código
5. ✅ Configurar GitHub Actions (opcional)
6. ✅ Configurar deployment automático (opcional)

---

**Estado**: ✅ **LISTO PARA GIT**

---

**Última actualización**: 2026-01-23
