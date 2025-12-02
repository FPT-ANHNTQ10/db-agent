#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Location: ./mcp-servers/python/db-agent-mcp/src/db_agent/db_models.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Database Agent Team

Database models and connection management for PostgreSQL.
"""

import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dbagent:dbagent123@localhost:5432/dbagent")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SlowQuery(Base):
    """Slow query log table."""
    __tablename__ = "slow_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="SLOW")
    table_name = Column(String(255))
    operation_type = Column(String(50))
    recommendations = Column(Text)


class DeadlockSession(Base):
    """Deadlock session information."""
    __tablename__ = "deadlock_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), nullable=False)
    transaction_id = Column(String(50), nullable=False)
    query = Column(Text, nullable=False)
    locked_resource = Column(String(255))
    wait_time_ms = Column(Integer)
    blocking_session = Column(String(50))
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)


class DeadlockLog(Base):
    """Historical deadlock logs."""
    __tablename__ = "deadlock_logs"

    id = Column(Integer, primary_key=True, index=True)
    deadlock_id = Column(String(50), unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    affected_queries = Column(Text)  # JSON array as text
    victim_session = Column(String(50))
    resolution = Column(String(100))


class DatabaseFile(Base):
    """Database file size tracking."""
    __tablename__ = "database_files"

    id = Column(Integer, primary_key=True, index=True)
    database_name = Column(String(255), nullable=False)
    size_mb = Column(Float, nullable=False)
    max_size_mb = Column(Float, default=10240.0)  # 10GB default
    growth_rate_mb_per_day = Column(Float)
    estimated_full_days = Column(Integer)
    last_checked = Column(DateTime, default=datetime.utcnow)


class AbnormalData(Base):
    """Abnormal data detection records."""
    __tablename__ = "abnormal_data"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(255), nullable=False)
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(20))  # HIGH, MEDIUM, LOW
    detected_at = Column(DateTime, default=datetime.utcnow)
    affected_row_ids = Column(Text)  # JSON array as text
    description = Column(Text)
    resolved = Column(Boolean, default=False)


class BatchProcessing(Base):
    """Batch processing logs."""
    __tablename__ = "batch_processing"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(50), unique=True, nullable=False)
    records_processed = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    failure_reasons = Column(Text)  # JSON object as text
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="COMPLETED")


# Orders table (example for testing)
class Order(Base):
    """Sample orders table for testing."""
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


# Products table (example for testing)
class Product(Base):
    """Sample products table for testing."""
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    stock = Column(Integer, default=0)
    max_threshold = Column(Integer, default=10000)
    last_checked = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
