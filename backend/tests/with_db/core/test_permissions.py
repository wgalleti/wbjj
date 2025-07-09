"""
Testes para permissões customizadas do Core
Foco: Validação de autenticação, autorização e isolamento de tenant
Objetivo: 100% de cobertura para core/permissions.py
"""

from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.test import APIRequestFactory

from apps.core.permissions import (
    CanManagePayments,
    CanManageStudents,
    IsAdminOrReadOnly,
    IsInstructorOrAdmin,
    IsOwnerOrReadOnly,
    IsStudentOwner,
    TenantPermission,
)
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory

User = get_user_model()


class TestTenantPermission(BaseModelTestCase):
    """Testes para TenantPermission - isolamento de tenant"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = TenantPermission()
        self.factory = APIRequestFactory()

    def test_has_permission_authenticated_with_tenant(self):
        """Teste permissão com usuário autenticado e tenant configurado"""
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        # Mock tenant no request
        request.tenant = Mock()
        request.tenant.schema_name = "test_tenant"

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_unauthenticated(self):
        """Teste erro com usuário não autenticado"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    @patch("apps.core.permissions.logger")
    def test_has_permission_no_tenant(self, mock_logger):
        """Teste erro quando middleware não configurou tenant"""
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user
        # Não adicionar tenant ao request

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

        # Verificar que warning foi logado
        mock_logger.warning.assert_called_once_with(
            "Request sem tenant configurado - middleware não funcionou"
        )

    def test_has_object_permission_always_true(self):
        """Teste que permissão de objeto sempre retorna True com schema isolation"""
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        mock_obj = Mock()
        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertTrue(result)


class TestIsOwnerOrReadOnly(BaseModelTestCase):
    """Testes para IsOwnerOrReadOnly - proprietário ou somente leitura"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = IsOwnerOrReadOnly()
        self.factory = APIRequestFactory()

    def test_has_object_permission_safe_methods(self):
        """Teste que métodos seguros (GET, HEAD, OPTIONS) são sempre permitidos"""
        user = UserFactory()
        other_user = UserFactory()

        # Mock objeto com user diferente
        mock_obj = Mock()
        mock_obj.user = other_user

        for method in permissions.SAFE_METHODS:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = user

                result = self.permission.has_object_permission(request, None, mock_obj)
                self.assertTrue(result)

    def test_has_object_permission_owner_write(self):
        """Teste que proprietário pode escrever"""
        user = UserFactory()
        request = self.factory.post("/")
        request.user = user

        # Mock objeto com mesmo user
        mock_obj = Mock()
        mock_obj.user = user

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertTrue(result)

    def test_has_object_permission_non_owner_write(self):
        """Teste que não-proprietário não pode escrever"""
        user = UserFactory()
        other_user = UserFactory()
        request = self.factory.post("/")
        request.user = user

        # Mock objeto com user diferente
        mock_obj = Mock()
        mock_obj.user = other_user

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertFalse(result)


class TestIsInstructorOrAdmin(BaseModelTestCase):
    """Testes para IsInstructorOrAdmin - permissão para instrutor ou admin"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = IsInstructorOrAdmin()
        self.factory = APIRequestFactory()

    def test_has_permission_instructor(self):
        """Teste permissão para usuário instrutor"""
        user = UserFactory(role="instructor")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_admin(self):
        """Teste permissão para usuário admin"""
        user = UserFactory(role="admin")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_student_denied(self):
        """Teste negação para usuário estudante"""
        user = UserFactory(role="student")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_unauthenticated(self):
        """Teste negação para usuário não autenticado"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_no_role_attribute(self):
        """Teste negação para usuário sem atributo role"""
        user = UserFactory()
        # Remover atributo role
        delattr(user, "role")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)


class TestIsStudentOwner(BaseModelTestCase):
    """Testes para IsStudentOwner - estudante acessa apenas seus dados"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = IsStudentOwner()
        self.factory = APIRequestFactory()

    def test_has_object_permission_unauthenticated(self):
        """Teste negação para usuário não autenticado"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False

        mock_obj = Mock()
        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertFalse(result)

    def test_has_object_permission_object_with_student(self):
        """Teste objeto que tem relação com student"""
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        # Mock objeto com student.user = user
        mock_obj = Mock()
        mock_obj.student = Mock()
        mock_obj.student.user = user

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertTrue(result)

    def test_has_object_permission_object_with_different_student(self):
        """Teste objeto que tem relação com student diferente"""
        user = UserFactory()
        other_user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        # Mock objeto com student.user = other_user
        mock_obj = Mock()
        mock_obj.student = Mock()
        mock_obj.student.user = other_user

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertFalse(result)

    def test_has_object_permission_object_with_user(self):
        """Teste objeto que tem atributo user direto"""
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        # Mock objeto com user = user (como Student model)
        mock_obj = Mock()
        mock_obj.user = user
        # Remover student para testar o segundo caso
        delattr(mock_obj, "student")

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertTrue(result)

    def test_has_object_permission_object_with_different_user(self):
        """Teste objeto que tem user diferente"""
        user = UserFactory()
        other_user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        # Mock objeto com user = other_user
        mock_obj = Mock()
        mock_obj.user = other_user
        # Remover student para testar o segundo caso
        delattr(mock_obj, "student")

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertFalse(result)

    def test_has_object_permission_object_without_relations(self):
        """Teste objeto sem relações student ou user"""
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        # Mock objeto sem student nem user
        mock_obj = Mock()
        delattr(mock_obj, "student")
        delattr(mock_obj, "user")

        result = self.permission.has_object_permission(request, None, mock_obj)
        self.assertFalse(result)


class TestIsAdminOrReadOnly(BaseModelTestCase):
    """Testes para IsAdminOrReadOnly - admin ou somente leitura"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = IsAdminOrReadOnly()
        self.factory = APIRequestFactory()

    def test_has_permission_admin_write(self):
        """Teste admin pode escrever"""
        user = UserFactory(role="admin")
        request = self.factory.post("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_non_admin_safe_methods(self):
        """Teste não-admin pode usar métodos seguros"""
        user = UserFactory(role="student")

        for method in permissions.SAFE_METHODS:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = user

                result = self.permission.has_permission(request, None)
                self.assertTrue(result)

    def test_has_permission_non_admin_write_denied(self):
        """Teste não-admin não pode escrever"""
        user = UserFactory(role="student")
        request = self.factory.post("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_unauthenticated(self):
        """Teste usuário não autenticado negado"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)


class TestCanManageStudents(BaseModelTestCase):
    """Testes para CanManageStudents - gerenciar estudantes"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = CanManageStudents()
        self.factory = APIRequestFactory()

    def test_has_permission_admin(self):
        """Teste admin pode gerenciar estudantes"""
        user = UserFactory(role="admin")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_instructor(self):
        """Teste instrutor pode gerenciar estudantes"""
        user = UserFactory(role="instructor")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_student_denied(self):
        """Teste estudante não pode gerenciar estudantes"""
        user = UserFactory(role="student")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_unauthenticated(self):
        """Teste usuário não autenticado negado"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)


class TestCanManagePayments(BaseModelTestCase):
    """Testes para CanManagePayments - gerenciar pagamentos"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.permission = CanManagePayments()
        self.factory = APIRequestFactory()

    def test_has_permission_admin(self):
        """Teste admin pode gerenciar pagamentos"""
        user = UserFactory(role="admin")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertTrue(result)

    def test_has_permission_instructor_denied(self):
        """Teste instrutor não pode gerenciar pagamentos"""
        user = UserFactory(role="instructor")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_student_denied(self):
        """Teste estudante não pode gerenciar pagamentos"""
        user = UserFactory(role="student")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_unauthenticated(self):
        """Teste usuário não autenticado negado"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)

    def test_has_permission_no_role_attribute(self):
        """Teste usuário sem atributo role negado"""
        user = UserFactory()
        # Remover atributo role
        delattr(user, "role")
        request = self.factory.get("/")
        request.user = user

        result = self.permission.has_permission(request, None)
        self.assertFalse(result)
