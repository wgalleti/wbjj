"""
URLs para gestão de alunos
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, GraduationViewSet, StudentViewSet

app_name = "students"

# Router para ViewSets
router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")
router.register(r"graduations", GraduationViewSet, basename="graduations")
router.register(r"attendances", AttendanceViewSet, basename="attendances")

urlpatterns = [
    path("", include(router.urls)),
]
