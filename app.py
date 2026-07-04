import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import json
import re

# Set up page config
st.set_page_config(page_title="Google Sheets Data Connection", layout="wide")

# ==========================================
# ABSOLUTE CRASH-PROOF AUTHENTICATION ENGINE
# ==========================================
@st.cache_resource(ttl="1h")
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 1. Extract dictionary keys directly from Streamlit's structural layers
    secrets_dict = {}
    
    # Layer A: Check root level
    for k in st.secrets.keys():
        if k != "connections":
            secrets_dict[k] = st.secrets[k]
            
    # Layer B: Check nested connection blocks (the classic [connections.gsheets] structure)
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        for k, v in st.secrets["connections"]["gsheets"].items():
            secrets_dict[k] = v

    # 2. Build our explicit credentials dictionary using standard structured keys
    credentials_info = {}
    
    # Simple direct dictionary extraction for standard text fields
    for field in ["type", "project_id", "private_key_id", "client_email", "client_id", "client_x509_cert_url"]:
        if field in secrets_dict:
            credentials_info[field] = str(secrets_dict[field]).strip().strip('"').strip("'")

    # 3. HIGH-POWER REGEX ONLY FOR THE PRIVATE KEY (The multi-line string culprit)
    raw_dump = str(st.secrets) + "\n" + json.dumps(secrets_dict)
    raw_dump = raw_dump.replace("\\n", "\n").replace("\\\\n", "\n")
    
    crypto_match = re.search(r"-----BEGIN PRIVATE KEY-----(.*?)-----END PRIVATE KEY-----", raw_dump, re.DOTALL)
    if crypto_match:
        pure_crypto_body = crypto_match.group(1)
        pure_crypto_body = re.sub(r'[^A-Za-z0-9+/=\s]', '', pure_crypto_body)
        clean_lines = [line.strip() for line in pure_crypto_body.split("\n") if line.strip()]
        credentials_info["private_key"] = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(clean_lines) + "\n-----END PRIVATE KEY-----\n"
    elif "private_key" in secrets_dict:
        raw_pk = str(secrets_dict["private_key"])
        raw_pk = raw_pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        raw_pk = re.sub(r'[^A-Za-z0-9+/=\s]', '', raw_pk)
        clean_lines = [line.strip() for line in raw_pk.split("\n") if line.strip()]
        credentials_info["private_key"] = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(clean_lines) + "\n-----END PRIVATE KEY-----\n"

    # 4. Global Endpoint Fallbacks
    credentials_info["token_uri"] = secrets_dict.get("token_uri", "https://oauth2.googleapis.com/token")
    credentials_info["auth_uri"] = secrets_dict.get("auth_uri", "https://accounts.google.com/o/oauth2/auth")
    credentials_info["auth_provider_x509_cert_url"] = secrets_dict.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs")

    # Verify if fields are missing now
    required_fields = ["type", "project_id", "client_email", "private_key"]
    missing = [f for f in required_fields if f not in credentials_info]
    
    if missing:
        st.error(f"🚨 Missing Key Fields from Secrets Stream: {missing}.")
        st.info(f"Available keys parsed: {list(credentials_info.keys())}")
        st.stop()

    try:
        creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Auth initialization failed: {e}")
        st.stop()

# ==========================================
# DATA FETCH ENGINE
# ==========================================
def load_sheet_data(spreadsheet_id, sheet_name="Sheet1"):
    try:
        client = get_gspread_client()
        # Open by ID is much faster and less prone to name conflicts
        sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Google Sheet Fetch Failure: {e}")
        return None

# ==========================================
# APP MAIN INTERFACE
# ==========================================
def main():
    st.title("📊 Google Sheets Live Dashboard")
    
    # URL or Sheet ID input field
    # (Extracts the ID automatically if they paste a full browser URL)
    raw_input = st.text_input(
        "Enter Google Sheet ID or Full Browser URL:",
        placeholder="1H_xxxx_spreadsheet_id_xxxx"
    )
    
    sheet_name_input = st.text_input("Worksheet Name (Tab Name):", value="Sheet1")
    
    if raw_input:
        # Clean ID out of a raw URL link if pasted
        sheet_id = raw_input
        if "docs.google.com/spreadsheets" in raw_input:
            match = re.search(r"/d/([a-zA-Z0-9-_]+)", raw_input)
            if match:
                sheet_id = match.group(1)
        
        st.write("---")
        with st.spinner("Fetching live spreadsheet data..."):
            df = load_sheet_data(sheet_id, sheet_name_input)
            
        if df is not None:
            st.success(f"Successfully loaded {len(df)} rows!")
            
            # Metric summaries for instant health check
            col1, col2 = st.columns(2)
            col1.metric("Total Rows", df.shape[0])
            col2.metric("Total Columns", df.shape[1])
            
            # Interactive data preview
            st.subheader("Data Preview")
            st.dataframe(df, use_container_width=True)
            
            # Simple data download option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"{sheet_name_input}_data.csv",
                mime="text/csv",
            )
    else:
        st.info("💡 Paste your Google Spreadsheet URL or Key ID above to view your real-time data.")
        st.warning("🔒 Make sure your Sheet has been shared with the `client_email` address listed in your credentials json!")

if __name__ == "__main__":
    main()
