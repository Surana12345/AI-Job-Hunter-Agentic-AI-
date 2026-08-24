"""
Salary Negotiation & Offer Evaluator Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="Salary Negotiator | AI Job Hunter", page_icon="💰", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("💰 Salary Negotiation & Offer Evaluator")
st.caption("AI-powered market benchmarking, offer evaluation, counter-offer email generator, and strategic levers.")

col1, col2 = st.columns(2)
with col1:
    job_title = st.text_input("Target Role Title", value="Senior Backend Engineer")
    company_name = st.text_input("Company Name", value="Acme Corp")
    location = st.text_input("Job Location", value="Remote (US)")
with col2:
    offered_base = st.number_input("Offered Base Salary ($)", value=140000, step=5000)
    offered_bonus = st.number_input("Offered Annual Bonus ($)", value=15000, step=1000)
    offered_equity = st.number_input("Offered Equity / RSUs ($)", value=20000, step=5000)

notes = st.text_area("Candidate Negotiation Notes / Priorities", placeholder="e.g. Seeking $160k base or sign-on bonus flexibility due to 5+ years of Python expertise...")

if st.button("Evaluate Offer & Generate Counter Strategy", type="primary"):
    with st.spinner("Analyzing market compensation benchmarks with AI..."):
        try:
            res = client.evaluate_salary_negotiation(
                job_title=job_title,
                company_name=company_name,
                offered_base=int(offered_base),
                offered_bonus=int(offered_bonus),
                offered_equity=int(offered_equity),
                location=location,
                notes=notes,
            )

            st.divider()
            st.subheader("📊 Market Benchmark Range (USD)")
            mr = res.get("market_range", {})
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("25th Percentile", f"${mr.get('percentile_25', 0):,}")
            m2.metric("50th (Median)", f"${mr.get('percentile_50_median', 0):,}")
            m3.metric("75th Percentile", f"${mr.get('percentile_75', 0):,}")
            m4.metric("AI Counter Target", f"${res.get('recommended_counter', 0):,}")

            st.subheader("💡 Offer Assessment")
            st.info(res.get("offer_assessment", ""))

            st.subheader("✉️ Counter-Offer Email Script")
            st.text_area("Editable Counter-Offer Email", value=res.get("counter_offer_script", ""), height=250)

            st.subheader("🎯 Key Negotiation Levers & Tactics")
            for lever in res.get("key_levers", []):
                st.markdown(f"- {lever}")

        except Exception as e:
            st.error(f"Evaluation failed: {e}")
