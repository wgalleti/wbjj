"""
Testes para views de autenticação

Foco: ViewSets de usuário, JWT authentication, logout, permissões
Objetivo: 100% de cobertura para authentication/views.py
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
        with (
            patch(
                "apps.authentication.views.UserUpdateSerializer",
                return_value=mock_update_serializer,
            ),
            patch(
                "apps.authentication.views.UserSerializer",
                return_value=mock_response_serializer,
            ),
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


class TestLogoutView(BaseModelTestCase):
    """Testes para LogoutView - logout com blacklist JWT"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_logout_success(self):
        """Teste logout bem-sucedido com blacklist do token"""
        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Dados do logout
        data = {"refresh": str(self.refresh_token)}

        # Fazer logout
        response = self.client.post("/api/v1/auth/logout/", data)

        # Verificar resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Logout realizado com sucesso")

    def test_logout_invalid_token(self):
        """Teste logout com token inválido"""
        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Dados com token inválido
        data = {"refresh": "token_invalido"}

        # Fazer logout
        response = self.client.post("/api/v1/auth/logout/", data)

        # Verificar erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)

    def test_logout_missing_token(self):
        """Teste logout sem token"""
        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Fazer logout sem dados
        response = self.client.post("/api/v1/auth/logout/", {})

        # Verificar erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(self):
        """Teste logout sem autenticação"""
        # Dados do logout
        data = {"refresh": str(self.refresh_token)}

        # Fazer logout sem autenticação
        response = self.client.post("/api/v1/auth/logout/", data)

        # Verificar erro de autenticação
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_already_blacklisted_token(self):
        """Teste logout com token já invalidado"""
        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Fazer blacklist do token manualmente
        self.refresh_token.blacklist()

        # Dados do logout
        data = {"refresh": str(self.refresh_token)}

        # Fazer logout
        response = self.client.post("/api/v1/auth/logout/", data)

        # Verificar erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.authentication.views.logger")
    def test_logout_logging(self, mock_logger):
        """Teste logs de segurança no logout"""
        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Dados do logout
        data = {"refresh": str(self.refresh_token)}

        # Fazer logout
        self.client.post("/api/v1/auth/logout/", data)

        # Verificar que foi logado
        mock_logger.info.assert_any_call(
            f"Tentativa de logout para: {self.user.email} ({self.user.role})"
        )
        mock_logger.info.assert_any_call(
            f"Logout bem-sucedido para: {self.user.email} ({self.user.role})"
        )


class TestCustomTokenObtainPairViewSecurity(BaseModelTestCase):
    """Testes de segurança para login JWT"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory(email="test@example.com", is_active=True)
        self.user.set_password("testpass123")
        self.user.save()

    @patch("apps.authentication.serializers.logger")
    def test_login_success_logging(self, mock_logger):
        """Teste logs de login bem-sucedido"""
        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post("/api/v1/auth/token/", data)

        # Verificar resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        # Verificar logs
        mock_logger.info.assert_any_call("Tentativa de login para: test@example.com")
        mock_logger.info.assert_any_call(
            f"Login bem-sucedido para: test@example.com (role: {self.user.role})"
        )

    @patch("apps.authentication.serializers.logger")
    def test_login_invalid_email_logging(self, mock_logger):
        """Teste logs de tentativa com email inexistente"""
        data = {"email": "inexistente@example.com", "password": "testpass123"}

        response = self.client.post("/api/v1/auth/token/", data)

        # Verificar erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar logs
        mock_logger.info.assert_called_with(
            "Tentativa de login para: inexistente@example.com"
        )
        mock_logger.warning.assert_called_with(
            "Tentativa de login com email inexistente: inexistente@example.com"
        )

    @patch("apps.authentication.serializers.logger")
    def test_login_wrong_password_logging(self, mock_logger):
        """Teste logs de tentativa com senha incorreta"""
        data = {"email": "test@example.com", "password": "senha_errada"}

        response = self.client.post("/api/v1/auth/token/", data)

        # Verificar erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar logs
        mock_logger.info.assert_called_with("Tentativa de login para: test@example.com")
        mock_logger.warning.assert_called_with(
            "Falha na autenticação para: test@example.com"
        )

    @patch("apps.authentication.serializers.logger")
    def test_login_inactive_user_logging(self, mock_logger):
        """Teste logs de tentativa com usuário inativo"""
        # Desativar usuário
        self.user.is_active = False
        self.user.save()

        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post("/api/v1/auth/token/", data)

        # Verificar erro
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar logs
        mock_logger.warning.assert_called_with(
            "Tentativa de login com usuário inativo: test@example.com"
        )

    def test_login_token_contains_user_info(self):
        """Teste que token JWT contém informações do usuário"""
        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post("/api/v1/auth/token/", data)

        # Verificar resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar dados do usuário na resposta
        user_data = response.data["user"]
        self.assertEqual(user_data["id"], str(self.user.id))
        self.assertEqual(user_data["email"], self.user.email)
        self.assertEqual(user_data["role"], self.user.role)
        self.assertEqual(user_data["is_verified"], self.user.is_verified)

    def test_login_updates_last_login(self):
        """Teste que login atualiza last_login"""
        # Verificar que last_login é None inicialmente
        self.assertIsNone(self.user.last_login)

        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post("/api/v1/auth/token/", data)

        # Verificar resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que last_login foi atualizado
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)


class TestJWTSecurityConfiguration(BaseModelTestCase):
    """Testes para configurações de segurança do JWT"""

    model_class = User

    def test_jwt_contains_security_claims(self):
        """Teste que JWT contém claims de segurança"""
        from apps.authentication.serializers import CustomTokenObtainPairSerializer

        user = UserFactory()
        token = CustomTokenObtainPairSerializer.get_token(user)

        # Verificar claims customizados
        self.assertIn("user_id", token)
        self.assertIn("email", token)
        self.assertIn("role", token)
        self.assertIn("is_verified", token)
        self.assertIn("login_time", token)

    def test_jwt_blacklist_functionality(self):
        """Teste funcionalidade de blacklist"""
        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken,
        )

        user = UserFactory()
        refresh_token = RefreshToken.for_user(user)

        # Verificar que o token está na tabela OutstandingToken
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        self.assertTrue(outstanding_tokens.exists())

        # Verificar que não está blacklistado inicialmente
        blacklisted_count_before = BlacklistedToken.objects.count()

        # Fazer blacklist
        refresh_token.blacklist()

        # Verificar que foi criado um registro de blacklist
        blacklisted_count_after = BlacklistedToken.objects.count()
        self.assertEqual(blacklisted_count_after, blacklisted_count_before + 1)


class TestMiddlewareSecurityIntegration(BaseModelTestCase):
    """Testes de integração com middleware de segurança"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = UserFactory()

    def test_authenticated_request_has_security_headers(self):
        """Teste que requests autenticados têm headers de segurança"""
        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Fazer request para endpoint protegido
        response = self.client.get("/api/v1/auth/users/me/")

        # Verificar headers de segurança
        self.assertIn("X-Content-Type-Options", response)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertIn("X-Frame-Options", response)
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertIn("X-XSS-Protection", response)
        self.assertEqual(response["X-XSS-Protection"], "1; mode=block")
