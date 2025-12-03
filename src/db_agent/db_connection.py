#!/usr/bin/env python3
"""Database connection module for PostgreSQL."""

import logging
import os
from typing import Any, Optional
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def convert_decimals(obj: Any) -> Any:
    """Recursively convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj


class DatabaseConnection:
    """Simple PostgreSQL connection manager."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "testdb",
        user: str = "dbagent",
        password: str = "dbagent123"
    ):
        """Initialize database connection parameters."""
        self.host = os.getenv("DB_HOST", host)
        self.port = int(os.getenv("DB_PORT", port))
        self.database = os.getenv("DB_NAME", database)
        self.user = os.getenv("DB_USER", user)
        self.password = os.getenv("DB_PASSWORD", password)

        self._connection = None
        logger.info(f"Database connection configured for {self.host}:{self.port}/{self.database}")

    def connect(self) -> None:
        """Establish database connection."""
        try:
            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=5
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    @contextmanager
    def cursor(self, dict_cursor: bool = True):
        """Context manager for database cursor."""
        if not self._connection:
            self.connect()

        cursor_factory = RealDictCursor if dict_cursor else None
        cur = self._connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cur.close()

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> list[dict[str, Any]] | None:
        """Execute a query and optionally fetch results."""
        with self.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                results = cur.fetchall()
                return convert_decimals(results)
            return None

    def execute_timed_query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> tuple[list[dict[str, Any]], float]:
        """Execute query and return results with execution time in milliseconds."""
        import time

        with self.cursor() as cur:
            start_time = time.perf_counter()
            cur.execute(query, params)
            results = cur.fetchall()
            end_time = time.perf_counter()

            execution_time_ms = (end_time - start_time) * 1000
            return convert_decimals(results), execution_time_ms

    def get_database_size(self) -> dict[str, Any]:
        """Get current database size."""
        query = "SELECT * FROM v_database_stats"
        with self.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            return convert_decimals(dict(result)) if result else {}

    def check_deadlocks(self) -> list[dict[str, Any]]:
        """Check for active deadlocks and blocking sessions."""
        query = """
        SELECT
            blocked.pid AS blocked_pid,
            blocked.usename AS blocked_user,
            blocked.query AS blocked_query,
            blocking.pid AS blocking_pid,
            blocking.usename AS blocking_user,
            blocking.query AS blocking_query,
            EXTRACT(EPOCH FROM (NOW() - blocked.query_start)) * 1000 AS wait_time_ms
        FROM pg_stat_activity AS blocked
        JOIN pg_locks AS blocked_locks ON blocked.pid = blocked_locks.pid
        JOIN pg_locks AS blocking_locks ON
            blocked_locks.locktype = blocking_locks.locktype
            AND blocked_locks.database IS NOT DISTINCT FROM blocking_locks.database
            AND blocked_locks.relation IS NOT DISTINCT FROM blocking_locks.relation
            AND blocked_locks.page IS NOT DISTINCT FROM blocking_locks.page
            AND blocked_locks.tuple IS NOT DISTINCT FROM blocking_locks.tuple
            AND blocked_locks.virtualxid IS NOT DISTINCT FROM blocking_locks.virtualxid
            AND blocked_locks.transactionid IS NOT DISTINCT FROM blocking_locks.transactionid
            AND blocked_locks.classid IS NOT DISTINCT FROM blocking_locks.classid
            AND blocked_locks.objid IS NOT DISTINCT FROM blocking_locks.objid
            AND blocked_locks.objsubid IS NOT DISTINCT FROM blocking_locks.objsubid
            AND blocked_locks.pid != blocking_locks.pid
        JOIN pg_stat_activity AS blocking ON blocking.pid = blocking_locks.pid
        WHERE NOT blocked_locks.granted
        AND blocking_locks.granted;
        """

        with self.cursor() as cur:
            cur.execute(query)
            return convert_decimals(cur.fetchall())

    def get_slow_queries(self, threshold_ms: float = 1000.0) -> list[dict[str, Any]]:
        """Get slow queries from query_stats table."""
        query = """
        SELECT
            query_text,
            execution_time_ms,
            rows_affected,
            executed_at
        FROM query_stats
        WHERE execution_time_ms > %s
        ORDER BY execution_time_ms DESC
        LIMIT 10;
        """

        with self.cursor() as cur:
            cur.execute(query, (threshold_ms,))
            return convert_decimals(cur.fetchall())


_db_connection: Optional[DatabaseConnection] = None


def get_db_connection() -> DatabaseConnection:
    """Get or create database connection singleton."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
        _db_connection.connect()
    return _db_connection
