"""
Views para sistema financeiro

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet
- SEMPRE documentar com drf-spectacular
- SEMPRE usar permissions granulares
"""
from decimal import Decimal
from typing import ClassVar

from django.db.models import Sum
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import CanManagePayments, IsAdminOrReadOnly
from apps.core.viewsets import TenantViewSet

from .models import Invoice, Payment, PaymentMethod
from .serializers import (
    ConfirmPaymentSerializer,
    InvoiceCreateSerializer,
    InvoiceSerializer,
    InvoiceStatsSerializer,
    PaymentCreateSerializer,
    PaymentMethodSerializer,
    PaymentSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar métodos de pagamento", tags=["payments"]),
    create=extend_schema(summary="Criar método de pagamento", tags=["payments"]),
    retrieve=extend_schema(summary="Obter método de pagamento", tags=["payments"]),
    update=extend_schema(summary="Atualizar método de pagamento", tags=["payments"]),
    destroy=extend_schema(summary="Deletar método de pagamento", tags=["payments"]),
)
class PaymentMethodViewSet(TenantViewSet):
    """ViewSet para métodos de pagamento"""

    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes: ClassVar = [IsAdminOrReadOnly]
    search_fields: ClassVar = ["name", "code"]
    filterset_fields: ClassVar = ["is_online", "is_active"]
    ordering: ClassVar = ["name"]


@extend_schema_view(
    list=extend_schema(summary="Listar faturas", tags=["payments"]),
    create=extend_schema(summary="Criar fatura", tags=["payments"]),
    retrieve=extend_schema(summary="Obter fatura", tags=["payments"]),
    update=extend_schema(summary="Atualizar fatura", tags=["payments"]),
    destroy=extend_schema(summary="Deletar fatura", tags=["payments"]),
)
class InvoiceViewSet(TenantViewSet):
    """ViewSet para faturas"""

    queryset = Invoice.objects.select_related("student__user").prefetch_related(
        "payments"
    )
    serializer_class = InvoiceSerializer
    permission_classes: ClassVar = [CanManagePayments]
    search_fields: ClassVar = [
        "student__user__first_name",
        "student__user__last_name",
        "description",
    ]
    filterset_fields: ClassVar = ["status", "due_date", "reference_month"]
    ordering_fields: ClassVar = ["due_date", "amount", "created_at"]
    ordering: ClassVar = ["-due_date"]

    def get_serializer_class(self):
        if self.action == "create":
            return InvoiceCreateSerializer
        return InvoiceSerializer

    @extend_schema(
        summary="Estatísticas de faturas",
        description="Retorna estatísticas financeiras",
        responses={200: InvoiceStatsSerializer},
        tags=["payments"],
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Estatísticas financeiras"""
        queryset = self.get_queryset()

        stats = {
            "total_pending": queryset.filter(status="pending").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0"),
            "total_paid": queryset.filter(status="paid").aggregate(total=Sum("amount"))[
                "total"
            ]
            or Decimal("0"),
            "total_overdue": queryset.filter(status="overdue").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0"),
            "count_pending": queryset.filter(status="pending").count(),
            "count_paid": queryset.filter(status="paid").count(),
            "count_overdue": queryset.filter(status="overdue").count(),
        }

        return Response(stats)


@extend_schema_view(
    list=extend_schema(summary="Listar pagamentos", tags=["payments"]),
    create=extend_schema(summary="Criar pagamento", tags=["payments"]),
    retrieve=extend_schema(summary="Obter pagamento", tags=["payments"]),
    update=extend_schema(summary="Atualizar pagamento", tags=["payments"]),
    destroy=extend_schema(summary="Deletar pagamento", tags=["payments"]),
)
class PaymentViewSet(TenantViewSet):
    """ViewSet para pagamentos"""

    queryset = Payment.objects.select_related(
        "invoice__student__user", "payment_method"
    )
    serializer_class = PaymentSerializer
    permission_classes: ClassVar = [CanManagePayments]
    filterset_fields: ClassVar = ["status", "payment_method", "payment_date"]
    ordering_fields: ClassVar = ["payment_date", "amount", "created_at"]
    ordering: ClassVar = ["-payment_date"]

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer

    @extend_schema(
        summary="Confirmar pagamento",
        description="Confirma um pagamento pendente",
        request=ConfirmPaymentSerializer,
        responses={200: PaymentSerializer},
        tags=["payments"],
    )
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """Confirma pagamento"""
        payment = self.get_object()

        if payment.status == "confirmed":
            return Response(
                {"error": "Pagamento já foi confirmado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.confirm_payment()

        serializer = PaymentSerializer(payment, context={"request": request})
        return Response(serializer.data)
