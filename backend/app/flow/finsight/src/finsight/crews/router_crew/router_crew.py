"""
Router Crew for intent classification, policy validation, and scope refinement.

This crew handles the initial processing of user queries (N1 in the flow).
"""

from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, Any
from datetime import datetime, date, timedelta
from ...models.contracts import UserQuery, RoutingPlan, TimeScope, QueryConstraints, RoutingConfig
from ...utils.llm import LLMFactory


@CrewBase
class RouterCrew:
    """
    Router Crew (N1) - Intent classification, policy validation, and scope refinement.
    """
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def intent_classifier(self) -> Agent:
        return Agent(
            config=self.agents_config['intent_classifier'],
            llm=LLMFactory.get_router_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def policy_guard(self) -> Agent:
        return Agent(
            config=self.agents_config['policy_guard'],
            llm=LLMFactory.get_router_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def scope_refiner(self) -> Agent:
        return Agent(
            config=self.agents_config['scope_refiner'],
            llm=LLMFactory.get_router_llm(),
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def classify_intent_task(self) -> Task:
        return Task(
            config=self.tasks_config['classify_intent_task'],
            agent=self.intent_classifier()
        )
    
    @task
    def validate_policy_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_policy_task'],
            agent=self.policy_guard()
        )
    
    @task
    def refine_scope_task(self) -> Task:
        return Task(
            config=self.tasks_config['refine_scope_task'],
            agent=self.scope_refiner()
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the crew with all agents and tasks."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process="sequential"  # These tasks must run in sequence
        )
    
    def _classify_intent(self, user_query: UserQuery) -> Dict[str, Any]:
        """Classify user intent and determine analysis targets."""
        query_lower = user_query.query.lower()
        targets = []
        
        # Simple keyword-based classification (placeholder)
        if any(keyword in query_lower for keyword in ['kpi', 'metrics', 'financial', 'revenue', 'ebitda']):
            targets.append('kpi')
        
        if any(keyword in query_lower for keyword in ['peer', 'competitor', 'benchmark', 'market']):
            targets.append('peers')
            
        if any(keyword in query_lower for keyword in ['risk', 'threat', 'warning', 'danger', 'alert']):
            targets.append('risk')
            
        if any(keyword in query_lower for keyword in ['comprehensive', 'full', 'complete', 'overall']):
            targets = ['kpi', 'peers', 'risk']
            
        # Default to KPI and risk if no specific targets identified
        if not targets:
            targets = ['kpi', 'risk']
        
        return {
            'targets': targets,
            'confidence': 0.8,
            'reasoning': f"Detected intent for: {', '.join(targets)}"
        }
    
    def _validate_policy(self, user_query: UserQuery) -> Dict[str, Any]:
        """Validate user request against policies."""
        violations = []
        restrictions = []
        
        # Mock validation - in real implementation would check actual policies
        return {
            'valid': True,
            'violations': violations,
            'restrictions': restrictions,
            'confidentiality_level': 'internal'
        }
    
    def _infer_time_scope(self, query: str, opts: Dict[str, Any]) -> TimeScope:
        """Infer appropriate time scope for the analysis."""
        # Check if explicit date range provided in opts
        if 'date_range' in opts:
            date_range = opts['date_range']
            if isinstance(date_range, dict) and 'from' in date_range and 'to' in date_range:
                return TimeScope(
                    from_date=date_range['from'],
                    to_date=date_range['to']
                )
        
        # Default to last quarter
        today = date.today()
        quarter_start = date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
        if quarter_start > today:
            quarter_start = date(today.year - 1, 10, 1)
        quarter_end = quarter_start + timedelta(days=90)
        
        return TimeScope(
            from_date=quarter_start.strftime('%Y-%m-%d'),
            to_date=min(quarter_end, today).strftime('%Y-%m-%d')
        )
    
    def _refine_scope(self, user_query: UserQuery, targets: list, policy_result: Dict[str, Any]) -> RoutingPlan:
        """Refine the complete scope for the analysis."""
        
        # Normalize query
        normalized_query = user_query.query.strip()
        if not any(word in normalized_query.lower() for word in ['financial', 'finance', 'company']):
            normalized_query = f"Generate financial analysis for: {normalized_query}"
        
        # Infer time scope
        time_scope = self._infer_time_scope(user_query.query, user_query.opts)
        
        # Infer constraints
        constraints = QueryConstraints(
            currency=user_query.opts.get('currency', 'USD'),
            level_of_detail=user_query.opts.get('level_of_detail', 'exec')
        )
        
        # Infer routing config
        routing = RoutingConfig(
            use_hybrid_rag=user_query.opts.get('use_hybrid_rag', True),
            use_relations_rag=user_query.opts.get('use_relations_rag', True)
        )
        
        return RoutingPlan(
            normalized_query=normalized_query,
            targets=targets,
            time_scope=time_scope,
            constraints=constraints,
            routing=routing
        )
    
    def process_query(self, user_query: UserQuery) -> RoutingPlan:
        """
        Process a user query through the complete router pipeline.
        
        Args:
            user_query: The user's query and context
            
        Returns:
            RoutingPlan with normalized query and analysis configuration
        """
        # Step 1: Classify intent
        intent_result = self._classify_intent(user_query)
        targets = intent_result['targets']
        
        # Step 2: Validate policy
        policy_result = self._validate_policy(user_query)
        if not policy_result['valid']:
            raise ValueError(f"Policy validation failed: {policy_result['violations']}")
        
        # Step 3: Refine scope
        routing_plan = self._refine_scope(user_query, targets, policy_result)
        
        return routing_plan
    
    def kickoff(self, inputs: Dict[str, Any]) -> RoutingPlan:
        """
        Execute the router crew.
        
        Args:
            inputs: Dictionary containing 'user_query'
            
        Returns:
            RoutingPlan for the downstream crews
        """
        user_query = inputs['user_query']
        return self.process_query(user_query)


def create_router_crew() -> RouterCrew:
    """Factory function to create a router crew instance."""
    return RouterCrew()
