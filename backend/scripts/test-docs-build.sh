#!/bin/bash

# Script para testar o build da documentação antes do deploy
# Uso: ./scripts/test-docs-build.sh

set -e

echo "🧪 Testando build da documentação wBJJ..."

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

# Navegar para docs e fazer build
echo "🔨 Executando build da documentação..."
cd docs

# Build com strict mode (como no CI)
echo "📋 Build modo strict (como no GitHub Actions)..."
uv run mkdocs build --clean --strict

# Verificar se o build foi bem-sucedido
if [ -d "site" ] && [ -f "site/index.html" ]; then
    echo "✅ Build bem-sucedido!"
    echo "📁 Arquivos gerados em: docs/site/"
    echo "📊 Tamanho total:"
    du -sh site/
    echo ""
    echo "🔍 Páginas principais encontradas:"
    find site/ -name "*.html" -type f | head -10
    echo ""
    echo "🚀 Pronto para deploy no GitHub Pages!"
else
    echo "❌ Build falhou - site/ não foi gerado corretamente"
    exit 1
fi
