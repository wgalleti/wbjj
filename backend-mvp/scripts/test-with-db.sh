#!/bin/bash

echo "🚀 Executando testes COM banco de dados..."
echo "🗄️  Testes completos: models, views, serializers, integração"

# Verificar se o banco está acessível
echo ""
echo "🔍 Verificando banco de dados..."

# Aplicar migrations
echo "📦 Aplicando migrations..."
DJANGO_SETTINGS_MODULE=config.settings.testing python manage.py migrate

echo "📂 Testando pasta: tests/with_db/"

# Executar testes COM banco usando pyproject.toml + argumentos específicos
DJANGO_SETTINGS_MODULE=config.settings.testing uv run pytest \
    tests/with_db/ \
    --create-db \
    --reuse-db \
    --cov=apps \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml \
    --cov-report=term-missing \
    --cov-fail-under=75 \
    --timeout=300 \
    $@

echo ""
echo "✅ Testes COM banco de dados concluídos!"
echo "📊 Relatório de cobertura: htmlcov/index.html"
