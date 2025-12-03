#!/usr/bin/env python3
"""Simulate batch processing with failures."""

import psycopg2
import time
import random
import json

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "user": "dbagent",
    "password": "dbagent123"
}


def create_batch_job(conn, batch_id):
    """Create batch job."""
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO batch_jobs (batch_id, job_type, status, started_at)
           VALUES (%s, %s, %s, NOW())""",
        (batch_id, 'import_orders', 'processing')
    )
    conn.commit()
    print(f"[BATCH] Created: {batch_id}")


def process_batch_records(conn, batch_id, num_records=100):
    """Process batch with failures."""
    cur = conn.cursor()

    processed = 0
    failed = 0

    print(f"\n[BATCH] Processing {num_records} records...")

    for i in range(1, num_records + 1):
        failure_type = None

        if i % 10 == 0:
            failure_type = "duplicate_key"
            failed += 1
        elif i % 15 == 0:
            failure_type = "validation_error"
            failed += 1
        elif i % 20 == 0:
            failure_type = "foreign_key_violation"
            failed += 1
        elif i % 50 == 0:
            failure_type = "timeout"
            failed += 1
        else:
            processed += 1

        record_data = {
            "record_id": i,
            "customer_id": random.randint(1, 100),
            "amount": random.uniform(10, 1000)
        }

        cur.execute(
            """INSERT INTO batch_staging (batch_id, record_data, is_processed, has_error, error_message)
               VALUES (%s, %s, %s, %s, %s)""",
            (batch_id, json.dumps(record_data), failure_type is None, failure_type is not None, failure_type)
        )

        if failure_type:
            error_messages = {
                "duplicate_key": "Duplicate key violation",
                "validation_error": "Validation failed: amount must be positive",
                "foreign_key_violation": "Foreign key constraint violation",
                "timeout": "Query timeout after 30s"
            }

            cur.execute(
                """INSERT INTO batch_errors (batch_id, record_data, error_type, error_message)
                   VALUES (%s, %s, %s, %s)""",
                (batch_id, json.dumps(record_data), failure_type, error_messages[failure_type])
            )

        if i % 20 == 0:
            print(f"   Processed: {i}/{num_records} (Failed: {failed})")

    conn.commit()
    return processed, failed


def complete_batch_job(conn, batch_id, processed, failed):
    """Mark batch as completed."""
    cur = conn.cursor()

    total = processed + failed

    cur.execute(
        """UPDATE batch_jobs
           SET status = 'completed',
               total_records = %s,
               processed_records = %s,
               failed_records = %s,
               completed_at = NOW()
           WHERE batch_id = %s""",
        (total, processed, failed, batch_id)
    )
    conn.commit()

    print(f"\n[BATCH] Completed: {batch_id}")
    print(f"   Total: {total}, Success: {processed}, Failed: {failed}")


def main():
    print("=" * 70)
    print("BATCH PROCESSING FAILURE TRIGGER")
    print("=" * 70)

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        batch_id = f"BATCH-{int(time.time())}"
        create_batch_job(conn, batch_id)

        processed, failed = process_batch_records(conn, batch_id, num_records=100)

        complete_batch_job(conn, batch_id, processed, failed)

        print("\n" + "=" * 70)
        print("Batch processing complete with failures.")
        print("Run check_batch_data to see analysis.")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
