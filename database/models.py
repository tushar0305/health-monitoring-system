from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class SystemMetric(Base):
    """Store system metrics with retention"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    disk_percent = Column(Float, nullable=False)
    process_count = Column(Integer, nullable=False)
    load_average_1m = Column(Float, nullable=True)
    load_average_5m = Column(Float, nullable=True)
    load_average_15m = Column(Float, nullable=True)
    bytes_sent = Column(Integer, nullable=True)
    bytes_recv = Column(Integer, nullable=True)
    packets_sent = Column(Integer, nullable=True)
    packets_recv = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

class ComponentHealth(Base):
    """Store component health data"""
    __tablename__ = "component_health"
    
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String(255), nullable=False, index=True)
    component_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    response_time = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata = Column(Text, nullable=True)  # JSON string
    metrics = Column(Text, nullable=True)   # JSON string
    created_at = Column(DateTime, default=func.now())

class Alert(Base):
    """Store alert data"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    component_id = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=True)
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string

class DataRetentionLog(Base):
    """Track data retention operations"""
    __tablename__ = "data_retention_log"
    
    id = Column(Integer, primary_key=True)
    operation_type = Column(String(100), nullable=False)  # 'archive', 'cleanup', 'retention'
    table_name = Column(String(100), nullable=False)
    records_processed = Column(Integer, nullable=False)
    records_archived = Column(Integer, nullable=False)
    records_deleted = Column(Integer, nullable=False)
    execution_time_seconds = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    details = Column(Text, nullable=True)  # JSON string with details