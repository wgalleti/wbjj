"""
Serializers para gestão de academias (tenants)

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE documentar campos computados
- Validações rigorosas de negócio
- Campos de auditoria padronizados
"""
from typing import ClassVar

from django.utils.text import slugify
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.serializers import BaseModelSerializer

from .models import Tenant


class TenantSerializer(BaseModelSerializer):
    """
    Serializer para academias (tenants)
    """

    subdomain_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    monthly_fee_formatted = serializers.SerializerMethodField()

    @extend_schema_field(serializers.URLField())
    def get_subdomain_url(self, obj):
        """URL do subdomínio"""
        return obj.subdomain_url

    @extend_schema_field(serializers.CharField())
    def get_full_address(self, obj):
        """Endereço completo formatado"""
        return f"{obj.address}, {obj.city}, {obj.state} - {obj.zip_code}"

    @extend_schema_field(serializers.CharField())
    def get_monthly_fee_formatted(self, obj):
        """Mensalidade formatada"""
        return (
            f"R$ {obj.monthly_fee:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    class Meta:
        model = Tenant
        fields: ClassVar = [
            "id",
            "name",
            "slug",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "logo",
            "primary_color",
            "secondary_color",
            "monthly_fee",
            "timezone",
            "founded_date",
            "website",
            "is_active",
            "created_at",
            "updated_at",
            # Campos computados
            "subdomain_url",
            "full_address",
            "monthly_fee_formatted",
        ]
        read_only_fields: ClassVar = [
            "id",
            "created_at",
            "updated_at",
            "subdomain_url",
            "full_address",
            "monthly_fee_formatted",
        ]
        extra_kwargs: ClassVar = {
            "name": {"help_text": "Nome da academia"},
            "slug": {"help_text": "Slug único para subdomínio"},
            "email": {"help_text": "Email principal da academia"},
            "phone": {"help_text": "Telefone da academia"},
            "address": {"help_text": "Endereço completo"},
            "city": {"help_text": "Cidade"},
            "state": {"help_text": "Estado"},
            "zip_code": {"help_text": "CEP"},
            "country": {"help_text": "País"},
            "logo": {"help_text": "Logo da academia"},
            "primary_color": {"help_text": "Cor primária em hex"},
            "secondary_color": {"help_text": "Cor secundária em hex"},
            "monthly_fee": {"help_text": "Mensalidade padrão"},
            "timezone": {"help_text": "Timezone da academia"},
            "founded_date": {"help_text": "Data de fundação"},
            "website": {"help_text": "Site da academia"},
        }


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de academias
    """

    class Meta:
        model = Tenant
        fields: ClassVar = [
            "name",
            "slug",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "primary_color",
            "secondary_color",
            "monthly_fee",
            "timezone",
            "founded_date",
            "website",
        ]
        extra_kwargs: ClassVar = {
            "name": {"help_text": "Nome da academia"},
            "slug": {"help_text": "Slug único para subdomínio"},
            "email": {"help_text": "Email principal da academia"},
            "phone": {"help_text": "Telefone da academia"},
            "address": {"help_text": "Endereço completo"},
            "city": {"help_text": "Cidade"},
            "state": {"help_text": "Estado"},
            "zip_code": {"help_text": "CEP"},
            "country": {"help_text": "País"},
            "primary_color": {"help_text": "Cor primária em hex"},
            "secondary_color": {"help_text": "Cor secundária em hex"},
            "monthly_fee": {"help_text": "Mensalidade padrão"},
            "timezone": {"help_text": "Timezone da academia"},
            "founded_date": {"help_text": "Data de fundação"},
            "website": {"help_text": "Site da academia"},
        }

    def validate_slug(self, value):
        """Validar slug único"""
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Este slug já está em uso")

        # Validar formato do slug
        if not value.replace("-", "").replace("_", "").isalnum():
            raise serializers.ValidationError(
                "Slug deve conter apenas letras, números, hífens e underscores"
            )

        return value

    def validate_email(self, value):
        """Validar email único"""
        if Tenant.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso")
        return value

    def validate_monthly_fee(self, value):
        """Validar mensalidade"""
        if value <= 0:
            raise serializers.ValidationError("Mensalidade deve ser maior que zero")
        return value

    def validate_primary_color(self, value):
        """Validar cor primária"""
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError("Cor deve estar no formato #RRGGBB")
        return value

    def validate_secondary_color(self, value):
        """Validar cor secundária"""
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError("Cor deve estar no formato #RRGGBB")
        return value

    def validate_zip_code(self, value):
        """Validar CEP"""
        # Remove caracteres especiais
        clean_zip = value.replace("-", "").replace(".", "").replace(" ", "")

        if len(clean_zip) != 8 or not clean_zip.isdigit():
            raise serializers.ValidationError("CEP deve ter 8 dígitos")

        return clean_zip

    def validate(self, attrs):
        """Validação customizada"""
        # Auto-gerar slug se não fornecido
        if not attrs.get("slug") and attrs.get("name"):
            attrs["slug"] = slugify(attrs["name"])

        return attrs


class TenantUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de academias
    """

    class Meta:
        model = Tenant
        fields: ClassVar = [
            "name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "primary_color",
            "secondary_color",
            "monthly_fee",
            "timezone",
            "founded_date",
            "website",
        ]
        extra_kwargs: ClassVar = {
            "name": {"help_text": "Nome da academia"},
            "email": {"help_text": "Email principal da academia"},
            "phone": {"help_text": "Telefone da academia"},
            "address": {"help_text": "Endereço completo"},
            "city": {"help_text": "Cidade"},
            "state": {"help_text": "Estado"},
            "zip_code": {"help_text": "CEP"},
            "country": {"help_text": "País"},
            "primary_color": {"help_text": "Cor primária em hex"},
            "secondary_color": {"help_text": "Cor secundária em hex"},
            "monthly_fee": {"help_text": "Mensalidade padrão"},
            "timezone": {"help_text": "Timezone da academia"},
            "founded_date": {"help_text": "Data de fundação"},
            "website": {"help_text": "Site da academia"},
        }

    def validate_monthly_fee(self, value):
        """Validar mensalidade"""
        if value <= 0:
            raise serializers.ValidationError("Mensalidade deve ser maior que zero")
        return value

    def validate_primary_color(self, value):
        """Validar cor primária"""
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError("Cor deve estar no formato #RRGGBB")
        return value

    def validate_secondary_color(self, value):
        """Validar cor secundária"""
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError("Cor deve estar no formato #RRGGBB")
        return value

    def validate_zip_code(self, value):
        """Validar CEP"""
        # Remove caracteres especiais
        clean_zip = value.replace("-", "").replace(".", "").replace(" ", "")

        if len(clean_zip) != 8 or not clean_zip.isdigit():
            raise serializers.ValidationError("CEP deve ter 8 dígitos")

        return clean_zip


class TenantPublicSerializer(serializers.ModelSerializer):
    """
    Serializer para informações públicas da academia

    Usado em páginas de login e landing pages
    """

    subdomain_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    @extend_schema_field(serializers.URLField())
    def get_subdomain_url(self, obj):
        """URL do subdomínio"""
        return obj.subdomain_url

    @extend_schema_field(serializers.CharField())
    def get_full_address(self, obj):
        """Endereço completo formatado"""
        return f"{obj.address}, {obj.city}, {obj.state} - {obj.zip_code}"

    class Meta:
        model = Tenant
        fields: ClassVar = [
            "id",
            "name",
            "slug",
            "email",
            "phone",
            "city",
            "state",
            "country",
            "logo",
            "primary_color",
            "secondary_color",
            "website",
            "founded_date",
            # Campos computados
            "subdomain_url",
            "full_address",
        ]
        read_only_fields: ClassVar = [
            "id",
            "name",
            "slug",
            "email",
            "phone",
            "city",
            "state",
            "country",
            "logo",
            "primary_color",
            "secondary_color",
            "website",
            "founded_date",
            "subdomain_url",
            "full_address",
        ]
