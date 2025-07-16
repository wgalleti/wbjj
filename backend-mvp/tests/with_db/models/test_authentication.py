"""
Testes para models de Authentication
Cobertura completa dos models User e funcionalidades de autenticação
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError

from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory

User = get_user_model()


class TestUserModel(BaseModelTestCase):
    """Testes para User model customizado"""

    model_class = User

    def test_create_user_success(self):
        """Teste criação básica de usuário"""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="João",
            last_name="Silva",
            password="testpass123",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "João")
        self.assertEqual(user.last_name, "Silva")
        self.assertEqual(user.role, "student")  # default
        self.assertFalse(user.is_verified)  # default
        self.assertTrue(user.check_password("testpass123"))

    def test_create_superuser_success(self):
        """Teste criação de superuser"""
        admin = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="adminpass123",
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, "admin")

    def test_user_str_representation(self):
        """Teste representação string do User"""
        user = UserFactory(
            first_name="João", last_name="Silva", email="test@example.com"
        )
        expected = "João Silva (test@example.com)"
        self.assertEqual(str(user), expected)

    def test_user_full_name_property(self):
        """Teste propriedade full_name"""
        user = UserFactory(first_name="João", last_name="Silva")
        self.assertEqual(user.full_name, "João Silva")

    def test_user_email_unique(self):
        """Teste unicidade do email"""
        UserFactory(email="test@example.com")

        with self.assertRaises(IntegrityError):
            # Force save para garantir que IntegrityError seja levantado
            user2 = UserFactory.build(email="test@example.com")
            user2.save()

    def test_user_roles(self):
        """Teste diferentes roles de usuário"""
        roles = ["student", "instructor", "manager", "admin"]

        for role in roles:
            user = UserFactory(role=role)
            self.assertEqual(user.role, role)

    def test_user_ordering(self):
        """Teste ordenação por nome"""
        UserFactory(first_name="Carlos", last_name="Silva", email="c@example.com")
        UserFactory(first_name="Ana", last_name="Santos", email="a@example.com")
        UserFactory(first_name="Bruno", last_name="Costa", email="b@example.com")

        users = User.objects.all()
        names = [user.first_name for user in users]

        self.assertEqual(names, ["Ana", "Bruno", "Carlos"])

    def test_is_instructor_method(self):
        """Teste método is_instructor"""
        instructor = UserFactory(role="instructor")
        admin = UserFactory(role="admin")
        student = UserFactory(role="student")

        self.assertTrue(instructor.is_instructor())
        self.assertTrue(admin.is_instructor())
        self.assertFalse(student.is_instructor())

    def test_is_student_user_method(self):
        """Teste método is_student_user"""
        student = UserFactory(role="student")
        instructor = UserFactory(role="instructor")

        self.assertTrue(student.is_student_user())
        self.assertFalse(instructor.is_student_user())

    def test_user_language_default(self):
        """Teste valor padrão do idioma"""
        user = UserFactory()
        self.assertEqual(user.language, "pt-br")

    def test_user_required_fields(self):
        """Teste campos obrigatórios"""
        # Email é obrigatório
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="", first_name="João", last_name="Silva", password="testpass123"
            )

    def test_user_phone_field(self):
        """Teste campo telefone opcional"""
        user = UserFactory(phone="+5511999999999")
        self.assertEqual(user.phone, "+5511999999999")

        # Pode ser vazio
        user_no_phone = UserFactory(phone="")
        self.assertEqual(user_no_phone.phone, "")

    def test_user_birth_date_field(self):
        """Teste campo data de nascimento opcional"""
        birth_date = date(1990, 5, 15)
        user = UserFactory(birth_date=birth_date)
        self.assertEqual(user.birth_date, birth_date)

        # Pode ser nulo
        user_no_birth = UserFactory(birth_date=None)
        self.assertIsNone(user_no_birth.birth_date)

    def test_user_verification_status(self):
        """Teste status de verificação"""
        user = UserFactory(is_verified=False)
        self.assertFalse(user.is_verified)

        # Verificar usuário
        user.is_verified = True
        user.save()
        self.assertTrue(user.is_verified)

    def test_password_hashing(self):
        """Teste hash de senhas"""
        password = "testpass123"
        user = User.objects.create_user(
            email="test@example.com",
            first_name="João",
            last_name="Silva",
            password=password,
        )

        # Senha não é armazenada em texto plano
        self.assertNotEqual(user.password, password)
        # Mas pode ser verificada
        self.assertTrue(user.check_password(password))
        # Senha incorreta falha
        self.assertFalse(user.check_password("wrongpass"))

    def test_user_manager_methods(self):
        """Teste métodos customizados do UserManager"""
        # create_user sem role usa padrão
        user = User.objects.create_user(
            email="student@example.com",
            first_name="Aluno",
            last_name="Teste",
            password="pass123",
        )
        self.assertEqual(user.role, "student")

        # create_superuser define role admin
        admin = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="Teste",
            password="adminpass123",
        )
        self.assertEqual(admin.role, "admin")

    def test_username_field_configuration(self):
        """Teste configuração USERNAME_FIELD"""
        # USERNAME_FIELD deve ser email
        self.assertEqual(User.USERNAME_FIELD, "email")

        # REQUIRED_FIELDS deve incluir nomes
        self.assertIn("first_name", User.REQUIRED_FIELDS)
        self.assertIn("last_name", User.REQUIRED_FIELDS)

    def test_user_active_status(self):
        """Teste status ativo/inativo"""
        user = UserFactory(is_active=True)
        self.assertTrue(user.is_active)

        # Desativar usuário
        user.is_active = False
        user.save()
        self.assertFalse(user.is_active)


class TestUserRolePermissions(BaseModelTestCase):
    """Testes para roles e permissões de usuário"""

    model_class = User

    def test_admin_permissions(self):
        """Teste permissões de admin"""
        admin = UserFactory(role="admin", is_staff=True, is_superuser=True)

        self.assertTrue(admin.is_instructor())
        self.assertFalse(admin.is_student_user())
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_instructor_permissions(self):
        """Teste permissões de instrutor"""
        instructor = UserFactory(role="instructor")

        self.assertTrue(instructor.is_instructor())
        self.assertFalse(instructor.is_student_user())
        self.assertFalse(instructor.is_staff)
        self.assertFalse(instructor.is_superuser)

    def test_student_permissions(self):
        """Teste permissões de aluno"""
        student = UserFactory(role="student")

        self.assertFalse(student.is_instructor())
        self.assertTrue(student.is_student_user())
        self.assertFalse(student.is_staff)
        self.assertFalse(student.is_superuser)

    def test_manager_permissions(self):
        """Teste permissões de gerente"""
        manager = UserFactory(role="manager")

        self.assertFalse(manager.is_instructor())
        self.assertFalse(manager.is_student_user())
        self.assertFalse(manager.is_staff)
        self.assertFalse(manager.is_superuser)


class TestUserIntegration(BaseModelTestCase):
    """Testes de integração para User model"""

    model_class = User

    def test_user_creation_flow(self):
        """Teste fluxo completo de criação de usuário"""
        # 1. Criar usuário instrutor
        instructor = User.objects.create_user(
            email="instructor@example.com",
            first_name="Carlos",
            last_name="Santos",
            password="instructor123",
            role="instructor",
        )

        # 2. Verificar dados básicos
        self.assertEqual(instructor.email, "instructor@example.com")
        self.assertEqual(instructor.full_name, "Carlos Santos")
        self.assertEqual(instructor.role, "instructor")
        self.assertTrue(instructor.is_instructor())

        # 3. Verificar autenticação
        self.assertTrue(instructor.check_password("instructor123"))

        # 4. Verificar status inicial
        self.assertFalse(instructor.is_verified)
        self.assertTrue(instructor.is_active)

    def test_user_roles_and_permissions(self):
        """Teste diferentes roles e suas permissões"""
        # Criar usuários com diferentes roles
        student = UserFactory(role="student")
        instructor = UserFactory(role="instructor")
        manager = UserFactory(role="manager")
        admin = UserFactory(role="admin", is_staff=True, is_superuser=True)

        # Definir expectativas (user, is_instructor, is_student, is_staff, is_superuser)
        users_data = [
            (student, False, True, False, False),
            (instructor, True, False, False, False),
            (manager, False, False, False, False),
            (admin, True, False, True, True),
        ]

        for user, is_instr, is_stud, is_staff, is_super in users_data:
            self.assertEqual(user.is_instructor(), is_instr)
            self.assertEqual(user.is_student_user(), is_stud)
            self.assertEqual(user.is_staff, is_staff)
            self.assertEqual(user.is_superuser, is_super)

        # Cleanup automático pelo Django TestCase


class TestTenantMiddleware(BaseModelTestCase):
    """Testes para TenantMiddleware"""

    model_class = User

    def test_middleware_structure(self):
        """Teste estrutura básica do middleware"""
        from apps.authentication.middleware import TenantMiddleware

        # Verificar que middleware pode ser importado
        self.assertTrue(TenantMiddleware)

        # Verificar que tem os métodos esperados
        expected_methods = [
            "process_request",
            "_extract_subdomain",
            "_get_tenant_by_subdomain",
        ]

        for method in expected_methods:
            self.assertTrue(hasattr(TenantMiddleware, method))
