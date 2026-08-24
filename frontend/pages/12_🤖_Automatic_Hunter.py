"""
Automatic Job Hunter Bot Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Automatic Job Hunter | AI Job Hunter", page_icon="🤖", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("🤖 Autonomous Agentic Job Hunter Bot")
st.caption("Automated background agent scanning job providers, ranking ATS match scores, and preparing review-ready application packages.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎯 Hunting Parameters")
    search_query = st.text_input("Target Job Keywords", value="Python AI Engineer")
    location_query = st.text_input("Preferred Location", value="Remote")
    min_salary = st.number_input("Minimum Base Salary ($)", value=120000, step=5000)
    min_ats_score = st.slider("Minimum ATS Filter Threshold (%)", 60, 95, 75)
    
    bot_status = st.toggle("Activate Autonomous Background Agent", value=True)
    if bot_status:
        st.success("🟢 Bot Status: ACTIVE & MONITORING")
    else:
        st.warning("🔴 Bot Status: PAUSED")

with col2:
    st.subheader("⚡ Instant Agent Run")
    st.markdown("Trigger an immediate multi-provider scan and ATS evaluation cycle.")
    if st.button("Run Hunter Agent Cycle Now", type="primary"):
        with st.spinner("Autonomous agent scanning Remotive & Adzuna for matching listings..."):
            try:
                # Fetch recommendations from backend background job monitor
                recs = client.get_job_recommendations()
                st.session_state["recent_hunting_results"] = recs
                st.success(f"Agent cycle complete! Evaluated {len(recs)} listings.")
            except Exception as e:
                st.error(f"Hunter execution failed: {e}")

st.divider()
st.subheader("📊 Recommended High-Match Applications")

results = st.session_state.get("recent_hunting_results") or [
    {
        "id": "demo-1",
        "title": "Senior AI Backend Engineer",
        "company": "Anthropic AI",
        "location": "Remote (US)",
        "source": "Remotive API",
        "ats_score": 92,
        "salary_max": 180000,
        "url": "https://remotive.com"
    },
    {
        "id": "demo-2",
        "title": "LangGraph & Python Systems Developer",
        "company": "Scale AI",
        "location": "Remote",
        "source": "Adzuna API",
        "ats_score": 88,
        "salary_max": 165000,
        "url": "https://adzuna.com"
    }
]

for job in results:
    with st.container():
        c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
        with c1:
            st.markdown(f"**[{job.get('title')}]({job.get('url')})**")
            st.caption(f"🏢 {job.get('company')} • 📍 {job.get('location')}")
        with c2:
            score = job.get('ats_score', 85)
            st.progress(score / 100.0, text=f"ATS Match: {score}%")
        with c3:
            st.badge(f"${job.get('salary_max', 150000):,}")
        with c4:
            if st.button("Track & Tailor", key=f"hunt_{job.get('id')}"):
                try:
                    client.create_application_track(
                        job_title=job.get('title'),
                        company_name=job.get('company'),
                        location=job.get('location'),
                        status="saved"
                    )
                    st.success("Tracked!")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.divider()
