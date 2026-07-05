import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(page_title="PIQA Live Matrix Portal", layout="wide")

# INITIALIZE SESSION STATE
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = []

def main():
    st.markdown("<h1>PIQA Live Matrix Portal</h1>", unsafe_allow_html=True)
    st.write("Unified suite for live operational analysis and internal feedback collection loops.")

    # NAVIGATION TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analytics Dashboard", 
        "📝 Department Survey Intake", 
        "🎛️ Control Room Pad", 
        "🖨️ Printing & Export"
    ])

    with tab1:
        st.subheader("Analysis Pad")
        st.write("Live performance metrics and trend analysis.")
        # Analytics logic here

    with tab2:
        st.subheader("Interactive Department Survey")
        dept = st.selectbox("Select Department:", ["PI & QA", "Manufacturing", "Logistics", "Strategic Planning"])
        feedback = st.text_area("Enter raw feedback for this department:")
        
        if st.button("Submit Survey"):
            st.session_state.feedback_data.append({"Dept": dept, "Feedback": feedback})
            st.success(f"Feedback submitted for {dept}")

    with tab3:
        st.subheader("Control Room Pad")
        st.write("Manual override and operational tracking tools.")
        if st.button("Refresh Systems"):
            st.rerun()

    with tab4:
        st.subheader("Final Printing Pad")
        if st.session_state.feedback_data:
            st.write(st.session_state.feedback_data)
            st.download_button("Download Report", str(st.session_state.feedback_data), "report.txt")
        else:
            st.info("No data available to print.")

if __name__ == "__main__":
    main()
