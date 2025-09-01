"""
Data contracts and Pydantic models for the FinSights multi-agent system.

This module defines all the data structures used to pass information between
agents and crews in the multi-agent pipeline.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


# Base models for evidence and citations
class EvidenceSource(BaseModel):
    """Reference to source document evidence."""
    doc_id: str = Field(..., description="Document identifier")
    chunk_id: Optional[str] = Field(None, description="Chunk identifier within document")
    page: Optional[int] = Field(None, description="Page number in the document")
    span: Optional[str] = Field(None, description="Specific text span as evidence")


class Citation(BaseModel):
    """Citation information for traceability."""
    doc_id: str = Field(..., description="Document identifier")
    page: int = Field(..., description="Page number")
    span: str = Field(..., description="Text span being cited")


# Context building contracts
class ContextItem(BaseModel):
    """Item from hybrid search context retrieval."""
    doc_id: str = Field(..., description="Document identifier")
    chunk_id: str = Field(..., description="Chunk identifier")
    parent_id: Optional[str] = Field(None, description="Parent chunk identifier")
    text: str = Field(..., description="Text content of the chunk")
    page: Optional[int] = Field(None, description="Page number in document")
    score: float = Field(..., description="Relevance score (0.0 to 1.0)")
    evidence_span: Optional[str] = Field(None, description="Specific evidence span")


class RelationItem(BaseModel):
    """Item from relational context extraction."""
    entity_class: str = Field(
        ...,
        description="Entity class",
        pattern="^(Metric|Value|TimePeriod|Company|Event|Risk|Trend|ComparisonTarget)$"
    )
    entity_text: str = Field(..., description="Text representation of the entity")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Entity attributes")
    evidence: EvidenceSource = Field(..., description="Source evidence for this relation")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")


# Router and policy contracts
class TimeScope(BaseModel):
    """Time period specification."""
    from_date: str = Field(..., description="Start date in YYYY-MM-DD format", alias="from")
    to_date: str = Field(..., description="End date in YYYY-MM-DD format", alias="to")


class QueryConstraints(BaseModel):
    """Query constraints and preferences."""
    currency: str = Field(default="USD", description="Preferred currency for financial data")
    level_of_detail: str = Field(
        default="exec",
        description="Level of detail",
        pattern="^(exec|detailed|technical)$"
    )


class RoutingConfig(BaseModel):
    """Routing configuration for context builders."""
    use_hybrid_rag: bool = Field(default=True, description="Enable hybrid RAG")
    use_relations_rag: bool = Field(default=True, description="Enable relations RAG")


class RoutingPlan(BaseModel):
    """Output contract from Router & Policy Gate."""
    normalized_query: str = Field(..., description="Normalized and refined query")
    targets: List[str] = Field(
        default_factory=lambda: ["kpi", "risk"],
        description="Analysis targets to include"
    )
    time_scope: TimeScope = Field(..., description="Time period for analysis")
    constraints: QueryConstraints = Field(default_factory=QueryConstraints)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)


# Context merging contracts
class HybridContext(BaseModel):
    """Output from Hybrid RAG Crew."""
    hybrid_context: List[ContextItem] = Field(default_factory=list)


class RelationalContext(BaseModel):
    """Output from Relations RAG Crew."""
    relational_context: List[RelationItem] = Field(default_factory=list)


class MergedContext(BaseModel):
    """Merged context from both RAG crews."""
    hybrid_items: List[ContextItem] = Field(default_factory=list)
    relational_items: List[RelationItem] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list, description="Detected conflicts")


# Analytics contracts
class KPIItem(BaseModel):
    """Financial KPI data item."""
    name: str = Field(..., description="KPI name (e.g., 'Revenue', 'EBITDA')")
    period: str = Field(..., description="Time period (e.g., 'Q2-2025')")
    value: Union[float, int] = Field(..., description="Numeric value")
    currency: str = Field(default="USD", description="Currency code")
    delta_qoq: Optional[float] = Field(None, description="Quarter-over-quarter change")
    delta_yoy: Optional[float] = Field(None, description="Year-over-year change")
    sources: List[EvidenceSource] = Field(default_factory=list, description="Evidence sources")


class PeerComparison(BaseModel):
    """Peer comparison data."""
    peer: str = Field(..., description="Peer company name")
    metric: str = Field(..., description="Metric being compared")
    ours: float = Field(..., description="Our company's value")
    peer_value: float = Field(..., description="Peer's value", alias="peer")
    gap: float = Field(..., description="Gap (positive = we're better)")


class RiskSignal(BaseModel):
    """Risk signal detection."""
    type: str = Field(..., description="Risk type (e.g., 'Liquidity', 'Credit')")
    signal: str = Field(..., description="Description of the risk signal")
    period: str = Field(..., description="Time period when detected")
    severity: str = Field(
        ...,
        description="Risk severity level",
        pattern="^(low|medium|high|critical)$"
    )
    evidence: List[EvidenceSource] = Field(default_factory=list)
    recommendation: Optional[str] = Field(None, description="Recommended action")


# Analytics bundle
class FinanceKPIsOutput(BaseModel):
    """Output from Finance KPIs Crew."""
    kpis: List[KPIItem] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list, description="Analysis notes")


class MarketPeersOutput(BaseModel):
    """Output from Market Peers Crew."""
    peers: List[PeerComparison] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list, description="Peer insights")


class RiskSignalsOutput(BaseModel):
    """Output from Risk Signals Crew."""
    risks: List[RiskSignal] = Field(default_factory=list)


class AnalysisBundle(BaseModel):
    """Combined analysis from all analytical crews."""
    kpis: List[KPIItem] = Field(default_factory=list)
    peers: List[PeerComparison] = Field(default_factory=list)
    risks: List[RiskSignal] = Field(default_factory=list)
    context_refs: List[Union[ContextItem, RelationItem]] = Field(default_factory=list)


# Synthesis contracts
class Synthesis(BaseModel):
    """Output from Synthesis crew."""
    executive_summary: str = Field(..., description="Executive summary narrative")
    key_takeaways: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)


class SynthesisOutput(BaseModel):
    """Complete synthesis output."""
    synthesis: Synthesis = Field(..., description="Synthesis results")


# Final report contracts
class ReportOutput(BaseModel):
    """Final report output structure."""
    company_id: str = Field(..., description="Company identifier")
    period: TimeScope = Field(..., description="Analysis period")
    kpis: List[KPIItem] = Field(default_factory=list)
    peers: List[PeerComparison] = Field(default_factory=list)
    risks: List[RiskSignal] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Input contracts
class UserQuery(BaseModel):
    """Initial user query input."""
    query: str = Field(..., description="User's query or directive")
    company_id: str = Field(..., description="Company identifier")
    opts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional parameters (e.g., 'include_peers', 'focus_area')"
    )


# Workflow state
class WorkflowState(BaseModel):
    """State object passed through the workflow."""
    session_id: str = Field(..., description="Unique session identifier")
    user_query: str = Field(..., description="Original user query")
    routing_plan: Optional[RoutingPlan] = Field(None, description="Routing plan from N1")
    merged_context: Optional[MergedContext] = Field(None, description="Merged context from N2")
    analysis_bundle: Optional[AnalysisBundle] = Field(None, description="Analysis from N3")
    synthesis_output: Optional[SynthesisOutput] = Field(None, description="Synthesis from N4")
    final_report: Optional[ReportOutput] = Field(None, description="Final report from N5")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
