#!/usr/bin/env python
"""
FinSights Multi-Agent System Main Entry Point.

This module provides the main interface for the FinSights financial analysis
multi-agent system, including both the new multi-agent pipeline and the
legacy poem generation functionality.
"""

import asyncio
from typing import Dict, Any, Optional

from .models.contracts import UserQuery
from .flow import build_flow, run_analysis
from .orchestrator import create_orchestrator, analyze_company_sync


def run_financial_analysis(
    query: str,
    company_id: str,
    output_type: str = "api",
    opts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run financial analysis using the multi-agent system.
    
    Args:
        query: Analysis query (e.g., "Generate quarterly financial report")
        company_id: Company identifier
        output_type: Output type ("api", "complete", "executive")
        opts: Optional parameters (date ranges, preferences, etc.)
        
    Returns:
        Analysis results
        
    Example:
        >>> result = run_financial_analysis(
        ...     "Analyze Q2 2025 financial performance and risks",
        ...     "company_abc",
        ...     "api"
        ... )
        >>> print(result["data"]["executive_summary"]["summary"])
    """
    try:
        result = analyze_company_sync(query, company_id, opts)
        print(f"✅ Analysis completed for {company_id}")
        return result
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "company_id": company_id
        }


def run_flow_demo():
    """
    Run a demonstration of the new CrewAI Flow system.
    """
    print("🚀 FinSights CrewAI Flow Demo")
    print("=" * 50)
    
    # Demo query
    demo_query = "Generate comprehensive financial analysis including KPIs, peer comparison, and risk assessment"
    demo_company = "demo_company_001"
    demo_opts = {
        "date_range": {
            "from": "2025-01-01",
            "to": "2025-06-30"
        },
        "include_peers": True,
        "focus_area": "comprehensive"
    }
    
    print(f"📊 Analyzing: {demo_company}")
    print(f"🔍 Query: {demo_query}")
    print(f"⚙️  Options: {demo_opts}")
    print()
    
    try:
        # Run analysis using the new flow
        result = run_analysis(
            demo_query,
            demo_company,
            **demo_opts
        )
        
        if result["status"] == "success":
            print("📈 Analysis Results Summary:")
            print("-" * 30)
            
            final_report = result.get("final_report", {})
            
            print(f"Company: {final_report.get('company_id', 'N/A')}")
            print(f"Session: {final_report.get('session_id', 'N/A')}")
            print(f"Generated: {final_report.get('generated_at', 'N/A')}")
            print(f"KPIs Extracted: {final_report.get('kpis_count', 0)}")
            print()
            
            if final_report.get("executive_summary"):
                print("📋 Executive Summary:")
                print(final_report["executive_summary"][:200] + "...")
                print()
            
            if final_report.get("key_takeaways"):
                print("🔑 Key Takeaways:")
                for takeaway in final_report["key_takeaways"][:3]:
                    print(f"  • {takeaway}")
            
        else:
            print(f"❌ Demo failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Flow demo failed: {str(e)}")


def run_orchestrator_demo():
    """
    Run a demonstration of the legacy multi-agent orchestrator.
    """
    print("🚀 FinSights Legacy Orchestrator Demo")
    print("=" * 50)
    
    # Demo query
    demo_query = "Generate comprehensive financial analysis including KPIs, peer comparison, and risk assessment"
    demo_company = "demo_company_001"
    demo_opts = {
        "date_range": {
            "from": "2025-01-01",
            "to": "2025-06-30"
        },
        "include_peers": True,
        "focus_area": "comprehensive"
    }
    
    print(f"📊 Analyzing: {demo_company}")
    print(f"🔍 Query: {demo_query}")
    print(f"⚙️  Options: {demo_opts}")
    print()
    
    # Run analysis
    result = run_financial_analysis(
        demo_query,
        demo_company,
        "api",
        demo_opts
    )
    
    if result["status"] == "success":
        print("📈 Analysis Results Summary:")
        print("-" * 30)
        
        data = result.get("data", {})
        metadata = data.get("metadata", {})
        summary_stats = data.get("summary_statistics", {})
        
        print(f"Company: {metadata.get('company_id', 'N/A')}")
        print(f"Generated: {metadata.get('generated_at', 'N/A')}")
        print(f"KPIs Extracted: {summary_stats.get('data_coverage', {}).get('total_kpis', 0)}")
        print(f"Peer Comparisons: {summary_stats.get('data_coverage', {}).get('peer_comparisons', 0)}")
        print(f"Risk Signals: {summary_stats.get('data_coverage', {}).get('risk_signals', 0)}")
        print()
        
        exec_summary = data.get("executive_summary", {})
        if exec_summary.get("summary"):
            print("📋 Executive Summary:")
            print(exec_summary["summary"][:200] + "...")
            print()
        
        if exec_summary.get("key_takeaways"):
            print("🔑 Key Takeaways:")
            for takeaway in exec_summary["key_takeaways"][:3]:
                print(f"  • {takeaway}")
        
    else:
        print(f"❌ Demo failed: {result.get('error', 'Unknown error')}")


# Legacy poem functionality for backward compatibility
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

try:
    from finsight.crews.poem_crew.poem_crew import PoemCrew
    
    class PoemState(BaseModel):
        sentence_count: int = 1
        poem: str = ""

    class PoemFlow(Flow[PoemState]):

        @start()
        def generate_sentence_count(self):
            print("Generating sentence count")
            self.state.sentence_count = randint(1, 5)

        @listen(generate_sentence_count)
        def generate_poem(self):
            print("Generating poem")
            result = (
                PoemCrew()
                .crew()
                .kickoff(inputs={"sentence_count": self.state.sentence_count})
            )

            print("Poem generated", result.raw)
            self.state.poem = result.raw

        @listen(generate_poem)
        def save_poem(self):
            print("Saving poem")
            with open("poem.txt", "w") as f:
                f.write(self.state.poem)

    def kickoff_poem():
        """Legacy poem generation function."""
        poem_flow = PoemFlow()
        poem_flow.kickoff()

    def plot_poem():
        """Legacy poem flow plotting function."""
        poem_flow = PoemFlow()
        poem_flow.plot()

except ImportError:
    print("⚠️  Legacy poem crew not available")
    
    def kickoff_poem():
        print("❌ Poem crew not available")
    
    def plot_poem():
        print("❌ Poem crew not available")


def main():
    """Main entry point - run the financial analysis demo."""
    print("🏦 FinSights - Financial Analysis AI System")
    print("=" * 50)
    print()
    print("Available functions:")
    print("1. run_flow_demo() - Run NEW CrewAI Flow demo")
    print("2. run_orchestrator_demo() - Run legacy orchestrator demo")
    print("3. run_financial_analysis() - Run custom analysis")
    print("4. kickoff_poem() - Legacy poem generation")
    print()
    
    # Run the new flow demo by default
    run_flow_demo()


if __name__ == "__main__":
    main()
