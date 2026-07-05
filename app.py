import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from datetime import datetime

# ==========================================
# 1. PAGE SETUP & THEME INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="PIQA Real-Time Analytics Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark industrial high-contrast theme styling rules
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=400;600;700&family=Syne:wght=700;800&family=Inter:wght=400;500;600;700&display=swap');
    
    .stApp { background-color: #05070F !important; color: #F1F5F9 !important; }
    [data-testid="stSidebar"] { background-color: #090D16 !important; border-right: 1px solid #1E293B !important; }
    
    /* Glowing gold sidebar header labels */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] + div label p {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #FBBF24 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-shadow: 0px 0px 8px rgba(251, 191, 36, 0.5) !important;
    }
    
    .main h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #34D399 50%, #FBBF24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        letter-spacing: -0.05em;
    }
    
    .section-title {
        font-family: 'Syne', sans-serif;
        color: #F8FAFC;
        font-size: 1.4rem;
        font-weight: 700;
        border-bottom: 2px solid #38BDF8;
        padding-bottom: 0.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1.2rem;
    }

    .metric-card {
        background: #111827;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #1E293B;
        border-left: 6px solid #38BDF8;
    }
    .question-block { background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 16px; margin-bottom: 0.8rem; }
    .scale-legend { background-color: #090D16; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 1.5rem; display: flex; justify-content: space-around; font-size: 0.85rem; color: #CBD5E1; }
    body, p, label { font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SURVEY MATRIX METADATA DEFINITION
# ==========================================
DEPARTMENT_QUESTIONS = {
    "Plant Engineering Department": [
        "Provide technical data and specification as per the request",
        "Cooperation in mould cleaning check up to shorten its change time",
        "Communication is on time to deliver the request service",
        "Provide support based on request"
    ],
    "Production Department": [
        "Recipes/Specifications/ Work instructions are updated periodically and understandable for users",
        "Helpful work instructions are prepared by considering quality with productivity",
        "Root cause analysis & prevention work in collaboration with CFT team"
    ],
    "Sales and Marketing Department": [
        "Provide technical data and specification as per the request",
        "Response for product quality improvement as per request",
        "Claim tire inspection and on time feedback."
    ]
}

emoji_options = ["1 🤬", "2 🙁", "3 😐", "4 🙂", "5 🤩"]
emoji_map = {1: "🤬", 2: "🙁", 3: "😐", 4: "🙂", 5: "🤩"}

# ==========================================
# 3. GLOBAL REAL-TIME DATA HUB (SHARED MEMORY)
# ==========================================
@st.cache_resource
def get_global_realtime_database():
    """Initializes a shared in-memory dataset that persists across all cloud user connections."""
    np.random.seed(101)
    records = []
    tenures = ['< 1 Year', '1-3 Years', '3+ Years']
    
    # Pre-populate base matrix with realistic sample trends
    for dept, questions in DEPARTMENT_QUESTIONS.items():
        for tenure in tenures:
            for resp_id in range(5):
                uid = f"SEED_{dept[:3].upper()}_{tenure[:2]}_{resp_id}"
                for q_idx, q in enumerate(questions):
                    score = int(np.random.choice([1, 2, 3, 4, 5], p=[0.04, 0.06, 0.15, 0.45, 0.30]))
                    records.append({
                        "RespondentID": uid, "Department": dept, "Question Number": f"Q{q_idx + 1}",
                        "Criteria Description": q, "Score": score, "Emoji": emoji_map[score],
                        "Sentiment": "Positive" if score > 3 else ("Neutral" if score == 3 else "Negative"),
                        "Tenure": tenure
                    })
    return records

# Retrieve the reference to the persistent memory block
global_db_reference = get_global_realtime_database()
df = pd.DataFrame(global_db_reference)

# ==========================================
# 4. SIDEBAR CONTROL ROOM FILTERS
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='font-family:\"Syne\"; color:#38BDF8; margin-top:0;'>🎨 Control Room</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    st.markdown("<b style='color:#F1F5F9; font-size: 0.95rem;'>🎨 Dashboard Filters</b>", unsafe_allow_html=True)
    
    selected_dept = st.radio("Target Department Hub:", ['All Matrix Mix'] + list(DEPARTMENT_QUESTIONS.keys()), key="dash_dept_radio")
    selected_tenure = st.segmented_control("Tenure Crosstab:", ['All Mix'] + list(df['Tenure'].unique()), default='All Mix', key="dash_tenure_seg")
    
    # Reset Action Pipeline
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    st.markdown("<b style='color:#FBBF24; font-size: 0.95rem;'>🔄 Reset Workspace</b>", unsafe_allow_html=True)
    
    if st.button("Reset Configuration", type="secondary", use_container_width=True):
        # Safe session parameter teardown loop
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# 5. RENDER SYSTEM PORTALS
# ==========================================
st.markdown("<h1>PIQA Matrix Interface Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; margin-bottom: 1.5rem;'>Live cloud synchronization pipeline active. Data charts refresh automatically across all clients upon new entry submission logs.</p>", unsafe_allow_html=True)

# Apply sidebar filter vectors dynamically over raw dataframe representation
filtered_df = df.copy()
if selected_dept != 'All Matrix Mix':
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_tenure != 'All Mix':
    filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

# Setup core operational tabs
tab_dash, tab_survey = st.tabs(["📊 Live Global Analytics Dashboard", "📝 Submit Real-Time Survey Feedback"])

# --- VIEW 1: LIVE GLOBAL ANALYTICS DASHBOARD ---
with tab_dash:
    # Layout metrics row
    m1, m2, m3 = st.columns(3)
    with m1:
        avg_val = round(filtered_df['Score'].mean(), 2) if not filtered_df.empty else 0.0
        st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size:0.8rem; text-transform:uppercase; margin:0;">Composite Score</p><h2>{avg_val} / 5.0</h2></div>', unsafe_allow_html=True)
    with m2:
        resp_count = filtered_df['RespondentID'].nunique()
        st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size:0.8rem; text-transform:uppercase; margin:0;">Active Database Sample Size</p><h2>{resp_count} Respondents</h2></div>', unsafe_allow_html=True)
    with m3:
        pos_ratio = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / len(filtered_df)) * 100) if not filtered_df.empty else 0
        st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size:0.8rem; text-transform:uppercase; margin:0;">Satisfaction Rating</p><h2>{pos_ratio}% Positive</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Visualization grids
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("<div class='section-title'>📊 Average Response Index across Monitored Parameters</div>", unsafe_allow_html=True)
        if not filtered_df.empty:
            chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index()
            fig_bar = px.bar(chart_data, x='Score', y='Criteria Description', orientation='h', color='Score', range_x=[1,5], color_continuous_scale='Blues', template='plotly_dark')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_showticklabels=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No active logs meet the sidebar tracking profile scope parameters.")
    with c2:
        st.markdown("<div class='section-title'>🍕 Global Sentiment Ratios</div>", unsafe_allow_html=True)
        if not filtered_df.empty:
            pie_data = filtered_df['Sentiment'].value_counts().reset_index()
            fig_pie = px.pie(pie_data, values='count', names='Sentiment', color='Sentiment', color_discrete_map={'Positive':'#34D399','Neutral':'#FBBF24','Negative':'#F87171'}, hole=0.4, template='plotly_dark')
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

# --- VIEW 2: INTERACTIVE SURVEY INPUTS ---
with tab_survey:
    st.markdown("<div class='section-title'>📝 Live Verification Logging Node</div>", unsafe_allow_html=True)
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        survey_dept = st.selectbox("Assign Active Target Unit:", list(DEPARTMENT_QUESTIONS.keys()))
    with s_col2:
        survey_tenure = st.selectbox("Plant Service Horizon Group:", ["< 1 Year", "1-3 Years", "3+ Years"])
        
    st.markdown("<div class='scale-legend'><span><b>1</b> 🤬 Strongly Disagree</span><span><b>3</b> 😐 Neutral</span><span><b>5</b> 🤩 Strongly Agree</span></div>", unsafe_allow_html=True)
    
    with st.form("cloud_realtime_form", clear_on_submit=True):
        form_scores = {}
        target_questions = DEPARTMENT_QUESTIONS[survey_dept]
        
        for index, question in enumerate(target_questions):
            st.markdown(f'<div class="question-block"><div class="question-text"><b>Q{index+1}.</b> {question}</div></div>', unsafe_allow_html=True)
            score_sel = st.segmented_control(label=f"Choice Q{index+1}", options=emoji_options, key=f"live_q_{index+1}", label_visibility="collapsed")
            form_scores[question] = score_sel
            
        submit_btn = st.form_submit_button("Broadcast Evaluation Log to Cloud Matrix")
        
    if submit_btn:
        is_valid = all(val is not None for val in form_scores.values())
        if not is_valid:
            st.error("⚠️ **Validation Failed:** Please make sure to input matching emoji metrics for all verification statements before broadcasting.")
        else:
            new_respondent_id = f"USER_{datetime.now().strftime('%M%S')}_{np.random.randint(10,99)}"
            
            # Append new records straight into global cached memory block
            for q_text, score_string in form_scores.items():
                extracted_score = int(score_string[0])
                global_db_reference.append({
                    "RespondentID": new_respondent_id,
                    "Department": survey_dept,
                    "Question Number": "Dynamic Entry",
                    "Criteria Description": q_text,
                    "Score": extracted_score,
                    "Emoji": emoji_map[extracted_score],
                    "Sentiment": "Positive" if extracted_score > 3 else ("Neutral" if extracted_score == 3 else "Negative"),
                    "Tenure": survey_tenure
                })
            
            st.success("🚀 **Payload Transmitted!** Survey records successfully written to global memory state. Switch tabs to see your entry computed in real-time charts.")
            st.rerun()
