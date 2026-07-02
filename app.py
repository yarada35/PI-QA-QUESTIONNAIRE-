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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@700;800&family=Inter:wght@400;500&display=swap');
    
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

    /* Style adjusting standard markdown block components text context color */
    .stMarkdown p {
        color: #CBD5E1;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Mock Data Generation Engine (Matching Survey Specifications)
@st.cache_data
def get_mock_survey_data():
    depts = ['Plant Engineering', 'Production', 'Sales & Marketing', 'Store Admin', 'Purchasing', 'PIQA Staff']
    emoji_map = {1: "🤬", 2: "🙁", 3: "😐", 4: "🙂", 5: "🤩"}
    
    np.random.seed(42)
    records = []
    for _ in range(250):
        d = np.random.choice(depts)
        score = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.10, 0.20, 0.45, 0.20])
        records.append({
            "Department": d,
            "Score": score,
            "Emoji": emoji_map[score],
            "Sentiment": "Positive" if score > 3 else ("Neutral" if score == 3 else "Negative"),
            "Tenure": np.random.choice(['< 1 Year', '1-3 Years', '3+ Years'])
        })
    return pd.DataFrame(records)

df = get_mock_survey_data()

# 3. Sidebar Configuration (Styled for Contrast)
with st.sidebar:
    st.markdown("<h2 style='font-family:\"Syne\"; color:#38BDF8; margin-top:0;'>🎨 Control Room</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
    
    st.markdown("<b style='color:#F1F5F9;'>Select Department Target Loop:</b>", unsafe_allow_html=True)
    selected_dept = st.radio(
        label="Target Departments",
        options=['All Departments'] + list(df['Department'].unique()),
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='border-color: #334155;'/>", unsafe_allow_html=True)
    st.markdown("<b style='color:#F1F5F9;'>Demographic Filtering Crosstab:</b>", unsafe_allow_html=True)
    selected_tenure = st.segmented_control(
        label="Employee Tenure",
        options=['All Mix'] + list(df['Tenure'].unique()),
        default='All Mix'
    )

# Filter Dataset based on interactive selections
filtered_df = df.copy()
if selected_dept != 'All Departments':
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_tenure != 'All Mix':
    filtered_df = filtered_df[filtered_df['Tenure'] == selected_tenure]

# 4. Main Canvas Heading Layout
st.markdown("<h1>PIQA Synergy Matrix Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94A3B8;'><b>Live Feed View:</b> <span style='color:#38BDF8;'>{selected_dept}</span> | <b>Tenure Filter Status:</b> <span style='color:#34D399;'>{selected_tenure}</span></p>", unsafe_allow_html=True)
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
            <p style="color:#94A3B8; font-size: 0.8rem; text-transform: uppercase; font-weight:600; margin-bottom:4px;">Sample Size (N)</p>
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

# 5. Graph Configuration using Plotly Dark Template Matrices
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("<div class='section-title'>📊 Response Frequency Distribution Matrix</div>", unsafe_allow_html=True)
    freq_data = filtered_df['Score'].value_counts().sort_index().reset_index()
    freq_data.columns = ['Likert Scale Rating', 'Total Feedback Logs']
    
    # Custom Bar Chart configured to match dark styling themes
    fig_bar = px.bar(
        freq_data, 
        x='Likert Scale Rating', 
        y='Total Feedback Logs',
        color='Total Feedback Logs',
        color_continuous_scale=['#1E40AF', '#3B82F6', '#60A5FA'],
        text_auto=True,
        template="plotly_dark"
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        xaxis=dict(tickmode='linear', gridcolor='#1E293B'),
        yaxis=dict(gridcolor='#1E293B'),
        coloraxis_showscale=False
    )
    fig_bar.update_traces(textfont_color="#FFFFFF")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>🍕 Sentiment Proportions</div>", unsafe_allowed_html=True)
    sentiment_data = filtered_df['Sentiment'].value_counts().reset_index()
    
    fig_pie = px.pie(
        sentiment_data, 
        values='count', 
        names='Sentiment',
        color='Sentiment',
        color_discrete_map={'Positive': '#10B981', 'Neutral': '#F59E0B', 'Negative': '#EF4444'},
        hole=0.5,
        template="plotly_dark"
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. Heatmap Section Matching Dark Grids
st.markdown("<div class='section-title'>⚡ Subgroup Cross-Tabulation Analysis</div>", unsafe_allow_html=True)
xtab = pd.crosstab(df['Department'], df['Score'], normalize='index') * 100
xtab = xtab.round(1)

fig_heat = px.imshow(
    xtab,
    text_auto=True,
    labels=dict(x="Likert Scale Rating Score", y="Department Hub", color="Percentage (%)"),
    x=['1 (Strongly Disagree)', '2 (Disagree)', '3 (Neutral)', '4 (Agree)', '5 (Strongly Agree)'],
    color_continuous_scale='Blues',
    template="plotly_dark"
)
fig_heat.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_family="Inter"
)
st.plotly_chart(fig_heat, use_container_width=True)

# 7. Actionable Recommendation Module
st.markdown("<div class='section-title'>🎯 Priority Action Register Matrix</div>", unsafe_allow_html=True)
if avg_score < 3.8:
    st.error("🚨 **High Alert Action Required:** Current metrics reflect a dip below standard target quality values (< 3.8). Schedule immediate Cross-Functional Team (CFT) meetings to clear process friction bottlenecks.")
else:
    st.success("✨ **Healthy Operational Standard Maintained:** Internal customer loops align with organizational operational health metrics. Continue monthly data cleaning runs to capture emerging workplace variations.")
