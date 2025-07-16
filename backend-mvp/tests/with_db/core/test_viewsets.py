"""
Testes para ViewSets base do Core
Foco: TenantViewSet, ReadOnlyTenantViewSet, isolamento, ações customizadas
Objetivo: 100% de cobertura para core/viewsets.py
"""

from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.core.viewsets import ReadOnlyTenantViewSet, TenantViewSet
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory

User = get_user_model()


# Mock models para testar diferentes cenários
class MockModelWithIsActive:
    """Mock model com campo is_active"""

    def __init__(self, id=1, is_active=True):
        self.id = id
        self.is_active = is_active
        self.deleted_at = None

    def delete(self):
        self.is_active = False
        self.deleted_at = "2024-01-01"

    def save(self):
        pass


class MockModelWithoutIsActive:
    """Mock model sem campo is_active"""

    def __init__(self, id=1):
        self.id = id

    def delete(self):
        pass


class MockQuerySet:
    """Mock queryset para testes"""

    def __init__(self, model_class, items=None):
        self.model = model_class
        self.items = items or []

    def filter(self, **kwargs):
        # Simula filtro por is_active
        if "is_active" in kwargs:
            filtered_items = [
                item
                for item in self.items
                if getattr(item, "is_active", True) == kwargs["is_active"]
            ]
            return MockQuerySet(self.model, filtered_items)
        return self

    def count(self):
        return len(self.items)


class TestTenantViewSet(BaseModelTestCase):
    """Testes para TenantViewSet - ViewSet base com isolamento de tenant"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.viewset = TenantViewSet()

        # Mock request
        self.request = self.factory.get("/")
        force_authenticate(self.request, user=self.user)
        self.viewset.request = self.request

    def test_get_queryset_with_is_active_field(self):
        """Teste get_queryset filtra por is_active quando modelo tem o campo"""
        mock_items = [
            MockModelWithIsActive(1, True),
            MockModelWithIsActive(2, False),
            MockModelWithIsActive(3, True),
        ]
        mock_queryset = MockQuerySet(MockModelWithIsActive, mock_items)

        # Mock super().get_queryset() diretamente
        with patch(
            "rest_framework.viewsets.ModelViewSet.get_queryset",
            return_value=mock_queryset,
        ):
            viewset = TenantViewSet()
            viewset.request = self.request

            # Mock hasattr para simular que modelo tem is_active
            with patch(
                "builtins.hasattr", side_effect=lambda obj, attr: attr == "is_active"
            ):
                result_queryset = viewset.get_queryset()

                # Verifica que filtrou por is_active=True
                self.assertEqual(result_queryset.count(), 2)  # Apenas 2 ativos

    def test_get_queryset_without_is_active_field(self):
        """Teste get_queryset quando modelo não tem is_active"""
        mock_items = [MockModelWithoutIsActive(1), MockModelWithoutIsActive(2)]
        mock_queryset = MockQuerySet(MockModelWithoutIsActive, mock_items)

        with patch(
            "rest_framework.viewsets.ModelViewSet.get_queryset",
            return_value=mock_queryset,
        ):
            viewset = TenantViewSet()
            viewset.request = self.request

            # Mock hasattr para simular que modelo NÃO tem is_active
            with patch("builtins.hasattr", return_value=False):
                result_queryset = viewset.get_queryset()

                # Verifica que não filtrou
                self.assertEqual(result_queryset.count(), 2)

    def test_perform_create(self):
        """Teste perform_create chama serializer.save()"""
        mock_serializer = Mock()

        self.viewset.perform_create(mock_serializer)

        mock_serializer.save.assert_called_once()

    def test_perform_update(self):
        """Teste perform_update chama serializer.save()"""
        mock_serializer = Mock()

        self.viewset.perform_update(mock_serializer)

        mock_serializer.save.assert_called_once()

    def test_perform_destroy_soft_delete(self):
        """Teste perform_destroy com soft delete"""
        mock_instance = MockModelWithIsActive()

        # Mock hasattr para indicar que tem delete e is_active
        with patch(
            "builtins.hasattr",
            side_effect=lambda obj, attr: attr in ["delete", "is_active"],
        ):
            self.viewset.perform_destroy(mock_instance)

            # Verifica que chamou delete (soft delete)
            self.assertFalse(mock_instance.is_active)

    def test_perform_destroy_hard_delete(self):
        """Teste perform_destroy com hard delete"""
        mock_instance = Mock()
        mock_instance.delete = Mock()

        # Mock hasattr para indicar que NÃO tem is_active
        with patch("builtins.hasattr", side_effect=lambda obj, attr: attr == "delete"):
            self.viewset.perform_destroy(mock_instance)

            # Verifica que chamou delete
            mock_instance.delete.assert_called_once()

    def test_restore_action_success(self):
        """Teste action restore com sucesso"""
        mock_instance = MockModelWithIsActive(is_active=False)
        mock_serializer_data = {"id": 1, "is_active": True}

        # Mock métodos necessários
        self.viewset.get_object = Mock(return_value=mock_instance)
        self.viewset.get_serializer = Mock(return_value=Mock(data=mock_serializer_data))

        with patch("builtins.hasattr", return_value=True):
            response = self.viewset.restore(self.request, pk=1)

            # Verifica sucesso
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(mock_instance.is_active)
            self.assertIsNone(mock_instance.deleted_at)

    def test_restore_action_not_supported(self):
        """Teste action restore para modelo sem suporte"""
        mock_instance = MockModelWithoutIsActive()

        self.viewset.get_object = Mock(return_value=mock_instance)

        # Mock hasattr para indicar que NÃO tem is_active
        with patch("builtins.hasattr", return_value=False):
            response = self.viewset.restore(self.request, pk=1)

            # Verifica erro
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)

    def test_stats_action_with_is_active(self):
        """Teste action stats para modelo com is_active"""
        mock_items = [
            MockModelWithIsActive(1, True),
            MockModelWithIsActive(2, False),
            MockModelWithIsActive(3, True),
        ]
        mock_queryset = MockQuerySet(MockModelWithIsActive, mock_items)

        self.viewset.get_queryset = Mock(return_value=mock_queryset)

        # Mock hasattr para indicar que tem is_active
        with patch("builtins.hasattr", return_value=True):
            response = self.viewset.stats(self.request)

            # Verifica estatísticas
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["total"], 3)
            self.assertEqual(response.data["active"], 2)
            self.assertEqual(response.data["inactive"], 1)

    def test_stats_action_without_is_active(self):
        """Teste action stats para modelo sem is_active"""
        mock_items = [MockModelWithoutIsActive(1), MockModelWithoutIsActive(2)]
        mock_queryset = MockQuerySet(MockModelWithoutIsActive, mock_items)

        self.viewset.get_queryset = Mock(return_value=mock_queryset)

        # Mock hasattr para indicar que NÃO tem is_active
        with patch("builtins.hasattr", return_value=False):
            response = self.viewset.stats(self.request)

            # Verifica estatísticas básicas
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["total"], 2)
            self.assertNotIn("active", response.data)
            self.assertNotIn("inactive", response.data)


class TestReadOnlyTenantViewSet(BaseModelTestCase):
    """Testes para ReadOnlyTenantViewSet - ViewSet somente leitura"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.viewset = ReadOnlyTenantViewSet()

        # Mock request
        self.request = self.factory.get("/")
        force_authenticate(self.request, user=self.user)
        self.viewset.request = self.request

    def test_get_queryset_with_is_active_field(self):
        """Teste get_queryset filtra por is_active quando modelo tem o campo"""
        mock_items = [
            MockModelWithIsActive(1, True),
            MockModelWithIsActive(2, False),
            MockModelWithIsActive(3, True),
        ]
        mock_queryset = MockQuerySet(MockModelWithIsActive, mock_items)

        with patch(
            "rest_framework.viewsets.ReadOnlyModelViewSet.get_queryset",
            return_value=mock_queryset,
        ):
            viewset = ReadOnlyTenantViewSet()
            viewset.request = self.request

            # Mock hasattr para simular que modelo tem is_active
            with patch(
                "builtins.hasattr", side_effect=lambda obj, attr: attr == "is_active"
            ):
                result_queryset = viewset.get_queryset()

                # Verifica que filtrou por is_active=True
                self.assertEqual(result_queryset.count(), 2)

    def test_get_queryset_without_is_active_field(self):
        """Teste get_queryset quando modelo não tem is_active"""
        mock_items = [MockModelWithoutIsActive(1), MockModelWithoutIsActive(2)]
        mock_queryset = MockQuerySet(MockModelWithoutIsActive, mock_items)

        with patch(
            "rest_framework.viewsets.ReadOnlyModelViewSet.get_queryset",
            return_value=mock_queryset,
        ):
            viewset = ReadOnlyTenantViewSet()
            viewset.request = self.request

            # Mock hasattr para simular que modelo NÃO tem is_active
            with patch("builtins.hasattr", return_value=False):
                result_queryset = viewset.get_queryset()

                # Verifica que não filtrou
                self.assertEqual(result_queryset.count(), 2)


class TestViewSetPermissionsAndPagination(BaseModelTestCase):
    """Testes para configurações de permissões e paginação"""

    model_class = User

    def test_tenant_viewset_default_configuration(self):
        """Teste configurações padrão do TenantViewSet"""
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import OrderingFilter, SearchFilter

        from apps.core.pagination import StandardResultsSetPagination
        from apps.core.permissions import TenantPermission

        viewset = TenantViewSet()

        # Verifica configurações padrão
        self.assertIn(TenantPermission, viewset.permission_classes)
        self.assertEqual(viewset.pagination_class, StandardResultsSetPagination)
        self.assertIn(DjangoFilterBackend, viewset.filter_backends)
        self.assertIn(SearchFilter, viewset.filter_backends)
        self.assertIn(OrderingFilter, viewset.filter_backends)

    def test_readonly_tenant_viewset_default_configuration(self):
        """Teste configurações padrão do ReadOnlyTenantViewSet"""
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import OrderingFilter, SearchFilter

        from apps.core.pagination import StandardResultsSetPagination
        from apps.core.permissions import TenantPermission

        viewset = ReadOnlyTenantViewSet()

        # Verifica configurações padrão
        self.assertIn(TenantPermission, viewset.permission_classes)
        self.assertEqual(viewset.pagination_class, StandardResultsSetPagination)
        self.assertIn(DjangoFilterBackend, viewset.filter_backends)
        self.assertIn(SearchFilter, viewset.filter_backends)
        self.assertIn(OrderingFilter, viewset.filter_backends)
