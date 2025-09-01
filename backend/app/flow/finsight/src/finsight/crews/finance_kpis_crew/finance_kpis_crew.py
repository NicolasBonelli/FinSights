"""
Finance KPIs Crew (C3a) for Analytical Layer.

This crew extracts, validates, and analyzes financial KPIs from the merged context.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import MergedContext, FinanceKPIsOutput, KPIItem, EvidenceSource
from ...utils.llm import LLMFactory


@CrewBase
class FinanceKPIsCrew:
    """
    Finance KPIs Crew (C3a) for financial metrics analysis.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def kpi_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['kpi_extractor'],
            llm=LLMFactory.get_finance_kpis_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def time_series_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['time_series_agent'],
            llm=LLMFactory.get_finance_kpis_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_agent'],
            llm=LLMFactory.get_finance_kpis_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def extract_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_task'],
            agent=self.kpi_extractor()
        )
    
    @task
    def time_series_task(self) -> Task:
        return Task(
            config=self.tasks_config['time_series_task'],
            agent=self.time_series_agent()
        )
    
    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['validation_task'],
            agent=self.validation_agent()
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
    
    def analyze_kpis(self, merged_context: MergedContext) -> FinanceKPIsOutput:
        """
        Analyze financial KPIs from merged context.
        
        Args:
            merged_context: Merged context from RAG crews
            
        Returns:
            FinanceKPIsOutput with analyzed KPIs and notes
        """
        # Mock implementation
        mock_kpis = [
            KPIItem(
                name="Revenue",
                period="Q2-2025",
                value=10500000,
                currency="USD",
                delta_qoq=0.15,
                sources=[EvidenceSource(
                    doc_id="doc_001",
                    chunk_id="chunk_001",
                    page=1,
                    span="Revenue for Q2 2025 was $10.5 million"
                )]
            )
        ]
        
        return FinanceKPIsOutput(
            kpis=mock_kpis,
            notes=["Analysis completed with mock data"]
        )


def create_finance_kpis_crew() -> FinanceKPIsCrew:
    """Factory function to create a Finance KPIs crew instance."""
    return FinanceKPIsCrew()
