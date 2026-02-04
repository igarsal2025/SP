# Revisión de pendientes antes de publicar en Render

**Fecha**: 2026-01-26  
**Objetivo**: Verificar que todo esté listo antes del primer deploy en Render.

---

## ✅ Ya cumplido (Pre-Deploy)

### Código y repositorio
| Item | Estado |
|------|--------|
| `requirements.txt` con dependencias de producción (gunicorn, whitenoise, psycopg2, dj-database-url) | ✅ |
| `build.sh` y `start.sh` en raíz | ✅ |
| `render.yaml` en raíz (web, workers, Redis, PostgreSQL) | ✅ |
| `settings.py`: SECRET_KEY, DEBUG, ALLOWED_HOSTS desde variables de entorno | ✅ |
| `settings.py`: PostgreSQL (DATABASE_URL), WhiteNoise, Redis opcional | ✅ |
| Código en GitHub (igarsal2025/SP, rama `main`) | ✅ |
| Rama `main` estable y con últimos cambios subidos | ✅ |

### Configuración (en código)
| Item | Estado |
|------|--------|
| `.env` está en `.gitignore` (no se suben secretos) | ✅ |
| `SECRET_KEY` no hardcodeado (usa `SECRET_KEY` de env; Render lo genera) | ✅ |
| `DEBUG` y `ALLOWED_HOSTS` definidos en `render.yaml` para producción | ✅ |

### Render (en `render.yaml`)
| Item | Estado |
|------|--------|
| Redis plan free | ✅ |
| ALLOWED_HOSTS = sitec-web.onrender.com | ✅ |
| Un solo bloque `services:` (web, workers, Redis) | ✅ |
| Variables: SECRET_KEY (generateValue), DATABASE_URL, REDIS_URL, RATE_LIMIT, CSP | ✅ |

---

## 🔍 Verificar antes de publicar (en tu PC)

### 1. Tests locales
Activar el entorno virtual y ejecutar tests:

```powershell
cd g:\SeguimientoProyectos
.\.venv\Scripts\activate   # o: venv\Scripts\activate
pip install -r requirements.txt   # si hace falta
cd backend
python manage.py test
```

O desde la raíz (con venv activo):

```powershell
python run_tests.py
```

- [ ] Tests pasando localmente (requiere venv activo e instalación de dependencias)

### 2. Build local (opcional)
Comprobar que el build de Render no falle por dependencias:

```powershell
cd g:\SeguimientoProyectos
pip install -r requirements.txt
cd backend
python manage.py check
python manage.py migrate --noinput --check  # solo comprueba, no aplica
```

- [ ] `manage.py check` sin errores
- [ ] Migraciones sin conflictos

### 3. Documentación
- [ ] Leída `docs/PUBLICAR_GITHUB_A_RENDER.md` (pasos en Render)
- [ ] Leído `docs/CHECKLIST_DEPLOYMENT_RENDER.md` (checklist completo del deploy)

---

## 📋 Pendientes que se hacen en Render (día del deploy)

Esto no se hace en código; se hace en el dashboard de Render cuando publiques:

| Paso | Acción en Render |
|------|------------------|
| 1 | Cuenta Render creada |
| 2 | Conectar repo **igarsal2025/SP** (Blueprint o Web Service) |
| 3 | Aplicar Blueprint (crea PostgreSQL, Redis, Web Service, workers) o crear servicios a mano |
| 4 | Revisar variables de entorno (ya vienen de `render.yaml` si usas Blueprint) |
| 5 | Primer deploy → revisar logs |
| 6 | Ajustar `ALLOWED_HOSTS` si la URL real es distinta (ej. `sitec-web-xxxx.onrender.com`) |
| 7 | Ejecutar migraciones y seed (Shell o job): `python manage.py migrate`, `python manage.py seed_sitec`, `createsuperuser` |
| 8 | Validar: `/health/`, login, MFA, estáticos |

Detalle completo: `docs/CHECKLIST_DEPLOYMENT_RENDER.md`.

---

## 📌 Pendientes de producto (no bloquean el deploy)

Estos son mejoras de producto; el sistema puede publicarse en Render sin ellos:

- **P0 (crítico)**  
  Vistas de detalle/edición (proyectos, reportes, creación). Ver `docs/RESUMEN_AVANCES_PENDIENTES_2026_01_23.md` y `docs/PLAN_IMPLEMENTACION_PRIORIZADO.md`.
- **P1**  
  WebAuthn, integraciones NOM-151/IA, Go Live (migración de datos, formación).
- **P2**  
  Optimizaciones, observabilidad, CI/CD.

---

## Resumen

| Área | Estado | Acción |
|-----|--------|--------|
| Código y repo | ✅ Listo | Ninguna |
| Config y seguridad en código | ✅ Listo | Ninguna |
| Tests locales | ⏳ Por verificar | Ejecutar tests y marcar en checklist |
| Build/migraciones | ⏳ Opcional | `manage.py check` y `migrate --check` |
| Publicar en Render | ⏳ Pendiente | Seguir `docs/PUBLICAR_GITHUB_A_RENDER.md` cuando quieras hacer el primer deploy |

**Conclusión**: El proyecto está listo para publicar en Render. Solo falta **verificar tests locales** y, el día que quieras, seguir los pasos del dashboard en `docs/PUBLICAR_GITHUB_A_RENDER.md` y `docs/CHECKLIST_DEPLOYMENT_RENDER.md`.

---

**Última actualización**: 2026-01-26
