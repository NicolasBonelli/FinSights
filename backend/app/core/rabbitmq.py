"""
RabbitMQ connection and messaging utilities
"""
import logging
import json
from typing import Optional, Dict, Any, Callable
import aio_pika
from aio_pika import Connection, Channel, Queue, Exchange
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """RabbitMQ connection manager"""
    
    def __init__(self):
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None
        self.settings = get_settings()
    
    async def connect(self):
        """Establish RabbitMQ connection"""
        try:
            self.connection = await aio_pika.connect_robust(
                f"amqp://{self.settings.rabbitmq_username}:{self.settings.rabbitmq_password}@{self.settings.rabbitmq_url.replace('amqp://', '')}"
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            logger.info("RabbitMQ connection established")
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise
    
    async def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            logger.info("RabbitMQ connection closed")
            
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    async def declare_queue(self, queue_name: str, durable: bool = True) -> Queue:
        """Declare a queue"""
        if not self.channel:
            raise RuntimeError("RabbitMQ channel not initialized")
        
        queue = await self.channel.declare_queue(queue_name, durable=durable)
        return queue
    
    async def declare_exchange(self, exchange_name: str, exchange_type: str = "direct") -> Exchange:
        """Declare an exchange"""
        if not self.channel:
            raise RuntimeError("RabbitMQ channel not initialized")
        
        exchange = await self.channel.declare_exchange(exchange_name, exchange_type)
        return exchange
    
    async def publish_message(
        self, 
        queue_name: str, 
        message: Dict[str, Any], 
        routing_key: Optional[str] = None
    ):
        """Publish a message to a queue"""
        try:
            if not self.channel:
                await self.connect()
            
            queue = await self.declare_queue(queue_name)
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    json.dumps(message).encode(),
                    content_type="application/json"
                ),
                routing_key=routing_key or queue_name
            )
            
            logger.info(f"Message published to queue: {queue_name}")
            
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            raise
    
    async def consume_messages(
        self, 
        queue_name: str, 
        callback: Callable,
        auto_ack: bool = False
    ):
        """Consume messages from a queue"""
        try:
            if not self.channel:
                await self.connect()
            
            queue = await self.declare_queue(queue_name)
            
            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process(ignore_processed=True):
                    try:
                        data = json.loads(message.body.decode())
                        await callback(data)
                        if not auto_ack:
                            message.ack()
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        if not auto_ack:
                            message.nack()
            
            await queue.consume(message_handler, no_ack=auto_ack)
            logger.info(f"Started consuming from queue: {queue_name}")
            
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            raise


class MessagePublisher:
    """Service for publishing messages to different queues"""
    
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
    
    async def send_ingestion_task(self, document_id: str, company_id: str, blob_url: str):
        """Send document ingestion task"""
        message = {
            "task_type": "document_ingestion",
            "document_id": document_id,
            "company_id": company_id,
            "blob_url": blob_url,
            "timestamp": str(json.dumps(None, default=str))
        }
        
        await self.connection.publish_message("ingestion_queue", message)
    
    async def send_analysis_task(
        self, 
        task_id: str, 
        company_id: str, 
        question: str, 
        agent_types: list
    ):
        """Send analysis task to agents"""
        message = {
            "task_type": "financial_analysis",
            "task_id": task_id,
            "company_id": company_id,
            "question": question,
            "agent_types": agent_types,
            "timestamp": str(json.dumps(None, default=str))
        }
        
        await self.connection.publish_message("analysis_queue", message)
    
    async def send_rag_query(
        self, 
        query_id: str, 
        company_id: str, 
        query: str, 
        rag_type: str
    ):
        """Send RAG query task"""
        message = {
            "task_type": "rag_query",
            "query_id": query_id,
            "company_id": company_id,
            "query": query,
            "rag_type": rag_type,  # "hybrid" or "langextract"
            "timestamp": str(json.dumps(None, default=str))
        }
        
        await self.connection.publish_message("rag_queue", message)


# Global connection instance
rabbitmq_connection = RabbitMQConnection()
message_publisher = MessagePublisher(rabbitmq_connection)


async def close_rabbitmq():
    """Close RabbitMQ connection"""
    await rabbitmq_connection.close()
