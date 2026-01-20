from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[3]

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, "sqlite:///" + str(BASE_DIR / "db.sqlite3")),
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
)

env.read_env(str(BASE_DIR / ".env"))

DEBUG = env.bool("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
REDIS_URL = env.str("REDIS_URL") or (
    f"redis://{env.str('REDIS_HOST')}:6379/0" if env.str("REDIS_HOST") else ""
)
ENVIRONMENT = env.str("ENVIRONMENT")
MONGO_DB_URI = env.str("MONGO_DB_URI")
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
    "apps.users",
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
        "DIRS": [BASE_DIR / "templates"],
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
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
