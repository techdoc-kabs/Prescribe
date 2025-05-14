import streamlit as st
import json
import pandas as pd
import os
# import mysql.connector
import appointments
import requested_tools
from datetime import datetime
import seaborn as sns
import sqlite3
import results_filled

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None
def fetch_student_users(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("STUD-") or search_input.isdigit():
        query = """
        SELECT student_id, name, age, gender, student_class, stream
        FROM student_users
        WHERE student_id = ?
        """
        cursor.execute(query, (search_input.strip(),))
    else: 
        name_parts = search_input.strip().split()
        query_conditions = []
        params = []

        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("name LIKE ?")
            query_conditions.append("name LIKE ?")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("name LIKE ?")
            params.append(f"%{search_input}%")
        query = f"""
        SELECT student_id, name, age, gender, student_class, stream
        FROM student_users
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))
    return cursor.fetchall()

def fetch_appointments_for_student(db, student_id):
    cursor = db.cursor()
    query = """
    SELECT appointment_id,student_id, name, appointment_type, appointment_date
    FROM screen_appointments 
    WHERE student_id = ?
    """
    cursor.execute(query, (student_id,))
    appointments = cursor.fetchall()
    return appointments


def display_session_notes(note):
    st.markdown("""
        <style>
            .preview-container {
                background-color: #EAEAEA;
                border: 2px solid #B0B0B0;
                padding: 10px 20px;
                border-radius: 20px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            .line {
                margin-bottom: 8px;
            }
            .label {
                font-family: 'Times New Roman', serif;
                font-size: 18px;
                font-weight: bold;
                color: #0056b3;
                font-style: italic;
                display: inline-block;
                width: 180px;
            }
            .text {
                font-family: 'Times New Roman', serif;
                font-size: 18px;
                color: #333;
                font-style: italic;
                display: inline-block;
                vertical-align: top;
                max-width: calc(100% - 200px);
                word-wrap: break-word;
            }
            .header {
                font-family: 'Times New Roman', serif;
                font-size: 20px;
                font-weight: bold;
                color: #222;
                margin-bottom: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    appointment_date = note.get("appointment_date", "N/A")
    appointment_time = note.get("appointment_time", "N/A")
    try:
        formatted_time = datetime.strptime(appointment_time, "%H:%M:%S").strftime("%H:%M")
    except:
        formatted_time = appointment_time 
    st.markdown(f"""
        <div class="preview-container">
            <div class="header">📌 SESSION NOTES</div>
            <div class="line"><span class="label">🕐 Date & Time:</span><span class="text">{appointment_date} at {formatted_time}</span></div>
            <div class="line"><span class="label">🗨️ Current Concerns:</span><span class="text">{note.get('current_concerns')}</span></div>
            <div class="line"><span class="label">🧾 Case Summary:</span><span class="text">{note.get('case_summary')}</span></div>
            <div class="line"><span class="label">🧠 Working Diagnosis:</span><span class="text">{note.get('working_diagnosis')}</span></div>
            <div class="line"><span class="label">🧩 Intervention:</span><span class="text">{note.get('intervention')}</span></div>
            <div class="line"><span class="label">📅 Follow-Up:</span><span class="text">{note.get('follow_up')}</span></div>
            <div class="line"><span class="label">🔁 Referral Plan:</span><span class="text">{note.get('refer')}</span></div>
            <div class="line"><span class="label">📝 Remarks:</span><span class="text">{note.get('remarks')}</span></div>
            <div class="line"><span class="label">👤 Clinician:</span><span class="text">{note.get('clinician_name')}</span></div>
        </div>
    """, unsafe_allow_html=True)

def fetch_session_notes(db, appointment_id):
    cursor = db.cursor()
    query = """
    SELECT * FROM session_notes WHERE appointment_id = ?
    """
    cursor.execute(query, (appointment_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

from streamlit_option_menu import option_menu

def main():
    db = create_connection()
    if 'student_id' not in st.session_state:
        st.session_state["student_id"] = ""

    if 'appointment_id' not in st.session_state:
        st.session_state["appointment_id"] = ""
    
    st.sidebar.subheader("STUDENT DETAILS")
    with st.sidebar.expander("🔍SEARCH", expanded=True):
        search_input = st.text_input("Enter Name or Student ID", "")
    results = []
    if search_input.strip():
        results = fetch_student_users(db, search_input)

    selected_record = None
    if results:
        st.sidebar.write(f"**{len(results)} result(s) found**")
        options = {f"{r['name']} - {r['student_id']}": r for r in results}
        selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
        selected_record = options[selected_option]
        if selected_record:
            with st.sidebar.expander("📄 STUDENT DETAILS", expanded=True):
                st.write(f"**Student ID:** {selected_record['student_id']}")
                st.write(f"**Student Name:** {selected_record['name']}")
                st.write(f"**Age(Yrs):** {selected_record['age']}")
                st.write(f"**Sex:** {selected_record['gender']}")
                st.write(f"**Class:** {selected_record['student_class']}")
                st.write(f"**Stream:** {selected_record['stream']}")
            st.session_state["student_id"] = selected_record["student_id"]
            student_id = st.session_state["student_id"]
            file_menu = option_menu(
            menu_title='',
            orientation='horizontal',
            menu_icon='',
            options=['Session notes', 'Assessments', 'Compiled_File'],
            icons=["book",  "pencil-square",'printer'],
            styles={
                "container": {"padding": "8!important", "background-color": '#e0f7fa', 'border': '2px solid red'},
                "icon": {"color": "red", "font-size": "15px"},
                "nav-link": {"color": "#000000", "font-size": "15px", "font-weight": 'bold', "text-align": "left", "--hover-color": "#d32f2f"},
                "nav-link-selected": {"background-color": "#1976d2"},
            },
            key="file_menu")
            if file_menu == 'Session notes':
                appointments = fetch_appointments_for_student(db, student_id)
                if appointments:
                    for idx, appointment in enumerate(appointments, start=1):  # Add index
                        appointment_id = appointment[0]
                        appointment_date = appointment[4]
                        with st.expander(f'📅 :blue[[{idx}]] :orange[{selected_record["name"]}] - :red[{appointment_id}] - :green[{appointment_date}]', expanded=False):
                            notes = fetch_session_notes(db, appointment_id)
                            if notes:
                                display_session_notes(notes)
                            else:
                                st.warning('No clinical notes')


            elif file_menu == 'Assessments':
                appointments = fetch_appointments_for_student(db, student_id)
                if appointments:
                    for idx, appointment in enumerate(appointments, start=1):  # Add index
                        appointment_id = appointment[0]
                        st.session_state["appointment_id"] = appointment_id
                        appointment_date = appointment[4]
                        # with st.expander(f'📅 :blue[[{idx}]] :orange[{selected_record["name"]}] - :red[{appointment_id}] - :green[{appointment_date}]', expanded=False):
                        results_filled.main()
                            
                        
    db.close()

if __name__ == "__main__":
    main()



