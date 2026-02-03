# Publicar el proyecto desde GitHub a Render

Guía paso a paso para conectar el repositorio **igarsal2025/SP** con Render y poner la app en producción.

---

## Requisitos previos

- Repositorio en GitHub: **https://github.com/igarsal2025/SP**
- Cuenta en [Render.com](https://render.com) (gratis para empezar)

---

## Opción A: Blueprint (recomendado, todo en uno)

El proyecto incluye `render.yaml` (Blueprint). Render crea Web Service, PostgreSQL, Redis y Workers en un solo paso.

### 1. Entra en Render

1. Ve a **https://dashboard.render.com**
2. Inicia sesión (con GitHub es más fácil para conectar el repo)

### 2. Conectar GitHub

1. En el dashboard: **"New +"** → **"Blueprint"**
2. Si te pide conectar GitHub:
   - **"Connect GitHub"** o **"Configure account"**
   - Autoriza a Render para acceder a tus repos
   - Elige **"Only select repositories"** y selecciona **igarsal2025/SP** (o **"All repositories"** si prefieres)
   - **Save**

### 3. Crear el Blueprint

1. De nuevo: **"New +"** → **"Blueprint"**
2. En **"Connect a repository"** elige: **igarsal2025/SP**
3. Render detectará el archivo **render.yaml** en la raíz.
4. Revisa los recursos que va a crear:
   - **sitec-web** (Web Service)
   - **sitec-db** (PostgreSQL)
   - **sitec-redis** (Redis)
   - **sitec-celery-worker** y **sitec-celery-beat** (workers)
5. **Plan**: si quieres gastar $0 al principio, cambia en `render.yaml` los `plan: starter` por `plan: free` donde exista (PostgreSQL free tiene límite de 90 días).
6. Pulsa **"Apply"** o **"Create Blueprint"**.

### 4. Esperar el primer deploy

- El **build** puede tardar 3–8 minutos.
- Revisa los **Logs** del servicio **sitec-web** por si hay errores.
- Cuando termine, la URL será algo como: **https://sitec-web.onrender.com**

### 5. Ajustar ALLOWED_HOSTS (si hace falta)

Si Django devuelve "DisallowedHost":

1. En Render: **sitec-web** → **Environment**
2. Añade o edita **ALLOWED_HOSTS** y pon tu URL real, por ejemplo:
   - `sitec-web.onrender.com`
   - O la URL que Render te muestre (ej. `sitec-web-xxxx.onrender.com`)

### 6. Datos iniciales (primera vez)

En Render no puedes ejecutar `manage.py` a mano como en tu PC. Opciones:

**A) Usar un One-off job (recomendado)**  
1. **sitec-web** → **Shell** (si Render lo ofrece en tu plan)  
   O crea un **Background Worker** temporal con:
   - Start Command: `cd backend && python manage.py migrate && python manage.py seed_sitec`
   - Ejecútalo una vez y luego puedes borrarlo o dejarlo.

**B) Crear superusuario por Django Admin**  
1. Entra a **https://tu-app.onrender.com/admin/**  
2. Si no hay usuarios, tendrás que usar la consola (Shell) de Render para:
   ```bash
   cd backend && python manage.py createsuperuser
   ```
   (Render → sitec-web → **Shell** tab, si está disponible)

---

## Opción B: Crear servicios a mano (sin Blueprint)

Si prefieres no usar el Blueprint o Render no te deja usarlo:

### 1. Base de datos PostgreSQL

1. **"New +"** → **"PostgreSQL"**
2. **Name:** `sitec-db`
3. **Plan:** Free (pruebas) o Starter
4. **Create Database**
5. Copia la **Internal Database URL** (la usarás como `DATABASE_URL`)

### 2. Redis (opcional pero recomendado para Celery)

1. **"New +"** → **"Redis"**
2. **Name:** `sitec-redis`
3. **Plan:** Free o Starter
4. **Create Redis**
5. Copia la **Internal Redis URL**

### 3. Web Service (Django)

1. **"New +"** → **"Web Service"**
2. Conecta el repo **igarsal2025/SP**
3. Configuración:
   - **Name:** `sitec-web`
   - **Region:** el más cercano a ti
   - **Branch:** `main`
   - **Root Directory:** (dejar vacío, la raíz del repo)
   - **Environment:** **Python 3**
   - **Build Command:** `./build.sh`
   - **Start Command:** `./start.sh`
   - **Plan:** Free o Starter

4. **Environment Variables** (añadir):

   | Key           | Value |
   |---------------|--------|
   | `PYTHON_VERSION` | `3.11.0` |
   | `SECRET_KEY`  | (generar uno aleatorio largo) |
   | `DEBUG`       | `false` |
   | `ALLOWED_HOSTS` | `sitec-web.onrender.com` |
   | `DATABASE_URL` | (pegar Internal Database URL de sitec-db) |
   | `REDIS_URL`   | (pegar Internal Redis URL de sitec-redis, o dejar vacío si no usas Redis) |

5. **Create Web Service**

### 4. Deploy

- El primer deploy se lanza solo.
- Revisa **Logs** en **sitec-web**.
- URL final: **https://sitec-web.onrender.com** (o la que Render asigne).

---

## Despliegues automáticos

Con la Opción A o B, una vez conectado el repo:

- Cada **push a la rama `main`** en GitHub dispara un nuevo deploy en Render.
- No hace falta hacer nada más; Render hace build y reinicia el servicio.

---

## Resumen rápido

| Paso | Acción |
|------|--------|
| 1 | Entrar en [dashboard.render.com](https://dashboard.render.com) |
| 2 | **New +** → **Blueprint** (o Web Service + DB + Redis si es manual) |
| 3 | Conectar repo **igarsal2025/SP** |
| 4 | Aplicar Blueprint o configurar Build/Start y variables |
| 5 | Esperar el build y revisar logs |
| 6 | Ajustar **ALLOWED_HOSTS** si Django lo pide |
| 7 | Ejecutar migraciones y `seed_sitec` (Shell o job) |

---

## Enlaces útiles

- [Render Dashboard](https://dashboard.render.com)
- [Render – Deploy from Git](https://render.com/docs/deploy-from-git)
- [Render – Blueprint Spec](https://render.com/docs/blueprint-spec)
- Repo: **https://github.com/igarsal2025/SP**
