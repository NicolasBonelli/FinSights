"""
Application configuration settings
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv(override=True)


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "FinSights API"
    debug: bool = False
    environment: str = Field(default="development", description="Environment: development, staging, production")
    api_v1_str: str = "/api/v1"
    
    # CORS
    allowed_hosts: List[str] = ["*"]
    
    # Database connections
    redis_url: str = Field(..., description="Redis connection URL")
    redis_password: Optional[str] = None
    
    # Elasticsearch
    elasticsearch_url: str = Field(..., description="Elasticsearch URL")
    elasticsearch_username: Optional[str] = None
    elasticsearch_password: Optional[str] = None
    elasticsearch_index_prefix: Optional[str] = None
    
    # RabbitMQ
    rabbitmq_url: str = Field(..., description="RabbitMQ connection URL")
    rabbitmq_username: str = Field(..., description="RabbitMQ username")
    rabbitmq_password: str = Field(..., description="RabbitMQ password")
    
    # Azure Blob Storage
    azure_storage_connection_string: str = Field(..., description="Azure Storage Connection String")
    azure_storage_account: str = Field(..., description="Azure Storage Account name")
    azure_storage_key: str = Field(..., description="Azure Storage Account key")
    azure_container_name: str = Field(default="financial-documents", description="Azure Blob container name")
    
    # Celery
    celery_broker_url: str = Field(..., description="Celery broker URL")
    celery_result_backend: str = Field(..., description="Celery result backend URL")
    
    # CrewAI / LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    default_llm_provider: str = Field(default="openai", description="Default LLM provider")
    
    # File processing
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    allowed_file_types: List[str] = Field(default=["pdf"], description="Allowed file types")
    
    # Agent settings
    max_concurrent_agents: int = Field(default=5, description="Maximum concurrent agents")
    agent_timeout_seconds: int = Field(default=300, description="Agent timeout in seconds")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validar que las variables obligatorias estén presentes
        self._validate_required_fields()
    
    def _validate_required_fields(self):
        """Validar que los campos obligatorios estén configurados"""
        required_fields = [
            'redis_url', 
            'elasticsearch_url',
            'rabbitmq_url',
            'rabbitmq_username',
            'rabbitmq_password',
            'azure_storage_connection_string',
            'azure_storage_account',
            'azure_storage_key',
            'celery_broker_url',
            'celery_result_backend'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(
                f"❌ Campos obligatorios faltantes en configuración: {', '.join(missing_fields)}\n"
                f"💡 Asegúrate de que estén definidos en tu archivo .env"
            )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
