"""
Market Peers Crew (N3b) for Analytical Layer.

This crew performs comparative analysis against market peers and industry benchmarks.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import MergedContext, MarketPeersOutput
from ...utils.llm import LLMFactory


@CrewBase
class MarketPeersCrew:
    """
    Market Peers Crew (N3b) for peer comparison analysis.
    
    Identifies relevant peers, researches benchmarks, and performs
    comparative analysis to generate strategic insights.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def market_analyst(self) -> Agent:
        """
        Market analyst that performs peer comparison analysis.
        """
        return Agent(
            config=self.agents_config['market_analyst'],
            llm=LLMFactory.get_market_peers_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def benchmark_researcher(self) -> Agent:
        """
        Researcher that compiles industry benchmarks and standards.
        """
        return Agent(
            config=self.agents_config['benchmark_researcher'],
            llm=LLMFactory.get_market_peers_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def competitive_insights(self) -> Agent:
        """
        Analyst that generates strategic insights from peer comparisons.
        """
        return Agent(
            config=self.agents_config['competitive_insights'],
            llm=LLMFactory.get_market_peers_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def peer_identification_task(self) -> Task:
        """
        Task to identify relevant market peers for comparison.
        """
        return Task(
            config=self.tasks_config['peer_identification_task'],
            agent=self.market_analyst()
        )
    
    @task
    def benchmark_research_task(self) -> Task:
        """
        Task to research industry benchmarks and standards.
        """
        return Task(
            config=self.tasks_config['benchmark_research_task'],
            agent=self.benchmark_researcher()
        )
    
    @task
    def competitive_analysis_task(self) -> Task:
        """
        Task to perform comparative analysis and generate insights.
        """
        return Task(
            config=self.tasks_config['competitive_analysis_task'],
            agent=self.competitive_insights()
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
    
    def analyze_market_position(self, merged_context: MergedContext, company_id: str) -> MarketPeersOutput:
        """
        Analyze company's market position against peers.
        
        Args:
            merged_context: Merged context from N2
            company_id: Company identifier
            
        Returns:
            MarketPeersOutput with peer comparison analysis
        """
        # Mock implementation - in production would use actual market data
        mock_analysis = {
            "peer_companies": [
                "CompetitorA Corp", "CompetitorB Inc", "Industry Leader Ltd"
            ],
            "market_position": "Above Average",
            "key_metrics_vs_peers": {
                "revenue_growth": {"company": 15.2, "peer_avg": 12.1, "percentile": 75},
                "profit_margin": {"company": 18.5, "peer_avg": 16.8, "percentile": 68},
                "debt_ratio": {"company": 0.35, "peer_avg": 0.42, "percentile": 25}
            },
            "competitive_strengths": [
                "Strong revenue growth above peer average",
                "Healthy profit margins",
                "Conservative debt management"
            ],
            "areas_for_improvement": [
                "Market share could be expanded",
                "Operating efficiency vs industry leaders"
            ],
            "strategic_recommendations": [
                "Leverage strong financial position for market expansion",
                "Invest in operational efficiency improvements"
            ]
        }
        
        return MarketPeersOutput(
            peers=[],
            insights=mock_analysis["strategic_recommendations"]
        )


def create_market_peers_crew() -> MarketPeersCrew:
    """Factory function to create a market peers crew instance."""
    return MarketPeersCrew()
