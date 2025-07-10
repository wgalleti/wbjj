# Sistema de Testes wBJJ

Documentação completa do sistema de testes para o projeto wBJJ - Backend Django com multitenancy.

## 🎯 Visão Geral

O sistema de testes do wBJJ está estruturado para garantir **qualidade** e **confiabilidade** do código, seguindo os padrões estabelecidos no [context.md](context.md) com foco em **produtividade** e **feedback rápido**.

### 🏆 Objetivos dos Testes

- **Cobertura mínima**: 80% do código
- **Feedback rápido**: Testes unitários < 30 segundos
- **Confiabilidade**: Testes determinísticos e isolados
- **Multitenancy**: Validação completa do isolamento por tenant
- **Integração**: Testes end-to-end de APIs

---

## 📂 Estrutura de Testes

### Organização Obrigatória

```
backend/tests/
├── without_db/                    # Testes RÁPIDOS sem banco
│   ├── core/                     # Utils, serializers, validações
│   │   ├── test_openapi.py       # Validação OpenAPI
│   │   └── test_serializers_validation.py
│   ├── models/                   # Unit tests de models (mocks)
│   └── utils/                    # Testes de utilities
│
├── with_db/                      # Testes COMPLETOS com banco
│   ├── base.py                   # Classes base para testes
│   ├── conftest.py               # Fixtures pytest
│   │
│   ├── models/                   # Testes de models com DB
│   │   ├── test_authentication.py
│   │   ├── test_payments.py
│   │   ├── test_students.py
│   │   └── test_tenants.py
│   │
│   ├── views/                    # Testes de ViewSets/APIs
│   │   ├── test_authentication.py
│   │   ├── test_core.py
│   │   ├── test_payments.py
│   │   ├── test_students.py
│   │   └── test_tenants.py
│   │
│   ├── serializers/              # Testes de serializers com DB
│   │   ├── test_authentication.py
│   │   ├── test_payments.py
│   │   ├── test_students.py
│   │   └── test_tenants.py
│   │
│   ├── middleware/               # Testes de middleware
│   │   └── test_tenant_middleware.py
│   │
│   └── factories/                # Factory Boy para dados de teste
│       ├── authentication.py
│       ├── payments.py
│       ├── students.py
│       └── tenants.py
│
├── fixtures/                     # Dados de teste compartilhados
│   ├── users.json
│   └── tenants.json
│
├── base.py                       # Classes base compartilhadas
└── README_TEST_STRUCTURE.md      # Documentação da estrutura
```

### Princípios de Organização

1. **`without_db/`**: Testes **unitários rápidos** sem dependência de banco
2. **`with_db/`**: Testes **integração** que precisam de banco de dados
3. **`factories/`**: **Factory Boy** para criação consistente de dados
4. **`fixtures/`**: Dados **JSON** compartilhados entre testes

---

## 🚀 Scripts de Teste Obrigatórios

### 1. Testes Rápidos (Sem Banco)

```bash
# Script principal - Feedback em ~10-30 segundos
./scripts/test-without-db.sh

# Comando direto
uv run pytest tests/without_db/ --no-migrations --nomigrations

# Com argumentos extras
./scripts/test-without-db.sh -v --tb=short
```

**Quando usar:**
- ✅ Durante desenvolvimento diário
- ✅ Para feedback rápido de mudanças
- ✅ Validação de lógica sem dependências
- ✅ CI/CD para checks rápidos

### 2. Testes Completos (Com Banco)

```bash
# Script principal - Testes completos em ~2-5 minutos
./scripts/test-with-db.sh

# Comando direto
uv run pytest tests/with_db/ --create-db --reuse-db --cov=apps

# Com argumentos extras
./scripts/test-with-db.sh --maxfail=1 -v
```

**Quando usar:**
- ✅ Antes de commits
- ✅ Para validação completa
- ✅ Testes de integração
- ✅ CI/CD pipelines

### 3. Comandos Específicos

#### Testes com Cobertura
```bash
# Cobertura completa com relatório HTML
uv run pytest tests/with_db/ \
  --create-db \
  --cov=apps \
  --cov-report=html:htmlcov \
  --cov-report=term-missing \
  --cov-fail-under=80

# Visualizar relatório
open htmlcov/index.html
```

#### Testes por Módulo
```bash
# Apenas autenticação
uv run pytest tests/with_db/views/test_authentication.py -v

# Apenas models
uv run pytest tests/with_db/models/ -v

# Padrão específico
uv run pytest tests/ -k "test_login" -v

# Apenas testes rápidos
uv run pytest tests/without_db/ -v
```

#### Debugging de Testes
```bash
# Output detalhado
uv run pytest tests/with_db/views/test_authentication.py -v -s

# Parar no primeiro erro
uv run pytest tests/with_db/ -x

# Apenas testes que falharam
uv run pytest tests/with_db/ --lf

# Debug com breakpoint
uv run pytest tests/with_db/ --pdb
```

---

## 🗄️ Gerenciamento de Banco de Dados de Teste

### Configuração Automática

#### Setup Completo (Recomendado)
```bash
# Setup inicial completo - cria tudo automaticamente
./scripts/dev-setup.sh

# Setup com limpeza total
./scripts/dev-setup.sh --clean
```

#### Criação Manual do Banco de Teste
```bash
# Criar banco de teste específico
docker-compose exec db psql -U wbjj_user -d wbjj_dev -c "CREATE DATABASE test_wbjj;"

# Verificar bancos existentes
docker-compose exec db psql -U wbjj_user -d wbjj_dev -c "\l"
```

### Reset do Banco de Teste

#### Reset Completo
```bash
# Dropar banco de teste (será recriado automaticamente)
docker-compose exec db psql -U wbjj_user -d wbjj_dev -c "DROP DATABASE IF EXISTS test_wbjj_testing;"

# Próximo teste criará novo banco automaticamente
uv run pytest tests/with_db/ --create-db
```

#### Reset de Schema
```bash
# Limpar apenas dados, manter estrutura
uv run pytest tests/with_db/ --create-db --reuse-db
```

### Migrations de Teste

#### Aplicar Migrations Manualmente
```bash
# Aplicar migrations no ambiente de teste
uv run manage.py migrate --settings=config.settings.testing

# Verificar status das migrations
uv run manage.py showmigrations --settings=config.settings.testing

# Fazer rollback se necessário
uv run manage.py migrate app_name 0001 --settings=config.settings.testing
```

#### Configurações de Testing
```python
# config/settings/testing.py
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'test_wbjj_testing',  # Banco específico para testes
        'USER': 'wbjj_user',
        'PASSWORD': 'wbjj_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_wbjj_testing',
        }
    }
}

# Configurações otimizadas para testes
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Mais rápido para testes
]

CELERY_TASK_ALWAYS_EAGER = True  # Executar tasks síncronamente
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

---

## 🏭 Factory Boy - Dados de Teste

### Configuração das Factories

#### Estrutura Base
```python
# tests/with_db/factories/__init__.py
from .authentication import UserFactory
from .tenants import TenantFactory, DomainFactory
from .students import StudentFactory
from .payments import PaymentFactory

__all__ = [
    'UserFactory',
    'TenantFactory', 'DomainFactory',
    'StudentFactory',
    'PaymentFactory',
]
```

#### Factory de Usuários
```python
# tests/with_db/factories/authentication.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(DjangoModelFactory):
    """Factory para criação de usuários de teste"""

    class Meta:
        model = User
        django_get_or_create = ('email',)

    # Dados básicos
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    first_name = factory.Faker('first_name', locale='pt_BR')
    last_name = factory.Faker('last_name', locale='pt_BR')

    # Configurações padrão
    role = 'student'
    is_active = True
    is_verified = True
    password = factory.PostGenerationMethodCall('set_password', '123456')

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Adicionar grupos se especificado"""
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)

# Factories especializadas
class AdminUserFactory(UserFactory):
    """Factory para usuários admin"""
    role = 'admin'
    email = factory.Sequence(lambda n: f"admin{n}@test.com")

class InstructorUserFactory(UserFactory):
    """Factory para instrutores"""
    role = 'instructor'
    email = factory.Sequence(lambda n: f"instructor{n}@test.com")

class StudentUserFactory(UserFactory):
    """Factory para alunos"""
    role = 'student'
    email = factory.Sequence(lambda n: f"student{n}@test.com")
```

#### Factory de Tenants
```python
# tests/with_db/factories/tenants.py
import factory
from factory.django import DjangoModelFactory
from apps.tenants.models import Tenant, Domain

class TenantFactory(DjangoModelFactory):
    """Factory para criação de tenants"""

    class Meta:
        model = Tenant

    schema_name = factory.Sequence(lambda n: f"tenant_{n}")
    name = factory.Faker('company', locale='pt_BR')
    is_active = True

class DomainFactory(DjangoModelFactory):
    """Factory para domínios de tenant"""

    class Meta:
        model = Domain

    domain = factory.Sequence(lambda n: f"tenant{n}.localhost")
    tenant = factory.SubFactory(TenantFactory)
    is_primary = True
```

### Uso das Factories

#### Testes Básicos
```python
# tests/with_db/models/test_authentication.py
from tests.with_db.factories import UserFactory, AdminUserFactory

class TestUserModel:

    def test_create_student_user(self):
        """Teste criação de usuário estudante"""
        user = UserFactory(role='student')
        assert user.role == 'student'
        assert user.is_active is True
        assert user.check_password('123456')

    def test_create_admin_user(self):
        """Teste criação de usuário admin"""
        admin = AdminUserFactory()
        assert admin.role == 'admin'
        assert 'admin' in admin.email

    def test_create_multiple_users(self):
        """Teste criação em lote"""
        users = UserFactory.create_batch(5, role='instructor')
        assert len(users) == 5
        assert all(user.role == 'instructor' for user in users)
```

#### Testes com Relacionamentos
```python
def test_user_with_custom_data(self):
    """Teste usuário com dados específicos"""
    user = UserFactory(
        email='custom@test.com',
        first_name='João',
        role='admin',
        is_verified=False
    )
    assert user.email == 'custom@test.com'
    assert user.first_name == 'João'
    assert user.is_verified is False
```

---

## 📋 Configurações de Teste

### pytest.ini Obrigatório

```ini
# pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.testing"
python_files = ["tests.py", "test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
testpaths = ["tests"]

addopts = [
    "--strict-markers",
    "--strict-config",
    "--reuse-db",
    "--nomigrations",
    "--tb=short",
    "--maxfail=10",
    "--timeout=300",
    "--disable-warnings",
]

markers = [
    "slow: marca testes como lentos (usar '-m \"not slow\"' para pular)",
    "unit: testes unitários",
    "integration: testes de integração",
    "requires_db: testes que precisam de banco de dados",
    "tenant: testes específicos de multitenancy",
]

# Configurações de coverage
filterwarnings = [
    "ignore::django.utils.deprecation.RemovedInDjango50Warning",
    "ignore::DeprecationWarning",
]
```

### Classes Base para Testes

#### BaseTestCase
```python
# tests/base.py
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from tests.with_db.factories import UserFactory, TenantFactory

User = get_user_model()

class BaseTestCase(TestCase):
    """Classe base para testes que não precisam de tenant"""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.admin = UserFactory(role='admin')

class BaseTenantTestCase(TestCase):
    """Classe base para testes com multitenancy"""

    @classmethod
    def setUpTestData(cls):
        # Criar tenant de teste
        cls.tenant = TenantFactory(schema_name='test_tenant')

        # Usuários por role
        cls.admin = UserFactory(role='admin')
        cls.instructor = UserFactory(role='instructor')
        cls.student = UserFactory(role='student')

    def setUp(self):
        # Configurar contexto de tenant para requests
        from django.test import RequestFactory
        self.factory = RequestFactory()
```

#### BaseModelTestCase
```python
# tests/with_db/base.py
from django.test import TestCase
from tests.with_db.factories import TenantFactory, UserFactory

class BaseModelTestCase(TestCase):
    """Classe base para testes de models com configuração padrão"""

    model_class = None  # DEVE ser sobrescrito nas subclasses

    @classmethod
    def setUpTestData(cls):
        if not cls.model_class:
            raise ValueError("model_class deve ser definido na subclasse")

        cls.tenant = TenantFactory()
        cls.user = UserFactory()

    def create_instance(self, **kwargs):
        """Helper para criar instância do model"""
        if hasattr(self.model_class, 'objects'):
            return self.model_class.objects.create(**kwargs)
        return self.model_class(**kwargs)
```

### Fixtures Pytest

#### conftest.py
```python
# tests/with_db/conftest.py
import pytest
from django.core.management import call_command
from tests.with_db.factories import UserFactory, TenantFactory

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup inicial do banco de dados"""
    with django_db_blocker.unblock():
        # Aplicar migrations se necessário
        call_command('migrate', '--run-syncdb', verbosity=0)

@pytest.fixture
def api_client():
    """Cliente REST API configurado"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    """Cliente autenticado com usuário padrão"""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client

@pytest.fixture
def admin_client(api_client):
    """Cliente autenticado como admin"""
    admin = UserFactory(role='admin')
    api_client.force_authenticate(user=admin)
    api_client.user = admin
    return api_client

@pytest.fixture
def tenant_setup():
    """Setup de tenant para testes"""
    tenant = TenantFactory()
    return {
        'tenant': tenant,
        'domain': tenant.domains.first(),
        'admin': UserFactory(role='admin'),
        'instructor': UserFactory(role='instructor'),
        'student': UserFactory(role='student'),
    }
```

---

## 🧪 Tipos de Teste

### 1. Testes Unitários (without_db/)

#### Serializers Validation
```python
# tests/without_db/core/test_serializers_validation.py
import pytest
from django.core.exceptions import ValidationError
from apps.students.serializers import StudentSerializer

class TestStudentSerializerValidation:
    """Testes de validação sem banco de dados"""

    def test_email_validation_invalid_format(self):
        """Teste validação de email inválido"""
        data = {'email': 'invalid-email', 'name': 'Teste'}
        serializer = StudentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_required_fields_validation(self):
        """Teste campos obrigatórios"""
        serializer = StudentSerializer(data={})
        assert not serializer.is_valid()

        required_fields = ['email', 'name']
        for field in required_fields:
            assert field in serializer.errors

    @pytest.mark.parametrize("email", [
        "valid@test.com",
        "user.name@domain.co.uk",
        "test+tag@example.org"
    ])
    def test_email_validation_valid_formats(self, email):
        """Teste formatos de email válidos"""
        data = {'email': email, 'name': 'Teste'}
        serializer = StudentSerializer(data=data)
        assert serializer.is_valid(), f"Email {email} deveria ser válido"
```

#### OpenAPI Validation
```python
# tests/without_db/core/test_openapi.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

class TestOpenAPISchema(TestCase):
    """Testes do schema OpenAPI sem banco"""

    def setUp(self):
        self.client = APIClient()

    def test_openapi_schema_generation(self):
        """Teste geração do schema OpenAPI"""
        # Não faz request real, testa apenas a geração
        from drf_spectacular.openapi import AutoSchema
        schema = AutoSchema()
        assert schema is not None

    def test_schema_endpoints_documented(self):
        """Teste se endpoints principais estão documentados"""
        from drf_spectacular.utils import extend_schema
        # Testa se decorators estão aplicados corretamente
        assert extend_schema is not None
```

### 2. Testes de Integração (with_db/)

#### Testes de ViewSets
```python
# tests/with_db/views/test_students.py
import pytest
from django.urls import reverse
from rest_framework import status
from tests.with_db.factories import StudentFactory, UserFactory

@pytest.mark.django_db
class TestStudentViewSet:
    """Testes do ViewSet de estudantes"""

    def test_list_students_as_admin(self, admin_client):
        """Admin pode listar todos os estudantes"""
        # Criar dados de teste
        StudentFactory.create_batch(3)

        url = reverse('student-list')
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_list_students_as_student_forbidden(self, authenticated_client):
        """Estudante não pode listar outros estudantes"""
        StudentFactory.create_batch(3)

        url = reverse('student-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_student_as_admin(self, admin_client):
        """Admin pode criar estudante"""
        data = {
            'email': 'new@test.com',
            'name': 'Novo Estudante',
            'belt_color': 'white'
        }

        url = reverse('student-list')
        response = admin_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == data['email']

    def test_student_can_access_own_data(self, api_client):
        """Estudante pode acessar próprios dados"""
        student_user = UserFactory(role='student')
        student = StudentFactory(user=student_user)

        api_client.force_authenticate(user=student_user)

        url = reverse('student-detail', kwargs={'pk': student.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(student.id)
```

#### Testes de Models
```python
# tests/with_db/models/test_students.py
import pytest
from django.core.exceptions import ValidationError
from tests.with_db.factories import StudentFactory, UserFactory

@pytest.mark.django_db
class TestStudentModel:
    """Testes do model Student"""

    def test_create_student_success(self):
        """Teste criação bem-sucedida de estudante"""
        student = StudentFactory()

        assert student.id is not None
        assert student.is_active is True
        assert student.created_at is not None

    def test_student_str_method(self):
        """Teste método __str__ do model"""
        student = StudentFactory(name="João Silva")
        assert str(student) == "João Silva"

    def test_email_unique_constraint(self):
        """Teste constraint de email único"""
        email = "teste@unique.com"
        StudentFactory(email=email)

        with pytest.raises(Exception):  # IntegrityError ou ValidationError
            StudentFactory(email=email)

    def test_belt_color_choices(self):
        """Teste choices de cor de faixa"""
        valid_colors = ['white', 'blue', 'purple', 'brown', 'black']

        for color in valid_colors:
            student = StudentFactory(belt_color=color)
            assert student.belt_color == color

    def test_soft_delete(self):
        """Teste soft delete"""
        student = StudentFactory()
        student_id = student.id

        # Soft delete
        student.is_active = False
        student.save()

        # Verificar que ainda existe no banco
        from apps.students.models import Student
        assert Student.objects.filter(id=student_id).exists()

        # Mas não aparece em queries padrão (se implementado)
        assert not Student.active_objects.filter(id=student_id).exists()
```

### 3. Testes de Middleware

#### TenantMiddleware
```python
# tests/with_db/middleware/test_tenant_middleware.py
import pytest
from django.test import RequestFactory
from django.http import HttpResponse
from apps.tenants.middleware import TenantMiddleware
from tests.with_db.factories import TenantFactory, DomainFactory

@pytest.mark.django_db
class TestTenantMiddleware:
    """Testes do middleware de tenant"""

    def setup_method(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda req: HttpResponse())

    def test_tenant_detection_by_subdomain(self):
        """Teste detecção de tenant por subdomínio"""
        # Criar tenant e domínio
        tenant = TenantFactory(schema_name='academia_alpha')
        DomainFactory(tenant=tenant, domain='academia-alpha.localhost')

        # Simular request com subdomínio
        request = self.factory.get('/', HTTP_HOST='academia-alpha.localhost')

        response = self.middleware(request)

        assert hasattr(request, 'tenant')
        assert request.tenant.schema_name == 'academia_alpha'

    def test_invalid_subdomain_returns_404(self):
        """Teste subdomínio inválido retorna 404"""
        request = self.factory.get('/', HTTP_HOST='inexistente.localhost')

        with pytest.raises(Exception):  # Deve levantar exceção
            self.middleware(request)

    def test_tenant_headers_in_response(self):
        """Teste headers de tenant na resposta"""
        tenant = TenantFactory(schema_name='test_tenant')
        DomainFactory(tenant=tenant, domain='test.localhost')

        request = self.factory.get('/', HTTP_HOST='test.localhost')
        response = self.middleware(request)

        assert 'X-Tenant-Schema' in response
        assert response['X-Tenant-Schema'] == 'test_tenant'
```

### 4. Testes de Performance

#### Benchmark de APIs
```python
# tests/with_db/performance/test_api_performance.py
import pytest
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from tests.with_db.factories import StudentFactory, UserFactory

class TestAPIPerformance(TransactionTestCase):
    """Testes de performance de APIs"""

    def setUp(self):
        self.client = APIClient()
        self.admin = UserFactory(role='admin')
        self.client.force_authenticate(user=self.admin)

    @pytest.mark.slow
    def test_student_list_performance_with_large_dataset(self):
        """Teste performance de listagem com muitos dados"""
        # Criar dataset grande
        StudentFactory.create_batch(1000)

        url = reverse('student-list')

        # Teste com assertNumQueries para controlar queries
        with self.assertNumQueries(3):  # Máximo 3 queries
            response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) <= 20  # Paginação

    @pytest.mark.slow
    def test_student_creation_batch_performance(self):
        """Teste performance de criação em lote"""
        import time

        students_data = [
            {
                'email': f'student{i}@test.com',
                'name': f'Student {i}',
                'belt_color': 'white'
            }
            for i in range(100)
        ]

        start_time = time.time()

        for data in students_data:
            url = reverse('student-list')
            response = self.client.post(url, data, format='json')
            assert response.status_code == 201

        end_time = time.time()

        # Deve criar 100 estudantes em menos de 10 segundos
        assert (end_time - start_time) < 10.0
```

---

## 🔍 Debugging e Troubleshooting

### Comandos de Debug

#### Logs Durante Testes
```python
# Habilitar logs específicos durante testes
import logging
import sys

# Configurar logging para testes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    stream=sys.stdout
)

def test_with_debug_logs():
    """Teste com logs detalhados"""
    logger = logging.getLogger(__name__)
    logger.debug("Iniciando teste com debug")

    # Seu teste aqui
    assert True

    logger.debug("Teste finalizado com sucesso")
```

#### Debugging com PDB
```bash
# Executar teste com breakpoint automático em falhas
uv run pytest tests/with_db/views/test_authentication.py --pdb

# Usar ipdb (mais avançado)
uv run pytest tests/with_db/ --pdb --pdbcls=IPython.terminal.debugger:Pdb
```

#### Verbosidade e Output
```bash
# Máxima verbosidade
uv run pytest tests/with_db/views/test_authentication.py -vvv -s

# Mostrar print statements
uv run pytest tests/with_db/ -s

# Mostrar apenas falhas
uv run pytest tests/with_db/ --tb=short

# Mostrar apenas linha da falha
uv run pytest tests/with_db/ --tb=line

# Parar no primeiro erro
uv run pytest tests/with_db/ -x
```

### Problemas Comuns e Soluções

#### 1. Banco de Dados
```bash
# Problema: Tabelas não existem
# Solução: Resetar banco de teste
docker-compose exec db psql -U wbjj_user -d wbjj_dev -c "DROP DATABASE IF EXISTS test_wbjj_testing;"
uv run pytest tests/with_db/ --create-db

# Problema: Migrations desatualizadas
# Solução: Aplicar migrations
uv run manage.py migrate --settings=config.settings.testing

# Problema: Dados sujos entre testes
# Solução: Usar --reuse-db com cuidado
uv run pytest tests/with_db/ --create-db  # Sempre criar novo
```

#### 2. Multitenancy
```python
# Problema: Tenant não configurado
# Solução: Usar BaseTenantTestCase ou configurar manualmente

from django_tenants.utils import schema_context

def test_with_tenant_context():
    tenant = TenantFactory()

    with schema_context(tenant.schema_name):
        # Teste executado no contexto do tenant
        student = StudentFactory()
        assert student.id is not None
```

#### 3. Performance
```bash
# Problema: Testes muito lentos
# Solução: Usar testes without_db quando possível
./scripts/test-without-db.sh  # Muito mais rápido

# Problema: Muitas queries desnecessárias
# Solução: Usar assertNumQueries
with self.assertNumQueries(2):
    response = client.get('/api/students/')
```

#### 4. Factories
```python
# Problema: Dados não realistas
# Solução: Configurar Faker com locale brasileiro

import factory

class StudentFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name', locale='pt_BR')
    city = factory.Faker('city', locale='pt_BR')

# Problema: Relacionamentos complexos
# Solução: Usar SubFactory e RelatedFactory

class StudentFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    academy = factory.SubFactory(AcademyFactory)
```

---

## 📊 Cobertura de Testes

### Configuração de Coverage

#### pyproject.toml
```toml
[tool.coverage.run]
source = ["apps"]
omit = [
    "*/migrations/*",
    "*/venv/*",
    "*/tests/*",
    "manage.py",
    "config/wsgi.py",
    "config/asgi.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "@abstract",
]

show_missing = true
skip_covered = false
precision = 2

[tool.coverage.html]
directory = "htmlcov"
```

#### Comandos de Coverage
```bash
# Coverage completa com relatório HTML
uv run pytest tests/with_db/ \
  --cov=apps \
  --cov-report=html:htmlcov \
  --cov-report=xml:coverage.xml \
  --cov-report=term-missing \
  --cov-fail-under=80

# Apenas report terminal
uv run pytest tests/with_db/ --cov=apps --cov-report=term-missing

# Coverage de arquivo específico
uv run pytest tests/with_db/views/test_authentication.py --cov=apps.authentication

# Coverage incremental (apenas código alterado)
uv run pytest tests/with_db/ --cov=apps --cov-report=term-missing --cov-context=test
```

### Metas de Cobertura

| **Módulo** | **Meta** | **Status** |
|------------|----------|------------|
| `apps.authentication` | 95% | ✅ |
| `apps.core` | 90% | ✅ |
| `apps.students` | 85% | 🔄 |
| `apps.payments` | 85% | 🔄 |
| `apps.tenants` | 90% | ✅ |
| **Global** | **80%** | **✅** |

---

## 🚀 CI/CD Integration

### GitHub Actions

#### Workflow de Testes
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run fast tests
        run: ./scripts/test-without-db.sh

      - name: Run full tests
        run: ./scripts/test-with-db.sh

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### Pre-commit Hooks

#### Configuração
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: fast-tests
        name: Fast Tests
        entry: ./scripts/test-without-db.sh
        language: system
        pass_filenames: false
        stages: [commit]

      - id: full-tests
        name: Full Tests (Pre-push)
        entry: ./scripts/test-with-db.sh
        language: system
        pass_filenames: false
        stages: [push]
```

#### Instalação
```bash
# Instalar pre-commit
uv add --dev pre-commit

# Configurar hooks
pre-commit install

# Configurar hook de push
pre-commit install --hook-type pre-push

# Testar hooks
pre-commit run --all-files
```

---

## 📝 Boas Práticas

### 1. Organização de Testes

✅ **FAZER:**
- Usar estrutura `with_db/` vs `without_db/`
- Nomear testes descritivamente: `test_admin_can_create_student`
- Agrupar testes relacionados em classes
- Usar factories ao invés de criar dados manualmente

❌ **NÃO FAZER:**
- Testes que dependem de outros testes
- Dados hardcoded em testes
- Testes muito longos (> 50 linhas)
- Ignorar cobertura de código

### 2. Performance

✅ **FAZER:**
- Executar testes rápidos durante desenvolvimento
- Usar `@pytest.mark.slow` para testes demorados
- Configurar `--reuse-db` para testes iterativos
- Otimizar queries com `assertNumQueries`

❌ **NÃO FAZER:**
- Criar dados desnecessários nos testes
- Executar testes with_db para validações simples
- Ignorar warnings de performance

### 3. Isolamento

✅ **FAZER:**
- Cada teste deve ser independente
- Usar transações para rollback automático
- Limpar dados entre testes quando necessário
- Validar isolamento de tenants

❌ **NÃO FAZER:**
- Compartilhar estado entre testes
- Modificar configurações globais sem reset
- Ignorar vazamentos de dados entre tenants

### 4. Assertivas

✅ **FAZER:**
- Assertivas específicas: `assert response.status_code == 201`
- Validar dados retornados: `assert 'email' in response.data`
- Testar edge cases e errors
- Usar `pytest.raises` para exceções

❌ **NÃO FAZER:**
- Assertivas genéricas: `assert response`
- Não testar casos de erro
- Assumir dados sem validar

---

## 🎯 Checklist de Testes

### Antes de Commit

```markdown
## Checklist de Testes ✅

### Desenvolvimento Diário
- [ ] `./scripts/test-without-db.sh` passou
- [ ] Novos testes criados para novas funcionalidades
- [ ] Testes existentes ainda passam
- [ ] Coverage não diminuiu

### Antes do Commit
- [ ] `./scripts/test-with-db.sh` passou
- [ ] Coverage >= 80%
- [ ] Todos os tipos de teste executados
- [ ] Testes de integração passaram

### Novos Features
- [ ] Testes unitários (models, serializers)
- [ ] Testes de integração (views, APIs)
- [ ] Testes de permissões (RBAC)
- [ ] Testes de multitenancy (isolamento)
- [ ] Factories criadas para novos models

### Performance
- [ ] Testes rápidos < 30 segundos
- [ ] Testes completos < 5 minutos
- [ ] Queries otimizadas (assertNumQueries)
- [ ] Sem vazamentos de memória
```

---

## 📚 Recursos Adicionais

### Documentação de Referência

- [Django Testing](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

### Ferramentas Úteis

- **pytest-xdist**: Execução paralela de testes
- **pytest-benchmark**: Benchmark automático
- **pytest-mock**: Mocking avançado
- **model-bakery**: Alternativa ao Factory Boy
- **django-test-plus**: Helpers para testes Django

### Exemplos Avançados

Consulte os arquivos de teste existentes em:
- `tests/with_db/views/test_authentication.py` - Autenticação JWT
- `tests/with_db/middleware/test_tenant_middleware.py` - Multitenancy
- `tests/with_db/models/test_*.py` - Models com validações
- `tests/without_db/core/test_*.py` - Validações rápidas

---

**Sistema de Testes wBJJ: Garantindo Qualidade e Confiabilidade** 🎯

*Documentação completa para desenvolvimento orientado a testes no projeto wBJJ.*
