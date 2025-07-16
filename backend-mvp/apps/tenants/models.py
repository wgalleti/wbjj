"""
Modelos para gestão de academias (tenants)

Implementação MVP simplificada com tenant_id:
- Tenant único por banco de dados
- Filtro automático por tenant_id
- Isolamento por aplicação
- Migrations simples
"""
from typing import ClassVar

from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import TimestampedModel


class Tenant(TimestampedModel):
    """
    Modelo principal para multitenancy MVP simplificado

    Implementação com tenant_id simples para isolamento de dados.
    Cada tenant representa uma academia/franquia com dados filtrados.
    """

    # Identificação do subdomínio
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        help_text="Subdomínio único (ex: gracie-barra para gracie-barra.wbjj.com)",
        validators=[RegexValidator(r'^[a-z0-9-]+$', 'Apenas letras minúsculas, números e hífens')]
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

    # Meta e __str__ definidos no final da classe

    @property
    def subdomain_url(self):
        """Retorna URL do subdomínio"""
        return f"https://{self.subdomain}.wbjj.com"

    def save(self, *args, **kwargs):
        """Validações antes de salvar"""
        # Garantir que subdomain seja lowercase
        if self.subdomain:
            self.subdomain = self.subdomain.lower()

        # Garantir que slug seja lowercase
        if self.slug:
            self.slug = self.slug.lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.subdomain})"

    class Meta:
        verbose_name = "Academia"
        verbose_name_plural = "Academias"
        ordering = ['name']
