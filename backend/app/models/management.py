from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
from app.database import Base

class DashboardMetric(Base):
    __tablename__ = "dashboard_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False)
    metric_category = Column(String(50), nullable=False)  # warehouse, transport, customer, financial
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)  # %, kg, items, hours, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    period = Column(String(20), nullable=True)  # daily, weekly, monthly
    metadata = Column(JSON, nullable=True)

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anomaly_type = Column(String(100), nullable=False)  # stock_discrepancy, delay_risk, unusual_pattern
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    description = Column(Text, nullable=False)
    affected_entity = Column(String(100), nullable=True)  # shipment_id, inventory_id, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(50), default="open")  # open, acknowledged, resolved
    resolution_notes = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_type = Column(String(50), nullable=False)  # demand, load, delay_risk, stock
    target_metric = Column(String(100), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    forecast_value = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=True)  # 0-1
    actual_value = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)  # time_series, ml_model, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, custom
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)  # Report data
    file_path = Column(String(255), nullable=True)  # S3/Azure storage path
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="generating")  # generating, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
