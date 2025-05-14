import streamlit as st
# import mysql.connector
from datetime import datetime
import json
import pandas as pd
import os
import phq9_qn

# def create_connection():
#     try:
#         conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
#         conn.row_factory = sqlite3.Row
#         return conn
#     except sqlite3.Error as e:
#         st.error(f"Error connecting to SQLite: {e}")
#         return None
# def create_requested_tools_table(db):
#     cursor = db.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS requested_tools (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             student_id VARCHAR(50),
#             appointment_id VARCHAR(50),
#             student_name VARCHAR(255),
#             tool_name VARCHAR(255),
#             requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             tool_status VARCHAR(50) DEFAULT 'Pending'
#         )
#     """)
#     db.commit()

# def update_tool_status(db, appointment_id, tool_name, new_status):
#     cursor = db.cursor()
#     cursor.execute("""
#         UPDATE requested_tools
#         SET tool_status = %s
#         WHERE appointment_id = %s AND tool_name = %s
#     """, (new_status, appointment_id, tool_name))
#     db.commit()

# def fetch_requested_tools(db, appointment_id):
#     cursor = db.cursor()
#     cursor.execute("""
#         SELECT tool_name, tool_status FROM requested_tools
#         WHERE appointment_id = %s
#     """, (appointment_id,))
#     return {row[0]: row[1] for row in cursor.fetchall()}

# def capture_questionnaire_responses(form_key, questions):
#     responses = []
#     answered_questions = set()
#     with st.form(form_key):
#         st.write(f'Filling {form_key} Questionnaire')
#         for i, question in enumerate(questions, start=1):
#             st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
#             selected_radio = st.radio(f'', ['Select from options below', 'Not at all', 'Several Days', 'More Than Half the Days', 'Nearly Every Day'], key=f"{form_key}_q{i}")
#             if selected_radio != 'Select from options below':
#                 responses.append({'question': f'Q{i}', 'response': selected_radio})
#                 answered_questions.add(i)
#         submit_button = st.form_submit_button('Submit')
#         if submit_button:
#             if len(answered_questions) != len(questions):
#                 st.warning('Please complete the entire form')
#                 return None
#             return responses
#     return None

# def check_existing_entry(db, appointment_id):
#     cursor = db.cursor()
#     cursor.execute("""
#         SELECT COUNT(*) FROM requested_tools WHERE appointment_id = %s AND tool_status = 'Completed'
#     """, (appointment_id,))
#     return cursor.fetchone()[0] > 0

import sqlite3
import streamlit as st

def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

def create_requested_tools_table(db):
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requested_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            appointment_id TEXT,
            student_name TEXT,
            tool_name TEXT,
            requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tool_status TEXT DEFAULT 'Pending'
        )
    """)
    db.commit()

def update_tool_status(db, appointment_id, tool_name, new_status):
    cursor = db.cursor()
    cursor.execute("""
        UPDATE requested_tools
        SET tool_status = ?
        WHERE appointment_id = ? AND tool_name = ?
    """, (new_status, appointment_id, tool_name))
    db.commit()

def fetch_requested_tools(db, appointment_id):
    cursor = db.cursor()
    cursor.execute("""
        SELECT tool_name, tool_status FROM requested_tools
        WHERE appointment_id = ?
    """, (appointment_id,))
    return {row[0]: row[1] for row in cursor.fetchall()}

def capture_questionnaire_responses(form_key, questions):
    responses = []
    answered_questions = set()
    with st.form(form_key):
        st.write(f'Filling {form_key} Questionnaire')
        for i, question in enumerate(questions, start=1):
            st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
            selected_radio = st.radio(
                f'', 
                ['Select from options below', 'Not at all', 'Several Days', 'More Than Half the Days', 'Nearly Every Day'], 
                key=f"{form_key}_q{i}"
            )
            if selected_radio != 'Select from options below':
                responses.append({'question': f'Q{i}', 'response': selected_radio})
                answered_questions.add(i)
        submit_button = st.form_submit_button('Submit')
        if submit_button:
            if len(answered_questions) != len(questions):
                st.warning('Please complete the entire form')
                return None
            return responses
    return None

def check_existing_entry(db, appointment_id):
    cursor = db.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM requested_tools 
        WHERE appointment_id = ? AND tool_status = 'Completed'
    """, (appointment_id,))
    return cursor.fetchone()[0] > 0


#### DRIVER CODE #######
def main():
    db = create_connection()
    create_requested_tools_table(db)
    
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
    
        requested_tools = fetch_requested_tools(db, appointment_id)
        tools_list = list(requested_tools.keys())
        if tools_list:
            tabs = st.tabs(tools_list)
            for tool, tab in zip(tools_list, tabs):
                with tab:
                    if tool == 'PHQ-9':
                        responses = capture_questionnaire_responses(f"PHQ-9-{appointment_id}", phq9_qn.questions)
                    elif tool == 'GAD-7':
                        responses = capture_questionnaire_responses(f"GAD-7-{appointment_id}", ['Question 1', 'Question 2', '...'])
                    else:
                        st.warning(f"No existing template for the tool: {tool}")
                        responses = None
                    
                    if responses:
                        if check_existing_entry(db, appointment_id):
                            st.error(f"A form already exists for Appointment ID: {appointment_id}.")
                        else:
                            update_tool_status(db, appointment_id, tool, 'Completed')
                            st.success(f"✅ {tool} form submitted successfully.")
        else:
            st.warning('No requested tools')
    db.close()

if __name__ == "__main__":
    main()
