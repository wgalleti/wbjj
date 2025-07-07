#!/bin/bash

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

# Aguardar banco de dados especificamente
echo "🗄️ Aguardando banco de dados..."
docker-compose run --rm web uv run python manage.py wait_for_db

# Executar migrations
echo "📊 Aplicando migrations..."
docker-compose run --rm web uv run python manage.py migrate

# Popular dados de desenvolvimento
echo "🌱 Populando dados de desenvolvimento..."
docker-compose run --rm web uv run python manage.py seed_data --clear

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