"""
AI Job Hunter - Main Streamlit Application

Entry point for the Agentic AI Career Assistant platform.
"""

import streamlit as st
from api_client import APIClient

st.set_page_config(
    page_title="AI Job Hunter | Career Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Glassmorphism Theme)
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #818CF8;
    }
    .metric-lbl {
        color: #94A3B8;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

def get_client() -> APIClient:
    return APIClient(token=st.session_state.get("token"))

def render_login():
    st.title("🎯 AI Job Hunter")
    st.caption("Agentic AI Assistant for Career Discovery, Resume Tailoring & Application Tracking")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        tab1, tab2 = st.tabs(["🔒 Sign In", "📝 Create Account"])
        
        with tab1:
            st.subheader("Welcome Back")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Sign In"):
                if email and password:
                    try:
                        client = APIClient()
                        res = client.login(email, password)
                        st.session_state["token"] = res["access_token"]
                        st.session_state["user"] = res.get("user")
                        st.success("Signed in successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sign in failed: {e}")
                else:
                    st.warning("Please fill in email and password.")

        with tab2:
            st.subheader("Create Account")
            name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Register Account"):
                if name and reg_email and reg_pass:
                    try:
                        client = APIClient()
                        res = client.register(reg_email, reg_pass, name)
                        st.session_state["token"] = res["access_token"]
                        st.session_state["user"] = res.get("user")
                        st.success("Account created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
                else:
                    st.warning("Please fill in all fields.")

    with col2:
        st.markdown("### Why AI Job Hunter?")
        st.markdown(
            """
            - **🤖 Multi-Agent Orchestration**: Autonomous agents parse resumes, score ATS compatibility, research companies, and tailor career materials.
            - **⚡ Real-time Job Search**: Search remote and global opportunities across Remotive & Adzuna.
            - **🎯 ATS Match & Keyword Gap**: Identify missing technical keywords and tailor your resume for 90%+ ATS match.
            - **🛡️ You Stay in Control**: Generates application packages for your review -- **never automatically submits or impersonates you**.
            """
        )

def main():
    if not st.session_state.get("token"):
        render_login()
        return

    # Sidebar Header & User Profile
    user = st.session_state.get("user") or {}
    user_name = user.get("full_name", "Candidate")
    user_email = user.get("email", "")

    st.sidebar.title("🎯 AI Job Hunter")
    st.sidebar.markdown(f"**Logged in as:** {user_name}")
    st.sidebar.caption(user_email)
    st.sidebar.divider()

    if st.sidebar.button("Sign Out"):
        st.session_state["token"] = None
        st.session_state["user"] = None
        st.rerun()

    st.title(f"Welcome back, {user_name}! 👋")
    st.markdown("Select a module from the sidebar navigation menu to get started.")

    st.markdown("### Quick Navigation")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📄 **Resume Manager**\nUpload and AI-parse your resume.")
        st.info("🔍 **Job Search**\nDiscover technical roles across Remotive & Adzuna.")
    with col2:
        st.success("🎯 **ATS Analyzer**\nScore compatibility and get keyword gap reports.")
        st.success("✨ **Career Assets**\nGenerate Cover Letters & Outreach Messages.")
    with col3:
        st.warning("📊 **Application Tracker**\nTrack applications and conversion metrics.")
        st.warning("🏢 **Company Research**\nAI intelligence on target companies & tech stack.")

if __name__ == "__main__":
    main()
