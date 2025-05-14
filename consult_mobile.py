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
import fitz 
import docx2txt
import fitz
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
from streamlit_card import card
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
        SELECT student_id, name, age, gender, student_class, stream, date
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
    return [dict(row) for row in cursor.fetchall()]



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
assessment_tools = ['PHQ-9', 'GAD-7', 'SRQ', 'HTQ', 'BDI']

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"



def fetch_appointment_details_by_name(name):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT a.appointment_id, a.name, a.appointment_type, a.screen_type, a.term, 
                       a.appointment_date, a.appointment_time, a.clinician_name, a.reason, 
                       s.student_class, s.stream,
                       GROUP_CONCAT(DISTINCT r.tool_status) AS tool_status
                FROM screen_appointments a
                JOIN student_users s ON a.student_id = s.student_id
                LEFT JOIN requested_tools_students r ON a.appointment_id = r.appointment_id
                WHERE s.name = ?
                GROUP BY a.appointment_id
            """
            cursor.execute(query, (name,))
            records = cursor.fetchall()
            return [dict(row) for row in records]
        except sqlite3.Error as e:
            st.error(f"Error fetching appointment details: {e}")
        finally:
            cursor.close()
            connection.close()
    return []

import appoint_consult
def main():
    db = create_connection()
    create_consults_table(db)
    create_assessment_tools_table(db)
    for key in ["appointment_id", "student_id", "student_name", "clinician_name", 
                "selected_term", "selected_screen_type", "selected_record", 
                "selected_appointment", "selected_tool", "last_search_input"]:
        if key not in st.session_state:
            st.session_state[key] = None
    with st.sidebar:
        st.subheader('STUDENT INFO')
    with st.sidebar.expander("🔍SEARCH", expanded=True):
        search_input = st.text_input("Enter Name or STD ID", "")
    if search_input != st.session_state.last_search_input:
        st.session_state.selected_record = None
        st.session_state.selected_appointment = None
        st.session_state.selected_tool = None
        st.session_state.last_search_input = search_input
    if st.session_state.selected_record is None and search_input.strip():
        results = fetch_students(db, search_input)
        if results:
            st.sidebar.write(f"**{len(results)} result(s) found**")
            options = {f"{r['name']} - {r['student_id']}": r for r in results}
            selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
            st.session_state.selected_record = options[selected_option]
        else:
            st.sidebar.error(f'No record for {search_input}')
    if st.session_state.selected_record:
        r = st.session_state.selected_record
        with st.sidebar.expander("📄 STUDENT INFO", expanded=True):
            st.write(f"Student ID: {r['student_id']}")
            st.write(f"Name: {r['name']}")
            st.write(f"Gender: {r['gender']}")
            st.write(f"Age: {r['age']} years")
            st.write(f"Class: {r['student_class']}")
            st.write(f"Stream: {r['stream']}")
        
        const_menu= option_menu(
                menu_title='',
                orientation='horizontal',
                menu_icon='',
                options=['SCHEDULE CONSULT', 'CONSULTATION'],
                icons=['list', 'hospital', 'cloud-upload'],
                styles={
                    "container": {"padding": "8!important", "background-color": 'black','border': '0.01px dotted red'},
                    "icon": {"color": "red", "font-size": "13px"},
                    "nav-link": {"color": "#d7c4c1", "font-size": "13px","font-weight":'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                    "nav-link-selected": {"background-color": "green"},
                },
                key="const_menu")

        if const_menu == 'SCHEDULE CONSULT':
            appoint_consult.main()

        elif const_menu == 'CONSULTATION':
            appointments = sorted(fetch_appointment_details_by_name(r['name']),
              key=lambda x: (x["appointment_date"], x["appointment_time"]),
              reverse=True)
            if appointments and not st.session_state.selected_appointment:
                if st.button("🔙 Screening Menu"):
                    st.session_state.selected_record = None
                    st.rerun()
                col1, col2 = st.columns(2)
                for idx, appointment in enumerate(appointments):
                    appointment_id = appointment["appointment_id"]
                    color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"
                    title = ordinal(len(appointments) - idx)
                    with col1 if idx % 2 == 0 else col2:
                        clicked = card(
                            title=f'{title} Appointment',
                            text=f"{appointment_id}",
                            url=None,
                            styles={
                                "card": {
                                    "width": "220px", "height": "200px",
                                    "border-radius": "30px", "background": color,
                                    "color": "white", "box-shadow": "0 4px 12px rgba(0,0,0,0.15)",
                                    "border": "0.01px solid red", "text-align": "center",
                                },
                                "text": {"font-family": "serif"},
                                "title": {"font-family": "serif", 'font-size': 22}
                            },
                        )
                        if clicked:
                            st.session_state.selected_appointment = appointment
                            st.session_state.appointment_id = appointment_id
                            st.rerun()
            elif st.session_state.selected_appointment:
                if st.button("🔙 Return to Appointments"):
                    st.session_state.selected_appointment = None
                    st.session_state.appointment_id = None
                    st.rerun()
                clinical_menu= option_menu(
                    menu_title='',
                    orientation='horizontal',
                    menu_icon='',
                    options=['Add_Notes', 'Diagnosis','Mgt_Plan', 'Follow-up', 'Report'],
                    icons=['book', 'hospital', 'file','cloud-upload', 'printer'],
                    styles={
                        "container": {"padding": "8!important", "background-color": 'black','border': '0.01px dotted red'},
                        "icon": {"color": "red", "font-size": "13px"},
                        "nav-link": {"color": "#d7c4c1", "font-size": "13px","font-weight":'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                        "nav-link-selected": {"background-color": "green"},
                    },
                    key="clinical_menu")
                if clinical_menu == 'Add_Notes':
                    clinical_notes.main()
                elif clinical_menu =='Diagnosis':
                    mental_disorder.main()
                elif clinical_menu == 'Mgt_Plan':
                    mgt_menu = st.tabs(['Psycholosocial Interventions', 'Pharmacotherapy'])
                    with mgt_menu[0]:
                        managment.main()
                    with mgt_menu[1]:
                        prescriptions.main()
                elif clinical_menu == 'Follow-up':
                    follow_ups.main()
    db.close()

if __name__ == "__main__":
    main()
