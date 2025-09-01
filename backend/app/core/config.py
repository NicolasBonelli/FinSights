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
    
    # Azure OpenAI
    openai_api_key: str = Field(..., description="Azure OpenAI API Key")
    azure_gpt4_endpoint: str = Field(..., description="Azure GPT-4 endpoint URL")
    azure_gpt4o_endpoint: str = Field(..., description="Azure GPT-4o endpoint URL")
    azure_gpt4o_mini_endpoint: str = Field(..., description="Azure GPT-4o-mini endpoint URL")
    azure_gpt35_turbo_endpoint: str = Field(..., description="Azure GPT-3.5-turbo endpoint URL")
    azure_openai_api_version: str = Field(default="2024-12-01-preview", description="Azure OpenAI API version")
    
    # CrewAI Configuration
    crewai_max_parallel: int = Field(default=3, description="Maximum parallel agents in CrewAI")
    context_top_k: int = Field(default=8, description="Top K context documents for RAG")
    context_parent_expansion: int = Field(default=2, description="Parent expansion for context")
    relations_confidence_min: float = Field(default=0.6, description="Minimum confidence for relations")
    analytics_timeout_sec: int = Field(default=45, description="Analytics timeout in seconds")
    synthesis_timeout_sec: int = Field(default=30, description="Synthesis timeout in seconds")
    report_renderer: str = Field(default="pdf", description="Report renderer format")
    strict_citation: bool = Field(default=True, description="Enable strict citation mode")
    
    # Legacy LLM settings (kept for backward compatibility)
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    default_llm_provider: str = Field(default="azure_openai", description="Default LLM provider")
    
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
            'celery_result_backend',
            'openai_api_key',
            'azure_gpt4_endpoint',
            'azure_gpt4o_endpoint',
            'azure_gpt4o_mini_endpoint',
            'azure_gpt35_turbo_endpoint'
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
