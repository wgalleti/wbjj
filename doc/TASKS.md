# Tarefas do Projeto wBJJ - Sistema de Gestão para Academias

## Informações de Custo

### Base de Cálculo
- **Desenvolvedor Sênior**: R$ 120/hora
- **Jornada**: 8 horas/dia útil
- **Sprint**: 2 semanas (10 dias úteis)

### Legendas
- 🔴 **Crítico**: Bloqueia outras tarefas
- 🟡 **Importante**: Necessário para funcionalidade
- 🟢 **Melhorias**: Pode ser postergado
- ⚡ **Rápido**: < 1 dia
- 📊 **Médio**: 1-3 dias
- 🏗️ **Grande**: > 3 dias

---

## FASE 1: FUNDAÇÃO E SETUP (6 semanas)

### Sprint 1-2: Decisões e Setup Inicial

#### T001 - Setup Repositório e Ambiente ✅ ⚡
**Tempo**: 4 horas
**Valor**: R$ 480
**Status**: **COMPLETA**
**Descrição**:
- Configurar monorepo com estrutura backend/frontend/mobile
- Setup Docker Compose para desenvolvimento
- Configurar Git com hooks básicos
- Documentar guia de setup para desenvolvedores

**Dependências**: Nenhuma
**Critérios de Aceitação**:
- [x] Repositório configurado com estrutura de pastas
- [x] Backend Django configurado com UV
- [x] Documentação completa em SETUP_SCRIPTS.md
- [x] Pre-commit hooks configurados
- [x] Django check funcionando

---

#### T002 - Models Django e Migrations ✅ 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Status**: **COMPLETA**
**Descrição**:
- Implementar Abstract Base Models (BaseModel, TimestampedModel, SoftDeleteModel)
- Criar models principais: Tenant, User personalizado, Student, Payment, etc.
- Configurar relacionamentos e constraints otimizados
- Gerar migrations Django com índices de performance
- Configurar Django Admin completo com inlines e fieldsets
- Implementar comando seed_data para desenvolvimento

**Dependências**: T001
**Critérios de Aceitação**:
- [x] BaseModel abstrato com UUID, timestamps e soft delete
- [x] User personalizado (email login, roles, multitenancy ready)
- [x] Models: Tenant, Student, Graduation, Attendance, Invoice, Payment
- [x] Django Admin configurado com filtros e busca
- [x] Migrations geradas e validadas (django check ✅)
- [x] Comando `python manage.py seed_data` funcionando
- [x] Documentação em T002_MODELS_DJANGO.md

---

#### T002B - Docker Compose e Banco de Dados ✅ 🏗️
**Tempo**: 6 horas (0,75 dias)
**Valor**: R$ 720
**Status**: **COMPLETA**
**Descrição**:
- Configurar Docker Compose com PostgreSQL e Redis
- Criar arquivos de ambiente (.env) para desenvolvimento
- Implementar scripts de inicialização do banco
- Aplicar migrations e popular dados de seed
- Documentar comandos de desenvolvimento

**Dependências**: T002
**Critérios de Aceitação**:
- [x] Docker Compose funcionando (PostgreSQL + Redis)
- [x] Migrations aplicadas automaticamente
- [x] Dados de seed carregados
- [x] Scripts de desenvolvimento documentados
- [x] Banco acessível para Django
- [x] Documentação completa em DOCKER_DEVELOPMENT.md

---

#### T003 - Setup Backend Django (REST API) ✅ 📊
**Tempo**: 12 horas (1,5 dias)
**Valor**: R$ 1.440
**Status**: **COMPLETA**
**Descrição**:
- Configurar Django REST Framework e serializers
- Implementar ViewSets e routers para APIs
- Configurar CORS e permissões básicas
- Setup documentação automática (OpenAPI/Swagger)
- Implementar endpoints de healthcheck e status

**Dependências**: T002B
**Critérios de Aceitação**:
- [x] Django REST Framework configurado
- [x] APIs básicas funcionando (CRUD models)
- [x] Documentação OpenAPI automática
- [x] CORS configurado para frontend
- [x] Endpoints de healthcheck respondendo
- [x] Sistema de autenticação JWT implementado
- [x] Permissões granulares configuradas
- [x] Health checks com métricas completas
- [x] Documentação API completa com exemplos

---

#### T004 - Sistema Multitenancy MVP (Simplificado) 🔴 🏗️
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Status**: **COMPLETA**
**Descrição**:
- Implementar middleware de detecção de tenant por subdomínio
- Criar modelo Tenant simples com campos básicos
- Implementar TenantModel base para herança
- Criar TenantViewSet base com filtros automáticos
- Implementar isolamento de dados por tenant_id
- Testes de segurança de isolamento (básicos)

**Dependências**: T003
**Critérios de Aceitação**:
- [x] Middleware funcionando com subdomínios
- [x] Modelo Tenant com campos de configuração
- [x] TenantModel base funcionando
- [x] TenantViewSet filtrando automaticamente por tenant
- [x] Isolamento por tenant_id funcionando
- [x] Testes automatizados de segurança básicos
- [x] Performance adequada (< 20ms overhead)
- [x] Cache de tenant por subdomínio

**Limitações MVP**:
- Isolamento parcial (mesmo banco)
- Risco de vazamento se filtros falharem
- Performance limitada com muitos tenants
- Backup não granular por tenant

---

#### T004D - Criação do Backend MVP Simplificado 🔴 🏗️
**Tempo**: 20 horas (2,5 dias)
**Valor**: R$ 2.400
**Status**: **PENDENTE**
**Descrição**:
- Criar novo diretório `backend-mvp` com implementação MVP simplificada
- Remover django-tenants e implementar TenantMixin com tenant_id
- Criar middleware de filtro de dados por tenant_id
- Migrar estrutura de dados para modelo simplificado
- Manter mesmos padrões de código e estrutura de diretórios
- Configurar ambiente de desenvolvimento para novo backend
- Ajustar os testes para nova estrutura

**Dependências**: T004 (backend django-tenants já implementado)
**Critérios de Aceitação**:
- [x] Novo diretório `backend-mvp` criado com estrutura Django limpa
- [ ] Django-tenants removido das dependências
- [ ] TenantMixin implementado com tenant_id em todos os models
- [ ] Middleware de detecção e filtro por tenant funcionando
- [ ] Migração de dados do schema separado para tenant_id
- [ ] Testes básicos funcionando no novo backend
- [ ] Docker e ambiente de desenvolvimento configurados
- [ ] Documentação atualizada para nova estrutura

**Estrutura de Diretórios Resultante**:
```
wBJJ/
├── backend-mvp/                    # Novo backend MVP simplificado
│   ├── apps/
│   │   ├── tenants/           # Modelo Tenant simples
│   │   ├── authentication/    # User com tenant_id
│   │   ├── students/          # Student com tenant_id
│   │   ├── payments/          # Payment com tenant_id
│   │   └── core/              # TenantMixin e utilities
│   ├── config/
│   ├── docker-compose.yml
│   └── requirements.txt
├── backend/                   # Backend original (django-tenants)
│   ├── apps/                  # Implementação com schemas separados
│   ├── config/
│   └── requirements.txt       # Com django-tenants
└── doc/                       # Documentação atualizada
```

**Implementação Detalhada**:

1. **TenantMixin Base**:
```python
# backend-mvp/apps/core/models.py
class TenantMixin(models.Model):
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            raise ValueError("Tenant é obrigatório")
        super().save(*args, **kwargs)
```

2. **Middleware de Filtro**:
```python
# backend-mvp/apps/core/middleware.py
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Detectar tenant por subdomínio
        subdomain = request.get_host().split('.')[0]
        tenant = Tenant.objects.get(subdomain=subdomain)
        request.tenant = tenant

        response = self.get_response(request)
        return response
```

3. **ViewSet Base com Filtro**:
```python
# backend-mvp/apps/core/viewsets.py
class TenantViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
```

**Migração de Dados**:
- Script para extrair dados dos schemas separados
- Transformar para estrutura com tenant_id
- Validar integridade dos dados migrados

**Benefícios da Abordagem**:
- **Preserva trabalho anterior**: Backend django-tenants mantido como referência
- **Acelera MVP**: Implementação mais simples e rápida
- **Facilita comparação**: Dois backends para avaliar performance
- **Reduz risco**: Rollback possível para implementação original
- **Melhora produtividade**: Desenvolvimento mais ágil no MVP

---

#### T004C - Débito Técnico: Multitenancy V2.0 (Schemas Separados) 🟡 🏗️
**Tempo**: 140 horas (17,5 dias)
**Valor**: R$ 16.800
**Status**: **DÉBITO TÉCNICO**
**Descrição**:
- Migrar para django-tenant-schemas
- Implementar schemas separados por tenant
- Reescrever middleware para mudança automática de schema
- Migrar dados existentes para novos schemas
- Implementar backup granular por tenant
- Testes completos de isolamento e performance
- Documentação da migração

**Dependências**: MVP validado e em produção
**Critérios de Aceitação**:
- [ ] Django-tenant-schemas configurado
- [ ] Middleware com mudança automática de schema
- [ ] Migração de dados sem perda
- [ ] Isolamento total entre tenants
- [ ] Backup granular por tenant
- [ ] Performance otimizada para milhares de tenants
- [ ] Testes completos de segurança
- [ ] Documentação da arquitetura V2.0

**Benefícios V2.0**:
- Isolamento total de dados
- Backup granular por tenant
- Performance otimizada
- Escalabilidade para milhares de tenants
- Segurança máxima

**Estimativa de Migração**:
- **Tempo**: 3-4 semanas de desenvolvimento
- **Custo**: R$ 14.400 - R$ 19.200
- **Complexidade**: Alta
- **Risco**: Médio (migração de dados)

---

#### T004B - Sistema de Testes Robusto e Padronizado 🔴 📊
**Tempo**: 18 horas (2,25 dias)
**Valor**: R$ 2.160
**Descrição**:
- Configurar pytest como framework principal de testes seguindo CONTEXT.md
- Implementar TenantTestCase para testes multitenancy MVP
- Setup factory-boy para factories consistentes
- Criar estrutura de testes por camada (models, serializers, viewsets, middleware, etc)
- Configurar pytest-django e pytest-cov para cobertura > 90%
- Implementar testes de integração e segurança
- Padronizar templates e convenções de teste
- Integrar testes no pipeline CI/CD

**Dependências**: T004
**Critérios de Aceitação**:
- [x] Pytest configurado com TenantTestCase funcionando
- [x] Factory-boy setup com factories para todos os models
- [x] Estrutura de testes organizada: tests/models/, tests/serializers/, tests/views/, tests/middleware/
- [x] Cobertura de código > 90% (pytest-cov)
- [x] Testes de isolamento multitenancy passando
- [x] Testes de performance middleware (< 50ms overhead)
- [x] Testes de segurança (OWASP básicos)
- [x] Templates de teste documentados
- [x] Integração com pre-commit hooks
- [x] Pipeline CI executando todos os testes
- [x] Relatórios de cobertura HTML gerados
- [x] Documentação completa em T004B_TESTING_FRAMEWORK.md

---

### Sprint 3-4: Core Backend APIs

#### T005 - Autenticação e Autorização ✅ 🏗️
**Tempo**: 20 horas (2,5 dias)
**Valor**: R$ 2.400
**Status**: **COMPLETA**
**Descrição**:
- Implementar sistema de login JWT
- Criar RBAC (Role-Based Access Control)
- Middleware de autorização por tenant
- Sistema de refresh tokens

**Dependências**: T004B
**Critérios de Aceitação**:
- [x] Login/logout funcionando
- [x] Roles por tenant
- [x] Tokens seguros com expiração
- [x] Endpoints protegidos

---

#### T006 - CRUD de Alunos 🔴 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Criar modelos de Student
- Implementar APIs CRUD completas
- Sistema de graduações de faixas
- Validações e regras de negócio

**Dependências**: T005
**Critérios de Aceitação**:
- [ ] APIs CRUD documentadas
- [ ] Sistema de graduações
- [ ] Validações implementadas
- [ ] Testes unitários

---

#### T007 - Módulo Financeiro Básico 🔴 📊
**Tempo**: 20 horas (2,5 dias)
**Valor**: R$ 2.400
**Descrição**:
- Modelos de Payment e Invoice
- APIs para mensalidades
- Controle de status de pagamento
- Relatórios básicos

**Dependências**: T006
**Critérios de Aceitação**:
- [ ] Sistema de mensalidades
- [ ] Controle de inadimplência
- [ ] APIs de relatórios
- [ ] Validações financeiras

---

## FASE 2: FRONTEND WEB (4 semanas)

### Sprint 5-6: Setup e Autenticação Web

#### T008 - Setup Vue.js + Tailwind 🔴 📊
**Tempo**: 12 horas (1,5 dias)
**Valor**: R$ 1.440
**Descrição**:
- Configurar projeto Vue.js 3
- Setup Tailwind CSS + Shadcn/Vue
- Configurar Pinia para estado global
- Setup de build e desenvolvimento

**Dependências**: T003
**Critérios de Aceitação**:
- [ ] Projeto Vue rodando
- [ ] Tailwind configurado
- [ ] Componentes base do Shadcn
- [ ] Hot reload funcionando

---

#### T009 - Sistema de Autenticação Web 🔴 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Telas de login/logout
- Integração com APIs do backend
- Proteção de rotas
- Gestão de tokens no frontend

**Dependências**: T008, T005
**Critérios de Aceitação**:
- [ ] Login funcionando
- [ ] Rotas protegidas
- [ ] Logout automático
- [ ] Feedback de erros

---

#### T010 - Multitenancy Frontend 🔴 📊
**Tempo**: 14 horas (1,75 dias)
**Valor**: R$ 1.680
**Descrição**:
- Detecção de tenant por subdomínio
- Sistema de temas por tenant
- Configuração de logos/cores
- Loading de configurações dinâmicas

**Dependências**: T009
**Critérios de Aceitação**:
- [ ] Subdomínios funcionando
- [ ] Temas personalizáveis
- [ ] Assets por tenant
- [ ] Performance otimizada

---

### Sprint 7-8: Dashboard e Gestão

#### T011 - Dashboard Administrativo 🔴 🏗️
**Tempo**: 24 horas (3 dias)
**Valor**: R$ 2.880
**Descrição**:
- Layout principal responsivo
- Sidebar com navegação
- Dashboard com métricas básicas
- Header com informações do usuário

**Dependências**: T010
**Critérios de Aceitação**:
- [ ] Layout responsivo
- [ ] Navegação funcional
- [ ] Métricas em tempo real
- [ ] UX otimizada

---

#### T012 - Gestão de Alunos Frontend 🔴 🏗️
**Tempo**: 20 horas (2,5 dias)
**Valor**: R$ 2.400
**Descrição**:
- Listagem de alunos com filtros
- Formulários de cadastro/edição
- Sistema de graduações visual
- Upload de fotos

**Dependências**: T011, T006
**Critérios de Aceitação**:
- [ ] CRUD completo funcionando
- [ ] Filtros e busca
- [ ] Interface intuitiva
- [ ] Validações client-side

---

#### T013 - Dashboard Financeiro 🔴 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Gráficos de receita
- Lista de mensalidades
- Controle de inadimplentes
- Relatórios básicos

**Dependências**: T012, T007
**Critérios de Aceitação**:
- [ ] Gráficos funcionais
- [ ] Dados em tempo real
- [ ] Exportação básica
- [ ] Performance adequada

---

## FASE 3: APLICATIVO MOBILE (5 semanas)

### Sprint 9-10: Setup e Autenticação Mobile

#### T014 - Setup Flutter 🔴 📊
**Tempo**: 12 horas (1,5 dias)
**Valor**: R$ 1.440
**Descrição**:
- Configurar projeto Flutter
- Setup de navegação
- Configurar state management (Riverpod)
- Setup de build para iOS/Android

**Dependências**: T003
**Critérios de Aceitação**:
- [ ] Projeto Flutter funcionando
- [ ] Navegação configurada
- [ ] Build iOS/Android
- [ ] Hot reload ativo

---

#### T015 - Autenticação Mobile 🔴 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Telas de login elegantes
- Integração com APIs
- Autenticação biométrica
- Onboarding inicial

**Dependências**: T014, T005
**Critérios de Aceitação**:
- [ ] Login funcionando
- [ ] Biometria implementada
- [ ] Onboarding fluido
- [ ] Design responsivo

---

#### T016 - Configuração Visual por Tenant 🔴 📊
**Tempo**: 14 horas (1,75 dias)
**Valor**: R$ 1.680
**Descrição**:
- Sistema de temas dinâmicos
- Carregamento de logos/cores
- Configurações per tenant
- Fallbacks para offline

**Dependências**: T015
**Critérios de Aceitação**:
- [ ] Temas funcionando
- [ ] Assets personalizados
- [ ] Performance otimizada
- [ ] Modo offline básico

---

### Sprint 11-12: Funcionalidades do Aluno

#### T017 - Dashboard do Aluno 🔴 📊
**Tempo**: 18 horas (2,25 dias)
**Valor**: R$ 2.160
**Descrição**:
- Tela inicial com informações
- Próximas aulas
- Progresso pessoal
- Notificações básicas

**Dependências**: T016
**Critérios de Aceitação**:
- [ ] Dashboard funcional
- [ ] Dados em tempo real
- [ ] Interface intuitiva
- [ ] Performance adequada

---

#### T018 - Sistema de Agendamentos 🔴 🏗️
**Tempo**: 24 horas (3 dias)
**Valor**: R$ 2.880
**Descrição**:
- Calendário de aulas
- Sistema de reservas
- Check-in/check-out
- Cancelamentos

**Dependências**: T017
**Critérios de Aceitação**:
- [ ] Calendário funcionando
- [ ] Reservas em tempo real
- [ ] Check-in funcional
- [ ] Regras de cancelamento

---

#### T019 - Push Notifications 🔴 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Configuração Firebase/FCM
- Notificações de aulas
- Lembretes de pagamento
- Configurações de usuário

**Dependências**: T018
**Critérios de Aceitação**:
- [ ] Notificações funcionando
- [ ] Diferentes tipos
- [ ] Configurações de usuário
- [ ] Performance otimizada

---

## FASE 4: INTEGRAÇÕES E REFINAMENTOS (3 semanas)

### Sprint 13-14: Integrações

#### T020 - Integração Gateway de Pagamento 🟡 🏗️
**Tempo**: 20 horas (2,5 dias)
**Valor**: R$ 2.400
**Descrição**:
- Integração com Stripe/PagSeguro
- Webhooks de confirmação
- Processamento assíncrono
- Logs e auditoria

**Dependências**: T007
**Critérios de Aceitação**:
- [ ] Pagamentos funcionando
- [ ] Webhooks implementados
- [ ] Logs completos
- [ ] Segurança validada

---

#### T021 - Landing Pages por Tenant 🟡 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Templates customizáveis
- SEO otimizado
- Formulários de contato
- Performance otimizada

**Dependências**: T010
**Critérios de Aceitação**:
- [ ] Templates funcionando
- [ ] SEO implementado
- [ ] Formulários integrados
- [ ] Performance > 90

---

### Sprint 15: Deploy e Testes

#### T022 - Setup CI/CD 🔴 📊
**Tempo**: 14 horas (1,75 dias)
**Valor**: R$ 1.680
**Descrição**:
- Pipeline GitHub Actions
- Deploy automatizado
- Testes automatizados
- Monitoramento básico

**Dependências**: T001
**Critérios de Aceitação**:
- [ ] Pipeline funcionando
- [ ] Deploy automático
- [ ] Testes passando
- [ ] Monitoramento ativo

---

#### T023 - Testes E2E Frontend e Mobile 🟡 📊
**Tempo**: 12 horas (1,5 dias)
**Valor**: R$ 1.440
**Descrição**:
- Testes E2E frontend com Cypress/Playwright
- Testes de fluxo completo usuário
- Testes de integração frontend-backend
- Testes mobile com detox (básicos)

**Dependências**: T022
**Critérios de Aceitação**:
- [ ] Testes E2E frontend funcionando
- [ ] Fluxos críticos cobertos
- [ ] CI rodando testes E2E
- [ ] Documentação atualizada

---

#### T024 - Academia Piloto e Launch 🔴 📊
**Tempo**: 16 horas (2 dias)
**Valor**: R$ 1.920
**Descrição**:
- Onboarding academia piloto
- Migração de dados
- Treinamento usuários
- Suporte pós-launch

**Dependências**: T023
**Critérios de Aceitação**:
- [ ] Academia configurada
- [ ] Dados migrados
- [ ] Usuários treinados
- [ ] Sistema estável

---

## RESUMO FINANCEIRO

### Por Fase (MVP)
- **Fase 1 - Fundação**: R$ 13.440 (112 horas) - Inclui T004D para criação do backend MVP
- **Fase 2 - Frontend**: R$ 10.320 (86 horas)
- **Fase 3 - Mobile**: R$ 10.080 (84 horas)
- **Fase 4 - Finalização**: R$ 7.440 (62 horas)

### Total do MVP
- **Tempo Total**: 344 horas (aprox. 8,6 semanas de desenvolvimento)
- **Valor Total**: R$ 41.280 (Inclui R$ 2.400 para criação do backend MVP)
- **Prazo**: 18 semanas (incluindo testes e ajustes)

### Cronograma de Pagamento Sugerido
- **30% na aprovação**: R$ 12.384
- **40% na entrega do MVP**: R$ 16.512
- **30% no go-live**: R$ 12.384

---

## DÉBITOS TÉCNICOS IDENTIFICADOS

### Para Versão 2.0 (Pós-MVP)
1. **T004C - Multitenancy com Schemas Separados** - Estimativa: 140h (R$ 16.800)
2. **Reescrita Backend para Golang** - Estimativa: 120h (R$ 14.400)
3. **Frontend em TypeScript + Framework moderno** - Estimativa: 80h (R$ 9.600)
4. **Testes mais robustos** - Estimativa: 40h (R$ 4.800)
5. **Performance optimization** - Estimativa: 60h (R$ 7.200)
6. **Funcionalidades avançadas** - Estimativa: 200h (R$ 24.000)

**Total V2.0**: R$ 76.800 adicional

### Prioridade dos Débitos Técnicos
1. **🔴 Crítico**: T004C - Multitenancy V2.0 (quando houver > 10 tenants)
2. **🟡 Importante**: Reescrita para Golang (quando performance for gargalo)
3. **🟢 Desejável**: TypeScript frontend (quando equipe crescer)

---

## BENEFÍCIOS DA SIMPLIFICAÇÃO MVP

### Economia Imediata
- **R$ 960 economizados** na implementação inicial
- **8 horas reduzidas** no desenvolvimento
- **Menor complexidade** para testes e debug
- **Deploy mais simples** sem configurações de schema

### Vantagens Estratégicas
- **Time-to-market mais rápido** para validação
- **Menos pontos de falha** na implementação inicial
- **Facilidade de desenvolvimento** para equipe
- **Testes mais simples** e diretos

### Quando Migrar para V2.0
- **> 10 tenants ativos** (performance)
- **> 1000 usuários por tenant** (escalabilidade)
- **Requisitos de compliance** específicos
- **Necessidade de backup granular** por tenant

---

## NOTAS IMPORTANTES

1. **Todas as estimativas incluem**:
   - Desenvolvimento
   - Testes básicos
   - Documentação mínima
   - Code review

2. **Não incluem**:
   - Design/UX (assumindo templates prontos)
   - Infraestrutura/hosting
   - Domínios e certificados
   - Integrações premium

3. **Riscos de prazo**:
   - Integrações externas podem adicionar 20% ao prazo
   - Mudanças de escopo podem impactar significativamente
   - Testes com academia piloto podem gerar retrabalho

4. **Status Atual**:
   - ✅ **T001 Completa**: Setup repositório e ambiente Django
   - ✅ **T002 Completa**: Models Django e migrations
   - ✅ **T002B Completa**: Docker Compose e banco de dados
   - ✅ **T003 Completa**: Setup Backend Django (REST API)
   - ✅ **T004 Completa**: Sistema Multitenancy MVP (Simplificado)
   - ✅ **T004B Completa**: Sistema de Testes Robusto e Padronizado
   - ✅ **T005 Completa**: Autenticação e Autorização
   - 📋 **Próxima**: T006 - CRUD de Alunos

5. **Débito Técnico Monitorado**:
   - **T004C**: Multitenancy V2.0 será implementado quando necessário
   - **Métricas de trigger**: Número de tenants, performance, requisitos de compliance
   - **Planejamento**: Migração será feita sem downtime e com rollback plan
