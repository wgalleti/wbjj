"""
Modelos para gestão de academias (tenants)

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE usar schema-per-tenant
- 1 tenant = 1 PostgreSQL schema
- Isolamento total automático
- Migrations aplicadas em todos os schemas
"""
from typing import ClassVar

from django.core.validators import RegexValidator
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

from apps.core.models import TimestampedModel


class Tenant(TenantMixin, TimestampedModel):
    """
    Modelo principal para multitenancy usando django-tenant-schemas

    Herda de TenantMixin para isolamento automático por schema PostgreSQL.
    Cada tenant representa uma academia/franquia com schema isolado.
    """

    # Campos obrigatórios do django-tenant-schemas
    # schema_name é automaticamente adicionado pelo TenantMixin
    # domain_url é obrigatório para o django-tenants
    domain_url = models.CharField(
        max_length=253,
        help_text="Domínio do tenant (ex: academia-teste.wbjj.com)",
        unique=True,
    )

    # Identificação
    name = models.CharField(max_length=255, help_text="Nome da academia")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Slug único para subdomínio (ex: gracie-barra)",
    )

    # Contato
    email = models.EmailField(help_text="Email principal da academia")
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$")],
        help_text="Telefone da academia",
    )

    # Endereço
    address = models.TextField(help_text="Endereço completo")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="Brasil")

    # Configurações visuais
    logo = models.ImageField(upload_to="tenant_logos/", blank=True, null=True)
    primary_color = models.CharField(
        max_length=7,
        default="#3B82F6",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$")],
        help_text="Cor primária em hex (ex: #3B82F6)",
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#1E40AF",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$")],
        help_text="Cor secundária em hex",
    )

    # Configurações de negócio
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Mensalidade padrão",
        default=150.00,  # Valor padrão para testes
    )
    timezone = models.CharField(
        max_length=50, default="America/Sao_Paulo", help_text="Timezone da academia"
    )

    # Metadata
    founded_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True)

    # Status de ativação
    is_active = models.BooleanField(default=True, help_text="Academia ativa")

    class Meta:
        ordering: ClassVar = ["name"]
        indexes: ClassVar = [
            models.Index(fields=["slug"]),
            models.Index(fields=["schema_name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def subdomain_url(self):
        """Retorna URL do subdomínio"""
        return f"https://{self.slug}.wbjj.com"

    def save(self, *args, **kwargs):
        """
        Override para garantir que schema_name seja criado baseado no slug
        """
        if not self.schema_name:
            # Gerar schema_name baseado no slug, sanitizado para PostgreSQL
            self.schema_name = f"tenant_{self.slug}".replace("-", "_")

        # Garantir que domain_url seja definido
        if not self.domain_url:
            self.domain_url = f"{self.slug}.wbjj.com"

        super().save(*args, **kwargs)


class Domain(DomainMixin):
    """
    Model para domínios de tenant (obrigatório pelo django-tenants)
    """

    pass
