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

# Function to verify administrator credentials
def verify_admin(username, password):
    return username == "admin" and password == "123"

# Function to create a new user (doctor, nurse, pharmacist)
def create_user(user_type, first_name, middle_name, last_name, specialisation=None):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        if user_type == "Doctor":
            cur.execute("""
                INSERT INTO doctors (first_name, middle_name, last_name, specialisation)
                VALUES (%s, %s, %s, %s)
                RETURNING doctor_id;
            """, (first_name, middle_name, last_name, specialisation))
        elif user_type == "Nurse":
            cur.execute("""
                INSERT INTO nurses (first_name, middle_name, last_name)
                VALUES (%s, %s, %s)
                RETURNING nurse_id;
            """, (first_name, middle_name, last_name))
        elif user_type == "Pharmacist":
            cur.execute("""
                INSERT INTO pharmacists (first_name, middle_name, last_name)
                VALUES (%s, %s, %s)
                RETURNING pharmacist_id;
            """, (first_name, middle_name, last_name))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        st.success(f"{user_type} added successfully! Your {user_type} ID is {user_id}. Please keep it safe.")
    except Exception as e:
        st.error(f"Error creating {user_type}: {e}")
    finally:
        cur.close()
        conn.close()

# Function to update user record
def update_user_record(user_type, user_id, first_name, middle_name, last_name, specialisation=None):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        if user_type == "Doctor":
            cur.execute("""
                UPDATE doctors
                SET first_name = %s, middle_name = %s, last_name = %s, specialisation = %s
                WHERE doctor_id = %s;
            """, (first_name, middle_name, last_name, specialisation, user_id))
        elif user_type == "Nurse":
            cur.execute("""
                UPDATE nurses
                SET first_name = %s, middle_name = %s, last_name = %s
                WHERE nurse_id = %s;
            """, (first_name, middle_name, last_name, user_id))
        elif user_type == "Pharmacist":
            cur.execute("""
                UPDATE pharmacists
                SET first_name = %s, middle_name = %s, last_name = %s
                WHERE pharmacist_id = %s;
            """, (first_name, middle_name, last_name, user_id))
        
        conn.commit()
        st.success(f"{user_type} record updated successfully.")
    except Exception as e:
        st.error(f"Error updating {user_type} record: {e}")
    finally:
        cur.close()
        conn.close()

# Function to delete user record
def delete_user_record(user_type, user_id):
    conn = connect_to_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        if user_type == "Doctor":
            cur.execute("DELETE FROM doctors WHERE doctor_id = %s;", (user_id,))
        elif user_type == "Nurse":
            cur.execute("DELETE FROM nurses WHERE nurse_id = %s;", (user_id,))
        elif user_type == "Pharmacist":
            cur.execute("DELETE FROM pharmacists WHERE pharmacist_id = %s;", (user_id,))
        
        if cur.rowcount == 0:
            return False
        else:
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error deleting {user_type} record: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# Function to view data (doctors, nurses, pharmacists)
def view_user_data(user_type):
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        if user_type == "Doctor":
            cur.execute("SELECT doctor_id, first_name, middle_name, last_name, specialisation FROM doctors ORDER BY doctor_id DESC;")
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=["Doctor ID", "First Name", "Middle Name", "Last Name", "Specialisation"])
        elif user_type == "Nurse":
            cur.execute("SELECT nurse_id, first_name, middle_name, last_name FROM nurses ORDER BY nurse_id DESC;")
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=["Nurse ID", "First Name", "Middle Name", "Last Name"])
        elif user_type == "Pharmacist":
            cur.execute("SELECT pharmacist_id, first_name, middle_name, last_name FROM pharmacists ORDER BY pharmacist_id DESC;")
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=["Pharmacist ID", "First Name", "Middle Name", "Last Name"])
        
        if data:
            st.dataframe(df)
        else:
            st.info("No data recorded yet!")
        
    except Exception as e:
        st.error(f"Error fetching {user_type} data: {e}")
    finally:
        cur.close()
        conn.close()

# Show the administrator page
def show_administrator_page():
    st.title("Administrator")

    # Login section
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Log In")

        if login_button:
            if verify_admin(username, password):
                st.success("Logged in successfully!")
                st.session_state.admin_logged_in = True
            else:
                st.error("Invalid username or password.")
    else:
        # Main action selection
        action = st.sidebar.radio("Select Action", ["View User Data", "Access Database", "Delete User Record"])

        if action == "View User Data":
            st.subheader("View User Data")
            user_type = st.selectbox("User Type", ["Doctor", "Nurse", "Pharmacist"])
            if st.button("View Data"):
                view_user_data(user_type)
        
        elif action == "Access Database":
            st.subheader("Access Database")
            access_option = st.radio("Select Option", ["Sign Up", "Update User Record"])

            if access_option == "Sign Up":
                user_type = st.selectbox("User Type", ["Doctor", "Nurse", "Pharmacist"])
                first_name = st.text_input("First Name")
                middle_name = st.text_input("Middle Name (Optional)", "")
                last_name = st.text_input("Last Name")
                specialisation = st.text_input("Specialisation") if user_type == "Doctor" else None
                
                if st.button("Sign Up"):
                    create_user(user_type, first_name, middle_name, last_name, specialisation)
            
            elif access_option == "Update User Record":
                user_type = st.selectbox("User Type", ["Doctor", "Nurse", "Pharmacist"])
                user_id = st.text_input(f"{user_type} ID")
                first_name = st.text_input("First Name")
                middle_name = st.text_input("Middle Name (Optional)", "")
                last_name = st.text_input("Last Name")
                specialisation = st.text_input("Specialisation") if user_type == "Doctor" else None
                
                if st.button("Update"):
                    update_user_record(user_type, user_id, first_name, middle_name, last_name, specialisation)
        
        elif action == "Delete User Record":
            st.subheader("Delete User Record")
            user_type = st.selectbox("User Type", ["Doctor", "Nurse", "Pharmacist"])
            user_id = st.text_input(f"Enter {user_type} ID to delete")
            if st.button("Delete"):
                if delete_user_record(user_type, user_id):
                    st.success(f"{user_type} record deleted successfully.")
                else:
                    st.error("This ID is not valid, make sure your ID is valid to proceed with the deletion.")
        
        if st.button("Log Out"):
            st.session_state.show_logout_confirmation = True
            st.experimental_rerun()

        if st.session_state.get("show_logout_confirmation", False):
            st.warning("Are you sure you want to log out?")
            if st.button("Yes, log me out"):
                st.session_state.admin_logged_in = False
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()
            if st.button("No, stay logged in"):
                st.session_state.show_logout_confirmation = False
                st.experimental_rerun()

