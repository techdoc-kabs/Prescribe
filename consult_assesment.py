import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu

def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'kabs_db'
    }
    return mysql.connector.connect(**config)

def create_requested_tools_table(db):
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS requested_tools (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(50),
        appointment_id VARCHAR(50),
        student_name VARCHAR(255),
        tool_name VARCHAR(255),
        requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tool_status VARCHAR(50) DEFAULT 'Pending'  -- New column for status
    )"""
    cursor.execute(create_table_query)
    db.commit()



def insert_requested_tools(db, student_id, appointment_id, student_name, tools_to_add):
    cursor = db.cursor()
    for tool in tools_to_add:
        insert_query = """
        INSERT INTO requested_tools (student_id, appointment_id, student_name, tool_name)
        VALUES (%s, %s, %s, %s)
        """
        values = (student_id, appointment_id, student_name, tool)
        cursor.execute(insert_query, values)
    db.commit()

def fetch_requested_tools(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT id, student_id, appointment_id, student_name, tool_name FROM requested_tools
    WHERE appointment_id = %s
    """
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    tools_list = []  
    for row in result:
        tools_list.append(row[4]) 
    cursor.close()
    return tools_list


def remove_requested_tool(db, appointment_id, tool_to_remove):
    cursor = db.cursor()
    delete_query = """
    DELETE FROM requested_tools
    WHERE appointment_id = %s AND tool_name = %s"""
    cursor.execute(delete_query, (appointment_id, tool_to_remove))
    db.commit()
    cursor.execute("""
    SELECT tool_name FROM requested_tools WHERE appointment_id = %s AND tool_name = %s
    """, (appointment_id, tool_to_remove))
    result = cursor.fetchone()
    if result is None:
        st.success(f"The tool '{tool_to_remove}' was successfully removed.")
    else:
        st.warning(f"Failed to remove the tool '{tool_to_remove}'.")
    cursor.close()

def fetch_requested_tools_df(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT id, student_id, appointment_id, student_name, tool_name, tool_status FROM requested_tools
    WHERE appointment_id = %s"""
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    tools_df = pd.DataFrame(result, columns=['ID', 'Student ID', 'Appointment ID', 'Student Name', 'Tool Name','Status'])
    cursor.close()
    return tools_df




### DRIVER CODE #####
def main():
    db = create_connection()
    create_requested_tools_table(db)

    if "appointment_id" in st.session_state:
        appointment_id = st.session_state['appointment_id']

    if "student_id" in st.session_state:
        student_id = st.session_state['student_id']

    if "student_name" in st.session_state:
        student_name = st.session_state['student_name']


        tools = ['PHQ-9', 'GAD-7', 'SRQ', 'BDI', 'CAGE', 'SAD PERSONS SCALE']
        tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
        tools_in_db = tools_in_db_df['Tool Name'].tolist()
        col1, col2 = st.columns(2)
        
        with col1.form('tool_form'):
            selected_tools = st.multiselect('ADMINISTER TOOL', tools)
            add = st.form_submit_button('Add')
            if add:
                tools_to_add = [tool for tool in selected_tools if tool not in tools_in_db]
                if not tools_to_add:
                    st.warning(f"{selected_tools} already exits")
                else:
                    insert_requested_tools(db, student_id, appointment_id, student_name, tools_to_add)
                    st.success(f"{tools_to_add} requested")
                    tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
                    tools_in_db = tools_in_db_df['Tool Name'].tolist()

        with st.expander("Tools in Database", expanded=True):
            st.dataframe(tools_in_db_df)

        

        with col2.form("remove_tool_form"):
            tool_to_remove = st.selectbox("Select a Tool to Remove", tools_in_db)
            remove = st.form_submit_button("Remove Tool")
            if remove:
                if tool_to_remove:
                    remove_requested_tool(db, appointment_id, tool_to_remove)
                    st.success(f"The tool '{tool_to_remove}' was successfully removed.")
                    tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
                    tools_in_db = tools_in_db_df['Tool Name'].tolist()
                else:
                    st.warning("Please select a tool to remove.")
        
    db.close()

if __name__ == '__main__':
    main()
