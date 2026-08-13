"""Phase 4 verification script -- tests job search adapters and company research agent."""
import asyncio
from backend.jobs.sources.remotive import search_remotive
from backend.agents.orchestrator import run_agent_pipeline

async def test_remotive_search():
    print("=" * 60)
    print("  TEST 1: Remotive Job Source Adapter")
    print("=" * 60)

    results = await search_remotive(query="Python", max_results=3)
    print(f"  Fetched {len(results)} remote job listings:")
    for i, res in enumerate(results, 1):
        print(f"  #{i} {res.title} at {res.company} ({res.location})")
        print(f"     URL: {res.url}")
    assert len(results) > 0, "Should fetch at least 1 job from Remotive"
    print("  [PASS] Remotive job adapter working correctly!")

async def test_company_research_agent():
    print("\n" + "=" * 60)
    print("  TEST 2: Company Research Agent (LangGraph)")
    print("=" * 60)

    res = await run_agent_pipeline(
        intent="research_company",
        state_overrides={
            "job_company": "Google",
            "job_title": "Senior AI Engineer",
        }
    )

    assert res.get("error") is None, f"Company research error: {res.get('error')}"
    info = res.get("company_info", {})
    print(f"  Company: {info.get('name', 'Google')}")
    print(f"  Summary: {info.get('summary')}")
    print(f"  Tech Stack: {info.get('tech_stack')}")
    print(f"  Interview Style: {info.get('interview_style')}")
    print("  [PASS] Company research agent working correctly!")

async def main():
    await test_remotive_search()
    await test_company_research_agent()
    print("\n" + "=" * 60)
    print("  PHASE 4 VERIFICATION COMPLETE -- ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
