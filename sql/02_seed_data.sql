-- Seed data for testing

-- ============================================================================
-- CUSTOMERS - For JOIN queries and deadlock testing
-- ============================================================================
INSERT INTO customers (name, email, status) VALUES
    ('Alice Johnson', 'alice@example.com', 'active'),
    ('Bob Smith', 'bob@example.com', 'active'),
    ('Charlie Brown', 'charlie@example.com', 'inactive'),
    ('Diana Prince', 'diana@example.com', 'active'),
    ('Ethan Hunt', 'ethan@example.com', 'active');

-- ============================================================================
-- INVENTORY
-- ============================================================================
INSERT INTO inventory (product_name, current_stock, max_threshold, category) VALUES
    ('Laptop Pro', 50, 100, 'electronics'),
    ('Wireless Mouse', 200, 500, 'electronics'),
    ('Desk Chair', 30, 100, 'furniture'),
    ('Standing Desk', 15, 50, 'furniture'),
    ('USB-C Cable', 500, 1000, 'electronics'),
    ('Monitor 27"', 40, 80, 'electronics'),
    ('Keyboard Mechanical', 80, 200, 'electronics'),
    ('Desk Lamp', 60, 150, 'furniture');

-- ============================================================================
-- ORDERS
-- ============================================================================
INSERT INTO orders (customer_id, product_id, quantity, total_amount, status) VALUES
    (1, 1, 1, 1299.99, 'processing'),
    (2, 2, 2, 39.98, 'pending'),
    (3, 3, 1, 299.99, 'shipped'),
    (4, 4, 1, 599.99, 'pending'),
    (5, 5, 10, 99.90, 'processing'),
    (1, 6, 2, 799.98, 'pending'),
    (2, 7, 1, 129.99, 'pending');

-- ============================================================================
-- ORDER ITEMS
-- ============================================================================
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
    (1, 1, 1, 1299.99),
    (2, 2, 2, 19.99),
    (3, 3, 1, 299.99),
    (4, 4, 1, 599.99),
    (5, 5, 10, 9.99),
    (6, 6, 2, 399.99),
    (7, 7, 1, 129.99);

-- ============================================================================
-- PRODUCTS (large dataset for slow queries)
-- ============================================================================
INSERT INTO products (name, description, category, price, stock_count)
SELECT
    'Product ' || i,
    'Description for product ' || i,
    CASE WHEN i % 4 = 0 THEN 'electronics'
         WHEN i % 4 = 1 THEN 'furniture'
         WHEN i % 4 = 2 THEN 'office'
         ELSE 'accessories'
    END,
    (random() * 1000 + 10)::DECIMAL(10,2),
    (random() * 500)::INTEGER
FROM generate_series(1, 10000) AS i;

-- ============================================================================
-- ABNORMAL DATA
-- ============================================================================

INSERT INTO transaction_log (transaction_type, amount, customer_id) VALUES
    ('refund', -150.00, 1),
    ('chargeback', -75.50, 2),
    ('adjustment', -200.00, 3);

INSERT INTO inventory (product_name, current_stock, max_threshold, category) VALUES
    ('Defective Item A', 999999, 10000, 'electronics'),
    ('Defective Item B', 888888, 5000, 'electronics');

BEGIN;
    ALTER TABLE orders DISABLE TRIGGER ALL;
    INSERT INTO orders (customer_id, product_id, quantity, total_amount, status) VALUES
        (1, 1, 1, -150.00, 'error'),
        (2, 2, 1, -75.50, 'error');
    ALTER TABLE orders ENABLE TRIGGER ALL;
COMMIT;

-- ============================================================================
-- BATCH JOBS
-- ============================================================================
INSERT INTO batch_jobs (batch_id, job_type, total_records, processed_records, failed_records, status, started_at) VALUES
    ('BATCH-2024-001', 'import_orders', 10000, 9955, 45, 'completed', NOW() - INTERVAL '1 hour'),
    ('BATCH-2024-002', 'import_customers', 5000, 4988, 12, 'completed', NOW() - INTERVAL '3 hours'),
    ('BATCH-2024-003', 'import_products', 1000, 500, 0, 'processing', NOW() - INTERVAL '30 minutes');

INSERT INTO batch_errors (batch_id, record_data, error_type, error_message) VALUES
    ('BATCH-2024-001', '{"order_id": 12345, "amount": -100}', 'validation_error', 'Negative amount not allowed'),
    ('BATCH-2024-001', '{"order_id": 12346, "customer_id": 999}', 'foreign_key_violation', 'Customer does not exist'),
    ('BATCH-2024-001', '{"order_id": 12347}', 'timeout', 'Query timeout after 30s'),
    ('BATCH-2024-002', '{"email": "duplicate@test.com"}', 'duplicate_key', 'Email already exists');

INSERT INTO batch_staging (batch_id, record_data, is_processed, has_error, error_message) VALUES
    ('BATCH-2024-003', '{"name": "Product A", "price": 100}', true, false, NULL),
    ('BATCH-2024-003', '{"name": "Product B", "price": -50}', false, true, 'Negative price'),
    ('BATCH-2024-003', '{"name": "Product C"}', false, true, 'Missing required field: price');
