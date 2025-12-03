-- Schema for DB Agent Testing

-- ============================================================================
-- TABLES FOR DEADLOCK TESTING
-- ============================================================================

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0,
    max_threshold INTEGER NOT NULL DEFAULT 10000,
    category VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES inventory(product_id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- ============================================================================
-- TABLES FOR SLOW QUERY TESTING
-- ============================================================================

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock_count INTEGER,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE query_stats (
    stat_id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    execution_time_ms NUMERIC(10,2) NOT NULL,
    rows_affected INTEGER,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_slow BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- TABLES FOR ABNORMAL DATA TESTING
-- ============================================================================

ALTER TABLE orders ADD CONSTRAINT check_positive_amount
    CHECK (total_amount >= 0) NOT VALID;

CREATE TABLE transaction_log (
    log_id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(50),
    amount DECIMAL(10,2),
    customer_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLES FOR BATCH PROCESSING
-- ============================================================================

CREATE TABLE batch_jobs (
    batch_id VARCHAR(50) PRIMARY KEY,
    job_type VARCHAR(100) NOT NULL,
    total_records INTEGER DEFAULT 0,
    processed_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE batch_errors (
    error_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) REFERENCES batch_jobs(batch_id),
    record_data JSONB,
    error_type VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE batch_staging (
    staging_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    record_data JSONB NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE,
    has_error BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_inventory_category ON inventory(category);

-- Intentionally missing indexes for slow query testing:
-- - products.category (will cause slow queries)
-- - customers.status (will cause slow queries)

CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX idx_batch_errors_batch ON batch_errors(batch_id);
CREATE INDEX idx_batch_staging_batch ON batch_staging(batch_id);
CREATE INDEX idx_batch_staging_processed ON batch_staging(is_processed);

-- ============================================================================
-- MONITORING VIEWS
-- ============================================================================

CREATE VIEW v_active_locks AS
SELECT
    l.pid,
    l.locktype,
    l.relation::regclass AS table_name,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.state,
    EXTRACT(EPOCH FROM (NOW() - a.query_start)) * 1000 AS wait_time_ms
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.granted = false;

CREATE VIEW v_database_stats AS
SELECT
    current_database() AS database_name,
    pg_database_size(current_database()) AS size_bytes,
    ROUND(pg_database_size(current_database()) / 1024.0 / 1024.0, 2) AS size_mb,
    ROUND(pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0, 4) AS size_gb;
