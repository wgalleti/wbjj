import os

from .base import *

DEBUG = True

# Permitir todos os hosts para testes
ALLOWED_HOSTS = ["*"]

# Always use PostgreSQL for tests to support multitenancy
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "test_wbjj",
        "USER": "wbjj_user",
        "PASSWORD": "wbjj_pass",
        "HOST": "localhost",
        "PORT": "5432",
        "TEST": {
            "NAME": "test_wbjj_testing",
        },
    }
}

# Fast password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# In-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ALWAYS use migrations for django-tenants compatibility
# Remove the DisableMigrations completely

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable logging during tests unless DEBUG_TESTS is set
if not os.environ.get("DEBUG_TESTS", "0") == "1":
    LOGGING_CONFIG = None

# Test-specific settings
CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True  # Propagate exceptions

# Security settings for tests
SECRET_KEY = "test-secret-key-only-for-testing"
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Media files for tests
MEDIA_ROOT = "/tmp/wbjj_test_media"

# Force database migrations for all tests
MIGRATION_MODULES = {}  # Use default migrations

# Django Tenants specific settings for tests
TENANT_CREATION_FAKES_MIGRATIONS = False
TENANT_LIMIT_SET_CALLS = True
