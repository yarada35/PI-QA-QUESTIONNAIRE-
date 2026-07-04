import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

# INITIALIZE MEMORY
# This creates a local list to store feedback during the session
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    st.write("Unified suite for live operational analysis and internal feedback.")

    tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "📝 Interactive Feedback Intake"])

    with tab1:
        st.subheader("Live Operational Overview")
        if not st.session_state.feedback_log:
            st.info("No feedback submitted in this session yet.")
        else:
            st.write("### Captured Feedback Entries:")
            for idx, entry in enumerate(st.session_state.feedback_log, 1):
                st.markdown(f"**{idx}.** {entry}")

    with tab2:
        st.subheader("Submit Feedback")
        with st.form("feedback_form", clear_on_submit=True):
            user_input = st.text_area("Enter your feedback here:")
            submitted = st.form_submit_button("Submit Feedback")
            
            if submitted and user_input:
                st.session_state.feedback_log.append(user_input)
                st.success("Feedback captured locally!")
            elif submitted and not user_input:
                st.warning("Please enter some text before submitting.")

if __name__ == "__main__":
    main()
