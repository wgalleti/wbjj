"""
Views para gestão de academias (tenants)

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet
- SEMPRE documentar com drf-spectacular
- SEMPRE usar permissions granulares
"""
from typing import ClassVar

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly
from apps.core.viewsets import TenantViewSet

from .models import Tenant
from .serializers import (
    TenantCreateSerializer,
    TenantPublicSerializer,
    TenantSerializer,
    TenantUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar academias", tags=["tenants"]),
    create=extend_schema(summary="Criar academia", tags=["tenants"]),
    retrieve=extend_schema(summary="Obter academia", tags=["tenants"]),
    update=extend_schema(summary="Atualizar academia", tags=["tenants"]),
    partial_update=extend_schema(
        summary="Atualizar academia parcialmente", tags=["tenants"]
    ),
    destroy=extend_schema(summary="Deletar academia", tags=["tenants"]),
)
class TenantViewSet(TenantViewSet):
    """ViewSet para gestão de academias"""

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes: ClassVar = [IsAdminOrReadOnly]
    search_fields: ClassVar = ["name", "email", "city", "state"]
    filterset_fields: ClassVar = ["city", "state", "country", "is_active"]
    ordering_fields: ClassVar = ["name", "founded_date", "created_at"]
    ordering: ClassVar = ["name"]

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na ação"""
        if self.action == "create":
            return TenantCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TenantUpdateSerializer
        elif self.action == "public":
            return TenantPublicSerializer
        return TenantSerializer

    @extend_schema(
        summary="Informações públicas da academia",
        description="Retorna informações básicas para landing pages",
        responses={200: TenantPublicSerializer},
        tags=["tenants"],
    )
    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def public(self, request, pk=None):
        """Informações públicas da academia"""
        tenant = self.get_object()
        serializer = TenantPublicSerializer(tenant, context={"request": request})
        return Response(serializer.data)
