import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'MHPSS_db'
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
        tool_status VARCHAR(50) DEFAULT 'Pending'
    )"""
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()

def insert_requested_tools(db, appointment_data, tools_to_add):
    cursor = db.cursor()
    try:
        for appointment in appointment_data:
            student_name = appointment.get("Student Name", "N/A")
            appointment_id = appointment.get("Appointment ID", "N/A")
            student_id = appointment.get("Student ID", "N/A")
            
            tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
            tools_in_db = tools_in_db_df['Tool Name'].tolist()
            new_tools = [tool for tool in tools_to_add if tool not in tools_in_db]
            
            for tool in new_tools:
                insert_query = """
                INSERT INTO requested_tools (student_id, appointment_id, student_name, tool_name)
                VALUES (%s, %s, %s, %s)
                """
                values = (student_id, appointment_id, student_name, tool)
                cursor.execute(insert_query, values)
        db.commit()
        st.success("selected tools added to seleced appointments!")
    except mysql.connector.Error as err:
        st.error(f"Error inserting tools: {err}")
    finally:
        cursor.close()

def fetch_requested_tools_df(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT id, student_id, appointment_id, student_name, tool_name, tool_status FROM requested_tools
    WHERE appointment_id = %s"""
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    tools_df = pd.DataFrame(result, columns=['ID', 'Student ID', 'Appointment ID', 'Student Name', 'Tool Name', 'Status'])
    cursor.close()
    return tools_df


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


def check_tool_duplicate(db, appointment_id, tool_to_check):
    cursor = db.cursor()
    check_query = """
    SELECT COUNT(*) FROM requested_tools
    WHERE appointment_id = %s AND tool_name = %s"""
    cursor.execute(check_query, (appointment_id, tool_to_check))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0  # Returns True if tool exists, False otherwise
def insert_requested_tools(db, appointment_data, tools_to_add):
    cursor = db.cursor()
    try:
        for appointment in appointment_data:
            student_name = appointment.get("Student Name", "N/A")
            appointment_id = appointment.get("Appointment ID", "N/A")
            student_id = appointment.get("Student ID", "N/A")
            
            tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
            tools_in_db = tools_in_db_df['Tool Name'].tolist()
            new_tools = [tool for tool in tools_to_add if tool not in tools_in_db]
            tools_added = False

            for tool in new_tools:
                if check_tool_duplicate(db, appointment_id, tool):
                    st.warning(f"The tool '{tool}' already exists for Appointment {appointment_id}.")
                else:
                    insert_query = """
                    INSERT INTO requested_tools (student_id, appointment_id, student_name, tool_name)
                    VALUES (%s, %s, %s, %s)
                    """
                    values = (student_id, appointment_id, student_name, tool)
                    cursor.execute(insert_query, values)
                    tools_added = True 
            if tools_added:
                db.commit()
                st.success("Selected tools added to selected appointments!")
            else:
                st.info("No new tools were added (all tools were already assigned).")
    except mysql.connector.Error as err:
        st.error(f"Error inserting tools: {err}")
    finally:
        cursor.close()







def main():
    db = create_connection()
    create_requested_tools_table(db)
    if "selected_appointment" in st.session_state and st.session_state.selected_appointment:
        appointment_data = st.session_state.selected_appointment
        if isinstance(appointment_data, list) and appointment_data:
            tools = ['PHQ-9', 'GAD-7', 'SRQ', 'BDI', 'CAGE', 'SAD PERSONS SCALE']
            col1, col2 = st.columns([3, 1])
            selected_tools_add = col1.multiselect('SELECT TOOL TO ADMINISTER', tools)
            # selected_tools_remove = col2.multiselect('REMOVE TOOL', tools)
            with col1:
                if col2.button(f'Add {selected_tools_add} '):
                    insert_requested_tools(db, appointment_data, selected_tools_add)
            for appointment in appointment_data:
                appointment_id = appointment.get('Appointment ID', 'N/A')
                tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
                tools_in_db = tools_in_db_df['Tool Name'].tolist()

                with col2.expander(f"REMOVE", expanded=True):
                    if tools_in_db:
                        tool_to_remove = st.selectbox(
                            f"Select a Tool to Remove for Appointment {appointment_id}", 
                            tools_in_db, 
                            key=f"remove_tool_{appointment_id}"
                        )

                        if st.button(f"Remove {tool_to_remove} from Appointment {appointment_id}"):
                            remove_requested_tool(db, appointment_id, tool_to_remove)
                            tools_in_db_df = fetch_requested_tools_df(db, appointment_id)
                            tools_in_db = tools_in_db_df['Tool Name'].tolist()
                            st.success(f"The tool '{tool_to_remove}' has been removed from Appointment {appointment_id}.")

            with st.expander("Tools in Database", expanded=True):
                all_tools_df = pd.concat([fetch_requested_tools_df(db, appointment.get("Appointment ID", "N/A")) for appointment in appointment_data], ignore_index=True)
                st.dataframe(all_tools_df)
        else:
            st.error("Appointment data is not in the expected format.")
    else:
        st.error('No appointment selected. Please select an appointment.')
    db.close()

if __name__ == '__main__':
    main()




