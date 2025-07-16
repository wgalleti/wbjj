"""
Testes para tratamento de exceções customizadas do Core
Foco: Exception handlers, logs estruturados, exceções customizadas
Objetivo: 100% de cobertura para core/exceptions.py
"""

from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from apps.core.exceptions import (
    BusinessLogicError,
    PermissionError,
    TenantError,
    custom_exception_handler,
    get_error_message,
    handle_generic_error,
    log_error,
)
from tests.base import BaseModelTestCase
from tests.with_db.factories import UserFactory

User = get_user_model()


class TestCustomExceptionHandler(BaseModelTestCase):
    """Testes para custom_exception_handler - handler principal de exceções"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    @patch("apps.core.exceptions.exception_handler")
    @patch("apps.core.exceptions.log_error")
    def test_exception_handler_with_drf_response(
        self, mock_log_error, mock_drf_handler
    ):
        """Teste quando DRF já tratou a exceção"""
        # Mock DRF handler retorna uma resposta
        mock_response = Response({"detail": "Error"}, status=400)
        mock_drf_handler.return_value = mock_response

        request = self.factory.get("/")
        request.user = UserFactory()
        context = {"request": request}

        exc = DRFValidationError("Test error")
        result = custom_exception_handler(exc, context)

        # Verifica estrutura da resposta customizada
        self.assertEqual(result.status_code, 400)
        self.assertTrue(result.data["error"])
        self.assertIn("message", result.data)
        self.assertIn("details", result.data)
        self.assertIn("status_code", result.data)
        self.assertIn("debug_info", result.data)

        # Verifica debug info
        debug_info = result.data["debug_info"]
        self.assertEqual(debug_info["path"], "/")
        self.assertEqual(debug_info["method"], "GET")
        self.assertIn("user", debug_info)

        # Verifica que log foi chamado
        mock_log_error.assert_called_once()

    @patch("apps.core.exceptions.exception_handler")
    @patch("apps.core.exceptions.handle_generic_error")
    @patch("apps.core.exceptions.log_error")
    def test_exception_handler_without_drf_response(
        self, mock_log_error, mock_handle_generic, mock_drf_handler
    ):
        """Teste quando DRF não tratou a exceção"""
        # Mock DRF handler retorna None
        mock_drf_handler.return_value = None

        # Mock handle_generic_error retorna uma resposta
        mock_response = Response({"error": True}, status=500)
        mock_handle_generic.return_value = mock_response

        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False
        context = {"request": request}

        exc = Exception("Generic error")
        result = custom_exception_handler(exc, context)

        # Verifica que handle_generic_error foi chamado
        mock_handle_generic.assert_called_once_with(exc, context)

        # Verifica estrutura da resposta
        self.assertIsNotNone(result)
        self.assertTrue(result.data["error"])

        # Verifica debug info para usuário anônimo
        debug_info = result.data["debug_info"]
        self.assertEqual(debug_info["user"], "Anonymous")

    @patch("apps.core.exceptions.exception_handler")
    def test_exception_handler_no_request_in_context(self, mock_drf_handler):
        """Teste quando não há request no context"""
        mock_response = Response({"detail": "Error"}, status=400)
        mock_drf_handler.return_value = mock_response

        context = {}  # Sem request
        exc = DRFValidationError("Test error")

        result = custom_exception_handler(exc, context)

        # Verifica que não adiciona debug_info se não há request
        self.assertNotIn("debug_info", result.data)


class TestHandleGenericError(BaseModelTestCase):
    """Testes para handle_generic_error - tratamento de erros não capturados pelo DRF"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    def test_handle_http404(self):
        """Teste tratamento de Http404"""
        exc = Http404("Page not found")
        context = {"request": self.factory.get("/")}

        response = handle_generic_error(exc, context)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["error"])
        self.assertEqual(response.data["message"], "Recurso não encontrado")
        self.assertEqual(response.data["details"]["code"], "not_found")

    def test_handle_validation_error_with_message_dict(self):
        """Teste tratamento de ValidationError com message_dict"""
        exc = ValidationError(
            {"field1": ["Error message 1"], "field2": ["Error message 2"]}
        )
        context = {"request": self.factory.get("/")}

        response = handle_generic_error(exc, context)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data["error"])
        self.assertEqual(response.data["message"], "Erro de validação")
        self.assertIn("validation_errors", response.data["details"])
        self.assertEqual(
            response.data["details"]["validation_errors"], exc.message_dict
        )

    def test_handle_validation_error_without_message_dict(self):
        """Teste tratamento de ValidationError sem message_dict"""
        exc = ValidationError("Simple error message")
        context = {"request": self.factory.get("/")}

        response = handle_generic_error(exc, context)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data["error"])
        self.assertEqual(response.data["message"], "Erro de validação")
        self.assertEqual(response.data["details"]["validation_errors"], str(exc))

    def test_handle_generic_exception(self):
        """Teste tratamento de exceção genérica"""
        exc = Exception("Generic error")
        context = {"request": self.factory.get("/")}

        response = handle_generic_error(exc, context)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertTrue(response.data["error"])
        self.assertEqual(response.data["message"], "Erro interno do servidor")
        self.assertEqual(response.data["details"]["code"], "internal_server_error")


class TestGetErrorMessage(BaseModelTestCase):
    """Testes para get_error_message - extração de mensagens amigáveis"""

    model_class = User

    def test_get_error_message_with_dict_detail(self):
        """Teste extração de mensagem de exceção com detail dict"""
        exc = Mock()
        exc.detail = {"field1": ["First error"], "field2": ["Second error"]}
        response = Mock()

        message = get_error_message(exc, response)

        self.assertEqual(message, "First error")

    def test_get_error_message_with_list_detail(self):
        """Teste extração de mensagem de exceção com detail list"""
        exc = Mock()
        exc.detail = ["First error", "Second error"]
        response = Mock()

        message = get_error_message(exc, response)

        self.assertEqual(message, "First error")

    def test_get_error_message_with_string_detail(self):
        """Teste extração de mensagem de exceção com detail string"""
        exc = Mock()
        exc.detail = "Simple error message"
        response = Mock()

        message = get_error_message(exc, response)

        self.assertEqual(message, "Simple error message")

    def test_get_error_message_without_detail(self):
        """Teste extração de mensagem de exceção sem detail"""
        exc = Exception("Generic exception")
        response = Mock()

        message = get_error_message(exc, response)

        self.assertEqual(message, "Generic exception")

    def test_get_error_message_nested_list_in_dict(self):
        """Teste extração com lista aninhada em dict"""
        exc = Mock()
        exc.detail = {"field": "Simple string"}  # String em vez de lista
        response = Mock()

        message = get_error_message(exc, response)

        self.assertEqual(message, "Simple string")


class TestLogError(BaseModelTestCase):
    """Testes para log_error - log estruturado de erros"""

    model_class = User

    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    @patch("apps.core.exceptions.logger")
    def test_log_error_server_error(self, mock_logger):
        """Teste log de erro do servidor (500+)"""
        user = UserFactory()
        request = self.factory.get("/test/")
        request.user = user
        request.tenant_id = "test_tenant"

        exc = Exception("Server error")
        response = Mock()
        response.status_code = 500
        context = {"request": request}

        log_error(exc, context, response)

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        self.assertIn("Server error", str(call_args[0][0]))

        # Verifica extra data
        extra_data = call_args[1]["extra"]
        self.assertEqual(extra_data["error_type"], "Exception")
        self.assertEqual(extra_data["status_code"], 500)
        self.assertEqual(extra_data["path"], "/test/")
        self.assertEqual(extra_data["method"], "GET")
        self.assertEqual(extra_data["user_id"], str(user.id))
        self.assertEqual(extra_data["tenant_id"], "test_tenant")

    @patch("apps.core.exceptions.logger")
    def test_log_error_client_error(self, mock_logger):
        """Teste log de erro do cliente (400-499)"""
        request = self.factory.post("/test/")
        request.user = Mock()
        request.user.is_authenticated = False

        exc = ValidationError("Validation error")
        response = Mock()
        response.status_code = 400
        context = {"request": request}

        log_error(exc, context, response)

        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args

        # Verifica extra data para usuário não autenticado
        extra_data = call_args[1]["extra"]
        self.assertIsNone(extra_data["user_id"])

    @patch("apps.core.exceptions.logger")
    def test_log_error_info_level(self, mock_logger):
        """Teste log de nível info (< 400)"""
        request = self.factory.get("/test/")
        request.user = UserFactory()

        exc = Exception("Info error")
        response = Mock()
        response.status_code = 200
        context = {"request": request}

        log_error(exc, context, response)

        mock_logger.info.assert_called_once()

    @patch("apps.core.exceptions.logger")
    def test_log_error_no_request(self, mock_logger):
        """Teste log sem request no context"""
        exc = Exception("No request error")
        response = Mock()
        response.status_code = 500
        context = {}  # Sem request

        log_error(exc, context, response)

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args

        # Verifica valores padrão quando não há request
        extra_data = call_args[1]["extra"]
        self.assertEqual(extra_data["path"], "unknown")
        self.assertEqual(extra_data["method"], "unknown")
        self.assertIsNone(extra_data["user_id"])
        self.assertIsNone(extra_data["tenant_id"])


class TestBusinessLogicError(BaseModelTestCase):
    """Testes para BusinessLogicError - exceção de regra de negócio"""

    model_class = User

    def test_business_logic_error_with_all_params(self):
        """Teste BusinessLogicError com todos os parâmetros"""
        message = "Business rule violated"
        code = "invalid_operation"
        details = {"field": "value", "reason": "constraint"}

        error = BusinessLogicError(message, code, details)

        self.assertEqual(error.message, message)
        self.assertEqual(error.code, code)
        self.assertEqual(error.details, details)
        self.assertEqual(str(error), message)

    def test_business_logic_error_with_defaults(self):
        """Teste BusinessLogicError com valores padrão"""
        message = "Business rule violated"

        error = BusinessLogicError(message)

        self.assertEqual(error.message, message)
        self.assertEqual(error.code, "business_logic_error")
        self.assertEqual(error.details, {})
        self.assertEqual(str(error), message)


class TestTenantError(BaseModelTestCase):
    """Testes para TenantError - exceção de tenant"""

    model_class = User

    def test_tenant_error_with_code(self):
        """Teste TenantError com código customizado"""
        message = "Tenant not found"
        code = "tenant_not_found"

        error = TenantError(message, code)

        self.assertEqual(error.message, message)
        self.assertEqual(error.code, code)
        self.assertEqual(str(error), message)

    def test_tenant_error_with_default_code(self):
        """Teste TenantError com código padrão"""
        message = "Tenant error occurred"

        error = TenantError(message)

        self.assertEqual(error.message, message)
        self.assertEqual(error.code, "tenant_error")
        self.assertEqual(str(error), message)


class TestPermissionError(BaseModelTestCase):
    """Testes para PermissionError - exceção de permissão"""

    model_class = User

    def test_permission_error_with_code(self):
        """Teste PermissionError com código customizado"""
        message = "Access denied"
        code = "access_denied"

        error = PermissionError(message, code)

        self.assertEqual(error.message, message)
        self.assertEqual(error.code, code)
        self.assertEqual(str(error), message)

    def test_permission_error_with_default_code(self):
        """Teste PermissionError com código padrão"""
        message = "Permission denied"

        error = PermissionError(message)

        self.assertEqual(error.message, message)
        self.assertEqual(error.code, "permission_error")
        self.assertEqual(str(error), message)
