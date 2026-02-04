# Celery en Oracle Cloud Always Free

Objetivo: ejecutar Celery worker y beat en una VM gratuita (Always Free)
conectada a Redis y Postgres en Render.

## Requisitos
- VM Ubuntu 22.04 (Always Free)
- Acceso SSH a la VM
- Redis en Render (Key Value) y Postgres en Render
- Variables de entorno de produccion

## Pasos
1) Crear VM en Oracle Cloud (Always Free)
2) Abrir puertos de salida (default OK). No necesitas exponer Celery.
3) Conectarte por SSH
4) Ejecutar el script de instalacion (ver abajo)
5) Crear el archivo de entorno en la VM
6) Habilitar servicios systemd

## Script de instalacion
En la VM:
```
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git build-essential
```

Clonar repo:
```
git clone https://github.com/igarsal2025/SP.git
cd SP
```

Crear venv e instalar deps:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno
Crear `/etc/sitec/sitec.env` con:
```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=sitec-web.onrender.com
DATABASE_URL=...
REDIS_URL=...
```

## Systemd
Copiar los archivos de servicio desde `scripts/systemd/` a `/etc/systemd/system/`
en la VM:
```
sudo cp scripts/systemd/celery-worker.service /etc/systemd/system/
sudo cp scripts/systemd/celery-beat.service /etc/systemd/system/
```

Recargar systemd y habilitar servicios:
```
sudo systemctl daemon-reload
sudo systemctl enable --now celery-worker
sudo systemctl enable --now celery-beat
```

Ver logs:
```
sudo journalctl -u celery-worker -f
sudo journalctl -u celery-beat -f
```

## Seguridad recomendada
Limita `ipAllowList` de Redis en Render a la IP publica de la VM.
