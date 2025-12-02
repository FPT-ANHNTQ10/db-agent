# Quick Start Guide

## Chạy với Docker Compose (Khuyến nghị)

```powershell
# Bước 1: Di chuyển vào thư mục
cd 'C:\Users\minh1\Desktop\Study\Fsoft\prj_test\SKT\mcp-context-forge\mcp-servers\python\db-agent-mcp'

# Bước 2: Build và start containers
docker-compose up -d --build

# Bước 3: Xem logs để check
docker-compose logs -f

# Bước 4: Seed test data (chạy sau khi containers đã start)
Start-Sleep -Seconds 10
docker-compose exec db-agent-mcp python -m db_agent.seed_data

# Bước 5: Test API
curl http://localhost:9002/health
```

## Kiểm tra các tools

### 1. Check Slow Queries
```powershell
curl -X POST http://localhost:9002/tools/call `
  -H "Content-Type: application/json" `
  -d '{
    "name": "check_query_response_time",
    "arguments": {"input": "show all slow queries"}
  }'
```

### 2. Check Deadlocks
```powershell
curl -X POST http://localhost:9002/tools/call `
  -H "Content-Type: application/json" `
  -d '{
    "name": "check_deadlock",
    "arguments": {"input": "check active deadlocks"}
  }'
```

### 3. Check File Sizes
```powershell
curl -X POST http://localhost:9002/tools/call `
  -H "Content-Type: application/json" `
  -d '{
    "name": "check_file_size",
    "arguments": {"input": "check database sizes"}
  }'
```

### 4. Check Abnormal Data
```powershell
curl -X POST http://localhost:9002/tools/call `
  -H "Content-Type: application/json" `
  -d '{
    "name": "check_abnormal_data",
    "arguments": {"input": "check orders"}
  }'
```

### 5. Check Batch Data
```powershell
curl -X POST http://localhost:9002/tools/call `
  -H "Content-Type: application/json" `
  -d '{
    "name": "check_batch_data",
    "arguments": {"input": "check batch processing"}
  }'
```

## Truy cập PostgreSQL

```powershell
# Connect to PostgreSQL container
docker-compose exec postgres psql -U dbagent -d dbagent

# Run queries
SELECT * FROM slow_queries;
SELECT * FROM deadlock_sessions;
SELECT * FROM abnormal_data;
```

## Dừng services

```powershell
# Stop containers
docker-compose down

# Stop và xóa volumes (xóa hết data)
docker-compose down -v
```

## Troubleshooting

### Container không start
```powershell
# Xem logs chi tiết
docker-compose logs db-agent-mcp
docker-compose logs postgres

# Restart
docker-compose restart
```

### Database connection error
```powershell
# Check PostgreSQL health
docker-compose exec postgres pg_isready -U dbagent

# Recreate containers
docker-compose down -v
docker-compose up -d --build
```

### Thêm data mới
```powershell
# Chạy lại seed script
docker-compose exec db-agent-mcp python -m db_agent.seed_data
```

## Các files quan trọng

- **docker-compose.yml**: Container orchestration
- **Dockerfile**: MCP app image
- **src/db_agent/server.py**: MCP server code
- **src/db_agent/db_models.py**: Database models
- **src/db_agent/seed_data.py**: Test data seeding
- **init_db.sql**: PostgreSQL init script
- **entrypoint.sh**: Container startup script
