#!/usr/bin/env python3
"""Insert abnormal data."""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "user": "dbagent",
    "password": "dbagent123"
}


def insert_abnormal_orders(conn):
    """Insert orders with negative amounts."""
    cur = conn.cursor()

    print("\n[1] Inserting orders with negative amounts...")

    # Drop the CHECK constraint temporarily to insert abnormal data
    cur.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS check_positive_amount")

    # ABNORMAL: Order amounts are negative (business logic violation)
    # Normal: amount should be >= 0
    abnormal_orders = [
        (1, 1, 1, -250.00, 'error'),
        (2, 2, 2, -150.75, 'error'),
        (3, 3, 1, -99.99, 'error'),
    ]

    for customer_id, product_id, quantity, amount, status in abnormal_orders:
        cur.execute(
            """INSERT INTO orders (customer_id, product_id, quantity, total_amount, status)
               VALUES (%s, %s, %s, %s, %s)""",
            (customer_id, product_id, quantity, amount, status)
        )
        print(f"   Inserted: customer={customer_id}, amount={amount}")

    # Re-add the constraint (marked as NOT VALID to allow existing bad data)
    cur.execute("ALTER TABLE orders ADD CONSTRAINT check_positive_amount CHECK (total_amount >= 0) NOT VALID")
    conn.commit()
    print("   Done!")


def insert_excessive_inventory(conn):
    """Insert inventory with excessive stock."""
    cur = conn.cursor()

    print("\n[2] Inserting excessive inventory...")

    # ABNORMAL: Stock exceeds max_threshold (warehouse capacity violation)
    # Normal: current_stock should be <= max_threshold
    abnormal_inventory = [
        ('Overflow Product A', 999999, 10000, 'electronics'),
        ('Overflow Product B', 888888, 5000, 'furniture'),
        ('Overflow Product C', 777777, 8000, 'office'),
    ]

    for name, stock, threshold, category in abnormal_inventory:
        cur.execute(
            """INSERT INTO inventory (product_name, current_stock, max_threshold, category)
               VALUES (%s, %s, %s, %s)""",
            (name, stock, threshold, category)
        )
        print(f"   Inserted: {name}, stock={stock} (exceeds {threshold})")

    conn.commit()
    print("   Done!")


def insert_abnormal_transactions(conn):
    """Insert large negative transactions."""
    cur = conn.cursor()

    print("\n[3] Inserting large negative transactions...")

    # ABNORMAL: Large negative amounts (exceeds -$100 threshold)
    # Normal: small negatives OK, but large ones indicate fraud/errors
    abnormal_transactions = [
        ('refund', -500.00, 1),
        ('chargeback', -350.50, 2),
        ('adjustment', -750.00, 3),
        ('error', -1000.00, 4),
    ]

    for trans_type, amount, customer_id in abnormal_transactions:
        cur.execute(
            """INSERT INTO transaction_log (transaction_type, amount, customer_id)
               VALUES (%s, %s, %s)""",
            (trans_type, amount, customer_id)
        )
        print(f"   Inserted: type={trans_type}, amount={amount}")

    conn.commit()
    print("   Done!")


def main():
    print("=" * 70)
    print("ABNORMAL DATA INSERTION")
    print("=" * 70)

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        insert_abnormal_orders(conn)
        insert_excessive_inventory(conn)
        insert_abnormal_transactions(conn)

        print("\n" + "=" * 70)
        print("Abnormal data inserted.")
        print("Run check_abnormal_data to detect.")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
