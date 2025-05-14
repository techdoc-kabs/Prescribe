import streamlit as st
import bcrypt
import sqlite3
# from pushbullet import Pushbullet
from datetime import datetime

# API_KEY = st.secrets['push_API_KEY']
# pb = Pushbullet(API_KEY)

def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_user_activity_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                name TEXT NOT NULL,
                login_time TEXT NOT NULL,
                logout_time TEXT DEFAULT NULL,
                duration TEXT DEFAULT NULL
            );
            """
            cursor.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Error creating user_activity_log table: {e}")
        finally:
            conn.close()

def log_login(username, name):
    conn = create_connection()
    if conn:
        try:
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = conn.cursor()
            query = """INSERT INTO user_activity_log (username, name, login_time) VALUES (?, ?, ?)"""
            cursor.execute(query, (username, name, login_time))
            conn.commit()
            return login_time
        except sqlite3.Error as e:
            st.error(f"Error logging login: {e}")
        finally:
            conn.close()

def log_logout(username):
    conn = create_connection()
    if conn:
        try:
            logout_time = datetime.now()
            cursor = conn.cursor()
            query = """SELECT id, login_time FROM user_activity_log WHERE username = ? ORDER BY id DESC LIMIT 1"""
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                log_id = result["id"]
                login_time = datetime.strptime(result["login_time"], "%Y-%m-%d %H:%M:%S")
                duration = str(logout_time - login_time)
                update_query = """UPDATE user_activity_log SET logout_time = ?, duration = ? WHERE id = ?"""
                cursor.execute(update_query, (logout_time.strftime("%Y-%m-%d %H:%M:%S"), duration, log_id))
                conn.commit()
        except sqlite3.Error as e:
            st.error(f"Error logging logout: {e}")
        finally:
            conn.close()

def authenticate_student(username, password):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                SELECT student_id, name, gender, age, student_class, stream, contact, username, email, password, role
                FROM student_users
                WHERE username = ?
            """
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                if check_password(password, user['password']):
                    login_time = log_login(user['username'], user['name'])  # Log login in DB
                    st.session_state.update({
                        "signedout": False,
                        "username": user['username'],
                        "user_role": user['role'],
                        "name": user['name'],
                        "email": user['email'],
                        "student_class": user['student_class'],
                        "stream": user['stream'],
                        "login_time": login_time
                    })
                    # if "notified" not in st.session_state or not st.session_state.notified:
                    #     pb.push_note("🔔 Login Alert",
                    #                  f"User: {user['name']} ({user['username']})\n"
                    #                  f"Email: {user['email']}\n"
                    #                  f"Tel: {user['contact']}\n"
                    #                  f"Date: {login_time.split()[0]}\n"
                    #                  f"Time: {login_time.split()[1]}")
                    #     st.session_state.notified = True
                    return user
                else:
                    st.warning("Login failed. Incorrect username or password.")
                    return None
            else:
                st.warning("Login failed. User not found.")
                return None
        except sqlite3.Error as e:
            st.error(f"Error during authentication: {e}")
        finally:
            connection.close()

def logout():
    if "username" in st.session_state:
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_name = st.session_state.get('name', 'Unknown')
        user_username = st.session_state.get('username', 'Unknown')

        log_logout(user_username)

        # pb.push_note("🚪 Logout Alert",
        #              f"User: {user_name} ({user_username})\n"
        #              f"Date: {logout_time.split()[0]}\n"
        #              f"Time: {logout_time.split()[1]}")

        st.session_state.clear()
        st.rerun()

def login_form():
    with st.expander(f'## Sign In', expanded=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_student(username, password)
            if user:
                st.sidebar.success(f"Welcome, {user['name']}!")

def main():
    db = create_connection()
    create_user_activity_table()
    if "signedout" not in st.session_state:
        st.session_state["signedout"] = True
    if st.session_state["signedout"]:
        login_form()
    else:
        if st.sidebar.button("Sign Out"):
            logout()

if __name__ == '__main__':
    main()
