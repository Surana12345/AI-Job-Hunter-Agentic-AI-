"""
Career Assets Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Career Assets | AI Job Hunter", page_icon="✨", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("✨ Career Assets Generator")
st.caption("AI-generated Cover Letters, Recruiter Cold Outreach Messages & Interview Guides.")

resumes = client.list_resumes()
if not resumes:
    st.warning("Please upload a resume in **Resume Manager** first.")
    st.stop()

resume_opts = {f"{r['filename']}": r['id'] for r in resumes}
selected_resume_id = resume_opts[st.selectbox("Select Resume Base", list(resume_opts.keys()))]

tab1, tab2, tab3 = st.tabs(["📝 Cover Letter", "💬 Recruiter Message", "💡 Interview Prep Guide"])

with tab1:
    st.subheader("Generate Cover Letter")
    cl_title = st.text_input("Job Title", value="Senior Backend Engineer", key="cl_title")
    cl_company = st.text_input("Company Name", value="Acme AI", key="cl_company")
    cl_desc = st.text_area("Job Description", height=150, key="cl_desc")

    if st.button("Generate Cover Letter", type="primary"):
        if cl_desc:
            with st.spinner("Writing tailored cover letter with AI..."):
                try:
                    res = client.generate_cover_letter(
                        resume_id=selected_resume_id,
                        job_description=cl_desc,
                        job_title=cl_title,
                        company_name=cl_company,
                    )
                    st.success("Cover Letter Generated!")
                    st.text_area("Result", value=res.get("cover_letter", ""), height=350)
                except Exception as e:
                    st.error(f"Generation failed: {e}")

with tab2:
    st.subheader("Generate Recruiter Outreach Message")
    rm_title = st.text_input("Job Title", value="AI Engineer", key="rm_title")
    rm_company = st.text_input("Company Name", value="Tech Corp", key="rm_company")
    platform = st.selectbox("Outreach Platform", ["LinkedIn", "Email", "Twitter"])

    if st.button("Generate Outreach Message", type="primary"):
        with st.spinner("Drafting cold message..."):
            try:
                res = client.generate_recruiter_message(
                    resume_id=selected_resume_id,
                    job_title=rm_title,
                    company_name=rm_company,
                    platform=platform,
                )
                st.success("Outreach Message Generated!")
                st.text_area("Message Text", value=res.get("message", ""), height=200)
            except Exception as e:
                st.error(f"Generation failed: {e}")

with tab3:
    st.subheader("Generate Interview Prep Guide")
    ip_title = st.text_input("Role Title", value="Software Architect", key="ip_title")
    ip_company = st.text_input("Target Company", value="Google", key="ip_company")
    ip_desc = st.text_area("Job Description Details", height=150, key="ip_desc")

    if st.button("Generate Interview Guide", type="primary"):
        with st.spinner("Building custom technical & behavioral interview guide..."):
            try:
                res = client.generate_interview_prep(
                    resume_id=selected_resume_id,
                    job_description=ip_desc,
                    company_name=ip_company,
                    role_title=ip_title,
                )
                st.success("Interview Prep Guide Generated!")
                
                st.markdown("### 💻 Technical Questions & Concepts")
                for q in res.get("technical_questions", []):
                    st.markdown(f"**Q: {q.get('question')}**")
                    st.caption(f"Suggested Focus: {q.get('suggested_answer')}")

                st.markdown("### ❓ Questions to Ask Interviewer")
                for q in res.get("questions_to_ask_interviewer", []):
                    st.markdown(f"- {q}")

            except Exception as e:
                st.error(f"Generation failed: {e}")

st.divider()
st.subheader("📦 Export Complete Application Dossier (PDF)")
st.caption("Compile your Cover Letter, Outreach Message, and Interview Guide into a single formatted PDF file.")

exp_title = st.text_input("Application Role Title", value="Senior Engineer", key="exp_title")
exp_company = st.text_input("Application Company Name", value="Tech Corp", key="exp_company")

if st.button("Generate & Download PDF Dossier", type="primary"):
    with st.spinner("Compiling PDF application dossier..."):
        try:
            pdf_bytes = client.export_application_pdf(
                job_title=exp_title,
                company_name=exp_company,
                cover_letter=st.session_state.get("last_cl", ""),
                recruiter_message=st.session_state.get("last_rm", ""),
                interview_prep=st.session_state.get("last_ip"),
            )
            st.download_button(
                label="📥 Download Application_Package.pdf",
                data=pdf_bytes,
                file_name=f"Application_Package_{exp_company.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )
            st.success("PDF Dossier compiled ready for download!")
        except Exception as e:
            st.error(f"PDF Export failed: {e}")

