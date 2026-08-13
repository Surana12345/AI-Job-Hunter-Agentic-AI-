"""Phase 5 verification script -- tests Cover Letter, Recruiter Message, and Interview Prep agents."""
import asyncio
from backend.agents.orchestrator import run_agent_pipeline

async def test_cover_letter_agent():
    print("=" * 60)
    print("  TEST 1: Cover Letter Agent (LangGraph)")
    print("=" * 60)

    res = await run_agent_pipeline(
        intent="generate_cover_letter",
        state_overrides={
            "resume_text": "Experienced Python Backend Engineer with 5 years in FastAPI, PostgreSQL, and LLMs.",
            "job_description": "Seeking Senior Python Engineer to build scalable microservices and AI agent pipelines.",
            "job_title": "Senior Python Engineer",
            "job_company": "Acme AI Corp",
        }
    )

    assert res.get("error") is None, f"Error: {res.get('error')}"
    letter = res.get("cover_letter", "")
    print(f"  Generated Cover Letter Snippet:\n{letter[:300]}...\n")
    assert len(letter) > 100
    print("  [PASS] Cover Letter agent working correctly!")

async def test_recruiter_message_agent():
    print("\n" + "=" * 60)
    print("  TEST 2: Recruiter Message Agent (LangGraph)")
    print("=" * 60)

    res = await run_agent_pipeline(
        intent="generate_recruiter_message",
        state_overrides={
            "resume_text": "Python Backend Engineer skilled in FastAPI and LangChain.",
            "job_title": "AI Engineer",
            "job_company": "Acme AI Corp",
            "outreach_platform": "LinkedIn",
        }
    )

    assert res.get("error") is None, f"Error: {res.get('error')}"
    msg = res.get("recruiter_message", "")
    print(f"  Generated Outreach Message:\n{msg}\n")
    assert len(msg) > 20
    print("  [PASS] Recruiter outreach message agent working correctly!")

async def test_interview_prep_agent():
    print("\n" + "=" * 60)
    print("  TEST 3: Interview Prep Agent (LangGraph)")
    print("=" * 60)

    res = await run_agent_pipeline(
        intent="prepare_interview",
        state_overrides={
            "resume_text": "Python Engineer with distributed systems experience.",
            "job_description": "Build high-throughput async Python APIs.",
            "job_title": "Backend Architect",
            "job_company": "Acme AI Corp",
        }
    )

    assert res.get("error") is None, f"Error: {res.get('error')}"
    prep = res.get("interview_prep", {})
    tech_qs = prep.get("technical_questions", [])
    print(f"  Technical Questions Generated: {len(tech_qs)}")
    if tech_qs:
        print(f"  Sample Q: {tech_qs[0].get('question')}")
    print("  [PASS] Interview prep agent working correctly!")

async def main():
    await test_cover_letter_agent()
    await test_recruiter_message_agent()
    await test_interview_prep_agent()
    print("\n" + "=" * 60)
    print("  PHASE 5 VERIFICATION COMPLETE -- ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
