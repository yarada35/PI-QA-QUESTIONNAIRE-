import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(
    page_title="PIQA Analytics & Survey Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injection for Premium Black/Dark UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=400;600;700&family=Syne:wght=700;800&family=Inter:wght=400;500;600;700&display=swap');
    
    .stApp {
        background-color: #05070F !important;
        color: #F1F5F9 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #090D16 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] + div label p {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #FBBF24 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-shadow: 0px 0px 8px rgba(251, 191, 36, 0.6) !important;
    }
    
    .main h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #34D399 50%, #FBBF24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        letter-spacing: -0.05em;
        margin-bottom: 0.5rem;
    }
    
    .section-title {
        font-family: 'Syne', sans-serif;
        color: #F8FAFC;
        font-size: 1.5rem;
        font-weight: 700;
        border-bottom: 2px solid #38BDF8;
        padding-bottom: 0.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    body, p, label {
        font-family: 'Inter', sans-serif;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        padding: 12px 24px !important;
        font-family: 'Syne', sans-serif !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #34D399 !important;
        border-bottom: 4px solid #34D399 !important;
        text-shadow: 0px 0px 12px rgba(52, 211, 153, 0.6);
    }
    
    .metric-card {
        background: #111827;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #1E293B;
        border-left: 6px solid #38BDF8;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .question-block {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
    }

    .question-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        font-weight: 500;
        color: #F8FAFC;
    }

    .scale-legend {
        background-color: #090D16;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-around;
        font-size: 0.85rem;
        color: #CBD5E1;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Hardcoded Survey Matrix Verbatim Mapping
DEPARTMENT_QUESTIONS = {
    "Plant Engineering Department": [
        "Provide technical data and specification as per the request",
        "Cooperation in mould cleaning check up to shorten its change time",
        "Communication is on time to deliver the request service",
        "Provide support based on request",
        "Test result is given for plant engineering on time",
        "Active participation in cross functional team to address common plant problems",
        "Satisfaction on overall relationship with the department"
    ],
    "Production Department": [
        "Recipes/Specifications/ Work instructions are updated periodically and understandable for users",
        "Helpful work instructions are prepared by considering quality with productivity",
        "Root cause analysis & prevention work in collaboration with CFT team",
        "There is cooperation with production team to reduce waste",
        "Work instructions are prepared based on good practices of the company",
        "Recommendations are given for nonconforming Semi finished products on time",
        "Materials are released for production as per laboratory testing time and material rest time",
        "Gaps seen in the process are highlighted for correction to be taken",
        "Providing gap base training as per request for production staffs."
    ],
    "Sales and Marketing Department": [
        "Provide technical data and specification as per the request",
        "Response for product quality improvement as per request",
        "Communication is on time about new products",
        "Provide technical support based on request",
        "Claim tire inspection and on time feedback.",
        "Actively participating on field and customer support activities",
        "Satisfaction on overall relationship with the department"
    ],
    "PIQA Employee Staff": [
        "I have immediate access to calibrated testing equipment required for my shift operations.",
        "The internal workspace, ventilation, and physical safety barriers support optimized execution.",
        "Shift assignment transitions and inter-departmental communications are clear and structured.",
        "Management consistently supports upskilling regarding changes in compound mixtures or compound recipes."
    ],
    "Purchase Department": [
        "PIQA delivers technical data and raw material inspection specifications quickly.",
        "The chemical and mechanical laboratory feedback loops for vendor samples align with purchasing timelines.",
        "Supplier Non-Conformance Reports (NCR) are detailed objectively to support raw material claims.",
        "Overall collaborative alignment on alternative material sourcing during supply line updates is positive."
    ],
    "Store Department": [
        "The testing processing times for incoming raw materials prevent compound inventory stagnations.",
        "Clear tags, visual indicators, and status updates are provided for quarantined/non-conforming stock.",
        "PIQA personnel follow warehouse zoning restrictions and material rest timelines accurately.",
        "Clear technical directions are provided for handling aging inventories or compound batch releases."
    ]
}

emoji_options = ["1 🤬", "2 🙁", "3 😐", "4 🙂", "5 🤩"]
emoji_clean_map = {"1": "🤬", "2": "🙁", "3": "😐", "4": "🙂", "5": "🤩"}

# 3. Securely Initialize Connection natively from Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read live dataset dynamically (Bypass cache)
try:
    df = conn.read(ttl="0d")
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
except Exception as e:
    df = pd.DataFrame(columns=["RespondentID", "Department", "Question Number", "Criteria Description", "Score", "Emoji", "Sentiment", "Tenure"])

def clear_global_filters():
    for k in ["dash_dept_radio", "dash_tenure_seg"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# Layout Headers
st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; font-size:1.1rem; margin-bottom: 1.5rem;'>Unified suite for live operational analysis and internal raw feedback collection loops.</p>", unsafe_allow_html=True)

# 4. Sidebar Controls
with st.sidebar:
    st.markdown("<h2 style='font-family:\"Syne\"; color:#38BDF8; margin-top:0;'>🎨 Control Room</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    
    selected_dept = st.radio(
        label="Target Departments Filter",
        options=['All Matrix Mix'] + list(DEPARTMENT_QUESTIONS.keys()),
        key="dash_dept_radio"
    )
    
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    selected_tenure = st.segmented_control(
        label="Employee Tenure Filter",
        options=['All Mix', '< 1 Year', '1-3 Years', '3+ Years'],
        default='All Mix',
        key="dash_tenure_seg"
    )
    
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    st.button("🔄 Clear App Filters", on_click=clear_global_filters, use_container_width=True)

# Process Filter Slices
filtered_df = df.dropna(subset=['Score']).copy() if not df.empty else df.copy()
if selected_dept != 'All Matrix Mix':
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_tenure != 'All Mix':
    filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

# Structural View Management Tabs
tab_dash, tab_survey, tab_print = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print & Distribution Hub"])

# ==========================================
# VIEW 1: LIVE ANALYTICS DASHBOARD
# ==========================================
with tab_dash:
    if filtered_df.empty:
        st.warning("📥 No live submissions recorded yet. Share the 'Interactive Survey Intake' tab with your departments to collect feedback!")
    else:
        distinct_active_respondents = filtered_df['RespondentID'].nunique()
        avg_score = round(filtered_df['Score'].mean(), 2)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Composite Mean Score</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{avg_score} <span style="font-size:1.2rem; color:#38BDF8;">/ 5.0</span></h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#34D399; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Total Sample Respondents</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{distinct_active_respondents} <span style="font-size:1.1rem; color:#94A3B8;">Staff</span></h2></div>', unsafe_allow_html=True)
        with col3:
            pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / len(filtered_df)) * 100)
            st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Satisfaction Index</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{pos_pct}%</h2></div>', unsafe_allow_html=True)
        with col4:
            mode_score = int(filtered_df['Score'].mode()[0])
            st.markdown(f'<div class="metric-card" style="border-left-color: #FBBF24;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Dominant Sentiment</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">Level {mode_score}</h2></div>', unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📋 Response Volume Layout Breakdown</div>", unsafe_allow_html=True)
        respondent_matrix = filtered_df.groupby(['Department', 'Tenure'])['RespondentID'].nunique().unstack(fill_value=0)
        st.dataframe(respondent_matrix, use_container_width=True)

        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("<div class='section-title'>📊 Average Ratings by Query Breakdown</div>", unsafe_allow_html=True)
            question_chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index().sort_values(by='Score')
            fig_bar = px.bar(question_chart_data, x='Score', y='Criteria Description', orientation='h', color='Score', color_continuous_scale='Blues', range_x=[1,5], template="plotly_dark")
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter", yaxis=dict(showticklabels=False))
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.markdown("<div class='section-title'>🍕 Proportion Summary</div>", unsafe_allow_html=True)
            sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
            fig_pie = px.pie(sentiment_data, values='count', names='Sentiment', hole=0.5, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# VIEW 2: INTERACTIVE SURVEY INTAKE
# ==========================================
with tab_survey:
    st.markdown("<div class='section-title'>📝 Live Questionnaire Engine</div>", unsafe_allow_html=True)
    
    col_surv_dept, col_surv_tenure = st.columns(2)
    with col_surv_dept:
        survey_dept = st.selectbox("Identify Your Active Department Hub:", list(DEPARTMENT_QUESTIONS.keys()))
    with col_surv_tenure:
        survey_tenure = st.selectbox("Your Plant Operational Tenure Profile:", ["< 1 Year", "1-3 Years", "3+ Years"])
        
    st.markdown("<div class='scale-legend'><span><b>1</b> 🤬 Strongly Disagree</span><span><b>2</b> 🙁 Disagree</span><span><b>3</b> 😐 Neutral</span><span><b>4</b> 🙂 Agree</span><span><b>5</b> 🤩 Strongly Agree</span></div>", unsafe_allow_html=True)
    
    with st.form("interactive_intake_form", clear_on_submit=True):
        survey_responses = {}
        active_questions = DEPARTMENT_QUESTIONS[survey_dept]
        
        for idx, question in enumerate(active_questions):
            st.markdown(f'<div class="question-block"><div class="question-text"><b>Q{idx+1}.</b> {question}</div></div>', unsafe_allow_html=True)
            score_selection = st.segmented_control(label=f"Rating for Q{idx+1}", options=emoji_options, key=f"live_q_{idx+1}", label_visibility="collapsed")
            survey_responses[idx] = {"criteria": question, "selected": score_selection}
            st.markdown("<br>", unsafe_allow_html=True)
            
        submit_survey_btn = st.form_submit_button("Submit Operational Evaluation Log")
        
    if submit_survey_btn:
        incomplete = [q for q, val in survey_responses.items() if val["selected"] is None]
        if incomplete:
            st.error("⚠️ Please answer all survey evaluation fields before submission.")
        else:
            new_rows = []
            resp_id = f"RSP_{datetime.now().strftime('%m%d_%H%M%S')}"
            
            for idx, val in survey_responses.items():
                raw_score_str = val["selected"][0] 
                score_int = int(raw_score_str)
                sentiment = "Positive" if score_int > 3 else ("Neutral" if score_int == 3 else "Negative")
                
                new_rows.append({
                    "RespondentID": resp_id,
                    "Department": survey_dept,
                    "Question Number": f"Q{idx+1}",
                    "Criteria Description": val["criteria"],
                    "Score": score_int,
                    "Emoji": emoji_clean_map[raw_score_str],
                    "Sentiment": sentiment,
                    "Tenure": survey_tenure
                })
            
            # Append rows back to the primary Google Sheet live
            new_df = pd.DataFrame(new_rows)
            updated_master_df = pd.concat([df, new_df], ignore_index=True)
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=updated_master_df)
            
            st.success("🎉 Evaluation captured securely inside the cloud database! Refresh page to update metrics.")
            st.balloons()

# ==========================================
# VIEW 3: PRINT & EXPORT
# ==========================================
with tab_print:
    st.markdown("<div class='section-title'>🖨️ Document Generation Center</div>", unsafe_allow_html=True)
    if not filtered_df.empty:
        st.download_button("📥 Export Current Slice Dataset to CSV", data=filtered_df.to_csv(index=False).encode('utf-8'), file_name="PIQA_Live_Data.csv", mime="text/csv")
    else:
        st.write("No active records available to download.")
