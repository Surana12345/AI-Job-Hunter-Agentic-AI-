"""
ATS Analyzer Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="ATS Analyzer | AI Job Hunter", page_icon="🎯", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("🎯 ATS Compatibility Analyzer")
st.caption("Compare your resume against a target job description to get match score, missing keywords, and recommendations.")

try:
    resumes = client.list_resumes()
except Exception as e:
    st.error(f"Failed to fetch resumes: {e}")
    resumes = []

if not resumes:
    st.warning("Please upload at least one resume in **Resume Manager** first.")
    st.stop()

resume_opts = {f"{r['filename']} ({r['id'][:8]}...)": r['id'] for r in resumes}
selected_label = st.selectbox("Select Resume", options=list(resume_opts.keys()))
selected_resume_id = resume_opts[selected_label]

job_title = st.text_input("Target Job Title", value="Senior Python Engineer")
job_company = st.text_input("Company Name", value="Tech Corp")
job_description = st.text_area("Job Description", height=200, placeholder="Paste the job description text here...")

if st.button("Run ATS Analysis", type="primary"):
    if not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing ATS Compatibility with AI..."):
            try:
                res = client.analyze_ats(
                    resume_id=selected_resume_id,
                    job_description=job_description,
                    job_title=job_title,
                    job_company=job_company,
                )
                
                score = res.get("overall_score", 0)
                st.subheader("ATS Score")
                st.progress(min(int(score), 100))
                st.markdown(f"## **{score}%** Match Score")

                col1, col2 = st.columns(2)
                with col1:
                    st.success("✅ Matched Keywords")
                    for k in res.get("matched_keywords", []):
                        st.markdown(f"- `{k}`")

                with col2:
                    st.error("❌ Missing Keywords / Skill Gaps")
                    for k in res.get("missing_keywords", []):
                        st.markdown(f"- `{k}`")

                st.subheader("💡 Recommendations")
                for sugg in res.get("suggestions", []):
                    st.info(f"• {sugg}")

            except Exception as e:
                st.error(f"ATS Analysis failed: {e}")
