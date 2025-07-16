"""
Testes para serializers de Tenant
Foco: Validações brasileiras, campos obrigatórios, formatação
Objetivo: 100% de cobertura para tenants/serializers.py
"""

from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.tenants.models import Tenant
from apps.tenants.serializers import (
    TenantCreateSerializer,
    TenantPublicSerializer,
    TenantSerializer,
    TenantUpdateSerializer,
)
from tests.base import BaseModelTestCase
from tests.with_db.factories import TenantFactory

User = get_user_model()


def get_valid_tenant_data():
    """Helper para criar dados válidos de tenant"""
    return {
        "name": "Academia Teste",
        "slug": "academia-teste",
        "email": "teste@academia.com",
        "phone": "+5511999999999",
        "address": "Rua Teste, 123",
        "city": "São Paulo",
        "state": "SP",
        "zip_code": "01234567",
        "country": "Brasil",
        "primary_color": "#FF0000",
        "secondary_color": "#0000FF",
        "monthly_fee": Decimal("200.00"),
        "timezone": "America/Sao_Paulo",
        "website": "https://teste.com",
    }


class TestTenantSerializer(BaseModelTestCase):
    """Testes para TenantSerializer - campos computados"""

    model_class = Tenant

    def test_serialize_computed_fields(self):
        """Teste campos computados do TenantSerializer"""
        tenant = TenantFactory(
            name="Gracie Barra SP",
            slug="gracie-barra-sp",
            address="Av. Paulista, 1000",
            city="São Paulo",
            state="SP",
            zip_code="01310-100",
            monthly_fee=Decimal("250.00"),
        )

        serializer = TenantSerializer(tenant)
        data = serializer.data

        # Verificar campos computados
        self.assertEqual(data["subdomain_url"], "https://gracie-barra-sp.wbjj.com")
        self.assertEqual(
            data["full_address"], "Av. Paulista, 1000, São Paulo, SP - 01310-100"
        )
        self.assertEqual(data["monthly_fee_formatted"], "R$ 250,00")

        # Verificar campos básicos
        self.assertEqual(data["name"], "Gracie Barra SP")
        self.assertEqual(data["slug"], "gracie-barra-sp")


class TestTenantCreateSerializer(BaseModelTestCase):
    """Testes para TenantCreateSerializer - validações básicas"""

    model_class = Tenant

    def test_validate_monthly_fee_zero_invalid(self):
        """Teste validação mensalidade zero é inválida"""
        data = get_valid_tenant_data()
        data["monthly_fee"] = Decimal("0.00")

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("monthly_fee", serializer.errors)

    def test_validate_monthly_fee_negative_invalid(self):
        """Teste validação mensalidade negativa é inválida"""
        data = get_valid_tenant_data()
        data["monthly_fee"] = Decimal("-100.00")

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("monthly_fee", serializer.errors)

    def test_validate_monthly_fee_positive_valid(self):
        """Teste validação mensalidade positiva é válida"""
        data = get_valid_tenant_data()
        data["monthly_fee"] = Decimal("150.00")

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_primary_color_format_invalid(self):
        """Teste validação cor primária formato inválido"""
        data = get_valid_tenant_data()
        data["primary_color"] = "FF0000"  # Sem #

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("primary_color", serializer.errors)

    def test_validate_primary_color_length_invalid(self):
        """Teste validação cor primária tamanho inválido"""
        data = get_valid_tenant_data()
        data["primary_color"] = "#FF00"  # Muito curto

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("primary_color", serializer.errors)

    def test_validate_primary_color_valid(self):
        """Teste validação cor primária válida"""
        data = get_valid_tenant_data()
        data["primary_color"] = "#FF0000"

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_secondary_color_format_invalid(self):
        """Teste validação cor secundária formato inválido"""
        data = get_valid_tenant_data()
        data["secondary_color"] = "0000FF"  # Sem #

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("secondary_color", serializer.errors)

    def test_validate_secondary_color_valid(self):
        """Teste validação cor secundária válida"""
        data = get_valid_tenant_data()
        data["secondary_color"] = "#0000FF"

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_slug_format_invalid_characters(self):
        """Teste validação slug com caracteres inválidos"""
        data = get_valid_tenant_data()
        data["slug"] = "slug-com@caracteres#inválidos"

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_validate_slug_already_exists(self):
        """Teste validação slug já existe"""
        # Criar tenant existente
        TenantFactory(slug="slug-existente")

        data = get_valid_tenant_data()
        data["slug"] = "slug-existente"

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_validate_slug_valid(self):
        """Teste validação slug válido"""
        data = get_valid_tenant_data()
        data["slug"] = "slug-valido-123"

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_email_already_exists(self):
        """Teste validação email já existe"""
        # Criar tenant existente
        TenantFactory(email="email@existente.com")

        data = get_valid_tenant_data()
        data["email"] = "email@existente.com"

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_validate_email_valid(self):
        """Teste validação email válido"""
        data = get_valid_tenant_data()
        data["email"] = "email@valido.com"

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_zip_code_format_invalid(self):
        """Teste validação CEP formato inválido"""
        data = get_valid_tenant_data()
        data["zip_code"] = "123"  # Muito curto

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("zip_code", serializer.errors)

    def test_validate_zip_code_non_numeric_invalid(self):
        """Teste validação CEP não numérico inválido"""
        data = get_valid_tenant_data()
        data["zip_code"] = "ABCD1234"  # Letras

        serializer = TenantCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("zip_code", serializer.errors)

    def test_validate_zip_code_valid_with_formatting(self):
        """Teste validação CEP válido com formatação"""
        data = get_valid_tenant_data()
        data["zip_code"] = "01234-567"  # Com hífen

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Verificar que foi limpo na validação
        validated_data = serializer.validated_data
        self.assertEqual(validated_data["zip_code"], "01234567")

    def test_validate_zip_code_valid_without_formatting(self):
        """Teste validação CEP válido sem formatação"""
        data = get_valid_tenant_data()
        data["zip_code"] = "01234567"  # Sem hífen

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_auto_generate_slug(self):
        """Teste auto-geração de slug baseado no nome"""
        data = get_valid_tenant_data()
        data["name"] = "Academia Super Legal"
        del data["slug"]  # Remover slug para testar auto-geração

        serializer = TenantCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Verificar que slug foi gerado
        validated_data = serializer.validated_data
        self.assertEqual(validated_data["slug"], "academia-super-legal")


class TestTenantUpdateSerializer(BaseModelTestCase):
    """Testes para TenantUpdateSerializer - validações de atualização"""

    model_class = Tenant

    def test_update_monthly_fee_invalid(self):
        """Teste atualização mensalidade inválida"""
        data = {"monthly_fee": Decimal("-50.00")}

        serializer = TenantUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("monthly_fee", serializer.errors)

    def test_update_monthly_fee_valid(self):
        """Teste atualização mensalidade válida"""
        tenant = TenantFactory()
        data = {"monthly_fee": Decimal("300.00")}

        serializer = TenantUpdateSerializer(tenant, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_primary_color_invalid(self):
        """Teste atualização cor primária inválida"""
        data = {"primary_color": "invalid-color"}

        serializer = TenantUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("primary_color", serializer.errors)

    def test_update_primary_color_valid(self):
        """Teste atualização cor primária válida"""
        tenant = TenantFactory()
        data = {"primary_color": "#00FF00"}

        serializer = TenantUpdateSerializer(tenant, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_secondary_color_invalid(self):
        """Teste atualização cor secundária inválida"""
        data = {"secondary_color": "#GGGGGG"}  # G não é válido

        serializer = TenantUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("secondary_color", serializer.errors)

    def test_update_secondary_color_valid(self):
        """Teste atualização cor secundária válida"""
        tenant = TenantFactory()
        data = {"secondary_color": "#FF00FF"}

        serializer = TenantUpdateSerializer(tenant, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_zip_code_invalid(self):
        """Teste atualização CEP inválido"""
        data = {"zip_code": "123ABC"}

        serializer = TenantUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("zip_code", serializer.errors)

    def test_update_zip_code_valid(self):
        """Teste atualização CEP válido"""
        tenant = TenantFactory()
        data = {"zip_code": "12345-678"}

        serializer = TenantUpdateSerializer(tenant, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class TestTenantPublicSerializer(BaseModelTestCase):
    """Testes para TenantPublicSerializer - dados públicos"""

    model_class = Tenant

    def test_public_fields_only(self):
        """Teste que apenas campos públicos são expostos"""
        tenant = TenantFactory(
            name="Academia Pública",
            slug="academia-publica",
            email="contato@publica.com",
        )

        serializer = TenantPublicSerializer(tenant)
        data = serializer.data

        # Verificar campos que devem estar presentes
        self.assertIn("name", data)
        self.assertIn("slug", data)
        self.assertIn("email", data)
        self.assertIn("primary_color", data)
        self.assertIn("secondary_color", data)
        self.assertIn("subdomain_url", data)
        self.assertIn("full_address", data)

        # Verificar campos sensíveis que NÃO devem estar presentes
        self.assertNotIn("monthly_fee", data)
        self.assertNotIn("schema_name", data)
        self.assertNotIn("domain_url", data)
