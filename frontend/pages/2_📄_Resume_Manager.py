"""
Resume Manager Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Resume Manager | AI Job Hunter", page_icon="📄", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("📄 Resume Manager")
st.caption("Upload PDF or DOCX resumes and extract structured skills using AI agents.")

tab1, tab2 = st.tabs(["📤 Upload Resume", "📋 Manage Resumes"])

with tab1:
    st.subheader("Upload Resume File")
    uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
    is_primary = st.checkbox("Set as primary resume", value=True)

    if st.button("Upload & Process", type="primary"):
        if uploaded_file is not None:
            try:
                bytes_data = uploaded_file.getvalue()
                res = client.upload_resume(
                    file_bytes=bytes_data,
                    filename=uploaded_file.name,
                    content_type=uploaded_file.type or "application/pdf",
                    is_primary=is_primary,
                )
                st.success(f"Resume '{uploaded_file.name}' uploaded successfully!")
                
                # Auto-parse skills with AI
                with st.spinner("AI parsing skills & experience..."):
                    parsed = client.parse_resume(res["id"])
                    st.success("AI Skill Parsing Complete!")
                    st.json(parsed.get("parsed_data", {}))
                st.rerun()
            except Exception as e:
                st.error(f"Upload/parsing failed: {e}")
        else:
            st.warning("Please select a file to upload.")

with tab2:
    st.subheader("Uploaded Resumes")
    try:
        resumes = client.list_resumes()
        if not resumes:
            st.info("No resumes uploaded yet.")
        else:
            for r in resumes:
                with st.expander(f"📄 {r['filename']} ({r['file_type'].split('/')[-1]}) {'⭐ Primary' if r['is_primary'] else ''}"):
                    st.write(f"**Uploaded:** {r['created_at']}")
                    st.write(f"**Skills Extracted:** {r.get('skills_count', 0)}")
                    if st.button("Run AI Skill Parsing", key=f"parse_{r['id']}"):
                        with st.spinner("Parsing resume with Gemini..."):
                            data = client.parse_resume(r["id"])
                            st.success("Parsing complete!")
                            st.json(data.get("parsed_data", {}))
    except Exception as e:
        st.error(f"Failed to load resumes: {e}")
