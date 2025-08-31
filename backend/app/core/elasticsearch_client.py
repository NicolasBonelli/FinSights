"""
Elasticsearch client and utilities
"""
import logging
from typing import Optional, Dict, List, Any
from elasticsearch import AsyncElasticsearch
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

# Global Elasticsearch client instance
elasticsearch_client: Optional[AsyncElasticsearch] = None


async def get_elasticsearch_client() -> AsyncElasticsearch:
    """Get Elasticsearch client instance"""
    global elasticsearch_client
    if elasticsearch_client is None:
        settings = get_settings()
        
        # Para Docker, no necesitamos autenticación por defecto
        elasticsearch_client = AsyncElasticsearch(
            [settings.elasticsearch_url],
            verify_certs=False,
            ssl_show_warn=False
        )
    
    return elasticsearch_client


async def close_elasticsearch():
    """Close Elasticsearch connection"""
    global elasticsearch_client
    if elasticsearch_client:
        await elasticsearch_client.close()
        elasticsearch_client = None


class ElasticsearchService:
    """Elasticsearch service for hybrid search"""
    
    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None
        self.settings = get_settings()
    
    async def get_client(self) -> AsyncElasticsearch:
        """Get Elasticsearch client"""
        if self.client is None:
            self.client = await get_elasticsearch_client()
        return self.client
    
    async def create_document_index(self, company_id: str) -> bool:
        """Create document index for a company"""
        try:
            client = await self.get_client()
            index_name = f"{self.settings.elasticsearch_index_prefix}_{company_id}_documents"
            
            mapping = {
                "mappings": {
                    "properties": {
                        "document_id": {"type": "keyword"},
                        "company_id": {"type": "keyword"},
                        "content": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "content_vector": {
                            "type": "dense_vector",
                            "dims": 1536  # OpenAI embeddings dimension
                        },
                        "chunk_id": {"type": "keyword"},
                        "page_number": {"type": "integer"},
                        "metadata": {"type": "object"},
                        "timestamp": {"type": "date"},
                        "document_type": {"type": "keyword"}
                    }
                }
            }
            
            await client.indices.create(index=index_name, body=mapping, ignore=400)
            logger.info(f"Created index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating document index: {e}")
            return False
    
    async def index_document_chunk(
        self, 
        company_id: str, 
        document_id: str, 
        chunk_data: Dict[str, Any]
    ) -> bool:
        """Index a document chunk"""
        try:
            client = await self.get_client()
            index_name = f"{self.settings.elasticsearch_index_prefix}_{company_id}_documents"
            
            await client.index(
                index=index_name,
                body=chunk_data,
                id=chunk_data.get("chunk_id")
            )
            return True
            
        except Exception as e:
            logger.error(f"Error indexing document chunk: {e}")
            return False
    
    async def hybrid_search(
        self, 
        company_id: str, 
        query: str, 
        query_vector: List[float], 
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search (BM25 + vector)"""
        try:
            client = await self.get_client()
            index_name = f"{self.settings.elasticsearch_index_prefix}_{company_id}_documents"
            
            search_body = {
                "size": size,
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "content": {
                                        "query": query,
                                        "boost": 1.0
                                    }
                                }
                            },
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                                        "params": {"query_vector": query_vector}
                                    },
                                    "boost": 1.0
                                }
                            }
                        ]
                    }
                },
                "_source": ["document_id", "content", "metadata", "page_number", "chunk_id"]
            }
            
            response = await client.search(index=index_name, body=search_body)
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "content": hit["_source"]["content"],
                    "metadata": hit["_source"]["metadata"],
                    "score": hit["_score"],
                    "document_id": hit["_source"]["document_id"],
                    "chunk_id": hit["_source"]["chunk_id"],
                    "page_number": hit["_source"].get("page_number")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing hybrid search: {e}")
            return []
    
    async def get_document_chunks(self, company_id: str, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            client = await self.get_client()
            index_name = f"{self.settings.elasticsearch_index_prefix}_{company_id}_documents"
            
            search_body = {
                "query": {
                    "term": {"document_id": document_id}
                },
                "sort": [{"page_number": {"order": "asc"}}],
                "size": 1000
            }
            
            response = await client.search(index=index_name, body=search_body)
            
            chunks = []
            for hit in response["hits"]["hits"]:
                chunks.append(hit["_source"])
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving document chunks: {e}")
            return []


# Global service instance
elasticsearch_service = ElasticsearchService()
