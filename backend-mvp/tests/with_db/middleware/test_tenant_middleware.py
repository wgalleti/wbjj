"""
Testes para TenantMiddleware
Foco: Isolamento de tenant, detecção de subdomain, segurança
Objetivo: 90% coverage seguindo CONTEXT.md
"""

from unittest.mock import Mock, patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from apps.authentication.middleware import TenantMiddleware
from tests.with_db.factories import TenantFactory


class TestTenantMiddleware:
    """Testes para TenantMiddleware"""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance"""
        get_response = Mock()
        return TenantMiddleware(get_response)

    @pytest.fixture
    def request_factory(self):
        """Request factory for middleware tests"""
        return RequestFactory()

    @pytest.fixture
    def test_tenant(self, db):
        """Create test tenant for middleware"""
        return TenantFactory(
            name="Test Academy",
            slug="test-academy",
            schema_name="test_middleware",
            domain_url="test-academy.wbjj.com",
        )

    def test_extract_subdomain_production(self, middleware, request_factory):
        """Test subdomain extraction in production"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "test-academy.wbjj.com"

        with patch.object(request, "get_host", return_value="test-academy.wbjj.com"):
            subdomain = middleware._extract_subdomain(request)
            assert subdomain == "test-academy"

    def test_extract_subdomain_localhost(self, middleware, request_factory):
        """Test subdomain extraction on localhost"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "localhost:8000"

        with patch.object(request, "get_host", return_value="localhost:8000"):
            subdomain = middleware._extract_subdomain(request)
            assert subdomain is None

    def test_extract_subdomain_www(self, middleware, request_factory):
        """Test subdomain extraction with www"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "www.wbjj.com"

        with patch.object(request, "get_host", return_value="www.wbjj.com"):
            subdomain = middleware._extract_subdomain(request)
            assert subdomain == "www"

    def test_process_request_success(self, middleware, request_factory, test_tenant):
        """Test successful request processing"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "test-academy.wbjj.com"

        with patch.object(request, "get_host", return_value="test-academy.wbjj.com"):
            result = middleware.process_request(request)

            assert result is None  # Continue processing
            assert hasattr(request, "tenant")
            assert request.tenant.slug == "test-academy"
            assert request.tenant_schema == "test_middleware"

    @pytest.mark.django_db
    def test_process_request_tenant_not_found(self, middleware, request_factory):
        """Test request processing when tenant not found"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "nonexistent.wbjj.com"

        with patch.object(request, "get_host", return_value="nonexistent.wbjj.com"):
            result = middleware.process_request(request)

            assert result is None  # Continue processing
            assert not hasattr(request, "tenant")

    def test_process_request_no_subdomain(self, middleware, request_factory):
        """Test request processing without subdomain"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "localhost:8000"

        with patch.object(request, "get_host", return_value="localhost:8000"):
            result = middleware.process_request(request)

            assert result is None
            assert not hasattr(request, "tenant")

    def test_process_response_with_tenant(
        self, middleware, request_factory, test_tenant
    ):
        """Test response processing with tenant"""
        request = request_factory.get("/")
        request.tenant = test_tenant
        request.tenant_schema = "test_middleware"

        response = HttpResponse()
        result = middleware.process_response(request, response)

        assert result["X-Tenant-Schema"] == "test_middleware"

    def test_process_response_without_tenant(self, middleware, request_factory):
        """Test response processing without tenant"""
        request = request_factory.get("/")
        response = HttpResponse()

        result = middleware.process_response(request, response)

        assert "X-Tenant-Schema" not in result

    def test_middleware_security_isolation(self, middleware, request_factory, db):
        """Test middleware ensures tenant isolation"""
        # Create two tenants
        TenantFactory(
            slug="academy-one",
            schema_name="academy_one",
            domain_url="academy-one.wbjj.com",
        )
        TenantFactory(
            slug="academy-two",
            schema_name="academy_two",
            domain_url="academy-two.wbjj.com",
        )

        # Request for tenant1
        request1 = request_factory.get("/")
        request1.META["HTTP_HOST"] = "academy-one.wbjj.com"

        with patch.object(request1, "get_host", return_value="academy-one.wbjj.com"):
            middleware.process_request(request1)
            assert request1.tenant.slug == "academy-one"

        # Request for tenant2
        request2 = request_factory.get("/")
        request2.META["HTTP_HOST"] = "academy-two.wbjj.com"

        with patch.object(request2, "get_host", return_value="academy-two.wbjj.com"):
            middleware.process_request(request2)
            assert request2.tenant.slug == "academy-two"

        # Verify isolation
        assert request1.tenant != request2.tenant

    @pytest.mark.django_db
    def test_middleware_error_handling(self, middleware, request_factory):
        """Test middleware error handling"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "malformed..domain.com"

        # Should handle malformed domains gracefully
        with patch.object(request, "get_host", return_value="malformed..domain.com"):
            result = middleware.process_request(request)
            assert result is None  # Should continue processing
            assert not hasattr(request, "tenant")

    def test_middleware_performance(self, middleware, request_factory, test_tenant):
        """Test middleware performance characteristics"""
        request = request_factory.get("/")
        request.META["HTTP_HOST"] = "test-academy.wbjj.com"

        import time

        with patch.object(request, "get_host", return_value="test-academy.wbjj.com"):
            start_time = time.time()
            middleware.process_request(request)
            end_time = time.time()

            # Middleware should be fast (< 10ms)
            processing_time = (end_time - start_time) * 1000
            assert processing_time < 10  # Less than 10ms
