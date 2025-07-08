# CONTEXT.md - Backend wBJJ

Siga exatamente como está escrito. Não reformule. Não explique.
• Do not present guesses or speculation as fact.
• If not confirmed, say:
- "I cannot verify this."
- "I do not have access to that information."
• Label all uncertain or generated content:
- [Inference] = logically reasoned, not confirmed
- [Speculation] = unconfirmed possibility
- [Unverified] = no reliable source
• Do not chain inferences. Label each unverified step.
• Only quote real documents. No fake sources.
• If any part is unverified, label the entire output.
• Do not use these terms unless quoting or citing:
- Prevent, Guarantee, Will never, Fixes, Eliminates, Ensures
that
• For LLM behavior claims, include:
- [Unverified] or (Inferencel, plus a disclaimer that
behavior is not guaranteed
• If you break this rule, say:
> Correction: I made an unverified claim. That was incorrect.

## 📋 Visão Geral do Projeto

**Projeto**: wBJJ - Sistema de gestão para academias de jiu-jitsu
**Tipo**: API RESTful Django com multitenancy
**Objetivo**: MVP para validação rápida de mercado
**Arquitetura**: Monolito modular com isolamento por schema

## 🛠 Stack Tecnológico OBRIGATÓRIO

### Core Framework
- **Django 4.2.x LTS** (VERSÃO FIXADA - não atualizar minor versions sem aprovação)
- **Django Rest Framework 3.14.x**
- **Python 3.11** (versão LTS)
- **PostgreSQL 15** (principal) + **Redis** (cache/sessions)

### Gerenciamento de Dependências
- **UV** como gerenciador de pacotes (NÃO usar pip/poetry)
- **pyproject.toml** para configuração do projeto
- Sempre especificar versões com ranges compatíveis

### Libs OBRIGATÓRIAS - Sempre Usar
```python
# Multitenancy
django-tenant-schemas  # Schema-per-tenant

# API & Documentação
drf-spectacular       # OpenAPI/Swagger automático
django-filter         # Filtros avançados
djangorestframework-camel-case  # CamelCase para frontend

# Autenticação & Segurança
djangorestframework-simplejwt  # JWT tokens
django-cors-headers           # CORS
django-permissions-policy     # Security headers

# Performance & Cache
django-redis          # Cache Redis
django-cachalot      # ORM cache automático
django-compression-middleware  # Gzip responses

# Desenvolvimento & Qualidade
ruff                 # Linter (substitui flake8)
black               # Formatação
pre-commit          # Git hooks
pytest-django       # Testes
factory-boy         # Test factories

# Monitoramento
django-structlog    # Logs estruturados
sentry-sdk         # Error tracking
django-health-check # Health endpoints
```

## 🏗 Padrões de Arquitetura OBRIGATÓRIOS

### 1. Estrutura de Apps Django
```
backend/
├── config/         # Configurações Django (settings, urls, wsgi)
├── apps/
│   ├── core/           # Utilities compartilhadas (abstract models, permissions, etc)
│   ├── tenants/        # Modelo de tenant + middleware
│   ├── authentication/ # Auth customizada + JWT
│   ├── students/       # Gestão de alunos
│   ├── payments/       # Sistema financeiro
│   ├── notifications/  # Sistema de notificações
│   └── reports/        # Relatórios e analytics
```

### 2. Padrões de Código OBRIGATÓRIOS

#### Models
```python
# SEMPRE usar UUID como PK
class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # SEMPRE adicionar campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # SEMPRE soft delete
    is_active = models.BooleanField(default=True)
```

#### ViewSets
```python
# SEMPRE herdar de TenantViewSet (nunca ModelViewSet direto)
class StudentViewSet(TenantViewSet):
    # SEMPRE documentar com drf-spectacular
    @extend_schema(summary="...", tags=['students'])
    def list(self, request, *args, **kwargs):
        pass
```

#### Serializers
```python
# SEMPRE documentar campos computados
@extend_schema_field(serializers.CharField())
def get_computed_field(self, obj):
    """Documentação do campo"""
    return computed_value
```

### 3. Nomenclatura OBRIGATÓRIA

#### Arquivos
- `models.py` - Modelos Django
- `serializers.py` - Serializers DRF
- `views.py` - ViewSets DRF
- `filters.py` - Django-filter classes
- `permissions.py` - Permissões customizadas
- `services.py` - Lógica de negócio complexa
- `tasks.py` - Tasks Celery (futuro)

#### Variáveis e Funções
- **snake_case** para tudo (Python padrão)
- **UPPER_CASE** para constantes
- Nomes descritivos: `create_student_graduation()` não `create_grad()`

#### URLs
- **kebab-case** para endpoints: `/api/v1/student-graduations/`
- Sempre versionadas: `/api/v1/`
- Resources no plural: `/students/` não `/student/`

## 🔒 Regras de Multitenancy CRÍTICAS

### 1. NUNCA quebrar isolamento entre tenants
```python
# ❌ ERRADO - pode vazar dados entre tenants
Student.objects.all()

# ✅ CORRETO - usar TenantViewSet que já filtra por schema
class StudentViewSet(TenantViewSet):
    queryset = Student.objects.all()  # Seguro aqui pois schema já está configurado
```

### 2. SEMPRE validar tenant no middleware
```python
# O middleware TenantMiddleware DEVE ser o primeiro após SecurityMiddleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.authentication.middleware.TenantMiddleware',  # PRIMEIRO!
    # ... outros middlewares
]
```

### 3. SEMPRE usar schema-per-tenant
- 1 tenant = 1 PostgreSQL schema
- Isolamento total automático
- Migrations aplicadas em todos os schemas

## 📝 Padrões de Documentação OBRIGATÓRIOS

### 1. SEMPRE documentar ViewSets
```python
@extend_schema_view(
    list=extend_schema(summary="Listar alunos", tags=['students']),
    create=extend_schema(summary="Criar aluno", tags=['students']),
    # ... todos os métodos
)
class StudentViewSet(TenantViewSet):
    """ViewSet para gestão completa de alunos da academia"""
```

### 2. SEMPRE documentar APIs customizadas
```python
@extend_schema(
    summary="Graduar aluno",
    request=GraduationRequestSerializer,
    responses={200: StudentSerializer},
    tags=['students']
)
@action(detail=True, methods=['post'])
def graduate(self, request, pk=None):
    """Promove aluno para nova faixa com validações de negócio"""
```

### 3. URLs da documentação SEMPRE disponíveis
- `/api/docs/` - Swagger UI
- `/api/redoc/` - ReDoc
- `/api/schema/` - Schema OpenAPI raw

## 🧪 Padrões de Teste OBRIGATÓRIOS

### 1. SEMPRE usar TenantTestCase
```python
from django_tenant_schemas.test.cases import TenantTestCase

class StudentTestCase(TenantTestCase):
    def setUp(self):
        # Tenant criado automaticamente
        self.student = StudentFactory()  # Usar factories
```

### 2. SEMPRE usar factories ao invés de create manual
```python
# factory_boy para dados de teste consistentes
class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
```

### 3. Cobertura mínima: 80%
```bash
pytest --cov=apps --cov-report=html --cov-fail-under=80
```

## 🚀 Padrões de Deploy e Configuração

### 1. Settings modulares OBRIGATÓRIOS
```python
config/settings/
├── __init__.py
├── base.py       # Configurações compartilhadas
├── development.py # Dev local
├── testing.py    # Testes
└── production.py # Produção
```

### 2. Environment Variables
```python
# SEMPRE usar python-decouple
from decouple import config, Csv

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
```

### 3. Docker SEMPRE otimizado
```dockerfile
# Multi-stage build para produção
FROM python:3.11-slim as base
# ... configuração otimizada
```

## ⚡ Performance OBRIGATÓRIA

### 1. SEMPRE usar cache
```python
# django-cachalot para ORM cache automático
INSTALLED_APPS = ['cachalot']

# Redis para cache manual
from django.core.cache import cache
cache.set('key', value, timeout=300)
```

### 2. SEMPRE otimizar queries
```python
# ❌ ERRADO - N+1 queries
for student in Student.objects.all():
    print(student.payments.count())

# ✅ CORRETO - prefetch
students = Student.objects.prefetch_related('payments')
```

### 3. SEMPRE paginar listagens
```python
# Paginação automática no DRF
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## 🛡 Segurança OBRIGATÓRIA

### 1. SEMPRE validar inputs
```python
# Serializers com validação rigorosa
class StudentSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        # Validação customizada
        if not value.endswith('@allowed-domain.com'):
            raise serializers.ValidationError("Email não permitido")
        return value
```

### 2. SEMPRE usar permissions granulares
```python
class StudentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Validar se user pode acessar este student
        return obj.academy == request.user.academy
```

### 3. SEMPRE logs estruturados
```python
import structlog
logger = structlog.get_logger()

logger.info("Student created",
    student_id=student.id,
    academy_id=request.tenant.id,
    user_id=request.user.id
)
```

## 🚫 NUNCA FAZER

### Código
- ❌ Não usar `Student.objects.all()` fora de TenantViewSet
- ❌ Não misturar dados de tenants diferentes
- ❌ Não usar `print()` - sempre `logger`
- ❌ Não fazer queries no template/serializer
- ❌ Não usar `pk` em URLs - sempre UUID
- ❌ Não usar `id` autoincrement - sempre UUID

### Dependências
- ❌ Não instalar packages sem aprovação
- ❌ Não usar versões exatas sem range
- ❌ Não usar pip/poetry - sempre UV
- ❌ Não atualizar Django minor version sem teste completo

### Estrutura
- ❌ Não criar models fora de apps específicas
- ❌ Não colocar lógica de negócio em views
- ❌ Não usar FBV - sempre CBV (ViewSets)
- ❌ Não criar endpoints sem documentação

## ✅ SEMPRE FAZER

### Antes de cada commit
1. `ruff check .` - Linting
2. `black .` - Formatação
3. `pytest` - Testes
4. `python manage.py spectacular --file schema.yml` - Atualizar docs

### Ao criar nova funcionalidade
1. Model com UUID + auditoria + soft delete
2. Serializer com validação + documentação
3. ViewSet herdando TenantViewSet + permissões
4. Filters se necessário
5. Tests com factories
6. Documentação OpenAPI completa

### Ao fazer deploy
1. Migrations testadas em staging
2. Schema docs atualizadas
3. Health checks passando
4. Logs estruturados configurados

## 🎯 Objetivos de Performance

- **Latência**: < 200ms para 95% das requests
- **Throughput**: > 1000 req/s por instância
- **Cache hit rate**: > 80%
- **Test coverage**: > 80%
- **Documentation coverage**: 100% dos endpoints

## 📞 Escalação

**Dúvidas técnicas**: Revisar este documento primeiro
**Mudanças de arquitetura**: Discussão obrigatória com time
**Novas dependências**: Aprovação obrigatória
**Breaking changes**: Versionamento de API obrigatório

---

🎯 **Lembre-se**: Este é um MVP focado em **produtividade**. Evite over-engineering, mas mantenha qualidade e padrões para facilitar evolução futura.
