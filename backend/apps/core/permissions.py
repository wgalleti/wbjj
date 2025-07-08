"""
Permissões customizadas para o sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- Sempre validar tenant no middleware
- Isolamento total entre tenants
- Permissões granulares
"""
from rest_framework import permissions


class TenantPermission(permissions.BasePermission):
    """
    Permissão base para garantir isolamento de tenant

    Valida que o usuário só pode acessar dados do seu tenant
    """

    def has_permission(self, request, view):
        """
        Verifica se o usuário tem permissão para acessar a view
        """
        # Usuário deve estar autenticado
        if not request.user.is_authenticated:
            return False

        # TODO: Implementar validação de tenant quando o middleware estiver pronto
        # Por enquanto, permite acesso para usuários autenticados
        return True

    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário pode acessar o objeto específico
        """
        # TODO: Implementar validação de tenant no objeto
        # Por enquanto, permite acesso para usuários autenticados
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
