# Guía Rápida: Deployment en Render.com

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 🚀 Deployment Rápido (15 minutos)

### 1. Preparar Código

```bash
# Asegúrate de que estos archivos existen:
# - build.sh (en raíz)
# - start.sh (en raíz)
# - render.yaml (opcional, en raíz)
# - requirements.txt actualizado
```

### 2. Crear Cuenta Render

1. Ir a [render.com](https://render.com)
2. Crear cuenta (GitHub, GitLab, o email)
3. Verificar email

### 3. Crear Base de Datos

1. **"New +"** → **"PostgreSQL"**
2. **Name**: `sitec-db`
3. **Plan**: `Free` (para pruebas) o `Starter` (producción)
4. Crear y copiar **Internal Database URL**

### 4. Crear Web Service

1. **"New +"** → **"Web Service"**
2. Conectar repositorio Git
3. Configurar:
   - **Name**: `sitec-web`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: `Free` o `Starter`

### 5. Variables de Entorno

En Web Service → **Environment**, agregar:

```
SECRET_KEY=<generar-key-seguro>
DEBUG=false
ALLOWED_HOSTS=sitec.onrender.com
DATABASE_URL=<desde-postgres-service>
```

### 6. Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Esperar build (2-5 minutos)
3. Verificar logs

### 7. Post-Deploy

```bash
# Conectar a servicio y ejecutar:
python manage.py migrate
python manage.py seed_sitec
python manage.py createsuperuser
```

---

## ✅ Verificación

```bash
# Health check
curl https://sitec.onrender.com/health/

# Debe retornar: {"status": "ok", ...}
```

---

## 📝 Notas

- **Primer deploy**: Puede tardar 5-10 minutos
- **Cold starts**: Servicios gratuitos pueden tener cold starts
- **Dominio**: Render proporciona `sitec.onrender.com` automáticamente
- **SSL**: Automático, no requiere configuración

---

**Para más detalles**: Ver `docs/PLAN_DEPLOYMENT_RENDER.md`
