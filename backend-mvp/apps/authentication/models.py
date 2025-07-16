from typing import ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from apps.core.models import TimestampedModel, TenantMixin


class UserManager(BaseUserManager):
    """Manager customizado para User model que usa email como username"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimestampedModel, TenantMixin):
    """
    User personalizado baseado em AbstractUser
    Adiciona campos específicos do wBJJ
    """

    # Remove username, usar email como identificador
    username = None
    email = models.EmailField(unique=True, help_text="Email do usuário")

    # Manager customizado
    objects = UserManager()

    # Campos pessoais
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)

    # Campos profissionais
    ROLE_CHOICES: ClassVar = [
        ("admin", "Administrador"),
        ("instructor", "Instrutor"),
        ("manager", "Gerente"),
        ("student", "Aluno"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    # Relacionamento com tenant (preparação multitenancy)
    # tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)

    # Configurações
    is_verified = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default="pt-br")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering: ClassVar = ["first_name", "last_name"]
        indexes: ClassVar = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_instructor(self):
        return self.role in ["instructor", "admin"]

    def is_student_user(self):
        return self.role == "student"
