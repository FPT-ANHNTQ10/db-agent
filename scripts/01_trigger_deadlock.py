#!/usr/bin/env python3
import psycopg2
import time
import threading

DB = {
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "user": "dbagent",
    "password": "dbagent123",
}

# Đồng bộ giữa hai thread
lock1_acquired = threading.Event()
lock2_acquired = threading.Event()

def txn1():
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        cur.execute("SET deadlock_timeout = '10s'")  # giữ chờ 10s để có thời gian quan sát

        # Lock row trong orders
        cur.execute("SELECT * FROM orders WHERE order_id = 1 FOR UPDATE")
        lock1_acquired.set()

        # Chờ txn2 giữ lock inventory
        lock2_acquired.wait()

        # Chờ thêm để chắc chắn 2 thread bị block nhau
        time.sleep(1)

        # Gây deadlock
        cur.execute("SELECT * FROM inventory WHERE product_id = 1 FOR UPDATE")

        conn.commit()

    except psycopg2.Error as e:
        print(f"[T1] DEADLOCK or rollback: {e.pgcode} - {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def txn2():
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        cur.execute("SET deadlock_timeout = '10s'")

        # Lock row trong inventory
        cur.execute("SELECT * FROM inventory WHERE product_id = 1 FOR UPDATE")
        lock2_acquired.set()

        # Chờ txn1 giữ lock orders
        lock1_acquired.wait()

        time.sleep(1)

        # Gây deadlock
        cur.execute("SELECT * FROM orders WHERE order_id = 1 FOR UPDATE")

        conn.commit()

    except psycopg2.Error as e:
        print(f"[T2] DEADLOCK or rollback: {e.pgcode} - {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def run_deadlock_round(round_id):
    print(f"\n=== ROUND {round_id} ===")
    lock1_acquired.clear()
    lock2_acquired.clear()

    t1 = threading.Thread(target=txn1)
    t2 = threading.Thread(target=txn2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"=== END ROUND {round_id} ===")


def main():
    round_id = 1
    while True:
        run_deadlock_round(round_id)
        round_id += 1
        time.sleep(1)  # tránh spam quá mạnh DB


if __name__ == "__main__":
    main()
