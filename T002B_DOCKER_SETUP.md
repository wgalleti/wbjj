# T002B - Docker Compose e Banco de Dados

## 🎯 Objetivo
Configurar ambiente completo de desenvolvimento com Docker Compose, incluindo PostgreSQL e Redis, para dar suporte aos models Django implementados na T002.

## 📋 Estrutura de Arquivos

```
backend/
├── docker-compose.yml          # Configuração principal
├── docker-compose.prod.yml     # Override para produção  
├── .env.example               # Template de variáveis
├── .env                      # Variáveis locais (gitignore)
├── scripts/
│   ├── init-db.sh           # Script de inicialização do banco
│   ├── wait-for-db.sh       # Script para aguardar banco
│   └── dev-setup.sh         # Setup completo de desenvolvimento
└── Dockerfile.dev            # Dockerfile otimizado para dev
```

---

## 🐳 IMPLEMENTAÇÃO DOCKER COMPOSE

### 1. Arquivo Principal docker-compose.yml

```yaml
# backend/docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: wbjj_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-wbjj_dev}
      POSTGRES_USER: ${POSTGRES_USER:-wbjj_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-wbjj_pass}
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh:ro
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    networks:
      - wbjj_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-wbjj_user} -d ${POSTGRES_DB:-wbjj_dev}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: wbjj_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis_pass}
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    networks:
      - wbjj_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: wbjj_backend
    restart: unless-stopped
    command: >
      sh -c "
        python manage.py wait_for_db &&
        python manage.py migrate &&
        python manage.py collectstatic --noinput &&
        python manage.py seed_data &&
        python manage.py runserver 0.0.0.0:8000
      "
    environment:
      - DEBUG=${DEBUG:-True}
      - SECRET_KEY=${SECRET_KEY:-django-insecure-dev-key}
      - DATABASE_URL=postgresql://${POSTGRES_USER:-wbjj_user}:${POSTGRES_PASSWORD:-wbjj_pass}@db:5432/${POSTGRES_DB:-wbjj_dev}
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis_pass}@redis:6379/0
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "${DJANGO_PORT:-8000}:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - wbjj_network

  # Opcional: Adminer para gerenciar banco via web
  adminer:
    image: adminer:latest
    container_name: wbjj_adminer
    restart: unless-stopped
    ports:
      - "${ADMINER_PORT:-8080}:8080"
    depends_on:
      - db
    networks:
      - wbjj_network
    environment:
      ADMINER_DEFAULT_SERVER: db

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local

networks:
  wbjj_network:
    driver: bridge
```

### 2. Dockerfile para Desenvolvimento

```dockerfile
# backend/Dockerfile.dev
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Instalar UV
RUN pip install uv

# Copiar arquivos de dependências
COPY pyproject.toml uv.lock* ./

# Instalar dependências Python
RUN uv sync --dev

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Comando padrão (pode ser sobrescrito)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 3. Arquivo de Ambiente (.env.example)

```bash
# backend/.env.example

# ===============================
# Django Settings
# ===============================
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
DJANGO_SETTINGS_MODULE=config.settings.development
DJANGO_PORT=8000

# ===============================
# Database Settings
# ===============================
POSTGRES_DB=wbjj_dev
POSTGRES_USER=wbjj_user
POSTGRES_PASSWORD=wbjj_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# URL completa do banco (alternativa)
DATABASE_URL=postgresql://wbjj_user:wbjj_pass@localhost:5432/wbjj_dev

# ===============================
# Redis Settings
# ===============================
REDIS_PASSWORD=redis_pass
REDIS_PORT=6379
REDIS_URL=redis://:redis_pass@localhost:6379/0

# ===============================
# Development Tools
# ===============================
ADMINER_PORT=8080

# ===============================
# Email Settings (desenvolvimento)
# ===============================
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# ===============================
# Security (desenvolvimento)
# ===============================
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 🛠️ SCRIPTS DE AUTOMAÇÃO

### 1. Script de Inicialização do Banco

```bash
#!/bin/bash
# backend/scripts/init-db.sh

set -e

# Aguardar PostgreSQL estar pronto
until pg_isready -h localhost -p 5432 -U "$POSTGRES_USER"; do
  echo "Aguardando PostgreSQL..."
  sleep 2
done

echo "PostgreSQL está pronto!"

# Criar banco principal se não existir
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE $POSTGRES_DB'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB');
EOSQL

echo "Banco $POSTGRES_DB criado/verificado com sucesso!"

# Configurações adicionais para performance
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Otimizações para desenvolvimento
    ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
    ALTER SYSTEM SET track_counts = on;
    ALTER SYSTEM SET track_functions = all;
    
    -- Configurações de memória para desenvolvimento
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET effective_cache_size = '1GB';
    ALTER SYSTEM SET work_mem = '16MB';
    
    SELECT pg_reload_conf();
EOSQL

echo "Configurações de performance aplicadas!"
```

### 2. Script Wait for Database

```bash
#!/bin/bash
# backend/scripts/wait-for-db.sh

set -e

host="$1"
port="$2"
user="$3"
database="$4"

until pg_isready -h "$host" -p "$port" -U "$user" -d "$database"; do
  >&2 echo "PostgreSQL não está disponível em $host:$port - aguardando..."
  sleep 1
done

>&2 echo "PostgreSQL está disponível em $host:$port"
```

### 3. Django Management Command - Wait for DB

```python
# backend/apps/core/management/commands/wait_for_db.py

import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Aguarda o banco de dados ficar disponível'

    def handle(self, *args, **options):
        self.stdout.write('Aguardando banco de dados...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()
            except OperationalError:
                self.stdout.write('Banco não disponível, aguardando 1 segundo...')
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS('Banco de dados disponível!')
        )
```

### 4. Script de Setup Completo

```bash
#!/bin/bash
# backend/scripts/dev-setup.sh

set -e

echo "🚀 Configurando ambiente de desenvolvimento wBJJ..."

# Copiar arquivo de ambiente se não existir
if [ ! -f .env ]; then
    echo "📄 Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado! Edite as variáveis se necessário."
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down -v

# Limpar volumes se solicitado
if [ "$1" = "--clean" ]; then
    echo "🧹 Limpando volumes..."
    docker-compose down -v --remove-orphans
    docker volume prune -f
fi

# Construir imagens
echo "🏗️ Construindo imagens Docker..."
docker-compose build

# Subir serviços
echo "🆙 Subindo serviços..."
docker-compose up -d db redis

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Executar migrations
echo "📊 Aplicando migrations..."
docker-compose run --rm web python manage.py migrate

# Popular dados de desenvolvimento
echo "🌱 Populando dados de desenvolvimento..."
docker-compose run --rm web python manage.py seed_data --clear

# Subir aplicação completa
echo "🚀 Subindo aplicação completa..."
docker-compose up -d

echo ""
echo "✅ Setup completo!"
echo ""
echo "📋 Serviços disponíveis:"
echo "   🌐 Django: http://localhost:8000"
echo "   🗄️ Adminer: http://localhost:8080"
echo "   🐘 PostgreSQL: localhost:5432"
echo "   🔴 Redis: localhost:6379"
echo ""
echo "🔧 Comandos úteis:"
echo "   docker-compose logs -f web    # Logs da aplicação"
echo "   docker-compose exec web bash  # Shell no container"
echo "   docker-compose down           # Parar serviços"
echo ""
echo "📚 Usuários de desenvolvimento criados:"
echo "   Admin: admin@wbjj.com / 123456"
echo "   Instrutor: professor@gb-sp.com.br / 123456"
echo "   Aluno: joao.silva@email.com / 123456"
```

---

## ⚙️ CONFIGURAÇÕES DJANGO

### 1. Atualizar Settings para Docker

```python
# backend/config/settings/development.py

import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '.localhost']

# Database com suporte a DATABASE_URL
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ['DATABASE_URL'])
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'wbjj_dev'),
            'USER': os.environ.get('POSTGRES_USER', 'wbjj_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'wbjj_pass'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }

# Redis Cache
if 'REDIS_URL' in os.environ:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ['REDIS_URL'],
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Debug toolbar apenas em desenvolvimento local
if DEBUG and not os.environ.get('DOCKER_CONTAINER'):
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']

# CORS para desenvolvimento
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Static e Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
```

---

## 📝 COMANDOS DE DESENVOLVIMENTO

### Comandos Básicos

```bash
# Setup inicial
chmod +x scripts/*.sh
./scripts/dev-setup.sh

# Desenvolvimento diário
docker-compose up -d                    # Subir serviços
docker-compose logs -f web              # Ver logs
docker-compose exec web python manage.py shell  # Django shell
docker-compose exec web python manage.py test   # Executar testes

# Banco de dados
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data --clear

# Acesso direto ao banco
docker-compose exec db psql -U wbjj_user -d wbjj_dev

# Limpeza
docker-compose down -v                  # Parar e remover volumes
docker-compose down --remove-orphans    # Limpar containers órfãos
```

### Comandos de Produção

```bash
# Build para produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🔒 SEGURANÇA E PERFORMANCE

### 1. Configurações PostgreSQL

```sql
-- Configurações recomendadas em produção
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### 2. Backup Automático

```bash
#!/bin/bash
# backend/scripts/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

docker-compose exec -T db pg_dump -U wbjj_user wbjj_dev > "$BACKUP_DIR/backup_$DATE.sql"
echo "Backup criado: $BACKUP_DIR/backup_$DATE.sql"
```

---

## ✅ CRITÉRIOS DE ACEITAÇÃO

### Verificações de Funcionamento

1. **Docker Compose Funcionando**:
   ```bash
   docker-compose ps  # Todos os serviços "Up"
   ```

2. **Migrations Aplicadas**:
   ```bash
   docker-compose exec web python manage.py showmigrations
   ```

3. **Dados de Seed Carregados**:
   ```bash
   docker-compose exec web python manage.py shell -c "from apps.students.models import Student; print(f'Alunos: {Student.objects.count()}')"
   ```

4. **APIs Funcionando**:
   ```bash
   curl http://localhost:8000/api/health/  # Deve retornar 200
   ```

5. **Banco Acessível**:
   ```bash
   docker-compose exec db psql -U wbjj_user -d wbjj_dev -c "\dt"
   ```

### Documentação Finalizada

- [ ] README.md atualizado com comandos Docker
- [ ] Scripts documentados e executáveis
- [ ] Variáveis de ambiente explicadas
- [ ] Troubleshooting básico documentado

---

## 🎯 RESULTADO ESPERADO

Após a implementação da T002B, o desenvolvedor deve conseguir:

1. **Executar um único comando** e ter todo o ambiente funcionando
2. **Acessar a aplicação** em http://localhost:8000 com dados pré-carregados
3. **Gerenciar o banco** via Adminer em http://localhost:8080
4. **Executar testes** e comandos Django sem configuração adicional
5. **Fazer backup/restore** do banco facilmente

O ambiente deve estar **pronto para a T003** (implementação das APIs REST), com banco de dados funcional e dados de desenvolvimento disponíveis para teste. 