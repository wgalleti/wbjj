"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Personalização do admin Django
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API URLs
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/", include("apps.students.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.tenants.urls")),
    # Health checks
    path("health/", include("health_check.urls")),
    # OpenAPI Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Static and media files in development
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar URLs - apenas em desenvolvimento
    try:
        from debug_toolbar import urls as debug_toolbar_urls

        urlpatterns += [
            path("__debug__/", include(debug_toolbar_urls)),
        ]
    except ImportError:
        # Debug toolbar não está instalado
        pass
