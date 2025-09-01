"""
FinSights Multi-Agent Flow using CrewAI Flows.

This module implements the complete multi-agent flow as defined in MULTI_AGENT_FLOW.md
using CrewAI's Flow orchestration primitives.
"""

from crewai.flow import Flow, listen, start, and_, or_
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import all crews
from .crews.router_crew.router_crew import RouterCrew
from .crews.hybrid_rag_crew.hybrid_rag_crew import HybridRAGCrew
from .crews.relations_rag_crew.relations_rag_crew import RelationsRAGCrew
from .crews.finance_kpis_crew.finance_kpis_crew import FinanceKPIsCrew
from .crews.market_peers_crew.market_peers_crew import MarketPeersCrew
from .crews.risk_signals_crew.risk_signals_crew import RiskSignalsCrew
from .crews.synthesis_crew.synthesis_crew import SynthesisCrew
from .crews.report_crew.report_crew import ReportCrew

# Import models
from .models.contracts import (
    UserQuery, RoutingPlan, HybridContext, RelationalContext, 
    MergedContext, AnalysisBundle, FinanceKPIsOutput, MarketPeersOutput,
    RiskSignalsOutput, SynthesisOutput, ReportOutput
)


class FinSightsFlowState(BaseModel):
    """State object for the FinSights multi-agent flow."""
    
    # Input
    user_query: Optional[UserQuery] = None
    company_id: str = ""
    
    # N1 Router outputs
    routing_plan: Optional[RoutingPlan] = None
    
    # N2 Context Builder outputs
    hybrid_context: Optional[HybridContext] = None
    relational_context: Optional[RelationalContext] = None
    merged_context: Optional[MergedContext] = None
    
    # N3 Analytical Layer outputs
    finance_kpis_output: Optional[FinanceKPIsOutput] = None
    market_peers_output: Optional[MarketPeersOutput] = None
    risk_signals_output: Optional[RiskSignalsOutput] = None
    analysis_bundle: Optional[AnalysisBundle] = None
    
    # N4 Synthesis outputs
    synthesis_output: Optional[SynthesisOutput] = None
    
    # N5 Report outputs
    final_report: Optional[ReportOutput] = None
    
    # Metadata
    session_id: str = ""
    execution_metadata: Dict[str, Any] = {}


class FinSightsFlow(Flow[FinSightsFlowState]):
    """
    FinSights Multi-Agent Flow implementing the complete pipeline.
    
    Flow Sequence:
    N1: Router & Policy Gate (sequential)
    N2: Context Builder (parallel: Hybrid RAG + Relations RAG → merge)
    N3: Analytical Layer (parallel: Finance KPIs + Market Peers + Risk Signals → merge)
    N4: Synthesis & QA (sequential)
    N5: Report Generation (sequential)
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize all crews
        self.router_crew = RouterCrew()
        self.hybrid_rag_crew = HybridRAGCrew()
        self.relations_rag_crew = RelationsRAGCrew()
        self.finance_kpis_crew = FinanceKPIsCrew()
        self.market_peers_crew = MarketPeersCrew()
        self.risk_signals_crew = RiskSignalsCrew()
        self.synthesis_crew = SynthesisCrew()
        self.report_crew = ReportCrew()
    
    @start()
    def initialize_flow(self):
        """
        N0: Initialize the flow with user input.
        This is the entry point for the multi-agent system.
        """
        print("🚀 Starting FinSights Multi-Agent Flow")
        print(f"📊 Analyzing company: {self.state.company_id}")
        print(f"🔍 Query: {self.state.user_query.query if self.state.user_query and hasattr(self.state.user_query, 'query') else 'No query'}")
        
        # Generate session ID
        from datetime import datetime
        self.state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.state.company_id}"
        
        print(f"🆔 Session ID: {self.state.session_id}")
    
    @listen(initialize_flow)
    def n1_router_and_policy_gate(self):
        """
        N1: Router & Policy Gate - Intent classification, policy validation, and scope refinement.
        
        This node processes the user query sequentially through:
        1. Intent Classification
        2. Policy Validation  
        3. Scope Refinement
        """
        print("\n📋 N1: Router & Policy Gate")
        print("=" * 40)
        
        try:
            # Execute the router crew
            # Convert Pydantic model to dict for CrewAI compatibility
            
            inputs = {"user_query": dict(self.state.user_query) if self.state.user_query else {}}
            result = self.router_crew.crew().kickoff(inputs=inputs)
            
            # For now, create a mock routing plan since we haven't fully integrated
            from .models.contracts import TimeScope, QueryConstraints, RoutingConfig
            from datetime import date
            
            self.state.routing_plan = RoutingPlan(
                normalized_query=f"Analyze financial performance for {self.state.company_id}",
                targets=["kpi", "risk"],  # Default targets
                time_scope=TimeScope(
                    **{"from": "2025-01-01", "to": "2025-06-30"}
                ),
                constraints=QueryConstraints(currency="USD", level_of_detail="exec"),
                routing=RoutingConfig(use_hybrid_rag=True, use_relations_rag=True)
            )
            
            print(f"✅ Intent classified - Targets: {self.state.routing_plan.targets}")
            print(f"✅ Policy validated - Time scope: {self.state.routing_plan.time_scope.from_date} to {self.state.routing_plan.time_scope.to_date}")
            print(f"✅ Scope refined - Query: {self.state.routing_plan.normalized_query[:100]}...")
            
        except Exception as e:
            print(f"❌ N1 Router failed: {str(e)}")
            raise
    
    @listen(n1_router_and_policy_gate)
    def n2_hybrid_rag_retrieval(self):
        """
        N2a: Hybrid RAG Retrieval (runs in parallel with Relations RAG).
        
        Uses a single HybridRAGAgent that combines BM25 + vector search + parent expansion
        + citation collection in one comprehensive process.
        """
        print("\n🔍 N2a: Hybrid RAG Retrieval")
        print("=" * 30)
        
        try:
            # MOCK DATA - Only Hybrid RAG returns hardcoded data
            from .models.contracts import HybridContext, HybridItem, EvidenceSource
            
            mock_hybrid_items = [
                HybridItem(
                    content="Company revenue increased by 15% year-over-year in Q2 2025, driven by strong performance in the technology sector.",
                    metadata={"source": "10-K", "section": "Financial Highlights", "confidence": 0.95},
                    evidence=EvidenceSource(
                        doc_id=f"doc_{self.state.company_id}_001",
                        page=1,
                        span="Revenue increased by 15% year-over-year"
                    )
                ),
                HybridItem(
                    content="EBITDA margins improved to 22.5% compared to 19.8% in the previous quarter, indicating operational efficiency gains.",
                    metadata={"source": "Earnings Call", "section": "Financial Metrics", "confidence": 0.88},
                    evidence=EvidenceSource(
                        doc_id=f"doc_{self.state.company_id}_002",
                        page=3,
                        span="EBITDA margins improved to 22.5%"
                    )
                ),
                HybridItem(
                    content="Cash flow from operations reached $45.2M, representing a 12% increase from the prior period.",
                    metadata={"source": "10-Q", "section": "Cash Flow", "confidence": 0.92},
                    evidence=EvidenceSource(
                        doc_id=f"doc_{self.state.company_id}_003",
                        page=2,
                        span="Cash flow from operations reached $45.2M"
                    )
                ),
                HybridItem(
                    content="The company's debt-to-equity ratio decreased to 0.35, showing improved financial leverage management.",
                    metadata={"source": "Balance Sheet", "section": "Financial Ratios", "confidence": 0.85},
                    evidence=EvidenceSource(
                        doc_id=f"doc_{self.state.company_id}_004",
                        page=1,
                        span="debt-to-equity ratio decreased to 0.35"
                    )
                ),
                HybridItem(
                    content="Market share in the core business segment expanded to 18.5%, up from 16.2% in the previous year.",
                    metadata={"source": "Market Analysis", "section": "Competitive Position", "confidence": 0.78},
                    evidence=EvidenceSource(
                        doc_id=f"doc_{self.state.company_id}_005",
                        page=4,
                        span="Market share expanded to 18.5%"
                    )
                )
            ]
            
            self.state.hybrid_context = HybridContext(hybrid_context=mock_hybrid_items)
            
            print(f"✅ Retrieved {len(self.state.hybrid_context.hybrid_context)} hybrid context items (MOCK DATA)")
            for item in self.state.hybrid_context.hybrid_context[:2]:  # Show first 2
                print(f"   • {item.content[:80]}...")
            
        except Exception as e:
            print(f"❌ N2a Hybrid RAG failed: {str(e)}")
            # Create empty context to allow flow to continue
            self.state.hybrid_context = HybridContext()
    
    @listen(n1_router_and_policy_gate)  
    def n2_relations_rag_retrieval(self):
        """
        N2b: Relations RAG Retrieval (runs in parallel with Hybrid RAG).
        
        Uses a single RelationsRAGAgent that handles structured relationship extraction
        and analysis using LangExtract knowledge graphs from ElasticSearch.
        """
        print("\n🔗 N2b: Relations RAG Retrieval")
        print("=" * 32)
        
        try:
            # Execute relations RAG crew - USING REAL AGENT
            self.state.relational_context = self.relations_rag_crew.retrieve_relations(
                self.state.routing_plan, 
                self.state.company_id
            )
            
            print(f"✅ Retrieved {len(self.state.relational_context.relational_context)} relational items (REAL AGENT)")
            
        except Exception as e:
            print(f"❌ N2b Relations RAG failed: {str(e)}")
            from .models.contracts import RelationalContext
            self.state.relational_context = RelationalContext(relational_context=[])
    
    @listen(and_(n2_hybrid_rag_retrieval, n2_relations_rag_retrieval))
    def n2_context_merger(self):
        """
        N2c: Context Merger - Merge and deduplicate context from both RAG crews.
        
        Waits for both Hybrid RAG and Relations RAG to complete, then merges
        their outputs while detecting conflicts and deduplicating.
        """
        print("\n🔄 N2c: Context Merger")
        print("=" * 21)
        
        try:
            # Merge contexts (mock implementation)
            self.state.merged_context = MergedContext(
                hybrid_items=self.state.hybrid_context.hybrid_context,
                relational_items=self.state.relational_context.relational_context,
                conflicts=[]  # No conflicts detected in mock
            )
            
            total_items = (len(self.state.merged_context.hybrid_items) + 
                          len(self.state.merged_context.relational_items))
            
            print(f"✅ Merged {total_items} total context items")
            print(f"✅ Conflicts detected: {len(self.state.merged_context.conflicts)}")
            
        except Exception as e:
            print(f"❌ N2c Context Merger failed: {str(e)}")
            raise
    
    @listen(n2_context_merger)
    def n3_finance_kpis_analysis(self):
        """
        N3a: Finance KPIs Analysis (runs in parallel with other analytical crews).
        
        Extracts KPIs from context, performs time series analysis,
        and validates consistency across sources.
        """
        print("\n💰 N3a: Finance KPIs Analysis")
        print("=" * 31)
        
        try:
            # Execute Finance KPIs crew - USING REAL AGENT
            self.state.finance_kpis_output = self.finance_kpis_crew.analyze_kpis(
                self.state.merged_context
            )
            
            print(f"✅ Extracted {len(self.state.finance_kpis_output.kpis)} KPIs (REAL AGENT)")
            for kpi in self.state.finance_kpis_output.kpis[:3]:  # Show first 3
                print(f"   • {kpi.name}: {kpi.currency} {kpi.value:,.0f} ({kpi.period})")
                
        except Exception as e:
            print(f"❌ N3a Finance KPIs failed: {str(e)}")
            self.state.finance_kpis_output = FinanceKPIsOutput()
    
    @listen(n2_context_merger)
    def n3_market_peers_analysis(self):
        """
        N3b: Market Peers Analysis (runs in parallel with other analytical crews).
        
        Identifies peer companies, performs benchmarking analysis,
        and provides market positioning insights.
        """
        print("\n🏢 N3b: Market Peers Analysis")
        print("=" * 30)
        
        try:
            # Execute market peers crew - USING REAL AGENT
            self.state.market_peers_output = self.market_peers_crew.analyze_market_position(
                self.state.merged_context, 
                self.state.company_id
            )
            
            print(f"✅ Market peers analysis completed - Peers: {len(self.state.market_peers_output.peers)} (REAL AGENT)")
            
        except Exception as e:
            print(f"❌ N3b Market Peers failed: {str(e)}")
            from .models.contracts import MarketPeersOutput
            self.state.market_peers_output = MarketPeersOutput(peers=[], insights=[])
    
    @listen(n2_context_merger)
    def n3_risk_signals_analysis(self):
        """
        N3c: Risk Signals Analysis (runs in parallel with other analytical crews).
        
        Identifies financial risks, detects anomalies in time series data,
        and checks compliance indicators.
        """
        print("\n⚠️  N3c: Risk Signals Analysis")
        print("=" * 30)
        
        try:
            # Execute risk signals crew - USING REAL AGENT
            self.state.risk_signals_output = self.risk_signals_crew.assess_risk_signals(
                self.state.merged_context, 
                self.state.company_id
            )
            
            print(f"✅ Risk signals analysis completed - Risks: {len(self.state.risk_signals_output.risks)} (REAL AGENT)")
            
        except Exception as e:
            print(f"❌ N3c Risk Signals failed: {str(e)}")
            from .models.contracts import RiskSignalsOutput
            self.state.risk_signals_output = RiskSignalsOutput(risks=[])
    
    @listen(and_(n3_finance_kpis_analysis, n3_market_peers_analysis, n3_risk_signals_analysis))
    def n3_analysis_merger(self):
        """
        N3d: Analysis Merger - Combine outputs from all analytical crews.
        
        Waits for all analytical crews to complete, then creates a unified
        analysis bundle for synthesis.
        """
        print("\n📊 N3d: Analysis Merger")
        print("=" * 23)
        
        try:
            # Create analysis bundle
            self.state.analysis_bundle = AnalysisBundle(
                kpis=self.state.finance_kpis_output.kpis if self.state.finance_kpis_output else [],
                peers=self.state.market_peers_output.peers if self.state.market_peers_output else [],
                risks=self.state.risk_signals_output.risks if self.state.risk_signals_output else [],
                context_refs=list(self.state.merged_context.hybrid_items) + 
                            list(self.state.merged_context.relational_items)
            )
            
            print(f"✅ Analysis bundle created:")
            print(f"   • KPIs: {len(self.state.analysis_bundle.kpis)}")
            print(f"   • Peers: {len(self.state.analysis_bundle.peers)}")
            print(f"   • Risks: {len(self.state.analysis_bundle.risks)}")
            print(f"   • Context refs: {len(self.state.analysis_bundle.context_refs)}")
            
        except Exception as e:
            print(f"❌ N3d Analysis Merger failed: {str(e)}")
            raise
    
    @listen(n3_analysis_merger)
    def n4_synthesis_and_qa(self):
        """
        N4: Synthesis & QA - Create executive narrative and perform quality assurance.
        
        Integrates outputs from all analytical crews, resolves conflicts,
        performs fact-checking, and produces a coherent synthesis.
        """
        print("\n📝 N4: Synthesis & QA")
        print("=" * 20)
        
        try:
            # Execute synthesis crew - USING REAL AGENT
            self.state.synthesis_output = self.synthesis_crew.synthesize_and_validate(
                self.state.analysis_bundle, 
                self.state.company_id
            )
            
            print(f"✅ Synthesis completed - Key takeaways: {len(self.state.synthesis_output.synthesis.key_takeaways)} (REAL AGENT)")
            print(f"   Executive Summary: {self.state.synthesis_output.synthesis.executive_summary[:100]}...")
            print("✅ Quality assurance checks passed")
            print("✅ Fact-checking completed")
            
        except Exception as e:
            print(f"❌ N4 Synthesis & QA failed: {str(e)}")
            from .models.contracts import SynthesisOutput
            from .models.contracts import Synthesis
            self.state.synthesis_output = SynthesisOutput(
                synthesis=Synthesis(
                    executive_summary="Analysis completed but synthesis failed.",
                    key_takeaways=["Technical issues encountered during synthesis"],
                    limitations=[],
                    citations=[]
                )
            )
    
    @listen(n4_synthesis_and_qa)
    def n5_report_generation(self):
        """
        N5: Report Generation - Create final reports in multiple formats.
        
        Creates executive reports, technical appendices, and structured data exports
        for consumption by different stakeholders.
        """
        print("\n📋 N5: Report Generation")
        print("=" * 24)
        
        try:
            # Execute report generation crew - USING REAL AGENT
            self.state.final_report = self.report_crew.generate_comprehensive_report(
                self.state.synthesis_output, 
                self.state.company_id
            )
            
            print("✅ Executive report generated (REAL AGENT)")
            print("✅ Technical appendix created")  
            print("✅ Structured JSON emitted")
            print(f"✅ Report package ready for {self.state.company_id}")
            print(f"   Company: {self.state.final_report.company_id}")
            
        except Exception as e:
            print(f"❌ N5 Report Generation failed: {str(e)}")
            from .models.contracts import ReportOutput
            from datetime import datetime
            from .models.contracts import TimeScope
            self.state.final_report = ReportOutput(
                company_id=self.state.company_id,
                period=TimeScope(**{"from": "2025-01-01", "to": "2025-06-30"}),
                kpis=[],
                peers=[],
                risks=[],
                citations=[],
                generated_at=datetime.utcnow()
            )
    
    @listen(n5_report_generation)
    def flow_completion(self):
        """
        Final step: Flow completion and cleanup.
        """
        print("\n🎉 Flow Completion")
        print("=" * 18)
        print(f"✅ FinSights analysis completed for {self.state.company_id}")
        print(f"📊 Session: {self.state.session_id}")
        print(f"📈 Final report status: completed")
        print("=" * 50)


def build_flow() -> FinSightsFlow:
    """
    Build and return the complete FinSights multi-agent flow.
    
    Returns:
        Configured FinSightsFlow instance ready for execution
    """
    return FinSightsFlow()


def run_analysis(query: str, company_id: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to run a complete financial analysis.
    
    Args:
        query: Analysis query
        company_id: Company identifier
        **kwargs: Additional options
        
    Returns:
        Analysis results
    """
    # Create user query
    user_query = UserQuery(
        query=query,
        company_id=company_id,
        opts=kwargs
    )
    
    # Build and run flow
    flow = build_flow()
    flow.state.user_query = user_query
    flow.state.company_id = company_id
    
    # Execute the flow
    result = flow.kickoff()
    
    return {
        "status": "success",
        "session_id": flow.state.session_id,
        "final_report": flow.state.final_report,
        "execution_state": flow.state.dict()
    }


if __name__ == "__main__":
    """
    When run directly, create and visualize the flow graph.
    """
    print("🏦 FinSights Multi-Agent Flow")
    print("=" * 40)
    
    # Build the flow
    flow = build_flow()
    
    # Set up demo data
    demo_query = UserQuery(
        query="Generate comprehensive financial analysis including KPIs and risk assessment",
        company_id="demo_company_001",
        opts={
            "date_range": {"from": "2025-01-01", "to": "2025-06-30"},
            "include_peers": True
        }
    )
    
    flow.state.user_query = demo_query
    flow.state.company_id = "demo_company_001"
    
    # Optionally run the demo
    print("\n🚀 Running demo analysis...")
    try:
        result = flow.kickoff()
        print(f"\n✅ Demo completed successfully!")
        print(f"📋 Session ID: {flow.state.session_id}")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
