import streamlit as st
import pandas as pd
import gspread
import re
from google.oauth2 import service_account

# ==========================================
# 1. PAGE SETUP & UI STYLING
# ==========================================
st.set_page_config(
    page_title="PIQA Analytics & Survey Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the dashboard aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #05070F !important; color: #F1F5F9 !important; }
    [data-testid="stSidebar"] { background-color: #090D16 !important; border-right: 1px solid #1E293B !important; }
    .main h1 { font-family: 'Syne', sans-serif; font-weight: 800; background: linear-gradient(135deg, #38BDF8 0%, #34D399 50%, #FBBF24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-card { background: #111827; border-radius: 16px; padding: 24px; border: 1px solid #1E293B; border-left: 6px solid #38BDF8; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 1.6rem !important; font-weight: 800 !important; font-family: 'Syne', sans-serif !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SANITIZED AUTHENTICATION ENGINE
# ==========================================
@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # Strictly sanitize key to base64 only to prevent InvalidByte(120, 61) errors
    raw_key = str(gs.get("private_key", ""))
    clean_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_key)
    
    # Reconstruct into PEM standard 64-character lines
    chunks = [clean_base64[i:i+64] for i in range(0, len(clean_base64), 64)]
    formatted_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
    
    credentials_info = {
        "type": gs["type"],
        "project_id": gs["project_id"],
        "private_key_id": gs["private_key_id"],
        "client_email": gs["client_email"],
        "client_id": gs["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": gs["client_x509_cert_url"],
        "private_key": formatted_key
    }
    
    creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

# ==========================================
# 3. APP INTERFACE
# ==========================================
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    st.write("Unified suite for live operational analysis and internal raw feedback collection loops.")

    with st.sidebar:
        st.markdown("<h2 style='color:#38BDF8;'>🎨 Control Room</h2>", unsafe_allow_html=True)
        st.radio("Target Departments Filter", [
            'All Matrix Mix', 'Plant Engineering Department', 'Production Department', 
            'Sales and Marketing Department', 'PIQA Employee Staff', 'Purchase Department', 'Store Department'
        ])

    tab1, tab2, tab3 = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print Hub"])

    with tab1:
        try:
            # Trigger authentication to display dashboard contents
            client = get_gspread_client()
            st.success("✅ Dashboard connected successfully.")
            # Data visualization logic would follow here
        except Exception as e:
            st.error(f"Initialization Error: {e}")

    with tab2:
        st.write("Interactive Survey Intake portal is ready.")

    with tab3:
        st.write("Print and Distribution Hub.")

if __name__ == "__main__":
    main()
