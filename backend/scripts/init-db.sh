#!/bin/bash

set -e

echo "Iniciando configuração do banco de dados..."

# Criar banco principal se não existir
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE $POSTGRES_DB'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB');
EOSQL

echo "Banco $POSTGRES_DB criado/verificado com sucesso!"

# Configurações básicas para desenvolvimento
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Configurações de memória para desenvolvimento
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET effective_cache_size = '1GB';
    ALTER SYSTEM SET work_mem = '16MB';
    
    -- Configurações de log
    ALTER SYSTEM SET log_statement = 'all';
    ALTER SYSTEM SET log_duration = on;
EOSQL

echo "Configurações de performance aplicadas!" 