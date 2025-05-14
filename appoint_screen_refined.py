import streamlit as st
import mysql.connector
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
from datetime import datetime
import plotly.express as px
import share_tools
import assessments
import stud_render_tools
import pandas as pd
import mysql.connector
import tempfile
import io
from fpdf import FPDF



# def create_connection():
#     try:
#         conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
#         conn.row_factory = sqlite3.Row
#         return conn
#     except sqlite3.Error as e:
#         st.error(f"Error connecting to SQLite: {e}")
#         return None
# def generate_appointment_id(db):
#     cursor = db.cursor()
#     cursor.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM screen_appointments")
#     next_id = cursor.fetchone()[0]
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     new_id = f"SCREEN-{current_date}-{next_id:04}"
#     return new_id

# def create_screen_appointments_table(db):
#     cursor = db.cursor()
#     create_screen_appointments_table_query = """
#     CREATE TABLE IF NOT EXISTS screen_appointments (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     appointment_id VARCHAR(30) UNIQUE,
#     student_id VARCHAR(20),
#     name VARCHAR(255),
#     username VARCHAR(50),
#     appointment_type VARCHAR(255) DEFAULT 'NEW',
#     term VARCHAR(255),
#     screen_type VARCHAR(255),
#     appointment_date DATE,
#     appointment_time TIME,
#     clinician_name VARCHAR(255),
#     reason TEXT,
#     FOREIGN KEY (student_id) REFERENCES student_users(STUDENT_ID))
# """
#     cursor.execute(create_screen_appointments_table_query)
#     db.commit()


# def determine_appointment_type(db, student_id):
#     cursor = db.cursor()
#     query = """
#     SELECT COUNT(*) FROM screen_appointments WHERE student_id = %s
#     """
#     cursor.execute(query, (student_id,))
#     count = cursor.fetchone()[0]
#     return "NEW" if count == 0 else "REVISIT"


# clinicians = ['','Lilian','Shana','Geofry']
# appointment_reasons = ['','Assessemnt','Group session','Indiviual therapy','Family therapy']
# st.session_state["appointment_reasons"] = appointment_reasons


# def fetch_students(db, search_input):
#     cursor = db.cursor(dictionary=True)
#     if search_input.strip().upper().startswith("STUD-") or search_input.isdigit():
#         query = """
#         SELECT student_id, name, age, gender, student_class, stream, username, email, contact
#         FROM student_users
#         WHERE student_id = %s
#         """
#         cursor.execute(query, (search_input.strip(),))
#     else: 
#         name_parts = search_input.strip().split()
#         query_conditions = []
#         params = []

#         if len(name_parts) == 2:
#             first_name, last_name = name_parts
#             query_conditions.append("name LIKE %s")
#             query_conditions.append("name LIKE %s")
#             params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
#         else:
#             query_conditions.append("name LIKE %s")
#             params.append(f"%{search_input}%")
#         query = f"""
#         SELECT student_id, name, age, gender, student_class, stream, username, email, contact
#         FROM student_users
#         WHERE {" OR ".join(query_conditions)}
#         """
#         cursor.execute(query, tuple(params))
#     return cursor.fetchall()


# def fetch_all_requested_tools_with_student_info(db):
#     try:
#         cursor = db.cursor()
#         fetch_query = """
#         SELECT 
#             a.appointment_id, 
#             su.student_id, 
#             su.name AS student_name, 
#             su.student_class, 
#             su.stream, 
#             a.term,
#             a.screen_type,
#             rt.tool_name, 
#             rt.tool_status 
#         FROM 
#             requested_tools_students rt
#         JOIN 
#             screen_appointments a ON rt.appointment_id = a.appointment_id
#         JOIN 
#             student_users su ON a.student_id = su.student_id
#         """
#         cursor.execute(fetch_query)
#         result = cursor.fetchall()
    
#         tools_df = pd.DataFrame(result, columns=['appointment_id', 'student_id', 'student_name', 'student_class', 'stream', 'term','screen_type','tool_name', 'tool_status'])
#     except mysql.connector.Error as e:
#         print(f"Database error: {e}")
#         return pd.DataFrame() 
#     finally:
#         cursor.close()
#     return tools_df

# def fetch_column_values(db, column):
#     cursor = db.cursor()
#     cursor.execute(f"SELECT DISTINCT {column} FROM student_users")
#     return [row[0] for row in cursor.fetchall()]




# def check_screen_conditions(db, student_id, name, term, screen_type):
#     cursor = db.cursor()
#     valid_screen_types = ['PRE-SCREEN', 'POST-SCREEN', 'CONSULT-SCREEN', 'ON-REQUEST']
    
#     if screen_type not in valid_screen_types:
#         st.warning(f"Invalid screen type: {screen_type}")
#         return False

#     cursor.execute("""
#     SELECT screen_type, appointment_date 
#     FROM screen_appointments 
#     WHERE student_id = %s AND term = %s
#     """, (student_id, term))
    
#     existing_appointments = cursor.fetchall()
#     pre_screen_found = False
#     post_screen_found = False
#     for appointment in existing_appointments:
#         existing_screen_type, existing_date = appointment
#         if existing_screen_type == 'PRE-SCREEN':
#             pre_screen_found = True
#         elif existing_screen_type == 'POST-SCREEN':
#             post_screen_found = True
#         if pre_screen_found and post_screen_found:
#             st.warning(f"{name} already has both PRE-SCREEN and POST-SCREEN for this {term}.")
#             return False

#     if screen_type == 'PRE-SCREEN':
#         if pre_screen_found:
#             st.warning(f"{name} already has a pre-screen appointment in this {term}.")
#             return False
#     elif screen_type == 'POST-SCREEN':
#         if not pre_screen_found:
#             st.warning(f"Post screen cannot occur before pre-screen in this {term}.")
#             return False
#         if post_screen_found:
#             st.warning(f"{name} already has a post-screen appointment in {term}.")
#             return False
#     return True


# def insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason, screen_type, term):
#     cursor = db.cursor()
#     cursor.execute("SELECT name FROM student_users WHERE STUDENT_ID = %s", (student_id,))
#     user_data = cursor.fetchone()
#     if not user_data:
#         st.warning("Student not found.")
#         return
#     name = user_data[0]
#     if not check_screen_conditions(db, student_id, name, term, screen_type):
#         return  
#     appointment_time_str = appointment_time.strftime("%H:%M:%S")
#     appointment_date_str = appointment_date.strftime("%Y-%m-%d")
#     insert_appointment_query = """
#     INSERT INTO screen_appointments (appointment_id, student_id, name, username, appointment_type, term, screen_type, appointment_date, appointment_time, clinician_name, reason)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#     cursor.execute("SELECT username FROM student_users WHERE STUDENT_ID = %s", (student_id,))
#     username = cursor.fetchone()[0]
#     appointment_data = (generate_appointment_id(db), student_id, name, username, appointment_type, term, screen_type, appointment_date_str, appointment_time_str, clinician_name, reason)
#     try:
#         cursor.execute(insert_appointment_query, appointment_data)
#         db.commit()
#         st.success(f"{name} for {reason} by {clinician_name} scheduled successfully.")
#     except mysql.connector.Error as err:
#         st.error(f"Error: {err}")
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd

def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

def generate_appointment_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM screen_appointments")
    next_id = cursor.fetchone()[0]
    current_date = datetime.now().strftime("%Y-%m-%d")
    new_id = f"SCREEN-{current_date}-{next_id:04}"
    return new_id

def create_screen_appointments_table(db):
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS screen_appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id TEXT UNIQUE,
        student_id TEXT,
        name TEXT,
        username TEXT,
        appointment_type TEXT DEFAULT 'NEW',
        term TEXT,
        screen_type TEXT,
        appointment_date TEXT,
        appointment_time TEXT,
        clinician_name TEXT,
        reason TEXT
    );
    """
    cursor.execute(create_table_query)
    db.commit()

def determine_appointment_type(db, student_id):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM screen_appointments WHERE student_id = ?", (student_id,))
    count = cursor.fetchone()[0]
    return "NEW" if count == 0 else "REVISIT"

clinicians = ['','Lilian','Shana','Geofry']
appointment_reasons = ['','Assessemnt','Group session','Indiviual therapy','Family therapy']
st.session_state["appointment_reasons"] = appointment_reasons

def fetch_students(db, search_input):
    cursor = db.cursor()
    search_input = search_input.strip()
    if search_input.upper().startswith("STUD-") or search_input.isdigit():
        cursor.execute("""
            SELECT student_id, name, age, gender, student_class, stream, username, email, contact
            FROM student_users WHERE student_id = ?
        """, (search_input,))
    else:
        name_parts = search_input.split()
        if len(name_parts) == 2:
            first_name, last_name = name_parts
            cursor.execute("""
                SELECT student_id, name, age, gender, student_class, stream, username, email, contact
                FROM student_users
                WHERE name LIKE ? OR name LIKE ?
            """, (f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"))
        else:
            cursor.execute("""
                SELECT student_id, name, age, gender, student_class, stream, username, email, contact
                FROM student_users
                WHERE name LIKE ?
            """, (f"%{search_input}%",))
    return [dict(row) for row in cursor.fetchall()]

def fetch_all_requested_tools_with_student_info(db):
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                a.appointment_id, 
                su.student_id, 
                su.name, 
                su.student_class, 
                su.stream, 
                a.term,
                a.screen_type,
                rt.tool_name, 
                rt.tool_status 
            FROM requested_tools_students rt
            JOIN screen_appointments a ON rt.appointment_id = a.appointment_id
            JOIN student_users su ON a.student_id = su.student_id
        """)
        result = cursor.fetchall()
        return pd.DataFrame(result, columns=[
            'appointment_id', 'student_id', 'student_name', 'student_class',
            'stream', 'term', 'screen_type', 'tool_name', 'tool_status'
        ])
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def fetch_column_values(db, column):
    cursor = db.cursor()
    cursor.execute(f"SELECT DISTINCT {column} FROM student_users")
    return [row[0] for row in cursor.fetchall()]

def check_screen_conditions(db, student_id, name, term, screen_type):
    cursor = db.cursor()
    valid_screen_types = ['PRE-SCREEN', 'POST-SCREEN', 'CONSULT-SCREEN', 'ON-REQUEST']
    
    if screen_type not in valid_screen_types:
        st.warning(f"Invalid screen type: {screen_type}")
        return False

    cursor.execute("""
        SELECT screen_type, appointment_date 
        FROM screen_appointments 
        WHERE student_id = ? AND term = ?
    """, (student_id, term))
    
    pre_screen_found = post_screen_found = False
    for row in cursor.fetchall():
        existing_screen_type = row[0]
        if existing_screen_type == 'PRE-SCREEN':
            pre_screen_found = True
        elif existing_screen_type == 'POST-SCREEN':
            post_screen_found = True
        if pre_screen_found and post_screen_found:
            st.warning(f"{name} already has both PRE-SCREEN and POST-SCREEN for this {term}.")
            return False

    if screen_type == 'PRE-SCREEN' and pre_screen_found:
        st.warning(f"{name} already has a pre-screen appointment in this {term}.")
        return False
    elif screen_type == 'POST-SCREEN':
        if not pre_screen_found:
            st.warning(f"Post screen cannot occur before pre-screen in this {term}.")
            return False
        if post_screen_found:
            st.warning(f"{name} already has a post-screen appointment in {term}.")
            return False

    return True

def insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason, screen_type, term):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM student_users WHERE student_id = ?", (student_id,))
    user_data = cursor.fetchone()
    if not user_data:
        st.warning("Student not found.")
        return

    name = user_data[0]
    if not check_screen_conditions(db, student_id, name, term, screen_type):
        return

    cursor.execute("SELECT username FROM student_users WHERE student_id = ?", (student_id,))
    username = cursor.fetchone()[0]

    appointment_data = (
        generate_appointment_id(db),
        student_id,
        name,
        username,
        appointment_type,
        term,
        screen_type,
        appointment_date.strftime("%Y-%m-%d"),
        appointment_time.strftime("%H:%M:%S"),
        clinician_name,
        reason
    )

    insert_query = """
        INSERT INTO screen_appointments (
            appointment_id, student_id, name, username, appointment_type,
            term, screen_type, appointment_date, appointment_time, clinician_name, reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        cursor.execute(insert_query, appointment_data)
        db.commit()
        st.success(f"{name} for {reason} by {clinician_name} scheduled successfully.")
    except sqlite3.Error as err:
        st.error(f"Error: {err}")



#### FILTER FUNCTION ######
def filter_requested_tools(data):
    if data.empty:
        st.warning("No data available.")
        return data
    with st.sidebar:
        st.header("FILTER OPTIONS")
        student_class_filter = st.multiselect("STUDENT CLASS", data["student_class"].unique())
        stream_filter = st.multiselect("STREAM", data["stream"].unique())
        tool_name_filter = st.multiselect("SCREENING TOOL", data["tool_name"].unique())
        tool_status_filter = st.multiselect("TOOL STATUS", data["tool_status"].unique())
        available_columns = list(data.columns)
        selected_columns = st.multiselect("COLUMNS TO DISPLAY", available_columns, default=available_columns)
    filtered_data = data.copy()
    if student_class_filter:
        filtered_data = filtered_data[filtered_data["student_class"].isin(student_class_filter)]
    if stream_filter:
        filtered_data = filtered_data[filtered_data["stream"].isin(stream_filter)]
    if tool_name_filter:
        filtered_data = filtered_data[filtered_data["tool_name"].isin(tool_name_filter)]
    if tool_status_filter:
        filtered_data = filtered_data[filtered_data["tool_status"].isin(tool_status_filter)]

    filtered_data = filtered_data[selected_columns]
    filtered_data.index = filtered_data.index + 1
    def color_tool_status(val):
        color = "green" if val.lower() == "completed" else "orange"
        return f'background-color: {color}; color: white; font-weight: bold;'
    if "tool_status" in filtered_data.columns:
        styled_data = filtered_data.style.applymap(color_tool_status, subset=["tool_status"])
        st.write(f'Filtered students: {len(filtered_data)}')
    else:
        st.table(filtered_data)
    def style_table(df):
        styles = [
            dict(selector="thead th", props=[("background-color", "#ADD8E6"), ("color", "black"), ("font-weight", "bold"), ("text-align", "center")]),  # Light blue headers
            dict(selector="tbody td", props=[("text-align", "center")]),  # Centered text
        ]
        return df.style.set_table_styles(styles).applymap(color_tool_status, subset=["tool_status"])
    csv = filtered_data.to_csv(index=True).encode("utf-8")
    st.download_button(label="📥 Downlod results", data=csv, file_name="filtered_tools.csv", mime="text/csv")
    st.table(style_table(filtered_data))
    return filtered_data






#### DRVER CODE #########
def main():
    db = create_connection()
    create_screen_appointments_table(db)
    appoint_menu = option_menu(
        menu_title='',
        orientation='horizontal',
        menu_icon='',
        options=['Schedule Screening', 'Render_Screening Tools', 'Screening Status'],
        icons=['calendar-plus', 'book', 'hourglass-split'],
        styles={
            "container": {"padding": "10!important", "background-color": 'black', 'border': '0.01px dotted red'},
            "icon": {"color": "red", "font-size": "14px"},
            "nav-link": {"color": "#d7c4c1", "font-size": "14px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
            "nav-link-selected": {"background-color": "green"},
        },
        key="register_menu"
    )
    if appoint_menu == 'Schedule Screening':
        with st.sidebar.expander('SCREENING SCHEDLE', expanded=True):
            schedule_option = st.selectbox("Select:", ['One Student', 'Custom Schedule'])
        st.sidebar.write('')
        if schedule_option == 'One Student':
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
                <div class='appointment-header'>STUDENT RECORD </div>
                """,
                unsafe_allow_html=True
            )
            st.sidebar.write('')
            with st.sidebar.expander("🔍 SEARCH", expanded=True):
                search_input = st.text_input("Enter Name or Student ID", "")
            results = fetch_students(db, search_input) if search_input.strip() else []
            selected_record = None
            if results:
                st.sidebar.write(f"**{len(results)} result(s) found**")
                options = {f"{r['name']} - {r['student_id']}": r for r in results}
                selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
                selected_record = options[selected_option]
            if selected_record:
                with st.sidebar.expander("📄 STUDENT DETAILS", expanded=True):
                    for key, value in selected_record.items():
                        st.write(f"{key.replace('_', ' ').title()}: {value}") 
                st.session_state.update(selected_record)
                student_id = selected_record['student_id']
                student_name = selected_record['name']
                with st.form("Vender"):
                    appointment_type = determine_appointment_type(db, student_id)
                    st.write(f"APPOINTMENT TYPE: {appointment_type}")
                    appointment_date = st.date_input("APPOINTMENT DATE:", key="appointment_date")
                    appointment_time = st.time_input("APPOINTMENT TIME", key="appointment_time")
                    clinician_name = st.selectbox("CLINICIAN:", clinicians)
                    reason = st.selectbox("REASON FOR APPOINTMENT:", appointment_reasons) 
                    term = st.selectbox('TERM', ['', '1st-Term', '2nd-Term', '3rd-Term']) 
                    screen_type = st.selectbox('SCREEN TYPE', ['', 'PRE-SCREEN', 'POST-SCREEN', 'CONSULT-SCREEN', 'ON-REQUEST'])  
                    submit = st.form_submit_button("Schedule Appointment")
                    if submit:
                        if not appointment_date or not appointment_time or not clinician_name or not reason or not screen_type or not term:
                            st.warning("Please fill in all the fields before submitting.")
                        else:
                            cursor = db.cursor()
                            cursor.execute("SELECT name FROM student_users WHERE STUDENT_ID = %s", (student_id,))
                            user_data = cursor.fetchone()
                            if not user_data:
                                st.warning("Student not found.")
                            else:
                                name = user_data[0]
                                if not check_screen_conditions(db, student_id, name, term, screen_type):
                                    return 
                                insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason, screen_type, term)
    
        









        elif schedule_option == 'Custom Schedule':
            st.sidebar.subheader("📅 Custom Scheduling")
            filter_columns = ['student_class', 'stream', 'gender']
            selected_filters = st.sidebar.multiselect("Filter students by:", filter_columns)
            if selected_filters:
                query = "SELECT * FROM student_users WHERE " + " AND ".join([f"{col} = %s" for col in selected_filters])
                filter_values = [st.sidebar.selectbox(f"Select {col.title()}", list(set(fetch_column_values(db, col)))) for col in selected_filters]
            else:
                query = "SELECT * FROM student_users"
                filter_values = []
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, filter_values if selected_filters else [])
            filtered_students = cursor.fetchall()
            if filtered_students:
                df = pd.DataFrame(filtered_students, columns=['student_id', 'name', 'gender', 'student_class', 'stream'])
                df.index = df.index + 1
                with st.expander(f":red[{len(filtered_students)}] selected student(s)", expanded=True):
                    st.write(df)
                with st.form("Schedule Appointments"):
                    appointment_date = st.date_input("APPOINTMENT DATE:")
                    appointment_time = st.time_input("APPOINTMENT TIME")
                    term = st.selectbox('TERM', ['', '1st-Term', '2nd-Term', '3rd-Term'])
                    screen_type = st.selectbox('SCREEN TYPE', ['', 'PRE-SCREEN', 'POST-SCREEN', 'CONSULT-SCREEN', 'ON-REQUEST'])
                    clinician_name = st.selectbox("CLINICIAN:", clinicians)
                    reason = st.selectbox("REASON FOR APPOINTMENT:", appointment_reasons)
                    submit = st.form_submit_button("Schedule Appointments")
                    if submit:
                        if not appointment_date or not appointment_time or not clinician_name or not reason:
                            st.warning("Please fill in all the fields before submitting.")
                        else:
                            for student in filtered_students:
                                student_id = student['student_id']
                                appointment_type = determine_appointment_type(db, student_id)
                                if not check_screen_conditions(db, student_id, student['name'], term, screen_type):
                                    continue 
                                else:
                                    insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason, screen_type, term)
                                    st.success(f"Appointment for {student['name']} scheduled successfully.")
            else:
                st.warning("No students found for the selected criteria.")






    elif appoint_menu == "Render_Screening Tools":
        stud_render_tools.main()
        # share_tools.main()
        # assessments.main()

    elif appoint_menu == "Screening Status":
        tool_df = fetch_all_requested_tools_with_student_info(db)

        
        if st.checkbox('All scheduled students'):
            tool_df.index = tool_df.index + 1
            st.write(f'No.OF Scheduled students: {len(tool_df)}')
            st.write(tool_df)

        if st.checkbox('Sorted Results'):
            filtered_data = filter_requested_tools(tool_df)
            if st.sidebar.checkbox('Graph View'):
                with st.expander("GRAPHICAL VIEW", expanded=True):
                    col1, col2 = st.columns([0.8, 3])
                    chart_type = col1.radio("Chart type", ["Bar Chart", "Pie Chart"])
                    if chart_type == "Bar Chart":
                        col2.info("Bar Chart Representation")
                        fig = px.bar(filtered_data, x="tool_name", color="tool_status",
                                     title="Tool Usage by Status", barmode="group")
                        col2.plotly_chart(fig, use_container_width=True)
                    elif chart_type == "Pie Chart":
                        col2.info("Pie Chart Representation")
                        fig = px.pie(filtered_data, names="tool_status", title="Tool Status Distribution")
                        col2.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()








