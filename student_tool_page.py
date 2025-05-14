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


def table_exists(db, table_name):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

def fetch_requested_tools(db, appointment_id):
    table_name = "requested_tools_students"
    if not table_exists(db, table_name):
        print(f"Warning: Table '{table_name}' does not exist.")
        return {}
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
    table_name = "requested_tools_students"
    if not table_exists(db, table_name):
        st.error(f"Warning: Table '{table_name}' does not exist.")
        return {}
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
    # create_table_query = """
    # CREATE TABLE IF NOT EXISTS functioning_responses (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     appointment_id TEXT NOT NULL,
    #     student_id TEXT NOT NULL,
    #     difficulty_level TEXT NOT NULL CHECK(difficulty_level IN ('Not difficult at all', 'Somewhat difficult', 'Very difficult', 'Extremely difficult')),
    #     submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    # );
    # """
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

# def insert_functioning_response(db, appointment_id, student_id, difficulty_level):
#     cursor = db.cursor()
#     insert_query = """
#     INSERT INTO functioning_responses (appointment_id, student_id, difficulty_level)
#     VALUES (?, ?, ?)
#     """
#     try:
#         cursor.execute(insert_query, (appointment_id, student_id, difficulty_level))
#         db.commit()
#         return True
#     except Exception as err:
#         st.error(f"Error inserting response: {err}")
#         return False
#     finally:
#         cursor.close()

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

import sqlite3

# def add_fnx_score_column():
#     db = sqlite3.connect("mhpss_db.sqlite")
#     cursor = db.cursor()
#     try:
#         # Try adding the column
#         cursor.execute("ALTER TABLE functioning_responses ADD COLUMN fnx_score INTEGER")
#         db.commit()
#         print("Column 'fnx_score' added successfully.")
#     except sqlite3.OperationalError as e:
#         # This error likely means the column already exists
#         print(f"Error (probably column exists): {e}")
#     finally:
#         cursor.close()
#         db.close()




def main():
    db = create_connection()
    create_functioning_responses_table()
    if "student_id" in st.session_state:
        student_id = st.session_state.student_id
    if 'username' in st.session_state:
        username = st.session_state.username
    if 'student_name' in st.session_state:
        student_name = st.session_state.student_name
    
    if "appointment_id" in st.session_state:
        appointment_id = st.session_state.appointment_id
        
        if appointment_id:
            tool_status_list = get_requested_tools(db, appointment_id)
            requested_tools = fetch_requested_tools(db, appointment_id)
            tools_list = list(requested_tools)  
            
            if not tools_list:
                st.warning("No requested tools found.")
                db.close()
                return
            else:
                tools_list = ["PROFILE"] + tools_list + ["FUNCTIONING"]
                
                if "selected_tool" not in st.session_state:
                    st.session_state.selected_tool = None  
            
                tool_colors = {}
                tool_images = {}
                
                for tool in tools_list:
                    tool_colors[tool] = f"#{hex(hash(tool) % 0xFFFFFF)[2:].zfill(6)}"  # Unique color based on hash
                    tool_images[tool] = f"images/{tool.lower()}.png"

                if st.session_state.selected_tool is None:
                    cols = st.columns(2)
                    
                    for idx, tool in enumerate(tools_list):
                        if tool == "FUNCTIONING":
                            tool_status = check_functioning_completed(db, appointment_id)
                            tool_status = "Completed" if tool_status and tool_status[0] else "Pending"
                        else:
                            tool_status = requested_tools.get(tool, "Pending")  # ✅ Restore original behavior

                        image_path = tool_images.get(tool, "brain.gif")  # Fallback image
                        
                        try:
                            with open(image_path, "rb") as f:
                                data = f.read()
                                encoded = base64.b64encode(data).decode("utf-8")
                                image_data = f"data:image/png;base64,{encoded}"
                        except FileNotFoundError:
                            image_data = None 
                    
                        with cols[idx % 2]:  
                            if tool == "PROFILE":
                                display_text = "Update"
                                text_color = "blue"
                            elif tool_status == "Completed":
                                display_text = "Completed ✅"
                                text_color = "green" 
                            else:
                                display_text = "Pending ⏳"
                                text_color = "orange"

                            hasClicked = card(
                                title=tool,
                                text=f"{display_text}",
                                image=image_data,
                                url=None, 
                                styles={
                                    "card": {
                                        "width": "280px",
                                        "height": "200px",
                                        "border-radius": "30px",
                                        "background-color": tool_colors.get(tool, "lightgray"),  # Use dynamic color
                                        "color": "white",
                                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                                        "border": "2px solid #600000"
                                    },
                                    "text": {"font-family": "serif"},
                                } 
                            )
                            if hasClicked:
                                st.session_state.selected_tool = tool
                                st.rerun()

                else:
                    selected_tool = st.session_state.selected_tool
                    if st.button("🔙 Return to Assessment Menu", key="return_btn"):
                        st.session_state.selected_tool = None
                        st.rerun()
                    
                    if selected_tool == "PROFILE":
                        search_edit_and_update_student(db, username)
                    elif selected_tool == "FUNCTIONING":
                        display_functioning_questionnaire(db, appointment_id, student_id)
                    else:
                        tool_status = requested_tools[selected_tool]
                        if selected_tool not in tool_modules:
                            st.warning(f"No module found for the tool: {selected_tool}. Please contact support for help.")
                        else:
                            module_function = tool_modules[selected_tool]
                            if tool_status == 'Pending':
                                st.info(f"Please fill out the {selected_tool} form:")
                                module_function()
                                if st.button(f"Submit to complete {selected_tool}"):
                                    update_tool_status(db, appointment_id, selected_tool, 'Completed')
                                    st.success(f"{selected_tool} response captured ✅!")
                            else:
                                st.success(f"{selected_tool} completed ✅")
    db.close()
if __name__ == "__main__":
    main()
