import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration & Black/Dark Theme Base Initializer
st.set_page_config(
    page_title="PIQA Analytics | Dark Synergy Matrix",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Custom CSS Injection to force uniform dark tones and high-impact text rendering
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=400;600;700&family=Syne:wght=700;800&family=Inter:wght=400;500&display=swap');
    
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

    .stMarkdown p {
        color: #CBD5E1;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Hardcoded Mapping of Verbatim Survey Criteria from Source JSONs
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

# 3. Comprehensive Mock Data Generation Pipeline using Actual Questions
@st.cache_data
def generate_verbatim_survey_dataset():
    np.random.seed(42)
    records = []
    emoji_map = {1: "🤬", 2: "🙁", 3: "😐", 4: "🙂", 5: "🤩"}
    tenures = ['< 1 Year', '1-3 Years', '3+ Years']
    
    # Generate balanced sample data points distributed across every specific unique criteria mapped above
    for dept, questions in DEPARTMENT_QUESTIONS.items():
        for q_idx, question in enumerate(questions):
            # Simulate 30 detailed historical entry responses per specific question string mapping
            for _ in range(30):
                score = np.random.choice([1, 2, 3, 4, 5], p=[0.04, 0.08, 0.18, 0.48, 0.22])
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

# 4. Interactive Sidebar Component Control Hub
with st.sidebar:
    st.markdown("<h2 style='font-family:\"Syne\"; color:#38BDF8; margin-top:0;'>🎨 Control Room</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
    
    st.markdown("<b style='color:#F1F5F9;'>Select Target Responder Department:</b>", unsafe_allow_html=True)
    selected_dept = st.radio(
        label="Target Departments",
        options=list(DEPARTMENT_QUESTIONS.keys()),
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
    st.markdown("<b style='color:#F1F5F9;'>Demographic Filtering Crosstab:</b>", unsafe_allow_html=True)
    selected_tenure = st.segmented_control(
        label="Employee Tenure",
        options=['All Mix'] + list(df['Tenure'].unique()),
        default='All Mix'
    )

# Slice and slice metrics safely using current states
filtered_df = df[df['Department'] == selected_dept]
if selected_tenure != 'All Mix':
    filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

# 5. Main Content Dashboard Panel Header Layout
st.markdown("<h1>PIQA Synergy Matrix Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94A3B8;'><b>Active Filter View:</b> Active Responder Profile: <span style='color:#38BDF8;'>{selected_dept}</span> | <b>Tenure:</b> <span style='color:#34D399;'>{selected_tenure}</span></p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #1E293B; margin-bottom: 2rem;'/>", unsafe_allow_html=True)

# High Impact Summary KPI Grid
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_score = round(filtered_df['Score'].mean(), 2) if not filtered_df.empty else 0.0
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #38BDF8;">
            <p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Composite Mean Score</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#F8FAFC; margin:0;">{avg_score} <span style="font-size:1.2rem; color:#38BDF8;">/ 5.0</span></h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    total_responses = len(filtered_df)
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #34D399;">
            <p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Evaluated Sample Blocks</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#F8FAFC; margin:0;">{total_responses}</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / total_responses) * 100) if total_responses > 0 else 0
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #34D399;">
            <p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Satisfaction Index</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#F8FAFC; margin:0;">{pos_pct}%</h2>
        </div>
    """, unsafe_allow_html=True)

with col4:
    mode_score = filtered_df['Score'].mode()[0] if not filtered_df.empty else 3
    emoji_star = "🤩" if mode_score == 5 else ("🙂" if mode_score == 4 else "😐")
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #FBBF24;">
            <p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Dominant Sentiment</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#F8FAFC; margin:0;">Level {mode_score} {emoji_star}</h2>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. Graph Visual Distribution Split Frameworks
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("<div class='section-title'>📊 Matrix Distribution Score by Specific Question Criteria</div>", unsafe_allow_html=True)
    
    # Aggregate data to display average score trends grouped by the exact verbatim question strings
    question_chart_data = filtered_df.groupby('Criteria Description')['Score'].mean().reset_index().sort_values(by='Score')
    
    fig_bar = px.bar(
        question_chart_data, 
        x='Score', 
        y='Criteria Description',
        orientation='h',
        color='Score',
        color_continuous_scale='Blues',
        text_auto='.2f',
        template="plotly_dark"
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        xaxis=dict(title="Average Score (Out of 5.0)", range=[1, 5], gridcolor='#1E293B'),
        yaxis=dict(title=None, tickmode='linear'),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>🍕 Sentiment Proportions</div>", unsafe_allow_html=True)
    sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
    
    fig_pie = px.pie(
        sentiment_data, 
        values='count', 
        names='Sentiment',
        color='Sentiment',
        color_discrete_map={'Positive': '#34D399', 'Neutral': '#FBBF24', 'Negative': '#F87171'},
        hole=0.5,
        template="plotly_dark"
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 7. Heatmap Cross-Tabulation Array Grid Breakdown
st.markdown("<div class='section-title'>⚡ Questionnaire Heatmap Matrix (All Departments Cross-Tabulation View)</div>", unsafe_allow_html=True)
xtab = pd.crosstab(df['Department'], df['Score'], normalize='index') * 100
xtab = xtab.round(1)

fig_heat = px.imshow(
    xtab,
    text_auto=True,
    labels=dict(x="Likert Scale Rating Score Profile", y="Department Hub", color="Percentage (%)"),
    x=['1 (Strongly Disagree)', '2 (Disagree)', '3 (Neutral)', '4 (Agree)', '5 (Strongly Agree)'],
    color_continuous_scale='Mint',
    template="plotly_dark"
)
fig_heat.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_family="Inter"
)
st.plotly_chart(fig_heat, use_container_width=True)

# 8. Dynamic Recommendation Logic Loops
st.markdown("<div class='section-title'>🎯 Priority Action Register Matrix</div>", unsafe_allow_html=True)
if avg_score < 3.8:
    st.error(f"🚨 **High Alert Action Required for {selected_dept}:** The custom segment analysis drops below target baseline thresholds (< 3.8). Schedule focus group sessions targeting these specific parameter gaps immediately.")
else:
    st.success(f"✨ **Healthy Operational Standard Maintained for {selected_dept}:** Quality index parameters line up properly with current baseline targets. Continue auditing workflows on schedule.")
