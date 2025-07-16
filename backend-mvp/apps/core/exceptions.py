"""
Exception handler personalizado para o sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- Tratamento de erros padronizado
- Logs estruturados
- Respostas consistentes para frontend
"""
import logging

from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Exception handler personalizado para APIs

    Padroniza respostas de erro e adiciona logs estruturados
    """
    # Chama o handler padrão do DRF primeiro
    response = exception_handler(exc, context)

    # Se o DRF não tratou a exceção, tratamos aqui
    if response is None:
        response = handle_generic_error(exc, context)

    # Adiciona informações extras para debug
    if response is not None:
        custom_response_data = {
            "error": True,
            "message": get_error_message(exc, response),
            "details": response.data if hasattr(response, "data") else None,
            "status_code": response.status_code,
        }

        # Em desenvolvimento, adicionar mais detalhes
        if hasattr(context.get("request"), "user"):
            request = context["request"]
            custom_response_data["debug_info"] = {
                "path": request.path,
                "method": request.method,
                "user": str(request.user)
                if request.user.is_authenticated
                else "Anonymous",
            }

        response.data = custom_response_data

        # Log estruturado do erro
        log_error(exc, context, response)

    return response


def handle_generic_error(exc, context):
    """
    Trata erros não capturados pelo DRF
    """
    if isinstance(exc, Http404):
        return Response(
            {
                "error": True,
                "message": "Recurso não encontrado",
                "details": {"code": "not_found"},
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, ValidationError):
        return Response(
            {
                "error": True,
                "message": "Erro de validação",
                "details": {
                    "validation_errors": exc.message_dict
                    if hasattr(exc, "message_dict")
                    else str(exc)
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Erro genérico
    return Response(
        {
            "error": True,
            "message": "Erro interno do servidor",
            "details": {"code": "internal_server_error"},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def get_error_message(exc, response):
    """
    Extrai mensagem de erro amigável
    """
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, dict):
            # Pega a primeira mensagem de erro
            first_key = next(iter(exc.detail))
            first_error = exc.detail[first_key]
            if isinstance(first_error, list):
                return str(first_error[0])
            return str(first_error)
        elif isinstance(exc.detail, list):
            return str(exc.detail[0])
        return str(exc.detail)

    return str(exc)


def log_error(exc, context, response):
    """
    Log estruturado de erros
    """
    request = context.get("request")

    log_data = {
        "error_type": type(exc).__name__,
        "status_code": response.status_code,
        "path": request.path if request else "unknown",
        "method": request.method if request else "unknown",
        "user_id": str(request.user.id)
        if request and request.user.is_authenticated
        else None,
        "tenant_id": getattr(request, "tenant_id", None) if request else None,
    }

    # Log com nível apropriado
    if response.status_code >= 500:
        logger.error(f"Server error: {exc}", extra=log_data)
    elif response.status_code >= 400:
        logger.warning(f"Client error: {exc}", extra=log_data)
    else:
        logger.info(f"Request error: {exc}", extra=log_data)


class BusinessLogicError(Exception):
    """
    Exceção para erros de regra de negócio
    """

    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code or "business_logic_error"
        self.details = details or {}
        super().__init__(self.message)


class TenantError(Exception):
    """
    Exceção para erros relacionados a tenant
    """

    def __init__(self, message, code=None):
        self.message = message
        self.code = code or "tenant_error"
        super().__init__(self.message)


class PermissionError(Exception):
    """
    Exceção para erros de permissão
    """

    def __init__(self, message, code=None):
        self.message = message
        self.code = code or "permission_error"
        super().__init__(self.message)
