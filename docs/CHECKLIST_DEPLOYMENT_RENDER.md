# Checklist: Deployment en Render.com

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## ✅ Pre-Deployment

### Código
- [x] `requirements.txt` actualizado con dependencias de producción
- [x] `build.sh` creado y probado
- [x] `start.sh` creado y probado
- [x] `render.yaml` creado (opcional)
- [x] `settings.py` actualizado para PostgreSQL y WhiteNoise
- [x] Código en repositorio Git (igarsal2025/SP)
- [x] Branch `main` estable y actualizada
- [ ] Tests pasando localmente (verificar antes del deploy)

### Configuración
- [x] `.env` está en `.gitignore` (no se suben secretos)
- [x] `SECRET_KEY` no está hardcodeado (usa variable de entorno; Render genera)
- [x] `DEBUG=False` en producción (definido en render.yaml)
- [x] `ALLOWED_HOSTS` configurado (sitec-web.onrender.com en render.yaml)

---

## 🚀 Deployment

### Render Dashboard
- [ ] Cuenta Render creada
- [ ] Repositorio Git conectado
- [ ] Base de datos PostgreSQL creada
- [ ] Servicio Redis creado (opcional)
- [ ] Web Service creado
- [ ] Variables de entorno configuradas:
  - [ ] `SECRET_KEY`
  - [ ] `DEBUG=false`
  - [ ] `ALLOWED_HOSTS`
  - [ ] `DATABASE_URL`
  - [ ] `REDIS_URL` (opcional)
  - [ ] `RATE_LIMIT_ENABLED=true`
  - [ ] `CSP_ENABLED=true`
- [ ] Build exitoso
- [ ] Servicio funcionando

### Post-Deployment
- [ ] Migraciones ejecutadas
- [ ] Seed de datos ejecutado (`seed_sitec`)
- [ ] Usuario administrador creado
- [ ] Health checks pasando:
  - [ ] `/health/` retorna 200
  - [ ] `/health/detailed/` retorna 200
- [ ] Funcionalidades validadas:
  - [ ] Login funciona
  - [ ] MFA funciona
  - [ ] API endpoints responden
  - [ ] Archivos estáticos se sirven
  - [ ] Rate limiting funciona
- [ ] Tests ejecutados (si aplica)
- [ ] Logs revisados

### Celery (Opcional)
- [ ] Celery Worker creado
- [ ] Celery Beat creado
- [ ] Workers procesan tareas
- [ ] Beat scheduler funciona

### Dominio Personalizado (Opcional)
- [ ] Dominio agregado en Render
- [ ] DNS configurado
- [ ] SSL verificado
- [ ] `ALLOWED_HOSTS` actualizado

---

## 🔒 Seguridad

- [ ] `SECRET_KEY` generado y seguro
- [ ] `DEBUG=False` en producción
- [ ] Rate limiting habilitado
- [ ] CSP headers habilitados
- [ ] Variables sensibles en Render (no en código)
- [ ] HTTPS funcionando
- [ ] Credenciales rotadas

---

## 📊 Monitoreo

- [ ] Logs accesibles en Render Dashboard
- [ ] Health checks configurados
- [ ] Alertas configuradas (opcional)
- [ ] Métricas monitoreadas

---

## 🎯 Validación Final

- [ ] Sistema accesible públicamente
- [ ] Todas las funcionalidades funcionan
- [ ] Performance aceptable
- [ ] Sin errores en logs
- [ ] Backups configurados (PostgreSQL)

---

**Estado**: ✅ **Pre-deploy listo** (código, repo, config). Pendiente: tests locales y pasos en Render Dashboard.

Ver también: `docs/REVISION_PENDIENTES_ANTES_RENDER.md` para revisión antes de publicar.

---

**Última actualización**: 2026-01-26
