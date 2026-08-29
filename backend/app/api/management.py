from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from uuid import UUID
from app.database import get_db
from app.models.management import DashboardMetric, Anomaly, Forecast, Report
from app.schemas.management import (
    DashboardMetricResponse, AnomalyResponse, ForecastResponse, 
    ReportResponse, DashboardSummaryResponse
)
from app.services.management_service import ManagementService
from app.utils.security import get_current_user

router = APIRouter()
management_service = ManagementService()

@router.get("/dashboard", response_model=DashboardSummaryResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard summary with key metrics"""
    summary = management_service.get_dashboard_summary(db)
    return summary

@router.get("/metrics", response_model=List[DashboardMetricResponse])
async def get_metrics(
    category: str = Query(None),
    period: str = Query("daily"),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard metrics"""
    query = db.query(DashboardMetric)
    if category:
        query = query.filter(DashboardMetric.metric_category == category)
    if period:
        query = query.filter(DashboardMetric.period == period)
    
    metrics = query.order_by(DashboardMetric.timestamp.desc()).offset(skip).limit(limit).all()
    return metrics

@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    severity: str = Query(None),
    status: str = Query("open"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detected anomalies"""
    query = db.query(Anomaly)
    if severity:
        query = query.filter(Anomaly.severity == severity)
    if status:
        query = query.filter(Anomaly.status == status)
    
    anomalies = query.order_by(Anomaly.detected_at.desc()).all()
    return anomalies

@router.put("/anomalies/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: UUID,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resolve an anomaly"""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    anomaly.status = "resolved"
    anomaly.resolution_notes = resolution_notes
    anomaly.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(anomaly)
    return anomaly

@router.get("/forecasts", response_model=List[ForecastResponse])
async def get_forecasts(
    forecast_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get load forecasts and predictions"""
    query = db.query(Forecast)
    if forecast_type:
        query = query.filter(Forecast.forecast_type == forecast_type)
    
    forecasts = query.order_by(Forecast.forecast_date.desc()).all()
    return forecasts

@router.post("/forecasts/generate")
async def generate_forecast(
    forecast_type: str,
    target_metric: str,
    days_ahead: int = 7,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate demand/load forecast"""
    forecasts = management_service.generate_forecasts(db, forecast_type, target_metric, days_ahead)
    return {"forecasts": forecasts}

@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    report_type: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get generated reports"""
    query = db.query(Report)
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports

@router.post("/reports/generate")
async def generate_report(
    report_type: str,  # daily, weekly, monthly
    include_metrics: List[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate comprehensive report"""
    report = management_service.generate_report(
        db, report_type, include_metrics, current_user.id
    )
    return report

@router.get("/insights")
async def get_insights(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-generated business insights"""
    insights = management_service.generate_insights(db)
    return insights
