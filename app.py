import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from io import BytesIO
from pypdf import PdfReader
from groq import Groq

# Set page config
st.set_page_config(
    page_title="Learning & Career Studio (LCS)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for LCS Theme
st.markdown("""
<style>
    /* Global Styles & Variables */
    :root {
        --deep-navy: #182B49;
        --royal-purple: #6C63FF;
        --teal: #19B5A5;
        --soft-pink: #F8D7E8;
        --blush-pink: #FCEAF3;
        --rose: #E8A4C4;
        --pink-purple: #D8B4E2;
        --bg-soft-white: #FAFBFE;
        --bg-cool-lavender: #F4F1FA;
        --bg-light-pink: #FFF7FA;
    }

    .stApp {
        background-color: var(--bg-soft-white);
        color: #182B49;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Card styling */
    .lcs-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(24, 43, 73, 0.05);
        border: 1px solid #EAEFF5;
        margin-bottom: 20px;
    }
    .lcs-card-accent {
        background-color: var(--bg-cool-lavender);
        border-left: 5px solid var(--royal-purple);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .lcs-card-highlight {
        background-color: var(--blush-pink);
        border-left: 5px solid var(--rose);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 15px;
    }

    /* Headers */
    .lcs-header {
        color: var(--deep-navy);
        font-weight: 700;
        margin-bottom: 5px;
    }
    .lcs-subheader {
        color: #5A6B82;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    /* Metric Badges */
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #EAEFF5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--royal-purple);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6C7A89;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--royal-purple);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #554CE1;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
    }

    /* Sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FD;
        border-right: 1px solid #EAEFF5;
    }

    /* Chat Drawer / Widget Styling */
    .chat-header {
        background-color: var(--deep-navy);
        color: white;
        padding: 12px 16px;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------------------------
def init_session_state():
    defaults = {
        'groq_api_key': '',
        'profile': {
            'name': 'Alex Student',
            'edu_level': 'University',
            'institution': 'Tech University',
            'degree': 'B.S. Computer Science',
            'semester': 'Semester 6',
            'gpa': '3.6',
            'subjects': ['Database Systems', 'Algorithms', 'Data Science', 'Software Engineering'],
            'skills': ['Python', 'SQL', 'HTML/CSS', 'Git', 'Data Structures'],
            'interests': ['Artificial Intelligence', 'Data Analytics', 'Web Development'],
            'certifications': ['Python for Data Science - Coursera'],
            'projects': ['E-commerce Web App', 'Student Management System'],
            'career_goal': 'Data Analyst / AI Engineer',
            'work_type': 'Hybrid / Remote'
        },
        'study_progress': {
            'Database Systems': {'SQL JOINs': 'Needs Revision', 'Normalization': 'Strong', 'Indexing': 'Practicing', 'Transactions': 'Not Started'},
            'Algorithms': {'Sorting & Searching': 'Strong', 'Dynamic Programming': 'Needs Revision', 'Graph Algorithms': 'Learning', 'Trees': 'Strong'},
            'Data Science': {'Pandas & Numpy': 'Strong', 'Data Cleaning': 'Strong', 'Machine Learning Basics': 'Learning', 'Visualization': 'Practicing'},
            'Software Engineering': {'Agile Methodology': 'Strong', 'Design Patterns': 'Learning', 'Testing': 'Not Started'}
        },
        'quiz_results': [],
        'weak_topics': ['SQL JOINs', 'Dynamic Programming', 'Machine Learning Basics'],
        'career_matches': [
            {'title': 'Data Analyst', 'match': 91, 'reasons': 'Strong SQL and Python background along with data visualization interest.'},
            {'title': 'Python Developer', 'match': 86, 'reasons': 'Good understanding of core algorithms and backend scripting.'},
            {'title': 'AI Engineer', 'match': 72, 'reasons': 'Interest in AI and Data Science basics, but missing deep learning & advanced math.'},
            {'title': 'Software Engineer', 'match': 84, 'reasons': 'Solid software engineering fundamentals and project experience.'}
        ],
        'skill_gaps': [
            {'skill': 'Power BI / Tableau', 'priority': 'High', 'status': 'Missing'},
            {'skill': 'Advanced SQL Window Functions', 'priority': 'Medium', 'status': 'Developing'},
            {'skill': 'Statistics & Probability', 'priority': 'High', 'status': 'Developing'},
            {'skill': 'Machine Learning Algorithms', 'priority': 'Medium', 'status': 'Developing'}
        ],
        'cv_score': 78,
        'cv_analysis': "Solid educational foundation and core programming skills. Needs more quantifiable project outcomes and professional experience details.",
        'readiness_score': 82,
        'chat_history': [
            {"role": "assistant", "content": "Hello Alex! I am your LCS Intelligent Agent. How can I assist your study or career goals today?"}
        ],
        'agent_open': False,
        'rag_docs': []
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# Helper function for Groq LLM API
def call_groq_llm(prompt, system_prompt="You are an intelligent educational and career advisor AI for Learning & Career Studio (LCS)."):
    api_key = st.session_state.get('groq_api_key', '')
    if not api_key:
        return "⚠️ Groq API key is not configured. Please set the GROQ_API_KEY environment variable or enter it in the top settings."
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error contacting Groq API: {str(e)}"

# ------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: #182B49; margin-bottom: 0;'>🎓 LCS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6C63FF; font-weight: 600; font-size: 0.85rem;'>Learning & Career Studio</p>", unsafe_allow_html=True)
    st.divider()

    # Groq API Key Input
    if not st.session_state['groq_api_key']:
        api_input = st.text_input("Enter Groq API Key", type="password", key="groq_key_input")
        if api_input:
            st.session_state['groq_api_key'] = api_input
            st.rerun()
    else:
        st.success("Groq API Connected", icon="✅")

    st.markdown("### 📌 NAVIGATION")
    nav = st.radio(
        "Select Section",
        [
            "Dashboard",
            "My Profile",
            "Study Workspace",
            "Study Roadmap & Planner",
            "Quizzes & Mock Exams",
            "PDF Material & RAG",
            "Career Discovery & Skills",
            "CV & Job Matcher",
            "Interview Intelligence",
            "Analytics & Next Action"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    # Agent Quick Trigger Button
    if st.button("💬 Toggle LCS Agent Panel", use_container_width=True):
        st.session_state['agent_open'] = not st.session_state['agent_open']

# ------------------------------------------------------------------------------
# TOP BAR & HEADER
# ------------------------------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"<h1 style='color: #182B49; font-size: 2rem; margin-bottom: 0;'>Learning & Career Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #5A6B82; font-size: 1rem;'>Intelligent Student Ecosystem — School to Career Mastery</p>", unsafe_allow_html=True)

with col_head2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 10px;">
        <span style="background-color: #F4F1FA; color: #6C63FF; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
            👤 {st.session_state.profile['name']} ({st.session_state.profile['degree']})
        </span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------------------
# RIGHT-SIDE / FLOATING LIVE LCS AGENT WIDGET
# ------------------------------------------------------------------------------
if st.session_state['agent_open']:
    with st.expander("🤖 LCS Intelligent Agent (Context-Aware Assistant)", expanded=True):
        st.markdown("""
        <div style="background-color: #182B49; color: white; padding: 10px 15px; border-radius: 8px 8px 0 0; font-weight: 600;">
            💬 LCS Live Agent | Personal Mentor & Assistant
        </div>
        """, unsafe_allow_html=True)
        
        chat_container = st.container(height=300)
        for msg in st.session_state.chat_history:
            with chat_container.chat_message(msg["role"]):
                st.write(msg["content"])

        user_query = st.chat_input("Ask LCS about studies, weak topics, career roadmap, CV or jobs...", key="agent_chat_input")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Construct context
            context_prompt = f"""
            Student Context:
            - Name: {st.session_state.profile['name']}
            - Level: {st.session_state.profile['edu_level']} ({st.session_state.profile['degree']}, {st.session_state.profile['semester']})
            - Weak Topics: {', '.join(st.session_state.weak_topics)}
            - Career Goal: {st.session_state.profile['career_goal']}
            - Skill Gaps: {[g['skill'] for g in st.session_state.skill_gaps]}
            - Readiness Score: {st.session_state.readiness_score}%

            User Query: {user_query}

            Provide a direct, practical, and highly personalized mentor response. Support English, Urdu, or Roman Urdu as requested.
            """
            
            with st.spinner("LCS Agent thinking..."):
                reply = call_groq_llm(context_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

# ------------------------------------------------------------------------------
# 1. DASHBOARD NAVIGATION VIEW
# ------------------------------------------------------------------------------
if nav == "Dashboard":
    st.markdown("<h2 class='lcs-header'>📊 Executive Student Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Overview of learning momentum, skill acquisition, and career readiness.</p>", unsafe_allow_html=True)

    # KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">76%</div>
            <div class="metric-label">Study Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value" style="color: #19B5A5;">84%</div>
            <div class="metric-label">Skill Strength</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value" style="color: #E8A4C4;">91%</div>
            <div class="metric-label">Top Career Match</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #6C63FF;">{st.session_state.readiness_score}%</div>
            <div class="metric-label">Career Readiness</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Next Best Action Card
    st.markdown("""
    <div class="lcs-card-highlight">
        <h4 style="margin:0 0 5px 0; color: #182B49;">⚡ Next Best Action Recommendation</h4>
        <p style="margin:0; font-size: 0.95rem; color: #4A5568;">
            <b>Focus Area: SQL JOINs & Power BI Skill Gap</b><br>
            Your recent quiz showed weaknesses in relational joins, while your target role (Data Analyst) requires Power BI mastery.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='lcs-header'>📚 Academic Progress by Subject</h3>", unsafe_allow_html=True)
        df_prog = pd.DataFrame({
            'Subject': ['Database Systems', 'Algorithms', 'Data Science', 'Software Eng.'],
            'Mastery (%)': [65, 80, 75, 85]
        })
        fig = px.bar(df_prog, x='Mastery (%)', y='Subject', orientation='h', color='Mastery (%)',
                     color_continuous_scale=['#D8B4E2', '#6C63FF', '#182B49'])
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d2:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='lcs-header'>🎯 Target Career Match Alignment</h3>", unsafe_allow_html=True)
        cm_df = pd.DataFrame(st.session_state.career_matches)
        fig_pie = px.pie(cm_df, values='match', names='title', color_discrete_sequence=['#6C63FF', '#19B5A5', '#E8A4C4', '#D8B4E2'])
        fig_pie.update_layout(height=250, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Weak Topics Summary
    st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='lcs-header'>⚠️ Detected Weak Topics Needing Revision</h3>", unsafe_allow_html=True)
    cols = st.columns(len(st.session_state.weak_topics))
    for idx, topic in enumerate(st.session_state.weak_topics):
        with cols[idx]:
            st.warning(f"**{topic}**

*Action Required: Take practice quiz & review notes.*")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. MY PROFILE
# ------------------------------------------------------------------------------
elif nav == "My Profile":
    st.markdown("<h2 class='lcs-header'>👤 Student Profile & Preferences</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Configure academic credentials, current skills, and career direction.</p>", unsafe_allow_html=True)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=st.session_state.profile['name'])
            edu_level = st.selectbox("Education Level", ["School", "College / Intermediate", "University"], index=2)
            institution = st.text_input("School / College / University Name", value=st.session_state.profile['institution'])
            degree = st.text_input("Degree / Program / Class", value=st.session_state.profile['degree'])
            semester = st.text_input("Semester / Grade", value=st.session_state.profile['semester'])
            gpa = st.text_input("GPA / Marks (Optional)", value=st.session_state.profile['gpa'])

        with col2:
            subjects_str = st.text_area("Enrolled Subjects (comma-separated)", value=", ".join(st.session_state.profile['subjects']))
            skills_str = st.text_area("Current Skills (comma-separated)", value=", ".join(st.session_state.profile['skills']))
            interests_str = st.text_area("Interests (comma-separated)", value=", ".join(st.session_state.profile['interests']))
            career_goal = st.text_input("Primary Target Career Goal", value=st.session_state.profile['career_goal'])
            work_type = st.selectbox("Preferred Work Type", ["Remote", "Hybrid", "On-site"], index=1)

        submitted = st.form_submit_button("Save & Update Profile Intelligence")
        if submitted:
            st.session_state.profile.update({
                'name': name,
                'edu_level': edu_level,
                'institution': institution,
                'degree': degree,
                'semester': semester,
                'gpa': gpa,
                'subjects': [s.strip() for s in subjects_str.split(',') if s.strip()],
                'skills': [s.strip() for s in skills_str.split(',') if s.strip()],
                'interests': [i.strip() for i in interests_str.split(',') if i.strip()],
                'career_goal': career_goal,
                'work_type': work_type
            })
            st.success("Profile saved successfully! Intelligence modules updated.")

# ------------------------------------------------------------------------------
# 3. STUDY WORKSPACE
# ------------------------------------------------------------------------------
elif nav == "Study Workspace":
    st.markdown("<h2 class='lcs-header'>📖 Intelligent Study Workspace</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Deep-dive into subject topics with automated AI explanations and key summaries.</p>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        selected_subject = st.selectbox("Select Subject", st.session_state.profile['subjects'])
        
        topics_dict = {
            'Database Systems': ['SQL JOINs', 'Normalization', 'Indexing', 'Transactions & ACID'],
            'Algorithms': ['Sorting & Searching', 'Dynamic Programming', 'Graph Algorithms', 'Trees & Heaps'],
            'Data Science': ['Pandas & Numpy', 'Data Cleaning', 'Machine Learning Basics', 'Data Visualization'],
            'Software Engineering': ['Agile Methodology', 'Design Patterns', 'Software Testing', 'CI/CD Pipelines']
        }
        
        available_topics = topics_dict.get(selected_subject, ['General Overview', 'Core Concepts'])
        selected_topic = st.selectbox("Select Topic", available_topics)
        
        st.markdown("---")
        action_mode = st.radio("Action", ["Topic Explanation & Examples", "Generate Concise Notes", "Quick Revision Flashcards"])
        generate_btn = st.button("Generate Study Insights")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_s2:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        if generate_btn:
            with st.spinner("Generating conceptual explanation from Groq OSS 120B..."):
                prompt = f"""
                Provide a structured educational guide for:
                Subject: {selected_subject}
                Topic: {selected_topic}
                Mode: {action_mode}

                Format clearly with:
                - Key Concepts
                - Real-World Example
                - Code snippet / Diagram representation if applicable
                - Common Exam Pitfalls
                """
                response = call_groq_llm(prompt)
                st.markdown(response)
        else:
            st.info("👈 Select a subject and topic, then click 'Generate Study Insights' to begin.")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. STUDY ROADMAP & PLANNER
# ------------------------------------------------------------------------------
elif nav == "Study Roadmap & Planner":
    st.markdown("<h2 class='lcs-header'>🗺️ Dynamic Study Roadmap & Planner</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Adaptive learning timeline based on mastery levels and upcoming exams.</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Interactive Topic Roadmap", "Exam Prep Planner Generator"])

    with tab1:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### Subject Topic Master Map")
        
        for subj, topics in st.session_state.study_progress.items():
            st.markdown(f"#### 📘 {subj}")
            cols = st.columns(len(topics))
            for i, (topic_name, status) in enumerate(topics.items()):
                color = "#19B5A5" if status == "Strong" else "#6C63FF" if status == "Learning" else "#E8A4C4" if status == "Needs Revision" else "#A0AEC0"
                with cols[i]:
                    st.markdown(f"""
                    <div style="border: 1px solid #CBD5E0; border-top: 4px solid {color}; border-radius: 6px; padding: 10px; text-align: center; background: white;">
                        <b style="font-size: 0.9rem;">{topic_name}</b><br>
                        <span style="font-size:0.75rem; color:{color}; font-weight:600;">{status}</span>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📅 Automated Study Schedule Generator")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            exam_days = st.number_input("Days Remaining Until Exam", min_value=1, max_value=60, value=14)
            daily_hours = st.slider("Available Daily Study Hours", 1, 10, 3)
        with col_p2:
            target_subjects = st.multiselect("Select Subjects to Cover", st.session_state.profile['subjects'], default=st.session_state.profile['subjects'][:2])
            focus_weak = st.checkbox("Prioritize Weak Topics Automatically", value=True)

        if st.button("Generate Optimized Study Plan"):
            with st.spinner("Calculating optimal study schedule..."):
                prompt = f"""
                Create a day-by-day study timetable for {exam_days} days.
                Daily Study Capacity: {daily_hours} hours/day.
                Subjects: {', '.join(target_subjects)}
                Weak Topics to Prioritize: {', '.join(st.session_state.weak_topics)}
                Structure it as:
                - Day Range
                - Focus Topics
                - Daily Activity (Learning, Revision, Practice Quiz)
                """
                plan = call_groq_llm(prompt)
                st.markdown(plan)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. QUIZZES & MOCK EXAMS
# ------------------------------------------------------------------------------
elif nav == "Quizzes & Mock Exams":
    st.markdown("<h2 class='lcs-header'>✏️ Quiz Generator & Adaptive Mock Exams</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Test knowledge, receive immediate evaluation, and update weak topic detection.</p>", unsafe_allow_html=True)

    st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        q_subj = st.selectbox("Subject", st.session_state.profile['subjects'], key="q_subj")
    with col_q2:
        q_topic = st.selectbox("Topic", ['SQL JOINs', 'Dynamic Programming', 'Pandas & Numpy', 'Agile Methodology'])
    with col_q3:
        q_diff = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

    if st.button("Generate Quiz Questions"):
        with st.spinner("Generating customized quiz..."):
            prompt = f"Generate 3 multiple choice questions for subject {q_subj}, topic {q_topic}, level {q_diff}. Include choices A, B, C, D and indicate correct answer at the end."
            quiz_content = call_groq_llm(prompt)
            st.session_state['current_quiz'] = quiz_content

    if 'current_quiz' in st.session_state:
        st.markdown("### 📝 Quiz Session")
        st.markdown(st.session_state['current_quiz'])
        
        st.markdown("---")
        st.markdown("#### Submit Answers for Auto-Evaluation")
        user_ans = st.text_area("Enter your answers (e.g., 1. A, 2. C, 3. B)")
        
        if st.button("Submit & Evaluate Quiz"):
            with st.spinner("Evaluating responses..."):
                eval_prompt = f"""
                Evaluate these student answers against the quiz.
                Quiz: {st.session_state['current_quiz']}
                Student Answers: {user_ans}

                Provide:
                1. Score (e.g. 2/3)
                2. Detailed Explanations
                3. Strong vs Weak Topic identification based on errors.
                """
                eval_res = call_groq_llm(eval_prompt)
                st.markdown(eval_res)
                
                # Add score entry
                st.session_state.quiz_results.append({'subject': q_subj, 'topic': q_topic, 'score': 'Evaluated'})
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. PDF MATERIAL & RAG
# ------------------------------------------------------------------------------
elif nav == "PDF Material & RAG":
    st.markdown("<h2 class='lcs-header'>📚 PDF Material RAG Intelligence</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Upload lecture slides or notes to query, summarize, or extract quiz questions.</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Course Material (PDF)", type=["pdf"])

    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "
"
            
            st.session_state['rag_text'] = extracted_text
            st.success(f"Successfully processed PDF! Extracted {len(extracted_text)} characters.")
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

    if 'rag_text' in st.session_state and st.session_state['rag_text']:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 🔍 Ask Questions from Uploaded PDF")
        pdf_query = st.text_input("Ask anything grounded in your uploaded document:")
        
        col_rag1, col_rag2 = st.columns(2)
        with col_rag1:
            if st.button("Answer Query"):
                if pdf_query:
                    with st.spinner("Searching document context..."):
                        # Lightweight chunk grounding
                        doc_snippet = st.session_state['rag_text'][:4000] # Fit in context
                        prompt = f"Document Context:
{doc_snippet}

Question: {pdf_query}
Answer based ONLY on the context provided:"
                        ans = call_groq_llm(prompt)
                        st.markdown(ans)
        with col_rag2:
            if st.button("Generate Notes & Summary"):
                with st.spinner("Summarizing document..."):
                    doc_snippet = st.session_state['rag_text'][:4000]
                    prompt = f"Document Context:
{doc_snippet}

Provide key revision bullet points and concise summary:"
                    summary = call_groq_llm(prompt)
                    st.markdown(summary)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 7. CAREER DISCOVERY & SKILLS
# ------------------------------------------------------------------------------
elif nav == "Career Discovery & Skills":
    st.markdown("<h2 class='lcs-header'>🎯 Career Discovery & Skill Gap Matrix</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Discover high-alignment career paths and pinpoint technical skill gaps.</p>", unsafe_allow_html=True)

    col_cd1, col_cd2 = st.columns([1, 1])

    with col_cd1:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 🧭 Recommended Career Pathways")
        for match in st.session_state.career_matches:
            st.markdown(f"""
            <div style="border: 1px solid #EAEFF5; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #182B49;">{match['title']}</h4>
                    <span style="background: #FCEAF3; color: #E8A4C4; padding: 4px 10px; border-radius: 12px; font-weight: bold;">
                        {match['match']}% Match
                    </span>
                </div>
                <p style="font-size: 0.85rem; color: #5A6B82; margin-top: 5px;">{match['reasons']}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cd2:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### ⚠️ Skill Gap Analysis (Target: Data Analyst)")
        
        gap_df = pd.DataFrame(st.session_state.skill_gaps)
        st.dataframe(gap_df, use_container_width=True)

        if st.button("Recommend Portfolio Projects for Skill Gaps"):
            with st.spinner("Finding optimal projects..."):
                prompt = f"""
                Target Career: {st.session_state.profile['career_goal']}
                Missing Skills: {[g['skill'] for g in st.session_state.skill_gaps]}
                
                Suggest 2 actionable portfolio projects with:
                - Title
                - Tech Stack
                - Key Features
                - Portfolio Value
                """
                projects = call_groq_llm(prompt)
                st.markdown(projects)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 8. CV & JOB MATCHER
# ------------------------------------------------------------------------------
elif nav == "CV & Job Matcher":
    st.markdown("<h2 class='lcs-header'>📄 CV Analyzer & Job Match Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Evaluate your CV alignment and match against target job descriptions.</p>", unsafe_allow_html=True)

    tab_cv1, tab_cv2 = st.tabs(["CV Analysis & Score", "Job Description Matcher"])

    with tab_cv1:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### Upload & Audit Resume / CV")
        cv_file = st.file_uploader("Upload CV (PDF)", type=["pdf"], key="cv_uploader")
        
        if cv_file:
            reader = PdfReader(cv_file)
            cv_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.success("CV Extracted Successfully!")
            
            if st.button("Analyze CV Quality"):
                with st.spinner("Auditing CV content..."):
                    prompt = f"Audit this CV text for a student targeting {st.session_state.profile['career_goal']}:

{cv_text[:3000]}

Provide: CV Score out of 100, Strengths, Weaknesses, and Formatting / Action Bullet improvements."
                    cv_res = call_groq_llm(prompt)
                    st.markdown(cv_res)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_cv2:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### Match Profile with Target Job Description")
        jd_text = st.text_area("Paste Target Job Description (JD) here:", height=180)
        
        if st.button("Calculate Match & Skill Fit"):
            if jd_text:
                with st.spinner("Matching skills with Job Description..."):
                    prompt = f"""
                    Student Skills: {', '.join(st.session_state.profile['skills'])}
                    Student Projects: {', '.join(st.session_state.profile['projects'])}
                    Job Description: {jd_text}

                    Provide:
                    1. Overall Match Percentage
                    2. Matching Skills Checkmarks
                    3. Missing Required Skills
                    4. Recommended Cover Letter Bullet Points
                    """
                    jd_res = call_groq_llm(prompt)
                    st.markdown(jd_res)
            else:
                st.warning("Please paste a job description first.")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 9. INTERVIEW INTELLIGENCE
# ------------------------------------------------------------------------------
elif nav == "Interview Intelligence":
    st.markdown("<h2 class='lcs-header'>🎤 Mock Interview Simulator</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Practise HR, technical, and behavioral interview questions with AI evaluation.</p>", unsafe_allow_html=True)

    st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
    interview_type = st.selectbox("Select Interview Focus", ["Technical Questions", "Behavioral (STAR Method)", "HR & Soft Skills"])
    
    if st.button("Generate Practice Questions"):
        with st.spinner("Preparing interview question..."):
            prompt = f"Generate 1 key {interview_type} interview question for a {st.session_state.profile['career_goal']} candidate."
            q = call_groq_llm(prompt)
            st.session_state['interview_question'] = q

    if 'interview_question' in st.session_state:
        st.markdown("### ❓ Question")
        st.info(st.session_state['interview_question'])
        
        user_response = st.text_area("Your Response / Answer:")
        if st.button("Evaluate Answer & Feedback"):
            with st.spinner("Evaluating interview response..."):
                eval_p = f"""
                Question: {st.session_state['interview_question']}
                User Response: {user_response}

                Rate the response out of 10 and give actionable feedback to improve clarity, technical depth, or structure.
                """
                feedback = call_groq_llm(eval_p)
                st.markdown(feedback)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 10. ANALYTICS & NEXT ACTION
# ------------------------------------------------------------------------------
elif nav == "Analytics & Next Action":
    st.markdown("<h2 class='lcs-header'>📈 Platform Analytics & Continuous Guidance</h2>", unsafe_allow_html=True)
    st.markdown("<p class='lcs-subheader'>Comprehensive readiness tracking and next best action engine.</p>", unsafe_allow_html=True)

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Career Readiness Score Breakdown")
        
        readiness_data = pd.DataFrame({
            'Metric': ['Skills Alignment', 'Project Portfolio', 'Education', 'CV Quality', 'Interview Practice'],
            'Score': [88, 80, 92, 84, 78]
        })
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=readiness_data['Score'],
            theta=readiness_data['Metric'],
            fill='toself',
            fillcolor='rgba(108, 99, 255, 0.3)',
            line=dict(color='#6C63FF')
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_a2:
        st.markdown("<div class='lcs-card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Priority Action List")
        st.markdown("""
        1. **Revise Relational SQL JOINs**  
           *Reason:* Quiz performance indicates ambiguity in multi-table queries.
        2. **Build Power BI Analytics Project**  
           *Reason:* Fills the high-priority skill gap for target Data Analyst role.
        3. **Practise Behavioral Interview STAR Answers**  
           *Reason:* Boost interview readiness score above 85%.
        """)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# FOOTER / CREDIT
# ------------------------------------------------------------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.85rem; padding: 10px 0;">
    Designed & Developed by Areeba Imran<br>
    © 2026 Learning & Career Studio (LCS). All rights reserved.
</div>
""", unsafe_allow_html=True)
