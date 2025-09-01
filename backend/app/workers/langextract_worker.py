"""
LangExtract Worker - Extracción de entidades y relaciones financieras
Cola: langextract_queue
"""

import asyncio
import json
import logging
import uuid
import sys
import os
from io import BytesIO
import textwrap
import langextract as lx

# Agregar el path del backend para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import aio_pika
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream

# Importar servicios del backend
from backend.app.core.config import get_settings
from backend.app.core.azure_storage import azure_blob_service
from backend.app.core.elasticsearch_client import get_elasticsearch_client

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class LangExtractWorker:
    """Worker para extracción de entidades y relaciones con LangExtract"""

    # Explicit configuration is recommended
    config = lx.factory.ModelConfig(
        model_id="gpt-4o",  # your Azure deployment name
        provider="AzureOpenAILanguageModel",
        provider_kwargs={
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        },
    )

    def __init__(self):
        self.settings = get_settings()
        self.connection = None
        self.channel = None
        self.doc_converter = DocumentConverter()

        # Prompt de extracción financiera
        self.prompt = textwrap.dedent("""\
            Extract financial entities, values, and relationships.
            Entities: Company, Metric, Value, TimePeriod, ComparisonTarget, Event, Risk, Trend
            Use exact text for extractions. Do not paraphrase.
            Provide attributes such as currency, percentage, period, or context.
        """)

        # Ejemplo guiado para LangExtract
        self.examples = [
            lx.data.ExampleData(
                text="In Q2 2024, Company ABC reported revenue of $10 million, a 20% increase compared to Q1 2024.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="Company",
                        extraction_text="Company ABC",
                        attributes={"type": "organization"}
                    ),
                    lx.data.Extraction(
                        extraction_class="Metric",
                        extraction_text="revenue",
                        attributes={"unit": "USD"}
                    ),
                    lx.data.Extraction(
                        extraction_class="Value",
                        extraction_text="$10 million",
                        attributes={"currency": "USD", "amount": "10000000"}
                    ),
                    lx.data.Extraction(
                        extraction_class="TimePeriod",
                        extraction_text="Q2 2024",
                        attributes={"type": "quarter"}
                    ),
                    lx.data.Extraction(
                        extraction_class="Trend",
                        extraction_text="20% increase",
                        attributes={"direction": "up", "percentage": "20%"}
                    ),
                    lx.data.Extraction(
                        extraction_class="ComparisonTarget",
                        extraction_text="Q1 2024",
                        attributes={"type": "quarter"}
                    ),
                ]
            )
        ]

    async def connect_rabbitmq(self):
        """Conectar a RabbitMQ"""
        self.connection = await aio_pika.connect_robust(
            f"amqp://{self.settings.rabbitmq_username}:{self.settings.rabbitmq_password}@{self.settings.rabbitmq_url.replace('amqp://', '')}"
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

    async def extract_entities_and_relations(self, text: str):
        """Usar LangExtract para extraer entidades y relaciones financieras con reintentos."""
        max_retries = 5
        base_delay = 10  # segundos

        for attempt in range(max_retries):
            try:
                # lx.extract es síncrono, lo ejecutamos en un hilo para no bloquear asyncio
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=self.prompt,
                    examples=self.examples,
                    config=self.config,                 # reuse the explicit configuration
                    # Azure OpenAI generation params
                    temperature=0.0,
                )

                relations = []
                for ext in result.extractions:
                    relations.append({
                        "id": str(uuid.uuid4()),
                        "doc_id": None,   # se completa en process_document
                        "entity_class": ext.extraction_class,
                        "entity_text": ext.extraction_text,
                        "attributes": ext.attributes,
                        "evidence_text": getattr(ext, "source_text", None),
                        "confidence": getattr(ext, "confidence", 0.9)
                    })
                return relations
            except Exception as e:
                if "429" in str(e) and "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit excedido. Reintentando en {delay} segundos... (Intento {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                    else:
                        logger.error("Rate limit excedido. Se alcanzó el máximo de reintentos.")
                        raise e
                else:
                    raise e

    async def download_and_extract_text(self, file_id: str) -> str:
        """Descargar archivo de Azure y extraer texto con Docling"""
        try:
            # Descargar archivo desde Azure Blob Storage
            blob_url = azure_blob_service.build_blob_url(file_id)
            content = await azure_blob_service.download_file(blob_url)

            if not content:
                raise Exception(f"No se pudo descargar el archivo: {file_id}")

            # Crear BytesIO stream para Docling
            file_stream = BytesIO(content)

            # Crear DocumentStream y convertir
            source = DocumentStream(name=f"{file_id}.pdf", stream=file_stream)
            conversion_result = self.doc_converter.convert(source)

            if conversion_result and conversion_result.document:
                text_content = conversion_result.document.export_to_text()
                logger.info(f"✅ Texto extraído con Docling: {len(text_content)} caracteres")
                return text_content
            else:
                raise Exception("No se pudo extraer texto del documento")

        except Exception as e:
            logger.error(f"❌ Error en descarga/extracción: {e}")
            raise

    async def process_document(self, file_id: str, doc_id: str, company_id: str):
        """Procesar documento para extraer entidades y relaciones"""
        try:
            # 1. Descargar archivo y extraer texto
            text_content = await self.download_and_extract_text(file_id)

            # 2. Extraer entidades y relaciones
            relations = await self.extract_entities_and_relations(text_content)

            # 3. Guardar en Elasticsearch
            es_client = await get_elasticsearch_client()
            for relation in relations:
                relation["doc_id"] = doc_id
                relation["company_id"] = company_id

                await es_client.index(
                    index=f"relations_{company_id}",
                    body=relation,
                    id=relation["id"]
                )

            logger.info(f"✅ Entidades y relaciones extraídas: {doc_id} - {len(relations)} registros")

        except Exception as e:
            logger.error(f"❌ Error extrayendo entidades del documento {doc_id}: {e}")
            raise

    async def process_message(self, message: aio_pika.IncomingMessage):
        """Procesar mensaje de la cola"""
        async with message.process(requeue=False):
            try:
                data = json.loads(message.body.decode())
                await self.process_document(
                    file_id=data["file_id"],
                    doc_id=data["doc_id"],
                    company_id=data["company_id"]
                )
                await message.ack()
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                await message.nack()

    async def start_consuming(self):
        """Iniciar consumo de mensajes"""
        await self.connect_rabbitmq()
        queue = await self.channel.declare_queue("langextract_queue", durable=True)
        await queue.consume(self.process_message)

        logger.info("🔄 LangExtract Worker iniciado. Escuchando cola 'langextract_queue'...")

        try:
            await asyncio.Future()  # Ejecutar indefinidamente
        except KeyboardInterrupt:
            logger.info("🛑 Worker detenido")
        finally:
            if self.connection:
                await self.connection.close()


if __name__ == "__main__":
    worker = LangExtractWorker()
    asyncio.run(worker.start_consuming())
