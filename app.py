import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pypdf import PdfReader
from groq import Groq

# Page Setup
st.set_page_config(
    page_title="Learning & Career Studio (LCS)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enhanced Styling (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container & Soft Background */
    .stApp {
        background: linear-gradient(135deg, #F9FBFC 0%, #F0F4F8 100%);
        color: #1A202C;
    }

    /* Cards Layout */
    .lcs-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(24, 43, 73, 0.04);
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }

    .lcs-highlight-box {
        background: linear-gradient(135deg, #FFF0F5 0%, #FCEAF3 100%);
        border-left: 5px solid #E8A4C4;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }

    /* Custom Navigation Buttons (Colorful Pill Style) */
    .stRadio > label {
        display: none !important;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 8px;
    }

    div[data-testid="stRadio"] label {
        background-color: #F1F5F9;
        color: #334155;
        border-radius: 10px;
        padding: 10px 16px !important;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        display: flex;
        align-items: center;
        width: 100%;
    }

    div[data-testid="stRadio"] label:hover {
        background-color: #E2E8F0;
        transform: translateX(3px);
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, #6C63FF 0%, #5A52E0 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #6C63FF;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
    }

    /* Agent Side Panel Styling */
    .agent-header {
        background: linear-gradient(135deg, #182B49 0%, #2A4365 100%);
        color: #FFFFFF;
        padding: 14px 18px;
        border-radius: 12px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(24, 43, 73, 0.15);
    }

    /* Button Enhancements */
    .stButton>button {
        background: linear-gradient(135deg, #6C63FF 0%, #5A52E0 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(108, 99, 255, 0.3);
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initializer
def init_session_state():
    defaults = {
        'groq_api_key': '',
        'profile': {
            'name': 'Areeba Imran',
            'edu_level': 'University',
            'institution': 'University of Agriculture Faisalabad',
            'degree': 'B.S. Information Technology',
            'semester': 'Semester 4',
            'gpa': '3.7',
            'subjects': ['Database Systems', 'Algorithms', 'Data Science', 'Software Engineering'],
            'skills': ['Python', 'SQL', 'HTML/CSS', 'Git', 'Data Structures'],
            'interests': ['Artificial Intelligence', 'Data Analytics', 'Web Development'],
            'certifications': ['Python for Data Science'],
            'projects': ['Tasty Bite Cafe Web App', 'DSA Educational Series'],
            'career_goal': 'Data Analyst / AI Engineer',
            'work_type': 'Hybrid / Remote'
        },
        'study_progress': {
            'Database Systems': {'SQL JOINs': 'Needs Revision', 'Normalization': 'Strong', 'Indexing': 'Practicing', 'Transactions': 'Not Started'},
            'Algorithms': {'Sorting & Searching': 'Strong', 'Dynamic Programming': 'Needs Revision', 'Graph Algorithms': 'Learning', 'Trees': 'Strong'},
            'Data Science': {'Pandas & Numpy': 'Strong', 'Data Cleaning': 'Strong', 'Machine Learning Basics': 'Learning', 'Visualization': 'Practicing'},
            'Software Engineering': {'Agile Methodology': 'Strong', 'Design Patterns': 'Learning', 'Testing': 'Not Started'}
        },
        'weak_topics': ['SQL JOINs', 'Dynamic Programming', 'Machine Learning Basics'],
        'career_matches': [
            {'title': 'Data Analyst', 'match': 92, 'reasons': 'Strong SQL, Python, and data visualization alignment.'},
            {'title': 'Python Developer', 'match': 85, 'reasons': 'Good grasp of algorithms and backend scripting.'},
            {'title': 'AI Engineer', 'match': 78, 'reasons': 'Solid AI interest; needs deeper machine learning exposure.'}
        ],
        'skill_gaps': [
            {'skill': 'Power BI / Tableau', 'priority': 'High', 'status': 'Missing'},
            {'skill': 'Advanced SQL Window Functions', 'priority': 'Medium', 'status': 'Developing'},
            {'skill': 'Statistics & Probability', 'priority': 'High', 'status': 'Developing'}
        ],
        'readiness_score': 84,
        'chat_history': [
            {"role": "assistant", "content": "Salam Areeba! Main aap ka LCS Intelligent Assistant hoon. Aaj parhai ya career guidance mein kis tarah madad karoon?"}
        ]
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# LLM Call Function
def call_groq_llm(prompt, system_prompt="You are an intelligent educational and career advisor AI for Learning & Career Studio (LCS)."):
    api_key = st.session_state.get('groq_api_key', '')
    if not api_key:
        return "⚠️ Groq API key is missing. Please enter your API key at the top bar."
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error contacting Groq API: {str(e)}"

# Header Area
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown("<h1 style='color: #182B49; margin-bottom: 0px; font-weight: 800;'>🎓 Learning & Career Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.95rem; font-weight: 500;'>Intelligent Student Ecosystem — School to Career Mastery</p>", unsafe_allow_html=True)

with top_col2:
    if not st.session_state['groq_api_key']:
        key_in = st.text_input("🔑 Private Groq API Key", type="password", help="Enter your Groq key here. It remains private in your session.")
        if key_in:
            st.session_state['groq_api_key'] = key_in
            st.rerun()
    else:
        st.success("API Key Active", icon="🔒")

st.divider()

# Custom Sidebar Navigation with Icons
with st.sidebar:
    st.markdown("<h3 style='color:#182B49; margin-bottom: 5px; font-weight: 700;'>📌 NAVIGATION</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.8rem; color:#64748B;'>Select Studio Workspace</p>", unsafe_allow_html=True)
    
    nav_options = [
        "📊 Dashboard",
        "👤 My Profile",
        "📖 Study Workspace",
        "🗺️ Study Roadmap & Planner",
        "✏️ Quizzes & Mock Exams",
        "📚 PDF Material & RAG",
        "🎯 Career Discovery & Skills",
        "📄 CV & Job Matcher",
        "🎤 Interview Intelligence",
        "📈 Analytics & Next Action"
    ]
    
    nav_selected = st.radio("Select Section", nav_options, label_visibility="collapsed")

# Page Layout: Workspace (Left 70%) | Persistent Agent (Right 30%)
main_content, right_agent_col = st.columns([2.5, 1.1])

# Attached Right Panel Agent (Always Visible)
with right_agent_col:
    st.markdown("""
    <div class='agent-header'>
        🤖 LCS Intelligent Assistant
    </div>
    """, unsafe_allow_html=True)
    
    chat_box = st.container(height=480)
    for msg in st.session_state.chat_history:
        with chat_box.chat_message(msg["role"]):
            st.write(msg["content"])

    agent_input = st.chat_input("Ask agent anything...", key="right_agent_input")
    if agent_input:
        st.session_state.chat_history.append({"role": "user", "content": agent_input})
        
        context_prompt = f"""
        Student Profile: {st.session_state.profile['name']}, {st.session_state.profile['degree']} ({st.session_state.profile['institution']})
        Weak Topics: {', '.join(st.session_state.weak_topics)}
        Career Goal: {st.session_state.profile['career_goal']}
        
        User Message: {agent_input}
        
        Provide a friendly, direct, mentor-style response in English, Urdu, or Roman Urdu as required.
        """
        with st.spinner("Agent typing..."):
            reply = call_groq_llm(context_prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

# Main Workspace Content
with main_content:

    # 1. Dashboard
    if "Dashboard" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown(f"### 👋 Welcome Back, {st.session_state.profile['name']}!")
        st.markdown(f"<p style='color:#64748B;'>{st.session_state.profile['degree']} | {st.session_state.profile['institution']}</p>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown("<div class='metric-card'><div class='metric-value'>78%</div><div class='metric-label'>Study Progress</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown("<div class='metric-card'><div class='metric-value' style='color:#19B5A5;'>86%</div><div class='metric-label'>Skill Strength</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown("<div class='metric-card'><div class='metric-value' style='color:#E8A4C4;'>92%</div><div class='metric-label'>Career Match</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#6C63FF;'>{st.session_state.readiness_score}%</div><div class='metric-label'>Readiness Score</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='lcs-highlight-box'>
            <h4 style='margin:0 0 6px 0; color:#182B49;'>⚡ Recommended Focus Action</h4>
            <p style='margin:0; color:#4A5568; font-size:0.95rem;'>
                <b>Topic: SQL JOINs & Power BI Integration</b><br>
                Aap ke target goal <i>Data Analyst</i> ke liye multi-table relational queries aur visualization essential hain.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📘 Subject Mastery")
            df_prog = pd.DataFrame({
                'Subject': ['Database', 'Algorithms', 'Data Science', 'Software Eng'],
                'Mastery': [68, 82, 76, 88]
            })
            fig = px.bar(df_prog, x='Mastery', y='Subject', orientation='h', color='Mastery',
                         color_continuous_scale=['#D8B4E2', '#6C63FF', '#182B49'])
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("#### 🎯 Target Path Alignment")
            cm_df = pd.DataFrame(st.session_state.career_matches)
            fig_pie = px.pie(cm_df, values='match', names='title', color_discrete_sequence=['#6C63FF', '#19B5A5', '#E8A4C4'])
            fig_pie.update_layout(height=220, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### ⚠️ Weak Topics Needing Revision")
        w_cols = st.columns(len(st.session_state.weak_topics))
        for idx, topic in enumerate(st.session_state.weak_topics):
            with w_cols[idx]:
                st.warning(f"**{topic}**\n\n*Action: Take quiz & review notes.*")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. My Profile
    elif "My Profile" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 👤 Student Profile & Credentials")
        with st.form("prof_form"):
            col1, col2 = st.columns(2)
            with col1:
                p_name = st.text_input("Full Name", value=st.session_state.profile['name'])
                p_inst = st.text_input("Institution", value=st.session_state.profile['institution'])
                p_deg = st.text_input("Degree / Program", value=st.session_state.profile['degree'])
            with col2:
                p_goal = st.text_input("Target Career Goal", value=st.session_state.profile['career_goal'])
                p_skills = st.text_area("Skills List (comma-separated)", value=", ".join(st.session_state.profile['skills']))
            
            if st.form_submit_button("Save Profile Settings"):
                st.session_state.profile['name'] = p_name
                st.session_state.profile['institution'] = p_inst
                st.session_state.profile['degree'] = p_deg
                st.session_state.profile['career_goal'] = p_goal
                st.session_state.profile['skills'] = [s.strip() for s in p_skills.split(',') if s.strip()]
                st.success("Profile updated successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Study Workspace
    elif "Study Workspace" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📖 Concept Workspace & Explanations")
        
        sub_col, top_col = st.columns(2)
        with sub_col:
            selected_sub = st.selectbox("Select Subject", st.session_state.profile['subjects'])
        with top_col:
            selected_top = st.selectbox("Select Topic", ['SQL JOINs', 'Dynamic Programming', 'Pandas & Numpy', 'Agile Methodologies'])
        
        mode = st.radio("Output Mode", ["Detailed Concept Explanation", "Quick Revision Notes", "Code Example"], horizontal=True)
        
        if st.button("Generate Study Insights"):
            with st.spinner("Generating conceptual explanation..."):
                res = call_groq_llm(f"Explain {selected_top} in {selected_sub} for an IT student in {mode} format.")
                st.markdown(res)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Study Roadmap & Planner
    elif "Study Roadmap" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 🗓️ Adaptive Exam Roadmap Generator")
        
        days = st.number_input("Days remaining until Exam", min_value=1, max_value=60, value=14)
        hours = st.slider("Daily available study hours", 1, 10, 4)
        
        if st.button("Generate Automated Schedule"):
            with st.spinner("Building optimal timetable..."):
                plan = call_groq_llm(f"Create a day-by-day {days}-day study plan ({hours} hrs/day) prioritizing weak topics: {st.session_state.weak_topics}.")
                st.markdown(plan)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Quizzes & Mock Exams
    elif "Quizzes" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📝 Adaptive Quiz & Mock Assessment")
        
        q_topic = st.selectbox("Quiz Topic", ['SQL JOINs', 'Dynamic Programming', 'Pandas & Numpy'])
        if st.button("Generate Practice Questions"):
            with st.spinner("Preparing quiz..."):
                q_text = call_groq_llm(f"Generate 3 multiple-choice questions on {q_topic} with choices and an answer key at the bottom.")
                st.session_state['active_quiz'] = q_text
        
        if 'active_quiz' in st.session_state:
            st.markdown(st.session_state['active_quiz'])
        st.markdown("</div>", unsafe_allow_html=True)

    # 6. PDF Material & RAG
    elif "PDF Material" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📄 Lecture PDF Q&A & Summarizer")
        
        uploaded_pdf = st.file_uploader("Upload Notes or Lecture Slides (PDF)", type=["pdf"])
        if uploaded_pdf:
            reader = PdfReader(uploaded_pdf)
            pdf_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.session_state['pdf_context'] = pdf_text[:3500]
            st.success("Document loaded successfully!")

        if 'pdf_context' in st.session_state:
            pdf_q = st.text_input("Ask any question grounded in the uploaded document:")
            if st.button("Search Document") and pdf_q:
                with st.spinner("Analyzing document..."):
                    ans = call_groq_llm(f"Document Context: {st.session_state['pdf_context']}\n\nQuestion: {pdf_q}")
                    st.markdown(ans)
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. Career Discovery & Skills
    elif "Career Discovery" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Skill Gap & Project Recommendation Matrix")
        
        st.dataframe(pd.DataFrame(st.session_state.skill_gaps), use_container_width=True)
        
        if st.button("Suggest Portfolio Projects to Fill Skill Gaps"):
            with st.spinner("Selecting optimal projects..."):
                p_ideas = call_groq_llm(f"Suggest 2 portfolio projects for a {st.session_state.profile['career_goal']} targeting missing skills: Power BI and Advanced SQL.")
                st.markdown(p_ideas)
        st.markdown("</div>", unsafe_allow_html=True)

    # 8. CV & Job Matcher
    elif "CV & Job Matcher" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📄 Job Description & Profile Matcher")
        
        jd = st.text_area("Paste Target Job Description (JD):", height=150)
        if st.button("Calculate Match & Skill Fit") and jd:
            with st.spinner("Comparing skills with Job Description..."):
                match_res = call_groq_llm(f"Compare student profile skills: {st.session_state.profile['skills']} against this JD:\n\n{jd}")
                st.markdown(match_res)
        st.markdown("</div>", unsafe_allow_html=True)

    # 9. Interview Intelligence
    elif "Interview Intelligence" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 🎤 Mock Interview Simulator")
        
        if st.button("Get Technical Question"):
            with st.spinner("Generating interview question..."):
                q = call_groq_llm(f"Ask 1 technical interview question for a {st.session_state.profile['career_goal']} role.")
                st.session_state['interview_q'] = q

        if 'interview_q' in st.session_state:
            st.info(st.session_state['interview_q'])
            ans = st.text_area("Your Response / Answer:")
            if st.button("Evaluate Response") and ans:
                feedback = call_groq_llm(f"Question: {st.session_state['interview_q']}\nAnswer: {ans}\nEvaluate out of 10 and suggest improvements.")
                st.markdown(feedback)
        st.markdown("</div>", unsafe_allow_html=True)

    # 10. Analytics & Next Action
    elif "Analytics" in nav_selected:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Comprehensive Growth Analytics")
        
        readiness_data = pd.DataFrame({
            'Metric': ['Skills', 'Projects', 'Academic', 'CV Fit', 'Interview'],
            'Score': [88, 80, 92, 84, 78]
        })
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=readiness_data['Score'],
            theta=readiness_data['Metric'],
            fill='toself',
            fillcolor='rgba(108, 99, 255, 0.25)',
            line=dict(color='#6C63FF')
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=280)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 10px 0;">
    Designed & Developed by <b>Areeba Imran</b> | © 2026 Learning & Career Studio (LCS)
</div>
""", unsafe_allow_html=True)
