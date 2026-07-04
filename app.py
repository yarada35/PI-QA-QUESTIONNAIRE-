import streamlit as st
import pandas as pd
import gspread
import re
from google.oauth2 import service_account

# --- PAGE SETUP ---
st.set_page_config(page_title="PIQA Analytics & Survey Hub", layout="wide")

# Styling for the professional dashboard look
st.markdown("""
    <style>
    .stApp { background-color: #05070F !important; color: #F1F5F9 !important; }
    [data-testid="stSidebar"] { background-color: #090D16 !important; border-right: 1px solid #1E293B !important; }
    .main h1 { color: #38BDF8 !important; font-family: 'Syne', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- SANITIZED AUTHENTICATION ENGINE ---
@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # Force clean the key: Remove all JSON-style escapes and non-base64 chars
    raw_key = str(gs.get("private_key", ""))
    clean_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_key.replace('\\n', ''))
    
    # Reconstruct PEM format (64 chars per line)
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
    
    return gspread.authorize(service_account.Credentials.from_service_account_info(
        credentials_info, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    ))

# --- DASHBOARD UI ---
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<h2 style='color:#38BDF8;'>🎨 Control Room</h2>", unsafe_allow_html=True)
        st.radio("Target Departments Filter", [
            'All Matrix Mix', 'Plant Engineering Department', 'Production Department', 
            'Sales and Marketing Department', 'PIQA Employee Staff', 'Purchase Department', 'Store Department'
        ])

    tab1, tab2, tab3 = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print Hub"])

    with tab1:
        try:
            client = get_gspread_client()
            st.success("✅ Dashboard connected successfully.")
        except Exception as e:
            st.error(f"Initialization Error: {e}")

    with tab2:
        st.write("Survey intake form active.")

    with tab3:
        st.write("Print and distribution hub active.")

if __name__ == "__main__":
    main()
