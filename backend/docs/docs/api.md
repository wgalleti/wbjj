# wBJJ API Documentation

Documentação completa da API REST para o sistema de gestão de academias de jiu-jitsu.

## 📖 Visão Geral

A wBJJ API é uma REST API robusta construída com Django REST Framework, projetada para gerenciar academias de jiu-jitsu com suporte completo a multitenancy.

### Características Principais

- **Multitenancy**: Isolamento total de dados por academia
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
POST /api/v1/auth/login/
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
    "firstName": "Admin",
    "lastName": "Sistema",
    "role": "admin"
  }
}
```

#### 2. Renovar Token

```http
POST /api/v1/auth/refresh/
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

#### 3. Usar Token nas Requisições

```http
GET /api/v1/students/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000
```

### Headers Obrigatórios

| Header | Descrição | Exemplo |
|--------|-----------|---------|
| `Authorization` | Token JWT | `Bearer eyJ0eXAi...` |
| `X-Tenant-ID` | ID da academia (UUID) | `123e4567-e89b-12d3...` |
| `Content-Type` | Tipo de conteúdo | `application/json` |

## 🏢 Multitenancy

Cada academia é um **tenant** isolado. O isolamento é garantido pelo header `X-Tenant-ID`.

### Como Funciona

1. **Criação do Tenant**: Cada academia recebe um UUID único
2. **Isolamento de Dados**: Todos os dados são filtrados pelo tenant
3. **Segurança**: Impossível acessar dados de outras academias

### Exemplo de Uso

```javascript
// Configurar cliente HTTP
const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'X-Tenant-ID': '123e4567-e89b-12d3-a456-426614174000'
  }
});

// Todas as requisições serão isoladas para essa academia
client.get('/students/');  // Só retorna alunos dessa academia
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
  "next": "http://localhost:8000/api/v1/students/?page=3&page_size=10",
  "previous": "http://localhost:8000/api/v1/students/?page=1&page_size=10",
  "pageSize": 10,
  "totalPages": 13,
  "currentPage": 2,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "joao.silva@email.com",
      "firstName": "João",
      "lastName": "Silva"
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
GET /api/v1/students/?ordering=first_name,last_name
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
  "email": "joao.silva@email.com",
  "firstName": "João",
  "lastName": "Silva",
  "phone": "(11) 99999-9999",
  "beltColor": "white",
  "status": "active",
  "birthDate": "1990-01-15",
  "address": "Rua das Flores, 123",
  "emergencyContact": "Maria Silva - (11) 88888-8888"
}
```

### Graduar Aluno

```http
POST /api/v1/students/{id}/graduate/
Content-Type: application/json

{
  "newBelt": "blue",
  "graduationDate": "2024-01-15",
  "notes": "Graduação merecida, aluno dedicado"
}
```

### Registrar Presença

```http
POST /api/v1/attendances/
Content-Type: application/json

{
  "student": "123e4567-e89b-12d3-a456-426614174000",
  "checkinTime": "2024-01-15T19:00:00Z",
  "classType": "gi",
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
  "dueDate": "2024-02-15",
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
  "paymentMethod": "123e4567-e89b-12d3-a456-426614174001",
  "amount": "150.00",
  "paymentDate": "2024-01-15",
  "notes": "Pagamento via PIX"
}
```

### Confirmar Pagamento

```http
POST /api/v1/payments/{id}/confirm/
Content-Type: application/json

{
  "confirmed": true,
  "confirmationNotes": "Pagamento confirmado no banco"
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

#### Validação (422)
```json
{
  "error": true,
  "message": "Erro de validação",
  "details": {
    "email": ["Este campo é obrigatório."],
    "beltColor": ["Valor inválido. Escolha entre: white, blue, purple, brown, black."]
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
  private baseURL = 'http://localhost:8000/api/v1';
  private tenantId: string;
  private token?: string;

  constructor(tenantId: string) {
    this.tenantId = tenantId;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/login/`, {
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
      'X-Tenant-ID': this.tenantId,
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
// Inicializar cliente
const api = new WBJJApiClient('123e4567-e89b-12d3-a456-426614174000');

// Login
await api.login('admin@academia.com', 'senha123');

// Listar alunos
const students = await api.get<ApiResponse<Student>>('/students/');

// Criar aluno
const newStudent = await api.post<Student>('/students/', {
  email: 'novo.aluno@email.com',
  firstName: 'Novo',
  lastName: 'Aluno',
  beltColor: 'white'
});

// Graduar aluno
await api.post(`/students/${newStudent.id}/graduate/`, {
  newBelt: 'blue',
  graduationDate: '2024-01-15'
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
        const response = await axios.post('/api/v1/auth/refresh/', {
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
  const tenantId = ref<string | null>(null);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });

    token.value = response.access;
    user.value = response.user;

    localStorage.setItem('accessToken', response.access);
    localStorage.setItem('refreshToken', response.refresh);
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  };

  return { token, user, tenantId, login, logout };
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
ALLOWED_HOSTS=api.wbjj.com,admin.wbjj.com
CORS_ALLOWED_ORIGINS=https://app.wbjj.com,https://admin.wbjj.com
```

### Health Check para Load Balancer

```nginx
# Nginx health check
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
   - `tenantId`: `123e4567-e89b-12d3-a456-426614174000`
   - `token`: (obtido após login)

### Rate Limiting (Futuro)

A API será configurada com rate limiting em produção:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## 📞 Suporte

Para dúvidas técnicas ou problemas:

1. Consulte esta documentação
2. Verifique o [schema OpenAPI](http://localhost:8000/api/schema/)
3. Teste na [interface Swagger](http://localhost:8000/api/docs/)
4. Consulte os logs da aplicação

---

**Versão da API**: 1.0.0
**Última atualização**: Janeiro 2024
**Ambiente**: Development
