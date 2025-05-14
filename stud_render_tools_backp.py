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
        'database': 'kabs_db'
    }
    return mysql.connector.connect(**config)

def create_requested_tools_students_table(db):
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS requested_tools_students(
        appointment_id VARCHAR(50),
        student_id VARCHAR(50),
        -- name VARCHAR(255),
        tool_name VARCHAR(255),
        requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tool_status VARCHAR(50) DEFAULT 'Pending',
        PRIMARY KEY (appointment_id, student_id, tool_name) 
    )"""
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()

def insert_requested_tools_students(db, student_id, appointment_id, tools_to_add):
    cursor = db.cursor()
    for tool in tools_to_add:
        insert_query = """
        INSERT INTO requested_tools_students (student_id, appointment_id,  tool_name)
        VALUES (%s, %s, %s)
        """
        values = (student_id, appointment_id, tool)
        try:
            cursor.execute(insert_query, values)
        except mysql.connector.IntegrityError:
            st.warning(f"Tool '{tool}' already requested for this appointment.")
    db.commit()
    cursor.close()

def fetch_requested_tools_df(db, student_id, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT student_id, appointment_id, tool_name, tool_status 
    FROM requested_tools_students WHERE student_id = %s AND appointment_id = %s"""
    cursor.execute(fetch_query, (student_id, appointment_id))
    result = cursor.fetchall()
    tools_df = pd.DataFrame(result, columns=['Student ID', 'Appointment ID', 'Tool Name', 'Status'])
    cursor.close()
    return tools_df

def remove_requested_tool(db, student_id, appointment_id, tool_to_remove):
    cursor = db.cursor()
    delete_query = """
    DELETE FROM requested_tools_students WHERE student_id = %s AND appointment_id = %s AND tool_name = %s"""
    cursor.execute(delete_query, (student_id, appointment_id, tool_to_remove))
    db.commit()
    cursor.close()
    st.success(f"The tool '{tool_to_remove}' was successfully removed.")

def fetch_appointments_for_student_and_id(db, student_id, appointment_id):
    query = """
        SELECT * 
        FROM screen_appointments
        WHERE student_id = %s AND appointment_id = %s
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
    WHERE STUDENT_ID = %s
    """
    cursor.execute(query, (student_id,))
    return cursor.fetchone() 


def fetch_appointments_students(db, search_input, selected_term=None, selected_screen_type=None):
    cursor = db.cursor(dictionary=True)

    if search_input.strip().upper().startswith("SCREEN-") or search_input.isdigit():
        query = """
        SELECT id, student_id, name, appointment_id, appointment_date, appointment_time, appointment_type, term, screen_type, clinician_name
        FROM screen_appointments
        WHERE appointment_id = %s
        """
        params = (search_input.strip(),)
    else:
        name_parts = search_input.strip().split()
        query_conditions = []
        params = []

        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("name LIKE %s")
            query_conditions.append("name LIKE %s")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("name LIKE %s")
            params.append(f"%{search_input}%")
        if selected_term:
            query_conditions.append("term = %s")
            params.append(selected_term)
        if selected_screen_type:
            query_conditions.append("screen_type = %s")
            params.append(selected_screen_type)
        query = f"""
        SELECT id, student_id, name, appointment_id, appointment_date, appointment_time, appointment_type, term, screen_type, clinician_name
        FROM screen_appointments
        WHERE {" AND ".join(query_conditions)}
        """
    query += " ORDER BY appointment_date DESC, appointment_time DESC"  # Sort by most recent appointment
    cursor.execute(query, tuple(params))

    appointments = cursor.fetchall()
    return appointments

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
            su.student_id = %s
        """
        cursor.execute(fetch_query, (student_id,))
        result = cursor.fetchall()

        tools_df = pd.DataFrame(result, columns=['appointment_id', 'student_id', 'student_name', 'student_class', 'stream', 'term', 'screen_type', 'tool_name', 'tool_status'])
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame() 
    finally:
        cursor.close()
    return tools_df



### DRVER CODE #########
def main():
    db = create_connection()
    create_requested_tools_students_table(db)
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
    unsafe_allow_html=True
)

    st.sidebar.write(' ')
    with st.sidebar.expander("🔍Search student", expanded=True):
        search_input = st.text_input("", placeholder='Type your name and press enter')
    
    results = []
    selected_record = None
    if search_input.strip():
        results = fetch_appointments_students(db, search_input)
        if results:
            selected_record = results[0]
            term_list = ["1st-Term", "2nd-Term", "3rd-Term"]
            with st.sidebar.expander('FILTER OPTIONS', expanded=True):
                c1, c2 = st.columns([1, 1.5])
                screen_type_list = ["PRE-SCREEN", "POST-SCREEN", "CONSULT-SCREEN", 'ON-REQUEST']
                selected_term = c1.selectbox("TERM", term_list, index=term_list.index(selected_record['term']) if selected_record['term'] in term_list else 0)
                selected_screen_type = c2.selectbox("SCREEN TYPE", screen_type_list, index=screen_type_list.index(selected_record['screen_type']) if selected_record['screen_type'] in screen_type_list else 0)
            filtered_results = [r for r in results if r['term'] == selected_term and r['screen_type'] == selected_screen_type]
            
            if filtered_results:
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
                
                    with st.sidebar.expander("🔍SEARCH RESULTS", expanded=True):
                        st.markdown(record_display)
            
            st.session_state["appointment_id"] = selected_record["appointment_id"]
            st.session_state["student_id"] = selected_record["student_id"]
            st.session_state["name"] = selected_record["name"]
            student_id = st.session_state["student_id"]
            student_id = st.session_state["student_id"]
            appointment_id = st.session_state["appointment_id"]
            name = st.session_state["name"]
            student = fetch_student_by_id(db, student_id)
            if student:
                appointments = fetch_appointments_for_student_and_id(db, student_id, appointment_id)
                tools = ['PHQ-9', 'GAD-7', 'SRQ', 'BDI', 'CAGE', 'SAD PERSONS SCALE']
                tools_for_student_df = fetch_requested_tools_for_student(db, student_id)
                tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
                st.write(tools_in_db_df)
                tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
                tools_for_student = dict(zip(tools_for_student_df['tool_name'], tools_for_student_df['tool_status']))
                col1, col2 = st.columns(2)
                
                with col1.form('tool_form'):
                    selected_tools = st.multiselect('Render tool', tools)
                    add = st.form_submit_button('Add')
                    if add:
                        tools_to_add = []
                        blocked_tools = []
                        for tool in selected_tools:
                            if tool in tools_in_appointment:
                                blocked_tools.append(f"{tool} (Already exists in this appointment)")
                            elif tool in tools_for_student and tools_for_student[tool] == "Pending":
                                blocked_tools.append(f"{tool} (Pending in previous appointment)")
                            else:
                                tools_to_add.append(tool)
                        if blocked_tools:
                            st.error(f"The following tools cannot be added: {', '.join(blocked_tools)}")
                        if tools_to_add:
                            insert_requested_tools_students(db, student_id, appointment_id, tools_to_add)
                            st.success(f"{tools_to_add} requested")
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
                        else:
                            st.warning('No existing tools')
            
            else:
                st.sidebar.warning(f"❌ No results found for filtered options for {search_input}.")
        else:
            st.sidebar.warning(f"❌ No results found for {search_input}.")


    db.close()
if __name__ == "__main__":
    main()





### DRVER CODE #########
# def main():
#     db = create_connection()
#     create_requested_tools_students_table(db)
#     st.sidebar.markdown(
#     """
#     <style>
#         .appointment-header {
#             font-family: Haettenschweiler, sans-serif;
#             text-align: center;
#             color: #FFFFFF;
#             background-color: #007BFF;
#             padding: 5px;
#             border-radius: 5px;
#             font-size: 25px;
#         }
#     </style>
#     <div class='appointment-header'>APPOINTMENT DETAILS</div>
#     """,
#     unsafe_allow_html=True
# )

#     st.sidebar.write(' ')
#     with st.sidebar.expander("🔍Search student", expanded=True):
#         search_input = st.text_input("", placeholder='Type your name and press enter')
    
#     results = []
#     selected_record = None
#     if search_input.strip():
#         results = fetch_appointments_students(db, search_input)
#         if results:
#             selected_record = results[0]
#             term_list = ["1st-Term", "2nd-Term", "3rd-Term"]
#             with st.sidebar.expander('FILTER OPTIONS', expanded=True):
#                 c1, c2 = st.columns([1, 1.5])
#                 screen_type_list = ["PRE-SCREEN", "POST-SCREEN", "CONSULT-SCREEN", 'ON-REQUEST']
#                 selected_term = c1.selectbox("TERM", term_list, index=term_list.index(selected_record['term']) if selected_record['term'] in term_list else 0)
#                 selected_screen_type = c2.selectbox("SCREEN TYPE", screen_type_list, index=screen_type_list.index(selected_record['screen_type']) if selected_record['screen_type'] in screen_type_list else 0)
#             filtered_results = [r for r in results if r['term'] == selected_term and r['screen_type'] == selected_screen_type]
            
#             if filtered_results:
#                 for record in filtered_results:
                    
#                     record_display = f"""
#                                 - ***Student ID***: `{record['student_id']}`
#                                 - ***Name***: `{record['name']}`
#                                 - ***Appointment ID***: `{record['appointment_id']}`
#                                 - ***Appointment Date***: `{record['appointment_date']}`
#                                 - ***Appointment Type***: `{record['appointment_type']}`
#                                 - ***Term***: `{record['term']}`
#                                 - ***Screen Type***: `{record['screen_type']}`
#                                 - ***Clinician Name***: `{record['clinician_name']}`
#                                 """
                
#                     with st.sidebar.expander("🔍SEARCH RESULTS", expanded=True):
#                         st.markdown(record_display)
            
#                     st.session_state["appointment_id"] = record["appointment_id"]
#                     st.session_state["student_id"] = record["student_id"]
#                     st.session_state["name"] = record["name"]
                    
#                     student_id = st.session_state["student_id"]
#                     student_name = st.session_state["name"]
                    
#                     appointment_id = st.session_state["appointment_id"]
#                     # name = st.session_state["name"]
#                     student = fetch_student_by_id(db, student_id)
                    

#                 if student:
#                     appointments = fetch_appointments_for_student_and_id(db, student_id, appointment_id)
#                     tools = ['PHQ-9', 'GAD-7', 'SRQ', 'BDI', 'CAGE', 'SAD PERSONS SCALE']
#                     tools_for_student_df = fetch_requested_tools_for_student(db, student_id)
#                     tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
#                     st.write(tools_in_db_df)
#                     tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
#                     tools_for_student = dict(zip(tools_for_student_df['tool_name'], tools_for_student_df['tool_status']))
#                     col1, col2 = st.columns(2)
                    
#                     with col1.form('tool_form'):
#                         selected_tools = st.multiselect('Render tool', tools)
#                         add = st.form_submit_button('Add')
#                         if add:
#                             tools_to_add = []
#                             blocked_tools = []
#                             for tool in selected_tools:
#                                 if tool in tools_in_appointment:
#                                     blocked_tools.append(f"{tool} (Already exists in this appointment)")
#                                 elif tool in tools_for_student and tools_for_student[tool] == "Pending":
#                                     blocked_tools.append(f"{tool} (Pending in previous appointment)")
#                                 else:
#                                     tools_to_add.append(tool)
#                             if blocked_tools:
#                                 st.error(f"The following tools cannot be added: {', '.join(blocked_tools)}")
#                             if tools_to_add:
#                                 insert_requested_tools_students(db, student_id, appointment_id, tools_to_add)
#                                 st.success(f"{tools_to_add} requested")
#                             tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
#                             tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
                    
#                     with st.expander(f'SCREEN HISTORY FOR - {student_id}', expanded=True):
#                         df = fetch_requested_tools_for_student(db, student_id)
#                         df.index = df.index + 1
#                         st.write(df[['student_class', 'term', 'screen_type', 'tool_name', 'tool_status']])
                    
#                     with col2.form("remove_tool_form"):
#                         tools_in_db = tools_in_db_df['Tool Name'].tolist()
#                         if tools_in_db:
#                             tool_to_remove = st.selectbox("Select a Tool to Remove", tools_in_db)
#                             remove = st.form_submit_button("Remove Tool")
#                             if remove:
#                                 remove_requested_tool(db, student_id, appointment_id, tool_to_remove)
#                                 tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
                
#                 else:
#                     st.sidebar.warning(f"❌ No results found for filtered options for {search_input}.")
#             else:
#                 st.sidebar.warning(f"❌ No results found for {search_input}.")


#     db.close()
# if __name__ == "__main__":
#     main()






# def main():
#     db = create_connection()
#     create_requested_tools_students_table(db)
#     st.sidebar.markdown(
#     """
#     <style>
#         .appointment-header {
#             font-family: Haettenschweiler, sans-serif;
#             text-align: center;
#             color: #FFFFFF;
#             background-color: #007BFF;
#             padding: 5px;
#             border-radius: 5px;
#             font-size: 25px;
#         }
#     </style>
#     <div class='appointment-header'>APPOINTMENT DETAILS</div>
#     """,
#     unsafe_allow_html=True
# )

#     st.sidebar.write(' ')
#     with st.sidebar.expander("🔍Search student", expanded=True):
#         search_input = st.text_input("", placeholder='Type your name and press enter')
    
#     results = []
#     selected_record = None
#     if search_input.strip():
#         results = fetch_appointments_students(db, search_input)
#         if results:
#             selected_record = results[0]
#             term_list = ["1st-Term", "2nd-Term", "3rd-Term"]
#             with st.sidebar.expander('FILTER OPTIONS', expanded=True):
#                 c1, c2 = st.columns([1, 1.5])
#                 screen_type_list = ["PRE-SCREEN", "POST-SCREEN", "CONSULT-SCREEN", 'ON-REQUEST']
#                 selected_term = c1.selectbox("TERM", term_list, index=term_list.index(selected_record['term']) if selected_record['term'] in term_list else 0)
#                 selected_screen_type = c2.selectbox("SCREEN TYPE", screen_type_list, index=screen_type_list.index(selected_record['screen_type']) if selected_record['screen_type'] in screen_type_list else 0)
#             filtered_results = [r for r in results if r['term'] == selected_term and r['screen_type'] == selected_screen_type]
            
#             if filtered_results:
#                 for record in filtered_results:
                    
#                     record_display = f"""
#                                 - ***Student ID***: `{record['student_id']}`
#                                 - ***Name***: `{record['name']}`
#                                 - ***Appointment ID***: `{record['appointment_id']}`
#                                 - ***Appointment Date***: `{record['appointment_date']}`
#                                 - ***Appointment Type***: `{record['appointment_type']}`
#                                 - ***Term***: `{record['term']}`
#                                 - ***Screen Type***: `{record['screen_type']}`
#                                 - ***Clinician Name***: `{record['clinician_name']}`
#                                 """
                
#                     with st.sidebar.expander("🔍SEARCH RESULTS", expanded=True):
#                         st.markdown(record_display)
                
#                     st.session_state["appointment_id"] = record["appointment_id"]
#                     st.session_state["student_id"] = record["student_id"]
#                     st.session_state["name"] = record["name"]
                    
#                     student_id = st.session_state["student_id"]
#                     student_name = st.session_state["name"]
                    
#                     appointment_id = st.session_state["appointment_id"]
#                     student = fetch_student_by_id(db, student_id)
                    

#                     if student:
#                         appointments = fetch_appointments_for_student_and_id(db, student_id, appointment_id)
#                         tools = ['PHQ-9', 'GAD-7', 'SRQ', 'BDI', 'CAGE', 'SAD PERSONS SCALE']
#                         tools_for_student_df = fetch_requested_tools_for_student(db, student_id)
#                         tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
#                         st.write(tools_in_db_df)
#                         tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
#                         tools_for_student = dict(zip(tools_for_student_df['tool_name'], tools_for_student_df['tool_status']))
#                         col1, col2 = st.columns(2)
                        
#                         with col1.form('tool_form'):
#                             selected_tools = st.multiselect('Render tool', tools)
#                             add = st.form_submit_button('Add')
#                             if add:
#                                 tools_to_add = []
#                                 blocked_tools = []
#                                 pre_screen_exists = any(
#                                     (row['term'] == selected_term and row['screen_type'] == 'PRE-SCREEN')
#                                     for _, row in tools_for_student_df.iterrows()
#                                 )
#                                 for tool in selected_tools:
#                                     if tool in tools_in_appointment:
#                                         blocked_tools.append(f"{tool} (Already exists in this appointment)")
#                                     elif tool in tools_for_student and tools_for_student[tool] == "Pending":
#                                         blocked_tools.append(f"{tool} (Pending in previous appointment)")
#                                     elif selected_screen_type == 'POST-SCREEN' and not pre_screen_exists:
#                                         blocked_tools.append(f"{tool} (Cannot add to POST-SCREEN without a PRE-SCREEN in this term)")
#                                     else:
#                                         tools_to_add.append(tool)
#                                 if blocked_tools:
#                                     st.error(f"The following tools cannot be added: {', '.join(blocked_tools)}")
#                                 if tools_to_add:
#                                     insert_requested_tools_students(db, student_id, appointment_id, tools_to_add)
#                                     st.success(f"{tools_to_add} requested")
#                                 tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
#                                 tools_in_appointment = dict(zip(tools_in_db_df['Tool Name'], tools_in_db_df['Status']))
                        
                        
#                         with st.expander(f'SCREEN HISTORY FOR - {student_id}', expanded=True):
#                             df = fetch_requested_tools_for_student(db, student_id)
#                             df.index = df.index + 1
#                             st.write(df[['student_class', 'term', 'screen_type', 'tool_name', 'tool_status']])
                        
#                         with col2.form("remove_tool_form"):
#                             tools_in_db = tools_in_db_df['Tool Name'].tolist()
#                             if tools_in_db:
#                                 tool_to_remove = st.selectbox("Select a Tool to Remove", tools_in_db)
#                                 remove = st.form_submit_button("Remove Tool")
#                                 if remove:
#                                     remove_requested_tool(db, student_id, appointment_id, tool_to_remove)
#                                     tools_in_db_df = fetch_requested_tools_df(db, student_id, appointment_id)
                    
#                     else:
#                         st.sidebar.warning(f"❌ No results found for filtered options for {search_input}.")
#             else:
#                 st.sidebar.warning(f"❌ No results found for {search_input}.")

#     db.close()
# if __name__ == "__main__":
#     main()


