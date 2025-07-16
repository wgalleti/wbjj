"""
Testes para serializers de Payments
Foco: Validações básicas sem dependência de DB
Objetivo: Cobertura simples dos serializers
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.payments.models import Invoice, Payment, PaymentMethod
from apps.payments.serializers import (
    ConfirmPaymentSerializer,
    InvoiceCreateSerializer,
    InvoiceSerializer,
    InvoiceStatsSerializer,
    PaymentCreateSerializer,
    PaymentMethodSerializer,
)
from tests.base import BaseModelTestCase
from tests.with_db.factories.payments import InvoiceFactory, PaymentMethodFactory
from tests.with_db.factories.students import StudentFactory

User = get_user_model()


@pytest.mark.usefixtures("tenant_models_context")
class TestPaymentMethodSerializer(BaseModelTestCase):
    """Testes para PaymentMethodSerializer - campos computados"""

    model_class = PaymentMethod

    def test_serialize_computed_fields(self):
        """Teste serialização de campos computados"""
        payment_method = PaymentMethodFactory(
            name="Cartão de Crédito",
            processing_fee=Decimal("0.035"),  # 3.5%
        )

        serializer = PaymentMethodSerializer(payment_method)
        data = serializer.data

        # Verificar campos computados
        self.assertIn("processing_fee_percentage", data)
        self.assertEqual(data["processing_fee_percentage"], "3.50%")


@pytest.mark.usefixtures("tenant_models_context")
class TestInvoiceSerializer(BaseModelTestCase):
    """Testes para InvoiceSerializer - campos computados"""

    model_class = Invoice

    def test_serialize_computed_fields(self):
        """Teste serialização de campos computados"""
        student = StudentFactory()
        invoice = InvoiceFactory(
            student=student,
            amount=Decimal("150.00"),
            discount=Decimal("10.00"),
            late_fee=Decimal("5.00"),
            status="pending",
        )

        serializer = InvoiceSerializer(invoice)
        data = serializer.data

        # Verificar campos computados
        self.assertIn("status_display", data)
        self.assertIn("total_amount", data)
        self.assertIn("total_paid", data)
        self.assertIn("remaining_amount", data)
        self.assertIn("is_overdue", data)
        self.assertIn("days_overdue", data)
        self.assertIn("reference_month_display", data)


@pytest.mark.usefixtures("tenant_models_context")
class TestInvoiceCreateSerializer(BaseModelTestCase):
    """Testes para InvoiceCreateSerializer - validações de criação"""

    model_class = Invoice

    def test_validate_amount_positive(self):
        """Teste sucesso com valor positivo"""
        student = StudentFactory()

        valid_data = {
            "student_id": str(student.id),
            "amount": "150.00",  # Positivo - válido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_amount_zero_invalid(self):
        """Teste erro com valor zero"""
        student = StudentFactory()

        invalid_data = {
            "student_id": str(student.id),
            "amount": "0.00",  # Zero - inválido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_validate_amount_negative_invalid(self):
        """Teste erro com valor negativo"""
        student = StudentFactory()

        invalid_data = {
            "student_id": str(student.id),
            "amount": "-50.00",  # Negativo - inválido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_validate_discount_not_negative(self):
        """Teste sucesso com desconto não negativo"""
        student = StudentFactory()

        valid_data = {
            "student_id": str(student.id),
            "amount": "150.00",
            "discount": "10.00",  # Positivo - válido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_discount_negative_invalid(self):
        """Teste erro com desconto negativo"""
        student = StudentFactory()

        invalid_data = {
            "student_id": str(student.id),
            "amount": "150.00",
            "discount": "-5.00",  # Negativo - inválido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("discount", serializer.errors)

    def test_validate_late_fee_not_negative(self):
        """Teste sucesso com multa não negativa"""
        student = StudentFactory()

        valid_data = {
            "student_id": str(student.id),
            "amount": "150.00",
            "late_fee": "15.00",  # Positivo - válido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_late_fee_negative_invalid(self):
        """Teste erro com multa negativa"""
        student = StudentFactory()

        invalid_data = {
            "student_id": str(student.id),
            "amount": "150.00",
            "late_fee": "-10.00",  # Negativo - inválido
            "due_date": "2024-12-31",
            "reference_month": "2024-01-01",
        }

        serializer = InvoiceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("late_fee", serializer.errors)

    def test_validate_reference_month_not_future(self):
        """Teste sucesso com mês de referência não futuro"""
        student = StudentFactory()

        # Mês atual
        current_month = date.today().replace(day=1)

        valid_data = {
            "student_id": str(student.id),
            "amount": "150.00",
            "due_date": "2024-12-31",
            "reference_month": current_month.isoformat(),  # Atual - válido
        }

        serializer = InvoiceCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_reference_month_first_day(self):
        """Teste validação que mês de referência deve ser primeiro dia"""
        student = StudentFactory()

        invalid_data = {
            "student_id": str(student.id),
            "amount": "150.00",
            "due_date": "2024-12-31",
            "reference_month": "2024-01-15",  # Não é primeiro dia - inválido
        }

        serializer = InvoiceCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("reference_month", serializer.errors)


@pytest.mark.usefixtures("tenant_models_context")
class TestPaymentCreateSerializer(BaseModelTestCase):
    """Testes para PaymentCreateSerializer - validações de criação"""

    model_class = Payment

    def test_validate_amount_positive(self):
        """Teste sucesso com valor positivo"""
        invoice = InvoiceFactory()
        payment_method = PaymentMethodFactory()

        valid_data = {
            "invoice_id": str(invoice.id),
            "payment_method_id": str(payment_method.id),
            "amount": "150.00",  # Positivo - válido
            "payment_date": timezone.now().isoformat(),
        }

        serializer = PaymentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_amount_zero_invalid(self):
        """Teste erro com valor zero"""
        invoice = InvoiceFactory()
        payment_method = PaymentMethodFactory()

        invalid_data = {
            "invoice_id": str(invoice.id),
            "payment_method_id": str(payment_method.id),
            "amount": "0.00",  # Zero - inválido
            "payment_date": timezone.now().isoformat(),
        }

        serializer = PaymentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_validate_payment_date_past_valid(self):
        """Teste sucesso com data no passado"""
        invoice = InvoiceFactory()
        payment_method = PaymentMethodFactory()

        past_date = timezone.now() - timedelta(days=1)
        valid_data = {
            "invoice_id": str(invoice.id),
            "payment_method_id": str(payment_method.id),
            "amount": "150.00",
            "payment_date": past_date.isoformat(),  # Passado - válido
        }

        serializer = PaymentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_payment_date_today_valid(self):
        """Teste sucesso com data hoje"""
        invoice = InvoiceFactory()
        payment_method = PaymentMethodFactory()

        valid_data = {
            "invoice_id": str(invoice.id),
            "payment_method_id": str(payment_method.id),
            "amount": "150.00",
            "payment_date": timezone.now().isoformat(),  # Hoje - válido
        }

        serializer = PaymentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_payment_date_not_future(self):
        """Teste erro com data no futuro"""
        invoice = InvoiceFactory()
        payment_method = PaymentMethodFactory()

        future_date = timezone.now() + timedelta(days=1)
        invalid_data = {
            "invoice_id": str(invoice.id),
            "payment_method_id": str(payment_method.id),
            "amount": "150.00",
            "payment_date": future_date.isoformat(),  # Futuro - inválido
        }

        serializer = PaymentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("payment_date", serializer.errors)


class TestConfirmPaymentSerializer(BaseModelTestCase):
    """Testes para ConfirmPaymentSerializer - validações de confirmação"""

    model_class = Payment

    def test_confirm_payment_empty_data(self):
        """Teste confirmação com dados vazios"""
        # Confirmação pode ser feita com dados vazios
        valid_data = {}

        serializer = ConfirmPaymentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_confirm_payment_with_external_id(self):
        """Teste confirmação com ID externo"""
        valid_data = {
            "external_id": "TXN_123456789",
            "notes": "Pagamento confirmado via gateway",
        }

        serializer = ConfirmPaymentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_confirm_payment_without_external_id(self):
        """Teste confirmação sem ID externo"""
        valid_data = {"notes": "Pagamento confirmado manualmente"}

        serializer = ConfirmPaymentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class TestInvoiceStatsSerializer(BaseModelTestCase):
    """Testes para InvoiceStatsSerializer - validações de estatísticas"""

    model_class = Invoice

    def test_invoice_stats_serialization(self):
        """Teste serialização de estatísticas"""
        stats_data = {
            "total_paid": Decimal("12000.00"),
            "total_pending": Decimal("3000.00"),
            "total_overdue": Decimal("1000.00"),
            "count_pending": 20,
            "count_paid": 75,
            "count_overdue": 5,
        }

        serializer = InvoiceStatsSerializer(data=stats_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Verificar que os dados são preservados
        validated_data = serializer.validated_data
        self.assertEqual(validated_data["total_paid"], Decimal("12000.00"))
        self.assertEqual(validated_data["total_pending"], Decimal("3000.00"))

    def test_invoice_stats_zero_values(self):
        """Teste estatísticas com valores zero"""
        stats_data = {
            "total_paid": Decimal("0.00"),
            "total_pending": Decimal("0.00"),
            "total_overdue": Decimal("0.00"),
            "count_pending": 0,
            "count_paid": 0,
            "count_overdue": 0,
        }

        serializer = InvoiceStatsSerializer(data=stats_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invoice_stats_invalid_integer(self):
        """Teste erro com valor inteiro inválido"""
        stats_data = {
            "count_pending": "invalid",  # Deveria ser inteiro
            "total_paid": Decimal("12000.00"),
            "total_pending": Decimal("3000.00"),
            "total_overdue": Decimal("1000.00"),
            "count_paid": 75,
            "count_overdue": 5,
        }

        serializer = InvoiceStatsSerializer(data=stats_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("count_pending", serializer.errors)

    def test_invoice_stats_invalid_decimal(self):
        """Teste erro com valor decimal inválido"""
        stats_data = {
            "total_paid": "invalid",  # Deveria ser decimal
            "total_pending": Decimal("3000.00"),
            "total_overdue": Decimal("1000.00"),
            "count_pending": 20,
            "count_paid": 75,
            "count_overdue": 5,
        }

        serializer = InvoiceStatsSerializer(data=stats_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("total_paid", serializer.errors)
