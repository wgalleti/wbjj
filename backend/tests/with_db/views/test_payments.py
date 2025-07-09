"""
Testes para Views de Pagamentos
Foco: PaymentMethodViewSet, InvoiceViewSet, PaymentViewSet, ações customizadas
Objetivo: 100% de cobertura para payments/views.py
"""

from decimal import Decimal
from unittest.mock import Mock, patch

from rest_framework import status

from apps.payments.views import InvoiceViewSet, PaymentMethodViewSet, PaymentViewSet
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory


class TestPaymentMethodViewSet(BaseModelTestCase):
    """Testes para PaymentMethodViewSet - métodos de pagamento"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = PaymentMethodViewSet()
        self.viewset.action = "list"

    def test_viewset_attributes(self):
        """Teste dos atributos básicos do ViewSet"""
        from apps.core.permissions import IsAdminOrReadOnly
        from apps.payments.serializers import PaymentMethodSerializer

        # Verifica serializer padrão
        self.assertEqual(self.viewset.serializer_class, PaymentMethodSerializer)

        # Verifica permissões
        self.assertEqual(self.viewset.permission_classes, [IsAdminOrReadOnly])

        # Verifica campos de busca
        expected_search_fields = ["name", "code"]
        self.assertEqual(self.viewset.search_fields, expected_search_fields)

        # Verifica campos de filtro
        expected_filter_fields = ["is_online", "is_active"]
        self.assertEqual(self.viewset.filterset_fields, expected_filter_fields)

        # Verifica ordenação
        self.assertEqual(self.viewset.ordering, ["name"])


class TestInvoiceViewSet(BaseModelTestCase):
    """Testes para InvoiceViewSet - faturas"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = InvoiceViewSet()
        self.viewset.action = "list"

    def test_viewset_attributes(self):
        """Teste dos atributos básicos do ViewSet"""
        from apps.core.permissions import CanManagePayments
        from apps.payments.serializers import InvoiceSerializer

        # Verifica serializer padrão
        self.assertEqual(self.viewset.serializer_class, InvoiceSerializer)

        # Verifica permissões
        self.assertEqual(self.viewset.permission_classes, [CanManagePayments])

        # Verifica campos de busca
        expected_search_fields = [
            "student__user__first_name",
            "student__user__last_name",
            "description",
        ]
        self.assertEqual(self.viewset.search_fields, expected_search_fields)

        # Verifica campos de filtro
        expected_filter_fields = ["status", "due_date", "reference_month"]
        self.assertEqual(self.viewset.filterset_fields, expected_filter_fields)

        # Verifica ordenação
        self.assertEqual(self.viewset.ordering, ["-due_date"])

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.payments.serializers import InvoiceCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, InvoiceCreateSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.payments.serializers import InvoiceSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, InvoiceSerializer)

    def test_stats_action(self):
        """Teste action stats - estatísticas financeiras"""
        # Mock request
        mock_request = Mock()

        # Mock queryset e agregações
        mock_queryset = Mock()

        # Mock para diferentes status
        mock_pending_queryset = Mock()
        mock_pending_queryset.aggregate.return_value = {"total": Decimal("1500.00")}
        mock_pending_queryset.count.return_value = 5

        mock_paid_queryset = Mock()
        mock_paid_queryset.aggregate.return_value = {"total": Decimal("3000.00")}
        mock_paid_queryset.count.return_value = 10

        mock_overdue_queryset = Mock()
        mock_overdue_queryset.aggregate.return_value = {"total": Decimal("500.00")}
        mock_overdue_queryset.count.return_value = 2

        # Mock filter calls
        def mock_filter(status):
            if status == "pending":
                return mock_pending_queryset
            elif status == "paid":
                return mock_paid_queryset
            elif status == "overdue":
                return mock_overdue_queryset
            return Mock()

        mock_queryset.filter.side_effect = mock_filter

        # Mock get_queryset
        self.viewset.get_queryset = Mock(return_value=mock_queryset)

        response = self.viewset.stats(mock_request)

        # Verifica resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_stats = {
            "total_pending": Decimal("1500.00"),
            "total_paid": Decimal("3000.00"),
            "total_overdue": Decimal("500.00"),
            "count_pending": 5,
            "count_paid": 10,
            "count_overdue": 2,
        }

        self.assertEqual(response.data, expected_stats)

    def test_stats_action_no_totals(self):
        """Teste action stats com totais nulos (retorna 0)"""
        # Mock request
        mock_request = Mock()

        # Mock queryset
        mock_queryset = Mock()

        # Mock para agregações que retornam None
        mock_status_queryset = Mock()
        mock_status_queryset.aggregate.return_value = {"total": None}
        mock_status_queryset.count.return_value = 0

        mock_queryset.filter.return_value = mock_status_queryset

        # Mock get_queryset
        self.viewset.get_queryset = Mock(return_value=mock_queryset)

        response = self.viewset.stats(mock_request)

        # Verifica que totais nulos viram Decimal('0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_pending"], Decimal("0"))
        self.assertEqual(response.data["total_paid"], Decimal("0"))
        self.assertEqual(response.data["total_overdue"], Decimal("0"))
        self.assertEqual(response.data["count_pending"], 0)
        self.assertEqual(response.data["count_paid"], 0)
        self.assertEqual(response.data["count_overdue"], 0)


class TestPaymentViewSet(BaseModelTestCase):
    """Testes para PaymentViewSet - pagamentos"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = PaymentViewSet()
        self.viewset.action = "list"

    def test_viewset_attributes(self):
        """Teste dos atributos básicos do ViewSet"""
        from apps.core.permissions import CanManagePayments
        from apps.payments.serializers import PaymentSerializer

        # Verifica serializer padrão
        self.assertEqual(self.viewset.serializer_class, PaymentSerializer)

        # Verifica permissões
        self.assertEqual(self.viewset.permission_classes, [CanManagePayments])

        # Verifica campos de filtro
        expected_filter_fields = ["status", "payment_method", "payment_date"]
        self.assertEqual(self.viewset.filterset_fields, expected_filter_fields)

        # Verifica campos de ordenação
        expected_ordering_fields = ["payment_date", "amount", "created_at"]
        self.assertEqual(self.viewset.ordering_fields, expected_ordering_fields)

        # Verifica ordenação padrão
        self.assertEqual(self.viewset.ordering, ["-payment_date"])

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.payments.serializers import PaymentCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, PaymentCreateSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.payments.serializers import PaymentSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, PaymentSerializer)

    def test_confirm_action_success(self):
        """Teste action confirm com sucesso"""
        # Mock request
        mock_request = Mock()

        # Mock get_object - pagamento pendente
        mock_payment = Mock()
        mock_payment.status = "pending"  # Não confirmado
        mock_payment.confirm_payment = Mock()

        self.viewset.get_object = Mock(return_value=mock_payment)

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.data = {"id": "payment123", "status": "confirmed"}

        with patch(
            "apps.payments.views.PaymentSerializer", return_value=mock_serializer
        ):
            response = self.viewset.confirm(mock_request, pk=1)

            # Verifica que confirmou o pagamento
            mock_payment.confirm_payment.assert_called_once()

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, mock_serializer.data)

    def test_confirm_action_already_confirmed(self):
        """Teste action confirm com pagamento já confirmado"""
        # Mock request
        mock_request = Mock()

        # Mock get_object - pagamento já confirmado
        mock_payment = Mock()
        mock_payment.status = "confirmed"  # Já confirmado

        self.viewset.get_object = Mock(return_value=mock_payment)

        response = self.viewset.confirm(mock_request, pk=1)

        # Verifica erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Pagamento já foi confirmado", response.data["error"])
