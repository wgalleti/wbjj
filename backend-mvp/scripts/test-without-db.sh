#!/bin/bash

echo "🚀 Executando testes SEM banco de dados..."
echo "⚡ Testes rápidos de validação, serializers, utils"

echo ""
echo "📂 Testando pasta: tests/without_db/"

# Executar testes SEM banco usando pyproject.toml + argumentos específicos
DJANGO_SETTINGS_MODULE=config.settings.testing uv run pytest \
    tests/without_db/ \
    --no-migrations \
    --nomigrations \
    --disable-warnings \
    --tb=line \
    $@

echo ""
echo "⚡ Testes SEM banco de dados concluídos!"
echo "🎯 Ideal para feedback rápido durante desenvolvimento"
