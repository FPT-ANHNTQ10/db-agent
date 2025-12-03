#!/usr/bin/env python3
"""Trigger slow query."""

import psycopg2
import time

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "user": "dbagent",
    "password": "dbagent123"
}


def run_slow_query(desc, query):
    """Execute query and measure time."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"\n[QUERY] {desc}")
    print(f"SQL: {query[:100]}...")

    start = time.perf_counter()
    cur.execute(query)
    results = cur.fetchall()
    end = time.perf_counter()

    exec_time_ms = (end - start) * 1000
    print(f"[RESULT] Rows: {len(results)}, Time: {exec_time_ms:.2f}ms")

    # Store in query_stats
    cur.execute(
        """INSERT INTO query_stats (query_text, execution_time_ms, rows_affected, is_slow)
           VALUES (%s, %s, %s, %s)""",
        (query, exec_time_ms, len(results), exec_time_ms > 1000)
    )
    conn.commit()

    cur.close()
    conn.close()

    return exec_time_ms


def main():
    print("=" * 70)
    print("SLOW QUERY TRIGGER")
    print("=" * 70)

    queries = [
        ("Full table scan on unindexed category",
         "SELECT * FROM products WHERE category='electronics'"),

        ("Complex JOIN",
         """SELECT p.name, c.name, o.total_amount
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE p.category='electronics'"""),

        ("LIKE on text field",
         "SELECT * FROM products WHERE description LIKE '%product%'"),

        ("Aggregate on large table",
         "SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category"),

        ("Subquery",
         """SELECT * FROM orders
            WHERE customer_id IN (
                SELECT customer_id FROM customers WHERE status='active'
            )""")
    ]

    total_time = 0
    for desc, query in queries:
        exec_time = run_slow_query(desc, query)
        total_time += exec_time
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print(f"Total: {total_time:.2f}ms")
    print("Run check_query_response_time to see results.")
    print("=" * 70)


if __name__ == "__main__":
    main()
