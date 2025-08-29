"""
Database models and schemas
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing" 
    INDEXED = "indexed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProcessingStage(str, Enum):
    """Document processing stages"""
    TEXT_EXTRACTION = "text_extraction"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    RELATION_EXTRACTION = "relation_extraction"
    COMPLETED = "completed"


class DocumentMetadata(BaseModel):
    """Document metadata schema"""
    document_id: str = Field(..., description="Unique document identifier")
    company_id: str = Field(..., description="Company identifier")
    filename: str = Field(..., description="Original filename")
    blob_url: str = Field(..., description="Azure Blob Storage URL")
    content_type: str = Field(..., description="MIME type")
    file_size: int = Field(..., description="File size in bytes")
    upload_timestamp: datetime = Field(..., description="Upload timestamp")
    status: DocumentStatus = Field(..., description="Processing status")
    current_stage: Optional[ProcessingStage] = Field(default=None, description="Current processing stage")
    
    # Document content metadata
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    word_count: Optional[int] = Field(default=None, description="Number of words")
    chunk_count: Optional[int] = Field(default=None, description="Number of chunks")
    
    # Business metadata
    document_type: str = Field(..., description="Type of document")
    period: Optional[str] = Field(default=None, description="Period covered")
    year: Optional[int] = Field(default=None, description="Document year")
    quarter: Optional[str] = Field(default=None, description="Quarter (Q1, Q2, Q3, Q4)")
    fiscal_year: Optional[int] = Field(default=None, description="Fiscal year")
    
    # Processing metadata
    processing_started_at: Optional[datetime] = Field(default=None, description="Processing start time")
    processing_completed_at: Optional[datetime] = Field(default=None, description="Processing completion time")
    processing_duration_seconds: Optional[float] = Field(default=None, description="Processing duration")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Custom metadata
    tags: Optional[List[str]] = Field(default=None, description="Document tags")
    description: Optional[str] = Field(default=None, description="Document description")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom metadata fields")


class ChunkMetadata(BaseModel):
    """Document chunk metadata"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document ID")
    company_id: str = Field(..., description="Company identifier")
    content: str = Field(..., description="Chunk content")
    content_vector: Optional[List[float]] = Field(default=None, description="Embedding vector")
    
    # Position metadata
    page_number: Optional[int] = Field(default=None, description="Page number")
    chunk_index: int = Field(..., description="Chunk index within document")
    start_char: Optional[int] = Field(default=None, description="Start character position")
    end_char: Optional[int] = Field(default=None, description="End character position")
    
    # Content metadata
    word_count: int = Field(..., description="Number of words in chunk")
    char_count: int = Field(..., description="Number of characters in chunk")
    sentence_count: Optional[int] = Field(default=None, description="Number of sentences")
    
    # Semantic metadata
    content_type: Optional[str] = Field(default=None, description="Content type (text, table, figure)")
    section_title: Optional[str] = Field(default=None, description="Section title")
    section_type: Optional[str] = Field(default=None, description="Section type")
    semantic_role: Optional[str] = Field(default=None, description="Semantic role in document")
    
    # Extraction metadata
    extracted_entities: Optional[List[Dict[str, Any]]] = Field(default=None, description="Extracted entities")
    extracted_relations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Extracted relations")
    financial_metrics: Optional[List[Dict[str, Any]]] = Field(default=None, description="Financial metrics found")
    
    # Indexing metadata
    indexed_at: datetime = Field(..., description="Indexing timestamp")
    index_name: Optional[str] = Field(default=None, description="Elasticsearch index name")


class CompanyProfile(BaseModel):
    """Company profile data"""
    company_id: str = Field(..., description="Unique company identifier")
    company_name: str = Field(..., description="Company name")
    legal_name: Optional[str] = Field(default=None, description="Legal company name")
    
    # Business information
    industry: Optional[str] = Field(default=None, description="Industry sector")
    sub_industry: Optional[str] = Field(default=None, description="Sub-industry")
    country: str = Field(..., description="Country of incorporation")
    headquarters: Optional[str] = Field(default=None, description="Headquarters location")
    
    # Financial information
    primary_currency: str = Field(default="USD", description="Primary reporting currency")
    fiscal_year_end: str = Field(default="12-31", description="Fiscal year end (MM-DD)")
    market_cap: Optional[float] = Field(default=None, description="Market capitalization")
    employee_count: Optional[int] = Field(default=None, description="Number of employees")
    
    # System metadata
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    status: str = Field(default="active", description="Company status")
    
    # Document statistics
    total_documents: int = Field(default=0, description="Total number of documents")
    last_document_upload: Optional[datetime] = Field(default=None, description="Last document upload")
    last_analysis: Optional[datetime] = Field(default=None, description="Last analysis timestamp")
    
    # Custom fields
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    website: Optional[str] = Field(default=None, description="Company website")
    stock_symbol: Optional[str] = Field(default=None, description="Stock ticker symbol")
    exchange: Optional[str] = Field(default=None, description="Stock exchange")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom profile fields")


class TaskMetadata(BaseModel):
    """Task metadata for tracking"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task")
    company_id: str = Field(..., description="Company identifier")
    
    # Task details
    description: str = Field(..., description="Task description")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    priority: str = Field(default="normal", description="Task priority")
    
    # Status tracking
    status: str = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Task creation time")
    started_at: Optional[datetime] = Field(default=None, description="Task start time")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion time")
    
    # Progress tracking
    progress_percentage: float = Field(default=0.0, description="Progress percentage")
    current_step: Optional[str] = Field(default=None, description="Current processing step")
    steps_completed: int = Field(default=0, description="Number of completed steps")
    total_steps: int = Field(default=1, description="Total number of steps")
    
    # Result and error handling
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task result")
    error_message: Optional[str] = Field(default=None, description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    retry_count: int = Field(default=0, description="Number of retries")
    max_retries: int = Field(default=3, description="Maximum retries")
    
    # Execution metadata
    agent_types_used: Optional[List[str]] = Field(default=None, description="Agents used for task")
    execution_duration_seconds: Optional[float] = Field(default=None, description="Execution duration")
    queue_time_seconds: Optional[float] = Field(default=None, description="Time spent in queue")
    resource_usage: Optional[Dict[str, Any]] = Field(default=None, description="Resource usage stats")


class CacheEntry(BaseModel):
    """Cache entry metadata"""
    key: str = Field(..., description="Cache key")
    value: str = Field(..., description="Cached value (serialized)")
    content_type: str = Field(..., description="Content type")
    created_at: datetime = Field(..., description="Cache entry creation time")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration time")
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(default=None, description="Last access time")
    tags: Optional[List[str]] = Field(default=None, description="Cache tags for grouping")
    size_bytes: int = Field(..., description="Size of cached data in bytes")
