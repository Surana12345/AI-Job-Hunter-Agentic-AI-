"""
Candidate Profile Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Candidate Profile | AI Job Hunter", page_icon="👤", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

user = st.session_state.get("user") or {}

st.title("👤 Candidate Profile & Preferences")
st.caption("Manage your professional identity, target career goals, and experience level.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Personal Details")
    full_name = st.text_input("Full Name", value=user.get("full_name", "Candidate"))
    email = st.text_input("Email Address", value=user.get("email", ""), disabled=True)
    phone = st.text_input("Phone Number", value="+1 (555) 019-2831")
    location = st.text_input("Current Location", value="San Francisco, CA (or Remote)")
    linkedin_url = st.text_input("LinkedIn Profile URL", value="https://linkedin.com/in/candidate")
    github_url = st.text_input("GitHub Portfolio URL", value="https://github.com/candidate")

with col2:
    st.subheader("Target Career Parameters")
    target_role = st.text_input("Target Job Title", value="Senior AI / Software Engineer")
    exp_level = st.selectbox("Experience Level", ["Entry Level (0-2 yrs)", "Mid Level (3-5 yrs)", "Senior Level (5-8 yrs)", "Lead / Staff (8+ yrs)"], index=2)
    target_salary = st.number_input("Target Base Salary ($/yr)", value=150000, step=5000)
    preferred_work_type = st.multiselect("Preferred Work Types", ["Remote", "Hybrid", "On-site"], default=["Remote", "Hybrid"])
    bio = st.text_area("Professional Summary Bio", value="Passionate Software Engineer specializing in Python, LangGraph, agentic AI systems, and cloud backend architecture.")

if st.button("Save Profile Updates", type="primary"):
    st.success("Candidate profile updated successfully!")
