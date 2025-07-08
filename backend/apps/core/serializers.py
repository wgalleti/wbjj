"""
Serializers base para o sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE documentar campos computados
- Validações rigorosas
- Campos de auditoria padronizados
"""
from typing import ClassVar

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class TimestampedModelSerializer(serializers.ModelSerializer):
    """
    Serializer base para models com timestamps

    Adiciona campos de auditoria padronizados
    """

    @extend_schema_field(serializers.DateTimeField())
    def get_created_at_formatted(self, obj):
        """Data de criação formatada"""
        return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")

    @extend_schema_field(serializers.DateTimeField())
    def get_updated_at_formatted(self, obj):
        """Data de atualização formatada"""
        return obj.updated_at.strftime("%d/%m/%Y %H:%M:%S")

    class Meta:
        abstract = True
        fields: ClassVar = ["id", "created_at", "updated_at"]
        read_only_fields: ClassVar = ["id", "created_at", "updated_at"]


class BaseModelSerializer(TimestampedModelSerializer):
    """
    Serializer base completo com timestamp + soft delete

    Adiciona campos de auditoria e status
    """

    @extend_schema_field(serializers.DateTimeField())
    def get_deleted_at_formatted(self, obj):
        """Data de exclusão formatada"""
        if obj.deleted_at:
            return obj.deleted_at.strftime("%d/%m/%Y %H:%M:%S")
        return None

    class Meta:
        abstract = True
        fields: ClassVar = ["id", "created_at", "updated_at", "is_active", "deleted_at"]
        read_only_fields: ClassVar = ["id", "created_at", "updated_at", "deleted_at"]


class StatsSerializer(serializers.Serializer):
    """
    Serializer para estatísticas básicas
    """

    total = serializers.IntegerField(help_text="Total de registros")
    active = serializers.IntegerField(help_text="Registros ativos", required=False)
    inactive = serializers.IntegerField(help_text="Registros inativos", required=False)

    class Meta:
        fields: ClassVar = ["total", "active", "inactive"]


class ErrorSerializer(serializers.Serializer):
    """
    Serializer para respostas de erro padronizadas
    """

    error = serializers.BooleanField(
        default=True, help_text="Indica se é uma resposta de erro"
    )
    message = serializers.CharField(help_text="Mensagem de erro principal")
    details = serializers.DictField(
        help_text="Detalhes específicos do erro", required=False
    )
    status_code = serializers.IntegerField(help_text="Código de status HTTP")
    debug_info = serializers.DictField(help_text="Informações de debug", required=False)

    class Meta:
        fields: ClassVar = ["error", "message", "details", "status_code", "debug_info"]


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer para health check
    """

    status = serializers.CharField(help_text="Status do serviço")
    timestamp = serializers.DateTimeField(help_text="Timestamp da verificação")
    version = serializers.CharField(help_text="Versão da API")
    database = serializers.CharField(help_text="Status do banco de dados")
    cache = serializers.CharField(help_text="Status do cache")

    class Meta:
        fields: ClassVar = ["status", "timestamp", "version", "database", "cache"]
