import streamlit as st
from streamlit_card import card
import mysql.connector
import LogIn, SignUp
import student_tool_page
import streamlit as st
import base64
import os
import get_help
from mysql.connector import Error
import datetime
from datetime import datetime
import sqlite3
import LogIn


def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

def set_background(image_path, width="500px", height="500px", border_color="red", border_width="5px"):
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
            border: {border_width} {border_color};
            margin: 0 auto;
            border-radius : 10%;
            position: fixed;
            top: 1;
        }}
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="image-container"></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading background image: {e}")

st.markdown(
    """
    <style>
        .mental-health-text {
            font-size: 70px;
            position: fixed;
            top: 0;
            font-weight: bold;
            # font-family: 'Courier New', monospace;
            font-family: 'Mistral', monospace;
            font-family: 'Edwardian Script ITC',monospace;
            color: #D4AF37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="mental-health-text">Mental Health Is Wealth</div>', unsafe_allow_html=True)
# set_background("brain_theme3.jpg", width="700px", height="500px", border_color="red", border_width="5px")
# st.logo('brain.gif')

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables access by column name
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

if "username" not in st.session_state:
    st.session_state["username"] = None

if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = None 



def set_custom_background(bg_color="skyblue", sidebar_img=None):
    page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {bg_color};
            background-size: 140%;
            background-position: top left;
            background-repeat: repeat;
            background-attachment: local;
            padding-top: 0px;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            {"background-image: url('data:image/png;base64," + sidebar_img + "');" if sidebar_img else ""}
            background-position: center; 
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
            padding-top: 0px;
        }}
        [data-testid="stToolbar"] {{
            right: 2rem;
        }}
        </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


pages = [
    {"title": '📝', "color": "#004d99", "text":"Appointments"},
    {"title": "🧑‍🤝‍🧑",   "color": "#660000", "text":"Support"},
    {"title": "💬",  "color": "#f39c12",  "text":"Chats"},
    {"title": "📚",  "color": "#27ae60", "text":"Self-help"},
    {"title": "📚.",  "color": "#27ae60", "text":"Content"},
    {"title": "📚_",  "color": "#27ae60", "text":"Profile"}
]

def get_menu():
    st.markdown(
        """
        <style>
        .main {
            # background: linear-gradient(135deg, #600000, #ff5e5e);
            padding: 20px;
            border-radius: 15px;
        }
        .button {
            background-color: #800000 !important;
            color: white !important;
            font-size: 16px !important;
            border-radius: 10px !important;
            padding: 8px 20px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,)

    if st.session_state.get("username"):
        st.sidebar.info('PERSONAL INFORMATION')
    elif "auth_page" not in st.session_state:
        st.markdown('<div class="main">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if card(
                title="📚 Sign In",
                text="Log In",
                key="sign_in_card",
                styles={
                    "card": {
                        "width": "300px",
                        "height": "250px",
                        "border-radius": "30px",
                        "background": "linear-gradient(135deg, #004d99, #0099ff)",
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": "2px solid #004d99",
                        "text-align": "center",
                    },
                    "text": {"font-family": "serif", "font-size": "16px"},
                },
            ):
                st.session_state["auth_page"] = "login"
                st.rerun()

        with col2:
            if card(
                title="📝 Sign Up",
                text="Register",
                key="sign_up_card",
                styles={
                    "card": {
                        "width": "300px",
                        "height": "250px",
                        "border-radius": "30px",
                        "background": "linear-gradient(135deg, #660000, #ff6666)",
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": "2px solid #660000",
                        "text-align": "center",
                    },
                    "text": {"font-family": "serif", "font-size": "16px"},},
            ):
                st.session_state["auth_page"] = "signup"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.session_state["auth_page"] == "login":
            set_background("brain_theme1.jpg", width="800px", height="400px", border_color="red", border_width="5px")
            LogIn.main()
        elif st.session_state["auth_page"] == "signup":
            set_background("brain_theme1.jpg", width="800px", height="600px", border_color="red", border_width="5px")
            SignUp.main()

        if st.button("🔙 Return to Menu", key="return_button"):
            del st.session_state["auth_page"]
            st.rerun()


def fetch_student_record(username):
    try:
        db = create_connection()
        # db.row_factory = sqlite3.Row  # 👈 Enable dictionary-style row access
        cursor = db.cursor()
        cursor.execute("SELECT * FROM student_users WHERE username = ?", (username,))
        row = cursor.fetchone()
        db.close()
        if row:
            return dict(row)  # Works now because row is a sqlite3.Row
        return None
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None


def fetch_student_details_by_username(username):
    connection = create_connection()
    student_details = {}
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM student_users WHERE username = ?", (username,))
            record = cursor.fetchone()
            student_details = dict(record) if record else {}
        except Exception as e:
            st.error(f"Error fetching student details: {e}")
        finally:
            cursor.close()
            connection.close()
    return student_details



def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"



def fetch_appointment_details_by_username(username):
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
                WHERE s.username = ?
                GROUP BY a.appointment_id
            """
            cursor.execute(query, (username,))
            appointments = [dict(row) for row in cursor.fetchall()]
            return appointments
        except Exception as e:
            st.error(f"Error fetching appointment details: {e}")
        finally:
            cursor.close()
            connection.close()
    return []



def create_user_sessions_table():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    user_name TEXT, 
                    name TEXT, 
                    login_time TEXT NOT NULL,
                    logout_time TEXT,
                    duration INTEGER,
                    status TEXT DEFAULT 'inactive',
                    FOREIGN KEY (student_id) REFERENCES student_users(student_id)
                );
            """)
            connection.commit()
            # st.success("user_sessions table created successfully.")
        except Exception as e:
            st.error(f"Error creating user_sessions table: {e}")
        finally:
            cursor.close()
            connection.close()


def insert_user_session(student_id, user_name, name):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT session_id FROM user_sessions 
                WHERE student_id = ? AND status = 'active';
            """, (student_id,))
            existing_session = cursor.fetchone()
            if existing_session:
                return
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO user_sessions (student_id, user_name, name, login_time, status)
                VALUES (?, ?, ?, ?, ?);
            """, (student_id, user_name, name, login_time, 'active'))
            connection.commit()
        except Exception as e:
            st.error(f"Error inserting user session: {e}")
        finally:
            cursor.close()
            connection.close()


def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    duration_parts = []
    if hours > 0:
        duration_parts.append(f"{hours} hr{'s' if hours > 1 else ''}")
    if minutes > 0:
        duration_parts.append(f"{minutes} min{'s' if minutes > 1 else ''}")
    if secs > 0 or not duration_parts:
        duration_parts.append(f"{secs} sec{'s' if secs > 1 else ''}")

    return ", ".join(duration_parts)



def update_user_session_logout(student_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT login_time FROM user_sessions 
                WHERE student_id = ? AND status = 'active';
            """, (student_id,))
            login_time_result = cursor.fetchone()

            if not login_time_result:
                st.warning(f"No active session found for user {student_id}.")
                return

            login_time_str = login_time_result[0]
            login_time = datetime.strptime(login_time_str, "%Y-%m-%d %H:%M:%S")
            logout_dt = datetime.strptime(logout_time, "%Y-%m-%d %H:%M:%S")
            duration_seconds = int((logout_dt - login_time).total_seconds())

            cursor.execute("""
                UPDATE user_sessions 
                SET logout_time = ?, duration = ?, status = 'inactive' 
                WHERE student_id = ? AND status = 'active';
            """, (logout_time, duration_seconds, student_id))
            connection.commit()

            st.success(f"Session ended. Duration: {format_duration(duration_seconds)}")
        except Exception as e:
            st.error(f"Error updating user session: {e}")
        finally:
            cursor.close()
            connection.close()

# def main():
#     set_custom_background(bg_color="#2c3e50", sidebar_img=None)
#     create_user_sessions_table()
#     if 'student_name' not in st.session_state:
#         st.session_state.student_name = ''
#     page_menu = get_menu()
#     if st.session_state["username"]:
#         st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
#         student_info = fetch_student_record(st.session_state["username"])
#         if student_info is None:
#             st.error("Student record not found.")
#             return

#         user_id = student_info.get('student_id')
#         user_name = student_info.get('username')
#         name = student_info.get('name')
#         if user_id:
#             insert_user_session(user_id, user_name, name)
#         if st.sidebar.button(":red[Sign Out]"):
#             update_user_session_logout(user_id)
#             username = st.session_state["username"]
#             st.toast(f"👋 :green[Bye] :green[{username}]")    
#             st.session_state.clear()  
#             st.rerun()   
        
#         if st.session_state["selected_page"]:
#             if st.button("🔙 Return to Menu"):
#                 st.session_state["selected_page"] = None  
#                 st.rerun()
#             if st.session_state.username:
#                 student_details = fetch_student_details_by_username(st.session_state.username)
#                 if student_details:
#                     st.session_state.student_id = student_details.get("student_id")
#                     st.session_state.name = student_details.get("name")
#                     st.session_state.gender = student_details.get("gender")
#                     st.session_state.age = student_details.get("age")
#                     st.session_state.student_class = student_details.get("student_class")
#                     st.session_state.stream = student_details.get("stream")
#                     st.session_state.contact = student_details.get("contact")
#                     st.session_state.email = student_details.get("email")
#                     st.session_state.role = student_details.get("role")
                    
#                 if st.session_state["selected_page"] == "📝":
#                     appointment_details = sorted(
#                         fetch_appointment_details_by_username(st.session_state.username),
#                         key=lambda x: (x["appointment_date"], x["appointment_time"]),
#                         reverse=True)

#                     if appointment_details:
#                         if "selected_appointment" not in st.session_state:
#                             st.session_state.selected_appointment = None 

#                         if st.button("🏠 Return to Main Menu"):
#                             st.session_state["selected_page"] = None
#                             st.session_state.selected_appointment = None
#                             st.rerun()

#                         if st.session_state.selected_appointment is None:
#                             col1, col2 = st.columns(2)

#                             for index, appointment in enumerate(appointment_details):
#                                 appointment_id = appointment["appointment_id"]
#                                 screen_type = appointment["screen_type"]

#                                 tool_statuses = appointment["tool_status"].split(", ") if appointment["tool_status"] else []
#                                 appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}" 
#                                 if all(status.strip() == "Completed" for status in tool_statuses):
#                                     status_text = "Completed ✅"
#                                 else:
#                                     status_text = "Pending ⏳"

#                                 title = ordinal(len(appointment_details) - index)

#                                 with col1 if index % 2 == 0 else col2:
#                                     hasClicked = card(
#                                         title=title,
#                                         text=f"{appointment_id} \n {status_text}",
#                                         url=None,
#                                         styles={
#                                             "card": {
#                                                 "width": "240px",
#                                                 "height": "200px",
#                                                 "border-radius": "30px",
#                                                 "background": appointment_color,
#                                                 "color": "white",
#                                                 "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
#                                                 "border": f"2px solid {appointment_color}",
#                                                 "text-align": "center",
#                                             },
#                                             "text": {"font-family": "serif"},
#                                         },
#                                     )

#                                     if hasClicked:
#                                         st.session_state.selected_appointment = appointment  # Fix: Set appointment
#                                         st.session_state.appointment_id = appointment["appointment_id"]  # Store ID
#                                         st.rerun()

#                         else:
#                             if st.button("🔙 Return to Appointments"):
#                                 st.session_state.selected_appointment = None
#                                 st.rerun()

#                             student_tool_page.main()

#                     else:
#                         st.info("No pending appointments, please wait for updates.")

#                 elif st.session_state["selected_page"] == "🧑‍🤝‍🧑":
#                      get_help.main()

#                 elif st.session_state["selected_page"] == "💬":
#                     st.subheader("Chats Page")
                
#                 elif st.session_state["selected_page"] == "📚":
#                     video_display.main()
                   
#                 elif st.session_state["selected_page"] == "PROFILE":
#                     st.subheader("Profile Page")
#                     student_info = fetch_student_record(st.session_state["username"])
#                     if student_info:
#                         st.write(student_info)
        
#         else:
#             col1, col2 = st.columns(2)
#             for index, page in enumerate(pages):
#                 with col1 if index % 2 == 0 else col2:
#                     if card(
#                         title=page["title"],
#                         text=page['text'],
#                         key=page["title"],
#                         styles={
#                             "card": {
#                                 "width": "250px",
#                                 "height": "250px",
#                                 "border-radius": "80px",
#                                 "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
#                                 "color": "white",
#                                 "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
#                                 "border": f"2px solid {page['color']}",
#                                 "text-align": "center",
#                             },
#                             "text": {"font-family": "Blackadder ITC", "font-size": "35px"},
                       
#                             "title": { "font-size": "80px",  "font-family": "Arial", }, },
#                     ):
#                         st.session_state["selected_page"] = page["title"]
#                         st.rerun()

# if __name__ == "__main__":
#     main()




# import streamlit as st
# from streamlit_javascript import st_javascript
# from streamlit_card import card

# def main():
#     set_custom_background(bg_color="#2c3e50", sidebar_img=None)
#     create_user_sessions_table()

#     # 📱 Detect screen width
#     # screen_width = st_javascript("""window.innerWidth""")
#     screen_width = st_javascript("window.innerWidth", key="screen_width_js")

#     is_mobile = screen_width and screen_width <= 700

#     if 'student_name' not in st.session_state:
#         st.session_state.student_name = ''

#     page_menu = get_menu()

#     if st.session_state.get("username"):
#         st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
#         student_info = fetch_student_record(st.session_state["username"])
#         if student_info is None:
#             st.error("Student record not found.")
#             return

#         user_id = student_info.get('student_id')
#         user_name = student_info.get('username')
#         name = student_info.get('name')
#         if user_id:
#             insert_user_session(user_id, user_name, name)

#         if st.sidebar.button(":red[Sign Out]"):
#             update_user_session_logout(user_id)
#             username = st.session_state["username"]
#             st.toast(f"👋 :green[Bye] :green[{username}]")
#             st.session_state.clear()
#             st.rerun()

#         if st.session_state.get("selected_page"):
#             if st.button("🔙 Return to Menu"):
#                 st.session_state["selected_page"] = None
#                 st.rerun()

#             if st.session_state.get("username"):
#                 student_details = fetch_student_details_by_username(st.session_state["username"])
#                 if student_details:
#                     st.session_state.update({
#                         "student_id": student_details.get("student_id"),
#                         "name": student_details.get("name"),
#                         "gender": student_details.get("gender"),
#                         "age": student_details.get("age"),
#                         "student_class": student_details.get("student_class"),
#                         "stream": student_details.get("stream"),
#                         "contact": student_details.get("contact"),
#                         "email": student_details.get("email"),
#                         "role": student_details.get("role"),
#                     })

#                 if st.session_state["selected_page"] == "📝":
#                     appointment_details = sorted(
#                         fetch_appointment_details_by_username(st.session_state["username"]),
#                         key=lambda x: (x["appointment_date"], x["appointment_time"]),
#                         reverse=True
#                     )

#                     if appointment_details:
#                         if "selected_appointment" not in st.session_state:
#                             st.session_state.selected_appointment = None

#                         if st.button("🏠 Return to Main Menu"):
#                             st.session_state["selected_page"] = None
#                             st.session_state.selected_appointment = None
#                             st.rerun()

#                         if st.session_state.selected_appointment is None:
#                             num_cols = 2 if is_mobile else 4
#                             cols = st.columns(num_cols)

#                             for index, appointment in enumerate(appointment_details):
#                                 appointment_id = appointment["appointment_id"]
#                                 screen_type = appointment["screen_type"]
#                                 tool_statuses = appointment["tool_status"].split(", ") if appointment["tool_status"] else []
#                                 appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"
#                                 status_text = "Completed ✅" if all(status.strip() == "Completed" for status in tool_statuses) else "Pending ⏳"
#                                 title = ordinal(len(appointment_details) - index)

#                                 col = cols[index % num_cols]
#                                 with col:
#                                     hasClicked = card(
#                                         title=title,
#                                         text=f"{appointment_id} \n {status_text}",
#                                         url=None,
#                                         styles={
#                                             "card": {
#                                                 "width": "100%",
#                                                 "height": "200px",
#                                                 "border-radius": "30px",
#                                                 "background": appointment_color,
#                                                 "color": "white",
#                                                 "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
#                                                 "border": f"2px solid {appointment_color}",
#                                                 "text-align": "center",
#                                             },
#                                             "text": {"font-family": "serif"},
#                                         },
#                                     )

#                                     if hasClicked:
#                                         st.session_state.selected_appointment = appointment
#                                         st.session_state.appointment_id = appointment["appointment_id"]
#                                         st.rerun()

#                         else:
#                             if st.button("🔙 Return to Appointments"):
#                                 st.session_state.selected_appointment = None
#                                 st.rerun()
#                             student_tool_page.main()

#                     else:
#                         st.info("No pending appointments, please wait for updates.")

#                 elif st.session_state["selected_page"] == "🧑‍🤝‍🧑":
#                     get_help.main()

#                 elif st.session_state["selected_page"] == "💬":
#                     st.subheader("Chats Page")

#                 elif st.session_state["selected_page"] == "📚":
#                     video_display.main()

#                 elif st.session_state["selected_page"] == "PROFILE":
#                     st.subheader("Profile Page")
#                     student_info = fetch_student_record(st.session_state["username"])
#                     if student_info:
#                         st.write(student_info)

#         else:
#             num_cols = 2 if is_mobile else 4
#             cols = st.columns(num_cols)

#             for index, page in enumerate(pages):
#                 col = cols[index % num_cols]
#                 with col:
#                     if card(
#                         title=page["title"],
#                         text=page["text"],
#                         key=page["title"],
#                         styles={
#                             "card": {
#                                 "width": "100%",
#                                 "height": "250px",
#                                 "border-radius": "80px",
#                                 "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
#                                 "color": "white",
#                                 "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
#                                 "border": f"2px solid {page['color']}",
#                                 "text-align": "center",
#                             },
#                             "text": {"font-family": "Blackadder ITC", "font-size": "35px"},
#                             "title": {"font-size": "80px", "font-family": "Arial"},
#                         },
#                     ):
#                         st.session_state["selected_page"] = page["title"]
#                         st.rerun()

# if __name__ == "__main__":
#     main()


from streamlit_javascript import st_javascript
def main():
    screen_width = st_javascript("window.innerWidth", key="screen_width_key")
    is_mobile = screen_width < 750 if screen_width else False  
    set_custom_background(bg_color="#2c3e50", sidebar_img=None)
    create_user_sessions_table()
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ''
    page_menu = get_menu()
    if st.session_state.get("username"):
        st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
        student_info = fetch_student_record(st.session_state["username"])
        if student_info is None:
            st.error("Student record not found.")
            return

        user_id = student_info.get('student_id')
        user_name = student_info.get('username')
        name = student_info.get('name')
        if user_id:
            insert_user_session(user_id, user_name, name)

        if st.sidebar.button(":red[Sign Out]"):
            update_user_session_logout(user_id)
            username = st.session_state["username"]
            st.toast(f"👋 :green[Bye] :green[{username}]")
            st.session_state.clear()
            st.rerun()

        if st.session_state.get("selected_page"):
            if st.button("🔙 Return to Menu"):
                st.session_state["selected_page"] = None
                st.rerun()

            student_details = fetch_student_details_by_username(st.session_state["username"])
            if student_details:
                for key in ["student_id", "name", "gender", "age", "student_class", "stream", "contact", "email", "role"]:
                    st.session_state[key] = student_details.get(key)

            if st.session_state["selected_page"] == "📝":
                appointment_details = sorted(
                    fetch_appointment_details_by_username(st.session_state["username"]),
                    key=lambda x: (x["appointment_date"], x["appointment_time"]),
                    reverse=True)

                if appointment_details:
                    if "selected_appointment" not in st.session_state:
                        st.session_state.selected_appointment = None

                    if st.button("🏠 Return to Main Menu"):
                        st.session_state["selected_page"] = None
                        st.session_state.selected_appointment = None
                        st.rerun()

                    if st.session_state.selected_appointment is None:
                        cols = st.columns(2 if is_mobile else 4)

                        for index, appointment in enumerate(appointment_details):
                            appointment_id = appointment["appointment_id"]
                            screen_type = appointment["screen_type"]
                            tool_statuses = appointment["tool_status"].split(", ") if appointment["tool_status"] else []
                            appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"

                            status_text = "Completed ✅" if all(status.strip() == "Completed" for status in tool_statuses) else "Pending ⏳"
                            title = ordinal(len(appointment_details) - index)

                            with cols[index % len(cols)]:
                                hasClicked = card(
                                    title=title,
                                    text=f"{appointment_id} \n {status_text}",
                                    key=f"card_{appointment_id}",
                                    styles={
                                        "card": {
                                            "width": "100%" if is_mobile else "200px",
                                            "height": "180px" if is_mobile else "150px",
                                            "border-radius": "20px" if is_mobile else "30px",
                                            "background": appointment_color,
                                            "color": "white",
                                            "box-shadow": "0 2px 8px rgba(0, 0, 0, 0.2)",
                                            "border": f"2px solid {appointment_color}",
                                            "text-align": "center",
                                        },
                                        "text": {"font-family": "serif", "font-size": "12px" if is_mobile else "15px"},
                                    },)

                                if hasClicked:
                                    st.session_state.selected_appointment = appointment
                                    st.session_state.appointment_id = appointment["appointment_id"]
                                    st.rerun()
                    else:
                        if st.button("🔙 Return to Appointments"):
                            st.session_state.selected_appointment = None
                            st.rerun()
                        student_tool_page.main()
                else:
                    st.info("No pending appointments, please wait for updates.")

            elif st.session_state["selected_page"] == "🧑‍🤝‍🧑":
                get_help.main()

            elif st.session_state["selected_page"] == "💬":
                st.subheader("Chats Page")

            elif st.session_state["selected_page"] == "📚":
                video_display.main()

            elif st.session_state["selected_page"] == "PROFILE":
                st.subheader("Profile Page")
                student_info = fetch_student_record(st.session_state["username"])
                if student_info:
                    st.write(student_info)

        else:
            cols = st.columns(2 if is_mobile else 4)
            for index, page in enumerate(pages):
                with cols[index % len(cols)]:
                    if card(
                        title=page["title"],
                        text=page['text'],
                        key=f"main_card_{page['title']}",
                        styles={
                            "card": {
                                "width": "100%" if is_mobile else "250px",
                                "height": "180px" if is_mobile else "250px",
                                "border-radius": "20px" if is_mobile else "80px",
                                "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
                                "color": "white",
                                "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                                "border": f"2px solid {page['color']}",
                                "text-align": "center",
                            },
                            "text": {"font-family": "Blackadder ITC", "font-size": "20px" if is_mobile else "35px"},
                            "title": {"font-size": "40px" if is_mobile else "80px", "font-family": "Arial"},
                        },
                    ):
                        st.session_state["selected_page"] = page["title"]
                        st.rerun()

if __name__ == "__main__":
    main()
