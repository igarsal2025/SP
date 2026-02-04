from pathlib import Path
import os
import sys

# Soporte para DATABASE_URL (Render, Heroku, etc.)
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Soporte para WhiteNoise (opcional, para producción)
try:
    import whitenoise
    WHITENOISE_AVAILABLE = True
except ImportError:
    WHITENOISE_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key desde variable de entorno (requerido en producción)
SECRET_KEY = os.getenv("SECRET_KEY", "replace-me-in-env")

# Debug desde variable de entorno
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Allowed hosts desde variable de entorno
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "apps.companies",
    "apps.accounts",
    "apps.localization",
    "apps.audit",
    "apps.ai",
    "apps.rules",
    "apps.frontend",
    "apps.sync",
    "apps.reports",
    "apps.projects",
    "apps.documents",
    "apps.dashboard",
    "apps.roi",
    "apps.transactions",
]

# Cache - usar Redis si está disponible (producción), sino memoria local (desarrollo)
REDIS_URL = os.getenv("REDIS_URL") or os.getenv("CACHE_URL")
if REDIS_URL:
    try:
        # Intentar usar Redis cache
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": REDIS_URL,
            }
        }
    except Exception:
        # Fallback a memoria local si Redis no está disponible
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "sitec-cache",
            }
        }
else:
    # Cache local para desarrollo
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sitec-cache",
        }
    }

# Celery (IA pesada y tareas async)
# Usar REDIS_URL si está disponible, sino CELERY_BROKER_URL
REDIS_URL_FOR_CELERY = REDIS_URL or os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL") or REDIS_URL_FOR_CELERY
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND") or REDIS_URL_FOR_CELERY
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"

CELERY_BEAT_SCHEDULE = {
    "dashboard_snapshots_15m": {
        "task": "apps.dashboard.tasks.refresh_dashboard_snapshots",
        "schedule": 900.0,
        "args": (None,),
    },
    "dashboard_aggregates_daily": {
        "task": "apps.dashboard.tasks.refresh_dashboard_aggregates",
        "schedule": 86400.0,
        "args": (None,),
    },
    "roi_snapshots_daily": {
        "task": "apps.roi.tasks.refresh_roi_snapshots",
        "schedule": 86400.0,
        "args": (None,),
    },
}

if "test" in sys.argv:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
]

# Agregar WhiteNoise middleware solo si está disponible
if WHITENOISE_AVAILABLE:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")  # WhiteNoise para archivos estáticos (producción)

MIDDLEWARE.extend([
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "apps.accounts.middleware_rate_limit.AdvancedRateLimitMiddleware",  # Rate limiting avanzado (opcional)
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",  # MFA middleware
    "apps.frontend.middleware.UserContextMiddleware",  # Contexto de usuario para frontend
    "apps.accounts.middleware.CompanySitecMiddleware",
    "apps.accounts.middleware_security.SecurityHeadersMiddleware",  # Security headers (CSP, etc.)
    "apps.audit.middleware.RequestMetricsMiddleware",
    "apps.accounts.middleware_observability.ObservabilityMiddleware",  # Métricas de observabilidad
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
])

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Base de datos - usar DATABASE_URL si está disponible (Render, Heroku, etc.)
# Si no, usar SQLite para desarrollo
if dj_database_url and os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # SQLite para desarrollo local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

if "test" in sys.argv:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Para collectstatic
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise storage (producción) - solo si está disponible
if WHITENOISE_AVAILABLE:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TEST_RUNNER = "config.test_runner.AppDiscoverRunner"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "apps.accounts.permissions.AccessPolicyPermission",
    ],
}

# Configuración de logging para depuración
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "apps.accounts.services": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "apps.accounts.permissions": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# NOM-151 provider (timbrado) - OPCIONAL
# El sistema funciona completamente sin proveedor NOM-151 configurado.
# Si no se configura, los documentos se generan con sello "pendiente".
# Para habilitar timbrado real, configurar NOM151_PROVIDER_URL y NOM151_API_KEY.
NOM151_PROVIDER_URL = os.getenv("NOM151_PROVIDER_URL", "")
NOM151_API_KEY = os.getenv("NOM151_API_KEY", "")
NOM151_TIMEOUT = int(os.getenv("NOM151_TIMEOUT", "15"))
NOM151_VERIFY_SSL = os.getenv("NOM151_VERIFY_SSL", "true").lower() == "true"
NOM151_RETRIES = int(os.getenv("NOM151_RETRIES", "1"))
NOM151_BACKOFF_BASE = float(os.getenv("NOM151_BACKOFF_BASE", "0.5"))
NOM151_PROVIDER_MODE = os.getenv("NOM151_PROVIDER_MODE", "json")
NOM151_SEND_PDF = os.getenv("NOM151_SEND_PDF", "false").lower() == "true"

# Dashboard snapshots
DASHBOARD_SNAPSHOT_TTL_MINUTES = int(os.getenv("DASHBOARD_SNAPSHOT_TTL_MINUTES", "15"))
DASHBOARD_SNAPSHOT_PERIOD_DAYS = [
    int(value) for value in os.getenv("DASHBOARD_SNAPSHOT_PERIOD_DAYS", "7,30,90,180").split(",")
]
DASHBOARD_AGGREGATE_MONTHS = int(os.getenv("DASHBOARD_AGGREGATE_MONTHS", "12"))

# ROI snapshots
ROI_SNAPSHOT_PERIOD_DAYS = [
    int(value) for value in os.getenv("ROI_SNAPSHOT_PERIOD_DAYS", "30,90,180").split(",")
]

# Observabilidad
OBS_SLOW_REQUEST_MS = int(os.getenv("OBS_SLOW_REQUEST_MS", "800"))
# OBSERVABILITY_ENABLED: Habilita métricas de observabilidad (default: True)
# El middleware recopila: timing de requests, conteo de requests, errores por endpoint
OBSERVABILITY_ENABLED = os.getenv("OBSERVABILITY_ENABLED", "true").lower() == "true"

# Rate Limiting Avanzado - OPCIONAL
# El sistema funciona sin rate limiting, pero se recomienda habilitarlo en producción.
# RATE_LIMIT_ENABLED: Habilita rate limiting (default: False)
# RATE_LIMIT_REQUESTS: Número máximo de requests por IP por ventana (default: 100)
# RATE_LIMIT_WINDOW: Ventana de tiempo en segundos para IP (default: 60)
# RATE_LIMIT_USER_REQUESTS: Número máximo de requests por usuario por ventana (default: 200)
# RATE_LIMIT_USER_WINDOW: Ventana de tiempo en segundos para usuario (default: 60)
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_USER_REQUESTS = int(os.getenv("RATE_LIMIT_USER_REQUESTS", "200"))
RATE_LIMIT_USER_WINDOW = int(os.getenv("RATE_LIMIT_USER_WINDOW", "60"))

# Configuración de rate limiting por endpoint
# Formato: {"path_pattern": {"method": {"ip": {...}, "user": {...}}}}
# Ejemplo:
# RATE_LIMIT_ENDPOINTS = {
#     "/api/auth/login/": {
#         "POST": {
#             "ip": {"requests": 5, "window": 60},  # 5 intentos por minuto por IP
#             "user": {"requests": 3, "window": 300},  # 3 intentos por 5 minutos por usuario
#         }
#     },
#     "/api/projects/*": {
#         "default": {
#             "ip": {"requests": 50, "window": 60},
#             "user": {"requests": 100, "window": 60},
#         }
#     },
# }
RATE_LIMIT_ENDPOINTS = {}

# Paths excluidos del rate limiting (además de los defaults)
RATE_LIMIT_EXCLUDED_PATHS = [
    "/health/",
    "/health/detailed/",
    "/api/metrics/",
]

# Security Headers
# CSP (Content Security Policy) - OPCIONAL pero recomendado en producción
# Configurar según necesidades de la aplicación
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CSP Headers (Content Security Policy) - OPCIONAL
# Habilitar CSP: CSP_ENABLED=true
# Ajustar según necesidades de la aplicación
CSP_ENABLED = os.getenv("CSP_ENABLED", "false").lower() == "true"
CSP_DEFAULT_SRC = os.getenv("CSP_DEFAULT_SRC", "'self'")
CSP_SCRIPT_SRC = os.getenv("CSP_SCRIPT_SRC", "'self' 'unsafe-inline'")
CSP_STYLE_SRC = os.getenv("CSP_STYLE_SRC", "'self' 'unsafe-inline'")
CSP_IMG_SRC = os.getenv("CSP_IMG_SRC", "'self' data: https:")
CSP_FONT_SRC = os.getenv("CSP_FONT_SRC", "'self' data:")
CSP_CONNECT_SRC = os.getenv("CSP_CONNECT_SRC", "'self'")

# IA real (pipeline) - OPCIONAL
# El sistema funciona completamente sin proveedor ML externo configurado.
# Los proveedores locales (RuleProvider, LightModelProvider, HeavyProvider) funcionan sin configuración.
# Para habilitar entrenamiento con proveedor ML externo, configurar AI_TRAIN_PROVIDER_URL y AI_TRAIN_API_KEY.
AI_TRAIN_PROVIDER_URL = os.getenv("AI_TRAIN_PROVIDER_URL", "")
AI_TRAIN_API_KEY = os.getenv("AI_TRAIN_API_KEY", "")
AI_TRAIN_TIMEOUT = int(os.getenv("AI_TRAIN_TIMEOUT", "20"))
AI_TRAIN_VERIFY_SSL = os.getenv("AI_TRAIN_VERIFY_SSL", "true").lower() == "true"
AI_TRAIN_RETRIES = int(os.getenv("AI_TRAIN_RETRIES", "1"))
AI_TRAIN_BACKOFF_BASE = float(os.getenv("AI_TRAIN_BACKOFF_BASE", "0.5"))
AI_TRAIN_SEND_FILE = os.getenv("AI_TRAIN_SEND_FILE", "false").lower() == "true"

# IA Throttling y Costos - OPCIONAL
# El sistema funciona sin throttling, pero se recomienda habilitarlo en producción.
# AI_THROTTLE_ENABLED: Habilita throttling de requests de IA (default: False)
# AI_THROTTLE_QUICK_PER_HOUR: Máximo de requests "quick" por hora por usuario (default: 100)
# AI_THROTTLE_QUICK_PER_DAY: Máximo de requests "quick" por día por usuario (default: 1000)
# AI_THROTTLE_HEAVY_PER_HOUR: Máximo de requests "heavy" por hora por usuario (default: 10)
# AI_THROTTLE_HEAVY_PER_DAY: Máximo de requests "heavy" por día por usuario (default: 100)
# AI_COST_TRACKING_ENABLED: Habilita tracking de costos estimados (default: False)
AI_THROTTLE_ENABLED = os.getenv("AI_THROTTLE_ENABLED", "false").lower() == "true"
AI_THROTTLE_QUICK_PER_HOUR = int(os.getenv("AI_THROTTLE_QUICK_PER_HOUR", "100"))
AI_THROTTLE_QUICK_PER_DAY = int(os.getenv("AI_THROTTLE_QUICK_PER_DAY", "1000"))
AI_THROTTLE_HEAVY_PER_HOUR = int(os.getenv("AI_THROTTLE_HEAVY_PER_HOUR", "10"))
AI_THROTTLE_HEAVY_PER_DAY = int(os.getenv("AI_THROTTLE_HEAVY_PER_DAY", "100"))
AI_COST_TRACKING_ENABLED = os.getenv("AI_COST_TRACKING_ENABLED", "false").lower() == "true"
