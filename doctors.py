import streamlit as st
import psycopg2

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

# Function to add new doctor
def add_doctor(first_name, middle_name, last_name, specialisation):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO doctors (first_name, middle_name, last_name, specialisation)
            VALUES (%s, %s, %s, %s)
            RETURNING doctor_id;
        """, (first_name, middle_name, last_name, specialisation))
        doctor_id = cur.fetchone()[0]
        conn.commit()
        st.success(f"Doctor added successfully! Your doctor ID is {doctor_id}. Please keep it safe.")
    except Exception as e:
        st.error(f"Error adding doctor: {e}")
    finally:
        cur.close()
        conn.close()

# Function to verify doctor credentials
def verify_doctor(doctor_id, last_name):
    conn = connect_to_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM doctors WHERE doctor_id = %s AND last_name = %s;", (doctor_id, last_name))
        doctor_data = cur.fetchone()
        return doctor_data is not None
    except Exception as e:
        st.error(f"Error verifying doctor: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# Function to get patient data
def get_patient_data(patient_id):
    conn = connect_to_db()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT doctor_report, drug_recommendation FROM patients WHERE patient_id = %s;", (patient_id,))
        patient_data = cur.fetchone()
        return patient_data
    except Exception as e:
        st.error(f"Error retrieving patient data: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Function to update patient report and drug recommendation
def update_patient_record(patient_id, doctor_report, drug_recommendation):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE patients
            SET doctor_report = %s, drug_recommendation = %s
            WHERE patient_id = %s;
        """, (doctor_report, drug_recommendation, patient_id))
        conn.commit()
        st.success("Patient record updated successfully!")
    except Exception as e:
        st.error(f"Error updating patient record: {e}")
    finally:
        cur.close()
        conn.close()

def show_doctors_page():
    st.title("Doctors")

    option = st.radio("Select an option", ["Sign Up", "Log In"])

    if option == "Sign Up":
        with st.form("sign_up_form"):
            first_name = st.text_input("First Name")
            middle_name = st.text_input("Middle Name (Optional)")
            last_name = st.text_input("Last Name")
            specialisation = st.text_input("Specialisation")
            submit = st.form_submit_button("Sign Up")

            if submit:
                add_doctor(first_name, middle_name, last_name, specialisation)

    elif option == "Log In":
        with st.form("log_in_form"):
            doctor_id = st.text_input("Doctor ID")
            last_name = st.text_input("Last Name")
            submit = st.form_submit_button("Log In")

            if submit:
                if verify_doctor(doctor_id, last_name):
                    st.success("Logged in successfully!")
                    st.session_state.doctor_logged_in = True
                    st.session_state.doctor_id = doctor_id
                else:
                    st.error("Invalid Doctor ID or Last Name")

        if st.session_state.get("doctor_logged_in"):
            st.subheader("Update Patient Record")
            with st.form("update_patient_form"):
                patient_id = st.text_input("Enter Patient ID")
                patient_submit = st.form_submit_button("Fetch Patient Data")
                
                if patient_submit and patient_id:
                    patient_data = get_patient_data(patient_id)
                    if patient_data:
                        current_doctor_report, current_drug_recommendation = patient_data
                        if current_doctor_report or current_drug_recommendation:
                            st.warning("This patient already has an existing report or drug recommendation.")
                            st.table({
                                "Current Doctor Report": [current_doctor_report],
                                "Current Drug Recommendation": [current_drug_recommendation]
                            })
                                
                            confirm = st.radio("Do you want to update it?", ["No", "Yes"])
                            
                            if confirm == "Yes":
                                doctor_report = st.text_area("Doctor Report", current_doctor_report)
                                drug_recommendation = st.text_area("Drug Recommendation", current_drug_recommendation)
                                update_submit = st.form_submit_button("Update Patient Record")
                                
                                if update_submit:
                                    update_patient_record(patient_id, doctor_report, drug_recommendation)
                        else:
                            doctor_report = st.text_area("Doctor Report")
                            drug_recommendation = st.text_area("Drug Recommendation")
                            update_submit = st.form_submit_button("Update Patient Record")
                            
                            if update_submit:
                                update_patient_record(patient_id, doctor_report, drug_recommendation)
                    else:
                        st.error("Patient ID not found.")
