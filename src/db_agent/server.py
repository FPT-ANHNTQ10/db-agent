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
from typing import Any

from fastmcp import FastMCP
from pydantic import Field
from db_agent.db_connection import get_db_connection

# Configure logging to stderr to avoid MCP protocol interference
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(name="db-agent", version="1.0.0")




class DatabaseAgent:
    """Database operations agent with support for multiple engines."""

    def __init__(self):
        """Initialize the database agent."""
        logger.info("Database Agent initialized for monitoring tools.")

    def _get_slow_query_recommendations(self, query: str) -> list[str]:
        """Generate recommendations for slow queries."""
        recommendations = []
        query_lower = query.lower()
        if "where" in query_lower and "category" in query_lower:
            recommendations.append("Add index on category column")
        if "join" in query_lower:
            recommendations.append("Review JOIN strategy and indexes")
        if "*" in query:
            recommendations.append("Select specific columns instead of *")
        if "like" in query_lower:
            recommendations.append("Avoid LIKE operations on large tables")
        return recommendations if recommendations else ["Consider adding appropriate indexes", "Review query execution plan"]

    def _get_size_recommendations(self, usage_percent: float, days_until_full: int) -> list[str]:
        """Generate recommendations for database size."""
        recommendations = []
        if usage_percent > 70:
            recommendations.append("Archive old data to reduce database size")
        if days_until_full < 60:
            recommendations.append("Consider increasing storage allocation")
        if usage_percent > 80:
            recommendations.append("Implement data retention policies")
        if not recommendations:
            recommendations.append("Monitor growth trends")
        return recommendations

    def check_query_response_time(self, input: str) -> dict[str, Any]:
        """
        Check DB query response time for slow query detection.

        Args:
            input: SQL query to execute and measure, or text to check for existing slow queries

        Returns:
            Query response time and slow query status
        """
        try:
            db = get_db_connection()
            threshold_ms = 1000.0

            input_lower = input.lower()

            # If input contains a SQL query, execute it and measure time
            if any(keyword in input_lower for keyword in ['select', 'update', 'delete', 'insert']):
                results, execution_time = db.execute_timed_query(input)

                # Store in query_stats
                db.execute_query(
                    """INSERT INTO query_stats (query_text, execution_time_ms, rows_affected, is_slow)
                       VALUES (%s, %s, %s, %s)""",
                    (input, execution_time, len(results), execution_time > threshold_ms),
                    fetch=False
                )

                is_slow = execution_time > threshold_ms

                return {
                    "success": True,
                    "input": input,
                    "query": input,
                    "response_time_ms": round(execution_time, 2),
                    "rows_returned": len(results),
                    "is_slow": is_slow,
                    "status": "SLOW" if is_slow else "NORMAL",
                    "threshold_ms": threshold_ms,
                    "recommendations": self._get_slow_query_recommendations(input) if is_slow else []
                }
            else:
                # Check for existing slow queries
                slow_queries = db.get_slow_queries(threshold_ms)

                if slow_queries:
                    return {
                        "success": True,
                        "input": input,
                        "slow_queries_found": len(slow_queries),
                        "status": "SLOW QUERIES DETECTED",
                        "queries": slow_queries,
                        "threshold_ms": threshold_ms
                    }
                else:
                    return {
                        "success": True,
                        "input": input,
                        "status": "NORMAL",
                        "message": "No slow queries detected"
                    }

        except Exception as e:
            logger.error(f"Query response time check error: {e}")
            return {"success": False, "error": str(e)}

    def check_deadlock(self, input: str) -> dict[str, Any]:
        """
        Check for database deadlocks.

        Args:
            input: Context text to trigger deadlock check

        Returns:
            Deadlock status and information
        """
        try:
            db = get_db_connection()

            # Check for active blocking/deadlock situations
            deadlocks = db.check_deadlocks()

            if deadlocks:
                return {
                    "success": True,
                    "input": input,
                    "deadlocks_detected": True,
                    "status": "ACTIVE DEADLOCK DETECTED",
                    "deadlock_count": len(deadlocks),
                    "transactions": [
                        {
                            "blocked_session": d["blocked_pid"],
                            "blocked_query": d["blocked_query"],
                            "blocking_session": d["blocking_pid"],
                            "blocking_query": d["blocking_query"],
                            "wait_time_ms": round(d["wait_time_ms"], 2)
                        }
                        for d in deadlocks
                    ],
                    "recommendation": "Review blocking queries and consider terminating long-running transactions"
                }
            else:
                return {
                    "success": True,
                    "input": input,
                    "deadlocks_detected": False,
                    "status": "NO ACTIVE DEADLOCK",
                    "message": "No deadlocks or blocking sessions detected"
                }

        except Exception as e:
            logger.error(f"Deadlock check error: {e}")
            return {"success": False, "error": str(e)}

    def check_file_size(self, input: str) -> dict[str, Any]:
        """
        Check database file size and usage.

        Args:
            input: Context text to trigger size check

        Returns:
            File size information and warnings
        """
        try:
            db = get_db_connection()

            # Get database size
            size_info = db.get_database_size()

            # Calculate usage against a configurable limit
            max_size_mb = 2048  # 2GB default limit
            size_mb = size_info["size_mb"]
            usage_percent = round((size_mb / max_size_mb) * 100, 2)

            # Determine status
            if usage_percent >= 90.0:
                status = "CRITICAL"
            elif usage_percent >= 75.0:
                status = "WARNING"
            else:
                status = "NORMAL"

            # Estimate growth (simplified)
            growth_rate_mb = 15.0
            estimated_days = int((max_size_mb - size_mb) / growth_rate_mb) if growth_rate_mb > 0 else 999

            return {
                "success": True,
                "input": input,
                "database": size_info["database_name"],
                "current_size_mb": size_info["size_mb"],
                "current_size_gb": size_info["size_gb"],
                "max_size_mb": max_size_mb,
                "usage_percent": usage_percent,
                "growth_rate_mb_per_day": growth_rate_mb,
                "estimated_days_until_full": estimated_days,
                "status": status,
                "recommendations": self._get_size_recommendations(usage_percent, estimated_days)
            }

        except Exception as e:
            logger.error(f"File size check error: {e}")
            return {"success": False, "error": str(e)}

    def check_abnormal_data(self, tables: str) -> dict[str, Any]:
        """
        Check for abnormal data patterns in database.

        Args:
            tables: Tables to check - "all", "orders", "inventory", or "transactions"

        Returns:
            Abnormal data detection results
        """
        try:
            db = get_db_connection()

            anomalies = []
            tables_lower = tables.lower()

            # Check 1: Negative amounts in orders
            if tables_lower in ["all", "orders"]:
                query = """
                SELECT order_id, customer_id, total_amount, status
                FROM orders
                WHERE total_amount < 0
                LIMIT 10;
                """
                negative_orders = db.execute_query(query)
                if negative_orders:
                    anomalies.append({
                        "table": "orders",
                        "anomaly_type": "Negative order amounts detected",
                        "severity": "HIGH",
                        "affected_count": len(negative_orders),
                        "sample_records": negative_orders[:3]
                    })

            # Check 2: Excessive inventory
            if tables_lower in ["all", "inventory"]:
                query = """
                SELECT product_id, product_name, current_stock, max_threshold
                FROM inventory
                WHERE current_stock > max_threshold
                LIMIT 10;
                """
                excessive_inventory = db.execute_query(query)
                if excessive_inventory:
                    anomalies.append({
                        "table": "inventory",
                        "anomaly_type": "Stock count exceeds maximum threshold",
                        "severity": "MEDIUM",
                        "affected_count": len(excessive_inventory),
                        "sample_records": excessive_inventory[:3]
                    })

            # Check 3: Negative transactions
            if tables_lower in ["all", "transactions", "transaction_log"]:
                query = """
                SELECT log_id, transaction_type, amount, customer_id, created_at
                FROM transaction_log
                WHERE amount < -100
                LIMIT 10;
                """
                negative_transactions = db.execute_query(query)
                if negative_transactions:
                    anomalies.append({
                        "table": "transaction_log",
                        "anomaly_type": "Large negative transactions detected",
                        "severity": "HIGH",
                        "affected_count": len(negative_transactions),
                        "sample_records": negative_transactions[:3]
                    })

            if anomalies:
                return {
                    "success": True,
                    "tables_checked": tables,
                    "has_abnormal_data": True,
                    "status": "ABNORMAL DATA DETECTED",
                    "anomaly_count": len(anomalies),
                    "total_affected_rows": sum(a["affected_count"] for a in anomalies),
                    "anomalies": anomalies,
                    "recommendations": [
                        "Review data validation rules",
                        "Investigate data entry processes",
                        "Consider implementing CHECK constraints"
                    ]
                }
            else:
                return {
                    "success": True,
                    "tables_checked": tables,
                    "has_abnormal_data": False,
                    "status": "NORMAL",
                    "message": f"No data anomalies detected in {tables}"
                }

        except Exception as e:
            logger.error(f"Abnormal data check error: {e}")
            return {"success": False, "error": str(e)}

    def check_batch_data(self, hours: int = 24, limit: int = 5) -> dict[str, Any]:
        """
        Check batch processing jobs for failures.

        Args:
            hours: Look back period in hours
            limit: Maximum number of batch jobs to return

        Returns:
            Batch data check results
        """
        try:
            db = get_db_connection()

            # Get recent batch jobs with failures within time window
            query = """
            SELECT
                batch_id,
                job_type,
                total_records,
                processed_records,
                failed_records,
                status,
                started_at,
                completed_at
            FROM batch_jobs
            WHERE failed_records > 0
                AND started_at >= NOW() - INTERVAL '%s hours'
            ORDER BY started_at DESC
            LIMIT %s;
            """
            batch_issues = db.execute_query(query, (hours, limit))

            if batch_issues:
                # Get detailed error breakdown
                batch_ids = [b["batch_id"] for b in batch_issues]
                placeholders = ','.join(['%s'] * len(batch_ids))

                error_query = f"""
                SELECT
                    batch_id,
                    error_type,
                    COUNT(*) as error_count
                FROM batch_errors
                WHERE batch_id IN ({placeholders})
                GROUP BY batch_id, error_type;
                """
                error_breakdown = db.execute_query(error_query, tuple(batch_ids))

                # Build failure_reasons dict per batch
                failure_reasons_map = {}
                for error in error_breakdown:
                    bid = error["batch_id"]
                    if bid not in failure_reasons_map:
                        failure_reasons_map[bid] = {}
                    failure_reasons_map[bid][error["error_type"]] = error["error_count"]

                # Enrich batch issues with error details
                for batch in batch_issues:
                    batch["failure_reasons"] = failure_reasons_map.get(batch["batch_id"], {})

                total_processed = sum(b["processed_records"] for b in batch_issues)
                total_failed = sum(b["failed_records"] for b in batch_issues)
                failure_rate = round((total_failed / total_processed) * 100, 2) if total_processed > 0 else 0

                return {
                    "success": True,
                    "time_window_hours": hours,
                    "limit": limit,
                    "has_abnormal_data": True,
                    "status": "BATCH ISSUES DETECTED",
                    "total_batches_analyzed": len(batch_issues),
                    "total_records_processed": total_processed,
                    "total_failed_records": total_failed,
                    "failure_rate_percent": failure_rate,
                    "batch_details": batch_issues,
                    "recommendations": [
                        "Review batch processing logs",
                        "Implement retry mechanism for transient failures",
                        "Validate data before batch processing"
                    ]
                }
            else:
                return {
                    "success": True,
                    "time_window_hours": hours,
                    "limit": limit,
                    "has_abnormal_data": False,
                    "status": "NORMAL",
                    "message": f"No batch failures detected in last {hours} hours"
                }

        except Exception as e:
            logger.error(f"Batch data check error: {e}")
            return {"success": False, "error": str(e)}


# Initialize database agent
db_agent = DatabaseAgent()


@mcp.tool(description="Check DB query response time - Execute SQL query to measure time or check for existing slow queries")
async def check_query_response_time(
    query: str = Field(..., description="SQL query to execute (SELECT/UPDATE/INSERT/etc) or 'check' to list slow queries"),
    threshold_ms: float = Field(1000.0, description="Slow query threshold in milliseconds (default: 1000)"),
):
    """
    Check database query response time and detect slow queries.

    If query contains SQL: executes and measures time.
    If query is 'check' or non-SQL: returns existing slow queries.
    """
    # Pass to agent with threshold
    result = db_agent.check_query_response_time(query)
    # Override threshold if specified
    if threshold_ms != 1000.0 and isinstance(result, dict) and result.get("success"):
        result["threshold_ms"] = threshold_ms
        if "is_slow" in result:
            result["is_slow"] = result.get("response_time_ms", 0) > threshold_ms
            result["status"] = "SLOW" if result["is_slow"] else "NORMAL"
    return result


@mcp.tool(description="Check for active database deadlocks and blocking sessions in real-time")
async def check_deadlock():
    """
    Check for active database deadlocks and blocking sessions.

    Queries pg_locks and pg_stat_activity to detect real-time deadlocks.
    Returns blocking/blocked sessions with wait times.
    No parameters needed - always checks current state.
    """
    return db_agent.check_deadlock("check")


@mcp.tool(description="Check current database file size and calculate usage percentage (warns if >90%)")
async def check_file_size():
    """
    Check database file size and warn if exceeds threshold.

    Queries pg_database_size() for actual database size in MB/GB.
    Returns size, usage %, growth estimate, and recommendations.
    No parameters needed - checks current database.
    """
    return db_agent.check_file_size("check")


@mcp.tool(description="Scan database for abnormal data patterns (negative amounts, excessive values, invalid data)")
async def check_abnormal_data(
    tables: str = Field("all", description="Tables to check: 'all', 'orders', 'inventory', or 'transactions'"),
):
    """
    Check database for data abnormalities.

    Scans specified tables for:
    - orders: Negative amounts
    - inventory: Stock exceeding thresholds
    - transactions: Large negative values
    Returns anomalies with severity and sample records.
    """
    return db_agent.check_abnormal_data(tables)


@mcp.tool(description="Analyze recent batch jobs for failures and error patterns")
async def check_batch_data(
    hours: int = Field(24, description="Look back period in hours (default: 24)"),
    limit: int = Field(5, description="Maximum number of batch jobs to return (default: 5)"),
):
    """
    Check batch processing jobs for failures and errors.

    Queries batch_jobs and batch_errors tables for recent failures.
    Returns failure statistics, error breakdown by type, and recommendations.
    """
    return db_agent.check_batch_data(hours=hours, limit=limit)


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
