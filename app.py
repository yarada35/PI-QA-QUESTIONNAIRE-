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

# Custom CSS Injection: Targets layout, sidebar, active tabs, glowing yellow sidebar text, and print styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=400;600;700&family=Syne:wght=700;800&family=Inter:wght=400;500;600;700&display=swap');
    
    /* Main App Deep Dark Background */
    .stApp {
        background-color: #05070F !important;
        color: #F1F5F9 !important;
    }
    
    /* Compatible Black Sidebar Target */
    [data-testid="stSidebar"] {
        background-color: #090D16 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* GLOWING SHINY REFLECTIVE YELLOW SIDEBAR DEPARTMENT LABELS */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] + div label p {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #FBBF24 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-shadow: 0px 0px 8px rgba(251, 191, 36, 0.6) !important;
        transition: all 0.2s ease;
    }
    
    /* Hover effect for an extra reflective sheen */
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] + div label:hover p {
        color: #FFE082 !important;
        text-shadow: 0px 0px 14px rgba(251, 191, 36, 0.9) !important;
    }

    /* Main App Header Text styling */
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
    
    /* Main selection tabs: Big, Bold, and Reflective */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        padding: 12px 24px !important;
        font-family: 'Syne', sans-serif !important;
        transition: all 0.3s ease;
    }
    /* Active reflective state when selected */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #34D399 !important;
        border-bottom: 4px solid #34D399 !important;
        text-shadow: 0px 0px 12px rgba(52, 211, 153, 0.6);
    }
    
    /* Premium Glossy Dark Metric Cards */
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
        margin-bottom: 1rem;
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

    .stMarkdown p {
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

@st.cache_data
def generate_verbatim_survey_dataset():
    np.random.seed(42)
    records = []
    emoji_map = {1: "🤬", 2: "🙁", 3: "😐", 4: "🙂", 5: "🤩"}
    tenures = ['< 1 Year', '1-3 Years', '3+ Years']
    
    for dept, questions in DEPARTMENT_QUESTIONS.items():
        for tenure in tenures:
            num_respondents = int(np.random.randint(8, 20)) 
            for resp_id in range(num_respondents):
                unique_survey_id = f"RESP_{dept[:3].upper()}_{tenure[:2]}_{resp_id}"
                for q_idx, question in enumerate(questions):
                    score = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.07, 0.15, 0.50, 0.23])
                    records.append({
                        "RespondentID": unique_survey_id,
                        "Department": dept,
                        "Question Number": f"Q{q_idx + 1}",
                        "Criteria Description": question,
                        "Score": score,
                        "Emoji": emoji_map[score],
                        "Sentiment": "Positive" if score > 3 else ("Neutral" if score == 3 else "Negative"),
                        "Tenure": tenure
                    })
    return pd.DataFrame(records)

df = generate_verbatim_survey_dataset()

# Title Banner
st.markdown("<h1>PIQA Matrix Interface Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; font-size:1.1rem; margin-bottom: 1.5rem;'>Unified suite for live operational analysis and internal raw feedback collection loops.</p>", unsafe_allow_html=True)

# Main Multi-Tab Layout Layout Selection Space including Print & Share Tab
tab_dash, tab_survey, tab_print = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print & Distribution Hub"])

# Global Sidebar Filters
with st.sidebar:
    st.markdown("<h2 style='font-family:\"Syne\"; color:#38BDF8; margin-top:0;'>🎨 Control Room</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    
    st.markdown("<b style='color:#F1F5F9; font-size: 0.95rem;'>Select Target Filter Profile:</b>", unsafe_allow_html=True)
    selected_dept = st.radio(
        label="Target Departments Filter",
        options=['All Matrix Mix'] + list(DEPARTMENT_QUESTIONS.keys()),
        key="dash_dept_radio",
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    st.markdown("<b style='color:#F1F5F9; font-size: 0.95rem;'>Demographic Filtering Crosstab:</b>", unsafe_allow_html=True)
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

distinct_active_respondents = filtered_df['RespondentID'].nunique()
avg_score = round(filtered_df['Score'].mean(), 2) if not filtered_df.empty else 0.0

# ==========================================
# VIEW 1: LIVE ANALYTICS DASHBOARD
# ==========================================
with tab_dash:
    st.markdown(f"<p style='color:#94A3B8;'><b>Active Analytics View:</b> Segment: <span style='color:#38BDF8;'>{selected_dept}</span> | Profile Mix: <span style='color:#34D399;'>{selected_tenure}</span></p>", unsafe_allow_html=True)
    
    # Summary KPI Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Composite Mean Score</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{avg_score} <span style="font-size:1.2rem; color:#38BDF8;">/ 5.0</span></h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#34D399; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Total Sample Respondents</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{distinct_active_respondents} <span style="font-size:1.1rem; color:#94A3B8;">Staff</span></h2></div>', unsafe_allow_html=True)
    with col3:
        pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / len(filtered_df)) * 100) if not filtered_df.empty else 0
        st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Satisfaction Index</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{pos_pct}%</h2></div>', unsafe_allow_html=True)
    with col4:
        mode_score = filtered_df['Score'].mode()[0] if not filtered_df.empty else 3
        emoji_star = "🤩" if mode_score == 5 else ("🙂" if mode_score == 4 else "😐")
        st.markdown(f'<div class="metric-card" style="border-left-color: #FBBF24;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Dominant Sentiment</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">Level {mode_score} {emoji_star}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📋 Total Number of Respondents Matrix (Observation Breakdown)</div>", unsafe_allow_html=True)
    respondent_matrix = df.groupby(['Department', 'Tenure'])['RespondentID'].nunique().unstack(fill_value=0)
    respondent_matrix['Total Fleet'] = respondent_matrix.sum(axis=1)
    st.dataframe(respondent_matrix, use_container_width=True)

    # Charts Section
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("<div class='section-title'>📊 Matrix Distribution Score by Specific Question Criteria</div>", unsafe_allow_html=True)
        question_chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index().sort_values(by='Score')
        fig_bar = px.bar(question_chart_data, x='Score', y='Criteria Description', orientation='h', color='Score', color_continuous_scale='Blues', text_auto='.2f', template="plotly_dark")
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Inter", xaxis=dict(title=dict(text="Average Score Value Out of 5.0", font=dict(color='#FFFFFF')), range=[1, 5], gridcolor='#1E293B'), yaxis=dict(title=None, showticklabels=False), coloraxis_showscale=False)
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
    
    col_surv_dept, col_surv_tenure = st.columns(2)
    with col_surv_dept:
        survey_dept = st.selectbox("Identify Your Active Department Hub:", list(DEPARTMENT_QUESTIONS.keys()), key="survey_dept_select")
    with col_surv_tenure:
        survey_tenure = st.selectbox("Your Plant Operational Tenure Profile:", ["< 1 Year", "1-3 Years", "3+ Years"], key="survey_tenure_select")
        
    st.markdown("<div class='scale-legend'><span><b>1</b> 🤬 Strongly Disagree</span><span><b>2</b> 🙁 Disagree</span><span><b>3</b> 😐 Neutral</span><span><b>4</b> <b>🙂 Agree</b></span><span><b>5</b> <b>🤩 Strongly Agree</b></span></div>", unsafe_allow_html=True)
    
    with st.form("interactive_intake_form", clear_on_submit=True):
        survey_responses = {}
        active_questions = DEPARTMENT_QUESTIONS[survey_dept]
        
        for idx, question in enumerate(active_questions):
            st.markdown(f'<div class="question-block"><div class="question-text"><b>Q{idx+1}.</b> {question}</div></div>', unsafe_allow_html=True)
            score_selection = st.segmented_control(label=f"Rating Choice for Survey Q{idx+1}", options=emoji_options, key=f"survey_q_{idx+1}", label_visibility="collapsed")
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
            st.download_button(label="📥 Download Clean Raw Data Block (.json)", data=json_string, file_name=f"PIQA_Raw_{survey_dept.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")

# ==========================================
# VIEW 3: NEW! PRINT & DISTRIBUTION HUB
# ==========================================
with tab_print:
    st.markdown("<div class='section-title'>🖨️ Document Generation & Share Center</div>", unsafe_allow_html=True)
    
    c_print_1, c_print_2 = st.columns([1, 2])
    
    with c_print_1:
        st.markdown("### 📄 Print Configuration")
        enable_print_mode = st.toggle("✨ Activate High-Contrast Print View Mode", value=False, help="Inverts backgrounds to crisp white and clean black ink lines to prevent dark background ink bleeding during print or PDF output exports.")
        
        # Inject styling rules if print view mode is checked by administrator
        if enable_print_mode:
            st.markdown("""
                <style>
                .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
                [data-testid="stSidebar"] { display: none !important; }
                .metric-card { background: #FFFFFF !important; border: 2px solid #000000 !important; color: #000000 !important; box-shadow: none !important; }
                .metric-card h2, .metric-card p { color: #000000 !important; }
                h1, .section-title, p, span { color: #000000 !important; background: none !important; -webkit-text-fill-color: initial !important; border-bottom-color: #000000 !important;}
                header, [data-testid="stHeader"] { display: none !important; }
                </style>
            """, unsafe_allow_html=True)
            st.info("💡 **Print Mode Active:** Background structures are modified to clean high contrast white paper profiles. Simply press `Ctrl + P` (or `Cmd + P` on Mac) to use your browser's printer profile or generate a clean local .pdf file!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📤 Export Raw Consolidated Matrices")
        
        # CSV Export Options for sharing across departments
        csv_buffer = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Current Slice Dataset to CSV",
            data=csv_buffer,
            file_name=f"PIQA_Export_{selected_dept.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with c_print_2:
        st.markdown("### 🔗 Share Snapshot Details")
        st.markdown("Generate a quick snapshot profile text summary block to send to leadership channels or internal team boards.")
        
        summary_share_string = f"""--- PIQA FIELD OPERATIONAL SNAPSHOT PROFILE ---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Target Scope Segment: {selected_dept}
Employee Tenure Profile Mix: {selected_tenure}
---------------------------------------------
* Total Validated Respondents Group: {distinct_active_respondents} Staff
* Active Composite Mean Metric Score: {avg_score} / 5.0
* Current Operational Quality Index Status: {"⚠️ Threshold Gaps Detected" if avg_score < 3.8 else "✅ Healthy Baseline Standard"}
---------------------------------------------"""
        
        st.text_area("📋 Copy Distribution Summary Block:", value=summary_share_string, height=200)
        st.caption("Select all text inside the block above to quickly share snapshot findings on internal messaging platforms or notification emails.")
