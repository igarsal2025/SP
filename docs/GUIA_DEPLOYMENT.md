# Guía de Deployment - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

Esta guía cubre el proceso completo de deployment del sistema SITEC, desde la configuración inicial hasta la puesta en producción.

---

## 🚀 Pre-requisitos

### Software Requerido

- **Python**: 3.10 o superior
- **PostgreSQL**: 12 o superior (recomendado para producción)
- **Redis**: 6.0 o superior (opcional, para cache y Celery)
- **Nginx**: 1.18 o superior (recomendado para producción)
- **Gunicorn**: Para servir la aplicación Django

### Dependencias del Sistema

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql postgresql-server redis nginx
```

---

## 📦 Instalación

### 1. Clonar Repositorio

```bash
git clone <repository-url>
cd SeguimientoProyectos
```

### 2. Crear Entorno Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows
```

### 3. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en `backend/`:

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/sitec_db

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Sitec
DEFAULT_SITEC_SCHEMA=sitec

# Proveedores Opcionales
# NOM-151 (opcional)
NOM151_PROVIDER_URL=
NOM151_API_KEY=

# IA ML (opcional)
AI_TRAIN_PROVIDER_URL=
AI_TRAIN_API_KEY=

# Cache (opcional - usar Redis en producción)
CACHE_URL=redis://localhost:6379/1

# Celery (opcional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security (opcional)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

CSP_ENABLED=true
CSP_DEFAULT_SRC='self'
CSP_SCRIPT_SRC='self' 'unsafe-inline'
CSP_STYLE_SRC='self' 'unsafe-inline'
```

### 5. Configurar Base de Datos

```bash
# Crear base de datos
sudo -u postgres createdb sitec_db
sudo -u postgres createuser sitec_user

# Configurar permisos
sudo -u postgres psql -c "ALTER USER sitec_user WITH PASSWORD 'your-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sitec_db TO sitec_user;"
```

### 6. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 7. Crear Usuario Administrador

```bash
python manage.py createsuperuser
```

### 8. Seed de Datos Iniciales

```bash
python manage.py seed_sitec
```

---

## 🔧 Configuración de Producción

### 1. Configurar Gunicorn

Crear archivo `gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

### 2. Crear Systemd Service

Crear `/etc/systemd/system/sitec.service`:

```ini
[Unit]
Description=SITEC Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/SeguimientoProyectos/backend
Environment="PATH=/path/to/SeguimientoProyectos/.venv/bin"
ExecStart=/path/to/SeguimientoProyectos/.venv/bin/gunicorn \
    --config gunicorn_config.py \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Activar servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sitec
sudo systemctl start sitec
```

### 3. Configurar Nginx

Crear `/etc/nginx/sites-available/sitec`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/SeguimientoProyectos/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/SeguimientoProyectos/backend/media/;
        expires 7d;
    }
}
```

Activar configuración:

```bash
sudo ln -s /etc/nginx/sites-available/sitec /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Configurar Celery (Opcional)

Crear `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/SeguimientoProyectos/backend
Environment="PATH=/path/to/SeguimientoProyectos/.venv/bin"
ExecStart=/path/to/SeguimientoProyectos/.venv/bin/celery -A config worker -l info

[Install]
WantedBy=multi-user.target
```

Crear `/etc/systemd/system/celery-beat.service`:

```ini
[Unit]
Description=Celery Beat
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/SeguimientoProyectos/backend
Environment="PATH=/path/to/SeguimientoProyectos/.venv/bin"
ExecStart=/path/to/SeguimientoProyectos/.venv/bin/celery -A config beat -l info

[Install]
WantedBy=multi-user.target
```

Activar servicios:

```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
```

---

## ✅ Validación Post-Deployment

### 1. Health Checks

```bash
# Health check básico
curl http://localhost:8000/health/

# Health check detallado
curl http://localhost:8000/health/detailed/
```

### 2. Scripts de Validación

```bash
# Linux/Mac
chmod +x scripts/validar_dashboard.sh
./scripts/validar_dashboard.sh

# Windows
.\scripts\validar_dashboard.ps1
```

### 3. Verificar Logs

```bash
# Logs de Gunicorn
sudo journalctl -u sitec -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Logs de Celery
sudo journalctl -u celery-worker -f
```

---

## 🔒 Seguridad

### 1. SSL/TLS

- Usar Let's Encrypt para certificados gratuitos
- Configurar renovación automática
- Forzar HTTPS en Nginx

### 2. Firewall

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. Variables de Entorno

- **Nunca** commitear `.env` al repositorio
- Usar secretos gestionados (AWS Secrets Manager, HashiCorp Vault)
- Rotar `SECRET_KEY` periódicamente

### 4. Rate Limiting

Habilitar en `.env`:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

---

## 📊 Monitoreo

### 1. Logs

- **Django**: `backend/logs/`
- **Gunicorn**: `journalctl -u sitec`
- **Nginx**: `/var/log/nginx/`
- **PostgreSQL**: `/var/log/postgresql/`

### 2. Métricas

- **Health Checks**: `/health/detailed/`
- **Performance**: Monitorear tiempo de respuesta
- **Cache**: Verificar hit rate
- **Database**: Monitorear queries lentas

### 3. Alertas

Configurar alertas para:
- Health checks fallando
- Tiempo de respuesta > 1s
- Uso de CPU/Memoria > 80%
- Errores 5xx

---

## 🔄 Actualizaciones

### 1. Backup

```bash
# Backup de base de datos
pg_dump -U sitec_user sitec_db > backup_$(date +%Y%m%d).sql

# Backup de media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz backend/media/
```

### 2. Deploy

```bash
# 1. Activar entorno virtual
source .venv/bin/activate

# 2. Pull cambios
git pull origin main

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 6. Reiniciar servicios
sudo systemctl restart sitec
sudo systemctl restart celery-worker celery-beat
```

---

## 🐛 Troubleshooting

Ver `docs/TROUBLESHOOTING.md` para problemas comunes.

---

## 📝 Checklist de Deployment

- [ ] Base de datos configurada
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] Usuario administrador creado
- [ ] Seed de datos ejecutado
- [ ] Gunicorn configurado y corriendo
- [ ] Nginx configurado y corriendo
- [ ] SSL/TLS configurado
- [ ] Firewall configurado
- [ ] Health checks pasando
- [ ] Scripts de validación pasando
- [ ] Logs monitoreados
- [ ] Backups configurados

---

**Última actualización**: 2026-01-18
