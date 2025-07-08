# 🐳 Guia de Desenvolvimento com Docker - wBJJ

## 🚀 Setup Rápido

### Pré-requisitos
- Docker e Docker Compose instalados
- Git configurado

### Primeira execução
```bash
# 1. Executar setup automático
./scripts/dev-setup.sh

# 2. Aguardar finalização e acessar
# 🌐 Django: http://localhost:8000
# 🗄️ Adminer: http://localhost:8080
```

## 📋 Serviços Disponíveis

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| Django  | 8000  | http://localhost:8000 | API principal |
| PostgreSQL | 5432 | localhost:5432 | Banco de dados |
| Redis   | 6379  | localhost:6379 | Cache/Sessions |
| Adminer | 8080  | http://localhost:8080 | Admin do banco |

## 🔧 Comandos Essenciais

### Gerenciamento de containers
```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f web

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v
```

### Executar comandos Django
```bash
# Shell no container
docker-compose exec web bash

# Django shell
docker-compose exec web uv run python manage.py shell

# Criar superuser
docker-compose exec web uv run python manage.py createsuperuser

# Executar migrations
docker-compose exec web uv run python manage.py migrate

# Popular dados de desenvolvimento
docker-compose exec web uv run python manage.py seed_data --clear

# Django check
docker-compose exec web uv run python manage.py check
```

### Banco de dados
```bash
# Acessar PostgreSQL diretamente
docker-compose exec db psql -U wbjj_user -d wbjj_dev

# Backup do banco
docker-compose exec db pg_dump -U wbjj_user wbjj_dev > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U wbjj_user -d wbjj_dev < backup.sql
```

## 🔑 Usuários de Desenvolvimento

O comando `seed_data` cria os seguintes usuários:

| Tipo | Email | Senha | Permissões |
|------|-------|-------|------------|
| Admin | admin@wbjj.com | 123456 | Todas |
| Instrutor | professor@gb-sp.com.br | 123456 | Gestão de alunos |
| Aluno | joao.silva@email.com | 123456 | Visualização |

## 🛠 Troubleshooting

### Problema: "Cannot connect to Docker daemon"
```bash
# Verificar se Docker está rodando
docker --version
docker ps

# No macOS, certifique-se que Docker Desktop está aberto
```

### Problema: Porta já em uso
```bash
# Verificar processos usando as portas
lsof -i :8000  # Django
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Alterar portas no .env se necessário
```

### Problema: Container falha ao subir
```bash
# Ver logs detalhados
docker-compose logs web

# Reconstruir imagem
docker-compose build --no-cache web

# Reset completo
./scripts/dev-setup.sh --clean
```

### Problema: Banco de dados não conecta
```bash
# Verificar se container está rodando
docker-compose ps

# Verificar logs do banco
docker-compose logs db

# Testar conexão manual
docker-compose exec web uv run python manage.py wait_for_db
```

## 🔄 Workflow de Desenvolvimento

### 1. Início do dia
```bash
# Subir ambiente
docker-compose up -d

# Verificar status
docker-compose ps
```

### 2. Durante desenvolvimento
```bash
# Ver logs em tempo real
docker-compose logs -f web

# Executar testes
docker-compose exec web uv run pytest

# Aplicar migrações
docker-compose exec web uv run python manage.py migrate
```

### 3. Final do dia
```bash
# Parar serviços (mantém dados)
docker-compose down
```

## 📁 Estrutura de Arquivos Docker

```
backend/
├── docker-compose.yml          # Definição dos serviços
├── Dockerfile.dev              # Imagem para desenvolvimento
├── .env.example               # Template de variáveis
├── .env                       # Suas variáveis (não commitado)
└── scripts/
    ├── dev-setup.sh           # Setup completo automático
    ├── init-db.sh             # Inicialização do PostgreSQL
    └── test-commands.sh       # Testes sem Docker
```

## 🌍 Variáveis de Ambiente

### Principais variáveis (.env)
```bash
# Django
DEBUG=True
SECRET_KEY=sua-chave-secreta
DJANGO_PORT=8000

# Banco de dados
POSTGRES_DB=wbjj_dev
POSTGRES_USER=wbjj_user
POSTGRES_PASSWORD=wbjj_pass
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=redis_pass
REDIS_PORT=6379

# Ferramentas
ADMINER_PORT=8080
```

## 📊 Monitoramento

### Health checks
```bash
# Verificar saúde dos serviços
docker-compose ps

# Status deve mostrar "healthy" para todos
```

### Métricas de performance
```bash
# Uso de recursos
docker stats

# Logs de performance
docker-compose logs web | grep "GET /"
```

## 🚨 Produção vs Desenvolvimento

| Aspecto | Desenvolvimento | Produção |
|---------|----------------|----------|
| DEBUG | True | False |
| Volumes | Code mounted | No mount |
| Secrets | .env file | Docker secrets |
| SSL | Não | Obrigatório |
| Cache | Local Redis | Redis cluster |

---

## 🆘 Suporte

- **Logs**: Sempre verifique `docker-compose logs` primeiro
- **Reset**: Use `./scripts/dev-setup.sh --clean` para reset completo
- **Performance**: Monitor com `docker stats`

🎯 **Dica**: Mantenha o ambiente Docker sempre atualizado para melhor performance!
