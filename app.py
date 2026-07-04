import streamlit as st
import gspread
import re
from google.oauth2 import service_account

# PAGE CONFIG
st.set_page_config(page_title="PIQA Analytics & Survey Hub", layout="wide")

@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # 1. Extract raw key
    raw_key = str(gs.get("private_key", ""))
    
    # 2. AGGRESSIVE CLEANUP: 
    # This regex removes EVERYTHING except A-Z, a-z, 0-9, +, /, and =
    clean_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_key)
    
    # 3. Reconstruct into standard 64-char lines to satisfy PEM requirements
    chunks = [clean_base64[i:i+64] for i in range(0, len(clean_base64), 64)]
    formatted_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
    
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

def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    try:
        client = get_gspread_client()
        st.success("✅ Dashboard connected.")
    except Exception as e:
        st.error(f"Authentication Failed: {e}")
        st.info("The system is still detecting invalid characters in your 'private_key'.")

if __name__ == "__main__":
    main()
