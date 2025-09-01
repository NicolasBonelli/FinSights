# FinSights Multi-Agent System Implementation

## Overview

This is the complete implementation of the FinSights multi-agent system for automated financial analysis and reporting. The system follows the design specified in `MULTI_AGENT_FLOW.md` and implements a sophisticated pipeline using **CrewAI Flows** that processes financial documents to generate comprehensive analysis reports.

## 🆕 NEW: CrewAI Flow Implementation

The system now uses **CrewAI Flows** for orchestration, providing:
- **Visual Flow Graphs**: Automatic visualization of the multi-agent pipeline
- **Declarative Flow Definition**: Clean, readable flow definitions with decorators
- **Built-in State Management**: Automatic state passing between flow steps
- **Parallel Execution**: Native support for parallel crew execution
- **Error Handling**: Robust error handling and flow recovery

## 🧹 Code Cleanup

**Removed Redundant Code**: The old `/agents/` folder has been eliminated to avoid duplication:
- ✅ **Crews Structure**: All agents now defined in `crews/` with YAML configurations
- ✅ **Single Source of Truth**: Agent definitions centralized in `agents.yaml` files
- ✅ **Simplified Maintenance**: No more dual implementations to maintain
- ✅ **CrewAI Best Practices**: Following official CrewAI patterns and conventions

## Architecture

The system implements a **5-node multi-agent pipeline**:

### N1: Router & Policy Gate
- **IntentClassifierAgent**: Classifies user queries and determines analysis targets
- **PolicyGuardAgent**: Validates access permissions and policy compliance
- **ScopeRefinerAgent**: Normalizes queries and infers missing parameters

### N2: Context Builder (Parallel)
- **HybridRAGCrew**: Retrieves context using BM25 + vector search
- **RelationsRAGCrew**: Extracts structured relations from LangExtract data
- **ContextMerger**: Merges and deduplicates context from both sources

### N3: Analytical Layer (Parallel)
- **FinanceKPIsCrew**: Extracts and validates financial KPIs
- **MarketPeersCrew**: Performs competitive benchmarking analysis
- **RiskSignalsCrew**: Identifies financial risks and anomalies

### N4: Synthesis & QA
- **SynthesisAgent**: Creates executive narrative from analysis results
- **ConflictResolverAgent**: Identifies and resolves data conflicts
- **FactCheckerAgent**: Validates citations and ensures traceability

### N5: Report Generation
- **ReportFormatterAgent**: Creates executive reports (HTML/PDF)
- **AppendixAgent**: Generates technical appendices and data exports
- **SchemaEmitterAgent**: Produces structured JSON for API consumption

## Directory Structure

```
src/finsight/
├── models/
│   └── contracts.py          # Pydantic data models and contracts
├── crews/                    # CrewAI Crews (NEW Structure)
│   ├── router_crew/          # N1 Router & Policy Gate
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   ├── __init__.py
│   │   └── router_crew.py
│   ├── hybrid_rag_crew/      # N2a Hybrid RAG
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   ├── __init__.py
│   │   └── hybrid_rag_crew.py
│   ├── relations_rag_crew/   # N2b Relations RAG
│   ├── finance_kpis_crew/    # N3a Finance KPIs
│   ├── market_peers_crew/    # N3b Market Peers
│   ├── risk_signals_crew/    # N3c Risk Signals
│   ├── synthesis_crew/       # N4 Synthesis & QA
│   └── report_crew/          # N5 Report Generation
├── flow.py                   # 🆕 Main CrewAI Flow orchestration
├── orchestrator.py           # Legacy orchestrator (updated to use crews/)
├── test_flow.py              # Flow testing utilities
└── main.py                   # Entry point and demos
```

## Data Contracts

The system uses Pydantic models for type safety and validation:

- **UserQuery**: Input query with company ID and options
- **RoutingPlan**: Router output with normalized query and targets
- **ContextItem/RelationItem**: Context retrieval results
- **KPIItem**: Financial KPI with sources and time series data
- **PeerComparison**: Competitive benchmarking results
- **RiskSignal**: Risk assessment with severity and evidence
- **Synthesis**: Executive summary with takeaways and limitations
- **ReportOutput**: Final structured report format

## Usage

### 🆕 NEW: CrewAI Flow Usage

```python
from finsight.flow import run_analysis

# Run financial analysis using CrewAI Flow
result = run_analysis(
    query="Generate Q2 2025 financial analysis with risk assessment",
    company_id="company_abc",
    date_range={"from": "2025-04-01", "to": "2025-06-30"},
    include_peers=True,
    focus_area="comprehensive"
)

print(result["final_report"]["executive_summary"])
```

### Advanced Flow Usage

```python
from finsight.flow import build_flow
from finsight.models.contracts import UserQuery

# Build the flow
flow = build_flow()

# Set up the query
user_query = UserQuery(
    query="Comprehensive financial analysis including KPIs, peers, and risks",
    company_id="company_xyz",
    opts={
        "focus_area": "comprehensive",
        "level_of_detail": "detailed"
    }
)

# Configure flow state
flow.state.user_query = user_query
flow.state.company_id = "company_xyz"

# Execute the flow
result = flow.kickoff()

# Access results
print(f"Session: {flow.state.session_id}")
print(f"Final Report: {flow.state.final_report}")
```

### Flow Visualization

```python
from finsight.flow import build_flow

# Build and visualize the flow
flow = build_flow()
flow.plot("finsights_flow_graph.png")
```

### Legacy Usage

```python
from finsight.main import run_financial_analysis

# Run using legacy orchestrator
result = run_financial_analysis(
    query="Generate Q2 2025 financial analysis with risk assessment",
    company_id="company_abc",
    output_type="api",
    opts={
        "date_range": {"from": "2025-04-01", "to": "2025-06-30"},
        "include_peers": True
    }
)
```

### Demos

Run the built-in demos:

```python
from finsight.main import run_flow_demo, run_orchestrator_demo

# NEW CrewAI Flow demo
run_flow_demo()

# Legacy orchestrator demo  
run_orchestrator_demo()
```

### Testing

```python
from finsight.test_flow import run_all_tests

# Run comprehensive test suite
success = run_all_tests()
```

## Output Formats

The system supports multiple output formats:

### API Response
Structured JSON suitable for web/mobile consumption:
```json
{
  "status": "success",
  "data": {
    "metadata": {...},
    "executive_summary": {...},
    "financial_metrics": {...},
    "market_position": {...},
    "risk_assessment": {...}
  }
}
```

### Complete Package
Full report package with:
- Executive report (HTML/PDF)
- Technical appendix with data tables
- CSV exports for all data
- Structured JSON

### Executive Summary
Condensed version with key insights only

## Key Features

### 🔄 Parallel Processing
- Context builders run in parallel
- Analytical crews execute simultaneously
- Optimized for performance

### 🛡️ Quality Assurance
- Conflict detection and resolution
- Comprehensive fact-checking
- Citation validation and traceability

### 📊 Comprehensive Analysis
- Financial KPI extraction and validation
- Time series analysis with QoQ/YoY calculations
- Competitive benchmarking
- Risk assessment with multiple detection methods

### 🎯 Flexible Output
- Multiple output formats (HTML, PDF, JSON, CSV)
- Configurable detail levels
- API-ready responses

### 🔍 Full Traceability
- Complete audit trail for all analysis
- Source document citations
- Evidence linking for all claims

## Configuration

The system includes configurable components:

- **Risk thresholds** in RiskPatternAgent
- **Policy limits** in PolicyGuardAgent
- **Peer databases** in PeerSelectorAgent
- **Output formats** in ReportFormatterAgent

## Current Implementation Status

✅ **Complete Skeleton Implementation**
- All 5 nodes implemented with proper structure
- Complete data contracts and type safety
- Full orchestrator with parallel execution
- Comprehensive error handling

🔄 **Mock Data & Placeholders**
- RAG tools use mock data (ElasticSearch integration pending)
- Peer data uses industry averages (external data pending)
- PDF generation placeholder (ReportLab integration pending)

## Next Steps

1. **RAG Integration**: Implement actual Elasticsearch hybrid search
2. **Data Sources**: Connect to real financial data APIs
3. **PDF Generation**: Implement ReportLab-based PDF creation
4. **Testing**: Add comprehensive unit and integration tests
5. **Deployment**: Configure for production environment

## Dependencies

The implementation uses:
- **CrewAI**: Multi-agent orchestration framework
- **Pydantic**: Data validation and serialization
- **asyncio**: Async/parallel execution
- **typing**: Type hints and safety

## Error Handling

The system includes robust error handling:
- Graceful degradation when crews fail
- Comprehensive logging and metrics
- Workflow state tracking for debugging
- Quality metrics and validation reporting

This implementation provides a solid foundation for the FinSights financial analysis system, with clear extension points for adding real data sources and advanced features.