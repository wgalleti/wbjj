"""
ViewSets base para o sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet (nunca ModelViewSet direto)
- SEMPRE documentar com drf-spectacular
- SEMPRE usar permissions granulares
- SEMPRE garantir isolamento de tenant
"""
from typing import ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .pagination import StandardResultsSetPagination
from .permissions import TenantPermission


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet base com isolamento de tenant

    Todos os ViewSets devem herdar desta classe para garantir:
    - Isolamento de dados por tenant
    - Paginação padronizada
    - Filtros e busca
    - Documentação automática
    - Permissões básicas
    """

    permission_classes: ClassVar = [TenantPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        """
        Filtra queryset por tenant

        Por enquanto retorna queryset base, mas será implementado
        isolamento de tenant no futuro
        """
        queryset = super().get_queryset()

        # TODO: Implementar filtro por tenant quando middleware estiver pronto
        # queryset = queryset.filter(tenant=self.request.tenant)

        # Aplicar filtro de registros ativos por padrão
        if hasattr(queryset.model, "is_active"):
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        """
        Customiza criação de objetos com tenant
        """
        # TODO: Adicionar tenant ao objeto criado
        # serializer.save(tenant=self.request.tenant)
        serializer.save()

    def perform_update(self, serializer):
        """
        Customiza atualização de objetos
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Implementa soft delete por padrão
        """
        if hasattr(instance, "delete") and hasattr(instance, "is_active"):
            # Soft delete
            instance.delete()
        else:
            # Hard delete para models sem soft delete
            instance.delete()

    @extend_schema(
        summary="Restaurar item deletado",
        description="Restaura um item que foi deletado com soft delete",
        responses={200: "Item restaurado com sucesso"},
    )
    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """
        Restaura item deletado (soft delete)
        """
        instance = self.get_object()

        if not hasattr(instance, "is_active"):
            return Response(
                {"error": "Este item não suporta restauração"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.is_active = True
        instance.deleted_at = None
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        summary="Obter estatísticas básicas",
        description="Retorna estatísticas básicas do recurso",
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Retorna estatísticas básicas do modelo
        """
        queryset = self.get_queryset()

        total = queryset.count()

        # Estatísticas específicas por tipo de modelo
        stats_data = {"total": total}

        # Se o modelo tem campo is_active, contar ativos/inativos
        if hasattr(queryset.model, "is_active"):
            stats_data.update(
                {
                    "active": queryset.filter(is_active=True).count(),
                    "inactive": queryset.filter(is_active=False).count(),
                }
            )

        return Response(stats_data)


class ReadOnlyTenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet base somente leitura com isolamento de tenant

    Para recursos que não precisam de operações de escrita
    """

    permission_classes: ClassVar = [TenantPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        """
        Filtra queryset por tenant (somente leitura)
        """
        queryset = super().get_queryset()

        # TODO: Implementar filtro por tenant quando middleware estiver pronto
        # queryset = queryset.filter(tenant=self.request.tenant)

        # Aplicar filtro de registros ativos por padrão
        if hasattr(queryset.model, "is_active"):
            queryset = queryset.filter(is_active=True)

        return queryset
