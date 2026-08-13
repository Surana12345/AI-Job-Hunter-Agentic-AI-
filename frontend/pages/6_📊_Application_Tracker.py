"""
Application Tracker Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Application Tracker | AI Job Hunter", page_icon="📊", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("📊 Application Tracker & Analytics")
st.caption("Manage your job application pipeline and track conversion rates across stages.")

try:
    analytics = client.get_tracker_analytics()
    tracks = client.list_application_tracks()
except Exception as e:
    st.error(f"Failed to load application tracker data: {e}")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Saved", analytics.get("saved_count", 0))
c2.metric("Applied", analytics.get("applied_count", 0))
c3.metric("Interviewing", analytics.get("interview_count", 0))
c4.metric("Offers", analytics.get("offer_count", 0))
c5.metric("Rejected", analytics.get("rejected_count", 0))

st.divider()

st.subheader("Add Application Entry")
with st.form("add_app_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        f_title = st.text_input("Job Title")
    with col2:
        f_company = st.text_input("Company Name")
    with col3:
        f_status = st.selectbox("Stage", ["saved", "applied", "interview", "offer", "rejected"])
    
    submit_app = st.form_submit_button("Add Application")
    if submit_app:
        if f_title and f_company:
            try:
                client.create_application_track(job_title=f_title, company_name=f_company, status=f_status)
                st.success(f"Added {f_title} at {f_company} to tracker!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add: {e}")
        else:
            st.warning("Please fill in job title and company name.")

st.divider()
st.subheader("Application Pipeline Table")

if tracks:
    for t in tracks:
        with st.expander(f"**{t['job_title']}** @ **{t['company_name']}** -- Status: `{t['status'].upper()}`"):
            col_s, col_n = st.columns([1, 2])
            with col_s:
                new_status = st.selectbox(
                    "Update Status",
                    ["saved", "applied", "interview", "offer", "rejected"],
                    index=["saved", "applied", "interview", "offer", "rejected"].index(t["status"]),
                    key=f"status_select_{t['id']}"
                )
                if st.button("Save Status Change", key=f"save_st_{t['id']}"):
                    client.update_application_track(t["id"], status=new_status)
                    st.success("Updated status!")
                    st.rerun()

            with col_n:
                st.write(f"**Created:** {t['created_at']}")
                if t.get("applied_date"):
                    st.write(f"**Applied Date:** {t['applied_date']}")
                st.caption(f"Notes: {t.get('notes') or 'No notes added.'}")
else:
    st.info("No applications tracked yet. Use the form above to add your first application!")
