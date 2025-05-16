import streamlit as st
import json
import pandas as pd
import os
import importlib
from datetime import datetime
import phq9_qn
import gad7_qn
import bcrypt
import base64
from streamlit_card import card
import sqlite3
import bcrypt
from streamlit_option_menu import option_menu
import session_notes

st.markdown(
        """
        <style>
        .card-wrapper {
            margin-bottom: 0px; /* Tight vertical spacing */
        }
        .element-container:has(.stCard) {
            padding-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def set_background(image_path, width="500px", height="500px", border_color="orange", border_width="5px"):
    try:
        if not os.path.exists(image_path):
            st.error(f"Image file '{image_path}' not found.")
            return
        
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        st.markdown(f"""
        <style>
        .image-container {{
            width: {width};
            height: {height};
            background-image: url('data:image/jpeg;base64,{encoded_string}');
            background-size: cover;
            background-position: right;
            border: {border_width}{border_color};
            margin: 0 auto;
            border-radius : 100%;
            position: fixed;
            top: 0;
        }}
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="image-container"></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading background image: {e}")


def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

# #### UTILS ####
class_list = ['','S1', 'S2', 'S3', 'S4', 'S5', 'S6']
stream_list = ['',"EAST", "SOUTH", 'WEST', 'NORTH']
gender_list = ['','MALE','FEMALE']

tool_modules = {
    'PHQ-9': phq9_qn.main,
    'GAD-7':gad7_qn.main
}


def fetch_requested_tools(db, appointment_id):
    try:
        cursor = db.cursor()
        fetch_query = """
        SELECT tool_name, tool_status FROM requested_tools_students
        WHERE appointment_id = ?
        """
        cursor.execute(fetch_query, (appointment_id,))
        result = cursor.fetchall()
        tools_status = {row[0]: row[1] for row in result}
    except Exception as e:
        print(f"Database error: {e}")
        return {}
    finally:
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
    cursor.close()

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

def edit_student_record(db, student_id, new_age, new_class, new_stream, new_email, new_contact, new_password):
    cursor = db.cursor()
    hashed_password = None
    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    update_query = """
    UPDATE student_users
    SET age = ?, student_class = ?, stream = ?, email = ?, contact = ?
    """
    values = [new_age, new_class, new_stream, new_email, new_contact]
    if hashed_password:
        update_query += ", password = ?"
        values.append(hashed_password)
    update_query += " WHERE student_id = ?"
    values.append(student_id)
    cursor.execute(update_query, tuple(values))
    db.commit()
    cursor.close()

def fetch_student_by_username(db, username):
    cursor = db.cursor()
    select_student_query = """
    SELECT student_id, name, age, gender, student_class, stream, username, email, contact, password
    FROM student_users
    WHERE username = ?
    """
    cursor.execute(select_student_query, (username,))
    student = cursor.fetchone()
    cursor.close()
    return student

def edit_student(db):
    if 'edit_student' in st.session_state and st.session_state.edit_student:
        student = st.session_state.edit_student
        with st.form('Edit form'):
            c1,c2 = st.columns(2)
            new_age = c1.number_input("AGE (yrs)", value=student['age'], min_value=1, step=1)
            new_class = c1.selectbox("CLASS", class_list, index=class_list.index(student['student_class']))
            new_stream = c1.selectbox("STREAM", stream_list, index=stream_list.index(student['stream']))
            new_email = c2.text_input("Update Email (Optional)", value=student['email'])
            new_contact = c2.text_input("Update Contact (Optional)", value=student['contact'])
            new_password = c2.text_input("Change your Password (Optional)", placeholder='Leave blank to keep current password', type="password")
            update = st.form_submit_button('Update Profie')
            if update:
                edit_student_record(db, student['student_id'], new_age, new_class, new_stream, new_email, new_contact, new_password.strip() if new_password else None)
                st.session_state.edit_student.update({
                    'age': new_age,
                    'student_class': new_class,
                    'stream': new_stream,
                    'email': new_email,
                    'contact': new_contact
                })
                st.success("Student details updated successfully!")
                st.rerun()


def search_edit_and_update_student(db, username):
    if username:
        student = fetch_student_by_username(db, username)
        if student:
            student_dict = {
                'student_id': student[0],
                'name': student[1],
                'age': student[2],
                'gender': student[3],
                'student_class': student[4],
                'stream': student[5],
                'username': student[6],
                'email': student[7],
                'contact': student[8]
            }
            st.session_state.edit_student = student_dict
            edit_student(db)
        else:
            st.error("Student record not found in the database.")

def get_requested_tools(db, appointment_id):
    try:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        query = """
        SELECT tool_name, tool_status FROM requested_tools_students
        WHERE appointment_id = ?
        """
        cursor.execute(query, (appointment_id,))
        tools = cursor.fetchall()
        tools_dict = {tool['tool_name']: tool['tool_status'] for tool in tools}
    except Exception as e:
        print(f"Database error: {e}")
        return {}
    finally:
        cursor.close()
    return tools_dict

def create_functioning_responses_table():
    db = sqlite3.connect("mhpss_db.sqlite")
    cursor = db.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS functioning_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            difficulty_level TEXT NOT NULL CHECK(difficulty_level IN ('Not difficult at all', 'Somewhat difficult', 'Very difficult', 'Extremely difficult')),
            fnx_score INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    try:
        cursor.execute(create_table_query)
        db.commit()
        print("Table 'functioning_responses' created successfully!")
    except Exception as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        db.close()

def check_functioning_completed(db, appointment_id):
    cursor = db.cursor()
    query = "SELECT difficulty_level FROM functioning_responses WHERE appointment_id = ?"
    cursor.execute(query, (appointment_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

def insert_functioning_response(db, appointment_id, student_id, difficulty_level):
    cursor = db.cursor()

    difficulty_to_score = {
        "Extremely difficult": 1,
        "Very difficult": 2,
        "Somewhat difficult": 3,
        "Not difficult at all": 4
    }

    fnx_score = difficulty_to_score.get(difficulty_level)
    if fnx_score is None:
        st.error("Invalid difficulty level.")
        return False

    insert_query = """
    INSERT INTO functioning_responses (appointment_id, student_id, difficulty_level, fnx_score)
    VALUES (?, ?, ?, ?)
    """
    try:
        cursor.execute(insert_query, (appointment_id, student_id, difficulty_level, fnx_score))
        db.commit()
        return True
    except Exception as err:
        st.error(f"Error inserting response: {err}")
        return False
    finally:
        cursor.close()

def display_functioning_questionnaire(db, appointment_id, student_id):
    completed_response = check_functioning_completed(db, appointment_id)
    if completed_response:
        st.success(f"Functioning completed ✅")
    else:
        st.info("If you checked off any problems, how difficult have these problems made it for you?")
        difficulty_level = st.radio(
            "Choose difficulty level:",
            ('Not difficult at all', 'Somewhat difficult', 'Very difficult', 'Extremely difficult'))

        if st.button("Submit Functioning Response"):
            success = insert_functioning_response(db, appointment_id, student_id, difficulty_level)
            if success:
                st.success("Functioning response recorded successfully ✅!")
                st.rerun() 

def set_background2(image_path, width="500px", height="500px", border_color="orange", border_width="5px"):
    try:
        if not os.path.exists(image_path):
            st.error(f"Image file '{image_path}' not found.")
            return
        
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        st.markdown(f"""
        <style>
        .image-container {{
            width: {width};
            height: {height};
            background-image: url('data:image/jpeg;base64,{encoded_string}');
            background-size: cover;
            background-position: right;
            border: {border_width}{border_color};
            margin: 300;
            border-radius : 100%;
            position: fixed;
            top: 5;
        }}
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="image-container"></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading background image: {e}")

col1, col2 = st.columns(2)
with col1:
    set_background("brain_theme3.jpg", width="300px", height="150px", border_color="red", border_width="5px")

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

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

import phq9_responses, gad7_responses, results_filled, stud_render_tools, clinical_notes
response_modules = {
    'PHQ-9': phq9_responses.main,
    'GAD-7':gad7_responses.main,
    'Functioning': 'Noted'
}


from streamlit_javascript import st_javascript


# def main():
#     db = create_connection()
#     create_functioning_responses_table()

#     # Detect screen width for responsive design
#     device_width = st_javascript("window.innerWidth", key="device_width")
#     if device_width is None:
#         st.stop()

#     is_mobile = device_width <= 768
#     num_cols = 3 if is_mobile else 4
#     card_width = "100%" if is_mobile else "150px"
#     appointment_card_height = "200px" if is_mobile else "150px"
#     tool_card_height = "150px"
#     font_size_title = "25px" if is_mobile else "25px"
#     font_size_text = "16px" if is_mobile else "13px"

#     for key, default in {
#         "selected_record": None,
#         "selected_appointment": None,
#         "selected_tool": None,
#         "selected_page": "screening_menu",
#         "last_search_input": ""
#     }.items():
#         if key not in st.session_state:
#             st.session_state[key] = default

#     col1, col2 = st.columns([2, 2])
#     with col1.expander("🔍SEARCH", expanded=True):
#         search_input = st.text_input("Enter Name or STD ID", "")

#     if search_input != st.session_state.last_search_input:
#         st.session_state.selected_record = None
#         st.session_state.selected_appointment = None
#         st.session_state.selected_tool = None
#         st.session_state.last_search_input = search_input

#     results = []
#     if st.session_state.selected_record is None and search_input.strip():
#         results = fetch_students(db, search_input)
#         if results:
#             with col1.expander('Results', expanded=True):
#                 st.write(f"**{len(results)} result(s) found**")
#                 options = {f"{r['name']} - {r['student_id']}": r for r in results}
#                 selected_option = st.selectbox("Select a record:", list(options.keys()))
#                 st.session_state.selected_record = options[selected_option]
#         else:
#             st.error(f'No record for {search_input} ')

#     if st.session_state.selected_record:
#         selected_record = st.session_state.selected_record
#         with col2.expander("📄 STUDENT INFO", expanded=True):
#             st.write(f"Student ID: {selected_record['student_id']}")
#             st.write(f"Name: {selected_record['name']}")
#             st.write(f"Gender: {selected_record['gender']}")
#             st.write(f"Age: {selected_record['age']} years")
#             st.write(f"Class: {selected_record['student_class']}")
#             st.write(f"Stream: {selected_record['stream']}")

#         appointment_details = sorted(
#             fetch_appointment_details_by_name(selected_record['name']),
#             key=lambda x: (x["appointment_date"], x["appointment_time"]),
#             reverse=True)

#         if st.session_state.selected_appointment is None:
#             if appointment_details:
#                 cols = st.columns(num_cols)
#                 for index, appointment in enumerate(appointment_details):
#                     with cols[index % num_cols]:
#                         appointment_id = appointment["appointment_id"]
#                         screen_type = appointment["screen_type"]
#                         tool_statuses = appointment["tool_status"].split(", ") if appointment["tool_status"] else []
#                         appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"
#                         status_text = "Completed ✅" if all(status.strip() == "Completed" for status in tool_statuses) else "Pending ⏳"
#                         title = ordinal(len(appointment_details) - index)

#                         hasClicked = card(
#                             title=f'{title} - {screen_type}',
#                             text=f"{appointment_id}\n{status_text}",
#                             url=None,
#                             styles={
#                                 "card": {
#                                     "width": card_width,
#                                     "height": appointment_card_height,
#                                     "margin": "10px 0px",
#                                     "border-radius": "30px",
#                                     "background": appointment_color,
#                                     "color": "white",
#                                     "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
#                                     "border": "1px solid red",
#                                     "text-align": "center",
#                                 },
#                                 "text": {"font-family": "serif", "font-size": font_size_text},
#                                 "title": {"font-family": "serif", "font-size": font_size_title}
#                             },
#                         )
#                         if hasClicked:
#                             st.session_state.selected_appointment = appointment
#                             st.session_state.appointment_id = appointment_id
#                             st.rerun()

#         elif st.session_state.selected_tool is None:
#             appointment_id = st.session_state.appointment_id
#             task_reslt = option_menu(
#                 menu_title='',
#                 orientation='horizontal',
#                 menu_icon='',
#                 options=['Screen', 'Results', 'Notes'],
#                 icons=['book', 'bar-chart', 'printer'],
#                 styles={
#                     "container": {"padding": "8!important", "background-color": 'black', 'border': '0.01px dotted red'},
#                     "icon": {"color": "red", "font-size": "15px"},
#                     "nav-link": {"color": "#d7c4c1", "font-size": "15px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
#                     "nav-link-selected": {"background-color": "green"},
#                 },
#                 key="task_reslt"
#             )

#             if task_reslt == 'Screen':
#                 tool_status_list = get_requested_tools(db, appointment_id)
#                 requested_tools = fetch_requested_tools(db, appointment_id)
#                 tools_list = list(requested_tools) + ["Functioning"]

#                 tool_colors = {tool: f"#{hex(hash(tool) % 0xFFFFFF)[2:].zfill(6)}" for tool in tools_list}
#                 tool_images = {tool: f"images/{tool.lower()}.png" for tool in tools_list}

#                 if st.button("🔙back"):
#                     st.session_state.selected_appointment = None
#                     st.rerun()

#                 cols = st.columns(num_cols)
#                 for idx, tool in enumerate(tools_list):
#                     with cols[idx % num_cols]:
#                         if tool == "Functioning":
#                             status_check = check_functioning_completed(db, appointment_id)
#                             tool_status = "Completed" if status_check and status_check[0] else "Pending"
#                         else:
#                             tool_status = requested_tools.get(tool, "Pending")

#                         image_path = tool_images.get(tool, "brain.gif")
#                         try:
#                             with open(image_path, "rb") as f:
#                                 encoded = base64.b64encode(f.read()).decode("utf-8")
#                                 image_data = f"data:image/png;base64,{encoded}"
#                         except FileNotFoundError:
#                             image_data = None

#                         display_text = "Update" if tool == "PROFILE" else ("Completed ✅" if tool_status == "Completed" else "Pending ⏳")
#                         hasClicked = card(
#                             title=tool,
#                             text=display_text,
#                             image=image_data,
#                             url=None,
#                             styles={
#                                 "card": {
#                                     "width": card_width,
#                                     "height": tool_card_height,
#                                     "margin": "10px 0px",
#                                     "border-radius": "30px",
#                                     "border-color": "red",
#                                     "background-color": tool_colors.get(tool, "lightgray"),
#                                     "color": "white",
#                                     "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
#                                     "border": "2px solid #600000"
#                                 },
#                                 "text": {"font-family": "serif", "font-size": font_size_text},
#                                 "title": {"font-family": "serif", "font-size": font_size_title}
#                             })

#                         if hasClicked:
#                             st.session_state.selected_tool = tool
#                             st.rerun()

#             elif task_reslt == 'Results':
#                 results_filled.main()
#             elif task_reslt == 'Notes':
#                 session_notes.main()

#             if st.button("🔙 back"):
#                 st.session_state.selected_appointment = None
#                 st.rerun()

#         else:
#             selected_tool = st.session_state.selected_tool
#             if st.button("🔙 back", key="return_btn"):
#                 st.session_state.selected_tool = None
#                 st.rerun()

#             appointment_id = st.session_state.appointment_id
#             student_id = st.session_state.selected_record['student_id']
#             if selected_tool == "Functioning":
#                 display_functioning_questionnaire(db, appointment_id, student_id)
#             else:
#                 tool_status = fetch_requested_tools(db, appointment_id).get(selected_tool, "Pending")
#                 if selected_tool not in tool_modules:
#                     st.warning(f"No module found for the tool: {selected_tool}. Please contact support.")
#                 else:
#                     module_function = tool_modules[selected_tool]
#                     response_function = response_modules[selected_tool]
#                     if tool_status == 'Pending':
#                         st.info(f"Please fill out the {selected_tool} form:")
#                         module_function()
#                         if st.button(f"Submit to complete {selected_tool}"):
#                             update_tool_status(db, appointment_id, selected_tool, 'Completed')
#                             st.success(f"{selected_tool} response captured ✅!")
#                     else:
#                         st.success(f"{selected_tool} completed ✅")
#                         response_function()
#     db.close()
# if __name__ == '__main__':
#     main()



def main():
    db = create_connection()
    create_functioning_responses_table()
    st.markdown(
        """
        <style>
        .card-wrapper {
            margin-bottom: 0px; /* Tight vertical spacing */
        }
        .element-container:has(.stCard) {
            padding-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Detect screen width for responsiveness
    device_width = st_javascript("window.innerWidth", key="device_width")
    if device_width is None:
        st.stop()

    is_mobile = device_width < 768
    num_cols = 3 if is_mobile else 4
    card_width = "100%" if is_mobile else "150px"
    appointment_card_height = "150px" if is_mobile else "150px"
    tool_card_height = "100px" if is_moble else "150"
    font_size_title = "25px" if is_mobile else "30px"
    font_size_text = "16px" if is_mobile else "20px"

    for key, default in {
        "selected_record": None,
        "selected_appointment": None,
        "selected_tool": None,
        "selected_page": "screening_menu",
        "last_search_input": ""
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    col1, col2 = st.columns([2, 2])
    with col1.expander("🔍SEARCH", expanded=True):
        search_input = st.text_input("Enter Name or STD ID", "")

    if search_input != st.session_state.last_search_input:
        st.session_state.selected_record = None
        st.session_state.selected_appointment = None
        st.session_state.selected_tool = None
        st.session_state.last_search_input = search_input

    results = []
    if st.session_state.selected_record is None and search_input.strip():
        results = fetch_students(db, search_input)
        if results:
            with col1.expander('Results', expanded=True):
                st.write(f"**{len(results)} result(s) found**")
                options = {f"{r['name']} - {r['student_id']}": r for r in results}
                selected_option = st.selectbox("Select a record:", list(options.keys()))
                st.session_state.selected_record = options[selected_option]
        else:
            st.error(f'No record for {search_input} ')

    if st.session_state.selected_record:
        selected_record = st.session_state.selected_record
        with col2.expander("📄 STUDENT INFO", expanded=True):
            st.write(f"Student ID: {selected_record['student_id']}")
            st.write(f"Name: {selected_record['name']}")
            st.write(f"Gender: {selected_record['gender']}")
            st.write(f"Age: {selected_record['age']} years")
            st.write(f"Class: {selected_record['student_class']}")
            st.write(f"Stream: {selected_record['stream']}")

        appointment_details = sorted(
            fetch_appointment_details_by_name(selected_record['name']),
            key=lambda x: (x["appointment_date"], x["appointment_time"]),
            reverse=True)

        if st.session_state.selected_appointment is None:
            if appointment_details:
                cols = st.columns(num_cols)
                for index, appointment in enumerate(appointment_details):
                    with cols[index % num_cols]:
                        with st.container():
                            st.markdown('<div class="card-wrapper">', unsafe_allow_html=True)
                            appointment_id = appointment["appointment_id"]
                            screen_type = appointment["screen_type"]
                            tool_statuses = appointment["tool_status"].split(", ") if appointment["tool_status"] else []
                            appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"
                            status_text = "Completed ✅" if all(status.strip() == "Completed" for status in tool_statuses) else "Pending ⏳"
                            title = ordinal(len(appointment_details) - index)

                            hasClicked = card(
                                title=f'{title} - {screen_type}',
                                text=f"{appointment_id}\n{status_text}",
                                url=None,
                                styles={
                                    "card": {
                                        "width": card_width,
                                        "height": appointment_card_height,
                                        "margin": "0px",
                                        "border-radius": "30px",
                                        "background": appointment_color,
                                        "color": "white",
                                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                                        "border": "1px solid red",
                                        "text-align": "center",
                                    },
                                    "text": {"font-family": "serif", "font-size": font_size_text},
                                    "title": {"font-family": "serif", "font-size": font_size_title}
                                },
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                            if hasClicked:
                                st.session_state.selected_appointment = appointment
                                st.session_state.appointment_id = appointment_id
                                st.rerun()

        elif st.session_state.selected_tool is None:
            appointment_id = st.session_state.appointment_id
            task_reslt = option_menu(
                menu_title='',
                orientation='horizontal',
                menu_icon='',
                options=['Screen', 'Results', 'Notes'],
                icons=['book', 'bar-chart', 'printer'],
                styles={
                    "container": {"padding": "8!important", "background-color": 'black', 'border': '0.01px dotted red'},
                    "icon": {"color": "red", "font-size": "15px"},
                    "nav-link": {"color": "#d7c4c1", "font-size": "15px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                    "nav-link-selected": {"background-color": "green"},
                },
                key="task_reslt"
            )

            if task_reslt == 'Screen':
                tool_status_list = get_requested_tools(db, appointment_id)
                requested_tools = fetch_requested_tools(db, appointment_id)
                tools_list = list(requested_tools) + ["Functioning"]

                tool_colors = {tool: f"#{hex(hash(tool) % 0xFFFFFF)[2:].zfill(6)}" for tool in tools_list}
                tool_images = {tool: f"images/{tool.lower()}.png" for tool in tools_list}

                if st.button("🔙back"):
                    st.session_state.selected_appointment = None
                    st.rerun()

                cols = st.columns(num_cols)
                for idx, tool in enumerate(tools_list):
                    with cols[idx % num_cols]:
                        with st.container():
                            st.markdown('<div class="card-wrapper">', unsafe_allow_html=True)
                            if tool == "Functioning":
                                status_check = check_functioning_completed(db, appointment_id)
                                tool_status = "Completed" if status_check and status_check[0] else "Pending"
                            else:
                                tool_status = requested_tools.get(tool, "Pending")

                            image_path = tool_images.get(tool, "brain.gif")
                            try:
                                with open(image_path, "rb") as f:
                                    encoded = base64.b64encode(f.read()).decode("utf-8")
                                    image_data = f"data:image/png;base64,{encoded}"
                            except FileNotFoundError:
                                image_data = None

                            display_text = "Update" if tool == "PROFILE" else ("Completed ✅" if tool_status == "Completed" else "Pending ⏳")
                            hasClicked = card(
                                title=tool,
                                text=display_text,
                                image=image_data,
                                url=None,
                                styles={
                                    "card": {
                                        "width": card_width,
                                        "height": tool_card_height,
                                        "margin": "0px",
                                        "border-radius": "30px",
                                        "border-color": "red",
                                        "background-color": tool_colors.get(tool, "lightgray"),
                                        "color": "white",
                                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                                        "border": "2px solid #600000"
                                    },
                                    "text": {"font-family": "serif", "font-size": font_size_text},
                                    "title": {"font-family": "serif", "font-size": font_size_title}
                                })

                            st.markdown('</div>', unsafe_allow_html=True)
                            if hasClicked:
                                st.session_state.selected_tool = tool
                                st.rerun()

            elif task_reslt == 'Results':
                results_filled.main()
            elif task_reslt == 'Notes':
                session_notes.main()

            if st.button("🔙 back"):
                st.session_state.selected_appointment = None
                st.rerun()

        else:
            selected_tool = st.session_state.selected_tool
            if st.button("🔙 back", key="return_btn"):
                st.session_state.selected_tool = None
                st.rerun()

            appointment_id = st.session_state.appointment_id
            student_id = st.session_state.selected_record['student_id']
            if selected_tool == "Functioning":
                display_functioning_questionnaire(db, appointment_id, student_id)
            else:
                tool_status = fetch_requested_tools(db, appointment_id).get(selected_tool, "Pending")
                if selected_tool not in tool_modules:
                    st.warning(f"No module found for the tool: {selected_tool}. Please contact support.")
                else:
                    module_function = tool_modules[selected_tool]
                    response_function = response_modules[selected_tool]
                    if tool_status == 'Pending':
                        st.info(f"Please fill out the {selected_tool} form:")
                        module_function()
                        if st.button(f"Submit to complete {selected_tool}"):
                            update_tool_status(db, appointment_id, selected_tool, 'Completed')
                            st.success(f"{selected_tool} response captured ✅!")
                    else:
                        st.success(f"{selected_tool} completed ✅")
                        response_function()
    db.close()

if __name__ == '__main__':
    main()
