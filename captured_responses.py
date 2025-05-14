import streamlit as st
# import mysql.connector
from datetime import datetime
import json
import pandas as pd
import os
import phq9_qn
import gad7_qn
import phq9_responses
import gad7_responses
# import requested_tools_students


# def create_connection():
#     config = {
#         'user': 'root',
#         'password': '',
#         'host': 'localhost',
#         'port': 3306,
#         'database': 'mhpss_db'
#     }
#     return mysql.connector.connect(**config)

# def fetch_requested_tools_students(db, appointment_id):
#     cursor = db.cursor()
#     cursor.execute("""
#         SELECT tool_name, tool_status FROM requested_tools_students
#         WHERE appointment_id = %s
#     """, (appointment_id,))
#     return {row[0]: row[1] for row in cursor.fetchall()}

# def get_tool_status(db, appointment_id, tool_name):
#     cursor = db.cursor()
#     cursor.execute("""
#         SELECT tool_status FROM requested_tools_students
#         WHERE appointment_id = %s AND tool_name = %s
#     """, (appointment_id, tool_name))
#     result = cursor.fetchone()
#     return result[0] if result else None 



import sqlite3

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Optional: for accessing columns by name
        return db
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        return None


def fetch_requested_tools_students(db, appointment_id):
    cursor = db.cursor()
    cursor.execute("""
        SELECT tool_name, tool_status FROM requested_tools_students
        WHERE appointment_id = ?
    """, (appointment_id,))
    return {row[0]: row[1] for row in cursor.fetchall()}


def get_tool_status(db, appointment_id, tool_name):
    cursor = db.cursor()
    cursor.execute("""
        SELECT tool_status FROM requested_tools_students
        WHERE appointment_id = ? AND tool_name = ?
    """, (appointment_id, tool_name))
    result = cursor.fetchone()
    return result[0] if result else None



tool_modules = {
    'PHQ-9': phq9_responses.main,
    'GAD-7': gad7_responses.main,
}   

def main():
    db = create_connection()
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
        st.write('Responses')
        requested_tools_students = fetch_requested_tools_students(db, appointment_id)
        tools_list = list(requested_tools_students.keys())

        if not tools_list:
            st.warning("No requested tools found.")
            db.close()
            return

        tabs = st.tabs(tools_list)
        for idx, tool in enumerate(tools_list):
            with tabs[idx]:
                tool_status = get_tool_status(db, appointment_id, tool)

                if tool in tool_modules:
                    if tool_status == 'Completed':
                        tool_function = tool_modules[tool]  
                        tool_function() 
                    else:
                        st.warning(f"{tool} is not yet filled. Please complete it.")
                else:
                    st.error(f"No existing template found for {tool}.")

    db.close()

if __name__ == "__main__":
    main()
