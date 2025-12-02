#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DB Agent MCP Server with PostgreSQL.
Location: ./mcp-servers/python/db-agent-mcp/src/db_agent/seed_data.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Database Agent Team

Script to seed test data into PostgreSQL database.
"""

import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_models import (
    Base,
    SlowQuery,
    DeadlockSession,
    DeadlockLog,
    DatabaseFile,
    AbnormalData,
    BatchProcessing,
    Order,
    Product
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dbagent:dbagent123@localhost:5432/dbagent")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def seed_data():
    """Seed test data into the database."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding slow queries...")
        slow_queries = [
            SlowQuery(
                query_text="SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id WHERE o.status='active'",
                execution_time_ms=2450.5,
                table_name="orders",
                operation_type="SELECT",
                recommendations=json.dumps([
                    "Add index on orders.status column",
                    "Consider adding covering index on (customer_id, status)",
                    "Review JOIN strategy"
                ])
            ),
            SlowQuery(
                query_text="UPDATE products SET last_checked=NOW() WHERE category='electronics'",
                execution_time_ms=1850.2,
                table_name="products",
                operation_type="UPDATE",
                recommendations=json.dumps([
                    "Add index on products.category column",
                    "Consider batching updates"
                ])
            ),
            SlowQuery(
                query_text="DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days'",
                execution_time_ms=3200.8,
                table_name="logs",
                operation_type="DELETE",
                recommendations=json.dumps([
                    "Add index on created_at column",
                    "Consider partitioning logs table by date"
                ])
            ),
        ]
        db.add_all(slow_queries)
        
        print("Seeding deadlock sessions...")
        deadlock_sessions = [
            DeadlockSession(
                session_id="SID-1234",
                transaction_id="TXN-5678",
                query="UPDATE orders SET status='shipped' WHERE order_id=12345",
                locked_resource="TABLE:orders:ROW:12345",
                wait_time_ms=1250,
                blocking_session="SID-5678",
                resolved=False
            ),
            DeadlockSession(
                session_id="SID-5678",
                transaction_id="TXN-9012",
                query="UPDATE inventory SET quantity=quantity-1 WHERE product_id=67890",
                locked_resource="TABLE:inventory:ROW:67890",
                wait_time_ms=980,
                blocking_session="SID-1234",
                resolved=False
            ),
        ]
        db.add_all(deadlock_sessions)
        
        print("Seeding deadlock logs...")
        deadlock_logs = [
            DeadlockLog(
                deadlock_id="DL-2024-001",
                timestamp=datetime.now() - timedelta(hours=2),
                affected_queries=json.dumps([
                    "UPDATE orders SET status='processing' WHERE order_id=98765",
                    "DELETE FROM order_items WHERE order_id=98765"
                ]),
                victim_session="SID-4321",
                resolution="Transaction rolled back"
            ),
            DeadlockLog(
                deadlock_id="DL-2024-002",
                timestamp=datetime.now() - timedelta(hours=5),
                affected_queries=json.dumps([
                    "UPDATE products SET stock=stock-5 WHERE product_id=111",
                    "INSERT INTO order_products (order_id, product_id) VALUES (222, 111)"
                ]),
                victim_session="SID-8765",
                resolution="Transaction rolled back"
            ),
        ]
        db.add_all(deadlock_logs)
        
        print("Seeding database file sizes...")
        db_files = [
            DatabaseFile(
                database_name="prod_db",
                size_mb=9400.5,
                max_size_mb=10240.0,
                growth_rate_mb_per_day=15.2,
                estimated_full_days=55
            ),
            DatabaseFile(
                database_name="staging_db",
                size_mb=512.3,
                max_size_mb=2048.0,
                growth_rate_mb_per_day=8.5,
                estimated_full_days=180
            ),
            DatabaseFile(
                database_name="dev_db",
                size_mb=256.8,
                max_size_mb=1024.0,
                growth_rate_mb_per_day=3.1,
                estimated_full_days=247
            ),
        ]
        db.add_all(db_files)
        
        print("Seeding abnormal data...")
        abnormal_data = [
            AbnormalData(
                table_name="orders",
                anomaly_type="Negative order amounts",
                severity="HIGH",
                affected_row_ids=json.dumps([
                    {"order_id": 12345, "amount": -150.00, "customer_id": 789},
                    {"order_id": 12389, "amount": -75.50, "customer_id": 234}
                ]),
                description="Orders with negative amounts detected",
                resolved=False
            ),
            AbnormalData(
                table_name="products",
                anomaly_type="Stock exceeds threshold",
                severity="MEDIUM",
                affected_row_ids=json.dumps([
                    {"product_id": 555, "current_stock": 999999, "max_threshold": 10000},
                    {"product_id": 666, "current_stock": 888888, "max_threshold": 5000}
                ]),
                description="Product stock counts exceed maximum threshold",
                resolved=False
            ),
        ]
        db.add_all(abnormal_data)
        
        print("Seeding batch processing records...")
        batch_records = [
            BatchProcessing(
                batch_id="BATCH-2024-001",
                records_processed=10000,
                failed_records=45,
                failure_reasons=json.dumps({
                    "duplicate_key": 30,
                    "validation_error": 10,
                    "timeout": 5
                }),
                timestamp=datetime.now() - timedelta(hours=1),
                status="COMPLETED"
            ),
            BatchProcessing(
                batch_id="BATCH-2024-002",
                records_processed=5000,
                failed_records=12,
                failure_reasons=json.dumps({
                    "foreign_key_violation": 8,
                    "data_type_mismatch": 4
                }),
                timestamp=datetime.now() - timedelta(hours=3),
                status="COMPLETED"
            ),
            BatchProcessing(
                batch_id="BATCH-2024-003",
                records_processed=25000,
                failed_records=0,
                failure_reasons=json.dumps({}),
                timestamp=datetime.now() - timedelta(minutes=30),
                status="COMPLETED"
            ),
        ]
        db.add_all(batch_records)
        
        print("Seeding sample orders...")
        orders = [
            Order(order_id=1, customer_id=100, amount=150.50, status="completed"),
            Order(order_id=2, customer_id=101, amount=299.99, status="pending"),
            Order(order_id=12345, customer_id=789, amount=-150.00, status="error"),  # Abnormal
            Order(order_id=12389, customer_id=234, amount=-75.50, status="error"),   # Abnormal
        ]
        db.add_all(orders)
        
        print("Seeding sample products...")
        products = [
            Product(product_id=1, name="Laptop", category="electronics", stock=50, max_threshold=1000),
            Product(product_id=2, name="Mouse", category="accessories", stock=200, max_threshold=500),
            Product(product_id=555, name="Defective Item", category="unknown", stock=999999, max_threshold=10000),  # Abnormal
        ]
        db.add_all(products)
        
        db.commit()
        print("✅ Data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting data seeding...")
    seed_data()
    print("Done!")
