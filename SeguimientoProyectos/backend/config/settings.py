from pathlib import Path
import os
import sys


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-me-in-env"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
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
]

# Cache local (reglas y lecturas frecuentes)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sitec-cache",
    }
}

# Celery (IA pesada y tareas async)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
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
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.CompanySitecMiddleware",
    "apps.audit.middleware.RequestMetricsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
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

# NOM-151 provider (timbrado)
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

# IA real (pipeline)
AI_TRAIN_PROVIDER_URL = os.getenv("AI_TRAIN_PROVIDER_URL", "")
AI_TRAIN_API_KEY = os.getenv("AI_TRAIN_API_KEY", "")
AI_TRAIN_TIMEOUT = int(os.getenv("AI_TRAIN_TIMEOUT", "20"))
AI_TRAIN_VERIFY_SSL = os.getenv("AI_TRAIN_VERIFY_SSL", "true").lower() == "true"
AI_TRAIN_RETRIES = int(os.getenv("AI_TRAIN_RETRIES", "1"))
AI_TRAIN_BACKOFF_BASE = float(os.getenv("AI_TRAIN_BACKOFF_BASE", "0.5"))
AI_TRAIN_SEND_FILE = os.getenv("AI_TRAIN_SEND_FILE", "false").lower() == "true"
