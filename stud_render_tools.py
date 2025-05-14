import streamlit as st
# import mysql.connector
import pandas as pd
from datetime import datetime
import sqlite3
import pandas as pd
import streamlit as st

def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None


# def create_requested_tools_students_table(db):
#     cursor = db.cursor()
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS requested_tools_students(
#         appointment_id TEXT,
#         student_id TEXT,
#         tool_name TEXT,
#         requested_date DATETIME DEFAULT CURRENT_TIMESTAMP,
#         tool_status TEXT DEFAULT 'Pending',
#         PRIMARY KEY (appointment_id, student_id, tool_name)
#     )
#     """
#     cursor.execute(create_table_query)
#     db.commit()
#     cursor.close()


def insert_requested_tools_students(db, student_id, appointment_id, tools_to_add):
    cursor = db.cursor()
    for tool in tools_to_add:
        insert_query = """
        INSERT INTO requested_tools_students (student_id, appointment_id, tool_name)
        VALUES (?, ?, ?)
        """
        values = (student_id, appointment_id, tool)
        try:
            cursor.execute(insert_query, values)
        except sqlite3.IntegrityError:
            st.warning(f"Tool '{tool}' already requested for this appointment.")
    db.commit()
    cursor.close()


def fetch_requested_tools_df(db, student_id, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT student_id, appointment_id, tool_name, tool_status 
    FROM requested_tools_students WHERE student_id = ? AND appointment_id = ?
    """
    cursor.execute(fetch_query, (student_id, appointment_id))
    result = cursor.fetchall()
    tools_df = pd.DataFrame(result, columns=['Student ID', 'Appointment ID', 'Tool Name', 'Status'])
    cursor.close()
    return tools_df


def remove_requested_tool(db, student_id, appointment_id, tool_to_remove):
    cursor = db.cursor()
    delete_query = """
    DELETE FROM requested_tools_students 
    WHERE student_id = ? AND appointment_id = ? AND tool_name = ?
    """
    cursor.execute(delete_query, (student_id, appointment_id, tool_to_remove))
    db.commit()
    cursor.close()
    st.success(f"The tool '{tool_to_remove}' was successfully removed.")


def fetch_appointments_for_student_and_id(db, student_id, appointment_id):
    query = """
        SELECT * 
        FROM screen_appointments
        WHERE student_id = ? AND appointment_id = ?
    """
    cursor = db.cursor()
    cursor.execute(query, (student_id, appointment_id))
    appointments = cursor.fetchall()
    cursor.close()
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


# def fetch_appointments_students(db, search_input, selected_term=None, selected_screen_type=None):
#     cursor = db.cursor()
#     params = []

#     if search_input.strip().upper().startswith("SCREEN-") or search_input.isdigit():
#         query = """
#         SELECT id, student_id, name, appointment_id, appointment_date, appointment_time, appointment_type, term, screen_type, clinician_name
#         FROM screen_appointments
#         WHERE appointment_id = ?
#         ORDER BY appointment_date DESC, appointment_time DESC
#         """
#         params = (search_input.strip(),)
#     else:
#         name_parts = search_input.strip().split()
#         query_conditions = []
#         if len(name_parts) == 2:
#             first_name, last_name = name_parts
#             query_conditions.append("name LIKE ?")
#             query_conditions.append("name LIKE ?")
#             params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
#         else:
#             query_conditions.append("name LIKE ?")
#             params.append(f"%{search_input}%")
#         if selected_term:
#             query_conditions.append("term = ?")
#             params.append(selected_term)
#         if selected_screen_type:
#             query_conditions.append("screen_type = ?")
#             params.append(selected_screen_type)
#         query = f"""
#         SELECT id, student_id, name, appointment_id, appointment_date, appointment_time, appointment_type, term, screen_type, clinician_name
#         FROM screen_appointments
#         WHERE {" AND ".join(query_conditions)}
#         ORDER BY appointment_date DESC, appointment_time DESC
#         """
#     cursor.execute(query, tuple(params))
#     appointments = [dict(row) for row in cursor.fetchall()]
#     return appointments


def fetch_requested_tools_for_student(db, student_id):
    try:
        cursor = db.cursor()
        fetch_query = """
        SELECT 
            a.appointment_id, 
            su.student_id, 
            su.name AS student_name, 
            su.student_class, 
            su.stream, 
            a.term,
            a.screen_type,
            rt.tool_name, 
            rt.tool_status 
        FROM 
            requested_tools_students rt
        JOIN 
            screen_appointments a ON rt.appointment_id = a.appointment_id
        JOIN 
            student_users su ON a.student_id = su.student_id
        WHERE 
            su.student_id = ?
        """
        cursor.execute(fetch_query, (student_id,))
        result = cursor.fetchall()
        tools_df = pd.DataFrame(result, columns=[
            'appointment_id', 'student_id', 'student_name', 'student_class', 'stream',
            'term', 'screen_type', 'tool_name', 'tool_status'
        ])
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
    return tools_df


###### DRIVER CODE ######
def main():
    db = create_connection()
    # create_requested_tools_students_table(db)
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
    

    if 'student_id' in st.session_state:
        student_id = st.session_state.student_id

        if appointment_id:
            appointments = fetch_appointments_for_student_and_id(db, student_id, appointment_id)
            tools = ['PHQ-9', 'GAD-7', 'SRQ', 'BDI', 'CAGE', 'SAD PERSONS SCALE']
            tools_for_student_df = fetch_requested_tools_for_student(db, student_id)
            tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
            # st.write(tools_in_db_df)
            tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
            tools_for_student = dict(zip(tools_for_student_df['tool_name'], tools_for_student_df['tool_status']))
            col1, col2 = st.columns(2)
            
            with col1.form('tool_form'):
                selected_tools = st.multiselect('Render tool', tools)
                add = st.form_submit_button('Add')
                if add:
                    tools_to_add = []
                    blocked_tools = []
                    pre_screen_exists = any(
                        (row['student_id'] == student_id and row['appointment_id'] == appointment_id and  row['term'] == selected_term and row['screen_type'] == 'PRE-SCREEN')
                        for _, row in tools_for_student_df.iterrows())
                    for tool in selected_tools:
                        if tool in tools_in_appointment:
                            blocked_tools.append(f"{tool} (Already exists on {appointment_id})")
                        elif tool in tools_for_student and tools_for_student[tool] == "Pending":
                            blocked_tools.append(f"{tool} when it is still pending on previous appointment")
                        elif selected_screen_type == 'POST-SCREEN' and not pre_screen_exists:
                            blocked_tools.append(f"{tool} to POST-SCREEN without a PRE-SCREEN in this term for this student")
                        else:
                            tools_to_add.append(tool)
                    if blocked_tools:
                        st.warning(f"Can't add {', '.join(blocked_tools)}")
                    if tools_to_add:
                        insert_requested_tools_students(db, student_id, appointment_id, tools_to_add)
                        st.success(f"{tools_to_add} requested for {appointment_id} as a {selected_screen_type}")
                    tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
                    tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
            
            with st.expander(f'SCREEN HISTORY FOR - {student_id}', expanded=True):
                df = fetch_requested_tools_for_student(db, student_id)
                df.index = df.index + 1
                st.write(df[['student_class', 'term', 'screen_type', 'tool_name', 'tool_status']])
            
            with col2.form("remove_tool_form"):
                tools_in_db = tools_in_db_df['Tool Name'].tolist()
                if tools_in_db:
                    tool_to_remove = st.selectbox("Select a Tool to Remove", tools_in_db)
                    remove = st.form_submit_button("Remove Tool")
                    if remove:
                        remove_requested_tool(db, student_id, appointment_id, tool_to_remove)
                        tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
        
                    # else:
                    #     st.sidebar.warning(f"❌ No results found for filtered options for {search_input}.")
                # else:
                #     st.sidebar.warning(f"❌ No results found for {search_input}.")

    db.close()
if __name__ == "__main__":
    main()











