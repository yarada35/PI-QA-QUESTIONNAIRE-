import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration & Artistic Style Injection
st.set_page_config(
    page_title="PIQA Analytics | Mosaic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for artistic fonts, gradient headers, and interactive UI card styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@700;800&family=Inter:wght@400;500&display=swap');
    
    /* Typography Overrides */
    .main h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #3B82F6 0%, #10B981 50%, #F59E0B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        letter-spacing: -0.05em;
    }
    
    .section-title {
        font-family: 'Syne', sans-serif;
        color: #1E293B;
        font-size: 1.75rem;
        font-weight: 700;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.25rem;
        margin-bottom: 1.5rem;
    }

    body, p, label {
        font-family: 'Inter', sans-serif;
    }
    
    /* Interactive Custom Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* Emoji Selector Badges */
    .emoji-badge {
        font-size: 1.5rem;
        padding: 10px;
        border-radius: 12px;
        text-align: center;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allowed_html=True)

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

# 3. Sidebar Header & Visual Badge Department Navigation
with st.sidebar:
    st.markdown("<h2 style='font-family:\"Syne\"; color:#3B82F6;'>🎨 Control Room</h2>", unsafe_allowed_html=True)
    st.markdown("---")
    
    st.markdown("**Select Department Target Loop:**")
    # Instead of an old drop-down, using clear pill-selectors for instant visual switching
    selected_dept = st.radio(
        label="Target Departments",
        options=['All Departments'] + list(df['Department'].unique()),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**Demographic Filtering Crosstab:**")
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

# 4. Main Canvas - Dynamic Visual Analytics Dashboard
st.markdown("<h1>PIQA Synergy Matrix Dashboard</h1>", unsafe_allowed_html=True)
st.markdown(f"**Live Feed View:** `{selected_dept}` | Tenure Status: `{selected_tenure}`")
st.markdown("---")

# High Impact Summary Cards 
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_score = round(filtered_df['Score'].mean(), 2)
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3B82F6;">
            <p style="color:#64748B; font-size: 0.8rem; text-transform: uppercase; font-weight:600;">Composite Mean Score</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#1E293B; margin:0;">{avg_score} <span style="font-size:1.2rem; color:#3B82F6;">/ 5.0</span></h2>
        </div>
    """, unsafe_allowed_html=True)

with col2:
    total_responses = len(filtered_df)
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <p style="color:#64748B; font-size: 0.8rem; text-transform: uppercase; font-weight:600;">Sample Size (N)</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#1E293B; margin:0;">{total_responses}</h2>
        </div>
    """, unsafe_allowed_html=True)

with col3:
    pos_pct = round((len(filtered_df[filtered_df['Sentiment'] == 'Positive']) / total_responses) * 180) if total_responses > 0 else 0
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <p style="color:#64748B; font-size: 0.8rem; text-transform: uppercase; font-weight:600;">Satisfaction index</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#1E293B; margin:0;">{pos_pct}%</h2>
        </div>
    """, unsafe_allowed_html=True)

with col4:
    mode_score = filtered_df['Score'].mode()[0] if not filtered_df.empty else 3
    emoji_star = "🤩" if mode_score == 5 else ("🙂" if mode_score == 4 else "😐")
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #F59E0B;">
            <p style="color:#64748B; font-size: 0.8rem; text-transform: uppercase; font-weight:600;">Dominant Sentiment</p>
            <h2 style="font-family:'Space Grotesk'; font-size:2.2rem; color:#1E293B; margin:0;">Level {mode_score} {emoji_star}</h2>
        </div>
    """, unsafe_allowed_html=True)

st.markdown("<br>", unsafe_allowed_html=True)

# 5. Visualizing Frequencies via Interactive Graphs
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("<div class='section-title'>📊 Response Frequency Distribution Matrix</div>", unsafe_allowed_html=True)
    freq_data = filtered_df['Score'].value_counts().sort_index().reset_index()
    freq_data.columns = ['Likert Scale Rating', 'Total Feedback Logs']
    
    # Artistic Color Palette Configured Chart
    fig_bar = px.bar(
        freq_data, 
        x='Likert Scale Rating', 
        y='Total Feedback Logs',
        color='Total Feedback Logs',
        color_continuous_scale=['#93C5FD', '#3B82F6', '#1D4ED8'],
        text_auto=True
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        xaxis=dict(tickmode='linear'),
        coloraxis_showscale=False
    )
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
        hole=0.5
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. Qualitative Insights & Subgroup Cross-Tabulations
st.markdown("<div class='section-title'>⚡ Subgroup Cross-Tabulation Analysis</div>", unsafe_allowed_html=True)
xtab = pd.crosstab(df['Department'], df['Score'], normalize='index') * 100
xtab = xtab.round(1)

# Heatmap visual for cross-tabulation metrics without relying on standard dataframes
fig_heat = px.imshow(
    xtab,
    text_auto=True,
    labels=dict(x="Likert Scale Rating Score", y="Department Hub", color="Percentage (%)"),
    x=['1 (Strongly Disagree)', '2 (Disagree)', '3 (Neutral)', '4 (Agree)', '5 (Strongly Agree)'],
    color_continuous_scale='Mint'
)
fig_heat.update_layout(font_family="Inter")
st.plotly_chart(fig_heat, use_container_width=True)

# 7. Actionable Recommendation Module
st.markdown("<div class='section-title'>🎯 Priority Action Register Matrix</div>", unsafe_allowed_html=True)
if avg_score < 3.8:
    st.error("🚨 **High Alert Action Required:** Current metrics reflect a dip below standard target quality values ($<3.8$). Schedule immediate Cross-Functional Team (CFT) meetings to clear process friction bottlenecks.")
else:
    st.success("✨ **Healthy Operational Standard Maintained:** Internal customer loops align with organizational operational health metrics. Continue monthly data cleaning runs to capture emerging workplace variations.")
