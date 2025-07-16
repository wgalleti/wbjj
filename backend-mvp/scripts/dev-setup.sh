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
uv run manage.py wait_for_db

# Executar migrations
echo "📊 Aplicando migrations..."
uv run manage.py migrate_schemas --shared
uv run manage.py migrate

# Popular dados de desenvolvimento
echo "🌱 Populando dados de desenvolvimento..."
uv run manage.py seed_data --clear


echo ""
echo "✅ Setup completo!"
echo ""
echo "📋 Serviços disponíveis:"
echo "   🗄️ Adminer: http://localhost:8080"
echo "   🐘 PostgreSQL: localhost:5432"
echo "   🔴 Redis: localhost:6379"
echo ""
echo "📚 Usuários de desenvolvimento criados:"
echo "   Admin: admin@wbjj.com / 123456"
echo "   Instrutor: professor@gb-sp.com.br / 123456"
echo "   Aluno: joao.silva@email.com / 123456"
