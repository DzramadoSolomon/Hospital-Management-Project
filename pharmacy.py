import streamlit as st
import psycopg2
import pandas as pd

# Function to establish connection to PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="hospitalManagement",
            user="postgres",
            password="#lydia4578",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Function to verify pharmacist credentials
def verify_pharmacist(pharmacist_id, last_name):
    conn = connect_to_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM pharmacists WHERE pharmacist_id = %s AND last_name = %s;", (pharmacist_id, last_name))
        pharmacist = cur.fetchone()
        return pharmacist is not None
    except Exception as e:
        st.error(f"Error verifying pharmacist: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# Function to retrieve patient data
def get_patient_data(patient_id):
    conn = connect_to_db()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT first_name, last_name, doctor_report, drug_recommendation FROM patients WHERE patient_id = %s;", (patient_id,))
        patient_data = cur.fetchone()
        return patient_data
    except Exception as e:
        st.error(f"Error retrieving patient data: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Function to add prescription to pharmacy records
def add_prescription(patient_id, pharmacist_id, drug_name, price, dosage):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO prescriptions (patient_id, pharmacist_id, drug_name, price, dosage)
            VALUES (%s, %s, %s, %s, %s);
        """, (patient_id, pharmacist_id, drug_name, price, dosage))
        conn.commit()
        st.success("Prescription added successfully!")
    except Exception as e:
        st.error(f"Error adding prescription: {e}")
    finally:
        cur.close()
        conn.close()

# Function to get prescription data by patient ID
def get_prescription_data(patient_id):
    conn = connect_to_db()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM prescriptions WHERE patient_id = %s;", (patient_id,))
        data = cur.fetchall()
        return data
    except Exception as e:
        st.error(f"Error retrieving prescription data: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Function to download prescription data for a specific patient
def download_prescription_data(patient_id):
    data = get_prescription_data(patient_id)
    if data:
        df = pd.DataFrame(data, columns=["Prescription ID", "Patient ID", "Pharmacist ID", "Drug Name", "Price", "Dosage"])
        csv = df.to_csv(index=False)
        st.download_button(label="Download Prescription Data", data=csv, file_name=f"prescription_data_patient_{patient_id}.csv", mime='text/csv')
    else:
        st.info(f"No prescription data available for patient ID {patient_id}.")

def show_pharmacy_page():
    st.title("Pharmacy")

    if "pharmacist_logged_in" not in st.session_state:
        st.session_state.pharmacist_logged_in = False
    if "show_logout_confirmation" not in st.session_state:
        st.session_state.show_logout_confirmation = False

    if st.session_state.pharmacist_logged_in:
        page = st.radio("Select Action", ["View Patient Data", "Add Prescription", "Download Prescription Data"])

        if page == "View Patient Data":
            st.subheader("Enter Patient ID")
            patient_id = st.text_input("Patient ID")

            if st.button("Get Patient Information"):
                patient_data = get_patient_data(patient_id)
                if patient_data:
                    first_name, last_name, doctor_report, drug_recommendation = patient_data
                    st.subheader("Patient Information")
                    st.write(f"First Name: {first_name}")
                    st.write(f"Last Name: {last_name}")
                    st.write(f"Doctor's Report: {doctor_report}")
                    st.write(f"Drug Recommendation: {drug_recommendation}")

        elif page == "Add Prescription":
            st.subheader("Add Prescription")
            with st.form("add_prescription_form"):
                patient_id = st.text_input("Patient ID")
                drug_name = st.text_input("Drug Name")
                price = st.number_input("Price")
                dosage = st.text_area("Dosage")
                add_prescription_submit = st.form_submit_button("Add Prescription")

                if add_prescription_submit:
                    pharmacist_id = st.session_state.pharmacist_id
                    add_prescription(patient_id, pharmacist_id, drug_name, price, dosage)

        elif page == "Download Prescription Data":
            st.subheader("Download Prescription Data")
            patient_id = st.text_input("Enter Patient ID for Prescription Data")
            if st.button("Download"):
                download_prescription_data(patient_id)

        if st.button("Log Out"):
            st.session_state.show_logout_confirmation = True
            st.experimental_rerun()

        if st.session_state.show_logout_confirmation:
            st.warning("Are you sure you want to log out?")
            if st.button("Yes, log me out"):
                st.session_state.pharmacist_logged_in = False
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()
            if st.button("No, keep me logged in"):
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()

    else:
        st.subheader("Pharmacist Log In")
        with st.form("pharmacist_log_in_form"):
            pharmacist_id = st.text_input("Pharmacist ID")
            last_name = st.text_input("Last Name")
            submit = st.form_submit_button("Log In")

            if submit:
                if verify_pharmacist(pharmacist_id, last_name):
                    st.session_state.pharmacist_logged_in = True
                    st.session_state.pharmacist_id = pharmacist_id
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid Pharmacist ID or Last Name.")

show_pharmacy_page()
