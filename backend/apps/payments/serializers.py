"""
Serializers para sistema financeiro

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE documentar campos computados
- Validações rigorosas financeiras
- Campos de auditoria padronizados
"""
from decimal import Decimal
from typing import ClassVar

from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.serializers import BaseModelSerializer
from apps.students.serializers import StudentSerializer

from .models import Invoice, Payment, PaymentMethod


class PaymentMethodSerializer(BaseModelSerializer):
    """
    Serializer para métodos de pagamento
    """

    processing_fee_percentage = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_processing_fee_percentage(self, obj):
        """Taxa de processamento em percentual"""
        return f"{obj.processing_fee * 100:.2f}%"

    class Meta:
        model = PaymentMethod
        fields: ClassVar = [
            "id",
            "name",
            "code",
            "is_online",
            "processing_fee",
            "is_active",
            "created_at",
            "updated_at",
            # Campos computados
            "processing_fee_percentage",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "processing_fee_percentage",
        ]
        extra_kwargs: ClassVar = {
            "name": {"help_text": "Nome do método de pagamento"},
            "code": {"help_text": "Código único"},
            "is_online": {"help_text": "É pagamento online?"},
            "processing_fee": {"help_text": "Taxa de processamento (decimal)"},
        }


class InvoiceSerializer(BaseModelSerializer):
    """
    Serializer para faturas
    """

    student = StudentSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    reference_month_display = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_status_display(self, obj):
        """Status da fatura formatado"""
        return obj.get_status_display()

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_amount(self, obj):
        """Valor total com desconto e multa"""
        return obj.total_amount

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_paid(self, obj):
        """Total pago"""
        return obj.payments.filter(status="confirmed").aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_remaining_amount(self, obj):
        """Valor restante"""
        return obj.total_amount - self.get_total_paid(obj)

    @extend_schema_field(serializers.BooleanField())
    def get_is_overdue(self, obj):
        """Verifica se está vencida"""
        return obj.is_overdue

    @extend_schema_field(serializers.IntegerField())
    def get_days_overdue(self, obj):
        """Dias em atraso"""
        if obj.is_overdue:
            return (timezone.now().date() - obj.due_date).days
        return 0

    @extend_schema_field(serializers.CharField())
    def get_reference_month_display(self, obj):
        """Mês de referência formatado"""
        return obj.reference_month.strftime("%m/%Y")

    class Meta:
        model = Invoice
        fields: ClassVar = [
            "id",
            "student",
            "due_date",
            "reference_month",
            "amount",
            "discount",
            "late_fee",
            "status",
            "description",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
            # Campos computados
            "status_display",
            "total_amount",
            "total_paid",
            "remaining_amount",
            "is_overdue",
            "days_overdue",
            "reference_month_display",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "status_display",
            "total_amount",
            "total_paid",
            "remaining_amount",
            "is_overdue",
            "days_overdue",
            "reference_month_display",
        ]
        extra_kwargs: ClassVar = {
            "due_date": {"help_text": "Data de vencimento"},
            "reference_month": {"help_text": "Mês de referência"},
            "amount": {"help_text": "Valor base da fatura"},
            "discount": {"help_text": "Desconto aplicado"},
            "late_fee": {"help_text": "Multa por atraso"},
            "status": {"help_text": "Status da fatura"},
            "description": {"help_text": "Descrição da fatura"},
            "notes": {"help_text": "Observações"},
        }


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de faturas
    """

    student_id = serializers.UUIDField(write_only=True, help_text="ID do aluno")

    class Meta:
        model = Invoice
        fields: ClassVar = [
            "student_id",
            "due_date",
            "reference_month",
            "amount",
            "discount",
            "late_fee",
            "description",
            "notes",
        ]
        extra_kwargs: ClassVar = {
            "due_date": {"help_text": "Data de vencimento"},
            "reference_month": {"help_text": "Mês de referência"},
            "amount": {"help_text": "Valor base da fatura"},
            "discount": {"help_text": "Desconto aplicado"},
            "late_fee": {"help_text": "Multa por atraso"},
            "description": {"help_text": "Descrição da fatura"},
            "notes": {"help_text": "Observações"},
        }

    def validate_amount(self, value):
        """Validar valor da fatura"""
        if value <= 0:
            raise serializers.ValidationError("Valor deve ser maior que zero")
        return value

    def validate_discount(self, value):
        """Validar desconto"""
        if value < 0:
            raise serializers.ValidationError("Desconto não pode ser negativo")
        return value

    def validate_late_fee(self, value):
        """Validar multa"""
        if value < 0:
            raise serializers.ValidationError("Multa não pode ser negativa")
        return value

    def validate_reference_month(self, value):
        """Validar mês de referência"""
        # Deve ser o primeiro dia do mês
        if value.day != 1:
            raise serializers.ValidationError(
                "Mês de referência deve ser o primeiro dia do mês"
            )
        return value


class PaymentSerializer(BaseModelSerializer):
    """
    Serializer para pagamentos
    """

    invoice = InvoiceSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    net_amount = serializers.SerializerMethodField()
    is_confirmed = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_status_display(self, obj):
        """Status do pagamento formatado"""
        return obj.get_status_display()

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_net_amount(self, obj):
        """Valor líquido (descontando taxa)"""
        return obj.amount - obj.processing_fee

    @extend_schema_field(serializers.BooleanField())
    def get_is_confirmed(self, obj):
        """Verifica se o pagamento foi confirmado"""
        return obj.status == "confirmed"

    class Meta:
        model = Payment
        fields: ClassVar = [
            "id",
            "invoice",
            "payment_method",
            "amount",
            "processing_fee",
            "payment_date",
            "confirmed_date",
            "status",
            "external_id",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
            # Campos computados
            "status_display",
            "net_amount",
            "is_confirmed",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "status_display",
            "net_amount",
            "is_confirmed",
        ]
        extra_kwargs: ClassVar = {
            "amount": {"help_text": "Valor do pagamento"},
            "processing_fee": {"help_text": "Taxa de processamento"},
            "payment_date": {"help_text": "Data/hora do pagamento"},
            "confirmed_date": {"help_text": "Data/hora da confirmação"},
            "status": {"help_text": "Status do pagamento"},
            "external_id": {"help_text": "ID da transação no gateway"},
            "notes": {"help_text": "Observações"},
        }


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de pagamentos
    """

    invoice_id = serializers.UUIDField(write_only=True, help_text="ID da fatura")
    payment_method_id = serializers.UUIDField(
        write_only=True, help_text="ID do método de pagamento"
    )

    class Meta:
        model = Payment
        fields: ClassVar = [
            "invoice_id",
            "payment_method_id",
            "amount",
            "payment_date",
            "external_id",
            "notes",
        ]
        extra_kwargs: ClassVar = {
            "amount": {"help_text": "Valor do pagamento"},
            "payment_date": {"help_text": "Data/hora do pagamento"},
            "external_id": {"help_text": "ID da transação no gateway"},
            "notes": {"help_text": "Observações"},
        }

    def validate_amount(self, value):
        """Validar valor do pagamento"""
        if value <= 0:
            raise serializers.ValidationError("Valor deve ser maior que zero")
        return value

    def validate_payment_date(self, value):
        """Validar data do pagamento"""
        if value > timezone.now():
            raise serializers.ValidationError(
                "Data do pagamento não pode ser no futuro"
            )
        return value


class ConfirmPaymentSerializer(serializers.Serializer):
    """
    Serializer para confirmação de pagamento
    """

    external_id = serializers.CharField(
        required=False, help_text="ID da transação no gateway"
    )
    notes = serializers.CharField(
        required=False, help_text="Observações sobre a confirmação"
    )

    class Meta:
        fields: ClassVar = ["external_id", "notes"]


class InvoiceStatsSerializer(serializers.Serializer):
    """
    Serializer para estatísticas de faturas
    """

    total_pending = serializers.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total pendente"
    )
    total_paid = serializers.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total pago"
    )
    total_overdue = serializers.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total em atraso"
    )
    count_pending = serializers.IntegerField(help_text="Quantidade pendente")
    count_paid = serializers.IntegerField(help_text="Quantidade paga")
    count_overdue = serializers.IntegerField(help_text="Quantidade em atraso")

    class Meta:
        fields: ClassVar = [
            "total_pending",
            "total_paid",
            "total_overdue",
            "count_pending",
            "count_paid",
            "count_overdue",
        ]
