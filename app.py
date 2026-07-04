import streamlit as st
import pandas as pd
import gspread
import re
import json
from google.oauth2 import service_account

# --- PAGE CONFIG ---
st.set_page_config(page_title="PIQA Analytics & Survey Hub", layout="wide")

# --- AUTHENTICATION ENGINE ---
@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # AGGRESSIVE CLEANUP: 
    # 1. Convert literal string "\n" to actual newlines
    # 2. Extract the key material precisely
    raw_key = str(gs.get("private_key", ""))
    
    # Handle both real newlines and escaped "\n" sequences
    clean_key = raw_key.replace('\\n', '\n').strip()
    
    # Ensure the key is wrapped correctly if the header/footer were stripped
    if "-----BEGIN PRIVATE KEY-----" not in clean_key:
        clean_key = f"-----BEGIN PRIVATE KEY-----\n{clean_key}\n-----END PRIVATE KEY-----"

    credentials_info = {
        "type": gs["type"],
        "project_id": gs["project_id"],
        "private_key_id": gs["private_key_id"],
        "private_key": clean_key,
        "client_email": gs["client_email"],
        "client_id": gs["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": gs["client_x509_cert_url"]
    }
    
    return gspread.authorize(service_account.Credentials.from_service_account_info(
        credentials_info, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    ))

# --- MAIN UI ---
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## 🎨 Control Room")
        st.radio("Target Departments Filter", [
            'All Matrix Mix', 'Plant Engineering Department', 'Production Department', 
            'Sales and Marketing Department', 'PIQA Employee Staff', 'Purchase Department', 'Store Department'
        ])

    tab1, tab2, tab3 = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print Hub"])

    with tab1:
        try:
            client = get_gspread_client()
            st.success("✅ Dashboard connected.")
        except Exception as e:
            st.error(f"Authentication Failed: {e}")
            st.info("Check your 'private_key' formatting in Streamlit Secrets.")

if __name__ == "__main__":
    main()
