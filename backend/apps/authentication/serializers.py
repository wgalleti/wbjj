"""
Serializers para autenticação

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE documentar campos computados
- Validações rigorosas
- Campos de auditoria padronizados
"""
from typing import ClassVar

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.serializers import BaseModelSerializer

from .models import User


class UserSerializer(BaseModelSerializer):
    """
    Serializer para usuários do sistema
    """

    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        """Nome completo do usuário"""
        return obj.full_name

    @extend_schema_field(serializers.CharField())
    def get_role_display(self, obj):
        """Papel do usuário formatado"""
        return obj.get_role_display()

    @extend_schema_field(serializers.IntegerField())
    def get_age(self, obj):
        """Idade do usuário calculada"""
        if obj.birth_date:
            today = timezone.now().date()
            return (
                today.year
                - obj.birth_date.year
                - (
                    (today.month, today.day)
                    < (obj.birth_date.month, obj.birth_date.day)
                )
            )
        return None

    class Meta:
        model = User
        fields: ClassVar = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "role",
            "is_verified",
            "language",
            "is_active",
            "last_login",
            "created_at",
            "updated_at",
            # Campos computados
            "full_name",
            "role_display",
            "age",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "last_login",
            "full_name",
            "role_display",
            "age",
        ]
        extra_kwargs: ClassVar = {
            "email": {"help_text": "Email único do usuário"},
            "first_name": {"help_text": "Primeiro nome"},
            "last_name": {"help_text": "Sobrenome"},
            "phone": {"help_text": "Telefone de contato"},
            "birth_date": {"help_text": "Data de nascimento"},
            "role": {"help_text": "Papel do usuário no sistema"},
            "is_verified": {"help_text": "Indica se o email foi verificado"},
            "language": {"help_text": "Idioma preferido"},
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuários
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="Senha deve seguir as regras de segurança",
    )
    password_confirm = serializers.CharField(
        write_only=True, help_text="Confirmação da senha"
    )

    class Meta:
        model = User
        fields: ClassVar = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "role",
            "language",
            "password",
            "password_confirm",
        ]
        extra_kwargs: ClassVar = {
            "email": {"help_text": "Email único do usuário"},
            "first_name": {"help_text": "Primeiro nome"},
            "last_name": {"help_text": "Sobrenome"},
            "phone": {"help_text": "Telefone de contato"},
            "birth_date": {"help_text": "Data de nascimento"},
            "role": {"help_text": "Papel do usuário no sistema"},
            "language": {"help_text": "Idioma preferido"},
        }

    def validate(self, attrs):
        """Validação customizada"""
        # Validar confirmação de senha
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem"}
            )

        # Validar email único
        if User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError({"email": "Este email já está em uso"})

        return attrs

    def create(self, validated_data):
        """Criação customizada de usuário"""
        # Remove confirmação de senha
        validated_data.pop("password_confirm", None)

        # Extrai senha
        password = validated_data.pop("password")

        # Cria usuário
        user = User.objects.create_user(password=password, **validated_data)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de usuários
    """

    class Meta:
        model = User
        fields: ClassVar = [
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "language",
            "is_active",
        ]
        extra_kwargs: ClassVar = {
            "first_name": {"help_text": "Primeiro nome"},
            "last_name": {"help_text": "Sobrenome"},
            "phone": {"help_text": "Telefone de contato"},
            "birth_date": {"help_text": "Data de nascimento"},
            "language": {"help_text": "Idioma preferido"},
            "is_active": {"help_text": "Status ativo do usuário"},
        }


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha
    """

    old_password = serializers.CharField(write_only=True, help_text="Senha atual")
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password], help_text="Nova senha"
    )
    new_password_confirm = serializers.CharField(
        write_only=True, help_text="Confirmação da nova senha"
    )

    def validate(self, attrs):
        """Validação customizada"""
        # Validar confirmação de senha
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": "As senhas não coincidem"}
            )

        return attrs

    def validate_old_password(self, value):
        """Validar senha atual"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para JWT com informações adicionais
    """

    @classmethod
    def get_token(cls, user):
        """Adiciona informações customizadas ao token"""
        token = super().get_token(user)

        # Adiciona informações do usuário
        token["user_id"] = str(user.id)
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["role"] = user.role
        token["is_verified"] = user.is_verified

        return token

    def validate(self, attrs):
        """Validação customizada do login"""
        data = super().validate(attrs)

        # Adiciona informações do usuário na resposta
        data["user"] = {
            "id": str(self.user.id),
            "email": self.user.email,
            "full_name": self.user.full_name,
            "role": self.user.role,
            "is_verified": self.user.is_verified,
        }

        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login
    """

    email = serializers.EmailField(help_text="Email do usuário")
    password = serializers.CharField(write_only=True, help_text="Senha do usuário")

    class Meta:
        fields: ClassVar = ["email", "password"]
