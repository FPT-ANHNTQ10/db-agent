#!/bin/bash
# Entrypoint script to wait for PostgreSQL and then start the server

echo "Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "postgres" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - initializing database..."

# Run database initialization (create tables)
python -c "from db_agent.db_models import init_db; init_db(); print('Database initialized')"

echo "Starting MCP server..."

# Start the server
exec python -m db_agent.server --transport http --host 0.0.0.0 --port 9002
