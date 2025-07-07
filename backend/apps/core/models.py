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
    is_active = models.BooleanField(default=True, help_text="Indica se o registro está ativo")
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


class ActiveManager(models.Manager):
    """Manager que retorna apenas registros ativos"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
