"""
Application lifespan events
"""
import logging
from app.core.config import get_settings
# from app.core.database import get_redis_client, close_redis
# from app.core.elasticsearch_client import get_elasticsearch_client, close_elasticsearch
# from app.core.rabbitmq import rabbitmq_connection, close_rabbitmq
# from app.agents.manager import agent_manager

logger = logging.getLogger(__name__)


async def startup_event():
    """Handle application startup"""
    settings = get_settings()
    logger.info("Starting FinSights API...")
    
    try:
        # # Initialize Redis connection
        # redis_client = await get_redis_client()
        # await redis_client.ping()
        # logger.info("Redis connection established")
        
        # # Initialize Elasticsearch connection
        # elasticsearch_client = await get_elasticsearch_client()
        # await elasticsearch_client.ping()
        # logger.info("Elasticsearch connection established")
        
        # # Initialize RabbitMQ connection
        # await rabbitmq_connection.connect()
        # logger.info("RabbitMQ connection established")
        
        # Initialize agent manager
        # await agent_manager.initialize()
        # logger.info("Agent manager initialized")
        
        logger.info("FinSights API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


async def shutdown_event():
    """Handle application shutdown"""
    logger.info("Shutting down FinSights API...")
    
    try:
        # Close agent manager
        # await agent_manager.shutdown()
        # logger.info("Agent manager shutdown completed")
        
        # # Close RabbitMQ connection
        # await close_rabbitmq()
        # logger.info("RabbitMQ connection closed")
        
        # # Close Elasticsearch connection
        # await close_elasticsearch()
        # logger.info("Elasticsearch connection closed")
        
        # # Close Redis connection
        # await close_redis()
        # logger.info("Redis connection closed")
        
        logger.info("FinSights API shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
