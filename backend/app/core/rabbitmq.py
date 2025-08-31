"""
Módulo para la gestión de la conexión y publicación de mensajes en RabbitMQ.
"""

import aio_pika
import json
import logging
from contextlib import asynccontextmanager
from backend.app.core.config import get_settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQClient:
    """Cliente para interactuar con RabbitMQ."""
    
    def __init__(self, settings):
        self.settings = settings
        self.connection = None
        self.channel = None

    async def connect(self):
        """Establece la conexión con RabbitMQ."""
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    f"amqp://{self.settings.rabbitmq_username}:{self.settings.rabbitmq_password}@{self.settings.rabbitmq_url.replace('amqp://', '')}"
                )
                self.channel = await self.connection.channel()
                logger.info("✅ Conexión con RabbitMQ establecida.")
            except Exception as e:
                logger.error(f"❌ No se pudo conectar a RabbitMQ: {e}")
                raise

    async def close(self):
        """Cierra la conexión con RabbitMQ."""
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("🛑 Conexión con RabbitMQ cerrada.")

    async def publish_message(self, queue_name: str, message_body: dict):
        """Publica un mensaje en una cola específica."""
        if not self.channel:
            await self.connect()
            
        try:
            await self.channel.declare_queue(queue_name, durable=True)
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_body).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=queue_name
            )
            logger.info(f"📤 Mensaje enviado a la cola '{queue_name}': {message_body}")
        except Exception as e:
            logger.error(f"❌ Error publicando mensaje en '{queue_name}': {e}")
            raise

# Instancia global del cliente RabbitMQ
settings = get_settings()
rabbitmq_client = RabbitMQClient(settings)

@asynccontextmanager
async def get_rabbitmq_client():
    """Proporciona una instancia del cliente RabbitMQ y gestiona su ciclo de vida."""
    try:
        await rabbitmq_client.connect()
        yield rabbitmq_client
    finally:
        await rabbitmq_client.close()