# Database Agent Setup

## Quick Start

### 1. Start PostgreSQL
```bash
docker-compose up -d
```

### 2. Setup Database
```bash
./scripts/setup_database.sh
```

### 3. Install Dependencies
```bash
pip install -e .
```

### 4. Run MCP Server
```bash
python -m db_agent.server
```

## Test Scenarios

### Trigger Deadlock
```bash
python3 scripts/01_trigger_deadlock.py
```

### Trigger Slow Queries
```bash
python3 scripts/02_trigger_slow_query.py
```

### Insert Abnormal Data
```bash
python3 scripts/03_insert_abnormal_data.py
```

### Trigger Batch Failures
```bash
python3 scripts/04_trigger_batch_failures.py
```

## MCP Tools

1. `check_query_response_time(query, threshold_ms=1000)` - Execute SQL query or check slow queries
2. `check_deadlock()` - Detect active deadlocks (no params)
3. `check_file_size()` - Check database size (no params)
4. `check_abnormal_data(tables="all")` - Scan for data anomalies (orders/inventory/transactions)
5. `check_batch_data(hours=24, limit=5)` - Analyze recent batch failures

### Example Usage

```python
# Execute specific query and measure time
check_query_response_time(
    query="SELECT * FROM products WHERE category='electronics'",
    threshold_ms=500
)

# Check for slow queries in database
check_query_response_time(query="check")

# Check deadlocks (no params needed)
check_deadlock()

# Scan specific tables for anomalies
check_abnormal_data(tables="orders")

# Check batch failures in last 12 hours
check_batch_data(hours=12, limit=10)
```

## Reset Database
```bash
docker-compose down
docker-compose up -d
./scripts/setup_database.sh
```

## Database Connection
- Host: localhost:5432
- Database: testdb
- User: dbagent
- Password: dbagent123
