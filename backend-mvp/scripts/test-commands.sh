#!/bin/bash

set -e

echo "🧪 Testando comandos Django..."

echo "✅ Testando comando wait_for_db..."
python manage.py help wait_for_db

echo "✅ Testando comando seed_data..."
python manage.py help seed_data

echo "✅ Testando django check..."
python manage.py check

echo "✅ Testando makemigrations (dry-run)..."
python manage.py makemigrations --dry-run

echo ""
echo "🎉 Todos os comandos Django estão funcionando!"
echo ""
echo "📋 Para usar com Docker:"
echo "   1. Certifique-se que Docker está rodando"
echo "   2. Execute: ./scripts/dev-setup.sh"
echo ""
echo "📋 Para desenvolvimento local sem Docker:"
echo "   1. Configure PostgreSQL e Redis localmente"
echo "   2. Copie .env.example para .env"
echo "   3. Ajuste as variáveis de ambiente"
echo "   4. Execute: python manage.py migrate"
echo "   5. Execute: python manage.py seed_data" 