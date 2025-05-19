import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_card import card
import random
import sqlite3
import bcrypt
# import student_page
import conslts
import LogIn, SignUp, student_tool_page


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .card-wrapper {
        margin-bottom: 1px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


width = st_javascript("window.innerWidth")
is_mobile = width is not None and width < 768

for key in ["role", "username", "logged_in", "initialized", "student_action", "student_role_selected"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["role", "username", "student_action"] else False

def get_random_color():
    colors = ["#FF6B6B", "#4ECDC4", "#556270", "#C7F464", "#FFCC5C"]
    return random.choice(colors)

def create_connection():
    db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db

def initialize_database():
    db = create_connection()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('therapist', 'admin', 'superadmin')) NOT NULL
        );
    ''')
    default_users = [
        ("therapist1", "pass123", "therapist"),
        ("admin1", "adminpass", "admin"),
        ("superadmin1", "superpass", "superadmin")
    ]
    for username, password, role in default_users:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_pw, role))
    db.commit()
    db.close()

def verify_user(username, password, role):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role))
    user = cursor.fetchone()
    db.close()
    if user:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))
        except Exception:
            st.error("⚠️ Password format issue. Please reset.")
    return False

def back_to_main_menu():
    if st.button("⬅️ Back to Main Menu"):
        for key in ["role", "username", "logged_in", "student_action", "student_role_selected"]:
            st.session_state[key] = None if key in ["role", "username", "student_action"] else False
        st.rerun()

def back_to_student_menu():
    if st.button("⬅️ Back to Student Menu"):
        st.session_state.student_action = None
        st.rerun()

def login_user(role_name):
    with st.form(key=f"{role_name}_form"):
        st.markdown(f'##### :red[{role_name.capitalize()} Login]')
        username = st.text_input("Username", key=f"{role_name}_user")
        password = st.text_input("Password", type="password", key=f"{role_name}_pass")
        submit = st.form_submit_button("Login")
        if submit:
            if verify_user(username, password, role_name):
                st.session_state.logged_in = True
                st.session_state.username = username  # Store actual username
                st.session_state.role = role_name
                st.success(f"👋 Welcome, {username}!")
                st.rerun()
            else:
                st.warning("❌ Invalid username or password.")
    back_to_main_menu()

def role_selection():
    card_data = [
        {"title": "🧑‍🎓🎓", "text": "student",     "key": "student_card"},
        {"title": "🎋", "text": "therapist",   "key": "therapist_card"},
        {"title": "👨‍👨‍👦", "text": "admin",      "key": "admin_card"},
        {"title": "😎", "text": "superadmin",  "key": "superadmin_card"},
    ]

    cols_per_row = 2 if is_mobile else 4
    rows = [card_data[i:i + cols_per_row] for i in range(0, len(card_data), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            color = get_random_color()
            with col:
                clicked = card(
                    title=item["title"],
                    text=item["text"].capitalize(),
                    key=item["key"],
                    styles={
                        "card": {
                            "width": "100%",
                            "height": "180px" if is_mobile else "220px",
                            "border-radius": "15px",
                            "background": f"linear-gradient(135deg, {color}, #ffffff)",
                            "color": "white",
                            "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                            "border": "1px solid #ccc",
                            "text-align": "center",
                            "padding": "10px",
                            "margin": "0",
                        },
                        "title": {
                            "font-size": "40px" if is_mobile else "100px",
                            "margin": "0 0 5px 0",
                        },
                        "text": {
                            "font-size": "18px" if is_mobile else "35px",
                            "margin": "0",
                        },
                    }
                )
                if clicked:
                    st.session_state.role = item["text"]
                    if item["text"] == "student":
                        st.session_state.student_role_selected = True
                    st.rerun()

def student_login_menu():
    st.markdown("### 🎓 Student Access")
    col1, col2 = st.columns(2)
    with col1:
        register_clicked = card(
            title="📝",
            text="Register",
            key="student_register_card",
            styles={
                "card": {
                    "height": "180px" if is_mobile else "220px",
                    "border-radius": "15px",
                    "background": "linear-gradient(135deg, #6A5ACD, #ffffff)",
                    "color": "white",
                    "text-align": "center",
                },
                "title": {"font-size": "40px" if is_mobile else "80px"},
                "text": {"font-size": "18px" if is_mobile else "30px"},
            }
        )
    with col2:
        login_clicked = card(
            title="🔐",
            text="Login",
            key="student_login_card",
            styles={
                "card": {
                    "height": "180px" if is_mobile else "220px",
                    "border-radius": "15px",
                    "background": "linear-gradient(135deg, #20B2AA, #ffffff)",
                    "color": "white",
                    "text-align": "center",
                },
                "title": {"font-size": "40px" if is_mobile else "80px"},
                "text": {"font-size": "18px" if is_mobile else "30px"},
            }
        )
    if register_clicked:
        st.session_state.student_action = "register"
        st.rerun()
    elif login_clicked:
        st.session_state.student_action = "login"
        st.rerun()
    back_to_main_menu()

def student_dashboard():
    student_tool_page.main()  

def show_dashboard(role):
    username = st.session_state.get("username", "User")
    st.success(f"🎉 Welcome, {username}!")

    if role == "therapist":
        conslts.main()
    elif role == "student":
        student_dashboard()
    elif role == "admin":
        conslts.main()
    elif role == "superadmin":
        conslts.main()
    else:
        st.info('This is your dashboard')



def show_dashboard(role):
    username = st.session_state.get("username", "User")
    st.success(f"🎉 Welcome, {username}!")

    
    if st.button("🚪 Logout"):
        for key in ["role", "username", "logged_in", "student_action", "student_role_selected"]:
            st.session_state[key] = None if key in ["role", "username", "student_action"] else False
        st.rerun()

    if role == "therapist":
        conslts.main()
    elif role == "student":
        student_dashboard()
    elif role == "admin":
        conslts.main()
    elif role == "superadmin":
        conslts.main()
    else:
        st.info('This is your dashboard')


def main():
    if not st.session_state.initialized:
        initialize_database()
        st.session_state.initialized = True
    if not st.session_state.username:
        if not st.session_state.role:
            role_selection()
        else:
            if st.session_state.role == "student" and not st.session_state.logged_in:
                if not st.session_state.student_role_selected:
                    role_selection()
                else:
                    if st.session_state.student_action is None:
                        student_login_menu()
                    elif st.session_state.student_action == "register":
                        SignUp.main()
                        back_to_student_menu()
                    elif st.session_state.student_action == "login":
                        LogIn.main()
                        back_to_student_menu()
            elif st.session_state.role in ["therapist", "admin", "superadmin"] and not st.session_state.logged_in:
                login_user(st.session_state.role)
    else:
        show_dashboard(st.session_state.role)

if __name__ == "__main__":
    main()

