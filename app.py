import streamlit as st
import gspread
import base64
from google.oauth2 import service_account

@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # 1. Extract and clean the key string
    raw_key = str(gs.get("private_key", ""))
    # Remove header, footer, and all newlines
    clean_base64 = raw_key.replace("-----BEGIN PRIVATE KEY-----", "") \
                          .replace("-----END PRIVATE KEY-----", "") \
                          .replace("\n", "").replace("\r", "").strip()
    
    # 2. Force correct padding (Base64 must be a multiple of 4)
    missing_padding = len(clean_base64) % 4
    if missing_padding:
        clean_base64 += '=' * (4 - missing_padding)
    
    # 3. Reconstruct into a strictly formatted PEM block
    formatted_key = "-----BEGIN PRIVATE KEY-----\n" + \
                    "\n".join([clean_base64[i:i+64] for i in range(0, len(clean_base64), 64)]) + \
                    "\n-----END PRIVATE KEY-----\n"
    
    credentials_info = {
        "type": gs["type"],
        "project_id": gs["project_id"],
        "private_key_id": gs["private_key_id"],
        "private_key": formatted_key,
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

# --- APP UI ---
def main():
    st.set_page_config(layout="wide")
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    
    try:
        client = get_gspread_client()
        st.success("✅ Dashboard successfully authenticated.")
    except Exception as e:
        st.error(f"Authentication Failed: {e}")

if __name__ == "__main__":
    main()
