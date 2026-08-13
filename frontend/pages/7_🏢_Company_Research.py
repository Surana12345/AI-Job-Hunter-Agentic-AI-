"""
Company Research Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Company Research | AI Job Hunter", page_icon="🏢", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("🏢 Company Intelligence Research")
st.caption("AI-powered research on target company mission, technical stack, culture, products, and interview strategies.")

col1, col2 = st.columns([3, 1])
with col1:
    company_input = st.text_input("Company Name", value="Google")
    role_input = st.text_input("Target Role", value="Senior AI Engineer")
with col2:
    st.write("")
    st.write("")
    research_clicked = st.button("Research Company", type="primary")

if research_clicked:
    if company_input:
        with st.spinner(f"Researching {company_input} with AI Agent..."):
            try:
                res = client.research_company(company_name=company_input, job_title=role_input)
                st.subheader(f"🏢 {res.get('name')}")
                st.markdown(f"**Overview:** {res.get('summary')}")
                if res.get("website"):
                    st.markdown(f"**Website:** [{res.get('website')}]({res.get('website')})")

                c1, c2 = st.columns(2)
                with c1:
                    st.success("🛠️ Typical Tech Stack")
                    for t in res.get("tech_stack", []):
                        st.markdown(f"- `{t}`")

                with c2:
                    st.info("💡 Key Products & Services")
                    for p in res.get("products", []):
                        st.markdown(f"- {p}")

                st.markdown("### 🎯 Interview Process & Cultural Strategy")
                st.write(res.get("interview_style", "Standard interview evaluation rounds."))

            except Exception as e:
                st.error(f"Research failed: {e}")
    else:
        st.warning("Please enter a company name.")
