import streamlit as st
import gspread
from google.oauth2 import service_account

# --- PAGE CONFIG ---
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #05070F !important; color: #F1F5F9 !important; }
    </style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ENGINE ---
@st.cache_resource(ttl="1h")
def get_gspread_client():
    # Load secrets directly from Streamlit
    gs = st.secrets["connections"]["gsheets"]
    
    # Create credentials dictionary directly from the TOML structure
    # This assumes your TOML keys match the Google Service Account JSON keys
    creds = service_account.Credentials.from_service_account_info(
        dict(gs), 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

# --- MAIN UI ---
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    
    # Separate the connection attempt from the UI rendering
    try:
        # If this fails, it jumps to the 'except' block, but the UI below still loads
        client = get_gspread_client()
        st.success("✅ Dashboard Connected")
    except Exception as e:
        # Log the error without crashing the page
        st.error("Authentication Error: Connection to Google Sheets failed.")
        st.write(f"Technical Details: {e}")

    # UI Components that will ALWAYS display, even if connection fails
    st.write("Unified suite for live operational analysis and internal raw feedback collection loops.")
    
    tab1, tab2, tab3 = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print Hub"])
    
    with tab1:
        st.write("Dashboard content loading...")
    with tab2:
        st.write("Survey intake form ready.")
    with tab3:
        st.write("Print and distribution hub ready.")

if __name__ == "__main__":
    main()
