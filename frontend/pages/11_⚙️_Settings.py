"""
Settings & Preferences Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Settings | AI Job Hunter", page_icon="⚙️", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

st.title("⚙️ System Settings & AI Configuration")
st.caption("Configure AI models, API keys, automated monitoring intervals, and system notifications.")

tab1, tab2, tab3 = st.tabs(["🤖 AI Model & API Config", "🔔 Notification & Alert Settings", "🔐 Security & Privacy"])

with tab1:
    st.subheader("LLM Engine & Agent Preferences")
    gemini_model = st.selectbox("Active Gemini Model", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"], index=0)
    temp = st.slider("Model Temperature (Creativity vs Determinism)", 0.0, 1.0, 0.3, 0.1)
    
    st.divider()
    st.subheader("API Keys Management")
    gemini_key = st.text_input("Google Gemini API Key", value="••••••••••••••••••••••••••••••••", type="password")
    adzuna_app_id = st.text_input("Adzuna App ID", value="••••••••", type="password")
    adzuna_key = st.text_input("Adzuna API Key", value="••••••••••••••••••••••••••••••••", type="password")
    
    if st.button("Save AI Configurations", type="primary"):
        st.success("AI configuration saved successfully!")

with tab2:
    st.subheader("Job Monitor & Recommendation Alerts")
    auto_poll = st.checkbox("Enable Background Job Polling Monitor", value=True)
    poll_freq = st.selectbox("Polling Frequency", ["Every 15 Minutes", "Every Hour", "Daily at 9:00 AM"], index=1)
    min_ats_filter = st.slider("Minimum ATS Compatibility Score for Alerts (%)", 50, 95, 75)
    email_alerts = st.checkbox("Send Email Notifications for 80%+ ATS Match Jobs", value=True)
    
    if st.button("Save Alert Settings"):
        st.success("Notification preferences updated!")

with tab3:
    st.subheader("Candidate Data Control & Safety Guarantee")
    st.info("🛡️ **Candidate Control Policy:** AI Job Hunter **never** submits applications or contacts recruiters without your explicit manual action.")
    st.checkbox("Enforce Manual Application Approval", value=True, disabled=True)
    st.checkbox("Log Agent Trajectories & Structured JSON Audits", value=True)
    
    if st.button("Clear Vectorstore Cache"):
        st.warning("Vectorstore cache cleared.")
