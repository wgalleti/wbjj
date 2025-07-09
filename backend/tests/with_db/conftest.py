"""
Configuração central do pytest para todos os apps
Foco em produtividade, cobertura real e qualidade
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.payments.models import Invoice, PaymentMethod
from apps.students.models import Attendance, Graduation, Student

# Import all models
from apps.tenants.models import Tenant

User = get_user_model()


# ========================================
# DATABASE CONFIGURATION
# ========================================


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup database for all tests"""
    with django_db_blocker.unblock():
        # Ensure we're using the right database
        pass


@pytest.fixture
def db_access():
    """Simple database access fixture"""
    pass


# ========================================
# TENANT FIXTURES
# ========================================


@pytest.fixture
def tenant(db):
    """Create a test tenant with schema"""
    from apps.tenants.models import Domain, Tenant

    tenant, created = Tenant.objects.get_or_create(
        slug="test-academy",
        defaults={
            "name": "Test Academy",
            "email": "test@wbjj.com",
            "phone": "+5511999999999",
            "address": "Test Street, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234567",
            "country": "Brasil",
            "primary_color": "#3B82F6",
            "secondary_color": "#1E40AF",
            "timezone": "America/Sao_Paulo",
            "website": "https://test.wbjj.com",
            "monthly_fee": Decimal("200.00"),
            "is_active": True,
        },
    )

    # Criar domínio se necessário
    domain, _ = Domain.objects.get_or_create(
        domain="test-academy.localhost", defaults={"tenant": tenant, "is_primary": True}
    )

    return tenant


@pytest.fixture
def tenant_context(tenant):
    """Context manager for tenant operations"""
    from django_tenants.utils import tenant_context

    return tenant_context(tenant)


@pytest.fixture
def use_tenant_context(tenant_context):
    """Fixture para usar tenant context explicitamente em testes que precisam"""
    with tenant_context:
        yield


@pytest.fixture
def tenant_models_context(tenant, tenant_context):
    """Fixture combinado para testes que precisam do tenant e do contexto ativo"""
    with tenant_context:
        yield tenant


# ========================================
# USER FIXTURES
# ========================================


@pytest.fixture
def user_data():
    """Base user data for tests"""
    return {
        "email": "test@example.com",
        "first_name": "João",
        "last_name": "Silva",
        "password": "testpass123",
        "phone": "+5511999999999",
        "birth_date": date(1990, 5, 15),
        "is_verified": True,
    }


@pytest.fixture
def user(db, user_data):
    """Create a regular user"""
    return User.objects.create_user(**user_data)


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    return User.objects.create_superuser(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password="adminpass123",
        role="admin",
    )


@pytest.fixture
def instructor_user(db, user_data):
    """Create an instructor user"""
    user_data.update({"email": "instructor@example.com", "role": "instructor"})
    return User.objects.create_user(**user_data)


@pytest.fixture
def student_user(db, user_data):
    """Create a student user"""
    user_data.update({"email": "student@example.com", "role": "student"})
    return User.objects.create_user(**user_data)


# ========================================
# STUDENT FIXTURES
# ========================================


@pytest.fixture
def student_data():
    """Base student data"""
    return {
        "registration_number": "TEST001",
        "enrollment_date": date.today(),
        "belt_color": "white",
        "emergency_contact_name": "Maria Silva",
        "emergency_contact_phone": "+5511888888888",
        "emergency_contact_relationship": "Mãe",
    }


@pytest.fixture
def student(db, student_user, student_data):
    """Create a student"""
    return Student.objects.create(user=student_user, **student_data)


@pytest.fixture
def attendance(db, student):
    """Create an attendance record"""
    return Attendance.objects.create(
        student=student,
        class_date=date.today(),
        check_in_time="18:00",
        class_type="regular",
        notes="Test attendance",
    )


@pytest.fixture
def graduation(db, student):
    """Create a graduation record"""
    return Graduation.objects.create(
        student=student,
        from_belt="white",
        to_belt="blue",
        graduation_date=date.today(),
        notes="Good progress",
    )


# ========================================
# PAYMENT FIXTURES
# ========================================


@pytest.fixture
def payment_method(db):
    """Create a payment method"""
    return PaymentMethod.objects.create(
        name="PIX", code="pix", is_online=True, processing_fee=Decimal("0.00")
    )


@pytest.fixture
def invoice(db, student):
    """Create an invoice"""
    return Invoice.objects.create(
        student=student,
        amount=Decimal("200.00"),
        due_date=date.today() + timedelta(days=30),
        reference_month=date.today().replace(day=1),
        status="pending",
        description="Mensalidade",
    )


# ========================================
# MIDDLEWARE FIXTURES
# ========================================


@pytest.fixture
def middleware():
    """Create TenantMiddleware instance for testing"""
    from apps.authentication.middleware import TenantMiddleware

    return TenantMiddleware(get_response=lambda r: None)


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests"""
    from django.test import RequestFactory

    return RequestFactory()


@pytest.fixture
def test_tenant(db):
    """Create a tenant specifically for middleware tests"""
    tenant = Tenant.objects.create(
        name="Middleware Test Academy",
        slug="middleware-test",
        schema_name="middleware_test",
        domain_url="middleware-test.wbjj.com",
        email="middleware@wbjj.com",
        phone="+5511999999999",
        address="Test Street, 456",
        city="São Paulo",
        state="SP",
        zip_code="01234-567",
        country="Brasil",
        primary_color="#3B82F6",
        secondary_color="#1E40AF",
        timezone="America/Sao_Paulo",
        website="https://middleware-test.wbjj.com",
        monthly_fee=Decimal("200.00"),
        is_active=True,
    )
    return tenant


# ========================================
# API CLIENT FIXTURES
# ========================================


@pytest.fixture
def api_client():
    """DRF API Client"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """API client with authenticated user"""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client with admin user"""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def web_client():
    """Django test client"""
    return Client()


# ========================================
# UTILITY FIXTURES
# ========================================


@pytest.fixture
def sample_data():
    """Sample data for various tests"""
    return {
        "belts": ["white", "blue", "purple", "brown", "black"],
        "class_types": ["regular", "competition", "fundamentals", "advanced"],
        "payment_types": ["pix", "credit_card", "bank_transfer", "cash"],
        "roles": ["student", "instructor", "admin", "staff"],
    }


@pytest.fixture
def mock_settings(settings):
    """Mock settings for tests"""
    settings.TESTING = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    return settings
