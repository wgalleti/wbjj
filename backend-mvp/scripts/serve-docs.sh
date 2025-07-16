#!/bin/bash

# Script para servir a documentação wBJJ localmente
# Uso: ./scripts/serve-docs.sh

set -e

echo "🚀 Iniciando servidor de documentação wBJJ..."

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Execute este script a partir do diretório backend/"
    exit 1
fi

# Verificar se docs existe
if [ ! -d "docs" ]; then
    echo "❌ Diretório docs/ não encontrado"
    exit 1
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
uv sync --dev

# Navegar para docs e servir
echo "📚 Servindo documentação em http://127.0.0.1:8001"
echo "📝 Pressione Ctrl+C para parar"
echo ""

cd docs
uv run mkdocs serve --dev-addr=127.0.0.1:8001
