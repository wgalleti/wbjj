from typing import ClassVar
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.core.models import BaseModel


class UserManager(BaseUserManager):
    """
    Manager personalizado para o modelo User
    """

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


class User(AbstractUser, BaseModel):
    """
    Modelo de usuário customizado que estende AbstractUser
    """

    ROLE_CHOICES: ClassVar = [
        ("student", "Aluno"),
        ("instructor", "Instrutor"),
        ("admin", "Administrador"),
        ("staff", "Staff"),
    ]

    # Campos personalizados
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        help_text="Papel do usuário no sistema",
    )

    # Remove username, usa email como identificador
    username = None
    email = models.EmailField(unique=True, help_text="Email será usado como login")

    # Campos adicionais
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="Email foi verificado")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering: ClassVar = ["email"]
        indexes: ClassVar = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_role_display_color(self):
        """Retorna cor baseada no papel do usuário"""
        colors = {
            "student": "#3B82F6",  # azul
            "instructor": "#10B981",  # verde
            "admin": "#F59E0B",  # amarelo
            "staff": "#8B5CF6",  # roxo
        }
        return colors.get(self.role, "#6B7280")
