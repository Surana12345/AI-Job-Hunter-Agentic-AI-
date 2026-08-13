"""
Job Search Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Job Search | AI Job Hunter", page_icon="🔍", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("🔍 Multi-Source Job Search")
st.caption("Search across Remotive & Adzuna for technical roles.")

col1, col2, col3 = st.columns([3, 2, 1])
with col1:
    query = st.text_input("Job Title / Skill Query", value="Python Developer")
with col2:
    location = st.text_input("Location Filter", value="Remote")
with col3:
    st.write("")
    st.write("")
    search_clicked = st.button("Search Jobs", type="primary")

if search_clicked or "last_search" not in st.session_state:
    with st.spinner("Searching job boards..."):
        try:
            jobs = client.search_jobs(query=query, location=location)
            st.session_state["last_search"] = jobs
        except Exception as e:
            st.error(f"Search failed: {e}")
            jobs = []
else:
    jobs = st.session_state.get("last_search", [])

st.subheader(f"Found {len(jobs)} Opportunities")

if jobs:
    for j in jobs:
        with st.container():
            st.markdown(f"### {j['title']} @ **{j['company']}**")
            st.caption(f"📍 {j.get('location') or 'Remote'} | 🌐 Source: {j.get('source', 'Web').title()}")
            if j.get("url"):
                st.markdown(f"[🔗 View Original Job Listing]({j['url']})")
            
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button("Track Application", key=f"track_{j['id']}"):
                    try:
                        client.create_application_track(
                            job_title=j["title"],
                            company_name=j["company"],
                            location=j.get("location", ""),
                            status="saved"
                        )
                        st.success("Added to Application Tracker!")
                    except Exception as ex:
                        st.error(f"Error: {ex}")
            st.divider()
else:
    st.info("No jobs found. Try adjusting your search query.")
