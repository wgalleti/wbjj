"""
Middleware customizado para aplicar políticas de permissão e cabeçalhos de segurança.
"""
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from apps.tenants.models import Tenant
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """Middleware MVP para detectar tenant via subdomínio"""

    def process_request(self, request):
        hostname = request.get_host().split(':')[0]
        subdomain = hostname.split('.')[0]

        # Pular para domínios principais
        main_domains = ['www', 'admin', 'api', 'localhost', '127']
        if subdomain in main_domains or subdomain.startswith('127'):
            request.tenant = None
            return None

        # Buscar tenant no cache
        cache_key = f"tenant:subdomain:{subdomain}"
        tenant = cache.get(cache_key)

        if tenant is None:
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                cache.set(cache_key, tenant, 3600)
            except Tenant.DoesNotExist:
                logger.warning(f"Tenant não encontrado: {subdomain}")
                raise Http404("Academia não encontrada")

        request.tenant = tenant
        request.tenant_id = tenant.id
        return None


class PermissionsPolicyMiddleware:
    """
    Middleware para aplicar cabeçalhos de Permissions Policy.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Adiciona cabeçalho de Permissions Policy para permitir eventos de unload
        response["Permissions-Policy"] = "unload=(self)"

        return response


class SecurityHeadersMiddleware:
    """
    Middleware para adicionar cabeçalhos de segurança extras.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Cabeçalhos de segurança adicionais
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["X-Content-Type-Options"] = "nosniff"

        # Remove o cabeçalho Server para não revelar informações do servidor
        if "Server" in response:
            del response["Server"]

        return response
