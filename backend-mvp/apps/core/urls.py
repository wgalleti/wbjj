"""
URLs para funcionalidades base do sistema
"""
from django.urls import path

from .views import (
    api_status,
    health_check,
    health_check_cache,
    health_check_database,
    health_check_quick,
    metrics,
    ping,
)

app_name = "core"

urlpatterns = [
    # Health checks
    path("health/", health_check, name="health-check"),
    path("health/quick/", health_check_quick, name="health-check-quick"),
    path("health/database/", health_check_database, name="health-check-database"),
    path("health/cache/", health_check_cache, name="health-check-cache"),
    # Monitoring
    path("metrics/", metrics, name="metrics"),
    path("status/", api_status, name="api-status"),
    path("ping/", ping, name="ping"),
]
