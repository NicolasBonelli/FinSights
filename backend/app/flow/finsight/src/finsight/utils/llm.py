"""
LLM Factory for FinSights Multi-Agent System.

This module provides centralized LLM model selection and configuration 
for different types of agents based on their computational requirements
and cost optimization strategy.
"""

from typing import Optional, Dict, Any


class LLMFactory:
    """
    Factory class for managing LLM selection and configuration across different agent types.
    
    Optimization Strategy:
    - RAG Agents: Use GPT-4/GPT-4o for large context windows and better retrieval reasoning
    - Router Agents: Use GPT-3.5-turbo for cost efficiency on simple classification tasks  
    - Analytical Agents: Use GPT-4o-mini for balanced speed and analytical reasoning
    - Synthesis Agents: Use GPT-4o for superior reasoning and narrative consistency
    - Report Agents: Use GPT-3.5-turbo for formatting and structured output tasks
    """
    
    # Model constants for easy maintenance
    GPT_4O = "gpt-4o"
    GPT_4 = "gpt-4" 
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    @staticmethod
    def get_router_llm() -> str:
        """
        LLM for Router crew agents (Intent Classifier, Policy Guard, Scope Refiner).
        
        Uses GPT-3.5-turbo for cost efficiency since these agents perform:
        - Simple classification tasks
        - Rule-based policy validation  
        - Basic query refinement
        
        Returns:
            str: Model name for router agents
        """
        return LLMFactory.GPT_35_TURBO
    
    @staticmethod
    def get_hybrid_rag_llm() -> str:
        """
        LLM for Hybrid RAG agent.
        
        Uses GPT-4o for:
        - Large context window needed for processing multiple retrieved chunks
        - Better understanding of financial document semantics
        - Superior reasoning for relevance scoring and context synthesis
        
        Returns:
            str: Model name for hybrid RAG agent
        """
        return LLMFactory.GPT_4O
    
    @staticmethod
    def get_relations_rag_llm() -> str:
        """
        LLM for Relations RAG agent.
        
        Uses GPT-4 for:
        - Complex relationship understanding from knowledge graphs
        - Large context for processing structured entity relationships
        - Advanced reasoning for connection inference
        
        Returns:
            str: Model name for relations RAG agent
        """
        return LLMFactory.GPT_4
    
    @staticmethod
    def get_finance_kpis_llm() -> str:
        """
        LLM for Finance KPIs crew agents.
        
        Uses GPT-4o-mini for:
        - Balanced cost and analytical capability
        - Financial ratio calculations and trend analysis
        - Good performance on structured financial data
        
        Returns:
            str: Model name for finance KPIs agents
        """
        return LLMFactory.GPT_4O_MINI
    
    @staticmethod
    def get_market_peers_llm() -> str:
        """
        LLM for Market Peers crew agents.
        
        Uses GPT-4o-mini for:
        - Comparative analysis tasks
        - Benchmark research and peer identification
        - Cost-effective for data-driven analysis
        
        Returns:
            str: Model name for market peers agents
        """
        return LLMFactory.GPT_4O_MINI
    
    @staticmethod
    def get_risk_signals_llm() -> str:
        """
        LLM for Risk Signals crew agents.
        
        Uses GPT-4o-mini for:
        - Risk pattern recognition
        - Financial stress indicator analysis
        - Good balance of speed and analytical reasoning
        
        Returns:
            str: Model name for risk signals agents
        """
        return LLMFactory.GPT_4O_MINI
    
    @staticmethod
    def get_synthesis_llm() -> str:
        """
        LLM for Synthesis & QA crew agents.
        
        Uses GPT-4o for:
        - Superior reasoning for conflict resolution
        - High-quality narrative synthesis
        - Fact-checking and quality assurance tasks
        - Executive-level communication coherence
        
        Returns:
            str: Model name for synthesis agents
        """
        return LLMFactory.GPT_4O
    
    @staticmethod
    def get_report_llm() -> str:
        """
        LLM for Report Generation crew agents.
        
        Uses GPT-3.5-turbo for:
        - Structured output formatting
        - Template-based report generation
        - Schema emission and data transformation
        - Cost efficiency for formatting tasks
        
        Returns:
            str: Model name for report generation agents
        """
        return LLMFactory.GPT_35_TURBO
    
    @staticmethod
    def get_llm_config(agent_type: str, **kwargs) -> Dict[str, Any]:
        """
        Get complete LLM configuration for an agent type.
        
        This method can be extended to include additional parameters like
        temperature, max_tokens, timeout, etc.
        
        Args:
            agent_type: Type of agent (e.g., 'router', 'hybrid_rag', 'finance_kpis')
            **kwargs: Additional configuration parameters
            
        Returns:
            Dict[str, Any]: Complete LLM configuration
        """
        # Model selection mapping
        model_map = {
            'router': LLMFactory.get_router_llm(),
            'hybrid_rag': LLMFactory.get_hybrid_rag_llm(),
            'relations_rag': LLMFactory.get_relations_rag_llm(),
            'finance_kpis': LLMFactory.get_finance_kpis_llm(),
            'market_peers': LLMFactory.get_market_peers_llm(),
            'risk_signals': LLMFactory.get_risk_signals_llm(),
            'synthesis': LLMFactory.get_synthesis_llm(),
            'report': LLMFactory.get_report_llm()
        }
        
        model = model_map.get(agent_type, LLMFactory.GPT_4O_MINI)
        
        # Base configuration
        config = {
            'model': model,
            'temperature': kwargs.get('temperature', 0.1),  # Low for consistency
            'max_tokens': kwargs.get('max_tokens', None),   # Use model defaults
            'timeout': kwargs.get('timeout', 30),          # 30 second timeout
        }
        
        # Model-specific optimizations
        if model in [LLMFactory.GPT_4O, LLMFactory.GPT_4]:
            config['temperature'] = kwargs.get('temperature', 0.2)  # Slightly higher for reasoning
        elif model == LLMFactory.GPT_35_TURBO:
            config['temperature'] = kwargs.get('temperature', 0.0)  # Very low for structured tasks
            
        return config
    
    @staticmethod
    def get_all_models() -> Dict[str, str]:
        """
        Get a mapping of all agent types to their assigned models.
        
        Useful for debugging, cost analysis, and configuration validation.
        
        Returns:
            Dict[str, str]: Mapping of agent types to model names
        """
        return {
            'router': LLMFactory.get_router_llm(),
            'hybrid_rag': LLMFactory.get_hybrid_rag_llm(),
            'relations_rag': LLMFactory.get_relations_rag_llm(),
            'finance_kpis': LLMFactory.get_finance_kpis_llm(),
            'market_peers': LLMFactory.get_market_peers_llm(),
            'risk_signals': LLMFactory.get_risk_signals_llm(),
            'synthesis': LLMFactory.get_synthesis_llm(),
            'report': LLMFactory.get_report_llm()
        }
    
    @staticmethod
    def estimate_cost_distribution() -> Dict[str, Dict[str, Any]]:
        """
        Estimate relative cost distribution across different model types.
        
        This helps understand cost implications of the current model selection.
        
        Returns:
            Dict[str, Dict[str, Any]]: Cost analysis by model type
        """
        # Relative cost multipliers (GPT-3.5-turbo as baseline = 1.0)
        cost_multipliers = {
            LLMFactory.GPT_35_TURBO: 1.0,
            LLMFactory.GPT_4O_MINI: 2.5,
            LLMFactory.GPT_4: 10.0,
            LLMFactory.GPT_4O: 8.0
        }
        
        model_usage = LLMFactory.get_all_models()
        cost_analysis = {}
        
        for agent_type, model in model_usage.items():
            cost_analysis[agent_type] = {
                'model': model,
                'relative_cost': cost_multipliers.get(model, 5.0),
                'usage_pattern': 'High' if agent_type in ['synthesis', 'hybrid_rag'] else 'Medium'
            }
            
        return cost_analysis
