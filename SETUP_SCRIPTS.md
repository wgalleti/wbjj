# Scripts de Setup - T001: Setup Repositório e Ambiente

## 🎯 Objetivo
Implementar T001 conforme especificação no TASKS.md:
- Configurar monorepo com estrutura backend/frontend/mobile
- Setup Docker Compose para desenvolvimento
- Configurar Git com hooks básicos
- Documentar guia de setup para desenvolvedores

## 📁 Estrutura Final Esperada
```
config/
├── backend/          # Django + DRF
├── frontend/         # Vue.js 3 + Tailwind
├── mobile/           # Flutter
├── docker-compose.yml
├── .gitignore
├── README.md
└── docs/
```

---

## 🐍 BACKEND SETUP (Django + UV)

### 1. Estrutura e Dependências
```bash
# Já criado - verificar se está correto
cd backend

# Verificar estrutura atual
ls -la

# Verificar se UV está funcionando
uv --version

# Instalar dependências de desenvolvimento
uv add --dev pre-commit

# Ativar pre-commit hooks
source .venv/bin/activate
pre-commit install

# Verificar instalação e Django
uv pip list | head -10
python manage.py check
```

### 2. Configuração Django Inicial
```bash
# Dentro de backend/ com ambiente ativado
cd backend
source .venv/bin/activate

# Criar projeto Django
python -m django startproject config .

# Mover settings para estrutura modular
mkdir -p config/settings
mv config/settings.py config/settings/base.py

# Criar __init__.py para settings
echo "from .development import *" > config/settings/__init__.py
```

### 3. Arquivos de Configuração Django
```bash
# Criar settings de desenvolvimento
cat > config/settings/development.py << 'EOF'
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Temporário para setup inicial
        'NAME': 'wbjj_dev',
        'USER': 'wbjj_user',
        'PASSWORD': 'wbjj_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# NOTA: Será alterado para 'django_tenant_schemas.postgresql_backend' na T004

# Cache Redis para desenvolvimento
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Debug toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']
EOF

# Criar settings de produção
cat > config/settings/production.py << 'EOF'
from .base import *
from decouple import config, Csv

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': 'django_tenant_schemas.postgresql_backend',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
EOF

# Criar settings de teste
cat > config/settings/testing.py << 'EOF'
from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django_tenant_schemas.postgresql_backend',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Cache em memória para testes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
EOF
```

### 4. Environment Files
```bash
# Criar .env para desenvolvimento
cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DB_NAME=wbjj_dev
DB_USER=wbjj_user
DB_PASSWORD=wbjj_pass
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
ALLOWED_HOSTS=localhost,127.0.0.1,.localhost
EOF

# Criar .env.example
cat > .env.example << 'EOF'
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_NAME=wbjj_prod
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
REDIS_URL=redis://your-redis-host:6379
ALLOWED_HOSTS=yourdomain.com,.yourdomain.com
SENTRY_DSN=your-sentry-dsn
EOF
```

### 5. Estrutura de Apps Django
```bash
# Criar apps Django
mkdir -p apps/{core,tenants,authentication,students,payments}

# Criar __init__.py para cada app
for app in core tenants authentication students payments; do
    touch apps/$app/__init__.py
    touch apps/$app/models.py
    touch apps/$app/views.py
    touch apps/$app/serializers.py
    touch apps/$app/urls.py
    touch apps/$app/admin.py
    touch apps/$app/apps.py
done
```

---

## 🌐 FRONTEND SETUP (Vue.js 3)

### 1. Criar Projeto Vue.js
```bash
# Voltar para raiz do projeto
cd ..

# Criar projeto Vue.js com Vite
npm create vue@latest frontend

# Opções a escolher:
# ✅ TypeScript: No (MVP em JavaScript)
# ✅ JSX: No
# ✅ Vue Router: Yes
# ✅ Pinia: Yes
# ✅ Vitest: Yes
# ✅ E2E Testing: No (por enquanto)
# ✅ ESLint: Yes
# ✅ Prettier: Yes

cd frontend
npm install
```

### 2. Instalar Dependências Vue
```bash
# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Shadcn Vue
npx shadcn-vue@latest init

# Outras dependências
npm install axios pinia-plugin-persistedstate
npm install -D @tailwindcss/forms @tailwindcss/typography
```

### 3. Configurar Tailwind
```bash
# Atualizar tailwind.config.js
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cores do wBJJ - podem ser customizadas por tenant
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
EOF

# Criar arquivo CSS principal
cat > src/assets/main.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors;
  }
}
EOF
```

### 4. Estrutura de Pastas Vue
```bash
# Criar estrutura de pastas
mkdir -p src/{components/{ui,layout,forms},views/{auth,dashboard,students},stores,utils,api,types}

# Criar arquivos base
touch src/api/client.js
touch src/api/auth.js
touch src/stores/auth.js
touch src/stores/tenant.js
touch src/utils/constants.js
```

### 5. Configuração Vite
```bash
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
EOF
```

---

## 📱 MOBILE SETUP (Flutter)

### 1. Criar Projeto Flutter
```bash
# Voltar para raiz
cd ..

# Verificar Flutter
flutter doctor

# Criar projeto Flutter
flutter create mobile --project-name wbjj_mobile --org com.wbjj

cd mobile
```

### 2. Configurar Dependências Flutter
```bash
# Adicionar dependências principais
flutter pub add http dio riverpod flutter_riverpod shared_preferences
flutter pub add go_router cached_network_image
flutter pub add material3_tokens material_color_utilities

# Dependências de desenvolvimento
flutter pub add --dev flutter_test build_runner json_annotation json_serializable

# Atualizar pubspec.yaml com configurações
cat >> pubspec.yaml << 'EOF'

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/

  fonts:
    - family: Inter
      fonts:
        - asset: assets/fonts/Inter-Regular.ttf
        - asset: assets/fonts/Inter-Medium.ttf
          weight: 500
        - asset: assets/fonts/Inter-SemiBold.ttf
          weight: 600
EOF
```

### 3. Estrutura de Pastas Flutter
```bash
# Criar estrutura de pastas
mkdir -p lib/{features/{auth,dashboard,students,notifications},shared/{models,providers,widgets,utils,api},core/{theme,router,constants}}

# Criar assets
mkdir -p assets/{images,icons,fonts}

# Arquivos base
touch lib/core/theme/app_theme.dart
touch lib/core/router/app_router.dart
touch lib/shared/api/api_client.dart
touch lib/shared/models/user.dart
touch lib/shared/providers/auth_provider.dart
```

### 4. Configurações Android/iOS
```bash
# Android - atualizar android/app/build.gradle
cat >> android/app/build.gradle << 'EOF'

android {
    compileSdkVersion 34
    
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 34
    }
}
EOF

# iOS - atualizar ios/Runner/Info.plist (adicionar permissões básicas)
```

---

## 🐳 DOCKER SETUP

### 1. Docker Compose Principal
```bash
# Voltar para raiz
cd ..

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: wbjj_dev
      POSTGRES_USER: wbjj_user
      POSTGRES_PASSWORD: wbjj_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Backend Django
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_venv:/app/.venv
    environment:
      - DEBUG=True
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
    command: python manage.py runserver 0.0.0.0:8000

  # Frontend Vue.js
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - frontend_modules:/app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host 0.0.0.0

volumes:
  postgres_data:
  redis_data:
  backend_venv:
  frontend_modules:
EOF
```

### 2. Dockerfiles de Desenvolvimento
```bash
# Backend Dockerfile
mkdir -p docker/backend
cat > backend/Dockerfile.dev << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Instalar UV
RUN pip install uv

# Copiar arquivos de dependências
COPY pyproject.toml ./
COPY uv.lock ./

# Instalar dependências
RUN uv venv && uv pip install -e .

# Copiar código
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

# Frontend Dockerfile  
cat > frontend/Dockerfile.dev << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
EOF
```

### 3. Scripts de PostgreSQL
```bash
mkdir -p docker/postgres

cat > docker/postgres/init.sql << 'EOF'
-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Criar schema público se não existir
CREATE SCHEMA IF NOT EXISTS public;

-- Configurações para multitenancy
ALTER DATABASE wbjj_dev SET search_path TO public;
EOF
```

---

## 🔧 CONFIGURAÇÕES GERAIS

### 1. Gitignore Global
```bash
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov

# Production builds
dist/
build/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# Flutter
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
build/
ios/Pods/
ios/.symlinks/
android/.gradle/
android/app/debug/
android/app/profile/
android/app/release/

# Docker
.docker/

# Temporary files
*.tmp
*.temp
EOF
```

### 2. README Principal
```bash
cat > README.md << 'EOF'
# wBJJ - Sistema de Gestão para Academias de Jiu-Jitsu

Sistema completo de gestão para academias de jiu-jitsu com multitenancy, incluindo backend API, dashboard web e aplicativo mobile.

## 🏗️ Arquitetura

```
config/
├── backend/    # Django + DRF API
├── frontend/   # Vue.js 3 Dashboard
├── mobile/     # Flutter App
└── docs/       # Documentação
```

## 🚀 Quick Start

### Requisitos
- Python 3.11+
- Node.js 18+
- Flutter 3.0+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Setup Completo
```bash
# 1. Clonar repositório
git clone <repo-url>
cd wBJJ

# 2. Subir infraestrutura
docker-compose up -d postgres redis

# 3. Backend
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .
python manage.py migrate
python manage.py runserver

# 4. Frontend
cd ../frontend
npm install
npm run dev

# 5. Mobile
cd ../mobile
flutter pub get
flutter run
```

### URLs de Desenvolvimento
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📖 Documentação

- [Arquitetura](doc/ARCHITECTURE.md)
- [Backend](doc/backend/README.md)
- [Frontend](doc/web/README.md)
- [Mobile](doc/app/README.md)
- [Tarefas](doc/TASKS.md)

## 🤝 Desenvolvimento

### Workflow
1. Ler `backend/CONTEXT.md` antes de trabalhar no backend
2. Seguir padrões estabelecidos em cada componente
3. Executar testes antes de commit
4. Usar pre-commit hooks

### Comandos Úteis
```bash
# Backend
cd backend && uv add <package>       # Adicionar dependência
pytest                              # Executar testes
ruff check . && black .             # Linting e formatação

# Frontend  
cd frontend && npm install <package> # Adicionar dependência
npm run test                        # Executar testes
npm run lint                        # Linting

# Mobile
cd mobile && flutter pub add <package> # Adicionar dependência
flutter test                           # Executar testes
flutter analyze                        # Análise de código
```

## 📋 Status das Tarefas

Ver [TASKS.md](doc/TASKS.md) para roadmap completo.

**Atual**: T001 - Setup Repositório ✅

## 🏷️ Tecnologias

- **Backend**: Django 4.2, DRF, PostgreSQL, Redis
- **Frontend**: Vue.js 3, Tailwind, Shadcn/Vue
- **Mobile**: Flutter, Material 3
- **Infra**: Docker, UV, Vite
EOF
```

### 3. Scripts de Desenvolvimento
```bash
mkdir -p scripts

# Script de setup completo
cat > scripts/setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Setup completo wBJJ..."

# Backend
echo "📦 Configurando backend..."
cd backend
if [ ! -d ".venv" ]; then
    uv venv
fi
source .venv/bin/activate
uv pip install -e .
pre-commit install

# Frontend
echo "🌐 Configurando frontend..."
cd ../frontend
npm install

# Mobile
echo "📱 Configurando mobile..."
cd ../mobile
flutter pub get

# Docker
echo "🐳 Iniciando infraestrutura..."
cd ..
docker-compose up -d postgres redis

echo "✅ Setup completo! URLs:"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  Docs: http://localhost:8000/api/docs/"
EOF

chmod +x scripts/setup.sh
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Backend
- [ ] `cd backend && uv pip list` mostra dependências
- [ ] `python manage.py check` passa sem erros
- [ ] `pre-commit run --all-files` executa
- [ ] Estrutura de apps criada

### Frontend  
- [ ] `cd frontend && npm run dev` inicia servidor
- [ ] Tailwind configurado
- [ ] Shadcn funcionando
- [ ] Estrutura de pastas criada

### Mobile
- [ ] `cd mobile && flutter doctor` sem problemas críticos
- [ ] `flutter pub get` instala dependências
- [ ] `flutter analyze` passa
- [ ] Estrutura de pastas criada

### Docker
- [ ] `docker-compose up -d` inicia serviços
- [ ] PostgreSQL acessível em localhost:5432
- [ ] Redis acessível em localhost:6379

### Geral
- [ ] `.gitignore` configurado
- [ ] `README.md` criado com instruções
- [ ] Scripts de setup funcionando

---

## 📞 Próximos Passos

Após executar estes scripts:

1. **Marcar T001 como completa**
2. **Iniciar T002 - Modelagem do Banco de Dados**
3. **Validar que todos os serviços estão funcionando**
4. **Commit inicial do setup**

**Total estimado**: 4 horas conforme T001 