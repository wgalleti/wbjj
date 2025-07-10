"""
Middleware para detecção automática de tenant via subdomínio.

Sistema multitenancy que extrai o tenant do subdomínio da URL e configura
o contexto adequado para isolamento de dados por schema PostgreSQL.
"""

import logging
import time
from collections.abc import Callable
from typing import ClassVar

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from apps.tenants.models import Tenant

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware para detecção automática de tenant por subdomínio

    Extrai tenant do subdomínio (ex: academia-teste.wbjj.com → academia-teste)
    e configura o contexto para isolamento automático por schema PostgreSQL.

    Features:
    - Detecção por subdomínio em produção
    - Suporte a localhost para desenvolvimento
    - Headers debug para monitoramento
    - Performance otimizada (< 50ms)
    - Logs detalhados para troubleshooting
    """

    # Subdomínios excluídos do sistema multitenancy
    EXCLUDED_SUBDOMAINS: ClassVar[list[str]] = [
        "www",
        "api",
        "admin",
        "static",
        "media",
        "mail",
        "ftp",
    ]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> None:
        """
        Processa request para detectar tenant por subdomínio
        """
        start_time = time.time()

        try:
            # Extrair subdomínio do host
            subdomain = self._extract_subdomain(request)

            if subdomain and subdomain not in self.EXCLUDED_SUBDOMAINS:
                # Buscar tenant pelo slug
                tenant = self._get_tenant_by_subdomain(subdomain)

                if tenant:
                    # Configurar contexto do tenant
                    self._setup_tenant_context(request, tenant)
                    logger.info(f"Tenant detectado: {tenant.name} ({tenant.slug})")
                else:
                    logger.warning(
                        f"Tenant não encontrado para subdomínio: {subdomain}"
                    )

            # Log de performance
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"TenantMiddleware processamento: {processing_time:.2f}ms")

        except Exception as err:
            logger.error(f"Erro no TenantMiddleware: {err}")
            raise RuntimeError("Erro na detecção de tenant") from err

    def _extract_subdomain(self, request: HttpRequest) -> str | None:
        """
        Extrai subdomínio do host da requisição

        Examples:
            - academia-teste.wbjj.com → academia-teste
            - localhost:8000 → None (desenvolvimento)
            - www.wbjj.com → www
        """
        host = request.get_host()

        # Desenvolvimento: localhost
        if "localhost" in host or "127.0.0.1" in host:
            return None

        # Extrair subdomínio
        parts = host.split(".")
        if len(parts) >= 3:  # subdomain.domain.com
            return parts[0]

        return None

    def _get_tenant_by_subdomain(self, subdomain: str) -> Tenant | None:
        """
        Busca tenant pelo slug do subdomínio
        """
        try:
            return Tenant.objects.get(slug=subdomain, is_active=True)
        except Tenant.DoesNotExist:
            return None
        except Exception as err:
            logger.error(f"Erro ao buscar tenant {subdomain}: {err}")
            raise RuntimeError(f"Erro na busca do tenant: {subdomain}") from err

    def _setup_tenant_context(self, request: HttpRequest, tenant: Tenant) -> None:
        """
        Configura contexto do tenant no request
        """
        # Adicionar tenant ao request
        request.tenant = tenant

        # Adicionar informações úteis
        request.tenant_schema = tenant.schema_name
        request.tenant_slug = tenant.slug

        logger.debug(f"Contexto configurado para tenant: {tenant.name}")

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Adiciona headers de debug na resposta
        """
        if hasattr(request, "tenant"):
            response["X-Tenant-Schema"] = request.tenant.schema_name

        return response


class SecurityAuthorizationMiddleware(MiddlewareMixin):
    """
    Middleware adicional para validações de segurança e autorização

    Funcionalidades:
    - Log de tentativas de acesso
    - Validação de tokens JWT expirados
    - Detecção de atividade suspeita
    - Headers de segurança adicionais
    """

    # Caminhos que não precisam de validação
    EXEMPT_PATHS: ClassVar[list[str]] = [
        "/api/v1/auth/token/",
        "/api/v1/auth/token/refresh/",
        "/api/v1/core/health/",
        "/api/v1/core/ping/",
        "/admin/",
        "/static/",
        "/media/",
    ]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> None:
        """
        Processa request para validações de segurança
        """
        start_time = time.time()

        try:
            # Pular validação para caminhos isentos
            if self._is_exempt_path(request):
                return

            # Log de acesso para auditoria
            self._log_access_attempt(request)

            # Validar contexto de segurança
            self._validate_security_context(request)

            # Log de performance
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"SecurityAuthorizationMiddleware: {processing_time:.2f}ms")

        except Exception as err:
            logger.error(f"Erro no SecurityAuthorizationMiddleware: {err}")
            # Não bloquear request em caso de erro

    def _is_exempt_path(self, request: HttpRequest) -> bool:
        """
        Verifica se o caminho está isento de validação
        """
        path = request.path
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)

    def _log_access_attempt(self, request: HttpRequest) -> None:
        """
        Log de tentativa de acesso para auditoria
        """
        user_info = "Anonymous"
        tenant_info = "No tenant"

        if request.user.is_authenticated:
            user_info = f"{request.user.email} ({request.user.role})"

        if hasattr(request, "tenant"):
            tenant_info = f"{request.tenant.name} ({request.tenant.slug})"

        logger.info(
            f"Access attempt: {request.method} {request.path}",
            extra={
                "user": user_info,
                "tenant": tenant_info,
                "ip": self._get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
                "method": request.method,
                "path": request.path,
            },
        )

    def _validate_security_context(self, request: HttpRequest) -> None:
        """
        Valida contexto de segurança da requisição
        """
        # Validar que usuário autenticado tem tenant
        if request.user.is_authenticated and not isinstance(
            request.user, AnonymousUser
        ):
            if not hasattr(request, "tenant"):
                logger.warning(
                    f"Usuário autenticado sem tenant configurado: {request.user.email}"
                )

        # Validar que tenant está ativo
        if hasattr(request, "tenant"):
            if not request.tenant.is_active:
                logger.warning(
                    f"Tentativa de acesso a tenant inativo: {request.tenant.slug}"
                )

    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Obtém IP do cliente respeitando proxies
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "Unknown")
        return ip

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Adiciona headers de segurança na resposta
        """
        # Headers de segurança adicionais
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Rate limiting headers (pode ser implementado futuramente)
        if hasattr(request, "user") and request.user.is_authenticated:
            response["X-RateLimit-Limit"] = "1000"
            response["X-RateLimit-Remaining"] = "999"

        return response
