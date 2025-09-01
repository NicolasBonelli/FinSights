"""
LLM Factory for FinSights Multi-Agent System.

This module provides centralized LLM model selection and configuration 
for different types of agents using Azure OpenAI with model-specific endpoints.
"""

from typing import Optional, Dict, Any
from openai import AzureOpenAI
from crewai import LLM
import sys
import os

# Add the project root to the path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from core.config import get_settings


class LLMFactory:
    """
    Factory class for managing Azure OpenAI LLM instances with model-specific endpoints.
    
    Each model has its own Azure endpoint for optimal performance and cost management.
    """
    
    # Model constants for easy maintenance (Azure deployment names)
    GPT_4O = "gpt-4o"
    GPT_4 = "gpt-4" 
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_35_TURBO = "gpt-35-turbo"
    
    @classmethod
    def _get_settings(cls):
        """Get application settings"""
        return get_settings()
    
    @classmethod
    def get_gpt4(cls) -> LLM:
        """
        Get GPT-4 Azure OpenAI LLM instance.
        
        Returns:
            LLM: CrewAI LLM instance configured for GPT-4
        """
        settings = cls._get_settings()
        return LLM(
            model=f"azure/{cls.GPT_4}",
            api_key=settings.openai_api_key,
            api_version=settings.azure_openai_api_version,
            base_url=settings.azure_gpt4_endpoint,
            temperature=0
        )
    
    @classmethod
    def get_gpt4o(cls) -> LLM:
        """
        Get GPT-4o Azure OpenAI LLM instance.
        
        Returns:
            LLM: CrewAI LLM instance configured for GPT-4o
        """
        settings = cls._get_settings()
        return LLM(
            model=f"azure/{cls.GPT_4O}",
            api_key=settings.openai_api_key,
            api_version=settings.azure_openai_api_version,
            base_url=settings.azure_gpt4o_endpoint,
            temperature=0
        )
    
    @classmethod
    def get_gpt4o_mini(cls) -> LLM:
        """
        Get GPT-4o-mini Azure OpenAI LLM instance.
        
        Returns:
            LLM: CrewAI LLM instance configured for GPT-4o-mini
        """
        settings = cls._get_settings()
        return LLM(
            model=f"azure/{cls.GPT_4O_MINI}",
            api_key=settings.openai_api_key,
            api_version=settings.azure_openai_api_version,
            base_url=settings.azure_gpt4o_mini_endpoint,
            temperature=0
        )
    
    @classmethod
    def get_gpt35_turbo(cls) -> LLM:
        """
        Get GPT-3.5-turbo Azure OpenAI LLM instance.
        
        Returns:
            LLM: CrewAI LLM instance configured for GPT-3.5-turbo
        """
        settings = cls._get_settings()
        return LLM(
            model=f"azure/{cls.GPT_35_TURBO}",
            api_key=settings.openai_api_key,
            api_version=settings.azure_openai_api_version,
            base_url=settings.azure_gpt35_turbo_endpoint,
            temperature=0
        )
    
    @classmethod
    def get_router_llm(cls) -> LLM:
        """
        LLM for Router crew agents (Intent Classifier, Policy Guard, Scope Refiner).
        
        Uses GPT-3.5-turbo for cost efficiency since these agents perform:
        - Simple classification tasks
        - Rule-based policy validation  
        - Basic query refinement
        
        Returns:
            LLM: CrewAI LLM instance for router agents
        """
        return cls.get_gpt35_turbo()
    
    @classmethod
    def get_hybrid_rag_llm(cls) -> LLM:
        """
        LLM for Hybrid RAG agent.
        
        Uses GPT-4o for:
        - Large context window needed for processing multiple retrieved chunks
        - Better understanding of financial document semantics
        - Superior reasoning for relevance scoring and context synthesis
        
        Returns:
            LLM: CrewAI LLM instance for hybrid RAG agent
        """
        return cls.get_gpt4o()
    
    @classmethod
    def get_relations_rag_llm(cls) -> LLM:
        """
        LLM for Relations RAG agent.
        
        Uses GPT-4 for:
        - Complex relationship understanding from knowledge graphs
        - Large context for processing structured entity relationships
        - Advanced reasoning for connection inference
        
        Returns:
            LLM: CrewAI LLM instance for relations RAG agent
        """
        return cls.get_gpt4()
    
    @classmethod
    def get_finance_kpis_llm(cls) -> LLM:
        """
        LLM for Finance KPIs crew agents.
        
        Uses GPT-4o-mini for:
        - Balanced cost and analytical capability
        - Financial ratio calculations and trend analysis
        - Good performance on structured financial data
        
        Returns:
            LLM: CrewAI LLM instance for finance KPIs agents
        """
        return cls.get_gpt4o_mini()
    
    @classmethod
    def get_market_peers_llm(cls) -> LLM:
        """
        LLM for Market Peers crew agents.
        
        Uses GPT-4o-mini for:
        - Comparative analysis tasks
        - Benchmark research and peer identification
        - Cost-effective for data-driven analysis
        
        Returns:
            LLM: CrewAI LLM instance for market peers agents
        """
        return cls.get_gpt4o_mini()
    
    @classmethod
    def get_risk_signals_llm(cls) -> LLM:
        """
        LLM for Risk Signals crew agents.
        
        Uses GPT-4o-mini for:
        - Risk pattern recognition
        - Financial stress indicator analysis
        - Good balance of speed and analytical reasoning
        
        Returns:
            LLM: CrewAI LLM instance for risk signals agents
        """
        return cls.get_gpt4o_mini()
    
    @classmethod
    def get_synthesis_llm(cls) -> LLM:
        """
        LLM for Synthesis & QA crew agents.
        
        Uses GPT-4o for:
        - Superior reasoning for conflict resolution
        - High-quality narrative synthesis
        - Fact-checking and quality assurance tasks
        - Executive-level communication coherence
        
        Returns:
            LLM: CrewAI LLM instance for synthesis agents
        """
        return cls.get_gpt4o()
    
    @classmethod
    def get_report_llm(cls) -> LLM:
        """
        LLM for Report Generation crew agents.
        
        Uses GPT-3.5-turbo for:
        - Structured output formatting
        - Template-based report generation
        - Schema emission and data transformation
        - Cost efficiency for formatting tasks
        
        Returns:
            LLM: CrewAI LLM instance for report generation agents
        """
        return cls.get_gpt35_turbo()
    
    @classmethod
    def get_llm_config(cls, agent_type: str, **kwargs) -> LLM:
        """
        Get complete LLM configuration for an agent type.
        
        This method returns a configured CrewAI LLM instance.
        
        Args:
            agent_type: Type of agent (e.g., 'router', 'hybrid_rag', 'finance_kpis')
            **kwargs: Additional configuration parameters
            
        Returns:
            LLM: Configured CrewAI LLM instance
        """
        # Agent type to method mapping
        agent_methods = {
            'router': cls.get_router_llm,
            'hybrid_rag': cls.get_hybrid_rag_llm,
            'relations_rag': cls.get_relations_rag_llm,
            'finance_kpis': cls.get_finance_kpis_llm,
            'market_peers': cls.get_market_peers_llm,
            'risk_signals': cls.get_risk_signals_llm,
            'synthesis': cls.get_synthesis_llm,
            'report': cls.get_report_llm
        }
        
        # Get the base LLM instance
        method = agent_methods.get(agent_type, cls.get_finance_kpis_llm)
        llm = method()
        
        # Apply any additional configuration if needed
        if kwargs:
            # Note: CrewAI LLM instances are immutable, so we return the base instance
            # Additional configuration would need to be handled at the agent level
            pass
            
        return llm
    
    @classmethod
    def get_all_models(cls) -> Dict[str, str]:
        """
        Get a mapping of all agent types to their assigned models.
        
        Useful for debugging, cost analysis, and configuration validation.
        
        Returns:
            Dict[str, str]: Mapping of agent types to model names
        """
        return {
            'router': cls.get_router_llm().model,
            'hybrid_rag': cls.get_hybrid_rag_llm().model,
            'relations_rag': cls.get_relations_rag_llm().model,
            'finance_kpis': cls.get_finance_kpis_llm().model,
            'market_peers': cls.get_market_peers_llm().model,
            'risk_signals': cls.get_risk_signals_llm().model,
            'synthesis': cls.get_synthesis_llm().model,
            'report': cls.get_report_llm().model
        }
    
    @classmethod
    def estimate_cost_distribution(cls) -> Dict[str, Dict[str, Any]]:
        """
        Estimate relative cost distribution across different model types.
        
        This helps understand cost implications of the current model selection.
        
        Returns:
            Dict[str, Dict[str, Any]]: Cost analysis by model type
        """
        # Relative cost multipliers (GPT-3.5-turbo as baseline = 1.0)
        cost_multipliers = {
            cls.GPT_35_TURBO: 1.0,
            cls.GPT_4O_MINI: 2.5,
            cls.GPT_4: 10.0,
            cls.GPT_4O: 8.0
        }
        
        model_usage = cls.get_all_models()
        cost_analysis = {}
        
        for agent_type, model in model_usage.items():
            cost_analysis[agent_type] = {
                'model': model,
                'relative_cost': cost_multipliers.get(model, 5.0),
                'usage_pattern': 'High' if agent_type in ['synthesis', 'hybrid_rag'] else 'Medium'
            }
            
        return cost_analysis
