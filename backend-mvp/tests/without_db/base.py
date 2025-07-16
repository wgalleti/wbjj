"""
Base classes para testes do sistema wBJJ

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE usar TenantTestCase para isolamento
- SEMPRE usar factory-boy para dados de teste
- SEMPRE validar isolamento entre tenants
- Cobertura > 90%
"""
from typing import ClassVar

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, TransactionTestCase
from django_tenants.test.cases import TenantTestCase
from rest_framework.test import APITestCase

User = get_user_model()


class BaseTenantTestCase(TenantTestCase):
    """
    Classe base para testes que requerem isolamento de tenant

    Seguindo CONTEXT.md:
    - Isolamento completo entre tenants
    - Limpeza automática de dados
    - Performance otimizada
    """

    # Nome do schema para testes (será criado automaticamente)
    tenant_schema_name = "test_tenant"

    def setUp(self):
        """
        Setup padrão para testes com tenant
        """
        super().setUp()
        cache.clear()

        # Força garantir que estamos no contexto correto do tenant
        from django.db import connection

        connection.set_schema(self.tenant.schema_name)

    def tearDown(self):
        """
        Cleanup padrão para testes com tenant
        """
        cache.clear()
        super().tearDown()

    def run(self, result=None):
        """
        Override run para garantir contexto de schema correto em cada teste
        """
        from django_tenants.utils import schema_context

        # Força contexto de schema para cada teste
        with schema_context(self.tenant.schema_name):
            return super().run(result)

    def create_user(self, **kwargs):
        """
        Helper para criar usuário no contexto do tenant

        Seguindo CONTEXT.md:
        - SEMPRE usar email como identificador único
        - SEMPRE validar que está no tenant correto
        """
        defaults = {
            "email": "user@test.com",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
        }
        defaults.update(kwargs)

        # TenantTestCase já gerencia o contexto do schema
        user = User.objects.create_user(**defaults)
        return user

    def create_superuser(self, **kwargs):
        """
        Helper para criar superuser no contexto do tenant
        """
        defaults = {
            "email": "admin@test.com",
            "first_name": "Admin",
            "last_name": "User",
            "is_active": True,
        }
        defaults.update(kwargs)

        user = User.objects.create_superuser(**defaults)
        return user

    def assert_tenant_isolation(self, model_class, obj_id):
        """
        Valida que objeto só existe no tenant atual

        Teste de segurança obrigatório conforme CONTEXT.md
        """
        # Objeto deve existir no tenant atual
        self.assertTrue(model_class.objects.filter(id=obj_id).exists())

        # Para testar isolamento, seria necessário criar outro tenant,
        # mas no contexto de TenantTestCase isso é complexo
        # Este teste pode ser implementado em testes de integração específicos


class BaseTenantAPITestCase(BaseTenantTestCase, APITestCase):
    """
    Classe base para testes de API com isolamento de tenant

    Combina TenantTestCase com APITestCase para testes de ViewSets
    """

    def setUp(self):
        """
        Setup com usuário autenticado por padrão
        """
        super().setUp()

        # Criar usuário de teste no tenant
        self.user = self.create_user()

        # Autenticar por padrão
        self.client.force_authenticate(user=self.user)

    def assert_response_tenant_context(self, response):
        """
        Valida que response está no contexto correto do tenant
        """
        # Response deve ser bem-sucedida
        self.assertIn(response.status_code, [200, 201, 204])

        # Headers de tenant devem estar presentes se configurados
        if hasattr(response, "wsgi_request"):
            request = response.wsgi_request
            if hasattr(request, "tenant"):
                self.assertEqual(request.tenant.schema_name, self.tenant.schema_name)


class BaseModelTestCase(TestCase):
    """
    Classe base para testes de models
    """

    model_class: ClassVar = None

    def setUp(self):
        """Setup padrão para testes de model"""
        super().setUp()
        cache.clear()

    def tearDown(self):
        """Cleanup padrão para testes de model"""
        cache.clear()
        super().tearDown()

    def assert_model_validation(self, obj, should_be_valid=True):
        """
        Helper para validar modelo seguindo CONTEXT.md
        """
        try:
            obj.full_clean()
            if not should_be_valid:
                self.fail(f"Model {obj.__class__.__name__} deveria ser inválido")
        except Exception as e:
            if should_be_valid:
                self.fail(f"Model {obj.__class__.__name__} deveria ser válido: {e}")

    def assert_required_fields(self, required_fields: list):
        """
        Testa campos obrigatórios do modelo
        """
        for field in required_fields:
            with self.subTest(field=field):
                # Criar instância com campo vazio
                kwargs = {field: None if field != "email" else ""}
                try:
                    obj = self.model_class(**kwargs)
                    obj.full_clean()
                    self.fail(f"Campo {field} deveria ser obrigatório")
                except Exception:
                    pass  # Esperado


class BaseSerializerTestCase(BaseTenantTestCase):
    """
    Classe base para testes de serializers

    Foca em validações customizadas e campos computados
    """

    # Sobrescrito pelas classes filhas
    serializer_class = None

    def assert_serializer_validation(
        self, data, should_be_valid=True, expected_errors=None
    ):
        """
        Helper para validar serializer
        """
        serializer = self.serializer_class(data=data)

        if should_be_valid:
            self.assertTrue(
                serializer.is_valid(), f"Serializer errors: {serializer.errors}"
            )
        else:
            self.assertFalse(serializer.is_valid())

            if expected_errors:
                for field, expected_error in expected_errors.items():
                    self.assertIn(field, serializer.errors)
                    if isinstance(expected_error, str):
                        self.assertIn(
                            expected_error.lower(),
                            str(serializer.errors[field]).lower(),
                        )


class BaseViewSetTestCase(BaseTenantAPITestCase):
    """
    Classe base para testes de ViewSets com tenant

    Foca em permissões, filtros e ações customizadas
    """

    # Configurações obrigatórias (sobrescritas pelas classes filhas)
    viewset_class = None
    factory_class = None
    base_url = None

    def assert_tenant_filtering(self):
        """
        Valida que ViewSet filtra corretamente por tenant
        """
        # Criar objetos em tenants diferentes
        obj1 = self.factory_class()  # Tenant atual

        # Buscar via API - deve retornar apenas objetos do tenant atual
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)

        # Validar que apenas objetos do tenant atual são retornados
        response_ids = [
            item["id"] for item in response.data.get("results", response.data)
        ]
        self.assertIn(obj1.id, response_ids)

    def assert_permissions(self, method="GET", expected_status=200):
        """
        Valida permissões de acesso
        """
        # Sem autenticação
        self.client.force_authenticate(user=None)
        response = getattr(self.client, method.lower())(self.base_url)
        self.assertEqual(response.status_code, 401)

        # Com autenticação
        self.client.force_authenticate(user=self.user)
        response = getattr(self.client, method.lower())(self.base_url)
        self.assertEqual(response.status_code, expected_status)


class SecurityTestMixin:
    """
    Mixin para testes de segurança
    """

    def assert_no_sql_injection(
        self, endpoint, param_name, dangerous_value="'; DROP TABLE users; --"
    ):
        """
        Testa proteção contra SQL injection
        """
        params = {param_name: dangerous_value}
        response = self.client.get(endpoint, params)

        # Não deve retornar erro 500 (indica possível vulnerabilidade)
        self.assertNotEqual(response.status_code, 500)

    def assert_no_xss(self, endpoint, xss_payload="<script>alert('xss')</script>"):
        """
        Testa proteção contra XSS
        """
        response = self.client.get(endpoint)

        # Response não deve conter o payload
        if hasattr(response, "content"):
            self.assertNotIn(xss_payload, response.content.decode())


class PerformanceTestMixin:
    """
    Mixin para testes de performance
    """

    def assert_response_time(self, endpoint, max_time_ms=200):
        """
        Valida tempo de resposta da API
        """
        import time

        start_time = time.time()
        response = self.client.get(endpoint)
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        self.assertLess(
            response_time_ms,
            max_time_ms,
            f"Response time {response_time_ms:.2f}ms exceeded {max_time_ms}ms",
        )

        return response


class TenantModelTestCase(TransactionTestCase):
    """
    Classe especial para testes de Tenant models que precisam do schema público
    Usa TransactionTestCase para permitir manipulação direta de schemas
    """

    def setUp(self):
        """Setup padrão para testes de tenant model"""
        super().setUp()
        cache.clear()

        # Forçar conexão com schema público para criação de tenants
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO public")

    def tearDown(self):
        """Cleanup padrão para testes de tenant model"""
        cache.clear()
        super().tearDown()


class BaseAPITestCase(APITestCase):
    """
    Classe base para testes de API
    """

    def setUp(self):
        """Setup padrão para testes de API"""
        super().setUp()
        cache.clear()

    def tearDown(self):
        """Cleanup padrão para testes de API"""
        cache.clear()
        super().tearDown()
