from typing import ClassVar

from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import BaseModel


class Tenant(BaseModel):
    """
    Model principal para multitenancy
    Representa uma academia/franquia
    """

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
        max_digits=10, decimal_places=2, help_text="Mensalidade padrão"
    )
    timezone = models.CharField(
        max_length=50, default="America/Sao_Paulo", help_text="Timezone da academia"
    )

    # Metadata
    founded_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True)

    class Meta:
        db_table = "tenants"
        ordering: ClassVar = ["name"]
        indexes: ClassVar = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def subdomain_url(self):
        """Retorna URL do subdomínio"""
        return f"https://{self.slug}.wbjj.com"
