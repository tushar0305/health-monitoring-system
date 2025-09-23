import asyncio
import aiohttp
import json
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class HealtStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"

@dataclass
class ComponentHealth:
    component_id: str
    name: str
    status: HealtStatus
    last_check: datetime
    response_time: float
    metadata: Dict[str, Any]
    metrics: Dict[str, float]

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]

class HealthCollector:
    def __init__(self, config):
        self.config = config
        self.registered_components = Dict[str, Dict] = {}
        self.component_health = Dict[str, ComponentHealth] = {}
        self.system_metrics = List[SystemMetrics] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False

    
    async def start(self):
        """Start the health collection service"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        self.running = True

        # Start collection tasks
        await asyncio.gather(
            self._collect_system_metric(),
            self._collect_component_health(),
            return_exception =True
        )

    async def stop(self):
        """Stop the health collection service"""
        self.running = False
        if self.session:
            await self.session.Close()