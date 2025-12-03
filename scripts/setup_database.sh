#!/bin/bash
# Setup database schema and seed data
# Runs psql commands inside the postgres container - no need to install psql locally

set -e

echo "=========================================="
echo "Database Setup"
echo "=========================================="

CONTAINER_NAME=${CONTAINER_NAME:-db-agent-postgres}
DB_NAME=${DB_NAME:-testdb}
DB_USER=${DB_USER:-dbagent}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_DIR="$SCRIPT_DIR/../sql"

echo "Waiting for PostgreSQL container..."
until docker exec "$CONTAINER_NAME" pg_isready -U "$DB_USER" -d "$DB_NAME" 2>/dev/null; do
  echo "  Waiting..."
  sleep 2
done

echo "PostgreSQL ready!"
echo ""

echo "Running schema..."
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$SQL_DIR/01_schema.sql"
echo "✓ Schema created"

echo ""
echo "Running seed data..."
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$SQL_DIR/02_seed_data.sql"
echo "✓ Seed data inserted"

echo ""
echo "=========================================="
echo "Database setup complete!"
echo "=========================================="
