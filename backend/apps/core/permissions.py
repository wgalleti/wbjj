"""
Permissões customizadas para o sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- Sempre validar tenant no middleware
- Isolamento total entre tenants
- Permissões granulares
"""
import logging

from rest_framework import permissions

logger = logging.getLogger(__name__)


class TenantPermission(permissions.BasePermission):
    """
    Permissão base para garantir isolamento de tenant

    Com django-tenant-schemas, o isolamento é automático via schema.
    Esta permissão garante que o usuário está autenticado e tem
    acesso ao tenant configurado pelo middleware.
    """

    def has_permission(self, request, view):
        """
        Verifica se o usuário tem permissão para acessar a view
        """
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False

        # Verificar se o middleware configurou o tenant
        if not hasattr(request, "tenant"):
            logger.warning("Request sem tenant configurado - middleware não funcionou")
            return False

        # Com schema isolation, se chegou até aqui, o acesso é válido
        return True

    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário pode acessar o objeto específico

        Com schema-per-tenant, se o objeto existe no schema atual,
        o usuário automaticamente tem acesso a ele.
        """
        # Com isolamento por schema, todos os objetos no schema atual
        # são acessíveis pelo usuário do tenant
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada para permitir apenas que proprietários do objeto possam editá-lo
    """

    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissões de escrita apenas para o proprietário do objeto
        return obj.user == request.user


class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Permissão para instrutor ou admin
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return hasattr(request.user, "role") and request.user.role in [
            "instructor",
            "admin",
        ]


class IsStudentOwner(permissions.BasePermission):
    """
    Permissão para aluno acessar apenas seus próprios dados
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Se o objeto tem relação com student, verificar se é o próprio usuário
        if hasattr(obj, "student"):
            return obj.student.user == request.user

        # Se o objeto é um Student, verificar se é o próprio usuário
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão para admin ou apenas leitura
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return hasattr(request.user, "role") and request.user.role == "admin"


class CanManageStudents(permissions.BasePermission):
    """
    Permissão para gerenciar alunos (admin ou instructor)
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return hasattr(request.user, "role") and request.user.role in [
            "admin",
            "instructor",
        ]


class CanManagePayments(permissions.BasePermission):
    """
    Permissão para gerenciar pagamentos (apenas admin)
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return hasattr(request.user, "role") and request.user.role == "admin"
