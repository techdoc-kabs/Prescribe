import streamlit as st
from streamlit_card import card
import LogIn, SignUp
import student_tool_page
import streamlit as st
import base64
import os
import datetime
from datetime import datetime
import sqlite3
import LogIn
from streamlit_javascript import st_javascript


def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

pages = [
    {"title": '📝', "color": "#004d99", "text":"Appointments"},
    {"title": "🧑‍🤝‍🧑",   "color": "#660000", "text":"Support"},
    {"title": "💬",  "color": "#f39c12",  "text":"Chats"},
    {"title": "📚",  "color": "#27ae60", "text":"Self-help"},
    {"title": "📚.",  "color": "#27ae60", "text":"Content"},
    {"title": "📚_",  "color": "#27ae60", "text":"Profile"}
]

def fetch_student_record(username):
    try:
        db = create_connection()
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


import student_tool_page
def main():
    screen_width = st_javascript("window.innerWidth", key="screen_width_js")
    is_mobile = screen_width and screen_width <= 768
    username = st.session_state.get("username", "Student")
    st.markdown(f"## 🎓 Welcome, {username}")
    if username:
        if st.session_state.get("selected_page"):
            if st.button("🔙 Return to Menu"):
                st.session_state["selected_page"] = None
                st.rerun()
            student_details = fetch_student_details_by_username(username)
            
            st.write(student_details)
            if student_details:
                st.session_state.update({
                    "student_id": student_details.get("student_id"),
                    "name": student_details.get("name"),
                    "gender": student_details.get("gender"),
                    "age": student_details.get("age"),
                    "student_class": student_details.get("student_class"),
                    "stream": student_details.get("stream"),
                    "contact": student_details.get("contact"),
                    "email": student_details.get("email"),
                    "role": student_details.get("role"),})
            

            selected_page = st.session_state["selected_page"]
    
            if selected_page:
                st.write('Ok continue')
                if st.button("🔙 Return to Menu"):
                    st.session_state["selected_page"] = None
                    st.session_state["selected_appointment"] = None
                    st.rerun()

                if selected_page == "📝":
                    st.write('ITS ME')
                    appointment_details = sorted(
                        fetch_appointment_details_by_username(username),
                        key=lambda x: (x["appointment_date"], x["appointment_time"]),
                        reverse=True
                    )

                    if appointment_details:
                        if "selected_appointment" not in st.session_state:
                            st.session_state.selected_appointment = None

                        if st.session_state.selected_appointment is None:
                            num_cols = 2 if is_mobile else 4
                            cols = st.columns(num_cols)
                            for index, appointment in enumerate(appointment_details):
                                appointment_id = appointment["appointment_id"]
                                tool_statuses = appointment["tool_status"].split(",") if appointment["tool_status"] else []
                                appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}"
                                status_text = "Completed ✅" if all(s.strip() == "Completed" for s in tool_statuses) else "Pending ⏳"
                                title = ordinal(len(appointment_details) - index)

                                col = cols[index % num_cols]
                                with col:
                                    clicked = card(
                                        title=title,
                                        text=f"{appointment_id} \n {status_text}",
                                        styles={
                                            "card": {
                                                "width": "100%",
                                                "height": "200px",
                                                "border-radius": "30px",
                                                "background": appointment_color,
                                                "color": "white",
                                                "text-align": "center",
                                                "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                                            },
                                            "text": {"font-family": "serif"},
                                        },
                                    )
                                    if clicked:
                                        st.session_state.selected_appointment = appointment
                                        st.session_state.appointment_id = appointment_id
                                        st.rerun()
                        else:
                            if st.button("🔙 Return to Appointments"):
                                st.session_state.selected_appointment = None
                                st.rerun()
                            student_tool_page.main()
                    else:
                        st.info("No appointments available at the moment.")

                elif selected_page == "🧑‍🤝‍🧑":
                    get_help.main()

                elif selected_page == "💬":
                    st.subheader("Chats Page")

                elif selected_page == "📚":
                    video_display.main()

                elif selected_page == "📚_" or selected_page.upper() == "PROFILE":
                    st.subheader("Profile")
                    student_info = fetch_student_record(username)
                    if student_info:
                        st.write(student_info)

            # If no page selected, show menu
            else:
                num_cols = 2 if is_mobile else 4
                cols = st.columns(num_cols)
                for index, page in enumerate(pages):
                    col = cols[index % num_cols]
                    with col:
                        clicked = card(
                            title=page["title"],
                            text=page["text"],
                            key=page["title"],
                            styles={
                                "card": {
                                    "width": "100%",
                                    "height": "250px",
                                    "border-radius": "80px",
                                    "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
                                    "color": "white",
                                    "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                                    "text-align": "center",
                                },
                                "text": {"font-size": "30px"},
                                "title": {"font-size": "60px"},
                            },
                        )
                        if clicked:
                            st.session_state["selected_page"] = page["title"]
                            st.rerun()
if __name__ == "__main__":
    main()
