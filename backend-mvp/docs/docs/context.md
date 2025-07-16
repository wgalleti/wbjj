# CONTEXT.md - Backend wBJJ MVP

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

**Projeto**: wBJJ MVP - Sistema de gestão para academias de jiu-jitsu
**Tipo**: API RESTful Django com multitenancy simplificado
**Objetivo**: MVP para validação rápida de mercado
**Arquitetura**: Monolito modular com isolamento por tenant_id

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
backend-mvp/
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
class Student(BaseModel, TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # SEMPRE adicionar campos de auditoria (via BaseModel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # SEMPRE soft delete (via BaseModel)
    is_active = models.BooleanField(default=True)
    # SEMPRE tenant_id (via TenantMixin)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
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

## 🔒 Regras de Multitenancy MVP CRÍTICAS

### 1. SEMPRE usar TenantMixin em todos os models
```python
# ✅ CORRETO - model com isolamento por tenant_id
class Student(BaseModel, TenantMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # ... outros campos
```

### 2. SEMPRE herdar de TenantViewSet
```python
# ✅ CORRETO - ViewSet com filtro automático por tenant
class StudentViewSet(TenantViewSet):
    queryset = Student.objects.all()  # Filtrado automaticamente pelo TenantViewSet
    serializer_class = StudentSerializer
```

### 3. SEMPRE usar middleware TenantMiddleware
```python
# O middleware TenantMiddleware DEVE ser configurado
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.core.middleware.TenantMiddleware',  # Detecta tenant por subdomínio
    'apps.authentication.middleware.SecurityAuthorizationMiddleware',
    # ... outros middlewares
]
```

### 4. SEMPRE validar tenant no request
```python
# Middleware automaticamente adiciona request.tenant
def get_queryset(self):
    if not hasattr(self.request, 'tenant') or not self.request.tenant:
        return self.queryset.none()
    return self.queryset.filter(tenant=self.request.tenant)
```

### 5. Como funciona o isolamento MVP
- **Detecção**: Subdomínio (ex: `academia-alpha.wbjj.com` → tenant `academia-alpha`)
- **Filtro**: Todos os querysets filtrados por `tenant_id`
- **Criação**: Objetos criados automaticamente com `tenant=request.tenant`
- **Segurança**: Impossível acessar dados de outros tenants

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

### 1. SEMPRE usar estrutura without_db/with_db
```python
# tests/without_db/ - Testes rápidos sem banco
# tests/with_db/ - Testes completos com banco
```

### 2. SEMPRE usar factories ao invés de create manual
```python
# factory_boy para dados de teste consistentes
class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory)
    tenant = factory.SubFactory(TenantFactory)  # SEMPRE incluir tenant
    belt_color = 'white'
```

### 3. SEMPRE testar isolamento de tenant
```python
def test_tenant_isolation():
    tenant1 = TenantFactory()
    tenant2 = TenantFactory()

    student1 = StudentFactory(tenant=tenant1)
    student2 = StudentFactory(tenant=tenant2)

    # Simular request com tenant1
    request.tenant = tenant1

    # Deve retornar apenas student1
    queryset = StudentViewSet().get_queryset()
    assert student1 in queryset
    assert student2 not in queryset
```

### 4. Cobertura mínima: 80%
```bash
uv run pytest --cov=apps --cov-report=html --cov-fail-under=80
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
from apps.core.models import BaseModel, TenantMixin
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
    permission_classes: ClassVar = [TenantPermission]  # ✅ CORRETO
    search_fields: ClassVar = ["user__first_name", "user__email"]  # ✅ CORRETO
    filterset_fields: ClassVar = ["status", "belt_color"]  # ✅ CORRETO
    ordering_fields: ClassVar = ["user__first_name", "created_at"]  # ✅ CORRETO
    ordering: ClassVar = ["-created_at"]  # ✅ CORRETO
    filter_backends: ClassVar = [DjangoFilterBackend, SearchFilter]  # ✅ CORRETO
```

### 4. Métodos ViewSet SEMPRE Usar self.request
```python
class StudentViewSet(TenantViewSet):
    def perform_create(self, serializer):
        """SEMPRE usar self.request, nunca request direto"""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            raise ValidationError("Tenant é obrigatório")

        serializer.save(tenant=self.request.tenant)  # ✅ CORRETO

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
    list_display: ClassVar = ['user__first_name', 'user__email', 'belt_color']  # ✅ CORRETO
    list_filter: ClassVar = ['belt_color', 'status']  # ✅ CORRETO
    search_fields: ClassVar = ['user__first_name', 'user__email']  # ✅ CORRETO
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
- SEMPRE implementar TenantMixin em models
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
from apps.core.models import BaseModel, TenantMixin

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
uv run pytest

# 5. Verificação Django
uv run manage.py check

# 6. Verificação de schema OpenAPI
uv run manage.py spectacular --file=/dev/null
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

#### Configuração Completa - `.pre-commit-config.yaml`
```yaml
# .pre-commit-config.yaml - CONFIGURAÇÃO OBRIGATÓRIA
repos:
  # Ruff - Linter extremamente rápido para Python
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        files: ^backend-mvp/.*\.py$
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
        files: ^backend-mvp/.*\.py$

  # Hooks básicos de qualidade - OBRIGATÓRIOS
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
        files: ^backend-mvp/.*\.(py|yaml|yml|json|toml|md)$
      - id: end-of-file-fixer
        files: ^backend-mvp/.*\.(py|yaml|yml|json|toml|md)$
      - id: check-yaml
        files: ^backend-mvp/.*\.ya?ml$
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
        files: ^backend-mvp/.*$
      - id: debug-statements
        files: ^backend-mvp/.*\.py$

  # Django específico - OBRIGATÓRIO
  - repo: local
    hooks:
      - id: django-check
        name: Django Check
        entry: bash -c 'cd backend-mvp && python manage.py check'
        language: system
        pass_filenames: false
        files: ^backend-mvp/.*\.py$

      - id: django-migrations-check
        name: Django Migrations Check
        entry: bash -c 'cd backend-mvp && python manage.py makemigrations --check --dry-run'
        language: system
        pass_filenames: false
        files: ^backend-mvp/.*\.py$

  # Segurança - Bandit OBRIGATÓRIO
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-r", "backend-mvp/apps/", "-f", "json", "--skip", "B101,B601"]
        files: ^backend-mvp/apps/.*\.py$
        exclude: ^backend-mvp/.*/migrations/.*\.py$
        pass_filenames: false
```

#### Regras de Formatação OBRIGATÓRIAS

**1. Ruff - Linting e Formatação**
- ✅ **SEMPRE** usar `ruff` como linter principal
- ✅ **SEMPRE** aplicar correções automáticas com `--fix`
- ✅ **SEMPRE** usar `ruff-format` para formatação
- ❌ **NUNCA** usar Black simultaneamente (conflito de formatação)

**2. Qualidade de Arquivo - OBRIGATÓRIO**
- ✅ **SEMPRE** remover espaços em branco no final das linhas (`trailing-whitespace`)
- ✅ **SEMPRE** garantir nova linha no final dos arquivos (`end-of-file-fixer`)
- ✅ **SEMPRE** validar sintaxe YAML (`check-yaml`)
- ✅ **SEMPRE** verificar conflitos de merge (`check-merge-conflict`)
- ❌ **NUNCA** deixar `print()` ou `pdb.set_trace()` no código (`debug-statements`)
- ❌ **NUNCA** fazer commit de arquivos > 1MB (`check-added-large-files`)

**3. Django - Validações OBRIGATÓRIAS**
- ✅ **SEMPRE** executar `python manage.py check` antes do commit
- ✅ **SEMPRE** verificar migrations pendentes com `--check --dry-run`
- ❌ **NUNCA** fazer commit com `manage.py check` falhando
- ❌ **NUNCA** fazer commit com migrations não criadas

**4. Segurança - Bandit OBRIGATÓRIO**
- ✅ **SEMPRE** executar análise de segurança com Bandit
- ✅ **SEMPRE** corrigir vulnerabilidades encontradas
- ❌ **NUNCA** ignorar alertas de segurança sem justificativa
- ❌ **NUNCA** fazer commit com vulnerabilidades críticas

#### Tipos de Arquivo Cobertos
```
Python:     *.py (linting, formatação, segurança)
YAML:       *.yaml, *.yml (validação de sintaxe)
JSON:       *.json (formatação)
TOML:       *.toml (formatação)
Markdown:   *.md (espaços, nova linha)
```

#### Exclusões Automáticas
```
Migrations:    backend-mvp/*/migrations/*.py (excluídas do Bandit)
Cache/Build:   __pycache__/, .git/, .venv/ (ignoradas)
```

### 11. Aplicação Prática das Regras de Formatação

#### Comandos de Verificação OBRIGATÓRIOS
```bash
# 1. Verificação completa antes do commit
pre-commit run --all-files

# 2. Verificação específica por ferramenta
ruff check backend-mvp/                    # Linting
ruff format backend-mvp/                   # Formatação
bandit -r backend-mvp/apps/               # Segurança
python backend-mvp/manage.py check        # Django

# 3. Verificação de qualidade de arquivo
pre-commit run trailing-whitespace --all-files
pre-commit run end-of-file-fixer --all-files
pre-commit run check-yaml --all-files

# 4. Verificação de migrations
cd backend-mvp && python manage.py makemigrations --check --dry-run
```

#### Workflow de Desenvolvimento com Pre-commit
```bash
# Setup inicial (uma vez por projeto)
pre-commit install               # Instalar hooks
pre-commit install --hook-type pre-push  # Hook de push

# Desenvolvimento diário
git add .                       # Adicionar arquivos
git commit -m "feat: nova funcionalidade"  # Commit automático executa hooks

# Se hooks falharem, corrigir e tentar novamente
git add .                       # Adicionar correções
git commit -m "feat: nova funcionalidade"  # Tentar commit novamente
```

#### Correções Automáticas vs Manuais

**Correções Automáticas (ruff --fix):**
- ✅ Import sorting (isort)
- ✅ Unused imports removal
- ✅ Code formatting
- ✅ Trailing whitespace removal
- ✅ End-of-file newline addition

**Correções Manuais Necessárias:**
- ❌ Exception chaining (`raise ... from err`)
- ❌ Unused variables (renomear para `_`)
- ❌ Security vulnerabilities (Bandit)
- ❌ Django check errors
- ❌ Missing migrations

#### Tratamento de Erros Comuns

**1. Ruff Errors (B904, F841, etc.)**
```bash
# Ver detalhes do erro
ruff check backend-mvp/apps/authentication/serializers.py --show-fixes

# Aplicar correções automáticas
ruff check backend-mvp/apps/authentication/serializers.py --fix

# Verificar resultado
ruff check backend-mvp/apps/authentication/serializers.py
```

**2. Django Check Failures**
```bash
# Verificar problemas
python backend-mvp/manage.py check --deploy

# Corrigir configurações
python backend-mvp/manage.py check --tag security

# Validar migrations
python backend-mvp/manage.py makemigrations --check
```

**3. Bandit Security Issues**
```bash
# Ver relatório detalhado
bandit -r backend-mvp/apps/ -f json -o security-report.json

# Verificar específicos
bandit -r backend-mvp/apps/authentication/ -ll

# Skip falsos positivos (cuidadosamente)
bandit -r backend-mvp/apps/ --skip B101,B601
```

**4. File Quality Issues**
```bash
# Trailing whitespace
find backend-mvp/ -name "*.py" -exec sed -i 's/[[:space:]]*$//' {} \;

# Missing newlines
find backend-mvp/ -name "*.py" -exec sh -c 'echo >> "$1"' _ {} \;

# Debug statements
grep -r "print\|pdb\.set_trace" backend-mvp/apps/
```

#### Integração com IDE/Editor

**VS Code - settings.json**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll.ruff": true
  }
}
```

**PyCharm - Configuração**
```
File → Settings → Tools → External Tools → Add
Name: Ruff Check
Program: ruff
Arguments: check $FileDir$
Working Directory: $ProjectFileDir$
```

#### Bypass de Emergência (USO RESTRITO)
```bash
# APENAS em emergências - pular hooks específicos
SKIP=bandit git commit -m "emergency fix"

# APENAS para correções urgentes - pular todos os hooks
git commit -m "hotfix" --no-verify

# NUNCA fazer isso em produção ou para features normais
```

### 12. NUNCA Fazer - Erros Comuns
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

# ❌ ERRADO - Model sem TenantMixin
class Student(BaseModel):  # ❌ Falta TenantMixin
    name = models.CharField(max_length=100)

# ❌ ERRADO - ViewSet sem herdar de TenantViewSet
class StudentViewSet(ModelViewSet):  # ❌ Deve herdar de TenantViewSet
    queryset = Student.objects.all()
```

### 13. Setup Inicial OBRIGATÓRIO para Qualidade
```bash
# 1. Instalar pre-commit no projeto
uv add --dev pre-commit

# 2. Instalar hooks (executar uma vez)
pre-commit install

# 3. Executar em todos os arquivos (primeira vez)
pre-commit run --all-files

# 4. Testar pipeline completo
ruff check . && ruff format . && uv run manage.py check && uv run pytest
```

### 14. Template Padrão para Novos Arquivos
```python
"""
[Nome do módulo] para [funcionalidade]

Seguindo padrões estabelecidos no CONTEXT.md:
- SEMPRE herdar de TenantViewSet/BaseModelSerializer
- SEMPRE usar TenantMixin em models
- SEMPRE documentar com drf-spectacular
- SEMPRE usar typing adequado
"""
from typing import ClassVar

from django.db import models
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.models import BaseModel, TenantMixin
from apps.core.serializers import BaseModelSerializer


# Implementação segue padrões do CONTEXT.md
```

### 15. Checklist Rápido de Qualidade ✅
```markdown
## Antes de fazer commit, verificar:

### Pre-commit Hooks - OBRIGATÓRIO
- [ ] `pre-commit run --all-files` = PASSA
- [ ] Todos os hooks configurados em `.pre-commit-config.yaml`
- [ ] Sem bypass de hooks (`--no-verify`) sem justificativa

### Formatação e Linting - OBRIGATÓRIO
- [ ] `ruff check backend-mvp/` = 0 erros
- [ ] `ruff format backend-mvp/` executado
- [ ] Sem `print()` ou `pdb.set_trace()` (`debug-statements`)
- [ ] Sem espaços em branco no final das linhas (`trailing-whitespace`)
- [ ] Nova linha no final de todos os arquivos (`end-of-file-fixer`)

### Qualidade de Arquivo - OBRIGATÓRIO
- [ ] Arquivos YAML válidos (`check-yaml`)
- [ ] Sem conflitos de merge não resolvidos (`check-merge-conflict`)
- [ ] Sem arquivos > 1MB (`check-added-large-files`)
- [ ] Sem vulnerabilidades críticas Bandit

### Django - OBRIGATÓRIO
- [ ] `python manage.py check` = OK
- [ ] `python manage.py makemigrations --check --dry-run` = OK
- [ ] Sem migrations pendentes
- [ ] `python manage.py spectacular --file=/dev/null` = OK

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
- [ ] Herda de `TenantViewSet` (nunca `ModelViewSet`)
- [ ] `permission_classes: ClassVar = [...]`
- [ ] `search_fields: ClassVar = [...]`
- [ ] `filterset_fields: ClassVar = [...]`
- [ ] `ordering_fields: ClassVar = [...]`
- [ ] `ordering: ClassVar = [...]`
- [ ] `filter_backends: ClassVar = [...]`
- [ ] `self.request.user` (não `request.user`)

### Models
- [ ] Herda de `BaseModel` e `TenantMixin`
- [ ] UUID como primary key
- [ ] Campos de auditoria (created_at, updated_at)
- [ ] Soft delete (is_active)
- [ ] Relacionamento com tenant

### Django Admin
- [ ] `list_display: ClassVar = [...]`
- [ ] `list_filter: ClassVar = [...]`
- [ ] `search_fields: ClassVar = [...]`

### Código Geral
- [ ] Variáveis não usadas com `_`
- [ ] Unpacking ao invés de concatenação: `[*list1, item]`
- [ ] Exception chaining correto (`raise ... from err`)
- [ ] Sem `print()` - usar `logger`

### Testes e Cobertura
- [ ] `uv run pytest tests/without_db/` = PASSA
- [ ] `uv run pytest tests/with_db/ --cov=apps` = PASSA
- [ ] Cobertura de código > 80%
- [ ] Testes específicos para mudanças implementadas
- [ ] Factories incluem tenant

### Segurança
- [ ] `bandit -r backend-mvp/apps/` = sem vulnerabilidades críticas
- [ ] Sem credenciais hardcoded
- [ ] Sem informações sensíveis em logs
- [ ] Validação adequada de inputs

### Multitenancy MVP
- [ ] Todos os models usam `TenantMixin`
- [ ] Todos os ViewSets herdam de `TenantViewSet`
- [ ] Middleware `TenantMiddleware` configurado
- [ ] Testes validam isolamento de tenant

### Comando Final de Verificação
```bash
# Executar ANTES de cada commit
pre-commit run --all-files && \
cd backend-mvp && \
python manage.py check && \
python manage.py makemigrations --check --dry-run && \
python manage.py spectacular --file=/dev/null && \
cd .. && \
uv run pytest tests/without_db/ && \
echo "✅ PRONTO PARA COMMIT"
```
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
    print(student.user.full_name)

# ✅ CORRETO - select_related
students = Student.objects.select_related('user')
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
        return obj.tenant == request.tenant
```

### 3. SEMPRE logs estruturados
```python
import structlog
logger = structlog.get_logger()

logger.info("Student created",
    student_id=student.id,
    tenant_id=request.tenant.id,
    user_id=request.user.id
)
```

## 🚫 NUNCA FAZER

### Código
- ❌ Não usar `Student.objects.all()` sem filtro por tenant
- ❌ Não criar models sem `TenantMixin`
- ❌ Não usar `print()` - sempre `logger`
- ❌ Não fazer queries no template/serializer
- ❌ Não usar `pk` em URLs - sempre UUID
- ❌ Não usar `id` autoincrement - sempre UUID
- ❌ Não herdar de `ModelViewSet` - sempre `TenantViewSet`

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
- ❌ Não quebrar isolamento de tenant

## ✅ SEMPRE FAZER

### Antes de cada commit
1. `ruff check .` - Linting (OBRIGATÓRIO - deve passar 100%)
2. `ruff format .` - Formatação automática
3. `uv run pytest` - Testes (cobertura > 80%)
4. `uv run manage.py check` - Verificação Django
5. `uv run manage.py spectacular --file=/dev/null` - Validar OpenAPI

### Ao criar nova funcionalidade
1. Model com `BaseModel` + `TenantMixin` + UUID + auditoria + soft delete
2. Serializer com validação + documentação
3. ViewSet herdando `TenantViewSet` + permissões
4. Filters se necessário
5. Tests com factories (incluindo tenant)
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

## 🧪 Sistema de Testes

Para documentação completa sobre testes, consulte o [Sistema de Testes](testing.md) dedicado que inclui:

- **Estrutura de Testes**: Organização `with_db/` vs `without_db/`
- **Scripts de Teste**: Comandos para execução rápida e completa
- **Banco de Dados**: Criação, reset e configuração
- **Factories e Fixtures**: Padrões com Factory Boy (incluindo tenant)
- **Debugging**: Comandos para troubleshooting
- **Coverage**: Relatórios e metas de cobertura
- **CI/CD**: Integração com GitHub Actions

### Comandos Essenciais de Teste

```bash
# Testes rápidos (sem banco) - ~10-30 segundos
./scripts/test-without-db.sh

# Testes completos (com banco) - ~2-5 minutos
./scripts/test-with-db.sh

# Cobertura de código
uv run pytest --cov=apps --cov-report=html
```

**Meta de Cobertura**: Mínimo 80% | **Documentação Completa**: [testing.md](testing.md)

## 🔧 Scripts de Desenvolvimento

### Scripts Essenciais

```bash
# Setup completo do ambiente
./scripts/dev-setup.sh            # Setup inicial (recomendado)
./scripts/dev-setup.sh --clean    # Setup com limpeza total

# Testes
./scripts/test-without-db.sh      # Testes rápidos (~10-30s)
./scripts/test-with-db.sh         # Testes completos (~2-5min)

# Documentação
./scripts/serve-docs.sh           # Servidor docs (http://127.0.0.1:8001)
./scripts/test-docs-build.sh      # Validar build da docs

# Validação
./scripts/test-commands.sh        # Verificar comandos Django
```

### Comandos Django Essenciais

```bash
# Desenvolvimento
uv run manage.py wait_for_db      # Aguardar banco
uv run manage.py migrate          # Aplicar migrations
uv run manage.py seed_data        # Popular dados de desenvolvimento
uv run manage.py runserver        # Executar servidor

# Validação
uv run manage.py check            # Verificar sistema
uv run manage.py spectacular --file=/dev/null  # Validar OpenAPI

# Testes
uv run pytest tests/without_db/   # Testes rápidos
uv run pytest tests/with_db/ --cov=apps  # Testes com cobertura
```

### Workflow de Desenvolvimento

1. **Setup inicial**: `./scripts/dev-setup.sh`
2. **Desenvolvimento diário**: `./scripts/test-without-db.sh`
3. **Antes do commit**: `./scripts/test-with-db.sh`
4. **Troubleshooting**: `./scripts/dev-setup.sh --clean`

**Documentação Completa**: [testing.md](testing.md#scripts-de-desenvolvimento-obrigatórios)

## 📞 Escalação

**Dúvidas técnicas**: Revisar este documento primeiro
**Mudanças de arquitetura**: Discussão obrigatória com time
**Novas dependências**: Aprovação obrigatória
**Breaking changes**: Versionamento de API obrigatório

---

🎯 **Lembre-se**: Este é um MVP focado em **produtividade** com multitenancy simplificado por `tenant_id`. Evite over-engineering, mas mantenha qualidade e padrões para facilitar evolução futura.

**Diferenças do MVP vs Versão Completa:**
- ✅ MVP: Filtro por `tenant_id` (simples e rápido)
- 🔄 V2.0: Schema-per-tenant (isolamento total)
- ✅ MVP: Detecção por subdomínio
- 🔄 V2.0: Domínios customizados
- ✅ MVP: Middleware de filtro
- 🔄 V2.0: Middleware de schema switching
