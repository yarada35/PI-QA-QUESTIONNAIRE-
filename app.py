import streamlit as st
import gspread
from google.oauth2 import service_account

# PAGE CONFIG
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

@st.cache_resource(ttl="1h")
def get_gspread_client():
    # Attempt to load the secrets directly
    # If using Streamlit Secrets, just access st.secrets directly
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    
    try:
        client = get_gspread_client()
        st.success("✅ Dashboard Connected")
    except Exception as e:
        st.error("Authentication Error")
        st.write(f"Error Details: {e}")

if __name__ == "__main__":
    main()
