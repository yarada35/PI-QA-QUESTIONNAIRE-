# ==========================================
# 3. Explicit Connection Credentials Configuration
# ==========================================
# 1. Clean out the broken secrets dashboard from the app's internal memory
if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    del st.secrets._secrets["connections"]["gsheets"]

# 2. Paste your UNALTERED credentials here directly from your downloaded Google JSON file
GOOGLE_CREDENTIALS_DATA = {
    "type": "service_account",
    "project_id": "YOUR_PROJECT_ID",
    "private_key_id": "YOUR_PRIVATE_KEY_ID",
    "private_key": """-----BEGIN PRIVATE KEY-----
PASTE_YOUR_LONG_CRYPTO_KEY_STRING_HERE
-----END PRIVATE KEY-----""",
    "client_email": "YOUR_SERVICE_ACCOUNT_EMAIL@PROJECT.iam.gserviceaccount.com",
    "client_id": "YOUR_CLIENT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT_EMAIL"
}

TARGET_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE"

# 3. Clean line breaks and force a strict 64-character formatting wrap on the key string
if "private_key" in GOOGLE_CREDENTIALS_DATA:
    raw_key = GOOGLE_CREDENTIALS_DATA["private_key"].replace("\\n", "\n").strip()
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    body = raw_key.replace(header, "").replace(footer, "").replace("\n", "").replace(" ", "").strip()
    chunks = [body[i:i+64] for i in range(0, len(body), 64)]
    GOOGLE_CREDENTIALS_DATA["private_key"] = f"{header}\n" + "\n".join(chunks) + f"\n{footer}\n"

# 4. Pass the cleaned credentials directly into the connection initialization layout
conn = st.connection(
    "gsheets",
    type=GSheetsConnection,
    spreadsheet=TARGET_SPREADSHEET_URL,
    **GOOGLE_CREDENTIALS_DATA
)
