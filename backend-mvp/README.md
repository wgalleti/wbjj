# wBJJ Backend MVP

Sistema de gestão para academias de jiu-jitsu - API REST MVP com multitenancy simplificado.

## 🚀 Status da Implementação

✅ **API REST Completa** - Todos os endpoints implementados e documentados
✅ **Autenticação JWT** - Login, refresh tokens e permissões granulares
✅ **Multitenancy MVP** - Isolamento de dados por tenant_id (simplificado)
✅ **Documentação OpenAPI** - Swagger/ReDoc com exemplos e autenticação
✅ **Health Checks** - Monitoramento completo com métricas detalhadas
✅ **CORS Configurado** - Headers e origens de produção configurados

## 📋 Diferenças da Implementação MVP

### ✅ Implementação Atual (MVP)
- **Multitenancy**: Filtro por `tenant_id` no mesmo banco
- **Isolamento**: Por aplicação usando middleware
- **Performance**: Adequada para validação de mercado
- **Complexidade**: Baixa, desenvolvimento rápido
- **Escalabilidade**: Limitada (adequada para MVP)

### 🔄 Implementação V2.0 (Planejada)
- **Multitenancy**: Schemas PostgreSQL separados
- **Isolamento**: Total por schema de banco
- **Performance**: Otimizada para milhares de tenants
- **Complexidade**: Alta, desenvolvimento mais lento
- **Escalabilidade**: Ilimitada

## 📚 Documentação

### 📖 Guias Principais
- **[API Documentation](API_DOCUMENTATION.md)** - Documentação completa da API
- **[Usage Examples](USAGE_EXAMPLES.md)** - Exemplos práticos de uso
- **[CONTEXT.md](CONTEXT.md)** - Padrões e regras do projeto
- **[Docker Development](DOCKER_DEVELOPMENT.md)** - Guia de desenvolvimento

### 🌐 Documentação Interativa
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema OpenAPI**: http://localhost:8000/api/schema/

## 🛠 Tecnologias

- **Django 4.2 LTS** - Framework web robusto
- **Django REST Framework 3.14** - APIs RESTful
- **PostgreSQL 15** - Banco de dados principal
- **Redis 7** - Cache e sessões
- **JWT Authentication** - Tokens seguros
- **Docker** - Containerização

## ⚡ Quick Start

### 1. Com Docker (Recomendado)

```bash
# Clone e configure
git clone <repository>
cd backend

# Iniciar ambiente completo
docker-compose up -d

# Popular dados de desenvolvimento
docker-compose exec web uv run python manage.py seed_data

# Acessar documentação
open http://localhost:8000/api/docs/
```

### 2. Desenvolvimento Local

```bash
# Instalar dependências
uv venv && source .venv/bin/activate
uv pip install -e .

# Configurar banco
python manage.py migrate
python manage.py seed_data

# Iniciar servidor
python manage.py runserver
```

## 🔗 URLs Importantes

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **API Docs (Swagger)** | http://localhost:8000/api/docs/ | Interface interativa da API |
| **ReDoc** | http://localhost:8000/api/redoc/ | Documentação alternativa |
| **Django Admin** | http://localhost:8000/admin/ | Interface administrativa |
| **Health Check** | http://localhost:8000/api/v1/health/ | Status da aplicação |
| **Metrics** | http://localhost:8000/api/v1/metrics/ | Métricas detalhadas |

## 🔐 Autenticação Rápida

### Obter Token JWT

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{
    "email": "admin@wbjj.com",
    "password": "123456"
  }'
```

### Usar Token nas Requisições

```bash
curl -X GET http://localhost:8000/api/v1/students/ \
  -H "Authorization: Bearer <seu-token-jwt>" \
  -H "X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000"
```

## 📊 APIs Disponíveis

### 🔐 Autenticação
- `POST /api/v1/auth/login/` - Login e obtenção de token
- `POST /api/v1/auth/refresh/` - Renovar token JWT
- `GET /api/v1/auth/me/` - Dados do usuário atual
- `POST /api/v1/auth/change-password/` - Alterar senha

### 👨‍🎓 Gestão de Alunos
- `GET|POST /api/v1/students/` - Listar/criar alunos
- `GET|PUT|PATCH|DELETE /api/v1/students/{id}/` - Operações por aluno
- `POST /api/v1/students/{id}/graduate/` - Graduar aluno
- `GET /api/v1/students/{id}/attendances/` - Presenças do aluno
- `GET /api/v1/students/{id}/graduations/` - Histórico de graduações

### 📅 Presenças
- `GET|POST /api/v1/attendances/` - Listar/registrar presenças
- `POST /api/v1/attendances/{id}/checkout/` - Checkout de presença

### 💰 Sistema Financeiro
- `GET|POST /api/v1/invoices/` - Faturas
- `GET|POST /api/v1/payments/` - Pagamentos
- `POST /api/v1/payments/{id}/confirm/` - Confirmar pagamento
- `GET|POST /api/v1/payment-methods/` - Métodos de pagamento

### 🏢 Academias (Tenants)
- `GET|POST /api/v1/tenants/` - Gestão de academias
- `GET /api/v1/tenants/{id}/public/` - Dados públicos da academia

### 🏥 Monitoramento
- `GET /api/v1/health/` - Health check completo
- `GET /api/v1/health/quick/` - Health check rápido
- `GET /api/v1/health/database/` - Status do banco
- `GET /api/v1/health/cache/` - Status do cache
- `GET /api/v1/metrics/` - Métricas do sistema

## 🧪 Comandos de Desenvolvimento

```bash
# Logs da aplicação
docker-compose logs -f web

# Shell no container
docker-compose exec web bash

# Django shell
docker-compose exec web uv run python manage.py shell

# Executar migrations
docker-compose exec web uv run python manage.py migrate

# Popular dados de desenvolvimento
docker-compose exec web uv run python manage.py seed_data --clear

# Executar testes
docker-compose exec web uv run pytest

# Gerar schema OpenAPI
docker-compose exec web uv run python manage.py spectacular --file schema.yml
```

## 👥 Usuários de Desenvolvimento

| Usuário | Email | Senha | Papel |
|---------|-------|-------|-------|
| **Admin** | admin@wbjj.com | 123456 | Administrador |
| **Instrutor** | professor@gb-sp.com.br | 123456 | Professor |
| **Aluno** | joao.silva@email.com | 123456 | Estudante |

## 🔍 Recursos Avançados

### Filtros e Busca
```bash
# Buscar alunos por nome
GET /api/v1/students/?search=João Silva

# Filtrar por faixa e status
GET /api/v1/students/?belt_color=blue&status=active

# Ordenar por data de criação (decrescente)
GET /api/v1/students/?ordering=-created_at

# Paginação customizada
GET /api/v1/students/?page=2&page_size=50
```

### Estatísticas
```bash
# Stats de alunos
GET /api/v1/students/stats/

# Stats de uma fatura específica
GET /api/v1/invoices/{id}/stats/

# Métricas gerais do sistema
GET /api/v1/metrics/
```

## 🏗 Arquitetura

### Estrutura de Apps Django
```
backend/
├── apps/
│   ├── core/           # Utilities base (viewsets, permissions, etc)
│   ├── authentication/ # Auth customizada + JWT
│   ├── students/       # Gestão de alunos
│   ├── payments/       # Sistema financeiro
│   └── tenants/        # Gestão de academias
├── config/             # Configurações Django
└── static/             # Arquivos estáticos
```

### Padrões Implementados

✅ **UUID como Primary Key** - Todos os models usam UUID
✅ **Soft Delete** - Exclusão lógica com `is_active`
✅ **Timestamps** - `created_at` e `updated_at` automáticos
✅ **TenantViewSet** - Base class para isolamento por tenant
✅ **Permissões Granulares** - Sistema de permissões flexível
✅ **Documentação OpenAPI** - Todas as APIs documentadas
✅ **Exception Handling** - Tratamento padronizado de erros
✅ **Structured Logging** - Logs estruturados para monitoramento

## 🚀 Deploy e Produção

### Variáveis de Ambiente
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:5432/wbjj_prod
REDIS_URL=redis://host:6379/0
ALLOWED_HOSTS=api.wbjj.com,admin.wbjj.com
CORS_ALLOWED_ORIGINS=https://app.wbjj.com,https://admin.wbjj.com
```

### Health Checks para Load Balancer
```nginx
# Nginx config
location /health/quick/ {
    proxy_pass http://backend;
    access_log off;
}
```

## 📞 Suporte

1. **Documentação**: Consulte [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Exemplos**: Veja [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
3. **Interface**: Teste em http://localhost:8000/api/docs/
4. **Issues**: Use o sistema de issues do repositório

---

**Status**: ✅ Produção Ready
**Versão**: 1.0.0
**Última atualização**: Janeiro 2024
