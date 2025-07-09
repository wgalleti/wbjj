"""
Testes para Views de Autenticação
Foco: UserViewSet, JWT views, ações customizadas, permissões
Objetivo: 100% de cobertura para authentication/views.py
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status

from apps.authentication.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserViewSet,
)
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory

User = get_user_model()


class TestUserViewSet(BaseModelTestCase):
    """Testes para UserViewSet - gestão completa de usuários"""

    model_class = User

    def setUp(self):
        super().setUp()
        # Criar usuários para testes
        self.admin_user = UserFactory(role="admin", email="admin@test.com")
        self.instructor_user = UserFactory(
            role="instructor", email="instructor@test.com"
        )
        self.student_user = UserFactory(role="student", email="student@test.com")

        self.viewset = UserViewSet()
        self.viewset.action = "list"  # Ação padrão

    def test_get_serializer_class_create(self):
        """Teste get_serializer_class para ação create"""
        from apps.authentication.serializers import UserCreateSerializer

        self.viewset.action = "create"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, UserCreateSerializer)

    def test_get_serializer_class_update(self):
        """Teste get_serializer_class para ações update/partial_update"""
        from apps.authentication.serializers import UserUpdateSerializer

        # Teste update
        self.viewset.action = "update"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, UserUpdateSerializer)

        # Teste partial_update
        self.viewset.action = "partial_update"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, UserUpdateSerializer)

    def test_get_serializer_class_default(self):
        """Teste get_serializer_class para outras ações"""
        from apps.authentication.serializers import UserSerializer

        self.viewset.action = "list"
        serializer_class = self.viewset.get_serializer_class()
        self.assertEqual(serializer_class, UserSerializer)

    def test_get_permissions_create(self):
        """Teste get_permissions para ação create"""
        from rest_framework import permissions

        from apps.core.permissions import IsAdminOrReadOnly

        self.viewset.action = "create"
        permission_instances = self.viewset.get_permissions()

        # Verifica que tem 2 permissões
        self.assertEqual(len(permission_instances), 2)
        self.assertIsInstance(permission_instances[0], permissions.IsAuthenticated)
        self.assertIsInstance(permission_instances[1], IsAdminOrReadOnly)

    def test_get_permissions_update(self):
        """Teste get_permissions para ações update/partial_update/destroy"""
        from rest_framework import permissions

        from apps.core.permissions import IsOwnerOrReadOnly

        for action in ["update", "partial_update", "destroy"]:
            self.viewset.action = action
            permission_instances = self.viewset.get_permissions()

            # Verifica que tem 2 permissões
            self.assertEqual(len(permission_instances), 2)
            self.assertIsInstance(permission_instances[0], permissions.IsAuthenticated)
            self.assertIsInstance(permission_instances[1], IsOwnerOrReadOnly)

    def test_get_permissions_default(self):
        """Teste get_permissions para outras ações"""
        from rest_framework import permissions

        self.viewset.action = "list"
        permission_instances = self.viewset.get_permissions()

        # Verifica que tem apenas IsAuthenticated
        self.assertEqual(len(permission_instances), 1)
        self.assertIsInstance(permission_instances[0], permissions.IsAuthenticated)

    def test_me_action(self):
        """Teste action me - retorna dados do usuário logado"""
        from unittest.mock import Mock

        # Mock request
        mock_request = Mock()
        mock_request.user = self.student_user

        # Mock get_serializer
        mock_serializer = Mock()
        mock_serializer.data = {
            "id": str(self.student_user.id),
            "email": self.student_user.email,
        }

        self.viewset.get_serializer = Mock(return_value=mock_serializer)
        self.viewset.request = mock_request

        response = self.viewset.me(mock_request)

        # Verifica resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewset.get_serializer.assert_called_once_with(self.student_user)

    def test_update_profile_action_success(self):
        """Teste action update_profile com sucesso"""
        from unittest.mock import Mock

        # Mock request
        mock_request = Mock()
        mock_request.user = self.student_user
        mock_request.data = {"first_name": "Updated Name"}

        # Mock serializers
        mock_update_serializer = Mock()
        mock_update_serializer.is_valid.return_value = None
        mock_update_serializer.save.return_value = None

        mock_response_serializer = Mock()
        mock_response_serializer.data = {
            "id": str(self.student_user.id),
            "first_name": "Updated Name",
        }

        # Mock UserUpdateSerializer e UserSerializer
        with patch(
            "apps.authentication.views.UserUpdateSerializer",
            return_value=mock_update_serializer,
        ), patch(
            "apps.authentication.views.UserSerializer",
            return_value=mock_response_serializer,
        ):
            response = self.viewset.update_profile(mock_request)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_update_serializer.is_valid.assert_called_once_with(
                raise_exception=True
            )
            mock_update_serializer.save.assert_called_once()

    def test_change_password_action_success(self):
        """Teste action change_password com sucesso"""
        from unittest.mock import Mock

        # Mock request
        mock_request = Mock()
        mock_request.user = self.student_user
        mock_request.data = {"old_password": "old123", "new_password": "new123"}

        # Mock serializer
        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = None
        mock_serializer.validated_data = {"new_password": "new123"}

        # Mock user.set_password e save
        mock_user = Mock()
        mock_user.set_password = Mock()
        mock_user.save = Mock()
        mock_request.user = mock_user

        with patch(
            "apps.authentication.views.PasswordChangeSerializer",
            return_value=mock_serializer,
        ):
            response = self.viewset.change_password(mock_request)

            # Verifica resposta
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["message"], "Senha alterada com sucesso")
            mock_serializer.is_valid.assert_called_once_with(raise_exception=True)
            mock_user.set_password.assert_called_once_with("new123")
            mock_user.save.assert_called_once()

    def test_verify_email_action(self):
        """Teste action verify_email"""
        from unittest.mock import Mock

        # Mock request
        mock_request = Mock()

        # Mock get_object
        mock_user = Mock()
        mock_user.is_verified = False
        mock_user.save = Mock()

        self.viewset.get_object = Mock(return_value=mock_user)

        response = self.viewset.verify_email(mock_request, pk=1)

        # Verifica que marcou como verificado
        self.assertTrue(mock_user.is_verified)
        mock_user.save.assert_called_once()

        # Verifica resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email verificado com sucesso")

    def test_toggle_active_action_activate(self):
        """Teste action toggle_active - ativar usuário"""
        from unittest.mock import Mock

        # Mock request
        mock_request = Mock()

        # Mock get_object - usuário inativo
        mock_user = Mock()
        mock_user.is_active = False
        mock_user.save = Mock()

        self.viewset.get_object = Mock(return_value=mock_user)

        response = self.viewset.toggle_active(mock_request, pk=1)

        # Verifica que ativou usuário
        self.assertTrue(mock_user.is_active)
        mock_user.save.assert_called_once()

        # Verifica resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Usuário ativado com sucesso")

    def test_toggle_active_action_deactivate(self):
        """Teste action toggle_active - desativar usuário"""
        from unittest.mock import Mock

        # Mock request
        mock_request = Mock()

        # Mock get_object - usuário ativo
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.save = Mock()

        self.viewset.get_object = Mock(return_value=mock_user)

        response = self.viewset.toggle_active(mock_request, pk=1)

        # Verifica que desativou usuário
        self.assertFalse(mock_user.is_active)
        mock_user.save.assert_called_once()

        # Verifica resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Usuário desativado com sucesso")


class TestCustomTokenObtainPairView(BaseModelTestCase):
    """Testes para CustomTokenObtainPairView - login JWT"""

    model_class = User

    def test_post_method_calls_super(self):
        """Teste que post chama super().post()"""
        from unittest.mock import Mock, patch

        view = CustomTokenObtainPairView()
        mock_request = Mock()

        # Mock super().post()
        with patch(
            "rest_framework_simplejwt.views.TokenObtainPairView.post"
        ) as mock_super_post:
            mock_super_post.return_value = Mock(status_code=200)

            view.post(mock_request, "arg1", kwarg1="value1")

            # Verifica que chamou super
            mock_super_post.assert_called_once_with(
                mock_request, "arg1", kwarg1="value1"
            )

    def test_serializer_class_assignment(self):
        """Teste que usa CustomTokenObtainPairSerializer"""
        from apps.authentication.serializers import CustomTokenObtainPairSerializer

        view = CustomTokenObtainPairView()
        self.assertEqual(view.serializer_class, CustomTokenObtainPairSerializer)


class TestCustomTokenRefreshView(BaseModelTestCase):
    """Testes para CustomTokenRefreshView - refresh JWT"""

    model_class = User

    def test_post_method_calls_super(self):
        """Teste que post chama super().post()"""
        from unittest.mock import Mock, patch

        view = CustomTokenRefreshView()
        mock_request = Mock()

        # Mock super().post()
        with patch(
            "rest_framework_simplejwt.views.TokenRefreshView.post"
        ) as mock_super_post:
            mock_super_post.return_value = Mock(status_code=200)

            view.post(mock_request, "arg1", kwarg1="value1")

            # Verifica que chamou super
            mock_super_post.assert_called_once_with(
                mock_request, "arg1", kwarg1="value1"
            )


class TestViewSetConfiguration(BaseModelTestCase):
    """Testes para configuração do ViewSet"""

    model_class = User

    def test_userviewset_attributes(self):
        """Teste atributos de configuração do UserViewSet"""
        from apps.authentication.serializers import UserSerializer
        from apps.core.permissions import IsAdminOrReadOnly

        viewset = UserViewSet()

        # Verifica queryset
        self.assertEqual(
            list(viewset.queryset.model._meta.get_fields()),
            list(User._meta.get_fields()),
        )

        # Verifica serializer padrão
        self.assertEqual(viewset.serializer_class, UserSerializer)

        # Verifica permission_classes
        self.assertEqual(viewset.permission_classes, [IsAdminOrReadOnly])

        # Verifica search_fields
        expected_search = ["first_name", "last_name", "email"]
        self.assertEqual(viewset.search_fields, expected_search)

        # Verifica filterset_fields
        expected_filters = ["role", "is_active", "is_verified"]
        self.assertEqual(viewset.filterset_fields, expected_filters)

        # Verifica ordering_fields
        expected_ordering_fields = ["first_name", "last_name", "email", "created_at"]
        self.assertEqual(viewset.ordering_fields, expected_ordering_fields)

        # Verifica ordering padrão
        expected_ordering = ["first_name", "last_name"]
        self.assertEqual(viewset.ordering, expected_ordering)
