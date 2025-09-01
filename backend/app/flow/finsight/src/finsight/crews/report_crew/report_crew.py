"""
Report Generation Crew (N5) for Report Generation Layer.

This crew generates comprehensive reports and structured outputs from synthesized insights.
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
from ...models.contracts import SynthesisOutput, ReportOutput
from ...utils.llm import LLMFactory
from datetime import datetime


@CrewBase
class ReportCrew:
    """
    Report Generation Crew (N5) for comprehensive report creation.
    
    Generates executive reports, technical appendices, and structured
    data outputs from synthesized analytical insights.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def executive_report_writer(self) -> Agent:
        """
        Writer that creates executive-level financial reports.
        """
        return Agent(
            config=self.agents_config['executive_report_writer'],
            llm=LLMFactory.get_report_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def technical_appendix_specialist(self) -> Agent:
        """
        Specialist that creates technical documentation and appendices.
        """
        return Agent(
            config=self.agents_config['technical_appendix_specialist'],
            llm=LLMFactory.get_report_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def structured_data_formatter(self) -> Agent:
        """
        Formatter that creates structured data outputs and schemas.
        """
        return Agent(
            config=self.agents_config['structured_data_formatter'],
            llm=LLMFactory.get_report_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def executive_report_generation_task(self) -> Task:
        """
        Task to generate executive-level financial report.
        """
        return Task(
            config=self.tasks_config['executive_report_generation_task'],
            agent=self.executive_report_writer()
        )
    
    @task
    def technical_appendix_creation_task(self) -> Task:
        """
        Task to create technical appendix and supporting documentation.
        """
        return Task(
            config=self.tasks_config['technical_appendix_creation_task'],
            agent=self.technical_appendix_specialist()
        )
    
    @task
    def structured_output_formatting_task(self) -> Task:
        """
        Task to format outputs into structured data formats.
        """
        return Task(
            config=self.tasks_config['structured_output_formatting_task'],
            agent=self.structured_data_formatter()
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
    
    def generate_comprehensive_report(self, synthesis_output: SynthesisOutput, company_id: str) -> ReportOutput:
        """
        Generate comprehensive report package from synthesized insights.
        
        Args:
            synthesis_output: Synthesized insights from N4
            company_id: Company identifier
            
        Returns:
            ReportOutput with complete report package
        """
        # Mock implementation - in production would generate actual reports
        current_time = datetime.now().isoformat()
        
        mock_executive_report = {
            "title": f"Financial Analysis Report - {company_id}",
            "generated_at": current_time,
            "executive_summary": synthesis_output.executive_summary,
            "key_findings": synthesis_output.key_findings,
            "recommendations": synthesis_output.actionable_recommendations,
            "sections": {
                "financial_performance": "Strong financial metrics with consistent growth trajectory",
                "market_analysis": "Competitive position above industry average with identified opportunities",
                "risk_assessment": "Moderate risk profile with clear mitigation strategies",
                "strategic_outlook": "Positive outlook with recommended strategic initiatives"
            }
        }
        
        mock_technical_appendix = {
            "methodology": "Comprehensive multi-agent analysis using hybrid RAG and structured knowledge graphs",
            "data_sources": ["Company financial statements", "Industry benchmarks", "Market data"],
            "analytical_frameworks": ["Financial ratio analysis", "Peer comparison", "Risk assessment"],
            "quality_metrics": synthesis_output.confidence_metrics,
            "calculations": {
                "kpi_calculations": "Detailed financial ratio calculations and trend analysis",
                "peer_comparisons": "Statistical comparison against industry peer group",
                "risk_scoring": "Quantitative risk assessment using established frameworks"
            },
            "limitations": ["Analysis based on available historical data", "Market assumptions subject to change"],
            "validation": "Multi-layer validation including fact-checking and conflict resolution"
        }
        
        mock_structured_data = {
            "analysis_metadata": {
                "company_id": company_id,
                "analysis_date": current_time,
                "analysis_type": "comprehensive_financial_analysis",
                "version": "1.0"
            },
            "financial_metrics": {
                "revenue_growth": 15.2,
                "profit_margin": 18.5,
                "debt_ratio": 0.35,
                "liquidity_ratio": 2.1
            },
            "peer_rankings": {
                "revenue_growth_percentile": 75,
                "profitability_percentile": 68,
                "debt_management_percentile": 25
            },
            "risk_scores": {
                "financial_risk": "Low",
                "market_risk": "Medium", 
                "operational_risk": "Low",
                "overall_risk": "Medium"
            },
            "recommendations_prioritized": [
                {"priority": 1, "category": "Growth", "action": "Market expansion"},
                {"priority": 2, "category": "Risk", "action": "Supply chain diversification"},
                {"priority": 3, "category": "Efficiency", "action": "Operational optimization"}
            ]
        }
        
        return ReportOutput(
            executive_report=mock_executive_report,
            technical_appendix=mock_technical_appendix,
            structured_data=mock_structured_data,
            report_metadata={
                "generation_timestamp": current_time,
                "company_id": company_id,
                "report_type": "comprehensive_financial_analysis",
                "quality_score": 0.92,
                "confidence_level": "High"
            }
        )


def create_report_crew() -> ReportCrew:
    """Factory function to create a report crew instance."""
    return ReportCrew()
