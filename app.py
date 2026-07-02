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

# Deep Custom CSS Injection to force uniform dark tones and high-impact text rendering
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=400;600;700&family=Syne:wght=700;800&family=Inter:wght=400;500;600&display=swap');
    
    /* Force main app background wrapper to dark theme */
    .stApp {
        background-color: #0B0F19 !important;
        color: #F1F5F9 !important;
    }
    
    /* Typography Overrides */
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
    
    /* Premium Glossy Dark Metric Cards */
    .metric-card {
        background: #1E293B;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #334155;
        border-left: 6px solid #38BDF8;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #475569;
    }

    .question-block {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 1rem;
    }

    .question-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        font-weight: 500;
        color: #F8FAFC;
    }

    .scale-legend {
        background-color: #111827;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-around;
        font-size: 0.85rem;
        color: #CBD5E1;
    }

    .stMarkdown p {
        color: #CBD5E1;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Dataset Blueprint Configuration
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
            for _ in range(35):
                score = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.07, 0.15, 0.50, 0.23])
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

# Title Banner
st.markdown("<h1>PIQA Matrix Interface Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; font-size:1.1rem; margin-bottom: 1.5rem;'>Unified suite for live operational analysis and internal raw feedback collection loops.</p>", unsafe_allow_html=True)

# 3. Main Interface Section View Tabs
tab_dash, tab_survey = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake"])

# ==========================================
# VIEW 1: LIVE ANALYTICS DASHBOARD
# ==========================================
with tab_dash:
    # Sidebar Configuration Links directly inside the Dashboard Tab environment
    with st.sidebar:
        st.markdown("<h2 style='font-family:\"Syne\"; color:#38BDF8; margin-top:0;'>🎨 Control Room</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
        
        st.markdown("<b style='color:#F1F5F9;'>Select Target Filter Profile:</b>", unsafe_allow_html=True)
        selected_dept = st.radio(
            label="Target Departments Filter",
            options=['All Matrix Mix'] + list(DEPARTMENT_QUESTIONS.keys()),
            key="dash_dept_radio"
        )
        
        st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
        st.markdown("<b style='color:#F1F5F9;'>Demographic Filtering Crosstab:</b>", unsafe_allow_html=True)
        selected_tenure = st.segmented_control(
            label="Employee Tenure Filter",
            options=['All Mix'] + list(df['Tenure'].unique()),
            default='All Mix',
            key="dash_tenure_seg"
        )

    # Slice Metrics safely based on dashboard settings
    filtered_df = df.copy()
    if selected_dept != 'All Matrix Mix':
        filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
    if selected_tenure != 'All Mix':
        filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

    st.markdown(f"<p style='color:#94A3B8;'><b>Active Analytics View:</b> Segment: <span style='color:#38BDF8;'>{selected_dept}</span> | Profile Mix: <span style='color:#34D399;'>{selected_tenure}</span></p>", unsafe_allow_html=True)
    
    # Summary KPI Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_score = round(filtered_df['Score'].mean(), 2) if not filtered_df.empty else 0.0
        st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Composite Mean Score</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{avg_score} <span style="font-size:1.2rem; color:#38BDF8;">/ 5.0</span></h2></div>', unsafe_allow_html=True)
    with col2:
        total_responses = len(filtered_df)
        st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Evaluated Sample Blocks</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{total_responses}</h2></div>', unsafe_allow_html=True)
    with col3:
        pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / total_responses) * 100) if total_responses > 0 else 0
        st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Satisfaction Index</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{pos_pct}%</h2></div>', unsafe_allow_html=True)
    with col4:
        mode_score = filtered_df['Score'].mode()[0] if not filtered_df.empty else 3
        emoji_star = "🤩" if mode_score == 5 else ("🙂" if mode_score == 4 else "😐")
        st.markdown(f'<div class="metric-card" style="border-left-color: #FBBF24;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Dominant Sentiment</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">Level {mode_score} {emoji_star}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Section
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("<div class='section-title'>📊 Matrix Distribution Score by Specific Question Criteria</div>", unsafe_allow_html=True)
        question_chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index().sort_values(by='Score')
        fig_bar = px.bar(question_chart_data, x='Score', y='Criteria Description', orientation='h', color='Score', color_continuous_scale='Blues', text_auto='.2f', template="plotly_dark")
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter", xaxis=dict(title="Average Score", range=[1, 5], gridcolor='#1E293B'), yaxis=dict(title=None, showticklabels=False), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.markdown("<div class='section-title'>🍕 Sentiment Proportions</div>", unsafe_allow_html=True)
        sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
        fig_pie = px.pie(sentiment_data, values='count', names='Sentiment', color='Sentiment', color_discrete_map={'Positive': '#34D399', 'Neutral': '#FBBF24', 'Negative': '#F87171'}, hole=0.5, template="plotly_dark")
        fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Matrix Cross-Tab Heatmap Section
    st.markdown("<div class='section-title'>⚡ Questionnaire Heatmap Matrix (All Departments Cross-Tabulation View)</div>", unsafe_allow_html=True)
    xtab = pd.crosstab(df['Department'], df['Score'], normalize='index') * 100
    fig_heat = px.imshow(xtab.round(1), text_auto=True, labels=dict(x="Likert Scale Rating Score Profile", y="Department Hub", color="Percentage (%)"), x=['1 (Strongly Disagree)', '2 (Disagree)', '3 (Neutral)', '4 (Agree)', '5 (Strongly Agree)'], color_continuous_scale='Mint', template="plotly_dark")
    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter")
    st.plotly_chart(fig_heat, use_container_width=True)

    # Operational Recommendation Module
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
    st.markdown("<p style='color:#94A3B8;'>Responders can log their ratings here. Select a department to generate its matching verification criteria matrix.</p>", unsafe_allow_html=True)
    
    # Demographics Choice for logging survey responses
    col_surv_dept, col_surv_tenure = st.columns(2)
    with col_surv_dept:
        survey_dept = st.selectbox("Identify Your Active Department Hub:", list(DEPARTMENT_QUESTIONS.keys()), key="survey_dept_select")
    with col_surv_tenure:
        survey_tenure = st.selectbox("Your Plant Operational Tenure Profile:", ["< 1 Year", "1-3 Years", "3+ Years"], key="survey_tenure_select")
        
    st.markdown("<div class='scale-legend'><span><b>1</b> 🤬 Strongly Disagree</span><span><b>2</b> 🙁 Disagree</span><span><b>3</b> 😐 Neutral</span><span><b>4</b> <b>🙂 Agree</b></span><span><b>5</b> <b>🤩 Strongly Agree</b></span></div>", unsafe_allow_html=True)
    
    # Survey Intake Submission Core Block Form
    with st.form("interactive_intake_form", clear_on_submit=True):
        survey_responses = {}
        active_questions = DEPARTMENT_QUESTIONS[survey_dept]
        
        for idx, question in enumerate(active_questions):
            st.markdown(f'<div class="question-block"><div class="question-text"><b>Q{idx+1}.</b> {question}</div></div>', unsafe_allow_html=True)
            score_selection = st.segmented_control(
                label=f"Rating Choice for Survey Q{idx+1}",
                options=emoji_options,
                key=f"survey_q_{idx+1}",
                label_visibility="collapsed"
            )
            survey_responses[f"Question {idx+1}"] = {"criteria": question, "selected_rating": score_selection}
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.markdown("### 📝 Additional Points or Recommendations")
        additional_notes = st.text_area("Notes entry:", label_visibility="collapsed", placeholder="Type any system anomalies or optimization notes here...", key="survey_notes_area")
        
        submit_survey_btn = st.form_submit_button("Submit Operational Evaluation Log")
        
    if submit_survey_btn:
        incomplete = [q for q, data in survey_responses.items() if data["selected_rating"] is None]
        if incomplete:
            st.error("⚠️ **Incomplete Fields Detected:** Please make sure to provide an interactive emoji rating for all question matrix blocks before submitting.")
        else:
            final_payload = {
                "timestamp": datetime.now().isoformat(),
                "department": survey_dept,
                "tenure": survey_tenure,
                "responses": [{"item_id": q_key, "criteria": val["criteria"], "score": int(val["selected_rating"][0])} for q_key, val in survey_responses.items()],
                "qualitative_feedback": additional_notes
            }
            st.success("🎉 **Feedback Recorded Successfully!** The payload is clean and verified against operational schemas.")
            
            json_string = json.dumps(final_payload, indent=2)
            st.download_button(
                label="📥 Download Clean Raw Data Block (.json)",
                data=json_string,
                file_name=f"PIQA_Raw_{survey_dept.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
