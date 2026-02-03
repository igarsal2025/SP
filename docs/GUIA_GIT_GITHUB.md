# Guía: Configurar Repositorio Git para GitHub

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 📋 Pre-requisitos

1. Cuenta en GitHub
2. Git instalado localmente
3. Código preparado y organizado

---

## 🚀 Pasos para Configurar Repositorio

### 1. Inicializar Repositorio Git

```bash
# En la raíz del proyecto
cd G:\SeguimientoProyectos

# Inicializar repositorio
git init

# Verificar estado
git status
```

### 2. Configurar .gitignore

El archivo `.gitignore` ya está creado. Verificar que incluya:

- ✅ Archivos Python compilados (`*.pyc`, `__pycache__/`)
- ✅ Entorno virtual (`.venv/`, `venv/`)
- ✅ Base de datos (`*.sqlite3`, `*.db`)
- ✅ Archivos de configuración sensibles (`.env`)
- ✅ Archivos temporales y logs
- ✅ Archivos de build y distribución

### 3. Agregar Archivos al Repositorio

```bash
# Agregar todos los archivos (respetando .gitignore)
git add .

# Verificar qué se agregará
git status

# Commit inicial
git commit -m "Initial commit: SITEC sistema completo"
```

### 4. Crear Repositorio en GitHub

1. Ir a [github.com](https://github.com)
2. Click en **"New repository"**
3. Configurar:
   - **Name**: `SeguimientoProyectos` o `sitec`
   - **Description**: "Sistema de Seguimiento de Proyectos SITEC"
   - **Visibility**: Private (recomendado) o Public
   - **NO** inicializar con README, .gitignore o licencia
4. Click **"Create repository"**

### 5. Conectar Repositorio Local con GitHub

```bash
# Agregar remote (reemplazar USERNAME y REPO_NAME)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Verificar remote
git remote -v

# Renombrar branch principal a main (si es necesario)
git branch -M main

# Push inicial
git push -u origin main
```

---

## 📁 Estructura Recomendada para Git

```
SeguimientoProyectos/
├── .gitignore                  # ✅ Incluir
├── README.md                   # ✅ Incluir
├── requirements.txt            # ✅ Incluir
├── build.sh                    # ✅ Incluir
├── start.sh                    # ✅ Incluir
├── render.yaml                 # ✅ Incluir (opcional)
├── backend/                    # ✅ Incluir
│   ├── apps/
│   ├── config/
│   └── static/
├── docs/                       # ✅ Incluir
│   ├── README.md
│   ├── deployment/
│   ├── security/
│   └── ...
├── scripts/                    # ✅ Incluir
└── .venv/                      # ❌ NO incluir (en .gitignore)
```

---

## ✅ Checklist Pre-Commit

Antes de hacer commit, verificar:

- [ ] `.gitignore` configurado correctamente
- [ ] No hay archivos sensibles (`.env`, `SECRET_KEY`, etc.)
- [ ] No hay archivos de base de datos (`*.sqlite3`)
- [ ] No hay archivos compilados (`*.pyc`, `__pycache__/`)
- [ ] No hay entorno virtual (`.venv/`)
- [ ] `README.md` actualizado
- [ ] Documentación organizada

---

## 🔒 Seguridad

### Archivos que NUNCA deben estar en Git

- ❌ `.env` - Variables de entorno
- ❌ `db.sqlite3` - Base de datos
- ❌ `SECRET_KEY` - Claves secretas
- ❌ `*.key`, `*.pem` - Certificados
- ❌ `credentials.json` - Credenciales
- ❌ Archivos con información sensible

### Verificar antes de commit

```bash
# Ver qué se va a commitear
git status

# Ver diferencias
git diff

# Ver archivos que se agregarán
git ls-files
```

---

## 📝 Comandos Git Útiles

### Configuración Inicial

```bash
# Configurar usuario (si no está configurado)
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@example.com"
```

### Trabajo Diario

```bash
# Ver estado
git status

# Agregar cambios
git add .

# Commit
git commit -m "Descripción del cambio"

# Push
git push origin main

# Pull (actualizar desde GitHub)
git pull origin main
```

### Branches

```bash
# Crear branch
git checkout -b feature/nueva-funcionalidad

# Cambiar branch
git checkout main

# Ver branches
git branch

# Merge branch
git merge feature/nueva-funcionalidad
```

---

## 🎯 Buenas Prácticas

### Commits

- ✅ Mensajes descriptivos y claros
- ✅ Commits pequeños y frecuentes
- ✅ Un commit por cambio lógico
- ❌ No commitear archivos temporales

### Branching

- ✅ `main` - Código estable
- ✅ `develop` - Desarrollo activo
- ✅ `feature/*` - Nuevas funcionalidades
- ✅ `fix/*` - Correcciones

### .gitignore

- ✅ Mantener actualizado
- ✅ Incluir todos los archivos temporales
- ✅ Revisar antes de cada commit

---

## 📚 Recursos

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [.gitignore Templates](https://github.com/github/gitignore)

---

**Última actualización**: 2026-01-23
