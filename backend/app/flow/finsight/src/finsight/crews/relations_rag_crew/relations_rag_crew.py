"""
Relations RAG Crew (C2b) for Context Builder.

This crew retrieves relational context using LangExtract entities and relations.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import RoutingPlan, RelationItem, RelationalContext
from ...utils.llm import LLMFactory


@CrewBase
class RelationsRAGCrew:
    """
    Relations RAG Crew (C2b) for relational context retrieval.
    
    Uses a single agent that handles structured relationship extraction
    and analysis using LangExtract knowledge graphs.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def relations_rag_agent(self) -> Agent:
        """
        Single agent that handles all relational RAG operations.
        Retrieves structured relationships using LangExtract knowledge graph.
        """
        return Agent(
            config=self.agents_config['relations_rag_agent'],
            llm=LLMFactory.get_relations_rag_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def relations_retrieval_task(self) -> Task:
        """
        Comprehensive task that retrieves structured relationships and connections.
        """
        return Task(
            config=self.tasks_config['relations_retrieval_task'],
            agent=self.relations_rag_agent()
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
    
    def retrieve_relations(self, routing_plan: RoutingPlan, company_id: str) -> RelationalContext:
        """
        Retrieve relational context for the given routing plan.
        
        Args:
            routing_plan: Routing plan from N1
            company_id: Company identifier
            
        Returns:
            RelationalContext with relations and entity connections
        """
        # Mock implementation - in production would use actual LangExtract + Elasticsearch
        mock_relations = [
            RelationItem(
                subject="Revenue",
                predicate="affects",
                object="EBITDA",
                confidence=0.95,
                evidence_span="Revenue growth directly impacts EBITDA margins",
                doc_id=f"doc_{company_id}_003",
                page=2
            ),
            RelationItem(
                subject="Market Share",
                predicate="correlates_with", 
                object="Competitive Position",
                confidence=0.89,
                evidence_span="Market share indicates competitive positioning strength",
                doc_id=f"doc_{company_id}_004",
                page=5
            )
        ]
        
        return RelationalContext(relations=mock_relations)


def create_relations_rag_crew() -> RelationsRAGCrew:
    """Factory function to create a relations RAG crew instance."""
    return RelationsRAGCrew()
