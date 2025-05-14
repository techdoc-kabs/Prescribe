import streamlit as st
# import mysql.connector
from streamlit_option_menu import option_menu
from datetime import datetime
import base64
import os
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import json
import PyPDF2
import io
import docx
from PIL import Image
import pytesseract
# import fitz 
import docx2txt
# import fitz
from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
from docx2pdf import convert
# import tools
# import , forms, follow_ups, patient_file
# import phq9_responses 
import clinical_notes
# import assessments, share_tools, captured_responses, , requested_tools, phq9_responses
# import retrive_file, captured_response_consult, reqested_forms_to_fill, entire_file
import mental_disorder, prescriptions
import consult_assesment, reqested_forms_to_fill, captured_responses, results_filled
import managment, follow_ups
#### DRIVER CODE #####

import sqlite3
import stud_render_tools_update 
import stud_render_tools_update_mlt, results_filled_mlt

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables access by column name
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None


### REGISTERING STUDENTS #################################
def create_consults_table(db):
    cursor = db.cursor()
    create_students_table_query = """
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        student_name TEXT NOT NULL,
        age INTEGER,
        gender TEXT, 
        class TEXT,
        date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_students_table_query)
    db.commit()


def create_assessment_tools_table(db):
    cursor = db.cursor()
    create_query = """
    CREATE TABLE IF NOT EXISTS assessment_tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id TEXT,
        assessment_tool TEXT
    )
    """
    cursor.execute(create_query)
    db.commit()


def insert_requested_assessment_tool(db, appointment_id, assessment_to_add):
    cursor = db.cursor()
    insert_query = """
    INSERT INTO assessment_tools (appointment_id, assessment_tool)
    VALUES (?, ?)
    """
    for assessment_tool in assessment_to_add:
        values = (appointment_id, assessment_tool)
        cursor.execute(insert_query, values)
    db.commit()
    st.success("Assessment tools added to the appointment!")


def fetch_requested_assessment_tools_df(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT id, appointment_id, assessment_tool 
    FROM assessment_tools
    WHERE appointment_id = ?
    """
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    columns = ["Test ID", "Appointment ID", "Assessment Tool"]
    assessment_tools_df = pd.DataFrame(result, columns=columns)
    return assessment_tools_df


def fetch_appointments(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("APP-") or search_input.isdigit():
        query = """
        SELECT student_id, name, appointment_id, appointment_date, appointment_type, clinician_name
        FROM screen_appointments
        WHERE appointment_id = ?
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
        SELECT student_id, name, appointment_id, appointment_date, appointment_type, clinician_name
        FROM screen_appointments
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))
    return cursor.fetchall()


def fetch_students(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("STUD-") or search_input.isdigit():
        query = """
        SELECT student_id, name, age, gender, class, stream
        FROM students
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
        SELECT student_id, name, age, gender, class, stream
        FROM students
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))
    return cursor.fetchall()
def fetch_appointments_students(db, search_input, selected_term=None, selected_screen_type=None):
    cursor = db.cursor()
    params = []

    if search_input.strip().upper().startswith("SCREEN-") or search_input.isdigit():
        query = """
        SELECT id, student_id, name, appointment_id, appointment_date, appointment_time, appointment_type, term, screen_type, clinician_name
        FROM screen_appointments
        WHERE appointment_id = ?
        ORDER BY appointment_date DESC, appointment_time DESC
        """
        params = (search_input.strip(),)
    else:
        name_parts = search_input.strip().split()
        query_conditions = []
        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("name LIKE ?")
            query_conditions.append("name LIKE ?")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("name LIKE ?")
            params.append(f"%{search_input}%")
        if selected_term:
            query_conditions.append("term = ?")
            params.append(selected_term)
        if selected_screen_type:
            query_conditions.append("screen_type = ?")
            params.append(selected_screen_type)
        query = f"""
        SELECT id, student_id, name, appointment_id, appointment_date, appointment_time, appointment_type, term, screen_type, clinician_name
        FROM screen_appointments
        WHERE {" AND ".join(query_conditions)}
        ORDER BY appointment_date DESC, appointment_time DESC
        """
    cursor.execute(query, tuple(params))
    appointments = [dict(row) for row in cursor.fetchall()]
    return appointments

def fetch_student_by_id(db, student_id):
    cursor = db.cursor()
    query = """
    SELECT student_id, name, age, gender, student_class, stream, username, contact, email 
    FROM student_users
    WHERE student_id = ?
    """
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    return result
# import managment, appoint_screen
assessment_tools = ['PHQ-9', 'GAD-7', 'SRQ', 'HTQ', 'BDI']


import stud_render_tools
##### DRIVER CODE #####################################################
def main():
    db = create_connection()
    create_consults_table(db)
    create_assessment_tools_table(db)
    if "appointment_id" not in st.session_state:
        st.session_state["appointment_id"] = None
    if "student_id" not in st.session_state:
        st.session_state["student_id"] = None

    if "student_name" not in st.session_state:
        st.session_state["student_name"] = None    
    
    if "clinician_name" not in st.session_state:
        st.session_state["clinician_name"] = None

    if "selected_term" not in st.session_state:
        st.session_state["selected_term"] = None
    

    if "selected_screen_type" not in st.session_state:
        st.session_state["selected_screen_type"] = None

    consult_menu = option_menu(
                    menu_title='',
                    orientation='horizontal',
                    menu_icon='',
                    options=['SCREENING', 'CONSULTATIONS', 'FOLLOW_UPS','PREVIEW'],
                    icons=['pencil', 'book','calendar-plus','eye',],
                    styles={
                        "container": {"padding": "8!important", "background-color": 'black','border': '0.01px dotted red'},
                        "icon": {"color": "red", "font-size": "11px"},
                        "nav-link": {"color": "#d7c4c1", "font-size": "11px","font-weight":'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                        "nav-link-selected": {"background-color": "green"},
                    },
                    key="consult_menu"
                )

    if consult_menu == 'SCREENING':
        c1, c2 = st.columns([1.3, 2])
        asses_menu= st.tabs(['Render', 'Fill','Responses', 'Results'])
        with c1.expander('SCREENING TASKS', expanded=True):
            schedule_option = st.radio("Select schedule", ['Single Student', 'Multiple Students'])
        if schedule_option == 'Single Student':
            with c2.expander("🔍 Search Student", expanded=True):
                search_input = st.text_input("", placeholder="Type your name and press enter")
            results = []
            selected_record = None
            if search_input.strip():
                results = fetch_appointments_students(db, search_input)
                if results:
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
                    <div class='appointment-header'>APPOINTMENT DETAILS</div>
                    """,
                    unsafe_allow_html=True)
                    st.sidebar.write(' ')
                    selected_record = results[0]
                    term_list = ["1st-Term", "2nd-Term", "3rd-Term"]
                    screen_type_list = ["PRE-SCREEN", "POST-SCREEN", "CONSULT-SCREEN", "ON-REQUEST"]
                    with st.sidebar.expander("FILTER OPTIONS", expanded=True):
                        st.write(f"**{len(results)} result(s) found**")
                        c1, c2 = st.columns([1, 1.5])
                        
                        selected_term = c1.selectbox("TERM", term_list, index=term_list.index(selected_record['term']) if selected_record['term'] in term_list else 0)
                        

                        selected_screen_type = c2.selectbox("SCREEN TYPE", screen_type_list, index=screen_type_list.index(selected_record['screen_type']) if selected_record['screen_type'] in screen_type_list else 0)
                    filtered_results = [r for r in results if r['term'] == selected_term and r['screen_type'] == selected_screen_type]
                    if filtered_results:
                        with st.sidebar.expander("🔍 SEARCH RESULTS", expanded=True):
                            for record in filtered_results:
                                record_display = f"""
                                - ***Student ID***: `{record['student_id']}`
                                - ***Name***: `{record['name']}`
                                - ***Appointment ID***: `{record['appointment_id']}`
                                - ***Appointment Date***: `{record['appointment_date']}`
                                - ***Appointment Type***: `{record['appointment_type']}`
                                - ***Term***: `{record['term']}`
                                - ***Screen Type***: `{record['screen_type']}`
                                - ***Clinician Name***: `{record['clinician_name']}`
                                """
                                st.markdown(record_display)
                        st.session_state["selected_term"] = selected_term
                        st.session_state["selected_screen_type"] = selected_screen_type
                        
                        st.session_state["appointment_id"] = record["appointment_id"]
                        st.session_state["student_id"] = record["student_id"]
                        st.session_state["name"] = record["name"]
                        if "student_id" in st.session_state:
                            student_id = st.session_state["student_id"]
                            student_name = st.session_state["name"]
                            appointment_id = st.session_state["appointment_id"]
                            clinician = st.session_state["clinician_name"]
                            # asses_menu= st.tabs(['Render', 'Fill','Responses', 'Results'])
                            with asses_menu[0]:
                                stud_render_tools_update.main()
                            with asses_menu[1]:
                                reqested_forms_to_fill.main()
                            with asses_menu[2]:
                                captured_responses.main()
                            with asses_menu[3]:
                                results_filled.main()

        elif schedule_option == 'Multiple Students':
            with asses_menu[0]:
                stud_render_tools_update_mlt.main()
            with asses_menu[1]:
                reqested_forms_to_fill.main()
            with asses_menu[2]:
                captured_responses.main()
            with asses_menu[3]:
                results_filled_mlt.main()

    elif consult_menu == 'CONSULTATIONS':
        with st.sidebar:
            st.subheader('STUDENT DETIALS')
        with st.sidebar.expander("🔍SEARCH", expanded=True):
            search_input = st.text_input("Enter Name or Appointment ID", "")
        results = []
        if search_input.strip():
            results = fetch_appointments(db, search_input)
        selected_record = None
        if results:
            st.sidebar.write(f"**{len(results)} result(s) found**")
            options = {f"{r['name']} - {r['appointment_id']}": r for r in results}
            selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
            selected_record = options[selected_option]
        if selected_record:
            with st.sidebar.expander("📄 APPOINTMENT DETIALS", expanded=True):
                st.write(f"Student ID: {selected_record['student_id']}")
                st.write(f"Student Name: {selected_record['name']}")
                st.write(f"Appointment ID: {selected_record['appointment_id']}")
                st.write(f"Appointment Date: {selected_record['appointment_date']}")
                st.write(f"Appointment Type: {selected_record['appointment_type']}")
                st.write(f"Clinician: {selected_record['clinician_name']}")
            st.session_state["appointment_id"] = selected_record["appointment_id"]
            st.session_state["student_id"] = selected_record["student_id"]
            st.session_state["student_name"] = selected_record["name"]
            st.session_state["clinician_name"] = selected_record["clinician_name"]
            appointment_id = st.session_state.appointment_id
            clinical_menu= st.tabs(['CLINICAL-NOTES','DIAGNOSIS','MANAGEMENT PLAN', 'FOLLOW_UP PLAN', 'ATTACHMENTS'])
            with clinical_menu[0]:
                note_menu = st.tabs(['Clinical assessment', 'Review Notes'])
                with note_menu[0]:
                    clinical_notes.main()

            with clinical_menu[1]:
                mental_disorder.main()
                
            with clinical_menu[2]:
                mgt_menu = st.tabs(['Psycholosocial Interventions', 'Pharmacotherapy'])
                with mgt_menu[0]:
                    managment.main()
                
                with mgt_menu[1]:
                    prescriptions.main()
                
            with clinical_menu[3]:
                follow_ups.main()

    db.close()
if __name__ == "__main__":
    main()

