import streamlit as st
import gspread
import re
from google.oauth2 import service_account

# Page Config
st.set_page_config(page_title="PIQA Analytics & Survey Hub", layout="wide")

# Styling to keep the professional look active even during errors
st.markdown("""
    <style>
    .stApp { background-color: #05070F !important; color: #F1F5F9 !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # BRUTE-FORCE SANITIZATION:
    # 1. Take the raw string
    raw = str(gs.get("private_key", ""))
    # 2. Extract ONLY valid base64 chars (A-Z, a-z, 0-9, +, /)
    # This specifically removes the '.' character (ASCII 46) causing your error
    clean_base64 = re.sub(r'[^A-Za-z0-9+/]', '', raw)
    
    # 3. Rebuild the PEM format standard
    formatted_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join([clean_base64[i:i+64] for i in range(0, len(clean_base64), 64)]) + "\n-----END PRIVATE KEY-----\n"
    
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

# Main UI
def main():
    st.title("PIQA Live Matrix Portal")
    try:
        client = get_gspread_client()
        st.success("Dashboard Initialized")
    except Exception as e:
        st.error(f"Authentication Failed: {e}")

if __name__ == "__main__":
    main()
