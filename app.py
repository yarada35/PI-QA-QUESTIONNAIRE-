import streamlit as st
import gspread
from google.oauth2 import service_account

# PAGE CONFIGURATION
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

# AUTHENTICATION ENGINE
@st.cache_resource(ttl="1h")
def get_gspread_client():
    """
    Loads credentials from a flat secret structure.
    This bypasses nested dictionaries that cause handshake failures.
    """
    # Load all secrets as a flat dictionary
    creds_dict = st.secrets
    
    # Initialize credentials directly
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

# MAIN INTERFACE
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    
    # Separate connection attempt from UI rendering to prevent blank screens
    try:
        client = get_gspread_client()
        st.success("✅ Dashboard Connected Successfully")
    except Exception as e:
        st.error("Authentication Error: Configuration handshake failed.")
        st.info("Ensure your Secrets panel contains the flat, full JSON structure.")
        with st.expander("See Diagnostic Logs"):
            st.code(str(e))

    # Dashboard Layout
    tab1, tab2, tab3 = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print Hub"])
    
    with tab1:
        st.subheader("Operational Overview")
        st.write("Metrics visualizers will populate once database hooks validate successfully.")
    with tab2:
        st.subheader("Data Intake Form")
        st.write("Department survey forms operational environment.")

if __name__ == "__main__":
    main()
