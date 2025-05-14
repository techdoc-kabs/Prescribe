import streamlit as st
from streamlit_card import card
import sqlite3
import LogIn, SignUp
import student_forms_page
import video_display
import base64
import os
from streamlit_card import card

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

st.markdown("""
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
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
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
    {"title": '📝', "color": "#004d99", "text":"Tasks"},
    {"title": "📊",  "color": "#27ae60", "text":"Reports"},
    {"title": "💬",  "color": "#f39c12",  "text":"Blogs"},
    {"title": "📚",  "color": "#27ae60", "text":"Files"}]
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
        pass
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


def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row  # enables dict-like access
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

def fetch_student_record(username):
    try:
        db = create_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM student_users WHERE username = ?", (username,))
        record = cursor.fetchone()
        db.close()
        return dict(record) if record else None
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
            if record:
                student_details = dict(record)
        except sqlite3.Error as e:
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
            records = cursor.fetchall()
            return [dict(row) for row in records]
        except sqlite3.Error as e:
            st.error(f"Error fetching appointment details: {e}")
        finally:
            cursor.close()
            connection.close()
    return []


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


def create_user_sessions_table():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    login_time DATETIME,
                    logout_time DATETIME,
                    duration INTEGER,
                    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'inactive',
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
            connection.commit()
            print("user_sessions table created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating user_sessions table: {e}")
        finally:
            cursor.close()
            connection.close()


def render_task_menu(page_title, task_menu):
    # st.subheader(f"📋 Select a Task for {page_title}")
    col1, col2 = st.columns(2)

    for index, task in enumerate(task_menu):
        with col1 if index % 2 == 0 else col2:
            if card(
                title=task["title"],
                text=task["text"],
                key=f"task-{task['text']}",
                styles={
                    "card": {
                        "width": "250px",
                        "height": "250px",
                        "border-radius": "60px",
                        "background": "linear-gradient(135deg, #ffffff)",
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": "0.1px solid red",
                        "text-align": "center",
                    },
                    "text": {"font-family": "serif", "font-size": "30px"},
                    "title": {"font-family": "serif", "font-size": "100px"},
                },
            ):
                st.session_state.selected_task = task["text"]
                st.rerun()

def render_task_menu(page_title, task_menu):
    col1, col2 = st.columns(2)
    for index, task in enumerate(task_menu):
        with col1 if index % 2 == 0 else col2:
            if card(
                title=task["title"],
                text=task["text"],
                key=f"task-{task['text']}",
                styles={
                    "card": {
                        "width": "300px",
                        "height": "250px",
                        "border-radius": "60px",
                        "background": f"linear-gradient(135deg, #34495e, #ffffff)",
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": f"2px solid #34495e",
                        "text-align": "center",
                    },
                    "text": {"font-family": "serif", "font-size": "30px"},
                    "title": {"font-family": "serif", "font-size": "100px"},
                },
            ):
                st.session_state.selected_task = task["text"]
                st.rerun()


# import streamlit as st
# import student_forms_page
# import consult_mobile
# import entire_file 
# import results_filled_mlt, impact

# def login_page():
#     st.warning("🔒 Please log in to continue.")

# def show_sidebar():
#     st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
#     if st.sidebar.button(":red[Sign Out]"):
#         st.toast(f"👋 :green[Bye] :green[{st.session_state['username']}]")
#         st.session_state.clear()
#         st.rerun()

# def show_page_menu():
#     pages = [
#         {"title": '📝', "color": "#004d99", "text": "Tasks"},
#         {"title": "📈", "color": "#27ae60", "text": "Reports"},
#         {"title": "📦", "color": "#f39c12", "text": "Archives"},
#         {"title": "📚", "color": "#27ae60", "text": "Files"},
#     ]
#     col1, col2 = st.columns(2)
#     for index, page in enumerate(pages):
#         with col1 if index % 2 == 0 else col2:
#             if card(
#                 title=page["title"],
#                 text=page["text"],
#                 key=f"page-{page['text']}",
#                 styles={
#                     "card": {
#                         "width": "300px",
#                         "height": "250px",
#                         "border-radius": "60px",
#                         "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
#                         "color": "white",
#                         "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
#                         "border": f"2px solid {page['color']}",
#                         "text-align": "center",
#                     },
#                     "text": {"font-family": "serif", "font-size": "30px"},
#                     "title": {"font-family": "serif", "font-size": "100px"},
#                 },
#             ):
#                 st.session_state.selected_page = page["title"]
#                 st.rerun()

# def show_task_menu(page_title):
#     task_menu = [
#         {"title": '📝', "text": "Screening"},
#         {"title": "🧑‍🤝‍🧑", "text": "Consultations"},
#         {"title": "💬", "text": "Follow-Up"},
#         {"title": "🛗", "text": "Group sessions"},
#     ]
#     render_task_menu(page_title, task_menu)


# def render_report_menu(page_title, report_menu):
#     col1, col2 = st.columns(2)
#     for index, report in enumerate(report_menu):
#         with col1 if index % 2 == 0 else col2:
#             if card(
#                 title=report["title"],
#                 text=report["text"],
#                 key=f"task-{report['text']}",
#                 styles={
#                     "card": {
#                         "width": "300px",
#                         "height": "250px",
#                         "border-radius": "60px",
#                         "background": f"linear-gradient(135deg, #34495e, #ffffff)",
#                         "color": "white",
#                         "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
#                         "border": f"2px solid #34495e",
#                         "text-align": "center",
#                     },
#                     "text": {"font-family": "serif", "font-size": "30px"},
#                     "title": {"font-family": "serif", "font-size": "100px"},
#                 },
#             ):
#                 st.session_state.selected_task = report["text"]
#                 st.rerun()


# def show_report_menu(page_title):
#     report_menu = [
#         {"title": '📝', "text": "Evaluation"},
#         {"title": "📈", "text": "Analysis"},
#     ]
#     render_report_menu(page_title, report_menu)



# def app_router(page, task):
#     if st.button("🔙 Return to Task Menu"):
#         st.session_state.selected_task = None
#         st.rerun()

#     if task == "Screening":
#         student_forms_page.main()
#     elif task == "Consultations":
#         consult_mobile.main()
#     elif task == "Follow-Up":
#         st.info("📌 Follow-Up Page - Coming soon!")
#     elif task == "Group sessions":
#         st.info("👥 Group Sessions - Coming soon!")





# def main():
#     db = create_connection()
#     create_user_sessions_table()
#     set_custom_background(bg_color="#2c3e50", sidebar_img=None)
#     get_menu()

#     for key in ['student_name', 'student_id', 'appointment_id', 'selected_appointment', 'selected_page', 'selected_task']:
#         if key not in st.session_state:
#             st.session_state[key] = None

#     if not st.session_state.get("username"):
#         login_page()
#         return

#     show_sidebar()
#     fetch_student_record(st.session_state["username"])

#     if not st.session_state.selected_page:
#         show_page_menu()
#     elif st.session_state.selected_page == "📚":  # Files
#         if st.button("🔙 Return to Page Menu"):
#             st.session_state.selected_page = None
#             st.rerun()
#         entire_file.main()


#     elif st.session_state.selected_page == "📈":  # Files
#         if st.button("🔙 Return to Page Menu"):
#             st.session_state.selected_page = None
#             st.rerun()
#         # results_filled_mlt.main()
#         # impact.main()
#         show_report_menu(st.session_state.selected_page)


#     elif not st.session_state.selected_task:
#         if st.button("🔙 Return to Page Menu"):
#             st.session_state.selected_page = None
#             st.rerun()
#         show_task_menu(st.session_state.selected_page)

    

#     elif not st.session_state.selected_task:
#         if st.button("🔙 Return to Page Menu"):
#             st.session_state.selected_page = None
#             st.rerun()
#         show_report_menu(st.session_state.selected_page)


#     else:
#         app_router(st.session_state.selected_page, st.session_state.selected_task)
# if __name__ == "__main__":
#     main()
import streamlit as st
import student_forms_page
import consult_mobile
import entire_file 
import results_filled_mlt, impact

def login_page():
    st.warning("🔒 Please log in to continue.")

def show_sidebar():
    st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
    if st.sidebar.button(":red[Sign Out]"):
        st.toast(f"👋 :green[Bye] :green[{st.session_state['username']}]")
        st.session_state.clear()
        st.rerun()

def show_page_menu():
    pages = [
        {"title": '📝', "color": "#004d99", "text": "Tasks"},
        {"title": "📈", "color": "#27ae60", "text": "Reports"},
        {"title": "📦", "color": "#f39c12", "text": "Archives"},
        {"title": "📚", "color": "#27ae60", "text": "Files"},
    ]
    col1, col2 = st.columns(2)
    for index, page in enumerate(pages):
        with col1 if index % 2 == 0 else col2:
            if card(
                title=page["title"],
                text=page["text"],
                key=f"page-{page['text']}",
                styles={
                    "card": {
                        "width": "300px",
                        "height": "250px",
                        "border-radius": "60px",
                        "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": f"2px solid {page['color']}",
                        "text-align": "center",
                    },
                    "text": {"font-family": "serif", "font-size": "30px"},
                    "title": {"font-family": "serif", "font-size": "100px"},
                },
            ):
                st.session_state.selected_page = page["title"]
                st.rerun()

def show_task_menu(page_title):
    task_menu = [
        {"title": '📝', "text": "Screening"},
        {"title": "🧑‍🤝‍🧑", "text": "Consultations"},
        {"title": "💬", "text": "Follow-Up"},
        {"title": "🛗", "text": "Group sessions"},
    ]
    render_task_menu(page_title, task_menu)

def render_report_menu(page_title, report_menu):
    col1, col2 = st.columns(2)
    for index, report in enumerate(report_menu):
        with col1 if index % 2 == 0 else col2:
            if card(
                title=report["title"],
                text=report["text"],
                key=f"report-{report['text']}",
                styles={
                    "card": {
                        "width": "300px",
                        "height": "250px",
                        "border-radius": "60px",
                        "background": f"linear-gradient(135deg, #34495e, #ffffff)",
                        "color": "white",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                        "border": f"2px solid #34495e",
                        "text-align": "center",
                    },
                    "text": {"font-family": "serif", "font-size": "30px"},
                    "title": {"font-family": "serif", "font-size": "100px"},
                },
            ):
                st.session_state.selected_report = report["text"]
                st.rerun()

def show_report_menu(page_title):
    report_menu = [
        {"title": '📝', "text": "Evaluation"},
        {"title": "📈", "text": "Analysis"},
        {"title": "🎋", "text": "Interventions"}
    ]
    render_report_menu(page_title, report_menu)

def app_router(page, task=None, report=None):
    # Handle Task Menu Navigation
    if task:
        if task == "Screening":
            student_forms_page.main()
        elif task == "Consultations":
            consult_mobile.main()
        elif task == "Follow-Up":
            st.info("📌 Follow-Up Page - Coming soon!")
        elif task == "Group sessions":
            st.info("👥 Group Sessions - Coming soon!")
        return
    if report:
        if report == "Evaluation":
            impact.main() 
        elif report == "Analysis":
            results_filled_mlt.main()

        elif report == "Interventions":
            st.info('Interventions done')
        else:
            st.info("🚨 Invalid Report Selection!")
        return


def main():
    db = create_connection()
    create_user_sessions_table()
    set_custom_background(bg_color="#2c3e50", sidebar_img=None)
    get_menu()

    for key in ['student_name', 'student_id', 'appointment_id', 'selected_appointment', 'selected_page', 'selected_task', 'selected_report']:
        if key not in st.session_state:
            st.session_state[key] = None

    if not st.session_state.get("username"):
        login_page()
        return

    show_sidebar()
    fetch_student_record(st.session_state["username"])

    # PAGE MENU
    if not st.session_state.selected_page:
        show_page_menu()
        return

    # FILES PAGE
    if st.session_state.selected_page == "📚":
        if st.button("🔙 Return to Page Menu"):
            st.session_state.selected_page = None
            st.rerun()
        entire_file.main()
        return

    # REPORT MENU
    if st.session_state.selected_page == "📈":
        # Show report content
        if st.session_state.selected_report:
            if st.button("🔙 Return to Report Menu"):
                st.session_state.selected_report = None
                st.rerun()
            app_router(st.session_state.selected_page, report=st.session_state.selected_report)
        else:
            if st.button("🔙 Return to Page Menu"):
                st.session_state.selected_page = None
                st.rerun()
            show_report_menu(st.session_state.selected_page)
        return

    # TASK MENU
    if st.session_state.selected_page == "📝":
        if st.session_state.selected_task:
            if st.button("🔙 Return to Task Menu"):
                st.session_state.selected_task = None
                st.rerun()
            app_router(st.session_state.selected_page, task=st.session_state.selected_task)
        else:
            if st.button("🔙 Return to Page Menu"):
                st.session_state.selected_page = None
                st.rerun()
            show_task_menu(st.session_state.selected_page)
        return
    st.warning("⚠️ Under development.")
    if st.button("🔙 Return to Page Menu"):
        st.session_state.selected_page = None
        st.rerun()
if __name__ == "__main__":
    main()
