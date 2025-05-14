import streamlit as st
import json
import pandas as pd
import os
import mysql.connector
from datetime import date, timedelta, datetime
from collections import OrderedDict

def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'MHPSS_db'
    }
    db = mysql.connector.connect(**config)
    return db

def fetch_all_appointments(db):
    cursor = db.cursor()
    query = """
    SELECT student_id, name, appointment_id, appointment_type, appointment_date, 
           appointment_time, clinician_name
    FROM appointment_students
    ORDER BY appointment_date ASC
    """
    cursor.execute(query)
    return cursor.fetchall()

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def format_time(appointment_time):
    if isinstance(appointment_time, timedelta):
        return str(appointment_time)
    elif isinstance(appointment_time, datetime):
        return appointment_time.strftime("%H:%M:%S")
    return appointment_time 


def main():
    db  = create_connection()
    if "selected_appointment" not in st.session_state:
        st.session_state.selected_appointment = []
    appointments = fetch_all_appointments(db)
    if not appointments:
        st.warning("No appointments found.")
        return
    formatted_appointments = [
        {
            "Student ID": appt[0],
            "Student Name": appt[1],
            "Appointment ID": appt[2],
            "Appointment Type": appt[3],
            "Appointment Date": appt[4].strftime("%Y-%m-%d") if isinstance(appt[4], date) else appt[4],
            "Appointment Time": format_time(appt[5]),
            "Clinician": appt[6]
        }
        for appt in appointments]

    unique_dates = sorted(set(appt["Appointment Date"] for appt in formatted_appointments))
    date_labels = {f"{ordinal(i+1)} Screening- {date}": date for i, date in enumerate(unique_dates)}
    with st.sidebar:
        mode = st.selectbox("Select Mode:", ["All", "Custom"], key="mode_selector")
        selected_date_label = st.selectbox("Filter by Date", list(date_labels.keys()), key="date_filter")
        selected_date = date_labels[selected_date_label]
        filtered_appointments = [appt for appt in formatted_appointments if appt["Appointment Date"] == selected_date]
        appointment_options = {
            f"{appt['Student Name']} - {appt['Student ID']} - {appt['Appointment ID']} - {appt['Appointment Type']} - {appt['Appointment Date']} - {appt['Appointment Time']} - {appt['Clinician']}": appt
            for appt in filtered_appointments}
        if mode == "All":
            chosen_appointments = list(appointment_options.keys())
        else:
            chosen_appointments = st.multiselect("Select Appointments", list(appointment_options.keys()), key="appointment_selector")
    if chosen_appointments:
        st.info(f":green[{selected_date_label}]: {len(chosen_appointments)}")
        selected_list = [appointment_options[appt] for appt in chosen_appointments]
        st.session_state.selected_appointment = selected_list 


    db.close()

if __name__ == "__main__":
    main()




