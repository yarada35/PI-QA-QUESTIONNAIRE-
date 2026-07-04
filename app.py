import streamlit as st
import gspread
import re
import base64
from google.oauth2 import service_account

@st.cache_resource(ttl="1h")
def get_gspread_client():
    # Load secrets
    gs = st.secrets["connections"]["gsheets"]
    
    # 1. Force the key to be a string
    raw_key = str(gs.get("private_key", ""))
    
    # 2. Extract only valid Base64 characters (strip all newlines, spaces, and underscores)
    clean_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_key)
    
    # 3. Ensure proper padding for the Base64 string
    missing_padding = len(clean_b64) % 4
    if missing_padding:
        clean_b64 += '=' * (4 - missing_padding)
    
    # 4. Reconstruct the full, clean PEM formatted string
    formatted_key = "-----BEGIN PRIVATE KEY-----\n" + \
                    "\n".join([clean_b64[i:i+64] for i in range(0, len(clean_b64), 64)]) + \
                    "\n-----END PRIVATE KEY-----\n"
    
    # 5. Build credentials
    creds_dict = {
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
        creds_dict, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    ))

def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    try:
        get_gspread_client()
        st.success("✅ Dashboard Connected")
    except Exception as e:
        st.error("Authentication Error")
        st.write(f"Details: {e}")

if __name__ == "__main__":
    main()
