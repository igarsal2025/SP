# Manual operativo y configuración

## 1) Prerrequisitos
- Windows 10 / PowerShell
- Python con entorno virtual `.venv`
- Redis instalado y corriendo
- Dependencias Python instaladas

## 2) Variables de entorno (resumen)
### NOM-151
- `NOM151_PROVIDER_URL`
- `NOM151_API_KEY`
- `NOM151_TIMEOUT`
- `NOM151_VERIFY_SSL`
- `NOM151_RETRIES`
- `NOM151_BACKOFF_BASE`
- `NOM151_PROVIDER_MODE` (`json` o `multipart`)
- `NOM151_SEND_PDF` (true/false)

### IA real
- `AI_TRAIN_PROVIDER_URL`
- `AI_TRAIN_API_KEY`
- `AI_TRAIN_TIMEOUT`
- `AI_TRAIN_VERIFY_SSL`
- `AI_TRAIN_RETRIES`
- `AI_TRAIN_BACKOFF_BASE`
- `AI_TRAIN_SEND_FILE` (true/false)

### Dashboards
- `DASHBOARD_SNAPSHOT_TTL_MINUTES`
- `DASHBOARD_SNAPSHOT_PERIOD_DAYS`
- `DASHBOARD_AGGREGATE_MONTHS`
- `ROI_SNAPSHOT_PERIOD_DAYS`

### Observabilidad
- `OBS_SLOW_REQUEST_MS`

## 3) Setup inicial (una vez)
1. Crear/activar entorno virtual:
   - `python -m venv .venv`
   - `.\.venv\Scripts\activate`
2. Instalar dependencias:
   - `pip install -r requirements.txt`
3. Migrar base de datos:
   - `python manage.py migrate`
4. Seed base (company/sitec/policies):
   - `python manage.py seed_sitec`

## 4) Redis (broker)
- Verifica puerto 6379:
  - `Test-NetConnection localhost -Port 6379`
- Iniciar Redis (si aplica):
  - `redis-server`

## 5) Celery (worker/beat)
- Worker:
  - `celery -A config worker -P solo -l info`
- Beat:
  - `celery -A config beat -l info`

## 6) Servidor Django
- `python manage.py runserver`

## 7) Operación NOM-151
1. Configura env vars NOM-151 (URL/API key/mode).
2. Modo `json`: envía metadatos.
3. Modo `multipart` + `NOM151_SEND_PDF=true`: envía PDF en `file`.
4. Validar en logs:
   - `Document.metadata.nom151` con `status/attempts/latency_ms`.

## 8) Operación IA real (pipeline)
1. Configura env vars de IA.
2. Ejecuta pipeline (dataset + job):
   - `python manage.py run_ai_pipeline --since-days 180 --limit 5000`
3. Tarea async (opcional):
   - `run_ai_training(company_id, sitec_id, created_by_id, since_days, limit)`
4. Verificar en BD:
   - Tabla `AiTrainingJob` con `status`, `dataset_path`, `provider_job_id`.

## 9) ABAC y catálogo de políticas
1. `seed_sitec` crea catálogo base por rol y acción.
2. Ajusta con `AccessPolicy` si se requiere granularidad.
3. Validar con:
   - `POST /api/policies/evaluate/`

## 10) Observabilidad y performance
- Headers en API: `X-Request-ID`, `X-Response-Time-ms`.
- Métricas UI: `POST /api/wizard/performance/metrics/`.
- UX telemetry: `POST /api/wizard/analytics/`.

## 11) Pruebas
- Ejecutar suite completa:
  - `python manage.py test`

## 12) Troubleshooting rápido
- **Celery no conecta**: validar Redis + `CELERY_BROKER_URL`.
- **NOM-151 sin sello**: revisar `NOM151_PROVIDER_URL`/payload/SSL.
- **IA sin job**: revisar `AI_TRAIN_PROVIDER_URL`/API key/logs.
- **Sync conflictos**: revisar banner y resolución por campo.
