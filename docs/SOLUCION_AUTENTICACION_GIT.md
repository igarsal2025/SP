# Solución: Error de Autenticación Git (403)

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 🔴 Problema

```
remote: Permission to igarsal2025/SP.git denied to igarsal2024.
fatal: unable to access 'https://github.com/igarsal2025/SP.git/': The requested URL returned error: 403
```

**Causa**: Estás autenticado como `igarsal2024` pero intentas acceder al repositorio de `igarsal2025`.

---

## ✅ Soluciones

### ⚡ Solución Rápida (Ya Ejecutada)

Las credenciales de `igarsal2024` ya fueron eliminadas. Ahora necesitas:

1. **Crear Personal Access Token** en GitHub para `igarsal2025`
2. **Configurar el remote** con el usuario correcto
3. **Hacer push** usando el token

Ver sección "Pasos Recomendados" más abajo.

---

### Opción 1: Eliminar Credenciales Guardadas (Recomendado)

#### En Windows (PowerShell)

```powershell
# Ver credenciales guardadas
cmdkey /list | Select-String "git"

# Eliminar credenciales de GitHub
cmdkey /delete:git:https://github.com

# O eliminar todas las credenciales de GitHub
cmdkey /list | ForEach-Object {
    if ($_ -match "github") {
        $cred = $_ -replace ".*Target: (.+)", '$1'
        cmdkey /delete:$cred
    }
}
```

#### En Windows (CMD)

```cmd
# Ver credenciales
cmdkey /list

# Eliminar credenciales de GitHub
cmdkey /delete:git:https://github.com
```

#### Luego, al hacer push, Git pedirá credenciales nuevas:

```bash
# Al hacer push, Git pedirá usuario y contraseña/token
git push -u origin main

# Usuario: igarsal2025
# Contraseña: [Tu Personal Access Token de GitHub]
```

---

### Opción 2: Usar Personal Access Token (PAT)

GitHub ya no acepta contraseñas para HTTPS. Necesitas un **Personal Access Token (PAT)**.

#### 1. Crear Personal Access Token en GitHub

1. Ir a GitHub.com → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Configurar:
   - **Note**: "SITEC - SeguimientoProyectos"
   - **Expiration**: Elegir duración (90 días, 1 año, etc.)
   - **Scopes**: Marcar `repo` (acceso completo a repositorios)
4. Click **"Generate token"**
5. **Copiar el token inmediatamente** (solo se muestra una vez)

#### 2. Usar el Token

```bash
# Al hacer push, cuando pida contraseña, usar el token
git push -u origin main

# Usuario: igarsal2025
# Contraseña: [Pegar el Personal Access Token]
```

---

### Opción 3: Configurar URL con Usuario

```bash
# Cambiar la URL del remote para incluir el usuario
git remote set-url origin https://igarsal2025@github.com/igarsal2025/SP.git

# Verificar
git remote -v

# Ahora hacer push (pedirá contraseña/token)
git push -u origin main
```

---

### Opción 4: Usar SSH (Alternativa)

#### 1. Generar SSH Key

```bash
# Generar nueva SSH key
ssh-keygen -t ed25519 -C "inti.garcia@fgr.org.mx"

# Presionar Enter para ubicación por defecto
# Ingresar passphrase (opcional pero recomendado)
```

#### 2. Agregar SSH Key a GitHub

```bash
# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub
# O en Windows:
type C:\Users\inti.garcia\.ssh\id_ed25519.pub
```

1. Ir a GitHub.com → **Settings** → **SSH and GPG keys**
2. Click **"New SSH key"**
3. **Title**: "SITEC - Windows"
4. **Key**: Pegar el contenido de `id_ed25519.pub`
5. Click **"Add SSH key"**

#### 3. Cambiar Remote a SSH

```bash
# Cambiar URL a SSH
git remote set-url origin git@github.com:igarsal2025/SP.git

# Verificar
git remote -v

# Probar conexión
ssh -T git@github.com

# Hacer push
git push -u origin main
```

---

## 🔧 Verificar Configuración Actual

```bash
# Ver remote configurado
git remote -v

# Ver credenciales guardadas (Windows)
cmdkey /list | Select-String "git"

# Ver configuración de Git
git config --list | Select-String "credential"
```

---

## 📝 Pasos Recomendados (Solución Rápida)

### Paso 1: Eliminar Credenciales Antiguas

```powershell
# En PowerShell
cmdkey /delete:git:https://github.com
```

### Paso 2: Crear Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Marcar `repo`
4. Copiar el token

### Paso 3: Configurar Remote con Usuario

```bash
git remote set-url origin https://igarsal2025@github.com/igarsal2025/SP.git
```

### Paso 4: Hacer Push

```bash
git push -u origin main

# Cuando pida credenciales:
# Usuario: igarsal2025
# Contraseña: [Pegar el Personal Access Token]
```

---

## 🔒 Seguridad

- **NUNCA** compartas tu Personal Access Token
- **NUNCA** subas tokens al repositorio
- Los tokens tienen los mismos permisos que tu cuenta
- Revoca tokens que ya no uses

---

## ✅ Verificación

Después de configurar, verificar:

```bash
# Ver remote
git remote -v

# Probar push
git push -u origin main

# Si funciona, deberías ver:
# "Branch 'main' set up to track remote branch 'main' from 'origin'."
```

---

## 🆘 Troubleshooting

### Error: "fatal: could not read Username"

```bash
# Configurar usuario en la URL
git remote set-url origin https://igarsal2025@github.com/igarsal2025/SP.git
```

### Error: "remote: Invalid username or password"

- Verificar que estás usando un **Personal Access Token**, no tu contraseña
- Verificar que el token tiene permisos `repo`
- Verificar que el token no ha expirado

### Error: "Permission denied (publickey)" (SSH)

```bash
# Verificar que la SSH key está agregada
ssh -T git@github.com

# Si no funciona, agregar la key al ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

**Última actualización**: 2026-01-23
