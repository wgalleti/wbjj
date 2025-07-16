import uuid

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model para auditoria temporal
    Adiciona created_at, updated_at automaticamente
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model para soft delete
    Adiciona is_active field
    """

    is_active = models.BooleanField(
        default=True, help_text="Indica se o registro está ativo"
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete - marca como inativo ao invés de deletar"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Delete real do banco de dados"""
        super().delete(using=using, keep_parents=keep_parents)


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Model base completo com timestamp + soft delete
    Herdar de BaseModel em todos os models principais
    """

    class Meta:
        abstract = True


class TenantMixin(models.Model):
    """
    Mixin para implementar multitenancy por tenant_id
    Adiciona relacionamento com Tenant e validações
    """

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        help_text="Tenant ao qual este registro pertence"
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['tenant']),
        ]

    def save(self, *args, **kwargs):
        """Validar que tenant é obrigatório"""
        if not self.tenant_id:
            raise ValueError("Tenant é obrigatório para este model")
        super().save(*args, **kwargs)


class ActiveManager(models.Manager):
    """Manager que retorna apenas registros ativos"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class TenantManager(models.Manager):
    """Manager que filtra automaticamente por tenant"""

    def __init__(self, tenant_id=None):
        super().__init__()
        self.tenant_id = tenant_id

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tenant_id:
            qs = qs.filter(tenant_id=self.tenant_id)
        return qs
