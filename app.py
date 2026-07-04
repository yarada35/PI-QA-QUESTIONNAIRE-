import streamlit as st
import gspread
from google.oauth2 import service_account

@st.cache_resource(ttl="1h")
def get_gspread_client():
    # Load all secrets as a dictionary
    gs = st.secrets["connections"]["gsheets"]
    
    # Create the credentials dictionary directly from the secrets
    # This assumes your secrets.toml contains all fields from the original JSON
    creds = service_account.Credentials.from_service_account_info(
        dict(gs), 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    try:
        get_gspread_client()
        st.success("✅ Dashboard Connected")
    except Exception as e:
        st.error("Authentication Error")
        st.write("Please ensure your 'secrets.toml' contains the raw, full JSON data.")

if __name__ == "__main__":
    main()
