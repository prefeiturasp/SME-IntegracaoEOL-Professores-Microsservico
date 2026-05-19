"""Configurações Django do microsserviço de professores."""

import os
import secrets
import sys as _sys
import urllib.parse
from pathlib import Path
from typing import Any

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
_POOL_OPTIONS = {
    "POOL_SIZE": DB_POOL_SIZE,
    "MAX_OVERFLOW": 0,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 1800,
    "PRE_PING": True,
}


def _parse_db_url(url: Any) -> dict:
    """Retorna configuração Django a partir de uma URL Postgres."""
    if not url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }

    if isinstance(url, bytes):
        url = url.decode("utf-8")

    parsed = urllib.parse.urlparse(str(url))
    return {
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "postgres",
        "PASSWORD": parsed.password or "postgres",
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or 5432),
        "POOL_OPTIONS": _POOL_OPTIONS,
    }


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("DJANGO_DEBUG", "1") == "0":
        raise ImproperlyConfigured(
            "A variável DJANGO_SECRET_KEY é obrigatória em produção."
        )
    SECRET_KEY = secrets.token_hex(50)

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.professores",
    "apps.turmas",
    "apps.funcionarios",
]

MIDDLEWARE = [
    "apps.core.middleware.PrefixMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

URL_BANCO_PROFESSORES = (
    None if "pytest" in _sys.modules else os.getenv("URL_BANCO_PROFESSORES")
)

DATABASES = {
    "default": _parse_db_url(URL_BANCO_PROFESSORES),
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, object]] = []

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

SCRIPT_PREFIX = os.getenv("APP_PREFIX", "")

FORCE_SCRIPT_NAME = SCRIPT_PREFIX or None
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

_static_prefix = SCRIPT_PREFIX.rstrip("/") if SCRIPT_PREFIX else ""
STATIC_URL = f"{_static_prefix}/static/"
MEDIA_URL = f"{_static_prefix}/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TEST_RUNNER = "config.test_runner.ProfessoresTestRunner"

NOME_APLICACAO = os.getenv(
    "NOME_APLICACAO", "SME-IntegracaoEOL-Professores-Microsservico"
)
AMBIENTE_APLICACAO = os.getenv("AMBIENTE_APLICACAO", "local")
NIVEL_LOG = os.getenv("NIVEL_LOG", "INFO")

API_KEY = os.getenv("API_KEY", "")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-IntegracaoEOL-Professores-Microsservico API",
    "DESCRIPTION": (
        "Endpoints do domínio Professores — SGP EOL.\n\n"
        "Dados servidos diretamente do PROFESSORES_DB (populado pelo ETL).\n"
        "Campos dependentes de outros domínios são retornados como null "
        "e enriquecidos pelo Transition Gateway."
    ),
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "padrao": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "padrao",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": NIVEL_LOG,
    },
}
