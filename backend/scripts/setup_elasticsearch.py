#!/usr/bin/env python3
"""
Script para configurar Elasticsearch en Docker
"""

import asyncio
import logging
from elasticsearch import AsyncElasticsearch
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_elasticsearch():
    """Configurar Elasticsearch para los workers"""
    
    settings = get_settings()
    
    # Conectar a Elasticsearch
    es_client = AsyncElasticsearch(
        [settings.elasticsearch_url],
        verify_certs=False,
        ssl_show_warn=False
    )
    
    try:
        # Verificar conexión
        info = await es_client.info()
        logger.info(f"✅ Conectado a Elasticsearch {info['version']['number']}")
        
        # Crear índices para los workers
        company_id = "default"  # Puedes cambiar esto
        
        # Índice para chunks pequeños
        chunks_small_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "doc_id": {"type": "keyword"},
                    "chunk_text": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "parent_id": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384  # e5-base-v2 embeddings
                    },
                    "company_id": {"type": "keyword"}
                }
            }
        }
        
        # Índice para chunks padres
        chunks_parent_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "doc_id": {"type": "keyword"},
                    "parent_text": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "company_id": {"type": "keyword"}
                }
            }
        }
        
        # Índice para relaciones
        relations_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "doc_id": {"type": "keyword"},
                    "entity_class": {"type": "keyword"},
                    "entity_text": {"type": "text"},
                    "attributes": {"type": "object"},
                    "evidence_text": {"type": "text"},
                    "confidence": {"type": "float"},
                    "company_id": {"type": "keyword"}
                }
            }
        }
        
        indices = [
            (f"chunks_small_{company_id}", chunks_small_mapping),
            (f"chunks_parent_{company_id}", chunks_parent_mapping),
            (f"relations_{company_id}", relations_mapping)
        ]
        
        for index_name, mapping in indices:
            try:
                await es_client.indices.create(
                    index=index_name,
                    body=mapping,
                    ignore=400  # Ignorar si ya existe
                )
                logger.info(f"✅ Índice creado: {index_name}")
            except Exception as e:
                logger.info(f"ℹ️ Índice {index_name}: {e}")
        
        logger.info("🎉 Configuración de Elasticsearch completada!")
        
    except Exception as e:
        logger.error(f"❌ Error configurando Elasticsearch: {e}")
        raise
    finally:
        await es_client.close()


if __name__ == "__main__":
    asyncio.run(setup_elasticsearch())
