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

### Detecção de Tenant
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
      const tenantData = await tenantService.getBySubdomain(subdomain.value)
      if (!tenantData) {
        throw new Error('Academia não encontrada')
      }
      
      tenant.value = tenantData
      applyTenantTheme(tenantData.theme)
      
    } catch (err) {
      error.value = err.message
      console.error('Erro ao carregar tenant:', err)
      router.push('/tenant-not-found')
    } finally {
      loading.value = false
    }
  }

  const applyTenantTheme = (theme) => {
    // Aplicar CSS custom properties
    document.documentElement.style.setProperty('--primary-color', theme.primaryColor)
    document.documentElement.style.setProperty('--secondary-color', theme.secondaryColor)
    
    // Trocar favicon
    const favicon = document.querySelector('link[rel="icon"]')
    if (favicon) {
      favicon.href = theme.favicon
    }
    
    // Trocar logo
    const logo = document.querySelector('.tenant-logo')
    if (logo) {
      logo.src = theme.logo
    }
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

### Router Guards para Tenant
```javascript
// router/guards.js
import { tenantService } from '@/services/tenants'

export async function tenantGuard(to, from, next) {
  // Extrair subdomain
  const hostname = window.location.hostname
  const subdomain = hostname.split('.')[0]
  
  // Pular validação para domínios principais
  const mainDomains = ['www', 'admin', 'api', 'localhost']
  if (mainDomains.includes(subdomain)) {
    return next()
  }
  
  try {
    // Verificar se tenant existe
    const tenant = await tenantService.validateTenant(subdomain)
    
    if (!tenant) {
      return next('/tenant-not-found')
    }
    
    // Adicionar tenant ao contexto global
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

### Configuração de Rotas com Guards
```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { tenantGuard, authGuard } from './guards'

// Views
import DashboardView from '@/views/dashboard/DashboardView.vue'
import StudentsView from '@/views/dashboard/StudentsView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import LandingView from '@/views/landing/LandingView.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView,
    beforeEnter: tenantGuard
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    beforeEnter: tenantGuard
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
    beforeEnter: [tenantGuard, authGuard]
  },
  {
    path: '/students',
    name: 'students',
    component: StudentsView,
    meta: { requiresAuth: true },
    beforeEnter: [tenantGuard, authGuard]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

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