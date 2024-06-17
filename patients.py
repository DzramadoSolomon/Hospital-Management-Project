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

# Function to verify nurse credentials
def verify_nurse(nurse_id, last_name):
    conn = connect_to_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM nurses WHERE nurse_id = %s AND last_name = %s;", (nurse_id, last_name))
        nurse = cur.fetchone()
        return nurse is not None
    except Exception as e:
        st.error(f"Error verifying nurse credentials: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# Function to add new patient
def add_patient(first_name, middle_name, last_name, gender, age, body_temp, pulse_rate, resp_rate, bp_reading):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO patients (first_name, middle_name, last_name, gender, age, body_temp, pulse_rate, resp_rate, bp_reading, doctor_report, drug_recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '', '')
            RETURNING patient_id;
        """, (first_name, middle_name, last_name, gender, age, body_temp, pulse_rate, resp_rate, bp_reading))
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
    patient_df = pd.DataFrame([patient_data], columns=["Patient ID", "First Name", "Middle Name", "Last Name", "Gender", "Age", "Body Temperature", "Pulse Rate", "Respiration Rate", "BP Reading", "Doctor Report", "Drug Recommendation", "Doctor ID"])
    patient_df = patient_df.drop(columns=["Doctor ID"])  # Remove Doctor ID column
    csv = patient_df.to_csv(index=False)
    first_name = patient_data[1]
    last_name = patient_data[3]
    return csv, f"{first_name}_{last_name}_data.csv"

# Show the patients page
def show_patients_page():
    st.title("Patients")

    if "nurse_logged_in" not in st.session_state:
        st.session_state.nurse_logged_in = False

    if "show_logout_confirmation" not in st.session_state:
        st.session_state.show_logout_confirmation = False

    if not st.session_state.nurse_logged_in:
        st.subheader("Nurse Login")
        nurse_id = st.text_input("Nurse ID")
        last_name = st.text_input("Last Name")
        login_button = st.button("Log In")

        if login_button:
            if verify_nurse(nurse_id, last_name):
                st.success("Logged in successfully!")
                st.session_state.nurse_logged_in = True
                
            else:
                st.error("Invalid Nurse ID or Last Name.")
    else:
        st.subheader("New Patient")
        if "patient_info" not in st.session_state:
            st.session_state.patient_info = {}
            st.session_state.step = "personal_info"
        
        if st.session_state.step == "personal_info":
            st.header("Personal Info")
            st.session_state.patient_info["first_name"] = st.text_input("First Name")
            st.session_state.patient_info["middle_name"] = st.text_input("Middle Name (Optional)", "")
            st.session_state.patient_info["last_name"] = st.text_input("Last Name")
            st.session_state.patient_info["gender"] = st.selectbox("Gender", ["Male", "Female", "Other"])
            st.session_state.patient_info["age"] = st.number_input("Age", min_value=0)
            if st.button("Next"):
                st.session_state.step = "vitals"
                st.experimental_rerun()
        
        elif st.session_state.step == "vitals":
            st.header("Vitals")
            st.session_state.patient_info["body_temp"] = st.number_input("Body Temperature (°C)", min_value=0.0)
            st.session_state.patient_info["pulse_rate"] = st.number_input("Pulse Rate (beats per minute)", min_value=0)
            st.session_state.patient_info["resp_rate"] = st.number_input("Respiration Rate (breaths per minute)", min_value=0)
            st.session_state.patient_info["bp_reading"] = st.text_input("BP Reading")
            if st.button("Submit"):
                add_patient(
                    st.session_state.patient_info["first_name"],
                    st.session_state.patient_info["middle_name"],
                    st.session_state.patient_info["last_name"],
                    st.session_state.patient_info["gender"],
                    st.session_state.patient_info["age"],
                    st.session_state.patient_info["body_temp"],
                    st.session_state.patient_info["pulse_rate"],
                    st.session_state.patient_info["resp_rate"],
                    st.session_state.patient_info["bp_reading"]
                )
                st.session_state.step = "personal_info"
                st.session_state.patient_info = {}
                

        st.subheader("Existing Patient")
        existing_patient_id = st.text_input("Enter your Patient ID")
        if existing_patient_id:
            patient_data = get_patient_data(existing_patient_id)
            if patient_data:
                st.header("Personal Info")
                st.write(f"First Name: {patient_data[1]}")
                st.write(f"Middle Name: {patient_data[2]}")
                st.write(f"Last Name: {patient_data[3]}")
                st.write(f"Gender: {patient_data[4]}")
                st.write(f"Age: {patient_data[5]}")
                
                st.header("Vitals")
                st.write(f"Body Temperature: {patient_data[6]}")
                st.write(f"Pulse Rate: {patient_data[7]}")
                st.write(f"Respiration Rate: {patient_data[8]}")
                st.write(f"BP Reading: {patient_data[9]}")
                st.write(f"Doctor Report: {patient_data[10]}")
                st.write(f"Drug Recommendation: {patient_data[11]}")
  
                # Download patient data as CSV
                csv, file_name = download_patient_data(patient_data)
                st.download_button(label="Download Patient Data", data=csv, file_name=file_name, mime='text/csv')
            else:
                st.error("Patient ID not found.")
        
        if st.button("Log Out"):
            st.session_state.show_logout_confirmation = True
            st.experimental_rerun()

        if st.session_state.show_logout_confirmation:
            st.warning("Are you sure you want to log out?")
            if st.button("Yes, log me out"):
                st.session_state.nurse_logged_in = False
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()
            if st.button("No, keep me logged in"):
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()

show_patients_page()