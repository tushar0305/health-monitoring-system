import asyncio
import logging
from datetime import datetime, timedelta

from database.archiver import archiver
from config.config import settings

logger = logging.getLogger(__name__)

class RetentionService:
    def __init__(self):
        self.running = False
        self.cleanup_task = None
    
    async def start(self):
        """Start the retention service"""
        self.running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Retention service started")
    
    async def stop(self):
        """Stop the retention service"""
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Retention service stopped")
    
    async def _cleanup_loop(self):
        """Main cleanup loop"""
        while self.running:
            try:
                await self._run_cleanup_cycle()
                
                # Wait for next cleanup cycle
                await asyncio.sleep(settings.cleanup_interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def _run_cleanup_cycle(self):
        """Run one cleanup cycle"""
        logger.info("Starting data retention cleanup cycle")
        start_time = datetime.now()
        
        try:
            # Archive old system metrics
            await archiver.archive_old_metrics()
            
            # Clean up old component health data
            await archiver.cleanup_old_component_health()
            
            # Clean up old resolved alerts
            await archiver.cleanup_old_alerts()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Data retention cleanup completed in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Data retention cleanup failed: {e}")
            raise
    
    async def run_manual_cleanup(self):
        """Run cleanup manually (for testing)"""
        logger.info("Running manual data cleanup")
        await self._run_cleanup_cycle()

# Global retention service instance
retention_service = RetentionService()
