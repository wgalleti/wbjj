"""
Factories para modelos de Authentication seguindo padrões brasileiros.

Seguindo CONTEXT.md:
- Dados realistas brasileiros
- Naming conventions consistentes
- Factories completas para testes
"""

from datetime import date

import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker("pt_BR")  # Faker brasileiro


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory para usuários brasileiros do sistema
    """

    class Meta:
        model = User
        skip_postgeneration_save = True

    # Dados pessoais brasileiros - garantir unicidade sem get_or_create
    email = factory.Sequence(lambda n: f"user{n:06d}@test.com")
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())

    # Telefone brasileiro
    phone = factory.LazyFunction(lambda: fake.phone_number())

    # Data de nascimento realista (18-65 anos)
    birth_date = factory.LazyFunction(
        lambda: fake.date_between(start_date="-65y", end_date="-18y")
    )

    # Status padrão
    is_active = True
    is_verified = False
    role = "student"  # Padrão

    # Senha padrão para testes
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class StudentUserFactory(UserFactory):
    """Factory para usuários estudantes"""

    class Meta:
        skip_postgeneration_save = True

    role = "student"


class InstructorUserFactory(UserFactory):
    """Factory para usuários instrutores"""

    class Meta:
        skip_postgeneration_save = True

    role = "instructor"
    is_verified = True


class AdminUserFactory(UserFactory):
    """Factory para usuários administradores"""

    class Meta:
        skip_postgeneration_save = True

    role = "admin"
    is_staff = True
    is_superuser = True
    is_verified = True


class StaffUserFactory(UserFactory):
    """Factory para usuários staff"""

    class Meta:
        skip_postgeneration_save = True

    role = "staff"
    is_staff = True
    is_verified = True


class UserFactoryData:
    """
    Factories com dados específicos para casos de teste
    """

    @classmethod
    def unverified_student(cls):
        """Estudante não verificado"""
        return StudentUserFactory(
            email="student.unverified@test.com",
            first_name="João",
            last_name="Silva",
            is_verified=False,
        )

    @classmethod
    def verified_instructor(cls):
        """Instrutor verificado"""
        return InstructorUserFactory(
            email="instructor@test.com",
            first_name="Carlos",
            last_name="Gracie",
            is_verified=True,
            birth_date=date(1985, 3, 15),
        )

    @classmethod
    def super_admin(cls):
        """Super administrador"""
        return AdminUserFactory(
            email="admin@test.com",
            first_name="Admin",
            last_name="Sistema",
            is_superuser=True,
            is_staff=True,
        )
