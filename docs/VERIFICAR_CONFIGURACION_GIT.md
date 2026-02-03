# Verificar Configuración de Git

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 🔍 Verificar Configuración de Git

### Ver Configuración Global

```bash
# Ver toda la configuración global
git config --global --list

# Ver configuración específica
git config --global user.name
git config --global user.email
```

### Ver Configuración Local (del Repositorio)

```bash
# Ver toda la configuración local
git config --local --list

# Ver configuración específica
git config --local user.name
git config --local user.email
```

### Ver Configuración Actual (Global + Local)

```bash
# Ver nombre de usuario actual
git config user.name

# Ver email actual
git config user.email

# Ver toda la configuración (global + local)
git config --list
```

---

## ⚙️ Configurar Usuario y Email

### Configuración Global (para todos los repositorios)

```bash
# Configurar nombre
git config --global user.name "Tu Nombre"

# Configurar email
git config --global user.email "tu.email@example.com"

# Verificar
git config --global user.name
git config --global user.email
```

### Configuración Local (solo para este repositorio)

```bash
# Primero inicializar Git si no está inicializado
git init

# Configurar nombre
git config --local user.name "Tu Nombre"

# Configurar email
git config --local user.email "tu.email@example.com"

# Verificar
git config --local user.name
git config --local user.email
```

---

## 📋 Verificar Otras Configuraciones

### Ver Editor Configurado

```bash
git config core.editor
```

### Ver Branch por Defecto

```bash
git config init.defaultBranch
```

### Ver Configuración de Merge

```bash
git config merge.tool
```

---

## ✅ Checklist de Verificación

Antes de hacer commits, verificar:

- [ ] `user.name` está configurado
- [ ] `user.email` está configurado
- [ ] El email coincide con tu cuenta de GitHub
- [ ] La configuración es correcta (global o local según necesites)

---

## 🔧 Comandos Útiles

### Ver Todas las Configuraciones

```bash
# Ver todas las configuraciones (global + local)
git config --list

# Ver solo globales
git config --global --list

# Ver solo locales
git config --local --list

# Ver con origen (dónde está definida cada opción)
git config --list --show-origin
```

### Eliminar Configuración

```bash
# Eliminar configuración global
git config --global --unset user.name
git config --global --unset user.email

# Eliminar configuración local
git config --local --unset user.name
git config --local --unset user.email
```

### Editar Configuración Manualmente

```bash
# Editar configuración global
git config --global --edit

# Editar configuración local
git config --local --edit
```

---

## 📝 Notas

1. **Configuración Global vs Local**:
   - **Global**: Aplica a todos los repositorios en tu máquina
   - **Local**: Solo aplica al repositorio actual (sobrescribe la global)

2. **Prioridad**: La configuración local tiene prioridad sobre la global.

3. **GitHub**: El email debe coincidir con el email de tu cuenta de GitHub para que los commits se asocien correctamente.

---

## 🎯 Ejemplo Completo

```bash
# 1. Verificar configuración actual
git config user.name
git config user.email

# 2. Si no está configurado, configurarlo
git config --global user.name "Juan Pérez"
git config --global user.email "juan.perez@example.com"

# 3. Verificar que se configuró correctamente
git config --global --list | grep user

# 4. Verificar en el repositorio actual
git config user.name
git config user.email
```

---

**Última actualización**: 2026-01-23
