import streamlit as st
import gspread
from google.oauth2 import service_account

# PAGE CONFIGURATION
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

# AUTHENTICATION ENGINE
@st.cache_resource(ttl="1h")
def get_gspread_client():
    """
    Loads credentials directly from Streamlit secrets. 
    The library natively handles the dictionary structure 
    and PEM formatting without manual string manipulation.
    """
    # Fetch the connection block as a dictionary from secrets
    creds_dict = st.secrets["connections"]["gsheets"]
    
    # Initialize credentials directly
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

# MAIN INTERFACE
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    
    # Handle connection and UI rendering separately to prevent blank pages
    try:
        client = get_gspread_client()
        st.success("✅ Dashboard Connected Successfully")
    except Exception as e:
        st.error("Authentication Error: Configuration handshake failed.")
        st.info("Ensure your Secrets panel contains the full, valid JSON structure.")
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
