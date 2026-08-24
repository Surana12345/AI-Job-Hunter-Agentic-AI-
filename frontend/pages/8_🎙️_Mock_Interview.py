"""
AI Mock Interview Simulator Page - AI Job Hunter
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="AI Mock Interview | AI Job Hunter", page_icon="🎙️", layout="wide")

if not st.session_state.get("token"):
    st.warning("Please sign in from the main app page.")
    st.stop()

client = APIClient(token=st.session_state["token"])

st.title("🎙️ AI Mock Interview Simulator")
st.caption("Practice answering technical and behavioral interview questions with real-time AI scoring & feedback.")

col1, col2 = st.columns([1, 1])
with col1:
    job_title = st.text_input("Target Job Role", value="Senior AI Engineer", key="mi_title")
with col2:
    company_name = st.text_input("Target Company", value="Google", key="mi_company")

if "curr_question" not in st.session_state:
    st.session_state["curr_question"] = f"Tell me about your technical background and why you are interested in the {job_title} role at {company_name}."
if "history" not in st.session_state:
    st.session_state["history"] = []

st.divider()

st.subheader("💡 Current Interview Question")
st.info(f"**Interviewer:** {st.session_state['curr_question']}")

cand_answer = st.text_area("Your Response", height=150, placeholder="Type your answer here using the STAR technique or system design principles...")

if st.button("Submit Answer for AI Evaluation", type="primary"):
    if cand_answer.strip():
        with st.spinner("AI Interviewer is evaluating your response..."):
            try:
                res = client.evaluate_mock_interview(
                    job_title=job_title,
                    company_name=company_name,
                    question=st.session_state["curr_question"],
                    candidate_answer=cand_answer,
                )
                
                score = res.get("score", 7)
                feedback = res.get("feedback", "")
                improved = res.get("improved_answer", "")
                next_q = res.get("next_question", "")

                st.session_state["history"].append({
                    "question": st.session_state["curr_question"],
                    "answer": cand_answer,
                    "score": score,
                    "feedback": feedback,
                    "improved": improved,
                })

                st.session_state["curr_question"] = next_q
                st.success("Response Evaluated! Scroll down to view feedback and next question.")
                st.rerun()

            except Exception as e:
                st.error(f"Evaluation failed: {e}")
    else:
        st.warning("Please type your answer before submitting.")

if st.session_state["history"]:
    st.divider()
    st.subheader("📜 Interview Session History & AI Feedback")
    for idx, item in enumerate(reversed(st.session_state["history"]), 1):
        with st.expander(f"Round #{len(st.session_state['history']) - idx + 1} | Score: **{item['score']}/10**"):
            st.markdown(f"**Question:** {item['question']}")
            st.markdown(f"**Your Answer:** {item['answer']}")
            st.markdown(f"**AI Feedback:** {item['feedback']}")
            if item.get("improved"):
                st.caption(f"Suggested Model Response: {item['improved']}")
