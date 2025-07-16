# Backend - wBJJ API

## Visão Geral
O projeto wBJJ possui duas implementações de backend para diferentes estratégias de multitenancy:

- **`backend-mvp/`** - Implementação MVP simplificada (ATIVO)
- **`backend/`** - Implementação com django-tenants (REFERÊNCIA)

## Estrutura Dual do Projeto

### Backend MVP (`backend-mvp/`) - ATIVO
**Estratégia**: Tenant por filtro de dados (tenant_id)
```
backend-mvp/
├── apps/
│   ├── tenants/           # Modelo Tenant simples
│   ├── authentication/    # User com tenant_id
│   ├── students/          # Student com tenant_id
│   ├── payments/          # Payment com tenant_id
│   └── core/              # TenantMixin e utilities
├── config/
├── docker-compose.yml
├── requirements.txt       # Sem django-tenants
└── manage.py
```

### Backend Original (`backend/`) - REFERÊNCIA
**Estratégia**: Tenant por schemas separados
```
backend/
├── apps/
│   ├── tenants/           # Modelo com TenantMixin
│   ├── authentication/    # User sem tenant_id
│   ├── students/          # Student sem tenant_id
│   ├── payments/          # Payment sem tenant_id
│   └── core/              # Utilities django-tenants
├── config/
├── docker-compose.yml
├── requirements.txt       # Com django-tenants
└── manage.py
```

## Decisão Tecnológica

### Backend MVP (Escolhido para Desenvolvimento)
**Justificativa**: Máxima produtividade para validação de mercado
- ✅ **Velocidade**: Desenvolvimento extremamente rápido
- ✅ **Simplicidade**: Implementação direta com tenant_id
- ✅ **Facilidade**: Testes e debug mais simples
- ✅ **Produtividade**: Menos complexidade inicial
- ✅ **Adequado**: Performance suficiente para MVP

### Backend Original (Preservado como Referência)
**Características**: Implementação completa com isolamento total
- ✅ **Isolamento**: Schemas separados por tenant
- ✅ **Escalabilidade**: Suporte a milhares de tenants
- ✅ **Segurança**: Impossibilidade de vazamento
- ✅ **Performance**: Otimizada para grandes volumes
- ✅ **Rollback**: Disponível se necessário

## Implementação MVP Detalhada

### Stack Tecnológico MVP
```python
# backend/requirements.txt
Django==4.2.7
djangorestframework==3.14.0
drf-spectacular==0.26.5
psycopg2-binary==2.9.7
redis==5.0.1
django-redis==5.4.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
django-filter==23.3
python-decouple==3.8
gunicorn==21.2.0
# Nota: SEM django-tenants
```

### Modelo Tenant Simplificado
```python
# backend-mvp/apps/tenants/models.py
from django.db import models
from apps.core.models import BaseModel

class Tenant(BaseModel):
    """Modelo de tenant MVP - tabela única"""
    name = models.CharField(max_length=255, verbose_name="Nome da Academia")
    subdomain = models.CharField(max_length=100, unique=True, verbose_name="Subdomínio")

    # Campos de configuração
    contact_email = models.EmailField(blank=True, verbose_name="Email de Contato")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    address = models.TextField(blank=True, verbose_name="Endereço")

    # Customização visual
    logo_url = models.URLField(blank=True, verbose_name="URL do Logo")
    primary_color = models.CharField(max_length=7, default='#3B82F6', verbose_name="Cor Primária")
    secondary_color = models.CharField(max_length=7, default='#1E40AF', verbose_name="Cor Secundária")

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = 'tenants'
        verbose_name = "Academia"
        verbose_name_plural = "Academias"

    def __str__(self):
        return self.name
```

### TenantMixin Base
```python
# backend-mvp/apps/core/models.py
from django.db import models
import uuid

class BaseModel(models.Model):
    """Modelo base para todos os models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class TenantMixin(BaseModel):
    """Mixin para models que pertencem a um tenant"""
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        verbose_name="Academia"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Validação obrigatória de tenant
        if not self.tenant_id:
            raise ValueError("Tenant é obrigatório para este modelo")
        super().save(*args, **kwargs)
```

### Middleware MVP
```python
# backend-mvp/apps/core/middleware.py
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from apps.tenants.models import Tenant
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    """
    Middleware MVP para detectar tenant via subdomínio
    Não altera schema - apenas adiciona tenant ao request
    """

    def process_request(self, request):
        # Extrair subdomínio
        hostname = request.get_host().split(':')[0]
        subdomain = hostname.split('.')[0]

        # Pular para domínios principais
        main_domains = ['www', 'admin', 'api', 'localhost', '127']
        if subdomain in main_domains or subdomain.startswith('127'):
            request.tenant = None
            return None

        # Buscar tenant no cache primeiro
        cache_key = f"tenant:subdomain:{subdomain}"
        tenant = cache.get(cache_key)

        if tenant is None:
            try:
                tenant = Tenant.objects.select_related().get(
                    subdomain=subdomain,
                    is_active=True
                )
                # Cache por 1 hora
                cache.set(cache_key, tenant, 3600)

            except Tenant.DoesNotExist:
                logger.warning(f"Tenant não encontrado: {subdomain}")
                raise Http404("Academia não encontrada")
            except Exception as e:
                logger.error(f"Erro no middleware de tenant: {e}")
                raise Http404("Erro interno")

        # Adicionar tenant ao request
        request.tenant = tenant
        request.tenant_id = tenant.id

        return None
```

### ViewSet Base com Filtro Automático
```python
# backend-mvp/apps/core/viewsets.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import models

class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet base que automaticamente filtra por tenant
    Todos os ViewSets devem herdar desta classe
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtra queryset pelo tenant atual"""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return self.queryset.none()

        # Filtro automático por tenant
        return self.queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        """Adiciona tenant automaticamente na criação"""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            raise ValidationError("Tenant não identificado")

        serializer.save(tenant=self.request.tenant)

    def perform_update(self, serializer):
        """Garante que tenant não pode ser alterado"""
        # Remove tenant dos dados se enviado
        if 'tenant' in serializer.validated_data:
            serializer.validated_data.pop('tenant')

        serializer.save()

    def list(self, request, *args, **kwargs):
        """Override para adicionar informações de tenant se necessário"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

### Exemplo de Model com TenantMixin
```python
# backend-mvp/apps/students/models.py
from django.db import models
from apps.core.models import TenantMixin

class Student(TenantMixin):
    """Modelo de aluno com tenant_id"""

    # Dados pessoais
    first_name = models.CharField(max_length=100, verbose_name="Nome")
    last_name = models.CharField(max_length=100, verbose_name="Sobrenome")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")

    # Dados específicos do jiu-jitsu
    belt_color = models.CharField(
        max_length=20,
        choices=[
            ('white', 'Branca'),
            ('blue', 'Azul'),
            ('purple', 'Roxa'),
            ('brown', 'Marrom'),
            ('black', 'Preta'),
        ],
        default='white',
        verbose_name="Cor da Faixa"
    )

    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Data de Matrícula")
    emergency_contact = models.TextField(blank=True, verbose_name="Contato de Emergência")

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = 'students'
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

        # Constraints para garantir integridade
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'tenant'],
                name='unique_student_email_per_tenant',
                condition=models.Q(email__isnull=False)
            )
        ]

        # Índices para performance
        indexes = [
            models.Index(fields=['tenant', 'belt_color']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', 'enrollment_date']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
```

### ViewSet de Exemplo
```python
# backend-mvp/apps/students/views.py
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.viewsets import TenantViewSet
from .models import Student
from .serializers import StudentSerializer

class StudentViewSet(TenantViewSet):
    """
    ViewSet para CRUD de alunos
    Herda filtro automático por tenant
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    # Filtros e busca
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['belt_color', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'enrollment_date', 'first_name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Queryset já filtrado por tenant via TenantViewSet"""
        queryset = super().get_queryset()

        # Filtros adicionais específicos se necessário
        if self.action == 'list':
            # Otimizar queries para listagem
            queryset = queryset.select_related('tenant')

        return queryset
```

## Migração de Dados

### Command para Migração
```python
# backend-mvp/apps/core/management/commands/migrate_from_tenant_schema.py
from django.core.management.base import BaseCommand
from django.db import connections
from apps.tenants.models import Tenant
from apps.students.models import Student
from apps.payments.models import Payment
import json

class Command(BaseCommand):
    help = 'Migra dados do backend django-tenants para MVP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-db',
            type=str,
            default='tenant_schema_db',
            help='Nome da conexão do banco django-tenants'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa migração sem salvar dados'
        )

    def handle(self, *args, **options):
        tenant_db = options['tenant_db']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('Executando em modo DRY RUN'))

        # 1. Conectar ao banco django-tenants
        tenant_connection = connections[tenant_db]

        # 2. Buscar todos os tenants
        tenants = self.get_tenants_from_schema_db(tenant_connection)

        self.stdout.write(f'Encontrados {len(tenants)} tenants para migrar')

        # 3. Para cada tenant, migrar dados
        for tenant_data in tenants:
            self.stdout.write(f'Migrando tenant: {tenant_data["name"]}')

            if not dry_run:
                self.migrate_tenant_data(tenant_data, tenant_connection)
            else:
                self.stdout.write(f'  - Simulando migração de {tenant_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS('Migração concluída com sucesso!')
        )

    def get_tenants_from_schema_db(self, connection):
        """Busca tenants do banco com schemas"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, subdomain, schema_name,
                       contact_email, phone, address,
                       primary_color, secondary_color, is_active
                FROM public.tenants
                WHERE is_active = true
            """)

            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def migrate_tenant_data(self, tenant_data, tenant_connection):
        """Migra dados de um tenant específico"""

        # 1. Criar tenant no novo modelo
        tenant, created = Tenant.objects.get_or_create(
            subdomain=tenant_data['subdomain'],
            defaults={
                'name': tenant_data['name'],
                'contact_email': tenant_data.get('contact_email', ''),
                'phone': tenant_data.get('phone', ''),
                'address': tenant_data.get('address', ''),
                'primary_color': tenant_data.get('primary_color', '#3B82F6'),
                'secondary_color': tenant_data.get('secondary_color', '#1E40AF'),
                'is_active': tenant_data.get('is_active', True),
            }
        )

        if created:
            self.stdout.write(f'  ✅ Tenant criado: {tenant.name}')
        else:
            self.stdout.write(f'  ⚠️  Tenant já existe: {tenant.name}')

        # 2. Migrar dados específicos do tenant
        schema_name = tenant_data['schema_name']

        # Migrar students
        students_migrated = self.migrate_students(tenant, schema_name, tenant_connection)
        self.stdout.write(f'  ✅ {students_migrated} alunos migrados')

        # Migrar payments
        payments_migrated = self.migrate_payments(tenant, schema_name, tenant_connection)
        self.stdout.write(f'  ✅ {payments_migrated} pagamentos migrados')

    def migrate_students(self, tenant, schema_name, connection):
        """Migra students de um schema específico"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, first_name, last_name, email, phone,
                       belt_color, enrollment_date, emergency_contact,
                       is_active, created_at, updated_at
                FROM {schema_name}.students
            """)

            count = 0
            for row in cursor.fetchall():
                Student.objects.update_or_create(
                    id=row[0],  # Manter mesmo UUID
                    defaults={
                        'tenant': tenant,
                        'first_name': row[1],
                        'last_name': row[2],
                        'email': row[3] or '',
                        'phone': row[4] or '',
                        'belt_color': row[5] or 'white',
                        'enrollment_date': row[6],
                        'emergency_contact': row[7] or '',
                        'is_active': row[8],
                        'created_at': row[9],
                        'updated_at': row[10],
                    }
                )
                count += 1

        return count

    def migrate_payments(self, tenant, schema_name, connection):
        """Migra payments de um schema específico"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, student_id, amount, due_date, paid_date,
                       status, description, created_at, updated_at
                FROM {schema_name}.payments
            """)

            count = 0
            for row in cursor.fetchall():
                try:
                    # Buscar student migrado
                    student = Student.objects.get(id=row[1], tenant=tenant)

                    Payment.objects.update_or_create(
                        id=row[0],  # Manter mesmo UUID
                        defaults={
                            'tenant': tenant,
                            'student': student,
                            'amount': row[2],
                            'due_date': row[3],
                            'paid_date': row[4],
                            'status': row[5],
                            'description': row[6] or '',
                            'created_at': row[7],
                            'updated_at': row[8],
                        }
                    )
                    count += 1
                except Student.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  Student não encontrado: {row[1]}')
                    )

        return count
```

## Comandos Úteis

### Desenvolvimento MVP
```bash
# Entrar no backend MVP
cd backend-mvp/

# Ambiente virtual
uv venv
source .venv/bin/activate
uv pip install -e .

# Django commands
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver

# Migração de dados
uv run manage.py migrate_from_tenant_schema --tenant-db=tenant_schema_db
uv run manage.py migrate_from_tenant_schema --dry-run  # Simular

# Criar tenant de teste
uv run manage.py shell
>>> from apps.tenants.models import Tenant
>>> Tenant.objects.create(name="Academia Teste", subdomain="teste")
```

### Comparação com Backend Original
```bash
# Backend original (referência)
cd backend/

# Mesmos comandos, mas com django-tenants
uv run manage.py migrate_schemas
uv run manage.py create_tenant
```

## Benefícios da Estratégia Dual

### Vantagens Técnicas
1. **Preserva investimento**: Trabalho anterior mantido
2. **Acelera desenvolvimento**: MVP mais simples
3. **Reduz risco**: Rollback sempre possível
4. **Facilita comparação**: Duas implementações para avaliar
5. **Melhora produtividade**: Menos complexidade inicial

### Vantagens de Negócio
1. **Time-to-market**: Entrega mais rápida
2. **Validação**: Teste de mercado com menos investimento
3. **Flexibilidade**: Migração quando necessário
4. **Economia**: Menos horas de desenvolvimento inicial

## Roadmap de Migração

### Quando Migrar para V2.0
- **> 10 tenants ativos** (performance)
- **> 1000 usuários por tenant** (escalabilidade)
- **Requisitos de compliance** específicos
- **Backup granular** necessário

### Processo de Migração V2.0
1. **Usar backend_tenant_schema/** como base
2. **Migrar dados** do MVP para schemas
3. **Testes extensivos** de performance
4. **Switch gradual** sem downtime
5. **Monitoramento** pós-migração

### Estimativa V2.0
- **Tempo**: 2-3 semanas (80-120 horas)
- **Custo**: R$ 9.600 - R$ 14.400
- **Risco**: Baixo (implementação já existe)

> 📋 **Tarefas detalhadas**: `doc/TASKS.md`
> 🏗️ **Arquitetura completa**: `doc/ARCHITECTURE.md`
> 🤖 **Contexto para IA**: `backend/CONTEXT.md`
