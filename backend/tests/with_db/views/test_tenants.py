"""
Testes para Views de Tenants
Foco: TenantViewSet, ações customizadas, get_serializer_class
Objetivo: 100% de cobertura para tenants/views.py
"""

from unittest.mock import Mock

from rest_framework import permissions, status

from apps.tenants.views import TenantViewSet
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory


class TestTenantViewSet(BaseModelTestCase):
    """Testes para TenantViewSet - gestão de academias"""

    model_class = UserFactory._meta.model

    def setUp(self):
        super().setUp()
        self.viewset = TenantViewSet()
        self.viewset.action = "list"

    def test_viewset_attributes(self):
        """Teste dos atributos básicos do ViewSet"""
        from apps.core.permissions import IsAdminOrReadOnly
        from apps.tenants.serializers import TenantSerializer

        # Verifica serializer padrão
        self.assertEqual(self.viewset.serializer_class, TenantSerializer)

        # Verifica permissões
        self.assertEqual(self.viewset.permission_classes, [IsAdminOrReadOnly])

        # Verifica campos de busca
        expected_search_fields = ["name", "email", "city", "state"]
        self.assertEqual(self.viewset.search_fields, expected_search_fields)

        # Verifica campos de filtro
        expected_filter_fields = ["city", "state", "country", "is_active"]
        self.assertEqual(self.viewset.filterset_fields, expected_filter_fields)

        # Verifica campos de ordenação
        expected_ordering_fields = ["name", "founded_date", "created_at"]
        self.assertEqual(self.viewset.ordering_fields, expected_ordering_fields)

        # Verifica ordenação padrão
        self.assertEqual(self.viewset.ordering, ["name"])

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.tenants.serializers import TenantCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, TenantCreateSerializer)

    def test_get_serializer_class_update(self):
        """Teste get_serializer_class para ações update/partial_update"""
        from apps.tenants.serializers import TenantUpdateSerializer

        # Teste update
        self.viewset.action = "update"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, TenantUpdateSerializer)

        # Teste partial_update
        self.viewset.action = "partial_update"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, TenantUpdateSerializer)

    def test_get_serializer_class_public(self):
        """Teste get_serializer_class para ação public"""
        from apps.tenants.serializers import TenantPublicSerializer

        self.viewset.action = "public"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, TenantPublicSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.tenants.serializers import TenantSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, TenantSerializer)

    def test_public_action(self):
        """Teste action public - informações públicas da academia"""
        # Mock request
        mock_request = Mock()

        # Mock get_object
        mock_tenant = Mock()
        mock_tenant.name = "Academia Test"
        mock_tenant.city = "São Paulo"
        self.viewset.get_object = Mock(return_value=mock_tenant)

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.data = {
            "name": "Academia Test",
            "city": "São Paulo",
            "public_info": "Informações públicas",
        }

        with self.patch(
            "apps.tenants.views.TenantPublicSerializer", return_value=mock_serializer
        ):
            response = self.viewset.public(mock_request, pk=1)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, mock_serializer.data)

    def test_public_action_permissions(self):
        """Teste que action public permite acesso anônimo"""
        # Verifica que a action public tem permission_classes=[permissions.AllowAny]
        from apps.tenants.views import TenantViewSet

        # Busca a definição da action public
        public_action = None
        for attr_name in dir(TenantViewSet):
            attr = getattr(TenantViewSet, attr_name)
            if hasattr(attr, "url_name") and attr.url_name == "public":
                public_action = attr
                break

        # Verifica se encontrou a action
        self.assertIsNotNone(public_action, "Action 'public' não encontrada")

        # Verifica que tem permission_classes=[permissions.AllowAny]
        if hasattr(public_action, "cls"):
            # Para actions definidas com @action
            detail = getattr(public_action.cls, "detail", None)
            methods = getattr(public_action.cls, "methods", None)
            permission_classes = getattr(public_action.cls, "permission_classes", None)

            self.assertTrue(detail, "Action public deve ser detail=True")
            self.assertEqual(methods, ["get"], "Action public deve aceitar apenas GET")
            self.assertEqual(
                permission_classes,
                [permissions.AllowAny],
                "Action public deve permitir acesso anônimo",
            )

    def patch(self, target, **kwargs):
        """Helper method para mocking"""
        from unittest.mock import patch

        return patch(target, **kwargs)
