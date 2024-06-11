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

# Function to create a new doctor
def create_doctor(first_name, middle_name, last_name, specialisation):
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
        st.error(f"Error creating doctor: {e}")
    finally:
        cur.close()
        conn.close()

# Function to verify doctor credentials
def verify_doctor(doctor_id, last_name):
    conn = connect_to_db()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM doctors WHERE doctor_id = %s AND last_name = %s;", (doctor_id, last_name))
        doctor_data = cur.fetchone()
        return doctor_data
    except Exception as e:
        st.error(f"Error verifying doctor: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Function to update patient record
def update_patient_record(doctor_id, patient_id, doctor_report, drug_recommendation):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        # Check if patient record exists
        cur.execute("SELECT * FROM patients WHERE patient_id = %s;", (patient_id,))
        patient_data = cur.fetchone()
        if patient_data:
            existing_doctor_report = patient_data[4]
            existing_drug_recommendation = patient_data[5]
            
            # Check if doctor report and drug recommendation are already filled
            if existing_doctor_report and existing_drug_recommendation:
                st.info("Doctor report and drug recommendation for this patient are already filled. "
                        "Please create a new diagnosis.")
                st.write(f"Existing Doctor Report: {existing_doctor_report}")
                st.write(f"Existing Drug Recommendation: {existing_drug_recommendation}")
                return

            # Update patient record
            cur.execute("""
                UPDATE patients
                SET doctor_id = %s, doctor_report = %s, drug_recommendation = %s
                WHERE patient_id = %s;
            """, (doctor_id, doctor_report, drug_recommendation, patient_id))
            conn.commit()
            st.info("Patient record updated successfully.")
        else:
            st.error("Patient ID not found.")
    except Exception as e:
        st.error(f"Error updating patient record: {e}")
    finally:
        cur.close()
        conn.close()


#To display a page of all the patients
def show_patients_page():
    st.title("Patients")

    # Show a list of patients with their basic details
    st.subheader("Patients List")
    conn = connect_to_db()
    if conn is not None:
        cur = conn.cursor()
        try:
            cur.execute("SELECT first_name, last_name, doctor_report, drug_recommendation FROM patients;")
            patients_data = cur.fetchall()
            if patients_data:
                # Display patients data as a table
                patients_df = pd.DataFrame(patients_data, columns=["First Name", "Last Name", "Doctor Report", "Drug Recommendation"])
                st.dataframe(patients_df)
            else:
                st.info("No patients found.")
        except Exception as e:
            st.error(f"Error fetching patients data: {e}")
        finally:
            cur.close()
            conn.close()

    # Allow doctor to edit patient record by entering patient ID
    st.subheader("Edit Patient Record")
    with st.form("edit_patient_form"):
        patient_id = st.text_input("Enter Patient ID to edit")
        if patient_id:
            # Fetch patient data if ID is provided
            patient_data = get_patient_data(patient_id)
            if patient_data:
                st.write(f"First Name: {patient_data[1]}")
                st.write(f"Last Name: {patient_data[2]}")
                st.write(f"Doctor Report: {patient_data[4]}")
                st.write(f"Drug Recommendation: {patient_data[5]}")
                
                # Display form to edit patient record
                doctor_report = st.text_area("Update Doctor's Report")
                drug_recommendation = st.text_area("Update Drug Recommendation")
                update_submit = st.form_submit_button("Update Patient Record")
                
                if update_submit:
                    # Call function to update patient record
                    update_patient_record(patient_id, doctor_report, drug_recommendation)
            else:
                st.error("Patient ID not found.")


# Show the doctor's page
# Show the doctor's page
def show_doctors_page():
    st.title("Doctors")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        page = st.radio("Select Action", ["View Patients Data", "Update Patient Record"])
        
        if page == "View Patients Data":
            st.subheader("Patients List")
            # Display list of patients with their basic details
            # Display list of patients with their basic details
            conn = connect_to_db()
            if conn is not None:
                cur = conn.cursor()
                try:
                    cur.execute("SELECT first_name, last_name, doctor_report, drug_recommendation FROM patients;")
                    patients_data = cur.fetchall()
                    if patients_data:
                        # Convert the data to a DataFrame
                        patients_df = pd.DataFrame(patients_data, columns=["First Name", "Last Name", "Doctor Report", "Drug Recommendation"])
                        
                        # Add a new column for the index starting from 1
                        patients_df.insert(0, "Number of Patients", range(1, len(patients_df) + 1))
                        
                        # Display patients data as a table
                        st.dataframe(patients_df)
                    else:
                        st.info("No patients found.")
                except Exception as e:
                    st.error(f"Error fetching patients data: {e}")
                finally:
                    cur.close()
                    conn.close()


        elif page == "Update Patient Record":
            st.subheader("Update Patient Record")
            with st.form("update_patient_form"):
                patient_id = st.text_input("Enter Patient ID")
                doctor_report = st.text_area("Doctor's Report")
                drug_recommendation = st.text_area("Drug Recommendation")
                update_submit = st.form_submit_button("Update Patient Record")
                
                if update_submit:
                    doctor_id = st.session_state.doctor_id
                    update_patient_record(doctor_id, patient_id, doctor_report, drug_recommendation)
        
        if st.button("Log Out"):
            st.session_state.logged_in = False
    else:
        auth_mode = st.radio("Choose an option", ["Sign Up", "Log In"])
        
        if auth_mode == "Sign Up":
            st.subheader("Doctor Sign Up")
            with st.form("doctor_sign_up_form"):
                first_name = st.text_input("First Name")
                middle_name = st.text_input("Middle Name (Optional)", "")
                last_name = st.text_input("Last Name")
                specialisation = st.text_input("Specialisation")
                submit = st.form_submit_button("Sign Up")
                
                if submit:
                    create_doctor(first_name, middle_name, last_name, specialisation)
        
        elif auth_mode == "Log In":
            st.subheader("Doctor Log In")
            with st.form("doctor_log_in_form"):
                doctor_id = st.text_input("Doctor ID")
                last_name = st.text_input("Last Name")
                submit = st.form_submit_button("Log In")
                
                if submit:
                    doctor_data = verify_doctor(doctor_id, last_name)
                    if doctor_data:
                        st.session_state.logged_in = True
                        st.session_state.doctor_id = doctor_id
                        st.success(f"Welcome Dr. {doctor_data[1]} {doctor_data[3]}!")
                    else:
                        st.error("Invalid Doctor ID or Last Name.")

show_doctors_page()
