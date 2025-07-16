import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", ".localhost"]

# Detectar se está rodando dentro do Docker ou localmente
IS_DOCKER = os.environ.get("DOCKER_CONTAINER", "false").lower() == "true"

# Database - PostgreSQL sempre (Docker ou local conectando ao Docker)
if "DATABASE_URL" in os.environ:
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"])}
else:
    # Se dentro do Docker, usa hostname 'db'
    # Se local, conecta ao PostgreSQL do Docker via localhost
    postgres_host = "db" if IS_DOCKER else "localhost"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",  # Backend PostgreSQL padrão
            "NAME": os.environ.get("POSTGRES_DB", "wbjj_dev"),
            "USER": os.environ.get("POSTGRES_USER", "wbjj_user"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "wbjj_pass"),
            "HOST": os.environ.get("POSTGRES_HOST", postgres_host),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

# Redis Cache - Redis sempre (Docker ou local conectando ao Docker)
if "REDIS_URL" in os.environ:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ["REDIS_URL"],
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    # Se dentro do Docker, usa hostname 'redis'
    # Se local, conecta ao Redis do Docker via localhost
    redis_host = "redis" if IS_DOCKER else "localhost"
    redis_password = os.environ.get("REDIS_PASSWORD", "redis_pass")

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://:{redis_password}@{redis_host}:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

# Debug toolbar apenas em desenvolvimento local (não no Docker)
if DEBUG and not IS_DOCKER:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", *MIDDLEWARE]
    INTERNAL_IPS = ["127.0.0.1"]

# CORS para desenvolvimento
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Static e Media files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR.parent, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR.parent, "media")
