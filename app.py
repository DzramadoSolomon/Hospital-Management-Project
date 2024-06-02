import streamlit as st
import home
import patients
import doctors

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Patients", "Doctors", "Pharmacy", "About", "Code Snippets"])

    if page == "Home":
        home.show_home_page()
    elif page == "Patients":
        patients.show_patients_page()
    elif page == "Doctors":
        doctors.show_doctors_page()
    elif page == "Pharmacy":
        st.write("Pharmacy Page")
    elif page == "About":
        st.write("About the Database")
    elif page == "Code Snippets":
        st.write("Code Snippets")

if __name__ == "__main__":
    main()
