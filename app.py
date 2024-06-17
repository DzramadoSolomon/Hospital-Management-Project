import streamlit as st
import home
import patients
import doctors
import pharmacy
import administrators
import about

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Patients", "Doctors", "Pharmacy", "Administrators", "About", "Code Snippets"])

    if page == "Home":
        home.show_home_page()
    elif page == "Patients":
        patients.show_patients_page()
    elif page == "Doctors":
        doctors.show_doctors_page()
    elif page == "Pharmacy":
        pharmacy.show_pharmacy_page()
    elif page == "Administrators":
        administrators.show_administrator_page()
    elif page == "About":
        about.show_about_page()
    elif page == "Code Snippets":
        st.write("Code Snippets")

if __name__ == "__main__":
    main()
