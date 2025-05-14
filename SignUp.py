import streamlit as st
import bcrypt
import sqlite3
from datetime import datetime
# from pushbullet import Pushbullet
import threading 

# API_KEY = st.secrets["push_API_KEY"]
# pb = Pushbullet(API_KEY)

def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def generate_student_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT student_id FROM student_users ORDER BY registration_date DESC LIMIT 1")
    last_id = cursor.fetchone()
    
    current_year = datetime.now().year
    if last_id:
        last_number = int(last_id[0].split('-')[-1])
        new_id = f"STUD-{current_year}-{last_number + 1:04}"
    else:
        new_id = f"STUD-{current_year}-0001"
    
    return new_id

def create_student_users_table():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_users (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    student_class TEXT NOT NULL,
                    stream TEXT NOT NULL,
                    contact TEXT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    registration_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
        except sqlite3.Error as e:
            st.error(f"Error creating student_users table: {e}")
        finally:
            connection.close()

def send_pushbullet_notification(name, username, email, student_id, gender, age, student_class, stream, contact, role, registration_date):
    message = (
        f"🆔 {student_id}\n"
        f"👤 {name}\n"
        f"{gender}\n"
        f"{age} years\n"
        f"{student_class} - {stream}\n"
        f"📞 {contact or '--'}\n"
        f"📧 {email or '--'}\n"
        f"Username: {username}\n"
        f"Role: {role}\n"
        f"📅 {registration_date}\n"
    )
    # threading.Thread(target=pb.push_note, args=("🎋Registration Alert", message)).start()

def insert_students(name, gender, age, student_class, stream, contact, username, email, password, role):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT username FROM student_users WHERE username = ?", (username,))
            if cursor.fetchone():
                st.warning("Username already exists. Try another one.")
                return
            student_id = generate_student_id(connection)
            hashed_password = hash_password(password)
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                INSERT INTO student_users 
                (student_id, name, gender, age, student_class, stream, contact, username, email, password, role, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (student_id, name, gender, age, student_class, stream, contact, username, email, hashed_password, role, registration_date))
            connection.commit()
            send_pushbullet_notification(name, username, email, student_id, gender, age, student_class, stream, contact, role, registration_date)
            st.success("Account created successfully! Please log in.")
        except sqlite3.Error as e:
            st.error(f"Error during user registration: {e}")
        finally:
            connection.close()

class_list = ['', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6']
stream_list = ['', "EAST", "SOUTH", 'WEST', 'NORTH']
gender_list = ['', 'MALE', 'FEMALE']

def sign_up_form():
    db = create_connection()
    with st.form("signup_form1", clear_on_submit=False):
        col1, col2 = st.columns(2)

        name = col1.text_input("NAME (:red[required *])")
        gender = col1.selectbox("GENDER (:red[required *])", gender_list)
        age = col1.number_input("AGE (:red[required *])", min_value=0, step=1, format="%d")
        student_class = col1.selectbox("CLASS (:red[required *])", class_list)  
        stream = col1.selectbox("STREAM (:red[required *])", stream_list)
        email = col1.text_input("EMAIL (Optional)", placeholder="Enter a valid email address")

        username = col2.text_input("Username (:red[required *])")
        password = col2.text_input("Password (:red[required *])", type="password")
        confirm_password = col2.text_input("Confirm Password (:red[required *])", type="password")
        contact = col2.text_input("CONTACT (Optional)", placeholder="Enter phone number (e.g., +256712345678)")
        role = col2.selectbox("Role", ["Student"])

        submit = st.form_submit_button(":green[Register]")

    if submit:
        if not name or not username or not password or not student_class or not stream or not age or not gender:
            st.error("Please fill in all required fields.")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        else:
            insert_students(name, gender, age, student_class, stream, contact, username, email, password, role)

def main():
    create_student_users_table()
    sign_up_form()

if __name__ == '__main__':
    main()

