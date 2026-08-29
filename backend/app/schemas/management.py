from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class DashboardMetricResponse(BaseModel):
    id: UUID
    metric_name: str
    metric_category: str
    metric_value: float
    unit: Optional[str]
    timestamp: datetime
    period: Optional[str]

    class Config:
        from_attributes = True

class AnomalyBase(BaseModel):
    anomaly_type: str
    severity: str
    description: str

class AnomalyCreate(AnomalyBase):
    affected_entity: Optional[str] = None
    entity_id: Optional[UUID] = None

class AnomalyResponse(AnomalyBase):
    id: UUID
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class ForecastBase(BaseModel):
    forecast_type: str
    target_metric: str
    forecast_date: datetime
    forecast_value: float

class ForecastCreate(ForecastBase):
    confidence_level: Optional[float] = None
    model_used: Optional[str] = None

class ForecastResponse(ForecastBase):
    id: UUID
    confidence_level: Optional[float]
    actual_value: Optional[float]
    variance: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    report_name: str
    report_type: str
    period_start: datetime
    period_end: datetime

class ReportCreate(ReportBase):
    data: Dict[str, Any]
    file_path: Optional[str] = None

class ReportResponse(ReportBase):
    id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardSummaryResponse(BaseModel):
    warehouse_items_count: int
    pending_tasks: int
    active_shipments: int
    available_vehicles: int
    critical_anomalies: int
    pending_communications: int
    key_metrics: Dict[str, float]
    recent_anomalies: list
