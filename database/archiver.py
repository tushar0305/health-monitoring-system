from datetime import datetime, timedelta
from sqlalchemy import delete, and_
from sqlalchemy.orm import Session
import json
import logging

from .models import SystemMetric, ComponentHealth, Alert, DataRetentionLog
from .connection import db_manager
from config.config import settings

logger = logging.getLogger(__name__)