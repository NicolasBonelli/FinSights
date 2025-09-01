# FinSights Utils - LLM Factory

## Overview

The `LLMFactory` provides centralized LLM model selection and configuration for all agents in the FinSights multi-agent system. It optimizes for both cost efficiency and performance based on each agent's specific requirements.

## Model Selection Strategy

### 🚀 **High-Performance Models (GPT-4o, GPT-4)**
- **Hybrid RAG Agent**: GPT-4o - Large context window for multiple retrieved chunks
- **Relations RAG Agent**: GPT-4 - Complex relationship reasoning from knowledge graphs  
- **Synthesis Agents**: GPT-4o - Superior reasoning for narrative synthesis and conflict resolution

### ⚡ **Balanced Models (GPT-4o-mini)**
- **Finance KPIs Agents**: Cost-effective analytical reasoning
- **Market Peers Agents**: Comparative analysis and benchmarking
- **Risk Signals Agents**: Pattern recognition and risk assessment

### 💰 **Cost-Optimized Models (GPT-3.5-turbo)**
- **Router Agents**: Simple classification and validation tasks
- **Report Generation Agents**: Structured formatting and schema emission

## Usage Examples

### Basic Usage
```python
from utils.llm import LLMFactory
from crewai import Agent

# For a Finance KPIs agent
agent = Agent(
    config=self.agents_config['kpi_extractor'],
    llm=LLMFactory.get_finance_kpis_llm(),  # Returns "gpt-4o-mini"
    verbose=True,
    allow_delegation=False
)

# For a Synthesis agent
synthesis_agent = Agent(
    config=self.agents_config['synthesis_analyst'],
    llm=LLMFactory.get_synthesis_llm(),  # Returns "gpt-4o"
    verbose=True
)
```

### Advanced Configuration
```python
from utils.llm import LLMFactory

# Get complete configuration with custom parameters
config = LLMFactory.get_llm_config(
    agent_type='synthesis',
    temperature=0.3,
    max_tokens=2000,
    timeout=45
)

agent = Agent(
    config=self.agents_config['agent_name'],
    llm=config['model'],
    temperature=config['temperature'],
    verbose=True
)
```

### Cost Analysis
```python
from utils.llm import LLMFactory

# View all model assignments
models = LLMFactory.get_all_models()
print(models)
# Output:
# {
#     'router': 'gpt-3.5-turbo',
#     'hybrid_rag': 'gpt-4o',
#     'finance_kpis': 'gpt-4o-mini',
#     ...
# }

# Analyze cost distribution
cost_analysis = LLMFactory.estimate_cost_distribution()
print(cost_analysis)
```

## Integration Pattern for All Crews

### 1. Import the Factory
```python
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, crew, task
from ...utils.llm import LLMFactory
```

### 2. Apply to Agent Definitions
```python
@CrewBase
class YourCrew:
    @agent
    def your_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['your_agent'],
            llm=LLMFactory.get_appropriate_llm(),  # Choose the right method
            verbose=True,
            allow_delegation=False
        )
```

### 3. Method Mapping by Crew Type

| Crew Type | Method | Model | Rationale |
|-----------|--------|-------|-----------|
| Router Crew | `get_router_llm()` | gpt-3.5-turbo | Simple classification |
| Hybrid RAG Crew | `get_hybrid_rag_llm()` | gpt-4o | Large context + reasoning |
| Relations RAG Crew | `get_relations_rag_llm()` | gpt-4 | Complex relationships |
| Finance KPIs Crew | `get_finance_kpis_llm()` | gpt-4o-mini | Balanced analysis |
| Market Peers Crew | `get_market_peers_llm()` | gpt-4o-mini | Comparative analysis |
| Risk Signals Crew | `get_risk_signals_llm()` | gpt-4o-mini | Pattern recognition |
| Synthesis Crew | `get_synthesis_llm()` | gpt-4o | High-quality reasoning |
| Report Crew | `get_report_llm()` | gpt-3.5-turbo | Formatting tasks |

## Cost Optimization Benefits

1. **Router agents**: ~10x cost reduction using GPT-3.5-turbo vs GPT-4
2. **Analytical agents**: ~4x cost reduction using GPT-4o-mini vs GPT-4
3. **Report agents**: ~10x cost reduction using GPT-3.5-turbo vs GPT-4
4. **High-value tasks**: Full performance with GPT-4o for synthesis and complex RAG

## Future Extensions

The factory can be extended to support:
- Custom API endpoints
- Model fine-tuning configurations
- Dynamic model selection based on load
- A/B testing different models
- Cost budgeting and limits
