# Test Queries for DB Agent MCP Server

These are example queries you can use to test the DB agent with the MCP server.

## 1. Deadlock Detection

**Query:**
```
Run a query to detect any active deadlocks in the database. Provide details of the transactions involved, including session IDs, query text, and locked resources.
```

**What it tests:** `check_deadlock()` tool

**Setup:** Run `python3 scripts/01_trigger_deadlock.py` in background first

---

## 2. Slow Query Detection

**Query:**
```
Check for slow queries in the database that took longer than 500ms to execute. Show me the query text, execution time, and when it was run.
```

**What it tests:** `check_query_response_time()` tool with default behavior

**Setup:** Run `python3 scripts/02_trigger_slow_query.py` first

---

## 3. Execute Specific Query

**Query:**
```
Execute this query and measure its performance: SELECT * FROM products WHERE category='electronics' AND price > 500. Tell me if it's slower than 1 second.
```

**What it tests:** `check_query_response_time()` tool with custom query

**Setup:** No setup needed (uses seed data)

---

## 4. Database Size Check

**Query:**
```
What is the current size of the database? Show me the size in MB and tell me if it's growing too large.
```

**What it tests:** `check_file_size()` tool

**Setup:** No setup needed

---

## 5. Abnormal Data - Orders

**Query:**
```
Check the orders table for any abnormal data. Look for negative amounts, invalid statuses, or other business logic violations.
```

**What it tests:** `check_abnormal_data(tables="orders")` tool

**Setup:** Run `python3 scripts/03_insert_abnormal_data.py` first

---

## 6. Abnormal Data - Inventory

**Query:**
```
Scan the inventory table for anomalies. Are there any products with stock levels that exceed their maximum threshold or other unusual values?
```

**What it tests:** `check_abnormal_data(tables="inventory")` tool

**Setup:** Run `python3 scripts/03_insert_abnormal_data.py` first

---

## 7. Abnormal Data - All Tables

**Query:**
```
Perform a comprehensive scan across all tables (orders, inventory, transactions) to find any abnormal data patterns or violations.
```

**What it tests:** `check_abnormal_data(tables="all")` tool

**Setup:** Run `python3 scripts/03_insert_abnormal_data.py` first

---

## 8. Batch Failures - Recent

**Query:**
```
Show me batch processing failures from the last 24 hours. Include the batch ID, error types, and sample error messages.
```

**What it tests:** `check_batch_data(hours=24, limit=5)` tool

**Setup:** Run `python3 scripts/04_trigger_batch_failures.py` first

---

## 9. Batch Failures - Last 12 Hours

**Query:**
```
Analyze batch job failures from the past 12 hours. Give me the top 10 most recent failures with details.
```

**What it tests:** `check_batch_data(hours=12, limit=10)` tool

**Setup:** Run `python3 scripts/04_trigger_batch_failures.py` first

---

## 10. Complex Query Performance

**Query:**
```
Run this complex query and check if it's performant: SELECT o.order_id, c.name, p.product_name, o.total_amount FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN inventory p ON o.product_id = p.product_id WHERE o.status = 'pending'. Is it faster than 2 seconds?
```

**What it tests:** `check_query_response_time()` tool with JOIN query

**Setup:** No setup needed (uses seed data)

---

## 11. Transaction Log Anomalies

**Query:**
```
Check the transaction_log table for any suspicious patterns. Look for large negative amounts that might indicate fraud or system errors.
```

**What it tests:** `check_abnormal_data(tables="transactions")` tool

**Setup:** Run `python3 scripts/03_insert_abnormal_data.py` first

---

## 12. Multiple Checks Combined

**Query:**
```
I need a health check of the database. Please check for: 1) any active deadlocks, 2) slow queries over 1 second, 3) abnormal data in all tables, and 4) the current database size.
```

**What it tests:** Multiple tools - `check_deadlock()`, `check_query_response_time()`, `check_abnormal_data()`, `check_file_size()`

**Setup:** Run all trigger scripts for comprehensive test

---

## Setup Instructions

To test all queries, run these commands first:

```bash
# Start database
docker-compose up -d
./scripts/setup_database.sh

# Trigger all scenarios
python3 scripts/01_trigger_deadlock.py &  # runs in background
python3 scripts/02_trigger_slow_query.py
python3 scripts/03_insert_abnormal_data.py
python3 scripts/04_trigger_batch_failures.py

# Stop deadlock script when done
kill %1
```

Then use any of the queries above with your AI agent that has access to this MCP server.
