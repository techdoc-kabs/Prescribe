import streamlit as st
from streamlit_card import card
import sqlite3
import LogIn, SignUp
import base64
import os
import random
from streamlit_javascript import st_javascript
import student_forms_page, consult_mobile


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



task_menu = {
    "Screening": [],
    "Sessions": ["Consultations", "Groups"],
    "Files": [],
    "Support": ["Emails", "Messages"],
}

def get_random_color(used_colors):
    while True:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if color not in used_colors:
            used_colors.add(color)
            return color

def show_cards(items, card_height, font_size_title, font_size_text, key_prefix, cols_per_row):
    used_colors = set()
    rows = [items[i : i + cols_per_row] for i in range(0, len(items), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            color = get_random_color(used_colors)
            with col:
                clicked = card(
                    title="🔹" if not item.get("subtasks") else "🎋",
                    text=item["name"],
                    key=f"{key_prefix}-{item['name']}",
                    styles={
                        "card": {
                            "width": "100%",
                            "height": card_height,
                            "border-radius": "20px",
                            "background": f"linear-gradient(135deg, {color}, #ffffff)",
                            "color": "white",
                            "box-shadow": "0 2px 6px rgba(0,0,0,0.15)",
                            "border": "1px solid #ccc",
                            "text-align": "center",
                            "padding": "10px",
                            "margin": "0",
                        },
                        "title": {
                            "font-family": "sans-serif",
                            "font-size": font_size_title,
                            "margin": "0 0 10px 0",
                        },
                        "text": {
                            "font-family": "sans-serif",
                            "font-size": font_size_text,
                            "margin": "0",
                        },
                    },
                )
                if clicked:
                    st.session_state.selected_task = item["name"]
                    st.rerun()

def show_task_menu(is_mobile):
    tasks = [{"name": k, "subtasks": v} for k, v in task_menu.items()]
    cols_per_row = 2 if is_mobile else 2
    show_cards(tasks, card_height="180px" if is_mobile else "220px",
               font_size_title="80px" if is_mobile else "100px",
               font_size_text="20px" if is_mobile else "24px",
               key_prefix="task",
               cols_per_row=cols_per_row)

def show_subtask_menu(task_name, is_mobile):
    subtasks = task_menu.get(task_name, [])
    if not subtasks:
        app_router(task_name)
        return
    subtasks_list = [{"name": subtask, "subtasks": []} for subtask in subtasks]
    cols_per_row = 1 if is_mobile else 2
    show_cards(subtasks_list, card_height="140px" if is_mobile else "200px",
               font_size_title="50px" if is_mobile else "100px",
               font_size_text="18px" if is_mobile else "30px",
               key_prefix="subtask",
               cols_per_row=cols_per_row)


def show_cards(items, card_height, font_size_title, font_size_text, key_prefix, cols_per_row):
    used_colors = set()
    rows = [items[i : i + cols_per_row] for i in range(0, len(items), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            color = get_random_color(used_colors)
            task_name = item["name"]
            icon = task_icons.get(task_name, "📌")  # default fallback icon

            with col:
                clicked = card(
                    title=f"{icon}",
                    text=task_name,
                    key=f"{key_prefix}-{task_name}",
                    styles={
                        "card": {
                            "width": "100%",
                            "height": card_height,
                            "border-radius": "20px",
                            "background": f"linear-gradient(135deg, {color}, #ffffff)",
                            "color": "white",
                            "box-shadow": "0 2px 6px rgba(0,0,0,0.15)",
                            "border": "1px solid red",
                            "text-align": "center",
                            "padding": "10px",
                            "margin": "0",
                        },
                        "title": {
                            "font-family": "sans-serif",
                            "font-size": font_size_title,
                            "margin": "0 0 10px 0",
                        },
                        "text": {
                            "font-family": "sans-serif",
                            "font-size": font_size_text,
                            "margin": "0",
                        },
                    },
                )
                if clicked:
                    st.session_state.selected_task = task_name
                    st.rerun()

def login_page():
    st.title("🔐 Login")
    st.write("Simulated login... click to continue.")
    if st.button("Log In"):
        st.session_state.username = "demo"
        st.rerun()

def show_logout():
    logout_key = f"logout_button_{st.session_state.get('username', 'guest')}"
    if st.button("🚪 Logout", key=logout_key):
        st.session_state.username = None
        st.session_state.selected_task = None
        st.rerun()

def app_router(task=None):
    if task == "Screening":
        student_forms_page.main()
    
    elif task == "Consultations":
        consult_mobile.main()
    
    elif task == "Groups":
        st.info("👥 Group Sessions - Coming soon!")
    
    elif task == "Files":
        st.info("📂 File Management - Coming soon!")
    
    elif task == "Emails":
        st.info("📧 Email Support - Coming soon!")
    
    elif task == "Messages":
        st.info("💬 Message Support - Coming soon!")
    
    else:
        st.warning("❌ Invalid task selected.")


task_icons = {
    "Screening": "📝",         # Questionnaires/forms
    "Consultations": "👩‍⚕️",   # One-on-one clinical consult
    "Groups": "👨‍👨‍👦",            # Group activities/sessions
    "Files": "📂",            # File/document management
    "Support": "🛠️",          # Help desk or tools
    "Emails": "📧",           # Email-based support
    "Messages": "💬",         # Messaging/chat support
}



def main():
    width = st_javascript("window.innerWidth", key="js-width-consults") or 1024
    is_mobile = width < 700
    for key in ['username', 'selected_task']:
        if key not in st.session_state:
            st.session_state[key] = None
    if not st.session_state.get("username"):
        login_page()
        return
    if st.session_state.selected_task:
        if st.button("🔙 Back"):
            current_task = st.session_state.selected_task
            if current_task in task_menu:
                st.session_state.selected_task = None
            else:
                for parent, children in task_menu.items():
                    if current_task in children:
                        st.session_state.selected_task = parent
                        break
            st.rerun()
        show_subtask_menu(st.session_state.selected_task, is_mobile)
    else:
        show_task_menu(is_mobile)

if __name__ == "__main__":
    main()
