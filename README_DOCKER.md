# DB Agent MCP Server with PostgreSQL

Database Agent MCP server integrated with PostgreSQL for real database monitoring.

## Quick Start with Docker Compose

### 1. Start the services

```bash
# From the db-agent-mcp directory
docker-compose up -d
```

This will start:
- **PostgreSQL** on port 5432
- **DB Agent MCP** on port 9002

### 2. Seed test data

```bash
# Wait for PostgreSQL to be ready (about 10 seconds)
sleep 10

# Seed data into PostgreSQL
docker-compose exec db-agent-mcp python -m db_agent.seed_data
```

### 3. Test the MCP server

```bash
# Test the API
curl http://localhost:9002/health

# Or test via MCP protocol (if configured in gateway)
```

### 4. View logs

```bash
# View MCP app logs
docker-compose logs -f db-agent-mcp

# View PostgreSQL logs
docker-compose logs -f postgres
```

### 5. Stop services

```bash
docker-compose down

# To also remove volumes (deletes all data)
docker-compose down -v
```

## Development Setup (Without Docker)

### 1. Install PostgreSQL

```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# On macOS with Homebrew
brew install postgresql@15
brew services start postgresql@15

# On Windows
# Download from https://www.postgresql.org/download/windows/
```

### 2. Create database and user

```bash
# Connect to PostgreSQL
psql postgres

# Create user and database
CREATE USER dbagent WITH PASSWORD 'dbagent123';
CREATE DATABASE dbagent OWNER dbagent;
GRANT ALL PRIVILEGES ON DATABASE dbagent TO dbagent;
\q
```

### 3. Install dependencies

```bash
# Install uv if not already installed
pip install uv

# Install project dependencies
uv pip install -e .
```

### 4. Set environment variable

```bash
# Linux/macOS
export DATABASE_URL="postgresql://dbagent:dbagent123@localhost:5432/dbagent"

# Windows PowerShell
$env:DATABASE_URL="postgresql://dbagent:dbagent123@localhost:5432/dbagent"
```

### 5. Seed test data

```bash
python -m db_agent.seed_data
```

### 6. Run the server

```bash
# HTTP mode (recommended for testing)
python -m db_agent.server --transport http --host 0.0.0.0 --port 9002

# Stdio mode (for MCP clients)
python -m db_agent.server --transport stdio
```

## Database Schema

The server uses the following tables:

- **slow_queries**: Slow query logs with execution times and recommendations
- **deadlock_sessions**: Active deadlock session information
- **deadlock_logs**: Historical deadlock events
- **database_files**: Database file size tracking and growth metrics
- **abnormal_data**: Anomaly detection records
- **batch_processing**: Batch job execution logs
- **orders**: Sample orders table (for testing)
- **products**: Sample products table (for testing)

## Available MCP Tools

1. **check_query_response_time**: Detect slow queries
2. **check_deadlock**: Check for database deadlocks (active and historical)
3. **check_file_size**: Monitor database file sizes and usage
4. **check_abnormal_data**: Detect data anomalies
5. **check_batch_data**: Monitor batch processing jobs

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: postgresql://dbagent:dbagent123@localhost:5432/dbagent)
- `LOG_LEVEL`: Logging level (default: INFO)

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:
- PostgreSQL credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)
- Port mappings
- Volume mounts

## Troubleshooting

### PostgreSQL connection failed

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Tables not created

```bash
# Run seed script to create tables
docker-compose exec db-agent-mcp python -m db_agent.seed_data
```

### Permission denied

```bash
# Fix file permissions
chmod +x src/db_agent/*.py

# Or use docker-compose with root user
docker-compose exec --user root db-agent-mcp bash
```

## Testing

### Query slow queries

```bash
curl -X POST http://localhost:9002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "check_query_response_time",
      "arguments": {"input": "show all slow queries"}
    }
  }'
```

### Check deadlocks

```bash
curl -X POST http://localhost:9002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "check_deadlock",
      "arguments": {"input": "check active deadlocks"}
    }
  }'
```

## Production Deployment

For production use:

1. Change default passwords in `docker-compose.yml`
2. Use environment variables for secrets
3. Enable SSL/TLS for PostgreSQL connections
4. Set up proper backup strategy for PostgreSQL data
5. Configure resource limits in docker-compose.yml
6. Use a reverse proxy (nginx) for the MCP server
7. Enable monitoring and alerting

## License

Apache-2.0
