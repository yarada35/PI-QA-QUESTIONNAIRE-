import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. PAGE & INITIALIZATION SETUP
# ==========================================
st.set_page_config(
    page_title="PIQA Analytics & Survey Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injection for Premium UI
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
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.6rem !important; 
        font-weight: 800 !important; 
        font-family: 'Syne', sans-serif !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { 
        color: #34D399 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. QUESTION MATRIX DICTIONARY
# ==========================================
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

# ==========================================
# 3. ADVANCED CRYPTOGRAPHIC REPAIR & INITIALIZATION
# ==========================================
try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        # Extract secret configuration parameters safely
        g_secrets = st.secrets["connections"]["gsheets"]
        if "private_key" in g_secrets:
            key_str = g_secrets["private_key"]
            
            # 1. Strip external string layout literal wrapping quotes if present
            if (key_str.startswith('"') and key_str.endswith('"')) or (key_str.startswith("'") and key_str.endswith("'")):
                key_str = key_str[1:-1]
            
            # 2. Convert explicit '\\n' tracking combinations into actual newlines
            key_str = key_str.replace("\\n", "\n")
            
            # 3. Clean up formatting whitespace patterns
            lines = [line.strip() for line in key_str.split("\n") if line.strip()]
            
            # 4. Construct structural PEM layout block explicitly
            cleaned_lines = []
            for line in lines:
                if "BEGIN PRIVATE KEY" in line:
                    cleaned_lines.append("-----BEGIN PRIVATE KEY-----")
                elif "END PRIVATE KEY" in line:
                    cleaned_lines.append("-----END PRIVATE KEY-----")
                else:
                    cleaned_lines.append(line)
            
            final_pem_key = "\n".join(cleaned_lines)
            
            # Re-inject the pristine key back into Streamlit's environment memory
            st.secrets["connections"]["gsheets"]["private_key"] = final_pem_key
except Exception as e:
    st.sidebar.error(f"Sanitization Warning: {e}")

# Initialize GSheets Driver Connection instance safely
conn = st.connection("gsheets", type=GSheetsConnection)

# Read master database directly from worksheet Sheet1
try:
    df = conn.read(worksheet="Sheet1", ttl="0d")
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
except Exception as e:
    st.error(f"Database Read Warning: {e}")
    df = pd.DataFrame(columns=["RespondentID", "Department", "Question Number", "Criteria Description", "Score", "Emoji", "Sentiment", "Tenure"])

def clear_global_filters():
    for k in ["dash_dept_radio", "dash_tenure_seg"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# Layout Banner Headers
st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; font-size:1.1rem; margin-bottom: 1.5rem;'>Unified suite for live operational analysis and internal raw feedback collection loops.</p>", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR GLOBAL CONTROLS
# ==========================================
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
        options=['All Mix'] + ['< 1 Year', '1-3 Years', '3+ Years'],
        default='All Mix',
        key="dash_tenure_seg"
    )
    
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)
    st.button("🔄 Clear App Filters", on_click=clear_global_filters, use_container_width=True)

# Filter Processing Engine Slices
filtered_df = df.dropna(subset=['Score']).copy() if not df.empty else df.copy()
if selected_dept != 'All Matrix Mix':
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_tenure != 'All Mix':
    filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

# Structural Tabs Initialization
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
            st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#34D399; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Total Valid Submissions</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{distinct_active_respondents} <span style="font-size:1.1rem; color:#94A3B8;">Staff</span></h2></div>', unsafe_allow_html=True)
        with col3:
            pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / len(filtered_df)) * 100)
            st.markdown(f'<div class="metric-card" style="border-left-color: #34D399;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Satisfaction Index</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">{pos_pct}%</h2></div>', unsafe_allow_html=True)
        with col4:
            mode_score = int(filtered_df['Score'].mode()[0]) if not filtered_df.empty else 3
            st.markdown(f'<div class="metric-card" style="border-left-color: #FBBF24;"><p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Dominant Score Profile</p><h2 style="font-family:\'Space Grotesk\'; font-size:2.2rem; color:#F8FAFC; margin:0;">Level {mode_score}</h2></div>', unsafe_allow_html=True)

        st.markdown("<div class='section-title'>📋 Response Volume Layout Breakdown</div>", unsafe_allow_html=True)
        try:
            respondent_matrix = filtered_df.groupby(['Department', 'Tenure'])['RespondentID'].nunique().unstack(fill_value=0)
            st.dataframe(respondent_matrix, use_container_width=True)
        except Exception:
            st.dataframe(filtered_df[['RespondentID', 'Department', 'Tenure']].drop_duplicates(), use_container_width=True)

        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("<div class='section-title'>📊 Average Ratings by Query Breakdown</div>", unsafe_allow_html=True)
            question_chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index().sort_values(by='Score')
            fig_bar = px.bar(question_chart_data, x='Score', y='Criteria Description', orientation='h', color='Score', color_continuous_scale='Blues', range_x=[1,5], template="plotly_dark")
            fig_bar.update_layout(yaxis=dict(showticklabels=False, title=None), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.markdown("<div class='section-title'>🍕 Sentiment Proportions</div>", unsafe_allow_html=True)
            sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
            fig_pie = px.pie(sentiment_data, values='count', names='Sentiment', hole=0.5, template="plotly_dark")
            fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
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
            
            new_df = pd.DataFrame(new_rows)
            updated_master_df = pd.concat([df, new_df], ignore_index=True)
            
            try:
                conn.update(
                    worksheet="Sheet1",
                    data=updated_master_df
                )
                st.success("🎉 Evaluation captured securely inside the cloud database! Refresh page to update metrics.")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to submit row data: {e}")

# ==========================================
# VIEW 3: PRINT & DISTRIBUTION HUB
# ==========================================
with tab_print:
    st.markdown("<div class='section-title'>🖨️ Document Generation Center</div>", unsafe_allow_html=True)
    
    c_print_1, c_print_2 = st.columns([1, 2])
    with c_print_1:
        st.markdown("### 📄 Print Configuration")
        enable_print_mode = st.toggle("✨ Activate High-Contrast Print View Mode", value=False)
        
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
            st.info("💡 Print Mode Active! Press Ctrl+P (or Cmd+P) to print or generate a clean local PDF.")

        st.markdown("<br>", unsafe_allow_html=True)
        if not filtered_df.empty:
            st.download_button(
                label="📥 Export Current Slice Dataset to CSV", 
                data=filtered_df.to_csv(index=False).encode('utf-8'), 
                file_name=f"PIQA_Live_Export_{datetime.now().strftime('%Y%m%d')}.csv", 
                mime="text/csv",
                use_container_width=True
            )
    
    with c_print_2:
        st.markdown("### 🔗 Share Snapshot Details")
        if not filtered_df.empty:
            distinct_active_respondents = filtered_df['RespondentID'].nunique()
            avg_score = round(filtered_df['Score'].mean(), 2)
            summary_share_string = f"""--- PIQA FIELD OPERATIONAL SNAPSHOT PROFILE ---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Target Scope Segment: {selected_dept}
Employee Tenure Profile Mix: {selected_tenure}
---------------------------------------------
* Total Validated Respondents Group: {distinct_active_respondents} Staff
* Active Composite Mean Metric Score: {avg_score} / 5.0
* Current Operational Quality Index Status: {"⚠️ Threshold Gaps" if avg_score < 3.8 else "✅ Healthy Baseline"}
---------------------------------------------"""
            st.text_area("📋 Copy Distribution Summary Block:", value=summary_share_string, height=180)
        else:
            st.write("No active metrics data loop to profile.")
