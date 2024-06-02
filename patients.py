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


# Function to add new patient
def add_patient(first_name, last_name, bp_reading):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO patients (first_name, last_name, bp_reading, doctor_report, drug_recommendation)
            VALUES (%s, %s, %s, '', '')
            RETURNING patient_id;
        """, (first_name, last_name, bp_reading))
        patient_id = cur.fetchone()[0]
        conn.commit()
        st.success(f"Patient added successfully! Your patient ID is {patient_id}. Please keep it safe.")
    except Exception as e:
        st.error(f"Error adding patient: {e}")
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
        cur.execute("SELECT * FROM patients WHERE patient_id = %s;", (patient_id,))
        patient_data = cur.fetchone()
        return patient_data
    except Exception as e:
        st.error(f"Error retrieving patient data: {e}")
        return None
    finally:
        cur.close()
        conn.close()
        
# Function to generate CSV file and download patient data
def download_patient_data(patient_data):
    first_name = patient_data[1]
    last_name = patient_data[2]
    patient_df = pd.DataFrame([patient_data], columns=["Patient ID", "First Name", "Last Name", "BP Reading", "Doctor Report", "Drug Recommendation"])
    csv = patient_df.to_csv(index=False)
    return csv, f"{first_name}_{last_name}_data.csv"

def show_patients_page():
    st.title("Patients")
    st.subheader("New Patient")
    with st.form("new_patient_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        bp_reading = st.text_input("BP Reading")
        submit = st.form_submit_button("Submit")

        if submit:
            add_patient(first_name, last_name, bp_reading)

    st.subheader("Existing Patient")
    existing_patient_id = st.text_input("Enter your Patient ID")
    if existing_patient_id:
        patient_data = get_patient_data(existing_patient_id)
        if patient_data:
            st.write(f"First Name: {patient_data[1]}")
            st.write(f"Last Name: {patient_data[2]}")
            st.write(f"BP Reading: {patient_data[3]}")
            st.write(f"Doctor Report: {patient_data[4]}")
            st.write(f"Drug Recommendation: {patient_data[5]}")
            
            # Download patient data as CSV
            csv, file_name = download_patient_data(patient_data)
            st.download_button(label="Download Patient Data", data=csv, file_name=file_name, mime='text/csv')
        else:
            st.error("Patient ID not found.")


