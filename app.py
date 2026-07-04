import streamlit as st
import gspread
import re
from google.oauth2 import service_account

@st.cache_resource(ttl="1h")
def get_gspread_client():
    gs = st.secrets["connections"]["gsheets"]
    
    # Get the key and ensure it's a string
    raw_key = str(gs.get("private_key", ""))
    
    # If the key is just the base64 content (no headers/footers), add them back
    # This logic handles both multi-line and single-line inputs
    if "-----BEGIN PRIVATE KEY-----" not in raw_key:
        # Reconstruct PEM format
        clean_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_key)
        chunks = [clean_base64[i:i+64] for i in range(0, len(clean_base64), 64)]
        formatted_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
    else:
        # If it already has headers, just replace escaped \n with actual newlines
        formatted_key = raw_key.replace('\\n', '\n')

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

# ... rest of your UI code ...
