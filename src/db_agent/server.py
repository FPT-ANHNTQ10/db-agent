#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Location: ./mcp-servers/python/db-agent-mcp/src/db_agent/server.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Database Agent Team

Database Agent MCP Server

Comprehensive database operations server supporting multiple database engines.
Provides tools for querying, schema inspection, data manipulation, and analytics.
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Any
import random

from fastmcp import FastMCP
from pydantic import Field

# Configure logging to stderr to avoid MCP protocol interference
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(name="db-agent", version="1.0.0")


# Mock data pools for realistic responses
MOCK_DEADLOCK_DETAILS = [
    {
        "session_id": "SID-1234",
        "transaction_id": "TXN-5678",
        "query": "UPDATE orders SET status='shipped' WHERE order_id=12345",
        "locked_resource": "TABLE:orders:ROW:12345",
        "wait_time_ms": 1250,
        "blocking_session": "SID-5678"
    },
    {
        "session_id": "SID-5678",
        "transaction_id": "TXN-9012",
        "query": "UPDATE inventory SET quantity=quantity-1 WHERE product_id=67890",
        "locked_resource": "TABLE:inventory:ROW:67890",
        "wait_time_ms": 980,
        "blocking_session": "SID-1234"
    },
    {
        "session_id": "SID-3456",
        "transaction_id": "TXN-7890",
        "query": "SELECT * FROM customers WHERE customer_id=456 FOR UPDATE",
        "locked_resource": "TABLE:customers:ROW:456",
        "wait_time_ms": 2100,
        "blocking_session": "SID-7890"
    }
]

MOCK_DEADLOCK_LOGS = [
    {
        "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "deadlock_id": "DL-2024-001",
        "affected_queries": [
            "UPDATE orders SET status='processing' WHERE order_id=98765",
            "DELETE FROM order_items WHERE order_id=98765"
        ],
        "victim_session": "SID-4321",
        "resolution": "Transaction rolled back"
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "deadlock_id": "DL-2024-002",
        "affected_queries": [
            "UPDATE products SET stock=stock-5 WHERE product_id=111",
            "INSERT INTO order_products (order_id, product_id) VALUES (222, 111)"
        ],
        "victim_session": "SID-8765",
        "resolution": "Transaction rolled back"
    }
]

MOCK_PREVENTIVE_ACTIONS = [
    {
        "issue": "Circular wait on orders and inventory tables",
        "root_cause": "Transactions acquiring locks in different order",
        "recommendations": [
            "Implement consistent lock ordering across all transactions",
            "Always acquire locks on orders table before inventory table",
            "Use NOWAIT or timeout hints to fail fast instead of waiting",
            "Consider using optimistic locking for read-modify-write patterns"
        ],
        "code_example": """
-- Good practice: Consistent lock order
BEGIN TRANSACTION;
  UPDATE orders SET ... WHERE order_id = @id;  -- Always lock orders first
  UPDATE inventory SET ... WHERE product_id = @pid;  -- Then inventory
COMMIT;
"""
    },
    {
        "issue": "Long-running transactions holding locks",
        "root_cause": "Transactions keeping resources locked for extended periods",
        "recommendations": [
            "Break large transactions into smaller batches",
            "Minimize time between acquiring locks and committing",
            "Use READ COMMITTED isolation level when possible",
            "Implement retry logic with exponential backoff"
        ],
        "code_example": """
-- Process in smaller batches
DECLARE @BatchSize INT = 100;
WHILE EXISTS (SELECT 1 FROM orders WHERE status='pending')
BEGIN
  BEGIN TRANSACTION;
    UPDATE TOP (@BatchSize) orders SET status='processing' WHERE status='pending';
  COMMIT;
END;
"""
    }
]

MOCK_SLOW_QUERIES = [
    {
        "query": "SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id WHERE o.status='active'",
        "execution_time_ms": 2450,
        "recommendations": [
            "Add index on orders.status column",
            "Consider adding covering index on (customer_id, status)",
            "Review JOIN strategy - might need to optimize customer table"
        ]
    },
    {
        "query": "UPDATE products SET last_checked=NOW() WHERE category='electronics'",
        "execution_time_ms": 1850,
        "recommendations": [
            "Add index on products.category column",
            "Consider batching updates instead of full table scan",
            "Use WHERE clause with indexed columns"
        ]
    }
]

MOCK_FILE_SIZE_DATA = [
    {"database": "prod_db", "size_mb": 1024.5, "growth_rate_mb_per_day": 15.2, "estimated_full_days": 45},
    {"database": "staging_db", "size_mb": 512.3, "growth_rate_mb_per_day": 8.5, "estimated_full_days": 90},
    {"database": "dev_db", "size_mb": 256.8, "growth_rate_mb_per_day": 3.1, "estimated_full_days": 180}
]

MOCK_ABNORMAL_DATA_PATTERNS = [
    {
        "table": "orders",
        "anomaly": "Negative order amounts detected",
        "affected_rows": [
            {"order_id": 12345, "amount": -150.00, "customer_id": 789},
            {"order_id": 12389, "amount": -75.50, "customer_id": 234}
        ],
        "severity": "HIGH"
    },
    {
        "table": "inventory",
        "anomaly": "Stock count exceeds maximum threshold",
        "affected_rows": [
            {"product_id": 555, "current_stock": 999999, "max_threshold": 10000},
            {"product_id": 666, "current_stock": 888888, "max_threshold": 5000}
        ],
        "severity": "MEDIUM"
    }
]

MOCK_BATCH_DATA_ISSUES = [
    {
        "batch_id": "BATCH-2024-001",
        "records_processed": 10000,
        "failed_records": 45,
        "failure_reasons": {
            "duplicate_key": 30,
            "validation_error": 10,
            "timeout": 5
        },
        "timestamp": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "batch_id": "BATCH-2024-002",
        "records_processed": 5000,
        "failed_records": 12,
        "failure_reasons": {
            "foreign_key_violation": 8,
            "data_type_mismatch": 4
        },
        "timestamp": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    }
]


class DatabaseAgent:
    """Database operations agent with support for multiple engines."""

    def __init__(self):
        """Initialize the database agent."""
        logger.info("Database Agent initialized for monitoring tools.")

    def check_query_response_time(self, input: str) -> dict[str, Any]:
        """
        Check DB query response time for slow query detection.
        
        Args:
            input: user input to test
        
        Returns:
            Query response time and slow query status
        """
        try:
            # Analyze input to determine if it's a slow query scenario
            input_lower = input.lower()
            
            # Select mock data based on input context
            if any(keyword in input_lower for keyword in ['slow', 'performance', 'optimize']):
                # Return a slow query from mock data
                mock_query = random.choice(MOCK_SLOW_QUERIES)
                return {
                    "success": True,
                    "input": input,
                    "analysis": f"Analyzing query performance for: {input}",
                    "detected_query": mock_query["query"],
                    "response_time_ms": mock_query["execution_time_ms"],
                    "is_slow": True,
                    "status": "SLOW",
                    "recommendations": mock_query["recommendations"]
                }
            else:
                # Return normal performance
                response_time_ms = round(random.uniform(15.0, 150.0), 2)
                return {
                    "success": True,
                    "input": input,
                    "analysis": f"Query performance check for: {input}",
                    "response_time_ms": response_time_ms,
                    "is_slow": False,
                    "status": "NORMAL",
                    "message": "Query execution time is within acceptable range"
                }

        except Exception as e:
            logger.error(f"Query response time check error: {e}")
            return {"success": False, "error": str(e)}

    def check_deadlock(self, input: str) -> dict[str, Any]:
        """
        Check for database deadlocks.
        
        Args:
            input: user input (for context)
        
        Returns:
            Deadlock status and information
        """
        try:
            input_lower = input.lower()
            
            # Q1: Detect active deadlocks with transaction details
            if any(keyword in input_lower for keyword in ['active', 'detect', 'session', 'transaction']):
                has_deadlock = random.choice([True, False])
                
                if has_deadlock:
                    # Return 2-3 deadlocked transactions
                    num_deadlocks = random.randint(2, 3)
                    deadlock_details = random.sample(MOCK_DEADLOCK_DETAILS, num_deadlocks)
                    
                    return {
                        "success": True,
                        "input": input,
                        "deadlocks_detected": True,
                        "status": "ACTIVE DEADLOCK DETECTED",
                        "deadlock_count": num_deadlocks,
                        "transactions": deadlock_details,
                        "recommendation": "Immediate action required - review transactions and consider killing blocking session"
                    }
                else:
                    return {
                        "success": True,
                        "input": input,
                        "deadlocks_detected": False,
                        "status": "NO ACTIVE DEADLOCK",
                        "message": "No active deadlocks detected in the database at this time"
                    }
            
            # Q2: Check deadlock logs for latest occurrence
            elif any(keyword in input_lower for keyword in ['log', 'history', 'latest', 'event', 'occurrence']):
                latest_deadlock = MOCK_DEADLOCK_LOGS[0]  # Most recent
                
                return {
                    "success": True,
                    "input": input,
                    "deadlocks_detected": True,
                    "status": "DEADLOCK LOG FOUND",
                    "latest_event": {
                        "timestamp": latest_deadlock["timestamp"],
                        "deadlock_id": latest_deadlock["deadlock_id"],
                        "affected_queries": latest_deadlock["affected_queries"],
                        "victim_session": latest_deadlock["victim_session"],
                        "resolution": latest_deadlock["resolution"]
                    },
                    "total_events_in_log": len(MOCK_DEADLOCK_LOGS),
                    "message": f"Latest deadlock occurred at {latest_deadlock['timestamp']}"
                }
            
            # Default: Generic deadlock check
            else:
                has_deadlock = random.choice([True, False])
                return {
                    "success": True,
                    "input": input,
                    "deadlocks_detected": has_deadlock,
                    "status": "DEADLOCK DETECTED" if has_deadlock else "NO DEADLOCK",
                    "message": "Use 'active' keyword for transaction details or 'log' for historical events"
                }

        except Exception as e:
            logger.error(f"Deadlock check error: {e}")
            return {"success": False, "error": str(e)}

    def check_file_size(self, input: str) -> dict[str, Any]:
        """
        Check database file size and usage.
        
        Args:
            input: user input (for context)
        
        Returns:
            File size information and warnings
        """
        try:
            input_lower = input.lower()
            
            # Select relevant database based on input
            if 'prod' in input_lower:
                db_data = MOCK_FILE_SIZE_DATA[0]
            elif 'staging' in input_lower or 'stage' in input_lower:
                db_data = MOCK_FILE_SIZE_DATA[1]
            elif 'dev' in input_lower:
                db_data = MOCK_FILE_SIZE_DATA[2]
            else:
                db_data = random.choice(MOCK_FILE_SIZE_DATA)
            
            # Calculate usage percentage with some variance
            max_size_mb = 2048  # 2GB limit
            usage_percent = round((db_data["size_mb"] / max_size_mb) * 100, 2)
            status = "CRITICAL" if usage_percent >= 90.0 else "WARNING" if usage_percent >= 75.0 else "NORMAL"
            
            return {
                "success": True,
                "input": input,
                "database": db_data["database"],
                "current_size_mb": db_data["size_mb"],
                "max_size_mb": max_size_mb,
                "usage_percent": usage_percent,
                "growth_rate_mb_per_day": db_data["growth_rate_mb_per_day"],
                "estimated_days_until_full": db_data["estimated_full_days"],
                "status": status,
                "recommendations": [
                    "Archive old data to reduce database size" if usage_percent > 70 else "Monitor growth trends",
                    "Consider increasing storage allocation" if db_data["estimated_full_days"] < 60 else "Storage growth is manageable",
                    "Implement data retention policies" if usage_percent > 80 else "Current retention policy is adequate"
                ]
            }

        except Exception as e:
            logger.error(f"File size check error: {e}")
            return {"success": False, "error": str(e)}

    def check_abnormal_data(self, input: str) -> dict[str, Any]:
        """
        Check for abnormal data based on input.
        
        Args:
            input: user input to get data to check
        
        Returns:
            Abnormal data detection results
        """
        try:
            input_lower = input.lower()
            
            # Check if input mentions specific table or anomaly type
            has_anomaly = random.choice([True, False])
            
            if has_anomaly:
                # Select 1-2 anomaly patterns
                num_anomalies = random.randint(1, 2)
                anomalies = random.sample(MOCK_ABNORMAL_DATA_PATTERNS, num_anomalies)
                
                total_affected = sum(len(a["affected_rows"]) for a in anomalies)
                
                return {
                    "success": True,
                    "input": input,
                    "has_abnormal_data": True,
                    "status": "ABNORMAL DATA DETECTED",
                    "anomaly_count": num_anomalies,
                    "total_affected_rows": total_affected,
                    "anomalies": [
                        {
                            "table": a["table"],
                            "anomaly_type": a["anomaly"],
                            "severity": a["severity"],
                            "affected_count": len(a["affected_rows"]),
                            "sample_records": a["affected_rows"][:2]  # Show first 2 samples
                        }
                        for a in anomalies
                    ],
                    "recommendations": [
                        "Review data validation rules",
                        "Investigate data entry processes",
                        "Consider implementing constraints to prevent invalid data"
                    ]
                }
            else:
                # No anomalies detected
                total_rows = random.randint(100, 1000)
                return {
                    "success": True,
                    "input": input,
                    "has_abnormal_data": False,
                    "status": "NORMAL",
                    "total_rows_scanned": total_rows,
                    "abnormal_count": 0,
                    "message": "All data appears normal - no anomalies detected"
                }

        except Exception as e:
            logger.error(f"Abnormal data check error: {e}")
            return {"success": False, "error": str(e)}

    def check_batch_data(self, input: str) -> dict[str, Any]:
        """
        Check batch data for abnormalities.
        
        Args:
            input: user input to get batch data
        
        Returns:
            Batch data check results
        """
        try:
            input_lower = input.lower()
            
            # Determine if there are batch issues
            has_issues = random.choice([True, False])
            
            if has_issues:
                # Select 1-2 batch issues from mock data
                num_batches = random.randint(1, 2)
                batch_issues = random.sample(MOCK_BATCH_DATA_ISSUES, num_batches)
                
                total_processed = sum(b["records_processed"] for b in batch_issues)
                total_failed = sum(b["failed_records"] for b in batch_issues)
                failure_rate = round((total_failed / total_processed) * 100, 2)
                
                return {
                    "success": True,
                    "input": input,
                    "has_abnormal_data": True,
                    "status": "BATCH ISSUES DETECTED",
                    "total_batches_analyzed": num_batches,
                    "total_records_processed": total_processed,
                    "total_failed_records": total_failed,
                    "failure_rate_percent": failure_rate,
                    "batch_details": batch_issues,
                    "recommendations": [
                        "Review batch processing logs for detailed error messages",
                        "Implement retry mechanism for transient failures",
                        "Validate data before batch processing",
                        "Consider increasing batch timeout settings" if any("timeout" in b.get("failure_reasons", {}) for b in batch_issues) else "Monitor data quality at source"
                    ]
                }
            else:
                # No batch issues
                total_records = random.randint(5000, 50000)
                return {
                    "success": True,
                    "input": input,
                    "has_abnormal_data": False,
                    "status": "NORMAL",
                    "total_records_processed": total_records,
                    "failed_records": 0,
                    "failure_rate_percent": 0.0,
                    "message": "All batch operations completed successfully"
                }

        except Exception as e:
            logger.error(f"Batch data check error: {e}")
            return {"success": False, "error": str(e)}


# Initialize database agent
db_agent = DatabaseAgent()


@mcp.tool(description="Check DB query response time for slow query detection")
async def check_query_response_time(
    input: str = Field(..., description="user input to check"),
) -> dict[str, Any]:
    """
    Check database query response time and detect slow queries.
    
    Simple 1-input function: input only.
    Returns response time and SLOW/NORMAL status.
    """
    return db_agent.check_query_response_time(input)


@mcp.tool(description="Check for database deadlocks")
async def check_deadlock(
    input: str = Field(..., description="user input (for context)"),
) -> dict[str, Any]:
    """
    Check for database deadlocks.
    
    Simple 1-input function: input only.
    Returns deadlock status.
    """
    return db_agent.check_deadlock(input)


@mcp.tool(description="Check database file size and warn if exceeds 90% threshold")
async def check_file_size(
    input: str = Field(..., description="user input (for context)"),
) -> dict[str, Any]:
    """
    Check database file size and warn if it exceeds 90% threshold.
    
    Simple 1-input function: input only.
    Returns file size and usage percentage.
    """
    return db_agent.check_file_size(input)


@mcp.tool(description="Check for abnormal data based on operator-defined rules")
async def check_abnormal_data(
    input: str = Field(..., description="user input to get data to check"),
) -> dict[str, Any]:
    """
    Check interface data for abnormalities.
    
    Simple 1-input function: input only.
    Returns abnormal data count and status.
    """
    return db_agent.check_abnormal_data(input)


@mcp.tool(description="Check batch data for abnormalities")
async def check_batch_data(
    input: str = Field(..., description="user input to get batch data"),
) -> dict[str, Any]:
    """
    Check batch data for abnormalities.
    
    Simple 1-input function: input only.
    Returns batch data abnormality count and status.
    """
    return db_agent.check_batch_data(input)


def main():
    """Main server entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Database Agent MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (stdio or http)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=9002, help="HTTP port")

    args = parser.parse_args()

    if args.transport == "http":
        logger.info(f"Starting Database Agent MCP Server on HTTP at {args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        logger.info("Starting Database Agent MCP Server on stdio")
        mcp.run()


if __name__ == "__main__":
    main()
