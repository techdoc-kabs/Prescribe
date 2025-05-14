
import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
import plotly.express as px
import datetime
import sqlite3

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row
        return db
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

def generate_appointment_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM consult_appointments")
    next_id = cursor.fetchone()[0]
    # current_date = datetime.now().strftime("%Y-%m-%d")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")


    return f"CONSULT-{current_date}-{next_id:04}"

def create_consult_appointments_table(db):
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consult_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id TEXT UNIQUE,
            student_id TEXT,
            name TEXT,
            username TEXT,
            appointment_type TEXT DEFAULT 'NEW',
            appointment_date DATE,
            appointment_time TIME,
            term TEXT,
            clinician_name TEXT,
            reason TEXT,
            FOREIGN KEY (student_id) REFERENCES student_users(student_id)
        )
    """)
    db.commit()

def determine_appointment_type(db, student_id):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM consult_appointments WHERE student_id = ?", (student_id,))
    return "NEW" if cursor.fetchone()[0] == 0 else "REVISIT"

def fetch_students(db, search_input):
    cursor = db.cursor()
    search_input = search_input.strip()
    
    if search_input.upper().startswith("STUD-") or search_input.isdigit():
        cursor.execute("""
            SELECT student_id, name, age, gender, student_class, stream, username, email, contact
            FROM student_users WHERE student_id = ?
        """, (search_input,))
    else:
        cursor.execute("""
            SELECT student_id, name, age, gender, student_class, stream, username, email, contact
            FROM student_users WHERE name LIKE ?
        """, (f"%{search_input}%",))
    
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def is_duplicate_appointment(db, student_id, appointment_date, appointment_time):
    cursor = db.cursor()
    # cursor.execute("""
    #     SELECT COUNT(*) FROM consult_appointments 
    #     WHERE student_id = ? AND appointment_date = ? AND appointment_time = ?
    # """, (student_id, appointment_date, appointment_time))
    
    
    cursor.execute("""
    SELECT COUNT(*) FROM consult_appointments 
    WHERE student_id = ? AND appointment_date = ? AND appointment_time = ?
""", (
    student_id,
    appointment_date.strftime("%Y-%m-%d"),
    appointment_time.strftime("%H:%M:%S")
))

    return cursor.fetchone()[0] > 0





def insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason, term):
    cursor = db.cursor()
    if is_duplicate_appointment(db, student_id, appointment_date, appointment_time):
        st.warning("An appointment already exists for this student at the selected date and time.")
        return

    cursor.execute("SELECT name, username FROM student_users WHERE student_id = ?", (student_id,))
    user_data = cursor.fetchone()
    if not user_data:
        st.warning("Student not found.")
        return
    
    name, username = user_data
    appointment_id = generate_appointment_id(db)
    
    
    cursor.execute("""
    INSERT INTO consult_appointments (appointment_id, student_id, name, username, appointment_type, term, 
                                      appointment_date, appointment_time, clinician_name, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    appointment_id,
    student_id,
    name,
    username,
    appointment_type,
    term,
    appointment_date.strftime("%Y-%m-%d"),
    appointment_time.strftime("%H:%M:%S"),
    clinician_name,
    reason
))
    db.commit()
    st.success(f"{name}'s appointment for {reason} with {clinician_name} scheduled successfully.")





#### DRIVER CODE #######
def main():
    db = create_connection()
    create_consult_appointments_table(db)

    st.sidebar.markdown(
        """
        <style>
            .appointment-header {
                font-family: Haettenschweiler, sans-serif;
                text-align: center;
                color: #FFFFFF;
                background-color: #007BFF;
                padding: 5px;
                border-radius: 5px;
                font-size: 25px;
            }
        </style>
        <div class='appointment-header'>STUDENT RECORD </div>
        """, unsafe_allow_html=True
    )

    consult_menu = option_menu(
        menu_title='',
        orientation='horizontal',
        menu_icon='',
        options=['CONSULT_APPOINTENT', 'CONSULT_STATUS', 'VISIO'],
        icons=['calendar-plus', 'hourglass-split', 'bar-chart'],
        styles={
            "container": {"padding": "8!important", "background-color": 'black', 'border': '0.01px dotted red'},
            "icon": {"color": "red", "font-size": "11px"},
            "nav-link": {"color": "#d7c4c1", "font-size": "11px", "font-weight": 'bold', "text-align": "left",
                         "margin": "0px", "--hover-color": "red"},
            "nav-link-selected": {"background-color": "green"},
        },
        key="consult_menu"
    )

    if consult_menu == 'CONSULT_APPOINTENT':
        with st.sidebar.expander('CONSULT SCHEDULE', expanded=True):
            st.write("🔍 SEARCH")
            search_input = st.text_input("Enter Name or Student ID", "")
        
        results = fetch_students(db, search_input) if search_input.strip() else []
        selected_record = None
        if results:
            with st.sidebar.expander('', expanded=True):
                st.write(f"**{len(results)} result(s) found**")
                options = {f"{r['name']} - {r['student_id']}": r for r in results}
                selected_option = st.selectbox("Select a record:", list(options.keys()))
            selected_record = options[selected_option]

        if selected_record:
            with st.sidebar.expander("📄 STUDENT DETAILS", expanded=True):
                for key, value in selected_record.items():
                    st.write(f"{key.replace('_', ' ').title()}: {value}")
            st.session_state.update(selected_record)
            student_id = selected_record['student_id']
            student_name = selected_record['name']
            with st.form("Schedule Appointment"):
                appointment_type = determine_appointment_type(db, student_id)
                st.write(f"APPOINTMENT TYPE: {appointment_type}")

                col1, col2 = st.columns(2)
                appointment_date = col1.date_input("APPOINTMENT DATE:", key="appointment_date")
                appointment_time = col1.time_input("APPOINTMENT TIME", key="appointment_time")
                clinician_name = col2.selectbox("CLINICIAN:", ['Dr. Smith', 'Dr. John'])  # Example list
                reason = col2.selectbox("REASON FOR APPOINTMENT:", ['Check-up', 'Follow-up', 'Urgent'])  # Example list
                term = col1.selectbox('TERM', ['', '1st-Term', '2nd-Term', '3rd-Term'])

                submit = col1.form_submit_button("Schedule Appointment")
                if submit:
                    if not all([appointment_date, appointment_time, clinician_name, reason, term]):
                        st.warning("Please fill in all the fields before submitting.")
                    else:
                        insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, term, clinician_name, reason)

    db.close()
if __name__ == "__main__":
    main()