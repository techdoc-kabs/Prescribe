
# import streamlit as st
# from streamlit_javascript import st_javascript
# from streamlit_card import card
# import random

# st.set_page_config(page_title="Responsive Cards", layout="wide")

# st.markdown(
#     """
#     <style>
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
#     .card-wrapper {
#         margin-bottom: 10px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# st.title("📱💻 Responsive Streamlit Cards (2-column mobile view)")

# width = st_javascript("window.innerWidth")
# is_mobile = width is not None and width < 768
# st.info(f"Screen width: {width}px")

# card_data = [
#     {"title": "📄 Card 1", "text": "This is card 1", "image": "https://placekitten.com/400/200", "key": "card1"},
#     {"title": "📄 Card 2", "text": "This is card 2", "image": "https://placekitten.com/401/200", "key": "card2"},
#     {"title": "📄 Card 3", "text": "This is card 3", "image": "https://placekitten.com/402/200", "key": "card3"},
#     {"title": "📄 Card 4", "text": "This is card 4", "image": "https://placekitten.com/403/200", "key": "card4"},
# ]

# def get_random_color():
#     colors = ["#FF6B6B", "#4ECDC4", "#556270", "#C7F464", "#FFCC5C"]
#     return random.choice(colors)

# response = st.empty()

# # Use 2-column layout on mobile for better fit
# if is_mobile:
#     st.subheader("📱 Mobile View (2 Columns)")
#     rows = [card_data[i:i+2] for i in range(0, len(card_data), 2)]  # split into pairs
#     for row in rows:
#         cols = st.columns(2)
#         for col, item in zip(cols, row):
#             color = get_random_color()
#             with col:
#                 clicked = card(
#                     title=item["title"],
#                     text=item["text"],
#                     image=item["image"],
#                     key=item["key"],
#                     styles={
#                         "card": {
#                             "width": "100%",
#                             "height": "180px",
#                             "border-radius": "15px",
#                             "background": f"linear-gradient(135deg, {color}, #ffffff)",
#                             "color": "white",
#                             "box-shadow": "0 3px 6px rgba(0, 0, 0, 0.1)",
#                             "border": "1px solid #ccc",
#                             "text-align": "center",
#                             "padding": "10px",
#                             "margin": "0",
#                         },
#                         "title": {
#                             "font-size": "30px",
#                             "margin": "0 0 5px 0",
#                         },
#                         "text": {
#                             "font-size": "16px",
#                             "margin": "0",
#                         },
#                     }
#                 )
#                 if clicked:
#                     response.success(f"You clicked: {item['title']}")

# else:
#     st.subheader("💻 Desktop View (3 Columns)")
#     cols = st.columns(4)
#     for col, item in zip(cols, card_data):
#         color = get_random_color()
#         with col:
#             clicked = card(
#                 title=item["title"],
#                 text=item["text"],
#                 image=item["image"],
#                 key=item["key"],
#                 styles={
#                     "card": {
#                         "width": "100%",
#                         "height": "220px",
#                         "border-radius": "20px",
#                         "background": f"linear-gradient(135deg, {color}, #ffffff)",
#                         "color": "white",
#                         "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
#                         "border": "1px solid #bbb",
#                         "text-align": "center",
#                         "padding": "15px",
#                         "margin": "0",
#                     },
#                     "title": {
#                         "font-size": "35px",
#                         "margin": "0 0 10px 0",
#                     },
#                     "text": {
#                         "font-size": "18px",
#                         "margin": "0",
#                     },
#                 }
#             )
#             if clicked:
#                 response.success(f"You clicked: {item['title']}")

import streamlit as st
from streamlit_card import card
import sqlite3
import bcrypt
# import student_page
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

# def role_selection():
#     col1, col2 = st.columns(2)
#     with col1:
#         if card("Student", "", image="https://img.icons8.com/color/96/student-male--v1.png", key="student_card"):
#             st.session_state.role = "student"
#             st.rerun()

#         if card("Admin", "", image="https://img.icons8.com/color/96/admin-settings-male.png", key="admin_card"):
#             st.session_state.role = "admin"
#             st.rerun()

#     with col2:
#         if card("Therapist", "", image="https://img.icons8.com/color/96/psychology.png", key="therapist_card"):
#             st.session_state.role = "therapist"
#             st.rerun()

#         if card("Super Admin", "", image="https://img.icons8.com/color/96/super-mario.png", key="superadmin_card"):
#             st.session_state.role = "superadmin"
#             st.rerun()



def role_selection():
    st.subheader("👤 Select Your Role")

    # Detect screen width
    width = st_javascript("window.innerWidth")
    is_mobile = width is not None and width < 768

    role_cards = [
        {"title": "Student", "image": "https://img.icons8.com/color/96/student-male--v1.png", "key": "student_card"},
        {"title": "Admin", "image": "https://img.icons8.com/color/96/admin-settings-male.png", "key": "admin_card"},
        {"title": "Therapist", "image": "https://img.icons8.com/color/96/psychology.png", "key": "therapist_card"},
        {"title": "Super Admin", "image": "https://img.icons8.com/color/96/super-mario.png", "key": "superadmin_card"},
    ]

    # 2 columns on mobile, 4 on desktop
    cols_per_row = 2 if is_mobile else 4
    rows = [role_cards[i:i+cols_per_row] for i in range(0, len(role_cards), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            with col:
                if card(title=item["title"], image=item["image"], key=item["key"]):
                    st.session_state.role = item["title"].lower().replace(" ", "")
                    st.rerun()


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
import base64
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

set_custom_background(bg_color="#111111", sidebar_img=None)
def main():
    if not st.session_state.initialized:
        initialize_database()
        st.session_state.initialized = True

    if st.session_state.role is None:
        role_selection()
    elif not st.session_state.logged_in:
        if st.session_state.role == "student":
            student_login()
        else:
            login_user(st.session_state.role)
    else:
        show_dashboard(st.session_state.role)

if __name__ == "__main__":
    main()
