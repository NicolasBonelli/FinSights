"""
Synthesis & QA Crew (N4) for Synthesis & QA Layer.

This crew synthesizes insights from all analytical crews and performs quality assurance.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import AnalysisBundle, SynthesisOutput
from ...utils.llm import LLMFactory


@CrewBase
class SynthesisCrew:
    """
    Synthesis & QA Crew (N4) for insight integration and quality assurance.
    
    Synthesizes insights from all analytical crews, performs fact-checking,
    and resolves conflicts to produce final integrated conclusions.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def synthesis_analyst(self) -> Agent:
        """
        Analyst that synthesizes insights from all analytical crews.
        """
        return Agent(
            config=self.agents_config['synthesis_analyst'],
            llm=LLMFactory.get_synthesis_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def fact_checker(self) -> Agent:
        """
        Specialist that performs fact-checking and quality assurance.
        """
        return Agent(
            config=self.agents_config['fact_checker'],
            llm=LLMFactory.get_synthesis_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def conflict_resolver(self) -> Agent:
        """
        Specialist that resolves conflicts between analytical perspectives.
        """
        return Agent(
            config=self.agents_config['conflict_resolver'],
            llm=LLMFactory.get_synthesis_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def synthesis_integration_task(self) -> Task:
        """
        Task to integrate insights from all analytical crews.
        """
        return Task(
            config=self.tasks_config['synthesis_integration_task'],
            agent=self.synthesis_analyst()
        )
    
    @task
    def quality_assurance_task(self) -> Task:
        """
        Task to perform quality assurance and fact-checking.
        """
        return Task(
            config=self.tasks_config['quality_assurance_task'],
            agent=self.fact_checker()
        )
    
    @task
    def conflict_resolution_task(self) -> Task:
        """
        Task to resolve conflicts and finalize conclusions.
        """
        return Task(
            config=self.tasks_config['conflict_resolution_task'],
            agent=self.conflict_resolver()
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
    
    def synthesize_and_validate(self, analysis_bundle: AnalysisBundle, company_id: str) -> SynthesisOutput:
        """
        Synthesize insights from all analytical crews and perform quality assurance.
        
        Args:
            analysis_bundle: Bundle with outputs from all analytical crews
            company_id: Company identifier
            
        Returns:
            SynthesisOutput with integrated and validated conclusions
        """
        # Mock implementation - in production would perform actual synthesis
        mock_synthesis = {
            "executive_summary": f"Analysis of {company_id} reveals a financially healthy company with strong growth potential but moderate market risks.",
            "key_findings": [
                "Strong financial performance with revenue growth above industry average",
                "Healthy profit margins and conservative debt management", 
                "Competitive position is solid but faces increasing market volatility",
                "Risk profile is moderate with manageable exposure to market fluctuations"
            ],
            "integrated_insights": {
                "financial_health": "Strong - KPIs show consistent performance and healthy ratios",
                "market_position": "Above Average - outperforming peers on key metrics", 
                "risk_assessment": "Moderate - manageable risks with clear mitigation strategies"
            },
            "actionable_recommendations": [
                "Leverage strong financial position to expand market share",
                "Diversify revenue streams to reduce market volatility impact",
                "Strengthen supplier relationships to mitigate supply chain risks",
                "Maintain conservative debt levels while investing in growth"
            ],
            "confidence_level": "High",
            "data_quality_score": 0.92,
            "analytical_consistency": "Good - no major conflicts detected between analyses"
        }
        
        from ...models.contracts import Synthesis
        
        return SynthesisOutput(
            synthesis=Synthesis(
                executive_summary=mock_synthesis["executive_summary"],
                key_takeaways=mock_synthesis["key_findings"],
                limitations=[],
                citations=[]
            )
        )


def create_synthesis_crew() -> SynthesisCrew:
    """Factory function to create a synthesis crew instance."""
    return SynthesisCrew()
