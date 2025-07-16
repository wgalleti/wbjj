"""
URLs para sistema financeiro
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, PaymentMethodViewSet, PaymentViewSet

app_name = "payments"

# Router para ViewSets
router = DefaultRouter()
router.register(r"payment-methods", PaymentMethodViewSet, basename="payment-methods")
router.register(r"invoices", InvoiceViewSet, basename="invoices")
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
]
