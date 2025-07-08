"""
URLs para gestão de academias (tenants)
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TenantViewSet

app_name = "tenants"

# Router para ViewSets
router = DefaultRouter()
router.register(r"tenants", TenantViewSet, basename="tenants")

urlpatterns = [
    path("", include(router.urls)),
]
