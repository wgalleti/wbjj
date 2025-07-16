# Arquitetura do Sistema wBJJ

## Visão Arquitetural

### Princípios de Design
- **Multitenancy**: Isolamento de dados por filial (MVP: tenant_id, V2.0: schemas separados)
- **Escalabilidade**: Suporte a crescimento horizontal
- **Segurança**: Autenticação e autorização robustas
- **Modularidade**: Componentes independentes e reutilizáveis
- **Performance**: Otimização de consultas e cache inteligente

## Arquitetura Multitenancy

### Estratégia de Implementação Dual

**Backend Original (django-tenants)** - `backend/`
```
Database: wbjj_main
├── public (schemas globais)
├── tenant_001_academia_alpha
├── tenant_002_academia_beta
└── tenant_xxx_academia_nome
```

**Backend MVP Simplificado** - `backend-mvp/`
```
Database: wbjj_mvp
├── tenants (tabela principal)
├── users (com tenant_id)
├── students (com tenant_id)
├── payments (com tenant_id)
└── ... (todas tabelas com tenant_id)
```

### Estrutura de Diretórios do Projeto

```
wBJJ/
├── backend-mvp/                # Backend MVP simplificado (ATIVO)
│   ├── apps/
│   │   ├── tenants/           # Modelo Tenant simples
│   │   ├── authentication/    # User com tenant_id
│   │   ├── students/          # Student com tenant_id
│   │   ├── payments/          # Payment com tenant_id
│   │   └── core/              # TenantMixin e utilities
│   ├── config/
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── manage.py
├── backend/                    # Backend original (REFERÊNCIA)
│   ├── apps/                  # Implementação com schemas separados
│   ├── config/
│   ├── requirements.txt       # Com django-tenants
│   └── manage.py
└── doc/                       # Documentação do projeto
```

### Vantagens da Abordagem Dual

**Backend MVP (`backend-mvp/`)**:
- ✅ **Simplicidade**: Implementação rápida e direta
- ✅ **Desenvolvimento Ágil**: Menos complexidade inicial
- ✅ **Facilidade de Testes**: Ambiente único de desenvolvimento
- ✅ **Manutenção**: Estrutura mais simples para MVP
- ✅ **Performance Adequada**: Suficiente para validação

**Backend Original (`backend/`)**:
- ✅ **Referência Técnica**: Implementação completa preservada
- ✅ **Isolamento Total**: Dados completamente separados
- ✅ **Escalabilidade**: Suporte a milhares de tenants
- ✅ **Segurança Máxima**: Impossibilidade de vazamento
- ✅ **Rollback**: Possibilidade de volta se necessário

### Limitações da Abordagem MVP
- **Isolamento Parcial**: Dados no mesmo banco
- **Escalabilidade Limitada**: Performance pode degradar com muitos tenants
- **Segurança**: Risco de vazamento se filtros falharem
- **Backup**: Não é possível backup granular por tenant

## Componentes da Arquitetura MVP

### 1. Backend MVP (Diretório `backend/`)

#### TenantMixin Base
```python
# backend-mvp/apps/core/models.py
from django.db import models
import uuid

class BaseModel(models.Model):
    """Modelo base abstrato para todos os modelos do sistema"""
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
        if not self.tenant_id:
            raise ValueError("Tenant é obrigatório")
        super().save(*args, **kwargs)
```

#### Middleware de Filtro MVP
```python
# backend-mvp/apps/core/middleware.py
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from apps.tenants.models import Tenant
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    """Middleware MVP para detectar tenant via subdomínio"""

    def process_request(self, request):
        hostname = request.get_host().split(':')[0]
        subdomain = hostname.split('.')[0]

        # Pular para domínios principais
        main_domains = ['www', 'admin', 'api', 'localhost', '127']
        if subdomain in main_domains or subdomain.startswith('127'):
            request.tenant = None
            return None

        # Buscar tenant no cache
        cache_key = f"tenant:subdomain:{subdomain}"
        tenant = cache.get(cache_key)

        if tenant is None:
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                cache.set(cache_key, tenant, 3600)
            except Tenant.DoesNotExist:
                logger.warning(f"Tenant não encontrado: {subdomain}")
                raise Http404("Academia não encontrada")

        request.tenant = tenant
        request.tenant_id = tenant.id
        return None
```

#### ViewSet Base com Filtro
```python
# backend-mvp/apps/core/viewsets.py
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError

class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet base que automaticamente filtra por tenant"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            raise ValidationError("Tenant não identificado")
        serializer.save(tenant=self.request.tenant)

    def perform_update(self, serializer):
        if 'tenant' in serializer.validated_data:
            serializer.validated_data.pop('tenant')
        serializer.save()
```

### 2. Migração de Dados

#### Script de Migração
```python
# backend/management/commands/migrate_from_tenant_schema.py
from django.core.management.base import BaseCommand
from django.db import connection
from apps.tenants.models import Tenant
from apps.students.models import Student
from apps.payments.models import Payment
import json

class Command(BaseCommand):
    help = 'Migra dados do backend django-tenants para MVP'

    def handle(self, *args, **options):
        # 1. Conectar ao banco django-tenants
        tenant_db = 'tenant_schema_db'

        # 2. Buscar todos os tenants
        tenants = self.get_tenants_from_schema_db()

        # 3. Para cada tenant, migrar dados
        for tenant_data in tenants:
            self.migrate_tenant_data(tenant_data)

        self.stdout.write(
            self.style.SUCCESS('Migração concluída com sucesso!')
        )

    def get_tenants_from_schema_db(self):
        # Buscar tenants do banco com schemas
        pass

    def migrate_tenant_data(self, tenant_data):
        # Criar tenant no novo modelo
        tenant = Tenant.objects.create(
            name=tenant_data['name'],
            subdomain=tenant_data['subdomain'],
            # ... outros campos
        )

        # Migrar students, payments, etc.
        self.migrate_students(tenant, tenant_data['schema_name'])
        self.migrate_payments(tenant, tenant_data['schema_name'])
```

## Débito Técnico - Migração V2.0

### Quando Migrar de Volta para Schemas Separados
1. **> 10 tenants ativos** (performance)
2. **> 1000 usuários por tenant** (escalabilidade)
3. **Requisitos de compliance** específicos
4. **Necessidade de backup granular** por tenant

### Processo de Migração V2.0
1. **Usar backend original** (`backend/`)
2. **Migrar dados** do MVP para schemas separados
3. **Testes extensivos** de performance e segurança
4. **Switch gradual** sem downtime
5. **Monitoramento** pós-migração

### Estimativa de Retorno para V2.0
- **Tempo**: 2-3 semanas (80-120 horas)
- **Custo**: R$ 9.600 - R$ 14.400
- **Benefícios**: Isolamento total, performance, backup granular
- **Risco**: Baixo (implementação já existe)

## Estratégia de Desenvolvimento

### Fase MVP (Atual)
1. **Usar backend MVP** (`backend/`) para desenvolvimento
2. **Foco na velocidade** de entrega
3. **Validação de mercado** com academia piloto
4. **Monitoramento** de performance e uso

### Fase V2.0 (Futuro)
1. **Avaliar métricas** de uso (tenants, usuários, performance)
2. **Decidir migração** baseada em dados reais
3. **Usar backend original** como base para V2.0
4. **Implementar melhorias** identificadas no MVP

### Benefícios da Estratégia Dual
- **Preserva investimento**: Trabalho anterior não perdido
- **Acelera MVP**: Desenvolvimento mais rápido
- **Reduz risco**: Rollback sempre possível
- **Facilita decisão**: Dados reais para escolher arquitetura final
