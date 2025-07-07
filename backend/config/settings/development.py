from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Backend padrão para T001 (setup)
        'NAME': 'wbjj_dev',                        # Será alterado para tenant_schemas na T004
        'USER': 'wbjj_user',
        'PASSWORD': 'wbjj_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Cache Redis para desenvolvimento
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Debug toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']
