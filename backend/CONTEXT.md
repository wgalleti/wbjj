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

## 📏 Padrões de Qualidade de Código OBRIGATÓRIOS

### 1. Estrutura de Imports SEMPRE Seguir Esta Ordem
```python
"""
Docstring do módulo
"""
# 1. Standard library imports
from datetime import timedelta
from typing import ClassVar
import uuid

# 2. Third-party imports
from django.contrib.auth import authenticate
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

# 3. Local application imports
from apps.core.models import BaseModel
from .models import Student
```

### 2. Serializers SEMPRE Anotar Atributos de Classe
```python
from typing import ClassVar

class StudentSerializer(serializers.ModelSerializer):
    """Serializer para alunos"""

    # SEMPRE usar ClassVar para atributos mutáveis de classe
    class Meta:
        model = Student
        fields: ClassVar = ["id", "name", "email"]  # ✅ CORRETO
        read_only_fields: ClassVar = ["id", "created_at"]  # ✅ CORRETO
        extra_kwargs: ClassVar = {  # ✅ CORRETO
            "email": {"help_text": "Email único"}
        }
```

### 3. ViewSets SEMPRE Anotar Atributos de Configuração
```python
from typing import ClassVar

class StudentViewSet(TenantViewSet):
    """ViewSet para gestão de alunos"""

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # SEMPRE usar ClassVar para listas/dicts de configuração
    permission_classes: ClassVar = [IsAuthenticated]  # ✅ CORRETO
    search_fields: ClassVar = ["name", "email"]  # ✅ CORRETO
    filterset_fields: ClassVar = ["status", "belt_color"]  # ✅ CORRETO
    ordering_fields: ClassVar = ["name", "created_at"]  # ✅ CORRETO
    ordering: ClassVar = ["-created_at"]  # ✅ CORRETO
    filter_backends: ClassVar = [DjangoFilterBackend, SearchFilter]  # ✅ CORRETO
```

### 4. Métodos ViewSet SEMPRE Usar self.request
```python
class StudentViewSet(TenantViewSet):
    def perform_create(self, serializer):
        """SEMPRE usar self.request, nunca request direto"""
        instructor = (
            User.objects.get(id=instructor_id)
            if instructor_id
            else self.request.user  # ✅ CORRETO
        )
        serializer.save(instructor=instructor)

    @action(detail=False, methods=['post'])
    def custom_action(self, request):
        """Em @action, usar request é correto"""
        user = request.user  # ✅ CORRETO (context de @action)
        return Response({"user": user.id})
```

### 5. Loops e Unpacking SEMPRE Otimizar
```python
# ❌ ERRADO - Variável não usada
for (path, method, callback) in endpoints:
    process_callback(callback)

# ✅ CORRETO - Usar underscore para não usadas
for (path, _, callback) in endpoints:
    process_callback(callback)

# ❌ ERRADO - Concatenação de listas
search_fields = getattr(cls, 'search_fields', []) + ['name']

# ✅ CORRETO - Unpacking de iteráveis
search_fields = [*getattr(cls, 'search_fields', []), 'name']
```

### 6. Django Admin SEMPRE Anotar Configurações
```python
from typing import ClassVar

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin para alunos"""

    # SEMPRE usar ClassVar para configurações do admin
    list_display: ClassVar = ['name', 'email', 'belt_color']  # ✅ CORRETO
    list_filter: ClassVar = ['belt_color', 'status']  # ✅ CORRETO
    search_fields: ClassVar = ['name', 'email']  # ✅ CORRETO
    readonly_fields: ClassVar = ['id', 'created_at']  # ✅ CORRETO
```

### 7. SEMPRE Estruturar Arquivos Python
```python
"""
Descrição do módulo

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE documentar funcionalidades
- SEMPRE seguir nomenclatura estabelecida
- SEMPRE usar typing adequado
"""
# 1. Imports typing PRIMEIRO quando necessário
from typing import ClassVar

# 2. Imports standard library
from datetime import datetime
import uuid

# 3. Imports third-party
from django.db import models
from rest_framework import serializers

# 4. Imports locais
from apps.core.models import BaseModel

# 5. Código do módulo
```

### 8. Verificação de Qualidade ANTES de Commit
```bash
# SEMPRE executar ANTES de fazer commit:

# 1. Verificação de lint
ruff check .

# 2. Formatação automática
ruff format .

# 3. Verificação de tipos (se usando mypy)
mypy apps/

# 4. Testes
pytest

# 5. Verificação Django
python manage.py check

# 6. Verificação de schema OpenAPI
python manage.py spectacular --file=/dev/null
```

### 9. Configuração Ruff OBRIGATÓRIA No pyproject.toml
```toml
[tool.ruff]
target-version = "py311"
line-length = 88
exclude = [
    "migrations",
    "__pycache__",
    ".git",
    ".venv",
]

[tool.ruff.lint]
# REGRAS OBRIGATÓRIAS - NÃO ALTERAR SEM APROVAÇÃO
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "RUF",  # Ruff-specific rules (RUF012 para ClassVar)
]

# NUNCA ignorar essas regras críticas
ignore = []

[tool.ruff.lint.per-file-ignores]
"migrations/*.py" = ["E501", "RUF012"]  # Migrations podem ter linha longa
"__init__.py" = ["F401"]  # Init files podem ter imports não usados

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.ruff.lint.isort]
known-first-party = ["apps", "config"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["fastapi.Depends"]
```

### 10. Pre-commit Hooks OBRIGATÓRIOS
```yaml
# .pre-commit-config.yaml - SEMPRE configurar
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: django-check
        name: Django Check
        entry: python manage.py check
        language: system
        pass_filenames: false

      - id: openapi-check
        name: OpenAPI Schema Check
        entry: python manage.py spectacular --file=/dev/null
        language: system
        pass_filenames: false
```

### 11. NUNCA Fazer - Erros Comuns
```python
# ❌ ERRADO - Request sem self em métodos de ViewSet
def perform_create(self, serializer):
    serializer.save(user=request.user)  # ❌ request undefined

# ❌ ERRADO - Imports no meio do arquivo
SECRET_KEY = "..."
from datetime import timedelta  # ❌ Import deve estar no topo

# ❌ ERRADO - Atributos de classe sem ClassVar
class Meta:
    fields = ["id", "name"]  # ❌ Deve ser fields: ClassVar

# ❌ ERRADO - Variável de loop não usada sem underscore
for (name, value, extra) in items:  # ❌ extra não é usado
    process(name, value)

# ❌ ERRADO - Concatenação desnecessária
items = list1 + ["new_item"]  # ❌ Usar unpacking
```

### 12. Setup Inicial OBRIGATÓRIO para Qualidade
```bash
# 1. Instalar pre-commit no projeto
uv add --dev pre-commit

# 2. Instalar hooks (executar uma vez)
pre-commit install

# 3. Executar em todos os arquivos (primeira vez)
pre-commit run --all-files

# 4. Testar pipeline completo
ruff check . && ruff format . && python manage.py check && pytest
```

### 13. Template Padrão para Novos Arquivos
```python
"""
[Nome do módulo] para [funcionalidade]

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet/BaseModelSerializer
- SEMPRE documentar com drf-spectacular
- SEMPRE usar typing adequado
"""
from typing import ClassVar

from django.db import models
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.models import BaseModel
from apps.core.serializers import BaseModelSerializer


# Implementação segue padrões do CONTEXT.md
```

### 14. Checklist Rápido de Qualidade ✅
```markdown
## Antes de fazer commit, verificar:

### Imports e Estrutura
- [ ] `from typing import ClassVar` quando necessário
- [ ] Imports organizados: standard → third-party → local
- [ ] Docstring no topo do arquivo
- [ ] Sem imports no meio do código

### Serializers
- [ ] `fields: ClassVar = [...]`
- [ ] `read_only_fields: ClassVar = [...]`
- [ ] `extra_kwargs: ClassVar = {...}`

### ViewSets
- [ ] `permission_classes: ClassVar = [...]`
- [ ] `search_fields: ClassVar = [...]`
- [ ] `filterset_fields: ClassVar = [...]`
- [ ] `ordering_fields: ClassVar = [...]`
- [ ] `ordering: ClassVar = [...]`
- [ ] `filter_backends: ClassVar = [...]`
- [ ] `self.request.user` (não `request.user`)

### Django Admin
- [ ] `list_display: ClassVar = [...]`
- [ ] `list_filter: ClassVar = [...]`
- [ ] `search_fields: ClassVar = [...]`

### Código Geral
- [ ] Variáveis não usadas com `_`
- [ ] Unpacking ao invés de concatenação: `[*list1, item]`
- [ ] Sem `print()` - usar `logger`

### Pipeline de Qualidade
- [ ] `ruff check .` = 0 erros
- [ ] `ruff format .` executado
- [ ] `python manage.py check` = OK
- [ ] `python manage.py spectacular --file=/dev/null` = OK
- [ ] `pytest` passa com cobertura > 80%
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
1. `ruff check .` - Linting (OBRIGATÓRIO - deve passar 100%)
2. `ruff format .` - Formatação automática
3. `pytest` - Testes (cobertura > 80%)
4. `python manage.py check` - Verificação Django
5. `python manage.py spectacular --file=/dev/null` - Validar OpenAPI

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
