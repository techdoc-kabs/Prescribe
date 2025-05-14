import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import consultations

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables access by column name
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd

def create_follow_up_table(db):
    cursor = db.cursor()
    create_follow_up_table_query = """
    CREATE TABLE IF NOT EXISTS follow_up (
        follow_up_id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,
        appointment_id TEXT NOT NULL,
        appointment_type TEXT NOT NULL,
        student_name TEXT NOT NULL,
        follow_up_count INTEGER NOT NULL,
        appoint_status TEXT,
        next_clinician TEXT,
        next_appoint DATE,
        referral_status TEXT,
        referral_notes TEXT,
        FOREIGN KEY (appointment_id) REFERENCES screen_appointments(appointment_id)
    );
    """
    cursor.execute(create_follow_up_table_query)
    db.commit()

def generate_follow_up_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM follow_up")
    result = cursor.fetchone()
    count = result[0] if result[0] is not None else 0
    current_year = datetime.now().year
    new_id = f"FOL-{current_year}-{count + 1:02}"
    return new_id

def count_previous_appointments(db, student_id):
    cursor = db.cursor()
    count_query = """
        SELECT COALESCE(MAX(follow_up_count), 0)
        FROM follow_up
        WHERE student_id = ?
    """
    cursor.execute(count_query, (student_id,))
    count = cursor.fetchone()[0]
    return count

def insert_follow_up_record(db, appointment_id, appointment_type, follow_up_count, referral_status, referral_notes, next_clinician, next_appoint, follow_up_reason, appoint_status):
    cursor = db.cursor()
    cursor.execute("SELECT student_id, name FROM screen_appointments WHERE appointment_id = ?", (appointment_id,))
    appointment_details = cursor.fetchone()
    if not appointment_details:
        st.error("Appointment not found!")
        return
    student_id, name = appointment_details
    follow_up_id = generate_follow_up_id(db)
    follow_up_data = (
        follow_up_id,
        student_id,
        appointment_id,
        appointment_type,
        name,
        follow_up_count,
        appoint_status,
        next_clinician,
        next_appoint,
        ', '.join(follow_up_reason) if follow_up_reason else None,
        referral_status,
        referral_notes
    )

    insert_follow_up_query = """
    INSERT INTO follow_up (
        follow_up_id, 
        student_id, 
        appointment_id,
        appointment_type, 
        student_name, 
        follow_up_count, 
        appoint_status, 
        next_clinician, 
        next_appoint, 
        follow_up_reason, 
        referral_status, 
        referral_notes
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.execute(insert_follow_up_query, follow_up_data)
        db.commit()
        st.success("Follow-up record created!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        db.rollback()

def fetch_appointment_by_id(db, appointment_id):
    cursor = db.cursor()
    select_appointment_query = """
       SELECT appointment_id, student_id, name, appointment_type, appointment_date, appointment_time, clinician_name, reason
       FROM screen_appointments
       WHERE appointment_id = ?
       """
    cursor.execute(select_appointment_query, (appointment_id,))
    appointment = cursor.fetchone()
    return appointment

def get_student_appointment_list(db):
    cursor = db.cursor()
    cursor.execute("SELECT appointment_id, appointment_type, student_id, name, appointment_date, appointment_time, clinician_name, reason FROM screen_appointments")
    students = cursor.fetchall()
    select_list = [""] 
    select_list += [f"{student[0]} - {student[1]} - {student[2]} {student[2]}, {student[3]}, {student[4]}, {student[5]},{student[6]}" for student in students]
    return select_list

def get_all_appointments(db):
    cursor = db.cursor()
    select_query = """
    SELECT appointment_id, student_id, name, appointment_date, appointment_time, clinician_name, reason
    FROM screen_appointments
    """
    cursor.execute(select_query)
    records = cursor.fetchall()
    if records:
        df = pd.DataFrame(records, columns=['Appointment ID', 'Student ID', 'Student Name', 'Appointment Date', 'Appointment Time', 'Clinician Name', 'Reason'])
        return df   
    else:
        st.warning("No appointments found")

def fetch_all_follow_ups(db):
    cursor = db.cursor()
    query = """
    SELECT 
        follow_up_id,
        student_id,
        appointment_id,
        appointment_type,
        student_name,
        follow_up_count,
        appoint_status,
        next_clinician,
        next_appoint,
        follow_up_reason,
        referral_status,
        referral_notes
    FROM follow_up
    """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if records:
            columns = [
                "Follow-Up ID",
                "Student ID",
                "Appointment ID",
                "Appointment Type",
                "Student Name",
                "Follow-Up  Count",
                "Appointment Status",
                "Next Clinician",
                "Next Appointment",
                "Follow-Up Reason",
                "Referral Status",
                "Referral Notes",
            ]
            df = pd.DataFrame(records, columns=columns)
            return df
        else:
            st.warning("No follow-up records found.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while fetching follow-up records: {e}")
        return pd.DataFrame()


clinians = ['Dr.Paul','Dr.Cissy','Dr.Dorothy']

### DRIVER CODE #####
def main():
    db = create_connection()
    create_follow_up_table(db)

    if "appointment_id" in st.session_state:
        appointment_id = st.session_state["appointment_id"]

    if "appointment_reasons" in st.session_state:
        appointment_reasons = st.session_state["appointment_reasons"]

        appointment = fetch_appointment_by_id(db, appointment_id)
        st.session_state['appointment'] = appointment

        if appointment:
            follow_up_menu = st.tabs(['Schedule follow-up','Track Follow-ups'])
            with follow_up_menu[0]:
                appointment_type = appointment[7] 
                student_id = appointment[1]
                if appointment_type == "NEW":
                    follow_up_count = 0
                elif appointment_type == "REVIEW":
                    follow_up_count = count_previous_appointments(db, student_id) + 1
                else:
                    follow_up_count = 0
                referral_status = st.selectbox('Referral Status', ['', 'With-In', 'Referred-Out', ])
                referral_notes = st.text_area('Referral Notes') if referral_status == 'Referred-Out' else None
                next_clinician = st.selectbox("Follow-up Clinician", clinians) if referral_status == 'With-In' else None
                next_appoint = st.date_input("Next Appointment Date") if referral_status == 'With-In' else None
                follow_up_reason = st.multiselect("Follow-up Reason", appointment_reasons)if referral_status == 'With-In' else None
                appoint_status = st.selectbox("Appointment Status", ['', "Pending", "Completed", "Canceled", 'Expired'])
                if st.button("Add Follow-Up"):
                    insert_follow_up_record(db, appointment_id, appointment_type,  follow_up_count, referral_status, referral_notes, next_clinician, next_appoint, follow_up_reason, appoint_status)
        
            with follow_up_menu[1]:
                follow_ups_df = fetch_all_follow_ups(db)
                if not follow_ups_df.empty:
                    st.dataframe(follow_ups_df)
        

    db.close()

if __name__ == "__main__":
    main()