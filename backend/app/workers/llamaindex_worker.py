"""
LlamaIndex Worker - Procesamiento de chunks y embeddings para RAG
Cola: llamaindex_queue
"""

import asyncio
import json
import logging
import uuid
from typing import List, Dict, Any
import sys
import os
from io import BytesIO

# Agregar el path del backend para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import aio_pika
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream

# Importar servicios del backend
from app.core.config import get_settings
from app.core.azure_storage import azure_blob_service
from app.core.elasticsearch_client import get_elasticsearch_client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LlamaIndexWorker:
    """Worker para procesamiento de documentos con LlamaIndex"""
    
    def __init__(self):
        self.settings = get_settings()
        self.connection = None
        self.channel = None
        self.embed_model = HuggingFaceEmbedding(model_name="intfloat/e5-base-v2")
        self.doc_converter = DocumentConverter()
        
    async def connect_rabbitmq(self):
        """Conectar a RabbitMQ"""
        self.connection = await aio_pika.connect_robust(
            f"amqp://{self.settings.rabbitmq_username}:{self.settings.rabbitmq_password}@{self.settings.rabbitmq_url.replace('amqp://', '')}"
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        
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
            file_stream.name = f"{file_id}.pdf"  # Asignar nombre para que Docling reconozca el tipo
            
            # Extraer texto usando Docling
            doc_stream = DocumentStream.from_file(file_stream)
            extracted_docs = self.doc_converter.convert(doc_stream)
            
            # Obtener texto extraído
            if extracted_docs and len(extracted_docs) > 0:
                text_content = extracted_docs[0].text
                logger.info(f"✅ Texto extraído con Docling: {len(text_content)} caracteres")
                return text_content
            else:
                raise Exception("No se pudo extraer texto del documento")
                
        except Exception as e:
            logger.error(f"❌ Error en descarga/extracción: {e}")
            raise
    
    async def process_document(self, file_id: str, doc_id: str, company_id: str):
        """Procesar documento completo"""
        try:
            # 1. Descargar archivo y extraer texto con Docling
            text_content = await self.download_and_extract_text(file_id)
            doc = Document(text=text_content, doc_id=doc_id)
            
            # 2. Crear chunks pequeños y grandes
            small_chunker = SentenceSplitter(chunk_size=300, chunk_overlap=20)
            parent_chunker = SentenceSplitter(chunk_size=1500, chunk_overlap=50)
            
            small_nodes = small_chunker.get_nodes_from_documents([doc])
            parent_nodes = parent_chunker.get_nodes_from_documents([doc])
            
            # 3. Generar embeddings solo para chunks pequeños
            small_texts = [node.text for node in small_nodes]
            embeddings = self.embed_model.get_text_embedding_batch(small_texts)
            
            # 4. Preparar datos para Elasticsearch
            es_client = await get_elasticsearch_client()
            
            # Indexar chunks pequeños con embeddings
            for i, (node, embedding) in enumerate(zip(small_nodes, embeddings)):
                chunk_data = {
                    "id": str(uuid.uuid4()),
                    "doc_id": doc_id,
                    "chunk_text": node.text,
                    "parent_id": f"parent_{i // 4}",  # Agrupar 4 small chunks por parent
                    "embedding": embedding,
                    "company_id": company_id
                }
                
                await es_client.index(
                    index=f"chunks_small_{company_id}",
                    body=chunk_data,
                    id=chunk_data["id"]
                )
            
            # Indexar chunks padres
            for i, node in enumerate(parent_nodes):
                parent_data = {
                    "id": f"parent_{i}",
                    "doc_id": doc_id,
                    "parent_text": node.text,
                    "company_id": company_id
                }
                
                await es_client.index(
                    index=f"chunks_parent_{company_id}",
                    body=parent_data,
                    id=parent_data["id"]
                )
            
            logger.info(f"✅ Documento procesado: {doc_id} - {len(small_nodes)} chunks pequeños, {len(parent_nodes)} chunks padres")
            
        except Exception as e:
            logger.error(f"❌ Error procesando documento {doc_id}: {e}")
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
                message.ack()
                
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                message.nack()
    
    async def start_consuming(self):
        """Iniciar consumo de mensajes"""
        await self.connect_rabbitmq()
        
        queue = await self.channel.declare_queue("llamaindex_queue", durable=True)
        await queue.consume(self.process_message)
        
        logger.info("🔄 LlamaIndex Worker iniciado. Escuchando cola 'llamaindex_queue'...")
        
        try:
            await asyncio.Future()  # Ejecutar indefinidamente
        except KeyboardInterrupt:
            logger.info("🛑 Worker detenido")
        finally:
            if self.connection:
                await self.connection.close()


if __name__ == "__main__":
    worker = LlamaIndexWorker()
    asyncio.run(worker.start_consuming())
