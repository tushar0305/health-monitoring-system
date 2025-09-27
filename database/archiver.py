from datetime import date, datetime, timedelta
from sqlalchemy import delete, and_, select
from sqlalchemy.orm import Session
import json
import logging

from .models import SystemMetric, ComponentHealth, Alert, DataRetentionLog
from .connection import db_manager
from config.config import settings

logger = logging.getLogger(__name__)

class DataArchiver:
    def __init__(self):
        self.batch_size = settings.archive_batch_size

    async def archive_old_metrics(self, days_to_keep: int = None):
        """Archive old system metrics"""
        if days_to_keep is None:
            days_to_keep = settings.metrics_retention_days
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        start_time = datetime.now()
        
        async with db_manager.get_session() as session:
            try:
                # Count records to be archived
                count_query = select(SystemMetric).filter(
                    SystemMetric.timestamp < cutoff_date
                )
                records_to_archive = await session.execute(count_query)
                total_records = len(records_to_archive.scalars().all())
                
                if total_records == 0:
                    logger.info("No old metrics to archive")
                    return
                
                # Archive in batches
                archived_count = 0
                while True:
                    # Get batch of old records
                    batch_query = select(SystemMetric).filter(
                        SystemMetric.timestamp < cutoff_date
                    ).limit(self.batch_size)
                    
                    batch_records = await session.execute(batch_query)
                    batch_data = batch_records.scalars().all()
                    
                    if not batch_data:
                        break
                    
                    # Archive batch (you could save to file, S3, etc.)
                    await self._save_archive_batch("system_metrics", batch_data)
                    
                    # Delete batch from main table
                    record_ids = [record.id for record in batch_data]
                    await session.execute(
                        delete(SystemMetric).where(SystemMetric.id.in_(record_ids))
                    )
                    
                    archived_count += len(batch_data)
                    logger.info(f"Archived {archived_count}/{total_records} metrics")
                
                # Log the operation
                execution_time = (datetime.now() - start_time).total_seconds()
                await self._log_retention_operation(
                    session, "archive", "system_metrics", 
                    total_records, archived_count, 0, execution_time
                )
                
                logger.info(f"Archived {archived_count} old metrics in {execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to archive metrics: {e}")
                raise
    
    async def cleanup_old_component_health(self, days_to_keep: int = None):
        """Clean up old component health data"""
        if days_to_keep is None:
            days_to_keep = settings.component_health_retention_days
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        start_time = datetime.now()
        
        async with db_manager.get_session() as session:
            try:
                # Delete old records
                delete_query = delete(ComponentHealth).where(
                    ComponentHealth.timestamp < cutoff_date
                )
                result = await session.execute(delete_query)
                deleted_count = result.rowcount
                
                # Log the operation
                execution_time = (datetime.now() - start_time).total_seconds()
                await self._log_retention_operation(
                    session, "cleanup", "component_health",
                    0, 0, deleted_count, execution_time
                )
                
                logger.info(f"Cleaned up {deleted_count} old component health records")
                
            except Exception as e:
                logger.error(f"Failed to cleanup component health: {e}")
                raise
    
    async def cleanup_old_alerts(self, days_to_keep: int = None):
        """Clean up old resolved alerts"""
        if days_to_keep is None:
            days_to_keep = settings.alert_retention_days
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        start_time = datetime.now()
        
        async with db_manager.get_session() as session:
            try:
                # Delete old resolved alerts
                delete_query = delete(Alert).where(
                    and_(
                        Alert.resolved_at.isnot(None),
                        Alert.resolved_at < cutoff_date
                    )
                )
                result = await session.execute(delete_query)
                deleted_count = result.rowcount
                
                # Log the operation
                execution_time = (datetime.now() - start_time).total_seconds()
                await self._log_retention_operation(
                    session, "cleanup", "alerts",
                    0, 0, deleted_count, execution_time
                )
                
                logger.info(f"Cleaned up {deleted_count} old alerts")
                
            except Exception as e:
                logger.error(f"Failed to cleanup alerts: {e}")
                raise
    
    async def _save_archive_batch(self, table_name: str, batch_data):
        """Save archived data to file or external storage"""
        # For now, we'll just log it. In production, save to file/S3/etc.
        archive_data = {
            "table": table_name,
            "archived_at": datetime.now().isoformat(),
            "record_count": len(batch_data),
            "sample_record": {
                "id": batch_data[0].id,
                "timestamp": batch_data[0].timestamp.isoformat() if hasattr(batch_data[0], 'timestamp') else None
            }
        }
        
        logger.info(f"Archived batch: {json.dumps(archive_data)}")
        # TODO: In production, save to S3, file system, or data warehouse
    
    async def _log_retention_operation(self, session, operation_type: str, table_name: str, 
                                     records_processed: int, records_archived: int, 
                                     records_deleted: int, execution_time: float):
        """Log retention operation"""
        log_entry = DataRetentionLog(
            operation_type=operation_type,
            table_name=table_name,
            records_processed=records_processed,
            records_archived=records_archived,
            records_deleted=records_deleted,
            execution_time_seconds=execution_time,
            details=json.dumps({
                "retention_policy": f"{table_name}_retention_days",
                "batch_size": self.batch_size
            })
        )
        session.add(log_entry)

# Global archiver instance
archiver = DataArchiver()