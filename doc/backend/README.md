# Backend - wBJJ API

## Visão Geral
O backend do wBJJ é uma API RESTful responsável por toda a lógica de negócio, gerenciamento de dados e implementação do sistema multitenancy para academias de jiu-jitsu.

## Decisão Tecnológica

### Opções Avaliadas

#### Django + Django Rest Framework (Escolhido para MVP)
**Justificativa**: Produtividade máxima para validação rápida de mercado
- ✅ **Produtividade**: Desenvolvimento extremamente rápido
- ✅ **Multitenancy**: Django-tenant-schemas maduro e testado
- ✅ **Admin Interface**: Interface administrativa pronta
- ✅ **Ecosystem**: Ecosystem mais maduro do Python
- ✅ **ORM**: Django ORM poderoso e intuitivo
- ⚠️ **Trade-off**: Performance inferior, mas adequada para MVP

#### Roadmap Futuro
- **V2.0 - Golang**: Migração pós-validação para alta performance
- **Microservices**: Arquitetura mais escalável quando necessário

## Arquitetura do Backend

### Estrutura de Diretórios
```
backend/
├── config/                    # Projeto Django principal
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Configurações base
│   │   ├── development.py     # Configurações de desenvolvimento
│   │   ├── production.py      # Configurações de produção
│   │   └── testing.py         # Configurações de teste
│   ├── urls.py                # URLs principais
│   ├── wsgi.py                # WSGI para deploy
│   └── asgi.py                # ASGI para async (futuro)
├── apps/                      # Django apps
│   ├── __init__.py
│   ├── tenants/               # App de multitenancy
│   │   ├── __init__.py
│   │   ├── models.py          # Modelos de tenant
│   │   ├── views.py           # Views de tenant
│   │   ├── serializers.py     # Serializers DRF
│   │   ├── urls.py            # URLs do app
│   │   ├── admin.py           # Admin interface
│   │   ├── migrations/        # Migrações do app
│   │   └── tests.py           # Testes do app
│   ├── authentication/        # App de autenticação
│   │   ├── __init__.py
│   │   ├── models.py          # User model customizado
│   │   ├── views.py           # Login/logout views
│   │   ├── serializers.py     # Auth serializers
│   │   ├── permissions.py     # Permissões customizadas
│   │   └── middleware.py      # Middleware de tenant
│   ├── students/              # App de alunos
│   │   ├── __init__.py
│   │   ├── models.py          # Student, Graduation models
│   │   ├── views.py           # CRUD views
│   │   ├── serializers.py     # Student serializers
│   │   ├── filters.py         # Filtros de busca
│   │   └── admin.py           # Admin interface
│   ├── payments/              # App financeiro
│   │   ├── __init__.py
│   │   ├── models.py          # Payment, Invoice models
│   │   ├── views.py           # Financial views
│   │   ├── serializers.py     # Payment serializers
│   │   ├── services.py        # Lógica de negócio
│   │   └── tasks.py           # Celery tasks (futuro)
│   └── core/                  # Utilities compartilhadas
│       ├── __init__.py
│       ├── models.py          # Abstract base models
│       ├── permissions.py     # Permissões base
│       ├── pagination.py      # Paginação customizada
│       ├── exceptions.py      # Exception handlers
│       └── utils.py           # Utilities gerais
├── static/                    # Arquivos estáticos
├── media/                     # Upload de arquivos
├── templates/                 # Templates Django (se necessário)
├── pyproject.toml             # Configuração do projeto (UV)
├── uv.lock                    # Lock file das dependências
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── scripts/
│   ├── start.sh             # Script de inicialização
│   ├── migrate.sh           # Script de migração
│   └── seed.sh              # Script de dados iniciais
├── manage.py                # Django management
├── CONTEXT.md              # Contexto e regras do projeto (IA)
└── docs/
    ├── api.md               # Documentação da API
    └── deployment.md        # Guia de deploy
```

## Stack Tecnológico

### Gerenciamento de Dependências
- **UV**: Gerenciador de pacotes moderno e rápido
- **pyproject.toml**: Configuração centralizada do projeto
- **Python 3.11**: Versão LTS com melhor performance

### Core Framework
- **Django 4.2.x**: Versão LTS fixada para estabilidade
- **Django Rest Framework 3.14.x**: APIs RESTful robustas
- **drf-spectacular**: Documentação OpenAPI automática
- **PostgreSQL 15**: Banco de dados principal

### Multitenancy & Isolamento
- **django-tenant-schemas**: Schemas dinâmicos por tenant
- **psycopg2-binary**: Driver PostgreSQL otimizado
- **redis**: Cache distribuído e sessions

### Autenticação & Segurança
- **djangorestframework-simplejwt**: JWT tokens seguros
- **django-cors-headers**: CORS configurável
- **django-permissions-policy**: Headers de segurança
- **cryptography**: Criptografia de dados sensíveis

### APIs & Integrações
- **drf-spectacular**: Swagger/OpenAPI 3.0 automático
- **django-filter**: Filtros avançados para APIs
- **djangorestframework-camel-case**: CamelCase para frontend
- **django-extensions**: Comandos úteis para desenvolvimento

### Performance & Cache
- **django-redis**: Cache Redis integrado
- **django-cachalot**: ORM cache automático
- **django-compression-middleware**: Compressão de respostas

### Desenvolvimento & Qualidade
- **pytest-django**: Framework de testes robusto
- **factory-boy**: Factories para dados de teste
- **django-debug-toolbar**: Debug avançado
- **pre-commit**: Hooks de qualidade de código
- **ruff**: Linter extremamente rápido
- **black**: Formatação de código automática

### Monitoramento & Logs
- **django-structlog**: Logs estruturados
- **sentry-sdk**: Monitoramento de erros
- **django-health-check**: Endpoints de saúde

## Implementação Multitenancy

### Modelo de Dados Global
```python
# apps/tenants/models.py
from django.db import models
from django_tenant_schemas.models import TenantMixin
import uuid

class Tenant(TenantMixin):
    """
    Modelo principal para multitenancy usando django-tenant-schemas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=100, unique=True)
    schema_name = models.CharField(max_length=100, unique=True)
    
    # Campos específicos do negócio
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='tenant_logos/', blank=True)
    
    # Configurações visuais
    primary_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#1E40AF')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        
    def __str__(self):
        return self.name
```

### Middleware de Tenant
```python
# apps/authentication/middleware.py
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django_tenant_schemas.utils import get_tenant_model, get_public_schema_name
from django.db import connection

class TenantMiddleware(MiddlewareMixin):
    """
    Middleware para detectar tenant via subdomínio e configurar schema
    """
    
    def process_request(self, request):
        # Extrair tenant do subdomínio
        hostname = request.get_host().split(':')[0]  # Remove porta se existir
        subdomain = hostname.split('.')[0]
        
        # Pular para schema público em casos específicos
        if subdomain in ['www', 'api', 'admin']:
            return None
            
        try:
            # Buscar tenant no banco
            tenant_model = get_tenant_model()
            tenant = tenant_model.objects.get(subdomain=subdomain, is_active=True)
            
            # Configurar conexão para usar schema do tenant
            connection.set_tenant(tenant)
            
            # Adicionar tenant ao request para uso posterior
            request.tenant = tenant
            
        except tenant_model.DoesNotExist:
            # Tenant não encontrado
            raise Http404("Academia não encontrada")
        except Exception as e:
            # Log do erro
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro no middleware de tenant: {e}")
            raise Http404("Erro interno")
```

### ViewSets DRF com Multitenancy
```python
# apps/core/viewsets.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db import connection

class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet base que garante isolamento por tenant
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna queryset filtrado pelo tenant atual
        Isolamento automático através do schema
        """
        return self.queryset.all()
    
    def perform_create(self, serializer):
        """
        Garante que objetos criados pertencem ao tenant atual
        """
        # O tenant já está configurado no schema via middleware
        serializer.save()
    
    def list(self, request, *args, **kwargs):
        """
        Override para adicionar informações do tenant se necessário
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

## APIs Principais

### Autenticação
```python
# apps/authentication/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserLoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Endpoint de autenticação com JWT
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Adicionar informações do tenant ao token
            if hasattr(request, 'tenant'):
                access_token['tenant_id'] = str(request.tenant.id)
                access_token['tenant_name'] = request.tenant.name
            
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                    'role': user.role if hasattr(user, 'role') else 'user'
                }
            })
        else:
            return Response(
                {'error': 'Credenciais inválidas'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Gestão de Alunos
```python
# apps/students/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.viewsets import TenantViewSet
from .models import Student
from .serializers import StudentSerializer, StudentCreateSerializer
from .filters import StudentFilter

class StudentViewSet(TenantViewSet):
    """
    ViewSet completo para gestão de alunos
    Inclui CRUD + funcionalidades específicas
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchBackend, filters.OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'belt_color']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer
    
    @action(detail=True, methods=['post'])
    def graduate(self, request, pk=None):
        """
        Endpoint específico para graduação de faixa
        """
        student = self.get_object()
        new_belt = request.data.get('new_belt')
        graduation_date = request.data.get('graduation_date')
        
        if not new_belt:
            return Response(
                {'error': 'Nova faixa é obrigatória'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lógica de graduação
        student.graduate(new_belt, graduation_date)
        
        return Response({
            'message': f'Aluno graduado para {new_belt}',
            'student': StudentSerializer(student).data
        })
    
    @action(detail=False)
    def by_belt(self, request):
        """
        Listar alunos agrupados por faixa
        """
        students_by_belt = {}
        for student in self.get_queryset():
            belt = student.belt_color
            if belt not in students_by_belt:
                students_by_belt[belt] = []
            students_by_belt[belt].append(StudentSerializer(student).data)
        
        return Response(students_by_belt)
```

## Documentação da API

### OpenAPI/Swagger com drf-spectacular
```python
# config/settings/base.py
INSTALLED_APPS = [
    # ... outras apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'wBJJ API',
    'DESCRIPTION': 'Sistema de gestão para academias de jiu-jitsu com multitenancy',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    
    # Configurações de segurança
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    },
    
    # Configurações de UI
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    
    # Tags para organização
    'TAGS': [
        {'name': 'auth', 'description': 'Autenticação e autorização'},
        {'name': 'students', 'description': 'Gestão de alunos'},
        {'name': 'payments', 'description': 'Gestão financeira'},
        {'name': 'tenants', 'description': 'Gestão de academias'},
        {'name': 'health', 'description': 'Monitoramento da aplicação'},
    ],
}
```

### URLs da Documentação
```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/tenants/', include('apps.tenants.urls')),
    
    # Documentação da API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health checks
    path('health/', include('health_check.urls')),
]
```

### Documentação Avançada de ViewSets
```python
# apps/students/views.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiParameter
from rest_framework import status

@extend_schema_view(
    list=extend_schema(
        summary="Listar alunos",
        description="Retorna lista paginada de alunos da academia atual",
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Buscar por nome, email ou telefone'
            ),
            OpenApiParameter(
                name='belt_color',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filtrar por cor da faixa'
            ),
        ],
        tags=['students']
    ),
    create=extend_schema(
        summary="Criar aluno",
        description="Cria um novo aluno na academia atual",
        tags=['students']
    ),
    retrieve=extend_schema(
        summary="Detalhes do aluno",
        description="Retorna detalhes completos de um aluno específico",
        tags=['students']
    ),
    update=extend_schema(
        summary="Atualizar aluno",
        description="Atualiza dados de um aluno existente",
        tags=['students']
    ),
    destroy=extend_schema(
        summary="Remover aluno",
        description="Remove um aluno da academia (soft delete)",
        tags=['students']
    ),
)
class StudentViewSet(TenantViewSet):
    """ViewSet para gestão completa de alunos"""
    
    @extend_schema(
        summary="Graduar aluno",
        description="Promove um aluno para uma nova faixa",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'new_belt': {'type': 'string', 'example': 'blue'},
                    'graduation_date': {'type': 'string', 'format': 'date', 'example': '2024-01-15'},
                    'notes': {'type': 'string', 'example': 'Excelente progresso técnico'}
                },
                'required': ['new_belt']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'student': {'$ref': '#/components/schemas/Student'}
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        tags=['students']
    )
    @action(detail=True, methods=['post'])
    def graduate(self, request, pk=None):
        # ... implementação
```

### Serializers com Documentação
```python
# apps/students/serializers.py
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    """Serializer completo para exibição de alunos"""
    
    full_name = serializers.SerializerMethodField()
    belt_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'email', 'full_name', 'phone', 
            'belt_color', 'belt_display', 'enrollment_date',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        """Nome completo do aluno"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    @extend_schema_field(serializers.CharField())
    def get_belt_display(self, obj):
        """Nome da faixa em português"""
        belt_names = {
            'white': 'Branca',
            'blue': 'Azul',
            'purple': 'Roxa',
            'brown': 'Marrom',
            'black': 'Preta'
        }
        return belt_names.get(obj.belt_color, obj.belt_color)

class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de alunos"""
    
    class Meta:
        model = Student
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'belt_color', 'enrollment_date', 'emergency_contact'
        ]
```

## Configuração de Desenvolvimento

### Instalação com UV
```bash
# Instalar UV (recomendado via pipx)
pipx install uv

# Criar ambiente virtual e instalar dependências
uv venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Instalar dependências do projeto
uv pip install -e .

# Comandos úteis
uv add django                    # Adicionar dependência
uv add --dev pytest            # Adicionar dependência de desenvolvimento
uv pip compile requirements.in  # Gerar lock file
uv pip sync requirements.txt    # Sincronizar ambiente
```

### Pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "wbjj-backend"
version = "1.0.0"
description = "Backend API para sistema de gestão de academias de jiu-jitsu"
authors = [{name = "wBJJ Team", email = "dev@wbjj.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    # Core Framework
    "Django>=4.2.0,<4.3.0",
    "djangorestframework>=3.14.0,<3.15.0",
    "drf-spectacular>=0.26.0",
    
    # Database & Storage
    "psycopg2-binary>=2.9.0",
    "redis>=5.0.0",
    "django-redis>=5.4.0",
    
    # Multitenancy
    "django-tenant-schemas>=1.11.0",
    
    # Authentication & Security
    "djangorestframework-simplejwt>=5.3.0",
    "django-cors-headers>=4.3.0",
    "django-permissions-policy>=4.18.0",
    "cryptography>=41.0.0",
    
    # APIs & Integrations
    "django-filter>=23.5",
    "djangorestframework-camel-case>=1.4.0",
    "django-extensions>=3.2.0",
    
    # Performance & Cache
    "django-cachalot>=2.6.0",
    "django-compression-middleware>=0.5.0",
    
    # Utilities
    "python-decouple>=3.8",
    "Pillow>=10.1.0",
    "celery>=5.3.0",
    
    # Monitoring & Logging
    "django-structlog>=7.0.0",
    "sentry-sdk[django]>=1.38.0",
    "django-health-check>=3.17.0",
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.4.0",
    "pytest-django>=4.7.0",
    "pytest-cov>=4.1.0",
    "factory-boy>=3.3.0",
    "freezegun>=1.2.0",
    
    # Code Quality
    "ruff>=0.1.0",
    "black>=23.0.0",
    "pre-commit>=3.5.0",
    "mypy>=1.7.0",
    "django-stubs>=4.2.0",
    
    # Development Tools
    "django-debug-toolbar>=4.2.0",
    "django-browser-reload>=1.12.0",
    "ipython>=8.16.0",
    "rich>=13.0.0",
]

prod = [
    "gunicorn>=21.2.0",
    "whitenoise>=6.6.0",
]

[project.urls]
Homepage = "https://github.com/wbjj/backend"
Documentation = "https://api.wbjj.com/docs/"
Repository = "https://github.com/wbjj/backend"

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "I", "N", "W", "B", "C4", "DJ"]
ignore = ["E501", "N806"]

[tool.ruff.per-file-ignores]
"*/migrations/*" = ["N806"]
"*/tests/*" = ["N806"]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.testing"
addopts = "--cov=apps --cov-report=html --cov-report=term-missing"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.11"
plugins = ["mypy_django_plugin.main"]
```

### Docker Setup
```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### Environment Variables
```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/wbjj_main
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,.wbjj.com
CORS_ALLOWED_ORIGINS=https://app.wbjj.com,https://admin.wbjj.com
```

## Testes

### Configuração de Testes
```python
# config/settings/testing.py
from .base import *

# Database para testes
DATABASES = {
    'default': {
        'ENGINE': 'django_tenant_schemas.postgresql_backend',
        'NAME': 'test_wbjj',
        'USER': 'test_user',
        'PASSWORD': 'test_pass',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_wbjj_test',
        }
    }
}

# Configurações específicas para testes
SECRET_KEY = 'test-secret-key-not-for-production'
DEBUG = True
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Mais rápido para testes
]

# Cache em memória para testes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Exemplo de teste
# apps/students/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django_tenant_schemas.test.cases import TenantTestCase
from apps.tenants.models import Tenant
from .models import Student

class StudentTestCase(TenantTestCase):
    def setUp(self):
        # Tenant será criado automaticamente pelo TenantTestCase
        self.user = get_user_model().objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_student(self):
        student = Student.objects.create(
            name='João Silva',
            email='joao@example.com',
            belt_color='white'
        )
        self.assertEqual(student.name, 'João Silva')
        self.assertEqual(student.belt_color, 'white')
    
    def test_student_graduation(self):
        student = Student.objects.create(
            name='Maria Santos',
            email='maria@example.com',
            belt_color='white'
        )
        
        # Testar graduação
        student.graduate('blue')
        self.assertEqual(student.belt_color, 'blue')
        self.assertIsNotNone(student.last_graduation_date)
```

## Deploy e Monitoramento

### Docker Compose Produção
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    build: 
      context: .
      dockerfile: docker/Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/wbjj_main
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=wbjj_main
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Scripts de Deploy
```bash
#!/bin/bash
# scripts/deploy.sh

echo "Starting deployment..."

# Build and push image
docker build -t wbjj-api:latest .
docker tag wbjj-api:latest registry.example.com/wbjj-api:latest
docker push registry.example.com/wbjj-api:latest

# Run migrations
docker run --rm --env-file .env wbjj-api:latest alembic upgrade head

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

echo "Deployment completed!"
```

## Performance e Monitoramento

### Configuração APM
```python
# app/main.py
from fastapi import FastAPI
import time
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="wBJJ API", version="1.0.0")

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Comandos Úteis do Projeto

### Desenvolvimento com UV
```bash
# Setup inicial do projeto
uv venv                        # Criar ambiente virtual
source .venv/bin/activate     # Ativar ambiente (Linux/Mac)
uv pip install -e .          # Instalar projeto em modo desenvolvimento

# Gerenciamento de dependências
uv add django-extensions      # Adicionar nova dependência
uv add --dev pytest-mock     # Adicionar dependência de desenvolvimento
uv pip sync pyproject.toml   # Sincronizar dependências

# Django
python manage.py migrate              # Aplicar migrations
python manage.py createsuperuser      # Criar superusuário
python manage.py collectstatic       # Coletar arquivos estáticos
python manage.py runserver           # Servidor de desenvolvimento

# Qualidade de código
ruff check .                  # Linting
ruff check . --fix           # Linting com correções automáticas
black .                      # Formatação de código
pytest                       # Executar testes
pytest --cov=apps           # Testes com cobertura

# Pre-commit hooks (qualidade automática)
pre-commit install           # Instalar hooks
pre-commit run --all-files  # Executar todos os hooks
pre-commit autoupdate       # Atualizar hooks

# Documentação
python manage.py spectacular --file schema.yml  # Gerar schema OpenAPI
```

### URLs Importantes
- **Admin Django**: http://localhost:8000/admin/
- **API Docs (Swagger)**: http://localhost:8000/api/docs/
- **API Docs (ReDoc)**: http://localhost:8000/api/redoc/
- **Health Check**: http://localhost:8000/health/

## Arquivo de Contexto para IA

### CONTEXT.md
Este projeto inclui um arquivo `backend/CONTEXT.md` que contém:

- ✅ **Stack tecnológico obrigatório** com versões fixadas
- ✅ **Padrões arquiteturais** e de código obrigatórios
- ✅ **Regras de multitenancy** críticas para segurança
- ✅ **Padrões de documentação** e testes
- ✅ **Configurações de deploy** e performance
- ✅ **Lista do que NUNCA fazer** vs **SEMPRE fazer**

**Como usar**: 
```bash
# Para trabalhar com IA no backend, sempre incluir:
cat backend/CONTEXT.md
# Copie e cole o conteúdo para o assistente de IA
```

> 🎯 **Importante**: Este arquivo garante que qualquer IA seguirá os padrões estabelecidos do projeto, evitando inconsistências e problemas de arquitetura.

## Tecnologia Atualizada: Django

**Decisão para MVP**: Django + Django Rest Framework
- ✅ **Produtividade máxima** para MVP
- ✅ **Django-tenant-schemas** para multitenancy
- ✅ **Admin interface** pronta
- ✅ **Ecosystem maduro** para todas funcionalidades

**Roadmap pós-MVP**: Migração para Golang
- Reescrita em Golang quando o produto estiver validado
- Foco em performance e escalabilidade
- Manutenção da mesma API contract

> 📋 **Tarefas detalhadas disponíveis em**: `doc/TASKS.md`  
> 🤖 **Contexto para IA disponível em**: `backend/CONTEXT.md` 