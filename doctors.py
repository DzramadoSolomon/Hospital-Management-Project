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
            existing_doctor_report = patient_data[11]
            existing_drug_recommendation = patient_data[12]
            
            # Display existing data if present
            if existing_doctor_report or existing_drug_recommendation:
                st.info("Patient already has a doctor report or drug recommendation.")
                st.write(f"Existing Doctor Report: {existing_doctor_report}")
                st.write(f"Existing Drug Recommendation: {existing_drug_recommendation}")
                
                # Ask for confirmation to rewrite
                rewrite_confirmation = st.radio("Do you want to rewrite?", ["Yes", "No"], index=1)

                # Process based on confirmation
                if rewrite_confirmation == "Yes":
                    # Proceed to update only if new values are provided
                    if doctor_report.strip() != "" or drug_recommendation.strip() != "":
                        cur.execute("""
                            UPDATE patients
                            SET doctor_id = %s, doctor_report = %s, drug_recommendation = %s
                            WHERE patient_id = %s;
                        """, (doctor_id, doctor_report, drug_recommendation, patient_id))
                        conn.commit()
                        st.success("Patient record updated successfully.")  
                        
                    else:
                        st.warning("Doctor's Report or Drug Recommendation cannot be empty. Please provide valid input.")
                elif rewrite_confirmation == "No":
                    st.success("Original doctor report maintained.")
                    
            
            else:
                # No existing data, proceed to update
                if doctor_report.strip() != "" or drug_recommendation.strip() != "":
                    cur.execute("""
                        UPDATE patients
                        SET doctor_id = %s, doctor_report = %s, drug_recommendation = %s
                        WHERE patient_id = %s;
                    """, (doctor_id, doctor_report, drug_recommendation, patient_id))
                    conn.commit()
                    st.success("Patient record updated successfully.")
                    
                    
                else:
                    st.warning("Doctor's Report or Drug Recommendation cannot be empty. Please provide valid input.")
                    
        else:
            st.error("Patient ID not found.")
    except Exception as e:
        st.error(f"Error updating patient record: {e}")
    finally:
        cur.close()
        conn.close()


# Show the doctor's page
def show_doctors_page():
    st.title("Doctors")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "show_update_confirmation" not in st.session_state:
        st.session_state.show_update_confirmation = False

    if st.session_state.logged_in:
        page = st.radio("Select Action", ["View Patients Data", "Update Patient Record"])
        
        if page == "View Patients Data":
            st.subheader("Patients List")
            conn = connect_to_db()
            if conn is not None:
                cur = conn.cursor()
                try:
                    cur.execute("SELECT first_name, last_name, doctor_report, drug_recommendation FROM patients;")
                    patients_data = cur.fetchall()
                    if patients_data:
                        patients_df = pd.DataFrame(patients_data, columns=["First Name", "Last Name", "Doctor Report", "Drug Recommendation"])
                        patients_df.insert(0, "Number of Patients", range(1, len(patients_df) + 1))
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
                    
                    # Check if patient ID is provided
                    if patient_id.strip() == "":
                        st.warning("Please enter a Patient ID.")
                    else:
                        # Check if doctor report or drug recommendation is provided
                        if doctor_report.strip() == "" and drug_recommendation.strip() == "":
                            st.warning("Doctor's Report or Drug Recommendation cannot be empty. Please provide valid input.")
                        else:
                            # Update patient record
                            update_patient_record(doctor_id, patient_id, doctor_report, drug_recommendation)

        if st.button("Log Out"):
            st.session_state.show_logout_confirmation = True
            st.experimental_rerun()

        if st.session_state.show_logout_confirmation:
            st.warning("Are you sure you want to log out?")
            if st.button("Yes, log me out"):
                st.session_state.logged_in = False
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()
            if st.button("No, keep me logged in"):
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()

    else:
        auth_mode = st.radio("Choose an option", ["Log In"])
        
        if auth_mode == "Log In":
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
