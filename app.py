import streamlit as st
import pandas as pd
import gspread
import re
import json
from google.oauth2 import service_account

# Set up page config
st.set_page_config(page_title="PIQA Analytics & Survey Hub", layout="wide")

# ==========================================
# ROBUST AUTHENTICATION ENGINE
# ==========================================
@st.cache_resource(ttl="1h")
def get_gspread_client():
    # 1. Fetch from standard Streamlit connections block
    gs = st.secrets["connections"]["gsheets"]
    
    # 2. Extract and sanitize private key specifically to solve InvalidByte(120, 61)
    # This regex removes all characters except valid Base64 and standard formatting
    raw_key = str(gs.get("private_key", ""))
    clean_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', raw_key)
    
    # 3. Reconstruct into PEM standard 64-character lines
    chunks = [clean_base64[i:i+64] for i in range(0, len(clean_base64), 64)]
    formatted_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
    
    # 4. Construct the credential info dictionary
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
# DATA FETCHING
# ==========================================
def load_data(spreadsheet_id, worksheet="Sheet1"):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet)
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"Google Sheet Fetch Failure: {e}")
        return pd.DataFrame()

# ==========================================
# UI INTERFACE
# ==========================================
def main():
    st.title("📊 PIQA Analytics & Survey Hub")
    
    # Add your logic here...
    sheet_id = st.text_input("Enter Google Sheet ID:")
    if sheet_id:
        df = load_data(sheet_id)
        if not df.empty:
            st.dataframe(df)

if __name__ == "__main__":
    main()
