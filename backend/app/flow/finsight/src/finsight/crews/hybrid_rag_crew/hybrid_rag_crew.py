"""
Hybrid RAG Crew (C2a) for Context Builder.

This crew retrieves context using Elasticsearch with both BM25 and vector search,
expands context with parent chunks, and collects citations.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import RoutingPlan, ContextItem, HybridContext
from ...utils.llm import LLMFactory


@CrewBase
class HybridRAGCrew:
    """
    Hybrid RAG Crew (C2a) for context retrieval.
    
    Uses a single agent that combines hybrid search, parent expansion,
    and citation collection in one comprehensive process.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def hybrid_rag_agent(self) -> Agent:
        """
        Single agent that handles all hybrid RAG operations.
        Combines BM25 + vector search + parent retrieval + citation collection.
        """
        return Agent(
            config=self.agents_config['hybrid_rag_agent'],
            llm=LLMFactory.get_hybrid_rag_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def hybrid_retrieval_task(self) -> Task:
        """
        Comprehensive task that retrieves and contextualizes financial information.
        """
        return Task(
            config=self.tasks_config['hybrid_retrieval_task'],
            agent=self.hybrid_rag_agent()
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the crew with all agents and tasks."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process="sequential"
        )
    
    def retrieve_context(self, routing_plan: RoutingPlan, company_id: str) -> HybridContext:
        """
        Retrieve hybrid context for the given routing plan.
        
        Args:
            routing_plan: Routing plan from N1
            company_id: Company identifier
            
        Returns:
            HybridContext with retrieved items
        """
        # Mock implementation - in production would use actual Elasticsearch
        mock_results = [
            ContextItem(
                doc_id=f"doc_{company_id}_001",
                chunk_id="chunk_001",
                parent_id="parent_001",
                text=f"Sample financial data for {routing_plan.normalized_query}: Revenue increased by 15% in Q2.",
                page=1,
                score=0.95,
                evidence_span="Revenue increased by 15% in Q2"
            ),
            ContextItem(
                doc_id=f"doc_{company_id}_002", 
                chunk_id="chunk_002",
                parent_id="parent_002",
                text=f"EBITDA margin analysis shows improvement from 12% to 14%.",
                page=3,
                score=0.87,
                evidence_span="EBITDA margin analysis shows improvement"
            )
        ]
        
        return HybridContext(hybrid_context=mock_results)


def create_hybrid_rag_crew() -> HybridRAGCrew:
    """Factory function to create a hybrid RAG crew instance."""
    return HybridRAGCrew()
