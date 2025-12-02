-- Init script for PostgreSQL database
-- This file is automatically executed when PostgreSQL container starts

-- Create database if not exists (optional, since POSTGRES_DB env var already creates it)
-- SELECT 'CREATE DATABASE dbagent' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dbagent')\gexec

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dbagent TO dbagent;

-- Create schema for monitoring data (optional)
-- CREATE SCHEMA IF NOT EXISTS monitoring;
-- GRANT ALL ON SCHEMA monitoring TO dbagent;

-- Note: Tables will be created automatically by SQLAlchemy when the app starts
-- or when you run seed_data.py script
