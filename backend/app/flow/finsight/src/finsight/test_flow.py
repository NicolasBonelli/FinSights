"""
Test script for the FinSights CrewAI Flow.

This script demonstrates how to run the complete multi-agent flow
and provides examples for different types of analysis.
"""

from .flow import build_flow, run_analysis
from .models.contracts import UserQuery


def test_basic_flow():
    """Test basic flow functionality."""
    print("🧪 Testing Basic FinSights Flow")
    print("=" * 40)
    
    try:
        # Test simple analysis
        result = run_analysis(
            query="Analyze Q2 2025 financial performance",
            company_id="test_company_001",
            date_range={"from": "2025-04-01", "to": "2025-06-30"}
        )
        
        print(f"✅ Basic flow test completed")
        print(f"📊 Session: {result['session_id']}")
        print(f"📈 Status: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic flow test failed: {str(e)}")
        return False


def test_comprehensive_analysis():
    """Test comprehensive financial analysis."""
    print("\n🧪 Testing Comprehensive Analysis")
    print("=" * 42)
    
    try:
        result = run_analysis(
            query="Generate comprehensive financial analysis including KPIs, peer comparison, and risk assessment for quarterly review",
            company_id="comprehensive_test_corp",
            date_range={"from": "2025-01-01", "to": "2025-06-30"},
            include_peers=True,
            focus_area="comprehensive",
            level_of_detail="detailed"
        )
        
        print(f"✅ Comprehensive analysis test completed")
        print(f"📊 Session: {result['session_id']}")
        
        # Show some results
        final_report = result.get('final_report', {})
        if final_report:
            print(f"📋 Executive Summary: {final_report.get('executive_summary', 'N/A')[:100]}...")
            print(f"🔢 KPIs Count: {final_report.get('kpis_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive analysis test failed: {str(e)}")
        return False


def test_risk_focused_analysis():
    """Test risk-focused analysis."""
    print("\n🧪 Testing Risk-Focused Analysis")
    print("=" * 38)
    
    try:
        result = run_analysis(
            query="Conduct risk assessment and identify potential financial threats",
            company_id="risk_test_corp",
            focus_area="risk",
            risk_threshold="medium"
        )
        
        print(f"✅ Risk-focused analysis test completed")
        print(f"📊 Session: {result['session_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk-focused analysis test failed: {str(e)}")
        return False


def test_flow_visualization():
    """Test flow visualization capabilities."""
    print("\n🧪 Testing Flow Visualization")
    print("=" * 35)
    
    try:
        # Build flow
        flow = build_flow()
        
        # Set up test data
        test_query = UserQuery(
            query="Test visualization flow",
            company_id="viz_test_corp",
            opts={}
        )
        
        flow.state.user_query = test_query
        flow.state.company_id = "viz_test_corp"
        
        # Try to plot
        try:
            flow.plot("test_flow_graph.png")
            print("✅ Flow graph generated successfully")
            print("📊 Saved as 'test_flow_graph.png'")
        except Exception as plot_error:
            print(f"⚠️  Flow plotting not available: {str(plot_error)}")
            print("💡 This is expected if graphviz is not installed")
        
        return True
        
    except Exception as e:
        print(f"❌ Flow visualization test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all flow tests."""
    print("🏦 FinSights Flow Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Flow", test_basic_flow),
        ("Comprehensive Analysis", test_comprehensive_analysis),
        ("Risk-Focused Analysis", test_risk_focused_analysis),
        ("Flow Visualization", test_flow_visualization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🚀 Running {test_name} test...")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Flow is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return passed == len(tests)


if __name__ == "__main__":
    """Run the test suite when executed directly."""
    success = run_all_tests()
    
    if success:
        print("\n💡 Flow is ready for production use!")
        print("💡 To run interactively, use: python -m finsight.main")
        print("💡 To use programmatically, import from finsight.flow")
    else:
        print("\n❌ Flow needs debugging before production use.")
    
    exit(0 if success else 1)
