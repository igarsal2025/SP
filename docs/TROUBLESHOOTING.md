# Guía de Troubleshooting - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

Esta guía cubre problemas comunes y sus soluciones para el sistema SITEC.

---

## 🔧 Problemas Comunes

### 1. Error: "ModuleNotFoundError: No module named 'django'"

**Causa**: Entorno virtual no activado o Django no instalado.

**Solución**:
```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

---

### 2. Error: "django.db.utils.OperationalError: could not connect to server"

**Causa**: PostgreSQL no está corriendo o credenciales incorrectas.

**Solución**:
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Iniciar PostgreSQL si no está corriendo
sudo systemctl start postgresql

# Verificar credenciales en .env
DATABASE_URL=postgresql://user:password@localhost:5432/sitec_db
```

---

### 3. Error: "Static files not found"

**Causa**: Archivos estáticos no recolectados.

**Solución**:
```bash
python manage.py collectstatic --noinput
```

---

### 4. Error: "Permission denied" en archivos estáticos

**Causa**: Permisos incorrectos en directorio de archivos estáticos.

**Solución**:
```bash
# Ajustar permisos
sudo chown -R www-data:www-data backend/static/
sudo chmod -R 755 backend/static/
```

---

### 5. Error: "Rate limit exceeded" (429)

**Causa**: Rate limiting habilitado y límite alcanzado.

**Solución**:
- Esperar el período de ventana
- Aumentar límite en `.env`:
  ```bash
  RATE_LIMIT_REQUESTS=200
  RATE_LIMIT_WINDOW=60
  ```
- Deshabilitar temporalmente:
  ```bash
  RATE_LIMIT_ENABLED=false
  ```

---

### 6. Error: "Health check failing"

**Causa**: Dependencias (DB, cache) no disponibles.

**Solución**:
```bash
# Verificar base de datos
sudo systemctl status postgresql

# Verificar Redis (si está configurado)
sudo systemctl status redis

# Verificar logs
python manage.py check
```

---

### 7. Error: "ABAC policies not working"

**Causa**: Políticas no cargadas o cache desactualizado.

**Solución**:
```bash
# Re-ejecutar seed
python manage.py seed_sitec

# Limpiar cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

### 8. Error: "Trends not loading"

**Causa**: No hay datos históricos o cache corrupto.

**Solución**:
```bash
# Limpiar cache de tendencias
python manage.py shell
>>> from django.core.cache import cache
>>> cache.delete_pattern("dashboard_trends_*")

# Verificar que hay datos
python manage.py shell
>>> from apps.dashboard.models import DashboardSnapshot
>>> DashboardSnapshot.objects.count()
```

---

### 9. Error: "Export not working" (gráficos)

**Causa**: JavaScript no cargado o navegador incompatible.

**Solución**:
- Verificar consola del navegador (F12)
- Verificar que JavaScript está habilitado
- Probar en otro navegador
- Verificar que no hay bloqueadores de contenido

---

### 10. Error: "NOM-151 stamp always 'pendiente'"

**Causa**: Proveedor NOM-151 no configurado.

**Solución**:
```bash
# Configurar en .env
NOM151_PROVIDER_URL=https://provider-url.com/api
NOM151_API_KEY=your-api-key
```

**Nota**: El sistema funciona sin proveedor NOM-151, pero los sellos serán "pendiente".

---

### 11. Error: "AI suggestions not working"

**Causa**: Proveedores locales no funcionando o proveedor ML no configurado.

**Solución**:
```bash
# Verificar logs
tail -f backend/logs/ai.log

# Verificar que proveedores locales están disponibles
python manage.py shell
>>> from apps.ai.providers import RuleProvider
>>> provider = RuleProvider()
>>> provider.suggest("test")
```

**Nota**: El sistema funciona con proveedores locales sin configuración adicional.

---

### 12. Error: "Tests failing"

**Causa**: Entorno de test no configurado o datos de test incorrectos.

**Solución**:
```bash
# Verificar entorno virtual
source .venv/bin/activate

# Ejecutar tests con verbosidad
python manage.py test --verbosity=2

# Ejecutar tests específicos
python manage.py test apps.accounts.tests_permissions --verbosity=2
```

---

## 🔍 Diagnóstico

### 1. Verificar Estado del Sistema

```bash
# Health check básico
curl http://localhost:8000/health/

# Health check detallado
curl http://localhost:8000/health/detailed/
```

### 2. Verificar Logs

```bash
# Logs de Django
tail -f backend/logs/django.log

# Logs de Gunicorn
sudo journalctl -u sitec -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

### 3. Verificar Base de Datos

```bash
# Conectar a PostgreSQL
psql -U sitec_user -d sitec_db

# Verificar tablas
\dt

# Verificar datos
SELECT COUNT(*) FROM accounts_userprofile;
```

### 4. Verificar Cache

```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set("test", "value", 60)
>>> cache.get("test")
```

### 5. Verificar Permisos ABAC

```bash
# Usar script de validación
./scripts/validar_dashboard.sh

# O manualmente
curl -X POST http://localhost:8000/api/policies/evaluate/ \
  -H "Content-Type: application/json" \
  -u "username:password" \
  -d '{"action":"dashboard.view"}'
```

---

## 🛠️ Comandos Útiles

### Limpiar Cache

```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Recrear Base de Datos

```bash
# ⚠️ ADVERTENCIA: Esto elimina todos los datos
python manage.py flush
python manage.py migrate
python manage.py seed_sitec
```

### Verificar Configuración

```bash
python manage.py check --deploy
```

### Verificar Migraciones Pendientes

```bash
python manage.py showmigrations
```

### Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

---

## 📊 Monitoreo

### 1. Performance

```bash
# Verificar tiempo de respuesta
curl -w "@-" -o /dev/null -s http://localhost:8000/api/dashboard/kpi/

# Verificar queries lentas
python manage.py shell
>>> from django.db import connection
>>> for query in connection.queries:
...     if float(query['time']) > 0.1:
...         print(query)
```

### 2. Uso de Recursos

```bash
# CPU y Memoria
top
htop

# Disco
df -h
du -sh backend/

# Red
netstat -tulpn
```

---

## 🆘 Soporte

Si el problema persiste:

1. **Revisar logs**: Buscar errores en logs de Django, Gunicorn, Nginx
2. **Verificar documentación**: Revisar `docs/` para guías específicas
3. **Ejecutar validación**: Usar scripts de validación
4. **Recopilar información**:
   - Versión de Python: `python --version`
   - Versión de Django: `python manage.py version`
   - Logs relevantes
   - Mensaje de error completo

---

## 📝 Checklist de Troubleshooting

- [ ] Entorno virtual activado
- [ ] Dependencias instaladas
- [ ] Base de datos corriendo
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] Archivos estáticos recolectados
- [ ] Permisos correctos
- [ ] Logs revisados
- [ ] Health checks pasando
- [ ] Cache funcionando

---

**Última actualización**: 2026-01-18
