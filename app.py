import streamlit as st
import pandas as pd
import json
from datetime import datetime

# 1. Page Configuration & Black/Dark Theme Base Initializer
st.set_page_config(
    page_title="PIQA Quality Feedback Loop",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Deep Custom CSS for high-impact typography, dark styling, and clickable layouts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');
    
    /* Force dark theme background */
    .stApp {
        background-color: #0B0F19 !important;
        color: #F1F5F9 !important;
    }
    
    /* Typography Overrides */
    h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #34D399 50%, #FBBF24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        letter-spacing: -0.05em;
        text-align: center;
    }
    
    .instruction-text {
        font-family: 'Inter', sans-serif;
        color: #94A3B8;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .question-block {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 1.5rem;
    }

    .question-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        font-weight: 500;
        color: #F8FAFC;
        margin-bottom: 1rem;
    }
    
    /* Legend styling */
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
    </style>
""", unsafe_allow_html=True)

# 2. Hardcoded Questionnaire Matrix from Source JSONs
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

# Emoji map config
emoji_options = ["1 🤬", "2 🙁", "3 😐", "4 🙂", "5 🤩"]

# Title Banner
st.markdown("<h1>PIQA Internal Satisfaction Intake</h1>", unsafe_allow_html=True)
st.markdown("<p class='instruction-text'>Select your department block below to populate your customized matrix questions.</p>", unsafe_allow_html=True)

# 3. Structural Selection Hub
col_dept, col_tenure = st.columns(2)
with col_dept:
    selected_dept = st.selectbox("Identify Your Active Department:", list(DEPARTMENT_QUESTIONS.keys()))
with col_tenure:
    selected_tenure = st.selectbox("Employee Plant Tenure:", ["< 1 Year", "1-3 Years", "3+ Years"])

st.markdown("---")

# Visual Likert Scale Reference Key
st.markdown("""
    <div class="scale-legend">
        <span><b>1</b> 🤬 Strongly Disagree</span>
        <span><b>2</b> 🙁 Disagree</span>
        <span><b>3</b> 😐 Neutral</span>
        <span><b>4</b> <b>🙂 Agree</b></span>
        <span><b>5</b> <b>🤩 Strongly Agree</b></span>
    </div>
""", unsafe_allow_html=True)

# 4. Form Submission Engine
with st.form("survey_form", clear_on_submit=True):
    responses = {}
    questions = DEPARTMENT_QUESTIONS[selected_dept]
    
    # Loop over the actual verbatim target questionnaire items
    for idx, question in enumerate(questions):
        st.markdown(f"""
            <div class="question-block">
                <div class="question-text"><b>Q{idx+1}.</b> {question}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Segmented controls provide a highly clickable option array
        score_selection = st.segmented_control(
            label=f"Rating Choice for Q{idx+1}",
            options=emoji_options,
            key=f"q_{idx+1}",
            label_visibility="collapsed"
        )
        responses[f"Question {idx+1}"] = {
            "criteria": question,
            "selected_rating": score_selection
        }
        st.markdown("<br>", unsafe_allow_html=True)

    # Qualitative Input Field
    st.markdown("### 📝 Additional Points or Recommendations")
    additional_notes = st.text_area(
        "If you have additional points please specify:",
        label_visibility="collapsed",
        placeholder="Type any process updates, structural notes, or comments here..."
    )

    # Form Submission Trigger Button
    submit_btn = st.form_submit_button("Submit Final Survey Entries")

# 5. Clean Structured Output Processing
if submit_btn:
    # Validation loop ensuring all questions received a rating
    incomplete = [q for q, data in responses.items() if data["selected_rating"] is None]
    
    if incomplete:
        st.error("⚠️ **Incomplete Fields Detected:** Please make sure to select an interactive emoji rating for all items before submitting.")
    else:
        # Construct clean JSON payload for your Data Preparation phase
        final_payload = {
            "timestamp": datetime.now().isoformat(),
            "department": selected_dept,
            "tenure": selected_tenure,
            "responses": [
                {
                    "item_id": q_key,
                    "criteria": val["criteria"],
                    "score": int(val["selected_rating"][0])  # Extracts the digit (1-5) from the chosen string option
                } for q_key, val in responses.items()
            ],
            "qualitative_feedback": additional_notes
        }
        
        st.success("🎉 **Feedback Recorded Successfully!** Thank you for helping optimize our inter-departmental operations.")
        
        # Provide clean down-stream export matching your exact pipeline parameters
        json_string = json.dumps(final_payload, indent=2)
        st.download_button(
            label="📥 Download Clean Raw Data (.json)",
            data=json_string,
            file_name=f"PIQA_Raw_{selected_dept.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        
        # Preview payload
        with st.expander("🔬 View Structured Data Output Preview (Step 1 Cleaning Pipeline)"):
            st.code(json_string, language="json")
