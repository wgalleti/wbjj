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

#### T003 - Setup Backend Django (REST API) 🔴 📊
**Tempo**: 12 horas (1,5 dias)  
**Valor**: R$ 1.440  
**Descrição**:
- Configurar Django REST Framework e serializers
- Implementar ViewSets e routers para APIs
- Configurar CORS e permissões básicas
- Setup documentação automática (OpenAPI/Swagger)
- Implementar endpoints de healthcheck e status

**Dependências**: T002B  
**Critérios de Aceitação**:
- [ ] Django REST Framework configurado
- [ ] APIs básicas funcionando (CRUD models)
- [ ] Documentação OpenAPI automática
- [ ] CORS configurado para frontend
- [ ] Endpoints de healthcheck respondendo

---

#### T004 - Sistema Multitenancy Core 🔴 🏗️
**Tempo**: 24 horas (3 dias)  
**Valor**: R$ 2.880  
**Descrição**:
- Implementar middleware de detecção de tenant
- Criar sistema de schemas dinâmicos PostgreSQL
- Implementar isolamento de dados por tenant
- Testes de segurança de isolamento

**Dependências**: T003  
**Critérios de Aceitação**:
- [ ] Middleware funcionando com subdomínios
- [ ] Isolamento total entre tenants
- [ ] Testes automatizados de segurança
- [ ] Performance adequada (< 50ms overhead)

---

### Sprint 3-4: Core Backend APIs

#### T005 - Autenticação e Autorização 🔴 🏗️
**Tempo**: 20 horas (2,5 dias)  
**Valor**: R$ 2.400  
**Descrição**:
- Implementar sistema de login JWT
- Criar RBAC (Role-Based Access Control)
- Middleware de autorização por tenant
- Sistema de refresh tokens

**Dependências**: T004  
**Critérios de Aceitação**:
- [ ] Login/logout funcionando
- [ ] Roles por tenant
- [ ] Tokens seguros com expiração
- [ ] Endpoints protegidos

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

#### T023 - Testes Automatizados 🟡 📊
**Tempo**: 18 horas (2,25 dias)  
**Valor**: R$ 2.160  
**Descrição**:
- Testes unitários backend
- Testes E2E frontend
- Testes de integração
- Coverage mínimo 70%

**Dependências**: T022  
**Critérios de Aceitação**:
- [ ] Testes implementados
- [ ] Coverage adequado
- [ ] CI passando
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

### Por Fase
- **Fase 1 - Fundação**: R$ 9.840 (82 horas)
- **Fase 2 - Frontend**: R$ 10.320 (86 horas)  
- **Fase 3 - Mobile**: R$ 10.080 (84 horas)
- **Fase 4 - Finalização**: R$ 8.160 (68 horas)

### Total do Projeto
- **Tempo Total**: 320 horas (aprox. 8 semanas de desenvolvimento)
- **Valor Total**: R$ 38.400
- **Prazo**: 18 semanas (incluindo testes e ajustes)

### Cronograma de Pagamento Sugerido
- **30% na aprovação**: R$ 11.520
- **40% na entrega do MVP**: R$ 15.360  
- **30% no go-live**: R$ 11.520

---

## DÉBITOS TÉCNICOS IDENTIFICADOS

### Para Versão 2.0 (Pós-MVP)
1. **Reescrita Backend para Golang** - Estimativa: 120h (R$ 14.400)
2. **Frontend em TypeScript + Framework moderno** - Estimativa: 80h (R$ 9.600)
3. **Testes mais robustos** - Estimativa: 40h (R$ 4.800)
4. **Performance optimization** - Estimativa: 60h (R$ 7.200)
5. **Funcionalidades avançadas** - Estimativa: 200h (R$ 24.000)

**Total V2.0**: R$ 60.000 adicional

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
   - 📋 **Próxima**: T003 - Setup Backend Django (REST API) 