from datetime import timedelta
import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[3]
_templates_dir = Path(os.getenv("DJANGO_TEMPLATES_DIR", BASE_DIR / "templates"))
if not _templates_dir.exists():
    cwd_templates = Path.cwd() / "templates"
    if cwd_templates.exists():
        _templates_dir = cwd_templates
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, ""),
    POSTGRES_DB_NAME=(str, ""),
    POSTGRES_DB_USER=(str, ""),
    POSTGRES_DB_PASSWORD=(str, ""),
    POSTGRES_DB_HOST=(str, ""),
    POSTGRES_DB_PORT=(int, 5432),
    REPLICA_DATABASE_URL=(str, ""),
    REDIS_URL=(str, ""),
    REDIS_HOST=(str, ""),
    ENVIRONMENT=(str, "dev"),
    MONGO_DB_URI=(str, ""),
    MONGO_TODAY_TTL_SECONDS=(int, 86400),
    MONGO_LAST_7_DAYS_TTL_SECONDS=(int, 604800),
    MONGO_LAST_30_DAYS_TTL_SECONDS=(int, 2592000),
    MONGO_LAST_6_MONTHS_TTL_SECONDS=(int, 15552000),
    MONGO_THIS_YEAR_TTL_SECONDS=(int, 31536000),
)

_read_dotenv = os.getenv("DJANGO_READ_DOT_ENV_FILE", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
_dotenv_path = BASE_DIR / ".env"
if _read_dotenv and _dotenv_path.exists():
    env.read_env(str(_dotenv_path))

DEBUG = env.bool("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
REDIS_URL = env.str("REDIS_URL") or (
    f"redis://{env.str('REDIS_HOST')}:6379/0" if env.str("REDIS_HOST") else ""
)
ENVIRONMENT = env.str("ENVIRONMENT")
MONGO_DB_URI = env.str("MONGO_DB_URI")
MONGO_TODAY_TTL_SECONDS = env.int("MONGO_TODAY_TTL_SECONDS")
MONGO_LAST_7_DAYS_TTL_SECONDS = env.int("MONGO_LAST_7_DAYS_TTL_SECONDS")
MONGO_LAST_30_DAYS_TTL_SECONDS = env.int("MONGO_LAST_30_DAYS_TTL_SECONDS")
MONGO_LAST_6_MONTHS_TTL_SECONDS = env.int("MONGO_LAST_6_MONTHS_TTL_SECONDS")
MONGO_THIS_YEAR_TTL_SECONDS = env.int("MONGO_THIS_YEAR_TTL_SECONDS")
TCP_HEALTH_URL = env.str("TCP_HEALTH_URL", default="http://tcp:7001/health")
MQTT_HEALTH_URL = env.str("MQTT_HEALTH_URL", default="http://mqtt:7002/health")
if not REDIS_URL and not DEBUG and ENVIRONMENT != "test":
    raise RuntimeError("REDIS_URL or REDIS_HOST must be configured")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
    "apps.users",
    "apps.service_zones",
    "apps.telemetry",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.RequestIdMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [_templates_dir],
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

database_url = env.str("DATABASE_URL")
if not database_url and env.str("POSTGRES_DB_HOST"):
    database_url = (
        f"postgres://{env.str('POSTGRES_DB_USER')}:{env.str('POSTGRES_DB_PASSWORD')}"
        f"@{env.str('POSTGRES_DB_HOST')}:{env.int('POSTGRES_DB_PORT')}"
        f"/{env.str('POSTGRES_DB_NAME')}"
    )
if not database_url:
    if DEBUG or ENVIRONMENT == "test":
        database_url = "sqlite:///" + str(BASE_DIR / "db.sqlite3")
    else:
        raise RuntimeError("DATABASE_URL or POSTGRES_DB_* must be configured")

DATABASES = {"default": env.db_url("DATABASE_URL", default=database_url)}

if env.str("REPLICA_DATABASE_URL"):
    DATABASES["replica"] = env.db("REPLICA_DATABASE_URL")

DATABASE_ROUTERS = ["common.db_router.PrimaryReplicaRouter"]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env.str("THROTTLE_ANON_RATE", default="60/min"),
        "user": env.str("THROTTLE_USER_RATE", default="600/min"),
        "login": env.str("THROTTLE_LOGIN_RATE", default="10/min"),
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Green Power API",
    "DESCRIPTION": "Production API documentation.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        seconds=sum(
            x * int(t)
            for x, t in zip(
                (3600, 60, 1), env.str("JWT_ACCESS_TOKEN_LIFETIME", default="00:15:00").split(":")
            )
        )
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        seconds=sum(
            x * int(t)
            for x, t in zip(
                (3600, 60, 1), env.str("JWT_REFRESH_TOKEN_LIFETIME", default="07:00:00").split(":")
            )
        )
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": env.str("JWT_ALGORITHM", default="HS256"),
    "SIGNING_KEY": env.str("JWT_SIGNING_KEY", default=SECRET_KEY),
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "common.logging.RequestIdFilter",
        }
    },
    "formatters": {
        "json": {
            "()": "common.logging.JsonFormatter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "json",
            "level": "DEBUG",
        }
        ,
        "warning_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "when": "midnight",
            "backupCount": 30,
            "encoding": "utf-8",
            "formatter": "json",
            "level": "WARNING",
            "delay": True,
        },
    },
    "root": {
        "handlers": ["console", "warning_file"],
        "level": "DEBUG",
    },
}
