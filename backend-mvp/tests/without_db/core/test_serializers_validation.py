"""
Testes de validação de serializers sem dependência de banco de dados
Foco: Validações puras, lógica de negócio, formatação
Objetivo: Testes rápidos para CI/CD sem setup de DB
"""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.payments.serializers import InvoiceStatsSerializer
from apps.students.serializers import GraduateStudentSerializer


class TestGraduateStudentValidations:
    """Testes de validação para graduação de estudantes sem DB"""

    def test_graduate_student_future_date_invalid(self):
        """Teste falha com data de graduação no futuro"""
        future_date = (timezone.now() + timedelta(days=1)).date()
        invalid_data = {"new_belt": "blue", "graduation_date": future_date.isoformat()}

        serializer = GraduateStudentSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "graduation_date" in serializer.errors

    def test_graduate_student_valid_date(self):
        """Teste sucesso com data válida"""
        today = timezone.now().date()
        valid_data = {"new_belt": "blue", "graduation_date": today.isoformat()}

        serializer = GraduateStudentSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_graduate_student_invalid_belt(self):
        """Teste falha com faixa inválida"""
        invalid_data = {"new_belt": "INVALID_BELT"}

        serializer = GraduateStudentSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "new_belt" in serializer.errors

    def test_graduate_student_valid_belts(self):
        """Teste sucesso com faixas válidas"""
        valid_belts = ["white", "blue", "purple", "brown", "black"]

        for belt in valid_belts:
            valid_data = {"new_belt": belt}

            serializer = GraduateStudentSerializer(data=valid_data)
            assert (
                serializer.is_valid()
            ), f"Faixa {belt} deveria ser válida: {serializer.errors}"


class TestInvoiceStatsValidations:
    """Testes de validação para estatísticas sem DB"""

    def test_invoice_stats_valid_data(self):
        """Teste estatísticas com dados válidos"""
        valid_data = {
            "total_paid": Decimal("1000.00"),
            "total_pending": Decimal("500.00"),
            "total_overdue": Decimal("200.00"),
            "count_pending": 10,
            "count_paid": 20,
            "count_overdue": 5,
        }

        serializer = InvoiceStatsSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_invoice_stats_invalid_decimal(self):
        """Teste falha com decimal inválido"""
        invalid_data = {
            "total_paid": "invalid",  # Deveria ser decimal
            "total_pending": Decimal("500.00"),
            "total_overdue": Decimal("200.00"),
            "count_pending": 10,
            "count_paid": 20,
            "count_overdue": 5,
        }

        serializer = InvoiceStatsSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "total_paid" in serializer.errors

    def test_invoice_stats_invalid_integer(self):
        """Teste falha com inteiro inválido"""
        invalid_data = {
            "total_paid": Decimal("1000.00"),
            "total_pending": Decimal("500.00"),
            "total_overdue": Decimal("200.00"),
            "count_pending": "invalid",  # Deveria ser inteiro
            "count_paid": 20,
            "count_overdue": 5,
        }

        serializer = InvoiceStatsSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "count_pending" in serializer.errors


class TestSerializerFieldTypes:
    """Testes de tipos de campos básicos"""

    def test_decimal_field_validation(self):
        """Teste validação de campos decimais"""
        valid_data = {
            "total_paid": "100.50",
            "total_pending": "0.00",
            "total_overdue": "25.99",
            "count_pending": 5,
            "count_paid": 10,
            "count_overdue": 2,
        }

        serializer = InvoiceStatsSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

        # Verificar conversão para Decimal
        validated_data = serializer.validated_data
        assert isinstance(validated_data["total_paid"], Decimal)
        assert validated_data["total_paid"] == Decimal("100.50")

    def test_integer_field_validation(self):
        """Teste validação de campos inteiros"""
        valid_data = {
            "total_paid": Decimal("100.00"),
            "total_pending": Decimal("50.00"),
            "total_overdue": Decimal("25.00"),
            "count_pending": "5",  # String que pode ser convertida
            "count_paid": 10,  # Inteiro direto
            "count_overdue": 2.0,  # Float que é inteiro
        }

        serializer = InvoiceStatsSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

        # Verificar conversão para int
        validated_data = serializer.validated_data
        assert isinstance(validated_data["count_pending"], int)
        assert validated_data["count_pending"] == 5
