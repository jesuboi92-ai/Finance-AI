from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.warehouse import WarehouseTask, Inventory
from app.models.transport import Shipment
from app.models.customer import CustomerOrder, Communication
from app.models.management import DashboardMetric, Anomaly, Forecast, Report
from datetime import datetime, timedelta
from uuid import UUID
import logging
import json

logger = logging.getLogger(__name__)

class ManagementService:
    def get_dashboard_summary(self, db: Session) -> dict:
        """Get dashboard summary with key metrics"""
        # Count items
        warehouse_items = db.query(func.count(Inventory.id)).scalar() or 0
        pending_tasks = db.query(func.count(WarehouseTask.id)).filter(
            WarehouseTask.status == "pending"
        ).scalar() or 0
        active_shipments = db.query(func.count(Shipment.id)).filter(
            Shipment.status.in_(["in_transit", "pending"])
        ).scalar() or 0
        pending_comms = db.query(func.count(Communication.id)).filter(
            Communication.status == "draft"
        ).scalar() or 0
        critical_anomalies = db.query(func.count(Anomaly.id)).filter(
            Anomaly.severity == "critical",
            Anomaly.status == "open"
        ).scalar() or 0
        
        # Get recent metrics
        recent_metrics = db.query(DashboardMetric).order_by(
            DashboardMetric.timestamp.desc()
        ).limit(10).all()
        
        metrics_dict = {}
        for metric in recent_metrics:
            metrics_dict[metric.metric_name] = metric.metric_value
        
        # Get recent anomalies
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.status == "open"
        ).order_by(Anomaly.detected_at.desc()).limit(5).all()
        
        anomalies_list = [
            {
                "id": str(a.id),
                "type": a.anomaly_type,
                "severity": a.severity,
                "description": a.description
            }
            for a in recent_anomalies
        ]
        
        return {
            "warehouse_items_count": warehouse_items,
            "pending_tasks": pending_tasks,
            "active_shipments": active_shipments,
            "available_vehicles": active_shipments,  # Simplified
            "critical_anomalies": critical_anomalies,
            "pending_communications": pending_comms,
            "key_metrics": metrics_dict,
            "recent_anomalies": anomalies_list
        }
    
    def generate_forecasts(self, db: Session, forecast_type: str, target_metric: str, days_ahead: int) -> list:
        """Generate demand/load forecasts"""
        forecasts = []
        
        for day in range(1, days_ahead + 1):
            forecast_date = datetime.utcnow() + timedelta(days=day)
            
            # Simplified forecast logic
            if forecast_type == "demand":
                forecast_value = 100 + (day * 5)  # Linear increase
            elif forecast_type == "load":
                forecast_value = 50 + (day * 3)   # Linear increase
            else:
                forecast_value = 75
            
            forecast = Forecast(
                forecast_type=forecast_type,
                target_metric=target_metric,
                forecast_date=forecast_date,
                forecast_value=forecast_value,
                confidence_level=0.85,
                model_used="time_series_simple"
            )
            db.add(forecast)
            forecasts.append(forecast)
        
        db.commit()
        logger.info(f"Generated {len(forecasts)} forecasts for {forecast_type}")
        return forecasts
    
    def generate_report(self, db: Session, report_type: str, include_metrics: list, generated_by: UUID) -> dict:
        """Generate comprehensive report"""
        now = datetime.utcnow()
        
        if report_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0)
            period_end = period_start + timedelta(days=1)
        elif report_type == "weekly":
            period_start = now - timedelta(days=7)
            period_end = now
        elif report_type == "monthly":
            period_start = now - timedelta(days=30)
            period_end = now
        else:
            period_start = now - timedelta(days=1)
            period_end = now
        
        # Collect data
        report_data = {
            "period": f"{period_start} to {period_end}",
            "generated_at": now.isoformat(),
            "summary": self.get_dashboard_summary(db),
            "warehouse": {
                "total_items": db.query(func.count(Inventory.id)).scalar() or 0,
                "tasks_completed": db.query(func.count(WarehouseTask.id)).filter(
                    WarehouseTask.status == "completed",
                    WarehouseTask.completed_at >= period_start
                ).scalar() or 0
            },
            "transport": {
                "shipments_delivered": db.query(func.count(Shipment.id)).filter(
                    Shipment.status == "delivered",
                    Shipment.actual_delivery >= period_start
                ).scalar() or 0,
                "delayed_shipments": db.query(func.count(Shipment.id)).filter(
                    Shipment.delay_risk == True,
                    Shipment.created_at >= period_start
                ).scalar() or 0
            },
            "customer": {
                "total_orders": db.query(func.count(CustomerOrder.id)).filter(
                    CustomerOrder.created_at >= period_start
                ).scalar() or 0,
                "communications_sent": db.query(func.count(Communication.id)).filter(
                    Communication.status == "sent",
                    Communication.sent_at >= period_start
                ).scalar() or 0
            }
        }
        
        # Create report record
        report = Report(
            report_name=f"{report_type.capitalize()} Report - {now.strftime('%Y-%m-%d')}",
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            data=report_data,
            generated_by=generated_by,
            status="completed"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Report generated: {report.id}")
        return report_data
    
    def generate_insights(self, db: Session) -> dict:
        """Generate AI-driven business insights"""
        summary = self.get_dashboard_summary(db)
        
        insights = {
            "generated_at": datetime.utcnow().isoformat(),
            "insights": []
        }
        
        # Analyze metrics and generate insights
        if summary["critical_anomalies"] > 0:
            insights["insights"].append({
                "title": "Critical Issues Detected",
                "description": f"There are {summary['critical_anomalies']} critical anomalies that need immediate attention",
                "priority": "high",
                "action": "Review and resolve anomalies immediately"
            })
        
        if summary["pending_tasks"] > 50:
            insights["insights"].append({
                "title": "High Task Backlog",
                "description": f"There are {summary['pending_tasks']} pending warehouse tasks",
                "priority": "high",
                "action": "Consider allocating more resources to warehouse operations"
            })
        
        if summary["pending_communications"] > 10:
            insights["insights"].append({
                "title": "Communications Pending Review",
                "description": f"There are {summary['pending_communications']} communications awaiting approval",
                "priority": "medium",
                "action": "Review and send pending customer communications"
            })
        
        return insights
