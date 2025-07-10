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


class TenantAdminPermission(permissions.BasePermission):
    """
    Permissão para admin do tenant atual

    Verifica se o usuário é admin E está no contexto do tenant correto
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Verificar se é admin
        if not hasattr(request.user, "role") or request.user.role != "admin":
            return False

        # Verificar contexto de tenant
        if not hasattr(request, "tenant"):
            logger.warning("Request sem tenant configurado para TenantAdminPermission")
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Para objetos específicos, confiamos no isolamento por schema
        return self.has_permission(request, view)


class TenantInstructorOrAdminPermission(permissions.BasePermission):
    """
    Permissão para instructor ou admin do tenant atual

    Combina validação de role com contexto de tenant
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Verificar se é instructor ou admin
        if not hasattr(request.user, "role"):
            return False

        if request.user.role not in ["instructor", "admin"]:
            return False

        # Verificar contexto de tenant
        if not hasattr(request, "tenant"):
            logger.warning(
                "Request sem tenant configurado para TenantInstructorOrAdminPermission"
            )
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class TenantUserPermission(permissions.BasePermission):
    """
    Permissão para usuários do tenant (qualquer role autenticada)

    Valida que o usuário pertence ao tenant atual
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Verificar contexto de tenant
        if not hasattr(request, "tenant"):
            logger.warning("Request sem tenant configurado para TenantUserPermission")
            return False

        # TODO: Implementar validação se usuário pertence ao tenant
        # Por agora, confiamos no isolamento por schema
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ReadOnlyForStudents(permissions.BasePermission):
    """
    Permissão que permite apenas leitura para estudantes

    Instrutores e admins têm acesso completo
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Métodos seguros são sempre permitidos para usuários autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # Métodos de escrita apenas para instructor ou admin
        return hasattr(request.user, "role") and request.user.role in [
            "instructor",
            "admin",
        ]

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CanManageFinances(permissions.BasePermission):
    """
    Permissão para gerenciar finanças (apenas admin)

    Mais específica que CanManagePayments, para operações financeiras sensíveis
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Apenas admin pode gerenciar finanças
        if not hasattr(request.user, "role") or request.user.role != "admin":
            return False

        # Verificar contexto de tenant
        if not hasattr(request, "tenant"):
            logger.warning("Request sem tenant configurado para CanManageFinances")
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CanManageGraduations(permissions.BasePermission):
    """
    Permissão para gerenciar graduações (instructor ou admin)

    Permite que instrutores gerenciem graduações de alunos
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return hasattr(request.user, "role") and request.user.role in [
            "instructor",
            "admin",
        ]

    def has_object_permission(self, request, view, obj):
        # Instrutores podem gerenciar graduações
        return self.has_permission(request, view)


class IsStudentOwnerOrInstructor(permissions.BasePermission):
    """
    Permissão que permite acesso ao próprio aluno OU a instrutores/admins

    Combina IsStudentOwner com permissões de instructor
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Instructor ou admin têm acesso total
        if hasattr(request.user, "role") and request.user.role in [
            "instructor",
            "admin",
        ]:
            return True

        # Estudante pode acessar apenas seus próprios dados
        if hasattr(obj, "student"):
            return obj.student.user == request.user

        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class DynamicPermission(permissions.BasePermission):
    """
    Permissão dinâmica baseada em configurações do tenant

    Permite configurar permissões específicas por tenant no futuro
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Por agora, funciona como TenantPermission
        if not hasattr(request, "tenant"):
            return False

        # TODO: Implementar configurações dinâmicas por tenant
        # Exemplo: request.tenant.permissions_config
        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
