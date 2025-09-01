"""
Main Orchestrator for the FinSights Multi-Agent System.

This orchestrator coordinates the entire flow from user query to final report,
managing the execution of all crews in the proper sequence and handling
data flow between them.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

from .models.contracts import (
    UserQuery, WorkflowState, RoutingPlan, MergedContext, 
    AnalysisBundle, SynthesisOutput, ReportOutput
)
from .crews.router_crew.router_crew import RouterCrew
from .crews.hybrid_rag_crew.hybrid_rag_crew import HybridRAGCrew
from .crews.finance_kpis_crew.finance_kpis_crew import FinanceKPIsCrew
# Note: Legacy orchestrator updated to use new crews structure


class FinSightsOrchestrator:
    """
    Main orchestrator for the FinSights multi-agent system.
    
    Coordinates the execution of all crews according to the MULTI_AGENT_FLOW.md
    specification, managing data flow and handling errors gracefully.
    """
    
    def __init__(self):
        """Initialize the orchestrator with all crews."""
        # Initialize crews using new structure
        self.router_crew = RouterCrew()
        self.hybrid_rag_crew = HybridRAGCrew()
        self.finance_kpis_crew = FinanceKPIsCrew()

        
        # Execution tracking
        self.execution_metrics = {}
    
    def initialize_workflow_state(self, user_query: UserQuery) -> WorkflowState:
        """
        Initialize workflow state for tracking execution.
        
        Args:
            user_query: User's query and context
            
        Returns:
            Initialized workflow state
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_query.company_id}"
        
        return WorkflowState(
            session_id=session_id,
            user_query=user_query,
            metadata={
                "started_at": datetime.utcnow().isoformat(),
                "execution_steps": [],
                "performance_metrics": {}
            }
        )
    
    def execute_n1_router(self, workflow_state: WorkflowState) -> WorkflowState:
        """
        Execute N1 Router & Policy Gate crew.
        
        Args:
            workflow_state: Current workflow state
            
        Returns:
            Updated workflow state with routing plan
        """
        start_time = time.time()
        
        try:
            # Execute router crew
            routing_plan = self.router_crew.execute(workflow_state.user_query)
            
            # Update workflow state
            workflow_state.routing_plan = routing_plan
            execution_time = time.time() - start_time
            
            workflow_state.metadata["execution_steps"].append({
                "step": "N1_Router",
                "status": "completed",
                "execution_time": execution_time,
                "output_summary": {
                    "targets": routing_plan.targets,
                    "normalized_query": routing_plan.normalized_query[:100] + "...",
                    "time_scope": routing_plan.time_scope.dict()
                }
            })
            
            return workflow_state
            
        except Exception as e:
            workflow_state.metadata["execution_steps"].append({
                "step": "N1_Router",
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            raise
    
    async def execute_n2_context_builder(self, workflow_state: WorkflowState) -> WorkflowState:
        """
        Execute N2 Context Builder crews in parallel.
        
        Args:
            workflow_state: Current workflow state with routing plan
            
        Returns:
            Updated workflow state with merged context
        """
        start_time = time.time()
        
        try:
            routing_plan = workflow_state.routing_plan
            company_id = workflow_state.user_query.company_id
            
            # Execute both RAG crews in parallel if enabled
            tasks = []
            
            if routing_plan.routing.use_hybrid_rag:
                tasks.append(self._execute_hybrid_rag(routing_plan, company_id))
            
            if routing_plan.routing.use_relations_rag:
                tasks.append(self._execute_relations_rag(routing_plan, company_id))
            
            # Wait for both crews to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                hybrid_context = None
                relational_context = None
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print(f"Context crew {i} failed: {result}")
                        continue
                    
                    if hasattr(result, 'hybrid_context'):
                        hybrid_context = result
                    elif hasattr(result, 'relational_context'):
                        relational_context = result
                
                # Merge contexts
                if hybrid_context is None:
                    from .models.contracts import HybridContext
                    hybrid_context = HybridContext()
                
                if relational_context is None:
                    from .models.contracts import RelationalContext
                    relational_context = RelationalContext()
                
                merged_context = self.context_merger.execute(hybrid_context, relational_context)
                workflow_state.merged_context = merged_context
            
            execution_time = time.time() - start_time
            
            workflow_state.metadata["execution_steps"].append({
                "step": "N2_ContextBuilder",
                "status": "completed",
                "execution_time": execution_time,
                "output_summary": {
                    "hybrid_items": len(workflow_state.merged_context.hybrid_items),
                    "relational_items": len(workflow_state.merged_context.relational_items),
                    "conflicts": len(workflow_state.merged_context.conflicts)
                }
            })
            
            return workflow_state
            
        except Exception as e:
            workflow_state.metadata["execution_steps"].append({
                "step": "N2_ContextBuilder",
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            raise
    
    async def _execute_hybrid_rag(self, routing_plan, company_id):
        """Execute Hybrid RAG crew asynchronously."""
        return self.hybrid_rag_crew.execute(routing_plan, company_id)
    
    async def _execute_relations_rag(self, routing_plan, company_id):
        """Execute Relations RAG crew asynchronously."""
        return self.relations_rag_crew.execute(routing_plan, company_id)
    
    async def execute_n3_analytical_layer(self, workflow_state: WorkflowState) -> WorkflowState:
        """
        Execute N3 Analytical Layer crews in parallel.
        
        Args:
            workflow_state: Current workflow state with merged context
            
        Returns:
            Updated workflow state with analysis bundle
        """
        start_time = time.time()
        
        try:
            merged_context = workflow_state.merged_context
            targets = workflow_state.routing_plan.targets
            
            # Execute analytical crews based on targets
            tasks = []
            task_names = []
            
            if 'kpi' in targets:
                tasks.append(self._execute_finance_kpis(merged_context))
                task_names.append('finance_kpis')
            
            if 'peers' in targets:
                tasks.append(self._execute_market_peers_placeholder(merged_context))
                task_names.append('market_peers')
            
            if 'risk' in targets:
                tasks.append(self._execute_risk_signals_placeholder(merged_context))
                task_names.append('risk_signals')
            
            # Wait for all analytical crews to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                finance_output = None
                peers_output = None
                risk_output = None
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print(f"Analytical crew {task_names[i]} failed: {result}")
                        continue
                    
                    if task_names[i] == 'finance_kpis':
                        finance_output = result
                    elif task_names[i] == 'market_peers':
                        peers_output = result
                    elif task_names[i] == 'risk_signals':
                        risk_output = result
                
                # Create analysis bundle
                analysis_bundle = AnalysisBundle(
                    kpis=finance_output.kpis if finance_output else [],
                    peers=peers_output.peers if peers_output else [],
                    risks=risk_output.risks if risk_output else [],
                    context_refs=list(merged_context.hybrid_items) + list(merged_context.relational_items)
                )
                
                workflow_state.analysis_bundle = analysis_bundle
            
            execution_time = time.time() - start_time
            
            workflow_state.metadata["execution_steps"].append({
                "step": "N3_AnalyticalLayer",
                "status": "completed",
                "execution_time": execution_time,
                "output_summary": {
                    "kpis_extracted": len(workflow_state.analysis_bundle.kpis),
                    "peers_analyzed": len(workflow_state.analysis_bundle.peers),
                    "risks_identified": len(workflow_state.analysis_bundle.risks)
                }
            })
            
            return workflow_state
            
        except Exception as e:
            workflow_state.metadata["execution_steps"].append({
                "step": "N3_AnalyticalLayer",
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            raise
    
    async def _execute_finance_kpis(self, merged_context):
        """Execute Finance KPIs crew asynchronously."""
        return self.finance_kpis_crew.execute(merged_context)
    
    async def _execute_market_peers_placeholder(self, merged_context):
        """Execute Market Peers crew with KPIs (placeholder - needs KPIs from finance crew)."""
        # In real implementation, would wait for finance KPIs first
        # For now, create empty KPIs list
        from .models.contracts import MarketPeersOutput
        return MarketPeersOutput()
    
    async def _execute_risk_signals_placeholder(self, merged_context):
        """Execute Risk Signals crew with context and KPIs (placeholder)."""
        # In real implementation, would have KPIs from finance crew
        from .models.contracts import RiskSignalsOutput
        return RiskSignalsOutput()
    
    def execute_n4_synthesis(self, workflow_state: WorkflowState) -> WorkflowState:
        """
        Execute N4 Synthesis & QA crew.
        
        Args:
            workflow_state: Current workflow state with analysis bundle
            
        Returns:
            Updated workflow state with synthesis output
        """
        start_time = time.time()
        
        try:
            analysis_bundle = workflow_state.analysis_bundle
            
            # Execute synthesis crew
            synthesis_output = self.synthesis_crew.execute(analysis_bundle)
            workflow_state.synthesis_output = synthesis_output
            
            execution_time = time.time() - start_time
            
            workflow_state.metadata["execution_steps"].append({
                "step": "N4_Synthesis",
                "status": "completed",
                "execution_time": execution_time,
                "output_summary": {
                    "executive_summary_length": len(synthesis_output.synthesis.executive_summary),
                    "key_takeaways": len(synthesis_output.synthesis.key_takeaways),
                    "limitations": len(synthesis_output.synthesis.limitations),
                    "citations": len(synthesis_output.synthesis.citations)
                }
            })
            
            return workflow_state
            
        except Exception as e:
            workflow_state.metadata["execution_steps"].append({
                "step": "N4_Synthesis",
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            raise
    
    def execute_n5_report_generation(
        self, 
        workflow_state: WorkflowState,
        output_type: str = "complete"
    ) -> WorkflowState:
        """
        Execute N5 Report Generation crew.
        
        Args:
            workflow_state: Current workflow state with synthesis output
            output_type: Type of output to generate
            
        Returns:
            Updated workflow state with final report
        """
        start_time = time.time()
        
        try:
            analysis_bundle = workflow_state.analysis_bundle
            synthesis_output = workflow_state.synthesis_output
            time_scope = workflow_state.routing_plan.time_scope
            company_id = workflow_state.user_query.company_id
            
            # Execute report generation crew
            final_report = self.report_crew.execute(
                analysis_bundle,
                synthesis_output,
                company_id,
                time_scope,
                output_type
            )
            
            workflow_state.final_report = final_report
            
            execution_time = time.time() - start_time
            
            workflow_state.metadata["execution_steps"].append({
                "step": "N5_ReportGeneration",
                "status": "completed",
                "execution_time": execution_time,
                "output_summary": {
                    "output_type": output_type,
                    "formats_generated": ["pdf", "json"]  # Default formats
                }
            })
            
            # Add final metadata
            workflow_state.metadata["completed_at"] = datetime.utcnow().isoformat()
            workflow_state.metadata["total_execution_time"] = sum(
                step.get("execution_time", 0) for step in workflow_state.metadata["execution_steps"]
            )
            
            return workflow_state
            
        except Exception as e:
            workflow_state.metadata["execution_steps"].append({
                "step": "N5_ReportGeneration",
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            raise
    
    async def execute_full_pipeline(
        self, 
        user_query: UserQuery,
        output_type: str = "complete"
    ) -> Dict[str, Any]:
        """
        Execute the complete multi-agent pipeline.
        
        Args:
            user_query: User's query and context
            output_type: Type of output to generate ("complete", "api", "executive")
            
        Returns:
            Complete pipeline results with workflow state and outputs
        """
        # Initialize workflow state
        workflow_state = self.initialize_workflow_state(user_query)
        
        try:
            # N1: Router & Policy Gate
            workflow_state = self.execute_n1_router(workflow_state)
            
            # N2: Context Builder (parallel)
            workflow_state = await self.execute_n2_context_builder(workflow_state)
            
            # N3: Analytical Layer (parallel)
            workflow_state = await self.execute_n3_analytical_layer(workflow_state)
            
            # N4: Synthesis & QA
            workflow_state = self.execute_n4_synthesis(workflow_state)
            
            # N5: Report Generation
            workflow_state = self.execute_n5_report_generation(workflow_state, output_type)
            
            # Return complete results
            return {
                "status": "success",
                "session_id": workflow_state.session_id,
                "workflow_state": workflow_state.dict(),
                "final_output": workflow_state.final_report,
                "execution_metadata": workflow_state.metadata
            }
            
        except Exception as e:
            # Handle pipeline failure
            workflow_state.metadata["failed_at"] = datetime.utcnow().isoformat()
            workflow_state.metadata["failure_reason"] = str(e)
            
            return {
                "status": "failed",
                "session_id": workflow_state.session_id,
                "error": str(e),
                "workflow_state": workflow_state.dict(),
                "execution_metadata": workflow_state.metadata
            }
    
    def execute_pipeline_sync(
        self, 
        user_query: UserQuery,
        output_type: str = "complete"
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for the pipeline execution.
        
        Args:
            user_query: User's query and context
            output_type: Type of output to generate
            
        Returns:
            Complete pipeline results
        """
        return asyncio.run(self.execute_full_pipeline(user_query, output_type))


# Factory function
def create_orchestrator() -> FinSightsOrchestrator:
    """Factory function to create an orchestrator instance."""
    return FinSightsOrchestrator()


# Convenience functions for common use cases
async def analyze_company(
    query: str,
    company_id: str,
    opts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze a company.
    
    Args:
        query: Analysis query
        company_id: Company identifier
        opts: Optional parameters
        
    Returns:
        Analysis results
    """
    orchestrator = create_orchestrator()
    user_query = UserQuery(
        query=query,
        company_id=company_id,
        opts=opts or {}
    )
    
    return await orchestrator.execute_full_pipeline(user_query, "api")


def analyze_company_sync(
    query: str,
    company_id: str,
    opts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Synchronous convenience function to analyze a company.
    
    Args:
        query: Analysis query
        company_id: Company identifier
        opts: Optional parameters
        
    Returns:
        Analysis results
    """
    return asyncio.run(analyze_company(query, company_id, opts))
