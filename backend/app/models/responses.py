"""
Response models for API endpoints
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = Field(..., description="Operation success status")
    message: Optional[str] = Field(default=None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = Field(default=False, description="Operation success status")
    error_code: Optional[str] = Field(default=None, description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")


class DocumentUploadResponse(BaseResponse):
    """Response for document upload"""
    document_id: str = Field(..., description="Unique document identifier")
    blob_url: str = Field(..., description="Azure Blob Storage URL")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    task_id: Optional[str] = Field(default=None, description="Processing task ID")


class TaskStatusResponse(BaseResponse):
    """Response for task status check"""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Progress percentage")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task result if completed")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")


class RAGSearchResult(BaseModel):
    """Individual RAG search result"""
    content: str = Field(..., description="Retrieved content")
    score: float = Field(..., description="Relevance score")
    document_id: str = Field(..., description="Source document ID")
    chunk_id: str = Field(..., description="Chunk identifier")
    page_number: Optional[int] = Field(default=None, description="Page number in source document")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class RAGQueryResponse(BaseResponse):
    """Response for RAG search query"""
    query: str = Field(..., description="Original search query")
    results: List[RAGSearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results found")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")
    rag_type: str = Field(..., description="Type of RAG used")


class FinancialKPI(BaseModel):
    """Financial KPI data"""
    name: str = Field(..., description="KPI name")
    value: Union[float, str] = Field(..., description="KPI value")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    period: Optional[str] = Field(default=None, description="Period covered")
    trend: Optional[str] = Field(default=None, description="Trend direction: up, down, stable")
    benchmark: Optional[float] = Field(default=None, description="Benchmark or industry average")
    source: Optional[str] = Field(default=None, description="Data source")


class RiskSignal(BaseModel):
    """Risk signal data"""
    signal_type: str = Field(..., description="Type of risk signal")
    severity: str = Field(..., description="Risk severity: low, medium, high, critical")
    description: str = Field(..., description="Risk description")
    impact: Optional[str] = Field(default=None, description="Potential impact")
    recommendation: Optional[str] = Field(default=None, description="Recommended action")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score")


class MarketComparison(BaseModel):
    """Market comparison data"""
    metric: str = Field(..., description="Comparison metric")
    company_value: Union[float, str] = Field(..., description="Company value")
    industry_avg: Optional[Union[float, str]] = Field(default=None, description="Industry average")
    percentile: Optional[float] = Field(default=None, description="Company percentile in industry")
    peers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Peer company data")


class AnalysisResult(BaseModel):
    """Analysis result data"""
    agent_type: str = Field(..., description="Type of agent that generated the result")
    summary: str = Field(..., description="Analysis summary")
    kpis: Optional[List[FinancialKPI]] = Field(default=None, description="Financial KPIs")
    risk_signals: Optional[List[RiskSignal]] = Field(default=None, description="Risk signals")
    market_comparisons: Optional[List[MarketComparison]] = Field(default=None, description="Market comparisons")
    insights: Optional[List[str]] = Field(default=None, description="Key insights")
    recommendations: Optional[List[str]] = Field(default=None, description="Recommendations")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Overall confidence")
    execution_time_ms: float = Field(..., description="Agent execution time")


class AnalysisResponse(BaseResponse):
    """Response for financial analysis"""
    task_id: str = Field(..., description="Analysis task ID")
    question: str = Field(..., description="Original analysis question")
    company_id: str = Field(..., description="Company identifier")
    results: List[AnalysisResult] = Field(..., description="Analysis results from agents")
    executive_summary: Optional[str] = Field(default=None, description="Executive summary")
    total_execution_time_ms: float = Field(..., description="Total analysis time")
    agents_used: List[str] = Field(..., description="List of agents that participated")


class CompanyInfo(BaseModel):
    """Company information"""
    company_id: str = Field(..., description="Company identifier")
    company_name: str = Field(..., description="Company name")
    industry: Optional[str] = Field(default=None, description="Industry sector")
    country: Optional[str] = Field(default=None, description="Country")
    document_count: int = Field(default=0, description="Number of uploaded documents")
    last_analysis: Optional[datetime] = Field(default=None, description="Last analysis timestamp")
    status: str = Field(..., description="Company status")


class CompanyListResponse(BaseResponse):
    """Response for company list"""
    companies: List[CompanyInfo] = Field(..., description="List of companies")
    total_count: int = Field(..., description="Total number of companies")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


class DocumentInfo(BaseModel):
    """Document information"""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Original filename")
    upload_date: datetime = Field(..., description="Upload timestamp")
    file_size: int = Field(..., description="File size in bytes")
    document_type: str = Field(..., description="Document type")
    processing_status: str = Field(..., description="Processing status")
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")


class DocumentListResponse(BaseResponse):
    """Response for document list"""
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


class HealthCheckResponse(BaseResponse):
    """Health check response"""
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")


class AgentStatusResponse(BaseResponse):
    """Agent status response"""
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Agent status")
    active_tasks: int = Field(..., description="Number of active tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    error_rate: float = Field(..., description="Error rate percentage")
    average_execution_time_ms: float = Field(..., description="Average execution time")


class SystemMetricsResponse(BaseResponse):
    """System metrics response"""
    agents: List[AgentStatusResponse] = Field(..., description="Agent statuses")
    queue_sizes: Dict[str, int] = Field(..., description="Message queue sizes")
    cache_stats: Dict[str, Any] = Field(..., description="Cache statistics")
    database_stats: Dict[str, Any] = Field(..., description="Database statistics")


class ExportOptions(BaseModel):
    """Export format options"""
    format: str = Field(..., description="Export format: json, csv, excel, pdf")
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    include_raw_data: bool = Field(default=False, description="Include raw data")


class ExportResponse(BaseResponse):
    """Export response"""
    export_id: str = Field(..., description="Export identifier")
    download_url: str = Field(..., description="Download URL")
    expires_at: datetime = Field(..., description="URL expiration time")
    file_size: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="Export format")
