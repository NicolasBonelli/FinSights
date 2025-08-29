"""
Request models for API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class AgentType(str, Enum):
    """Available agent types"""
    FINANCE_KPIS = "finance_kpis"
    MARKET_PEERS = "market_peers"
    RISK_SIGNALS = "risk_signals"
    HYBRID_RAG = "hybrid_rag"
    LANGEXTRACT_RAG = "langextract_rag"


class AnalysisRequest(BaseModel):
    """Request for financial analysis"""
    company_id: str = Field(..., description="Company identifier")
    question: str = Field(..., min_length=10, max_length=1000, description="Analysis question")
    agent_types: Optional[List[AgentType]] = Field(
        default=None, 
        description="Specific agents to use (if not provided, system will auto-select)"
    )
    priority: Optional[str] = Field(default="normal", description="Task priority: low, normal, high")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for analysis")
    
    @validator("question")
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class RAGQueryRequest(BaseModel):
    """Request for RAG search"""
    company_id: str = Field(..., description="Company identifier")
    query: str = Field(..., min_length=5, max_length=500, description="Search query")
    rag_type: str = Field(default="hybrid", description="RAG type: hybrid or langextract")
    max_results: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum number of results")
    include_metadata: Optional[bool] = Field(default=True, description="Include document metadata")
    
    @validator("rag_type")
    def validate_rag_type(cls, v):
        if v not in ["hybrid", "langextract"]:
            raise ValueError("rag_type must be 'hybrid' or 'langextract'")
        return v


class DocumentUploadMetadata(BaseModel):
    """Metadata for document upload"""
    company_id: str = Field(..., description="Company identifier")
    document_type: Optional[str] = Field(default="financial_report", description="Type of document")
    period: Optional[str] = Field(default=None, description="Period covered (e.g., Q1 2024)")
    year: Optional[int] = Field(default=None, ge=2000, le=2030, description="Year of the document")
    tags: Optional[List[str]] = Field(default=None, description="Document tags")
    description: Optional[str] = Field(default=None, max_length=500, description="Document description")


class AgentExecutionRequest(BaseModel):
    """Request for direct agent execution"""
    agent_type: AgentType = Field(..., description="Type of agent to execute")
    task_description: str = Field(..., min_length=10, description="Task description for the agent")
    company_id: str = Field(..., description="Company identifier")
    context_data: Optional[Dict[str, Any]] = Field(default=None, description="Context data for the agent")
    timeout_seconds: Optional[int] = Field(default=300, ge=30, le=600, description="Execution timeout")


class BulkAnalysisRequest(BaseModel):
    """Request for bulk analysis across multiple companies or questions"""
    company_ids: List[str] = Field(..., min_items=1, max_items=10, description="List of company identifiers")
    questions: List[str] = Field(..., min_items=1, max_items=5, description="List of analysis questions")
    agent_types: Optional[List[AgentType]] = Field(default=None, description="Agents to use for analysis")
    parallel_execution: Optional[bool] = Field(default=True, description="Execute tasks in parallel")


class TaskStatusRequest(BaseModel):
    """Request to check task status"""
    task_id: str = Field(..., description="Task identifier")


class CompanyOnboardingRequest(BaseModel):
    """Request for company onboarding"""
    company_id: str = Field(..., description="Unique company identifier")
    company_name: str = Field(..., min_length=2, max_length=200, description="Company name")
    industry: Optional[str] = Field(default=None, description="Industry sector")
    country: Optional[str] = Field(default=None, description="Country of operation")
    currency: Optional[str] = Field(default="USD", description="Primary currency")
    fiscal_year_end: Optional[str] = Field(default="12-31", description="Fiscal year end (MM-DD)")
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    
    @validator("company_id")
    def validate_company_id(cls, v):
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Company ID must contain only alphanumeric characters, hyphens, and underscores")
        return v.lower()


class FilterOptions(BaseModel):
    """Options for filtering results"""
    date_from: Optional[str] = Field(default=None, description="Filter from date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(default=None, description="Filter to date (YYYY-MM-DD)")
    document_types: Optional[List[str]] = Field(default=None, description="Filter by document types")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    score_threshold: Optional[float] = Field(default=0.0, ge=0.0, le=1.0, description="Minimum relevance score")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
