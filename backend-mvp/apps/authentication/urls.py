"""
URLs para autenticação e gestão de usuários
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    UserViewSet,
)

app_name = "authentication"

# Router para ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    # JWT Authentication
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # ViewSets URLs
    path("", include(router.urls)),
]
