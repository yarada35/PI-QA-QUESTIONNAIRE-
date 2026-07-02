import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from datetime import datetime

# 1. Page Configuration & Black/Dark Theme Base Initializer
st.set_page_config(
    page_title="PIQA Analytics & Survey Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Custom CSS Injection to force huge, ultra-bold, high-visibility text
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=Syne:wght@700;800&family=Inter:wght@700;800&display=swap');
    
    /* Force main app background wrapper to deep dark theme */
    .stApp {
        background-color: #05070F !important;
        color: #FFFFFF !important;
    }
    
    /* Main Dashboard Header Text */
    .main h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #34D399 50%, #FBBF24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }
    
    /* Make Section Titles Huge and Vibrant Cyan */
    .section-title {
        font-family: 'Syne', sans-serif;
        color: #38BDF8 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        border-bottom: 4px solid #38BDF8;
        padding-bottom: 0.6rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        text-shadow: 0px 0px 10px rgba(56, 189, 248, 0.3);
    }

    /* Force Every Piece of Paragraph/Standard Text to be Big and White */
    p, label, span, div {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    
    /* Make Streamlit Native Tab Text Massive and Readable */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        padding: 12px 24px !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #34D399 !important;
        border-bottom-color: #34D399 !important;
        text-shadow: 0px 0px 12px rgba(52, 211, 153, 0.5);
    }
    
    /* Huge Premium High-Contrast KPI Cards */
    .metric-card {
        background: #111827 !important;
        border-radius: 16px;
        padding: 30px;
        border: 2px solid #475569 !important;
        border-left: 10px solid #38BDF8 !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0;
    }

    /* Survey Intake Block Styling - Bright White Bold Content Text */
    .question-block {
        background: #1E293B !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 14px;
        padding: 26px;
        margin-bottom: 1.5rem;
        box-shadow: 0px 4px 20px rgba(56, 189, 248, 0.1);
    }
    .question-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        line-height: 1.5;
    }
    
    /* Streamlit Form Input Headers Label Visibility Tweak */
    .stSelectbox label, .stRadio label {
        font-size: 1.4rem !important;
        color: #F1F5F9 !important;
        font-weight: 800 !important;
    }

    /* Legend Scale Frame Box */
    .scale-legend {
        background-color: #111827;
        border: 2px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 2.5rem;
        display: flex;
        justify-content: space-around;
        font-size: 1.25rem !important;
        color: #F1F5F9 !important;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Hardcoded Survey Matrix Verbatim Mapping
DEPARTMENT_QUESTIONS = {
    "Plant Engineering Department": [
        "Provide technical data and specification as per the request[cite: 2]",
        "Cooperation in mould cleaning check up to shorten its change time[cite: 2]",
        "Communication is on time to deliver the request service[cite: 2]",
        "Provide support based on request[cite: 2]",
        "Test result is given for plant engineering on time[cite: 2]",
        "Active participation in cross functional team to address common plant problems[cite: 2]",
        "Satisfaction on overall relationship with the department[cite: 2]"
    ],
    "Production Department": [
        "Recipes/Specifications/ Work instructions are updated periodically and understandable for users[cite: 3]",
        "Helpful work instructions are prepared by considering quality with productivity[cite: 3]",
        "Root cause analysis & prevention work in collaboration with CFT team[cite: 3]",
        "There is cooperation with production team to reduce waste[cite: 3]",
        "Work instructions are prepared based on good practices of the company[cite: 3]",
        "Recommendations are given for nonconforming Semi finished products on time[cite: 3]",
        "Materials are released for production as per laboratory testing time and material rest time[cite: 3]",
        "Gaps seen in the process are highlighted for correction to be taken[cite: 3]",
        "Providing gap base training as per request for production staffs.[cite: 3]"
    ],
    "Sales and Marketing Department": [
        "Provide technical data and specification as per the request[cite: 5]",
        "Response for product quality improvement as per request[cite: 5]",
        "Communication is on time about new products[cite: 5]",
        "Provide technical support based on request[cite: 5]",
        "Claim tire inspection and on time feedback.[cite: 5]",
        "Actively participating on field and customer support activities[cite: 5]",
        "Satisfaction on overall relationship with the department[cite: 5]"
    ],
    "PIQA Employee Staff": [
        "I have immediate access to calibrated testing equipment required for my shift operations.[cite: 1]",
        "The internal workspace, ventilation, and physical safety barriers support optimized execution.[cite: 1]",
        "Shift assignment transitions and inter-departmental communications are clear and structured.[cite: 1]",
        "Management consistently supports upskilling regarding changes in compound mixtures or compound recipes.[cite: 1]"
    ],
    "Purchase Department": [
        "PIQA delivers technical data and raw material inspection specifications quickly.[cite: 4]",
        "The chemical and mechanical laboratory feedback loops for vendor samples align with purchasing timelines.[cite: 4]",
        "Supplier Non-Conformance Reports (NCR) are detailed objectively to support raw material claims.[cite: 4]",
        "Overall collaborative alignment on alternative material sourcing during supply line updates is positive.[cite: 4]"
    ],
    "Store Department": [
        "The testing processing times for incoming raw materials prevent compound inventory stagnations.[cite: 6]",
        "Clear tags, visual indicators, and status updates are provided for quarantined/non-conforming stock.[cite: 6]",
        "PIQA personnel follow warehouse zoning restrictions and material rest timelines accurately.[cite: 6]",
        "Clear technical directions are provided for handling aging inventories or compound batch releases.[cite: 6]"
    ]
}

emoji_options = ["1 🤬", "2 🙁", "3 😐", "4 🙂", "5 🤩"]

@st.cache_data
def generate_verbatim_survey_dataset():
    np.random.seed(42)
    records = []
    emoji_map = {1: "🤬", 2: "🙁", 3: "😐", 4: "🙂", 5: "🤩"}
    tenures = ['< 1 Year', '1-3 Years', '3+ Years']
    
    for dept, questions in DEPARTMENT_QUESTIONS.items():
        for q_idx, question in enumerate(questions):
            for _ in range(40):
                score = np.random.choice([1, 2, 3, 4, 5], p=[0.04, 0.06, 0.12, 0.53, 0.25])
                records.append({
                    "Department": dept,
                    "Question Number": f"Q{q_idx + 1}",
                    "Criteria Description": question,
                    "Score": score,
                    "Emoji": emoji_map[score],
                    "Sentiment": "Positive" if score > 3 else ("Neutral" if score == 3 else "Negative"),
                    "Tenure": np.random.choice(tenures)
                })
    return pd.DataFrame(records)

df = generate_verbatim_survey_dataset()

# Top Branding Title Layout Area
st.markdown("<h1>PIQA Matrix Interface Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#CBD5E1; font-size:1.4rem !important; margin-bottom: 2rem; font-weight:800;'>Unified industrial ecosystem for live metrics visual processing and feedback acquisition.</p>", unsafe_allow_html=True)

# Main Multi-Tab Display Layout (Text sizing managed seamlessly via CSS injections above)
tab_dash, tab_survey = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake"])

# ==========================================
# VIEW 1: LIVE ANALYTICS DASHBOARD
# ==========================================
with tab_dash:
    with st.sidebar:
        st.markdown("<h1 style='font-size:2.2rem !important; color:#38BDF8; margin-top:0; font-family:\"Syne\";'>🎨 Control Room</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #475569; border-width: 2px;'/>", unsafe_allow_html=True)
        
        selected_dept = st.radio(
            label="Select Profile View Loop Target:",
            options=['All Matrix Mix'] + list(DEPARTMENT_QUESTIONS.keys()),
            key="dash_dept_radio"
        )
        
        st.markdown("<hr style='border-color: #475569; border-width: 2px;'/>", unsafe_allow_html=True)
        selected_tenure = st.segmented_control(
            label="Filter Dataset by Plant Tenure:",
            options=['All Mix'] + list(df['Tenure'].unique()),
            default='All Mix',
            key="dash_tenure_seg"
        )

    # Filter evaluation dataset arrays safely
    filtered_df = df.copy()
    if selected_dept != 'All Matrix Mix':
        filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
    if selected_tenure != 'All Mix':
        filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

    st.markdown(f"<p style='color:#F1F5F9; font-size:1.4rem !important;'><b>Current Analytics View Loop Context:</b> Section: <span style='color:#38BDF8;'>{selected_dept}</span> | Mix Vector: <span style='color:#34D399;'>{selected_tenure}</span></p>", unsafe_allow_html=True)
    
    # Ultra Bold, High Contrast KPI Panels Grid Execution Block
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_score = round(filtered_df['Score'].mean(), 2) if not filtered_df.empty else 0.0
        st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size:1.1rem !important; text-transform:uppercase; margin-bottom:6px;">Composite Mean Score</p><h2 class="metric-value">{avg_score} <span style="font-size:1.5rem !important; color:#38BDF8;">/ 5.0</span></h2></div>', unsafe_allow_html=True)
    with col2:
        total_responses = len(filtered_df)
        st.markdown(f'<div class="metric-card" style="border-left-color: #34D399 !important;"><p style="color:#94A3B8; font-size:1.1rem !important; text-transform:uppercase; margin-bottom:6px;">Evaluated Sample Blocks</p><h2 class="metric-value">{total_responses}</h2></div>', unsafe_allow_html=True)
    with col3:
        pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / total_responses) * 100) if total_responses > 0 else 0
        st.markdown(f'<div class="metric-card" style="border-left-color: #34D399 !important;"><p style="color:#94A3B8; font-size:1.1rem !important; text-transform:uppercase; margin-bottom:6px;">Satisfaction Index</p><h2 class="metric-value">{pos_pct}%</h2></div>', unsafe_allow_html=True)
    with col4:
        mode_score = filtered_df['Score'].mode()[0] if not filtered_df.empty else 3
        emoji_star = "🤩" if mode_score == 5 else ("🙂" if mode_score == 4 else "😐")
        st.markdown(f'<div class="metric-card" style="border-left-color: #FBBF24 !important;"><p style="color:#94A3B8; font-size:1.1rem !important; text-transform:uppercase; margin-bottom:6px;">Dominant Sentiment</p><h2 class="metric-value">Lvl {mode_score} {emoji_star}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Grid Display Chart Splits
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("<div class='section-title'>📊 Matrix Distribution Score by Specific Question Criteria</div>", unsafe_allow_html=True)
        question_chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index().sort_values(by='Score')
        fig_bar = px.bar(question_chart_data, x='Score', y='Criteria Description', orientation='h', color='Score', color_continuous_scale='Blues', text_auto='.2f', template="plotly_dark")
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter", font=dict(size=14, weight='bold'), xaxis=dict(title="Average Score Value Out of 5.0", range=[1, 5], gridcolor='#334155', titlefont=dict(size=16, color='#FFFFFF')), yaxis=dict(title=None, showticklabels=False), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.markdown("<div class='section-title'>🍕 Sentiment Proportions</div>", unsafe_allow_html=True)
        sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
        fig_pie = px.pie(sentiment_data, values='count', names='Sentiment', color='Sentiment', color_discrete_map={'Positive': '#34D399', 'Neutral': '#FBBF24', 'Negative': '#F87171'}, hole=0.5, template="plotly_dark")
        fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter", legend=dict(font=dict(size=16, color='#FFFFFF')))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Crosstab Heatmap Grid
    st.markdown("<div class='section-title'>⚡ Questionnaire Heatmap Matrix (All Departments Cross-Tabulation View)</div>", unsafe_allow_html=True)
    xtab = pd.crosstab(df['Department'], df['Score'], normalize='index') * 100
    fig_heat = px.imshow(xtab.round(1), text_auto=True, labels=dict(x="Likert Scale Rating Score Profile", y="Department Hub", color="Percentage (%)"), x=['1 (Strongly Disagree)', '2 (Disagree)', '3 (Neutral)', '4 (Agree)', '5 (Strongly Agree)'], color_continuous_scale='Mint', template="plotly_dark")
    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter", font=dict(size=14, color='#FFFFFF', weight='bold'))
    st.plotly_chart(fig_heat, use_container_width=True)

    # Dynamic Alert Flag Block Module
    st.markdown("<div class='section-title'>🎯 Priority Action Register Matrix</div>", unsafe_allow_html=True)
    if avg_score < 3.8:
        st.error(f"🚨 **High Alert Action Required for {selected_dept}:** The custom segment analysis drops below target baseline thresholds (< 3.8). Schedule focus group sessions targeting these specific parameter gaps immediately.")
    else:
        st.success(f"✨ **Healthy Operational Standard Maintained for {selected_dept}:** Quality index parameters line up properly with current baseline targets. Continue auditing workflows on schedule.")

# ==========================================
# VIEW 2: INTERACTIVE SURVEY INTAKE
# ==========================================
with tab_survey:
    st.markdown("<div class='section-title'>📝 Live Questionnaire Engine</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#F1F5F9; font-size:1.3rem !important; font-weight:800; margin-bottom:2rem;'>Please select your active sector profile below to initialize the target verification questionnaire metrics loops.</p>", unsafe_allow_html=True)
    
    col_surv_dept, col_surv_tenure = st.columns(2)
    with col_surv_dept:
        survey_dept = st.selectbox("Identify Your Active Department Hub Target Field:", list(DEPARTMENT_QUESTIONS.keys()), key="survey_dept_select")
    with col_surv_tenure:
        survey_tenure = st.selectbox("Your Plant Operational Tenure Tracking Profile Segment:", ["< 1 Year", "1-3 Years", "3+ Years"], key="survey_tenure_select")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='scale-legend'><span><b>1</b> 🤬 Strongly Disagree</span><span><b>2</b> 🙁 Disagree</span><span><b>3</b> 😐 Neutral</span><span><b>4</b> <b>🙂 Agree</b></span><span><b>5</b> <b>🤩 Strongly Agree</b></span></div>", unsafe_allow_html=True)
    
    # Live Response Form Panel Execution
    with st.form("interactive_intake_form", clear_on_submit=True):
        survey_responses = {}
        active_questions = DEPARTMENT_QUESTIONS[survey_dept]
        
        for idx, question in enumerate(active_questions):
            # Formatted via .question-block for massive high contrast text parsing visibility
            st.markdown(f'<div class="question-block"><div class="question-text"><b>Q{idx+1}.</b> {question}</div></div>', unsafe_allow_html=True)
            
            score_selection = st.segmented_control(
                label=f"Rating Choice Selection Button Array Array for Survey Q{idx+1}",
                options=emoji_options,
                key=f"survey_q_{idx+1}",
                label_visibility="collapsed"
            )
            survey_responses[f"Question {idx+1}"] = {"criteria": question, "selected_rating": score_selection}
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.markdown("<h3 style='color:#38BDF8; font-family:\"Syne\"; font-size:1.8rem !important; font-weight:800;'>📝 Additional Structural Points or Recommendations</h3>", unsafe_allow_html=True)
        additional_notes = st.text_area("Notes entry field area loop:", label_visibility="collapsed", placeholder="Type any system deviations, structural anomalies, or raw feedback comments here...", key="survey_notes_area")
        
        submit_survey_btn = st.form_submit_button("Submit Operational Evaluation Log")
        
    if submit_survey_btn:
        incomplete = [q for q, data in survey_responses.items() if data["selected_rating"] is None]
        if incomplete:
            st.error("⚠️ **Incomplete Fields Detected:** Please provide an interactive emoji rating selection for all question matrix blocks before submitting.")
        else:
            final_payload = {
                "timestamp": datetime.now().isoformat(),
                "department": survey_dept,
                "tenure": survey_tenure,
                "responses": [{"item_id": q_key, "criteria": val["criteria"], "score": int(val["selected_rating"][0])} for q_key, val in survey_responses.items()],
                "qualitative_feedback": additional_notes
            }
            st.success("🎉 **Feedback Recorded Successfully!** The raw dataset block has been logged and compiled safely.")
            
            json_string = json.dumps(final_payload, indent=2)
            st.download_button(
                label="📥 Download Clean Raw Data Block (.json)",
                data=json_string,
                file_name=f"PIQA_Raw_{survey_dept.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
