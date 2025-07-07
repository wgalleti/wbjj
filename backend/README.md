# wBJJ Backend

Sistema de gestão para academias de jiu-jitsu - API Backend

## Tecnologias

- Django 4.2 LTS
- Django REST Framework
- PostgreSQL 15
- Redis 7
- Docker

## Desenvolvimento

### Com Docker (Recomendado)

```bash
# Setup completo automático
./scripts/dev-setup.sh

# Acessar aplicação
# 🌐 Django: http://localhost:8000
# 🗄️ Adminer: http://localhost:8080
```

### Comandos úteis

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
```

## Documentação

- [Guia Docker](DOCKER_DEVELOPMENT.md)
- [Contexto do Projeto](CONTEXT.md)
- [Tarefas](../doc/TASKS.md)

## Usuários de Desenvolvimento

- **Admin**: admin@wbjj.com / 123456
- **Instrutor**: professor@gb-sp.com.br / 123456
- **Aluno**: joao.silva@email.com / 123456
