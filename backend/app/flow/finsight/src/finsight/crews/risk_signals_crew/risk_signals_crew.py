"""
Risk Signals Crew (N3c) for Analytical Layer.

This crew identifies and assesses various types of business and financial risks.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import MergedContext, RiskSignalsOutput
from ...utils.llm import LLMFactory


@CrewBase
class RiskSignalsCrew:
    """
    Risk Signals Crew (N3c) for comprehensive risk assessment.
    
    Identifies financial, regulatory, market, and operational risks
    that could impact business performance.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def financial_risk_analyst(self) -> Agent:
        """
        Analyst that identifies financial risks and vulnerabilities.
        """
        return Agent(
            config=self.agents_config['financial_risk_analyst'],
            llm=LLMFactory.get_risk_signals_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def regulatory_compliance_expert(self) -> Agent:
        """
        Expert that assesses regulatory and compliance risks.
        """
        return Agent(
            config=self.agents_config['regulatory_compliance_expert'],
            llm=LLMFactory.get_risk_signals_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def market_risk_specialist(self) -> Agent:
        """
        Specialist that evaluates market and operational risks.
        """
        return Agent(
            config=self.agents_config['market_risk_specialist'],
            llm=LLMFactory.get_risk_signals_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def financial_risk_assessment_task(self) -> Task:
        """
        Task to assess financial risks and early warning indicators.
        """
        return Task(
            config=self.tasks_config['financial_risk_assessment_task'],
            agent=self.financial_risk_analyst()
        )
    
    @task
    def regulatory_risk_evaluation_task(self) -> Task:
        """
        Task to evaluate regulatory compliance and legal risks.
        """
        return Task(
            config=self.tasks_config['regulatory_risk_evaluation_task'],
            agent=self.regulatory_compliance_expert()
        )
    
    @task
    def market_operational_risk_task(self) -> Task:
        """
        Task to assess market and operational risk factors.
        """
        return Task(
            config=self.tasks_config['market_operational_risk_task'],
            agent=self.market_risk_specialist()
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
    
    def assess_risk_signals(self, merged_context: MergedContext, company_id: str) -> RiskSignalsOutput:
        """
        Assess comprehensive risk signals for the company.
        
        Args:
            merged_context: Merged context from N2
            company_id: Company identifier
            
        Returns:
            RiskSignalsOutput with comprehensive risk assessment
        """
        # Mock implementation - in production would use actual risk analysis
        mock_risks = {
            "financial_risks": [
                {"type": "Liquidity Risk", "level": "Medium", "description": "Cash flow seasonality could impact short-term liquidity"},
                {"type": "Credit Risk", "level": "Low", "description": "Strong debt service coverage and low leverage"}
            ],
            "regulatory_risks": [
                {"type": "Compliance Risk", "level": "Low", "description": "Good compliance track record with minor gaps"},
                {"type": "Regulatory Change", "level": "Medium", "description": "Upcoming regulatory changes may increase compliance costs"}
            ],
            "market_risks": [
                {"type": "Market Volatility", "level": "High", "description": "Industry facing significant market volatility"},
                {"type": "Competitive Risk", "level": "Medium", "description": "New competitors entering market"}
            ],
            "operational_risks": [
                {"type": "Supply Chain", "level": "Medium", "description": "Dependency on key suppliers creates vulnerability"},
                {"type": "Technology Risk", "level": "Low", "description": "Systems are robust but require ongoing investment"}
            ]
        }
        
        # Calculate overall risk score
        risk_levels = {"Low": 1, "Medium": 2, "High": 3}
        total_score = 0
        total_risks = 0
        
        for category in mock_risks.values():
            for risk in category:
                total_score += risk_levels[risk["level"]]
                total_risks += 1
        
        overall_risk_level = "Low" if total_score/total_risks < 1.5 else "Medium" if total_score/total_risks < 2.5 else "High"
        
        return RiskSignalsOutput(
            identified_risks=mock_risks,
            risk_prioritization=[
                "Market Volatility (High)",
                "Regulatory Changes (Medium)", 
                "Supply Chain Dependencies (Medium)",
                "Liquidity Seasonality (Medium)"
            ],
            mitigation_recommendations=[
                "Diversify supplier base to reduce supply chain risk",
                "Build cash reserves to handle market volatility",
                "Implement compliance monitoring for regulatory changes",
                "Develop contingency plans for liquidity management"
            ],
            overall_risk_level=overall_risk_level
        )


def create_risk_signals_crew() -> RiskSignalsCrew:
    """Factory function to create a risk signals crew instance."""
    return RiskSignalsCrew()
