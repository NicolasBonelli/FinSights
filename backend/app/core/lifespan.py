"""
Application lifespan events
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.core.config import get_settings
from backend.app.core.elasticsearch_client import get_elasticsearch_client, close_elasticsearch
from backend.app.core.rabbitmq import rabbitmq_client

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    """
    settings = get_settings()
    logger.info("🚀 Starting FinSights API...")
    
    # Startup
    try:
        # Initialize Elasticsearch
        es_client = await get_elasticsearch_client()
        if not await es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        logger.info("✅ Elasticsearch connection established")
        
        # Initialize RabbitMQ
        await rabbitmq_client.connect()
        logger.info("✅ RabbitMQ connection established")
        
        logger.info("🎉 FinSights API startup completed successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("🛑 Shutting down FinSights API...")
        
        # Close RabbitMQ connection
        await rabbitmq_client.close()
        
        # Close Elasticsearch connection
        await close_elasticsearch()
        
        logger.info("👋 FinSights API shutdown completed")
