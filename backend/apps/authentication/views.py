"""
Views para autenticação e gestão de usuários

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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from apps.core.viewsets import TenantViewSet

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar usuários", tags=["authentication"]),
    create=extend_schema(summary="Criar usuário", tags=["authentication"]),
    retrieve=extend_schema(summary="Obter usuário", tags=["authentication"]),
    update=extend_schema(summary="Atualizar usuário", tags=["authentication"]),
    partial_update=extend_schema(
        summary="Atualizar usuário parcialmente", tags=["authentication"]
    ),
    destroy=extend_schema(summary="Deletar usuário", tags=["authentication"]),
)
class UserViewSet(TenantViewSet):
    """
    ViewSet para gestão completa de usuários
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes: ClassVar = [IsAdminOrReadOnly]
    search_fields: ClassVar = ["first_name", "last_name", "email"]
    filterset_fields: ClassVar = ["role", "is_active", "is_verified"]
    ordering_fields: ClassVar = ["first_name", "last_name", "email", "created_at"]
    ordering: ClassVar = ["first_name", "last_name"]

    def get_serializer_class(self):
        """
        Retorna serializer apropriado baseado na ação
        """
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view requer
        """
        if self.action == "create":
            # Apenas admins podem criar usuários
            permission_classes: ClassVar = [
                permissions.IsAuthenticated,
                IsAdminOrReadOnly,
            ]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Admin ou próprio usuário
            permission_classes: ClassVar = [
                permissions.IsAuthenticated,
                IsOwnerOrReadOnly,
            ]
        else:
            # Ações de leitura para usuários autenticados
            permission_classes: ClassVar = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Obter perfil do usuário atual",
        description="Retorna informações do usuário logado",
        responses={200: UserSerializer},
        tags=["authentication"],
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Retorna informações do usuário logado
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Atualizar perfil do usuário atual",
        description="Atualiza informações do usuário logado",
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=["authentication"],
    )
    @action(detail=False, methods=["patch"])
    def update_profile(self, request):
        """
        Atualiza perfil do usuário logado
        """
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Retorna dados completos
        response_serializer = UserSerializer(request.user, context={"request": request})
        return Response(response_serializer.data)

    @extend_schema(
        summary="Alterar senha",
        description="Permite ao usuário alterar sua senha",
        request=PasswordChangeSerializer,
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}}
        },
        tags=["authentication"],
    )
    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """
        Permite ao usuário alterar sua senha
        """
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Alterar senha
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Senha alterada com sucesso"})

    @extend_schema(
        summary="Verificar email",
        description="Marca o email do usuário como verificado",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}}
        },
        tags=["authentication"],
    )
    @action(detail=True, methods=["post"])
    def verify_email(self, request, pk=None):
        """
        Marca email como verificado (apenas admin)
        """
        user = self.get_object()
        user.is_verified = True
        user.save()

        return Response({"message": "Email verificado com sucesso"})

    @extend_schema(
        summary="Ativar/Desativar usuário",
        description="Ativa ou desativa um usuário",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}}
        },
        tags=["authentication"],
    )
    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Ativa/desativa usuário (apenas admin)
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        status_msg = "ativado" if user.is_active else "desativado"
        return Response({"message": f"Usuário {status_msg} com sucesso"})


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para obter tokens JWT com informações extras
    """

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Login com JWT",
        description="Autentica usuário e retorna tokens JWT com informações do usuário",
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "email": {"type": "string"},
                            "full_name": {"type": "string"},
                            "role": {"type": "string"},
                            "is_verified": {"type": "boolean"},
                        },
                    },
                },
            }
        },
        tags=["authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    View customizada para refresh de tokens JWT
    """

    @extend_schema(
        summary="Refresh JWT",
        description="Gera novo access token usando refresh token",
        tags=["authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
