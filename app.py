import streamlit as st
import gspread
import json
from google.oauth2 import service_account

# --- PROPER PAGE INITIALIZATION ---
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

@st.cache_resource(ttl="1h")
def get_gspread_client():
    """
    Directly converts Streamlit connections secrets into a native 
    credentials object without string manual manipulation.
    """
    # Fetch your secrets section directly
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # Safely convert the mapping object to a standard Python dictionary
    credentials_dict = dict(gs_secrets)
    
    # Standardize the private key format dynamically
    if "private_key" in credentials_dict:
        # Handle string variations directly if they contain escaped literal '\n'
        credentials_dict["private_key"] = credentials_dict["private_key"].replace('\\n', '\n')

    # Authorize using the raw structured config dictionary
    creds = service_account.Credentials.from_service_account_info(
        credentials_dict, 
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(creds)

# --- APPLICATION INTERFACE ---
def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    st.write("Unified suite for live operational analysis and internal raw feedback collection loops.")

    # Isolated connection state testing block
    try:
        client = get_gspread_client()
        st.success("✅ Dashboard Connected Successfully")
    except Exception as e:
        st.error("Authentication Error: Configuration handshake failed.")
        st.info("Please inspect the precise formatting inside your Streamlit Cloud Settings panel.")
        with st.expander("See Diagnostic Logs"):
            st.code(str(e))

    # Structural Dashboard Layout Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Live Analytics Dashboard", "📝 Interactive Survey Intake", "🖨️ Print Hub"])
    
    with tab1:
        st.subheader("Operational Overview")
        st.info("Metrics visualizers will populate once database hooks validate successfully.")
        
    with tab2:
        st.subheader("Data Intake Form")
        st.write("Department survey forms operational environment.")

if __name__ == "__main__":
    main()
