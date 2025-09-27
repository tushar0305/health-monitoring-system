from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import session, sessionmaker
from contextlib import asynccontextmanager
import logging

from ..database.models import Base
from config.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def initialize(self):
        """Initialize database connection"""
        try:
            # Create engine
            self.engine = create_async_engine(
                settings.database_url.replace("sqlite://", "sqlite+aiosqlite://"),
                echo=settings.debug,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow
            )

            # Session Factory
            self.session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Create Tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed successfully")

    @asynccontextmanager
    async def get_session(self):
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

#Global database manager instance
db_manager = DatabaseManager()