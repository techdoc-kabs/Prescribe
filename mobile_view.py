import streamlit as st
st.set_page_config(page_title="Responsive Cards", layout="wide")
from streamlit_javascript import st_javascript
from streamlit_card import card
import random
import sqlite3
import bcrypt
# import student_page

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .card-wrapper {
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


width = st_javascript("window.innerWidth")
is_mobile = width is not None and width < 768
st.info(f"Screen width: {width}px")

card_data = [
    {"title": "📄", "text": "Student", "key": "student_card"},
    {"title": "🎋", "text": "Therapist",  "key": "therapist_card"},
    {"title": "👨‍👨‍👦", "text": "Admin",  "key": "admin_card"},
    {"title": "😎", "text": "Superadmin",  "key": "superadmin_card"},
]


def get_random_color():
    colors = ["#FF6B6B", "#4ECDC4", "#556270", "#C7F464", "#FFCC5C"]
    return random.choice(colors)


for key in ["role", "username", "logged_in", "initialized"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["role", "username"] else False
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
        for key in ["role", "username", "logged_in"]:
            st.session_state[key] = None if key in ["role", "username"] else False
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
                st.session_state.username = username  # ✅ Store actual username
                st.success(f"👋 Welcome, {username}!")
                st.rerun()
            else:
                st.warning("❌ Invalid username or password.")
    back_to_main_menu()


def student_login():
    student_page.main()
    back_to_main_menu()

import conslts
def show_dashboard(role):
    username = st.session_state.get("username", "User")
    st.success(f"🎉 Welcome, {username}!")
    if st.button("🚪 Logout"):
        for key in ["role", "username", "logged_in"]:
            st.session_state[key] = None if key in ["role", "username"] else False
        st.rerun()
    if role == "therapist":
        conslts.main()
    
    elif role == "student":
        student_page.main()
    
    elif role == "admin":
        conslts.main()
    
    elif role == "superadmin":
        conslts.main()

    else:
        st.write("This is your dashboard.")


def role_selection():
    card_data = [
        {"title": "📄", "text": "student",     "key": "student_card"},
        {"title": "🎋", "text": "therapist",   "key": "therapist_card"},
        {"title": "👨‍👨‍👦", "text": "admin",      "key": "admin_card"},
        {"title": "😎", "text": "superadmin",  "key": "superadmin_card"},
    ]

    def get_random_color():
        colors = ["#FF6B6B", "#4ECDC4", "#556270", "#C7F464", "#FFCC5C"]
        return random.choice(colors)

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
                    image=None,
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
                            "font-size": "80px" if is_mobile else "80px",
                            "margin": "0 0 5px 0",
                        },
                        "text": {
                            "font-size": "25px" if is_mobile else "30px",
                            "margin": "0",
                        },
                    }
                )
                if clicked:
                    st.session_state.role = item["text"]
                    st.rerun()

def main():
    if not st.session_state.initialized:
        initialize_database()
        st.session_state.initialized = True

    if st.session_state.role is None:
        role_selection()  # ✅ Handles both mobile and desktop rendering
    elif not st.session_state.logged_in:
        if st.session_state.role == "student":
            student_login()
        else:
            login_user(st.session_state.role)
    else:
        show_dashboard(st.session_state.role)
if __name__ == "__main__":
    main()
