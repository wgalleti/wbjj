"""
Factories para modelos de Tenants seguindo padrões brasileiros de academias de jiu-jitsu.

Seguindo CONTEXT.md:
- Dados realistas brasileiros
- Naming conventions consistentes
- Factories completas para testes
"""

import factory
from factory import fuzzy
from faker import Faker

from apps.tenants.models import Tenant

fake = Faker("pt_BR")  # Faker brasileiro


class TenantFactory(factory.django.DjangoModelFactory):
    """
    Factory para academias de jiu-jitsu brasileiras
    """

    class Meta:
        model = Tenant

    # Identificação
    name = factory.LazyFunction(lambda: fake.company() + " - Academia de Jiu-Jitsu")
    slug = factory.LazyAttribute(
        lambda obj: obj.name.lower()
        .replace(" ", "-")
        .replace("academia", "ac")
        .replace("jiu-jitsu", "jj")
        .replace("--", "-")[:50]
    )

    # Subdomain para MVP (sem schema separado)
    subdomain = factory.LazyAttribute(lambda obj: obj.slug[:100])

    # Contato
    email = factory.LazyAttribute(lambda obj: f"contato@{obj.slug}.com")
    phone = factory.LazyFunction(lambda: fake.phone_number())

    # Endereço brasileiro
    address = factory.LazyFunction(lambda: fake.street_address())
    city = factory.LazyFunction(lambda: fake.city())
    state = factory.LazyFunction(lambda: fake.state_abbr())
    zip_code = factory.LazyFunction(lambda: fake.postcode())
    country = "Brasil"

    # Configurações visuais (cores do BJJ)
    primary_color = fuzzy.FuzzyChoice(
        [
            "#000000",  # Preto - tradicional BJJ
            "#0000FF",  # Azul - cor clássica
            "#FF0000",  # Vermelho - cor forte
            "#800080",  # Roxo - faixa roxa
            "#8B4513",  # Marrom - faixa marrom
            "#FFD700",  # Dourado - detalhes
        ]
    )
    secondary_color = fuzzy.FuzzyChoice(
        [
            "#FFFFFF",  # Branco - tradicional
            "#C0C0C0",  # Prata - detalhes
            "#FFD700",  # Dourado - tradicional
            "#000000",  # Preto - contraste
        ]
    )

    # Negócio (preços brasileiros realistas)
    monthly_fee = fuzzy.FuzzyDecimal(80.00, 300.00, 2)  # R$ 80-300 por mês
    timezone = "America/Sao_Paulo"

    # Metadata
    founded_date = factory.LazyFunction(
        lambda: fake.date_between(start_date="-30y", end_date="-1y")
    )
    website = factory.LazyAttribute(lambda obj: f"https://www.{obj.slug}.com.br")

    # Status
    is_active = True


class TenantFactoryData:
    """
    Factories com dados específicos de academias famosas
    """

    @classmethod
    def gracie_barra(cls):
        """Academia Gracie Barra"""
        return TenantFactory(
            name="Gracie Barra São Paulo",
            slug="gracie-barra-sp",
            schema_name="tenant_gracie_barra_sp",
            domain_url="gracie-barra-sp.wbjj.com",
            email="contato@graciebarrasp.com.br",
            phone="+5511999888777",
            address="Av. Paulista, 1000 - Bela Vista",
            city="São Paulo",
            state="SP",
            zip_code="01310-100",
            primary_color="#FF0000",  # Vermelho GB
            secondary_color="#000000",  # Preto GB
            monthly_fee=250.00,
            website="https://www.graciebarrasp.com.br",
            founded_date=fake.date_between(start_date="-20y", end_date="-10y"),
        )

    @classmethod
    def alliance(cls):
        """Academia Alliance"""
        return TenantFactory(
            name="Alliance Jiu-Jitsu Rio",
            slug="alliance-rio",
            schema_name="tenant_alliance_rio",
            domain_url="alliance-rio.wbjj.com",
            email="info@allianceriodejaneiro.com.br",
            phone="+5521888777666",
            address="Rua Visconde de Pirajá, 500 - Ipanema",
            city="Rio de Janeiro",
            state="RJ",
            zip_code="22410-002",
            primary_color="#000000",  # Preto Alliance
            secondary_color="#FFD700",  # Dourado Alliance
            monthly_fee=280.00,
            website="https://www.allianceriodejaneiro.com.br",
            founded_date=fake.date_between(start_date="-25y", end_date="-15y"),
        )

    @classmethod
    def checkmat(cls):
        """Academia Checkmat"""
        return TenantFactory(
            name="Checkmat Brazilian Jiu-Jitsu",
            slug="checkmat-bh",
            schema_name="tenant_checkmat_bh",
            domain_url="checkmat-bh.wbjj.com",
            email="contato@checkmatbh.com.br",
            phone="+5531777666555",
            address="Av. do Contorno, 2000 - Centro",
            city="Belo Horizonte",
            state="MG",
            zip_code="30110-017",
            primary_color="#800080",  # Roxo Checkmat
            secondary_color="#FFFFFF",  # Branco Checkmat
            monthly_fee=200.00,
            website="https://www.checkmatbh.com.br",
            founded_date=fake.date_between(start_date="-18y", end_date="-8y"),
        )


# Alias para compatibilidade
TenantFactoryByType = TenantFactoryData
