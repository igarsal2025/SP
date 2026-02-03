# Guía Rápida: Autenticarse con igarsal2025

**Fecha**: 2026-01-23

---

## ✅ Credenciales Antiguas Eliminadas

Las credenciales de `igarsal2024` ya fueron eliminadas del sistema.

---

## 🚀 Pasos para Autenticarse con igarsal2025

### Paso 1: Crear Personal Access Token

1. Ir a: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Configurar:
   - **Note**: "SITEC - SeguimientoProyectos"
   - **Expiration**: 90 días o 1 año
   - **Scopes**: Marcar `repo` (acceso completo)
4. Click **"Generate token"**
5. **Copiar el token** (solo se muestra una vez)

---

### Paso 2: Configurar Remote

```bash
# Si ya tienes el repositorio inicializado
cd G:\SeguimientoProyectos

# Ver remote actual
git remote -v

# Configurar con usuario igarsal2025
git remote set-url origin https://igarsal2025@github.com/igarsal2025/SP.git

# Verificar
git remote -v
```

---

### Paso 3: Hacer Push

```bash
# Hacer push
git push -u origin main
```

**Cuando pida credenciales**:
- **Usuario**: `igarsal2025`
- **Contraseña**: [Pegar el Personal Access Token que copiaste]

---

## 🔧 Script Automático

También puedes usar el script:

```powershell
.\scripts\configurar_git_igarsal2025.ps1
```

---

## ✅ Verificación

```bash
# Verificar remote
git remote -v

# Debe mostrar:
# origin  https://igarsal2025@github.com/igarsal2025/SP.git (fetch)
# origin  https://igarsal2025@github.com/igarsal2025/SP.git (push)
```

---

## 🆘 Si Sigue Fallando

1. **Verificar que el token tiene permisos `repo`**
2. **Verificar que el token no ha expirado**
3. **Eliminar credenciales manualmente**:
   ```powershell
   cmdkey /list
   # Buscar y eliminar cualquier credencial de GitHub
   cmdkey /delete:"LegacyGeneric:target=git:https://..."
   ```

---

**Para más detalles**: Ver `docs/SOLUCION_AUTENTICACION_GIT.md`
