
import streamlit as st
import json
import pandas as pd
import os
# import mysql.connector
import importlib
from datetime import datetime

# def create_connection():
#     config = {
#         'user': 'root',
#         'password': '',
#         'host': 'localhost',
#         'port': 3306,
#         'database': 'mhpss_db'
#     }
#     db = mysql.connector.connect(**config)
#     cursor = db.cursor()
#     cursor.execute("USE mhpss_db")
#     return db

# def fetch_requested_tools_students(db, appointment_id):
#     cursor = db.cursor()
#     fetch_query = """
#     SELECT tool_name, tool_status FROM requested_tools_students
#     WHERE appointment_id = %s
#     """
#     cursor.execute(fetch_query, (appointment_id,))
#     result = cursor.fetchall()
#     tools_status = {row[0]: row[1] for row in result}
#     cursor.close()
#     return tools_status

# def update_tool_status(db, appointment_id, tool_name, new_status):
#     cursor = db.cursor()
#     update_query = """
#     UPDATE requested_tools_students
#     SET tool_status = %s
#     WHERE appointment_id = %s AND tool_name = %s
#     """
#     cursor.execute(update_query, (new_status, appointment_id, tool_name))
#     db.commit()

# def check_existing_entry(db, appointment_id):
#     try:
#         cursor = db.cursor()
#         query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = %s"
#         cursor.execute(query, (appointment_id,))
#         result = cursor.fetchone()[0]
#         return result > 0
#     except Exception as e:
#         st.error(f"An error occurred while checking for duplicates: {e}")
#         return False
#     finally:
#         cursor.close()
import sqlite3
import streamlit as st

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Optional: allows row['column_name'] access
        return db
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        return None


def fetch_requested_tools_students(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT tool_name, tool_status FROM requested_tools_students
    WHERE appointment_id = ?
    """
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    tools_status = {row[0]: row[1] for row in result}
    cursor.close()
    return tools_status


def update_tool_status(db, appointment_id, tool_name, new_status):
    cursor = db.cursor()
    update_query = """
    UPDATE requested_tools_students
    SET tool_status = ?
    WHERE appointment_id = ? AND tool_name = ?
    """
    cursor.execute(update_query, (new_status, appointment_id, tool_name))
    db.commit()


def check_existing_entry(db, appointment_id):
    try:
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = ?"
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()[0]
        return result > 0
    except Exception as e:
        st.error(f"An error occurred while checking for duplicates: {e}")
        return False
    finally:
        cursor.close()

import phq9_qn
import gad7_qn

tool_modules = {
    'PHQ-9': phq9_qn.main,
    'GAD-7':gad7_qn.main
}



### DRIVER CODE ######
def main():
    db = create_connection()
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id

        requested_tools_students = fetch_requested_tools_students(db, appointment_id)
        st.write(requested_tools_students)
        tools_list = list(requested_tools_students.keys())
        if not tools_list:
            st.warning("No requested tools found.")
            db.close() 
            return

        tabs = st.tabs(tools_list)
        for idx, tool in enumerate(tools_list):
            with tabs[idx]:
                tool_status = requested_tools_students[tool]
                if tool not in tool_modules:
                    st.warning(f"No module found for the tool: {tool} Please contact suppport for help")
                    continue
                module_function = tool_modules[tool]
                if tool_status == 'Pending':
                    st.info(f"Please fill out the {tool} form:")
                    module_function() 
                    if st.button(f"Submit {tool} responses"):
                        st.success(f"{tool} response captured ✅ !")
                        update_tool_status(db, appointment_id, tool, 'Completed')
                else:
                    st.success(f"{tool} completed ✅ ")

    db.close()

if __name__ == "__main__":
    main()


