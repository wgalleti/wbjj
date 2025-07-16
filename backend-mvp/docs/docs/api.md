# wBJJ API Documentation - MVP

Documentação completa da API REST para o sistema de gestão de academias de jiu-jitsu - Versão MVP.

## 📖 Visão Geral

A wBJJ API MVP é uma REST API robusta construída com Django REST Framework, projetada para gerenciar academias de jiu-jitsu com suporte a multitenancy simplificado por tenant_id.

### Características Principais

- **Multitenancy MVP**: Isolamento por tenant_id com filtro automático
- **Autenticação JWT**: Tokens seguros com refresh automático
- **Documentação OpenAPI**: Interface Swagger/ReDoc interativa
- **Paginação Automática**: Listagens otimizadas com metadados
- **Filtros Avançados**: Busca e ordenação flexível
- **Health Checks**: Monitoramento completo da aplicação

## 🔐 Autenticação

### JWT (JSON Web Tokens)

A API utiliza JWT para autenticação. Tokens têm duração de 60 minutos e podem ser renovados por até 7 dias.

#### 1. Login (Obter Token)

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "admin@academia.com",
  "password": "senha123"
}
```

**Resposta de Sucesso:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@academia.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "role": "admin"
  }
}
```

#### 2. Renovar Token

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Resposta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. Logout (Blacklist Token)

```http
POST /api/v1/auth/logout/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. Usar Token nas Requisições

```http
GET /api/v1/students/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Headers Obrigatórios

| Header | Descrição | Exemplo |
|--------|-----------|---------|
| `Authorization` | Token JWT | `Bearer eyJ0eXAi...` |
| `Content-Type` | Tipo de conteúdo | `application/json` |

## 🏢 Multitenancy MVP

Cada academia é um **tenant** com isolamento por tenant_id. O tenant é detectado automaticamente pelo subdomínio.

### Como Funciona

1. **Detecção do Tenant**: Subdomínio da URL (ex: `academia-alpha.wbjj.com` → tenant `academia-alpha`)
2. **Middleware**: `TenantMiddleware` detecta e configura `request.tenant`
3. **Filtro Automático**: Todos os dados filtrados por `tenant_id`
4. **Segurança**: Impossível acessar dados de outras academias

### Exemplo de Uso

```javascript
// Configurar cliente HTTP
const client = axios.create({
  baseURL: 'https://academia-alpha.wbjj.com/api/v1',
  // Tenant detectado automaticamente pelo subdomínio
});

// Todas as requisições serão isoladas para essa academia
client.get('/students/');  // Só retorna alunos da academia-alpha
```

### Detecção de Tenant

```http
# Produção - tenant detectado por subdomínio
GET https://academia-alpha.wbjj.com/api/v1/students/

# Desenvolvimento - tenant configurado manualmente
GET http://localhost:8000/api/v1/students/
Host: academia-alpha.localhost
```

## 📄 Paginação

Todas as listagens utilizam paginação automática.

### Parâmetros

| Parâmetro | Descrição | Padrão | Máximo |
|-----------|-----------|--------|--------|
| `page` | Número da página | 1 | - |
| `page_size` | Itens por página | 20 | 100 |

### Exemplo de Requisição

```http
GET /api/v1/students/?page=2&page_size=10
```

### Resposta Paginada

```json
{
  "count": 123,
  "next": "https://academia-alpha.wbjj.com/api/v1/students/?page=3&page_size=10",
  "previous": "https://academia-alpha.wbjj.com/api/v1/students/?page=1&page_size=10",
  "pageSize": 10,
  "totalPages": 13,
  "currentPage": 2,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user": {
        "email": "joao.silva@email.com",
        "first_name": "João",
        "last_name": "Silva"
      },
      "belt_color": "blue",
      "status": "active"
    }
  ]
}
```

## 🔍 Filtros e Busca

### Busca Textual

Use o parâmetro `search` para busca em múltiplos campos:

```http
GET /api/v1/students/?search=João Silva
```

### Ordenação

Use o parâmetro `ordering` (prefixe com `-` para ordem decrescente):

```http
GET /api/v1/students/?ordering=-created_at
GET /api/v1/students/?ordering=user__first_name,user__last_name
```

### Filtros Específicos

Cada endpoint pode ter filtros específicos:

```http
GET /api/v1/students/?belt_color=blue&status=active
GET /api/v1/payments/?payment_date__gte=2024-01-01
```

## 👨‍🎓 Gestão de Alunos

### Listar Alunos

```http
GET /api/v1/students/
```

### Criar Aluno

```http
POST /api/v1/students/
Content-Type: application/json

{
  "user": {
    "email": "joao.silva@email.com",
    "first_name": "João",
    "last_name": "Silva",
    "phone": "(11) 99999-9999"
  },
  "registration_number": "2024001",
  "enrollment_date": "2024-01-15",
  "belt_color": "white",
  "status": "active",
  "emergency_contact_name": "Maria Silva",
  "emergency_contact_phone": "(11) 88888-8888",
  "emergency_contact_relationship": "Mãe"
}
```

### Graduar Aluno

```http
POST /api/v1/students/{id}/graduate/
Content-Type: application/json

{
  "new_belt": "blue",
  "graduation_date": "2024-01-15",
  "notes": "Graduação merecida, aluno dedicado"
}
```

### Registrar Presença

```http
POST /api/v1/attendances/
Content-Type: application/json

{
  "student": "123e4567-e89b-12d3-a456-426614174000",
  "checkin_time": "2024-01-15T19:00:00Z",
  "class_type": "gi",
  "notes": "Treino de raspagem"
}
```

## 💰 Sistema Financeiro

### Criar Fatura

```http
POST /api/v1/invoices/
Content-Type: application/json

{
  "student": "123e4567-e89b-12d3-a456-426614174000",
  "amount": "150.00",
  "due_date": "2024-02-15",
  "reference_month": "2024-01-01",
  "description": "Mensalidade Janeiro 2024",
  "status": "pending"
}
```

### Registrar Pagamento

```http
POST /api/v1/payments/
Content-Type: application/json

{
  "invoice": "123e4567-e89b-12d3-a456-426614174000",
  "payment_method": "123e4567-e89b-12d3-a456-426614174001",
  "amount": "150.00",
  "payment_date": "2024-01-15",
  "notes": "Pagamento via PIX"
}
```

### Confirmar Pagamento

```http
POST /api/v1/payments/{id}/confirm/
Content-Type: application/json

{
  "confirmed": true,
  "confirmation_notes": "Pagamento confirmado no banco"
}
```

## 🏛️ Gestão de Academias (Tenants)

### Listar Academias (Admin)

```http
GET /api/v1/tenants/
```

### Criar Academia

```http
POST /api/v1/tenants/
Content-Type: application/json

{
  "name": "Academia Gracie Barra",
  "subdomain": "gracie-barra",
  "slug": "gracie-barra",
  "email": "contato@graciebarra.com",
  "phone": "(11) 99999-9999",
  "address": "Rua das Academias, 123",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01234-567",
  "monthly_fee": "180.00"
}
```

### Obter Academia Atual

```http
GET /api/v1/tenants/current/
```

**Resposta:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Academia Gracie Barra",
  "subdomain": "gracie-barra",
  "slug": "gracie-barra",
  "email": "contato@graciebarra.com",
  "phone": "(11) 99999-9999",
  "address": "Rua das Academias, 123",
  "city": "São Paulo",
  "state": "SP",
  "monthly_fee": "180.00",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🏥 Monitoramento e Health Checks

### Health Check Completo

```http
GET /api/v1/health/
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "development",
  "database": "ok - 25 migrations applied",
  "cache": "ok - read/write successful",
  "memoryUsage": {
    "total": "8.00 GB",
    "available": "6.50 GB",
    "percent": 18.75,
    "status": "ok"
  },
  "diskUsage": {
    "total": "100.00 GB",
    "used": "45.20 GB",
    "free": "54.80 GB",
    "percent": 45.2,
    "status": "ok"
  },
  "uptime": "2 days, 15:30:22",
  "responseTimeMs": 45.32,
  "errors": []
}
```

### Health Checks Específicos

```http
GET /api/v1/health/quick/      # Verificação rápida
GET /api/v1/health/database/   # Só banco de dados
GET /api/v1/health/cache/      # Só cache
GET /api/v1/metrics/           # Métricas detalhadas
```

## 📊 Códigos de Resposta HTTP

| Código | Significado | Quando Usar |
|--------|-------------|-------------|
| 200 | OK | Operação bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 204 | No Content | Operação bem-sucedida sem retorno |
| 400 | Bad Request | Dados inválidos na requisição |
| 401 | Unauthorized | Token ausente ou inválido |
| 403 | Forbidden | Sem permissão para a operação |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Erro de validação |
| 500 | Internal Server Error | Erro interno do servidor |
| 503 | Service Unavailable | Serviço temporariamente indisponível |

## ❌ Tratamento de Erros

### Formato Padrão de Erro

```json
{
  "error": true,
  "message": "Erro de validação",
  "details": {
    "email": ["Este email já está em uso."],
    "password": ["A senha deve ter pelo menos 8 caracteres."]
  },
  "statusCode": 400,
  "debugInfo": {
    "path": "/api/v1/students/",
    "method": "POST",
    "user": "admin@academia.com"
  }
}
```

### Exemplos de Erros Comuns

#### Token Inválido (401)
```json
{
  "error": true,
  "message": "Token inválido ou expirado",
  "details": {"code": "token_not_valid"},
  "statusCode": 401
}
```

#### Sem Permissão (403)
```json
{
  "error": true,
  "message": "Você não tem permissão para realizar esta ação",
  "details": {"code": "permission_denied"},
  "statusCode": 403
}
```

#### Tenant Não Encontrado (404)
```json
{
  "error": true,
  "message": "Academia não encontrada",
  "details": {"code": "tenant_not_found"},
  "statusCode": 404
}
```

#### Validação (422)
```json
{
  "error": true,
  "message": "Erro de validação",
  "details": {
    "email": ["Este campo é obrigatório."],
    "belt_color": ["Valor inválido. Escolha entre: white, blue, purple, brown, black."]
  },
  "statusCode": 422
}
```

## 🧪 Exemplos de Uso com JavaScript/TypeScript

### Cliente HTTP Base

```typescript
interface ApiResponse<T> {
  count?: number;
  next?: string;
  previous?: string;
  results: T[];
}

class WBJJApiClient {
  private baseURL: string;
  private token?: string;

  constructor(subdomain: string, environment: 'development' | 'production' = 'development') {
    if (environment === 'production') {
      this.baseURL = `https://${subdomain}.wbjj.com/api/v1`;
    } else {
      this.baseURL = 'http://localhost:8000/api/v1';
    }
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access;
      return data;
    }

    throw new Error('Login failed');
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: this.getHeaders()
    });

    if (response.ok) {
      return response.json();
    }

    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });

    if (response.ok) {
      return response.json();
    }

    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
}
```

### Usando o Cliente

```typescript
// Inicializar cliente para academia específica
const api = new WBJJApiClient('academia-alpha', 'production');

// Login
await api.login('admin@academia.com', 'senha123');

// Listar alunos
const students = await api.get<ApiResponse<Student>>('/students/');

// Criar aluno
const newStudent = await api.post<Student>('/students/', {
  user: {
    email: 'novo.aluno@email.com',
    first_name: 'Novo',
    last_name: 'Aluno'
  },
  belt_color: 'white',
  registration_number: '2024002',
  enrollment_date: '2024-01-15'
});

// Graduar aluno
await api.post(`/students/${newStudent.id}/graduate/`, {
  new_belt: 'blue',
  graduation_date: '2024-01-15'
});
```

## 📱 Integração com Frontend

### Interceptor para Auto-refresh de Token

```javascript
// Axios interceptor para renovar token automaticamente
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: refreshToken
        });

        const newToken = response.data.access;
        localStorage.setItem('accessToken', newToken);

        // Repetir requisição original
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Redirect para login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
```

### Gerenciamento de Estado (Pinia/Vuex)

```typescript
// store/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null);
  const user = ref<User | null>(null);
  const tenant = ref<Tenant | null>(null);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/token/', { email, password });

    token.value = response.access;
    user.value = response.user;

    localStorage.setItem('accessToken', response.access);
    localStorage.setItem('refreshToken', response.refresh);

    // Buscar informações do tenant atual
    tenant.value = await api.get('/tenants/current/');
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      await api.post('/auth/logout/', { refresh: refreshToken });
    }

    token.value = null;
    user.value = null;
    tenant.value = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  };

  return { token, user, tenant, login, logout };
});
```

## 🚀 Deploy e Configuração

### Variáveis de Ambiente

```bash
# Backend (.env)
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/wbjj_prod
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=*.wbjj.com,admin.wbjj.com
CORS_ALLOWED_ORIGINS=https://*.wbjj.com,https://admin.wbjj.com
```

### Configuração de Subdomínios

```nginx
# Nginx configuração para subdomínios
server {
    listen 80;
    server_name *.wbjj.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Health check para Load Balancer
location /health/quick/ {
    proxy_pass http://backend;
    proxy_set_header Host $host;
    access_log off;
}
```

## 📚 Recursos Adicionais

### Documentação Interativa

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **Schema OpenAPI**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

### Postman Collection

A API pode ser importada no Postman usando o schema OpenAPI:

1. Abra o Postman
2. Import > Link
3. Cole: `http://localhost:8000/api/schema/`
4. Configure environment variables:
   - `baseUrl`: `http://localhost:8000/api/v1`
   - `subdomain`: `academia-alpha`
   - `token`: (obtido após login)

### Rate Limiting (Futuro)

A API será configurada com rate limiting em produção:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## 🔄 Diferenças MVP vs Versão Completa

### MVP (Atual)
- ✅ **Multitenancy**: Filtro por tenant_id
- ✅ **Detecção**: Subdomínio automático
- ✅ **Performance**: Filtros simples e rápidos
- ✅ **Desenvolvimento**: Setup rápido
- ✅ **Escalabilidade**: Até ~100 tenants

### V2.0 (Futuro)
- 🔄 **Multitenancy**: Schema-per-tenant PostgreSQL
- 🔄 **Detecção**: Domínios customizados
- 🔄 **Performance**: Isolamento total
- 🔄 **Desenvolvimento**: Setup mais complexo
- 🔄 **Escalabilidade**: Ilimitada

## 📞 Suporte

Para dúvidas técnicas ou problemas:

1. Consulte esta documentação
2. Verifique o [schema OpenAPI](http://localhost:8000/api/schema/)
3. Teste na [interface Swagger](http://localhost:8000/api/docs/)
4. Consulte os logs da aplicação

---

**Versão da API**: 1.0.0 MVP
**Última atualização**: Janeiro 2025
**Ambiente**: Development
**Multitenancy**: Tenant ID (MVP)
