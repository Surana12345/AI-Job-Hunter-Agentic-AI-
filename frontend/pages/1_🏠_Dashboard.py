"""
Dashboard Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Dashboard | AI Job Hunter", page_icon="🏠", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("🏠 Overview Dashboard")
st.caption("Key job search metrics, resume status, and recent activity.")

try:
    analytics = client.get_tracker_analytics()
    resumes = client.list_resumes()
    jobs = client.list_jobs()
except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Resumes", len(resumes))
with col2:
    st.metric("Discovered Jobs", len(jobs))
with col3:
    st.metric("Applications Tracked", analytics.get("total_tracked", 0))
with col4:
    st.metric("Interview Conversion", f"{analytics.get('interview_rate', 0)}%")

st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Application Status Breakdown")
    c1, c2, c3 = st.columns(3)
    c1.metric("Saved", analytics.get("saved_count", 0))
    c2.metric("Applied", analytics.get("applied_count", 0))
    c3.metric("Interviews", analytics.get("interview_count", 0))

with col_right:
    st.subheader("📄 Uploaded Resumes")
    if resumes:
        for r in resumes:
            is_prim = "⭐ Primary" if r.get("is_primary") else ""
            st.markdown(f"- **{r.get('filename')}** ({r.get('file_type').split('/')[-1].upper()}) {is_prim}")
    else:
        st.info("No resumes uploaded yet. Go to **Resume Manager** to upload one!")
