# Frontend Web - wBJJ Admin Dashboard

## Visão Geral
O frontend web do wBJJ é uma aplicação administrativa completa que permite o gerenciamento de academias de jiu-jitsu, incluindo dashboard executivo, gestão de alunos, controle financeiro e landing pages personalizadas por filial.

## Stack Tecnológico

### Frontend Framework
**Vue.js 3** - Escolha para MVP:
- ✅ **Produtividade**: Desenvolvimento rápido
- ✅ **Learning curve**: Mais simples que React
- ✅ **Template syntax**: Familiar e intuitivo
- ✅ **Performance**: Adequada para MVP
- ✅ **Bundle size**: Menor footprint

### UI e Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/Vue**: Componentes prontos
- **Heroicons**: Ícones consistentes
- **CSS Transitions**: Animações nativas Vue

### Estado e Dados
- **Pinia**: Estado global oficial Vue 3
- **VueUse**: Composables utilitários
- **Axios**: Cliente HTTP simples
- **Vue Router**: Roteamento oficial

### Desenvolvimento (MVP Simplificado)
- **JavaScript**: Sem TypeScript para agilidade
- **ESLint**: Linting básico
- **Prettier**: Formatação de código
- **Vite**: Build tool rápido

## Arquitetura do Frontend

### Estrutura de Diretórios
```
web/
├── src/
│   ├── main.js                 # Entry point da aplicação
│   ├── App.vue                 # Componente raiz
│   ├── router/
│   │   ├── index.js            # Configuração de rotas
│   │   ├── auth.js             # Rotas de autenticação
│   │   └── guards.js           # Guards de navegação
│   ├── views/                  # Páginas da aplicação
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   ├── dashboard/
│   │   │   ├── DashboardView.vue
│   │   │   ├── StudentsView.vue
│   │   │   ├── PaymentsView.vue
│   │   │   ├── ReportsView.vue
│   │   │   └── SettingsView.vue
│   │   └── landing/
│   │       └── LandingView.vue
│   ├── components/             # Componentes reutilizáveis
│   │   ├── ui/                 # Componentes base do Shadcn
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   ├── Card.vue
│   │   │   └── Dialog.vue
│   │   ├── forms/              # Componentes de formulário
│   │   │   ├── StudentForm.vue
│   │   │   ├── PaymentForm.vue
│   │   │   └── LoginForm.vue
│   │   ├── charts/             # Componentes de gráficos
│   │   │   ├── RevenueChart.vue
│   │   │   └── StudentsChart.vue
│   │   ├── tables/             # Componentes de tabelas
│   │   │   ├── StudentsTable.vue
│   │   │   └── PaymentsTable.vue
│   │   └── layout/             # Componentes de layout
│   │       ├── AppHeader.vue
│   │       ├── AppSidebar.vue
│   │       └── AppFooter.vue
│   ├── composables/            # Composables Vue
│   │   ├── useAuth.js          # Composable de autenticação
│   │   ├── useTenant.js        # Composable de tenant
│   │   ├── useApi.js           # Composable para API calls
│   │   └── useTheme.js         # Composable para temas
│   ├── services/               # Serviços de API
│   │   ├── api.js              # Cliente API base
│   │   ├── auth.js             # Serviços de autenticação
│   │   ├── students.js         # Serviços de alunos
│   │   ├── payments.js         # Serviços financeiros
│   │   └── tenants.js          # Serviços de tenant
│   ├── stores/                 # Pinia stores
│   │   ├── auth.js             # Store de autenticação
│   │   ├── tenant.js           # Store de tenant
│   │   ├── students.js         # Store de alunos
│   │   └── ui.js               # Store de UI
│   ├── utils/                  # Utilitários
│   │   ├── constants.js        # Constantes
│   │   ├── helpers.js          # Funções auxiliares
│   │   ├── formatters.js       # Formatadores
│   │   └── validators.js       # Validadores
│   └── assets/                 # Assets do projeto
│       ├── css/
│       │   ├── main.css        # Estilos principais
│       │   └── themes/         # Temas por tenant
│       ├── images/
│       └── icons/
├── public/
│   ├── assets/                 # Assets estáticos
│   ├── tenant-assets/          # Assets por tenant
│   │   ├── tenant-1/
│   │   │   ├── logo.png
│   │   │   └── theme.css
│   │   └── tenant-2/
│   ├── favicon.ico
│   └── index.html
├── tests/
│   ├── unit/                   # Testes unitários
│   ├── e2e/                    # Testes E2E
│   └── setup.js                # Configuração de testes
├── vite.config.js              # Configuração Vite
├── tailwind.config.js          # Configuração Tailwind
├── package.json
└── docs/
    ├── components.md           # Documentação de componentes
    └── deployment.md           # Guia de deploy
```

## Implementação Multitenancy

### Detecção de Tenant (MVP Simplificado)
```javascript
// composables/useTenant.js
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { tenantService } from '@/services/tenants'

export function useTenant() {
  const tenant = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const router = useRouter()

  const subdomain = computed(() => {
    if (typeof window === 'undefined') return null
    return window.location.hostname.split('.')[0]
  })

  const loadTenant = async () => {
    loading.value = true
    error.value = null

    try {
      // MVP: Buscar tenant por subdomínio via API
      const tenantData = await tenantService.getBySubdomain(subdomain.value)
      if (!tenantData) {
        throw new Error('Academia não encontrada')
      }

      tenant.value = tenantData
      applyTenantTheme(tenantData)

    } catch (err) {
      error.value = err.message
      console.error('Erro ao carregar tenant:', err)
      router.push('/tenant-not-found')
    } finally {
      loading.value = false
    }
  }

  const applyTenantTheme = (tenantData) => {
    // Aplicar CSS custom properties
    document.documentElement.style.setProperty('--primary-color', tenantData.primary_color)
    document.documentElement.style.setProperty('--secondary-color', tenantData.secondary_color)

    // Trocar favicon se disponível
    if (tenantData.favicon_url) {
      const favicon = document.querySelector('link[rel="icon"]')
      if (favicon) {
        favicon.href = tenantData.favicon_url
      }
    }

    // Trocar logo se disponível
    if (tenantData.logo_url) {
      const logo = document.querySelector('.tenant-logo')
      if (logo) {
        logo.src = tenantData.logo_url
      }
    }

    // Atualizar título da página
    document.title = `${tenantData.name} - Sistema de Gestão`
  }

  return {
    tenant,
    loading,
    error,
    subdomain,
    loadTenant,
    applyTenantTheme
  }
}
```

### Serviço de Tenant (MVP)
```javascript
// services/tenants.js
import { api } from './api'

export const tenantService = {
  /**
   * Buscar tenant por subdomínio
   * MVP: Endpoint simples que retorna dados do tenant
   */
  async getBySubdomain(subdomain) {
    try {
      const response = await api.get(`/api/v1/tenants/by-subdomain/${subdomain}/`)
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * Validar se tenant existe e está ativo
   */
  async validateTenant(subdomain) {
    try {
      const response = await api.get(`/api/v1/tenants/validate/${subdomain}/`)
      return response.data
    } catch (error) {
      return null
    }
  },

  /**
   * Obter configurações do tenant atual
   */
  async getCurrentTenantConfig() {
    try {
      const response = await api.get('/api/v1/tenants/current/config/')
      return response.data
    } catch (error) {
      throw error
    }
  }
}
```

### Router Guards para Tenant (Simplificado)
```javascript
// router/guards.js
import { tenantService } from '@/services/tenants'

export async function tenantGuard(to, from, next) {
  // Extrair subdomain
  const hostname = window.location.hostname
  const subdomain = hostname.split('.')[0]

  // Pular validação para domínios principais
  const mainDomains = ['www', 'admin', 'api', 'localhost', '127']
  if (mainDomains.includes(subdomain) || subdomain.startsWith('127')) {
    return next()
  }

  try {
    // MVP: Validação simples via API
    const tenant = await tenantService.validateTenant(subdomain)

    if (!tenant) {
      return next('/tenant-not-found')
    }

    // Adicionar tenant ao contexto da rota
    to.meta.tenant = tenant
    next()

  } catch (error) {
    console.error('Erro na validação do tenant:', error)
    next('/error')
  }
}

export function authGuard(to, from, next) {
  const token = localStorage.getItem('auth_token')

  if (!token && to.meta.requiresAuth) {
    return next('/login')
  }

  next()
}
```

### Store de Tenant (Pinia)
```javascript
// stores/tenant.js
import { defineStore } from 'pinia'
import { tenantService } from '@/services/tenants'

export const useTenantStore = defineStore('tenant', {
  state: () => ({
    current: null,
    loading: false,
    error: null,
    config: null
  }),

  getters: {
    isLoaded: (state) => state.current !== null,
    subdomain: (state) => state.current?.subdomain,
    name: (state) => state.current?.name,
    colors: (state) => ({
      primary: state.current?.primary_color || '#3B82F6',
      secondary: state.current?.secondary_color || '#1E40AF'
    }),
    logo: (state) => state.current?.logo_url,
    isActive: (state) => state.current?.is_active || false
  },

  actions: {
    async loadTenant() {
      this.loading = true
      this.error = null

      try {
        // Extrair subdomain do hostname
        const hostname = window.location.hostname
        const subdomain = hostname.split('.')[0]

        // MVP: Buscar tenant via API
        const tenant = await tenantService.getBySubdomain(subdomain)

        if (!tenant) {
          throw new Error('Academia não encontrada')
        }

        this.current = tenant
        this.applyTheme()

      } catch (error) {
        this.error = error.message
        console.error('Erro ao carregar tenant:', error)
      } finally {
        this.loading = false
      }
    },

    async loadConfig() {
      try {
        this.config = await tenantService.getCurrentTenantConfig()
      } catch (error) {
        console.error('Erro ao carregar configurações:', error)
      }
    },

    applyTheme() {
      if (!this.current) return

      // Aplicar CSS custom properties
      const root = document.documentElement
      root.style.setProperty('--primary-color', this.colors.primary)
      root.style.setProperty('--secondary-color', this.colors.secondary)

      // Atualizar favicon
      if (this.current.favicon_url) {
        const favicon = document.querySelector('link[rel="icon"]')
        if (favicon) {
          favicon.href = this.current.favicon_url
        }
      }

      // Atualizar título
      document.title = `${this.name} - Sistema de Gestão`
    },

    clearTenant() {
      this.current = null
      this.config = null
      this.error = null
    }
  }
})
```

### Componente de Tenant Loading
```vue
<!-- components/tenant/TenantLoader.vue -->
<template>
  <div v-if="loading" class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600">Carregando academia...</p>
    </div>
  </div>

  <div v-else-if="error" class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="text-red-600 text-6xl mb-4">⚠️</div>
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Academia não encontrada</h1>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <button
        @click="retry"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
      >
        Tentar novamente
      </button>
    </div>
  </div>

  <slot v-else />
</template>

<script>
import { computed } from 'vue'
import { useTenantStore } from '@/stores/tenant'

export default {
  name: 'TenantLoader',
  setup() {
    const tenantStore = useTenantStore()

    const loading = computed(() => tenantStore.loading)
    const error = computed(() => tenantStore.error)

    const retry = () => {
      tenantStore.loadTenant()
    }

    return {
      loading,
      error,
      retry
    }
  }
}
</script>
```

### Débito Técnico - Multitenancy V2.0

#### Limitações da Abordagem MVP
1. **Dependência de API**: Cada carregamento de página faz request para buscar tenant
2. **Cache Limitado**: Cache apenas no browser, não no servidor
3. **Personalização Limitada**: Apenas cores e logo básicos
4. **Performance**: Latência adicional para carregar configurações

#### Migração Planejada para V2.0
```javascript
// Estrutura planejada para V2.0 com SSR e cache otimizado

// middleware/tenant.js (Nuxt.js V2.0)
export default async function ({ route, store, error, redirect }) {
  // Server-side tenant detection
  const subdomain = process.server
    ? req.headers.host.split('.')[0]
    : window.location.hostname.split('.')[0]

  // Cache otimizado com Redis
  const tenant = await $cache.get(`tenant:${subdomain}`) ||
                 await $api.tenants.getBySubdomain(subdomain)

  if (!tenant) {
    return error({ statusCode: 404, message: 'Academia não encontrada' })
  }

  // Aplicar configurações no servidor
  store.commit('tenant/SET_CURRENT', tenant)

  // Injetar CSS no servidor
  if (process.server) {
    route.meta.theme = {
      primary: tenant.primary_color,
      secondary: tenant.secondary_color
    }
  }
}
```

#### Benefícios da Migração V2.0
- **SSR**: Tenant detectado no servidor
- **Cache Redis**: Performance otimizada
- **CSS Injection**: Estilos aplicados no servidor
- **SEO**: Melhor indexação por tenant
- **Personalização Avançada**: Layouts customizados por tenant

#### Estimativa de Migração V2.0
- **Tempo**: 2-3 semanas (80-120 horas)
- **Custo**: R$ 9.600 - R$ 14.400
- **Complexidade**: Média
- **Benefícios**: Performance, SEO, UX melhorada

## Componentes Principais

### Layout do Dashboard
```vue
<!-- components/layout/DashboardLayout.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading state -->
    <div v-if="isLoading" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Main layout -->
    <div v-else class="min-h-screen">
      <AppSidebar :tenant="tenant" />

      <div class="lg:pl-72">
        <AppHeader :user="user" :tenant="tenant" />

        <main class="py-6">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <slot />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'

export default {
  name: 'DashboardLayout',
  components: {
    AppSidebar,
    AppHeader
  },
  setup() {
    const authStore = useAuthStore()
    const tenantStore = useTenantStore()

    const user = computed(() => authStore.user)
    const tenant = computed(() => tenantStore.current)
    const isLoading = computed(() => authStore.loading || tenantStore.loading)

    onMounted(async () => {
      // Garantir que tenant e auth estão carregados
      if (!tenant.value) {
        await tenantStore.loadTenant()
      }

      if (!user.value) {
        await authStore.checkAuth()
      }
    })

    return {
      user,
      tenant,
      isLoading
    }
  }
}
</script>
```

### Componente de Student Management
```vue
<!-- views/dashboard/StudentsView.vue -->
<template>
  <DashboardLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Alunos</h1>
        <button
          @click="showAddModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Adicionar Aluno
        </button>
      </div>

      <!-- Filtros -->
      <div class="flex space-x-4">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Buscar alunos..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <select
          v-model="selectedBelt"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todas as faixas</option>
          <option v-for="belt in belts" :key="belt" :value="belt">
            {{ belt }}
          </option>
        </select>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-8 text-red-600">
        Erro ao carregar alunos: {{ error }}
      </div>

      <!-- Students Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StudentCard
          v-for="student in filteredStudents"
          :key="student.id"
          :student="student"
          @edit="handleEditStudent"
          @delete="handleDeleteStudent"
        />
      </div>

      <!-- Add Student Modal -->
      <AddStudentModal
        v-if="showAddModal"
        @close="showAddModal = false"
        @success="handleStudentAdded"
      />
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStudentsStore } from '@/stores/students'
import DashboardLayout from '@/components/layout/DashboardLayout.vue'
import StudentCard from '@/components/students/StudentCard.vue'
import AddStudentModal from '@/components/students/AddStudentModal.vue'

export default {
  name: 'StudentsView',
  components: {
    DashboardLayout,
    StudentCard,
    AddStudentModal
  },
  setup() {
    const studentsStore = useStudentsStore()

    const showAddModal = ref(false)
    const searchTerm = ref('')
    const selectedBelt = ref('')

    const belts = ['Branca', 'Azul', 'Roxa', 'Marrom', 'Preta']

    const students = computed(() => studentsStore.students)
    const loading = computed(() => studentsStore.loading)
    const error = computed(() => studentsStore.error)

    const filteredStudents = computed(() => {
      let filtered = students.value

      if (searchTerm.value) {
        filtered = filtered.filter(student =>
          student.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
          student.email.toLowerCase().includes(searchTerm.value.toLowerCase())
        )
      }

      if (selectedBelt.value) {
        filtered = filtered.filter(student => student.belt_color === selectedBelt.value)
      }

      return filtered
    })

    const handleEditStudent = (student) => {
      // TODO: Abrir modal de edição
      console.log('Editar aluno:', student)
    }

    const handleDeleteStudent = async (student) => {
      if (confirm(`Tem certeza que deseja excluir ${student.name}?`)) {
        await studentsStore.deleteStudent(student.id)
      }
    }

    const handleStudentAdded = () => {
      showAddModal.value = false
      studentsStore.loadStudents() // Recarregar lista
    }

    onMounted(() => {
      studentsStore.loadStudents()
    })

    return {
      showAddModal,
      searchTerm,
      selectedBelt,
      belts,
      students,
      loading,
      error,
      filteredStudents,
      handleEditStudent,
      handleDeleteStudent,
      handleStudentAdded
    }
  }
}
</script>
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            // Refetch students
          }}
        />
      )}
    </div>
  );
}
```

### Dashboard Financeiro
```typescript
// components/financial/FinancialDashboard.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { getFinancialSummary } from '@/lib/api';
import RevenueChart from './RevenueChart';
import PaymentStatus from './PaymentStatus';
import FinancialMetrics from './FinancialMetrics';

export default function FinancialDashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['financial-summary'],
    queryFn: getFinancialSummary,
  });

  if (isLoading) return <div>Carregando dados financeiros...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard Financeiro</h1>

      <FinancialMetrics summary={summary} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart data={summary?.revenueChart} />
        <PaymentStatus data={summary?.paymentStatus} />
      </div>
    </div>
  );
}
```

## Sistema de Autenticação

### Hook de Autenticação
```typescript
// hooks/useAuth.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  tenantId: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,

      login: async (email: string, password: string) => {
        try {
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          });

          if (!response.ok) {
            throw new Error('Login failed');
          }

          const { user, token } = await response.json();
          set({ user, token });
        } catch (error) {
          throw error;
        }
      },

      logout: () => {
        set({ user: null, token: null });
      },

      refreshToken: async () => {
        try {
          const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${get().token}`,
            },
          });

          if (response.ok) {
            const { token } = await response.json();
            set({ token });
          } else {
            // Token invalid, logout
            get().logout();
          }
        } catch (error) {
          get().logout();
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

### Proteção de Rotas
```typescript
// components/auth/ProtectedRoute.tsx
'use client';

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

export default function ProtectedRoute({
  children,
  requiredRole
}: ProtectedRouteProps) {
  const { user, token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }

    if (requiredRole && user?.role !== requiredRole) {
      router.push('/unauthorized');
      return;
    }
  }, [user, token, requiredRole, router]);

  if (!token || (requiredRole && user?.role !== requiredRole)) {
    return <div>Carregando...</div>;
  }

  return <>{children}</>;
}
```

## Landing Pages por Tenant

### Template Dinâmico
```typescript
// app/landing/[tenant]/page.tsx
import { getTenantConfig } from '@/lib/api';
import LandingPage from '@/components/landing/LandingPage';

interface LandingPageProps {
  params: {
    tenant: string;
  };
}

export default async function TenantLanding({ params }: LandingPageProps) {
  const tenantConfig = await getTenantConfig(params.tenant);

  if (!tenantConfig) {
    return <div>Academia não encontrada</div>;
  }

  return <LandingPage config={tenantConfig} />;
}

// Componente da Landing Page
// components/landing/LandingPage.tsx
interface LandingPageProps {
  config: TenantConfig;
}

export default function LandingPage({ config }: LandingPageProps) {
  return (
    <div style={{ '--primary': config.theme.primaryColor } as React.CSSProperties}>
      <Header logo={config.theme.logo} />
      <Hero
        title={config.content.heroTitle}
        subtitle={config.content.heroSubtitle}
        image={config.content.heroImage}
      />
      <About content={config.content.about} />
      <Contact info={config.contact} />
      <Footer />
    </div>
  );
}
```

## Configuração e Deploy

### Next.js Config
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'api.wbjj.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Docker Setup
```dockerfile
# Dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

### Tailwind Configuration
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary-color)',
        secondary: 'var(--secondary-color)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

## Testes

### Setup de Testes
```typescript
// tests/setup.ts
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Mock Server (MSW)
```typescript
// tests/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/students', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', name: 'João Silva', belt: 'blue' },
        { id: '2', name: 'Maria Santos', belt: 'white' },
      ])
    );
  }),
];
```

## Estratégia MVP vs V2.0

### MVP (Vue.js simples)
- **Foco**: Entregar rápido e validar mercado
- **Trade-offs**: Débito técnico controlado
- **Timeline**: 4 semanas de desenvolvimento
- **Tecnologia**: Vue.js + JavaScript + Tailwind

### V2.0 (Pós-validação)
- **Foco**: Performance e escalabilidade
- **Tecnologias**: Vue 3 + TypeScript ou migração para framework moderno
- **Features**: PWA, SSR, otimizações avançadas
- **Timeline**: Reescrita planejada pós-MVP

> 📋 **Tarefas detalhadas disponíveis em**: `doc/TASKS.md`
