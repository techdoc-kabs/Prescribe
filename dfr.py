import streamlit as st
from streamlit_card import card
import mysql.connector
import LogIn, SignUp
import student_forms_page
import video_display
import streamlit as st
import base64
import os

# st.set_page_config(initial_sidebar_state='expanded')
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
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'mhpss_db'
    }
    return mysql.connector.connect(**config)

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
    {"title": "APPOINTMENTS", "icon": "clipboard-check", "color": "#004d99", "image": "assessment.png", "text":"🛗"},
    {"title": "SUPPORT", "icon": "lifebuoy", "color": "#660000", "image": "support.png", "text":"🛗"},
    {"title": "CHAT ROOM", "icon": "chat-dots", "color": "#f39c12", "image": "chat.png", "text":"🛗"},
    {"title": "CONTENT", "icon": "bell", "color": "#27ae60", "image": "content.png", "text":"CONTENT"},
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
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_users WHERE username = %s", (username,))
        record = cursor.fetchone()
        db.close()
        return record
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return None


def fetch_student_details_by_username(username):
    connection = create_connection() 
    student_details = {}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM student_users WHERE username = %s", (username,))
            student_details = cursor.fetchone() 
        except mysql.connector.Error as e:
            st.error(f"Error fetching student details: {e}")
        finally:
            cursor.close()
            connection.close()
    return student_details


def fetch_appointment_details_by_username(username):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)  
            query = """
                SELECT a.appointment_id, a.name, a.appointment_type, a.screen_type, a.term,  
                       a.appointment_date, a.appointment_time, a.clinician_name, a.reason, 
                       s.student_class, s.stream
                FROM screen_appointments a
                JOIN student_users s ON a.student_id = s.student_id
                WHERE s.username = %s
            """
            cursor.execute(query, (username,))
            appointments = cursor.fetchall()
            return appointments
        except mysql.connector.Error as e:
            st.error(f"Error fetching appointment details: {e}")
            return []
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



# def fetch_appointment_details_by_username(username):
#     connection = create_connection()
#     if connection:
#         try:
#             cursor = connection.cursor(dictionary=True)
            
#             query = """
#                 SELECT a.appointment_id, a.name, a.appointment_type, a.screen_type, a.term, 
#                        a.appointment_date, a.appointment_time, a.clinician_name, a.reason, 
#                        s.student_class, s.stream,
#                        GROUP_CONCAT(DISTINCT r.tool_status ORDER BY r.tool_status SEPARATOR ', ') AS tool_status
#                 FROM screen_appointments a
#                 JOIN student_users s ON a.student_id = s.student_id
#                 LEFT JOIN requested_tools_students r ON a.appointment_id = r.appointment_id
#                 WHERE s.username = %s
#                 GROUP BY a.appointment_id
#             """
            
#             cursor.execute(query, (username,))
#             appointments = cursor.fetchall()
#             return appointments

#         except mysql.connector.Error as e:
#             st.error(f"Error fetching appointment details: {e}")

#         finally:
#             cursor.close()
#             connection.close()

#     return []




def main():
    set_custom_background(bg_color="#2c3e50", sidebar_img=None)
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ''
    page_menu = get_menu()
    if st.session_state["username"]:
        st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
        student_info = fetch_student_record(st.session_state["username"])
        st.sidebar.write(student_info)
        if st.sidebar.button(":red[Sign Out]"):
            username = st.session_state["username"]
            st.toast(f"👋 :green[Bye] :green[{username}]")    
            st.session_state.clear()  
            st.rerun()
        if st.session_state["selected_page"]:
            if st.session_state["selected_page"] == "APPOINTMENTS":
                appointment_details = fetch_appointment_details_by_username(st.session_state.username)
                appointment_details = sorted(appointment_details, key=lambda x: x.get("appointment_id", 0), reverse=True)
                if appointment_details:
                    if "selected_appointment" not in st.session_state:
                        st.session_state.selected_appointment = None 
                    if st.button("🏠 Return to Main Menu"):
                        st.session_state["selected_page"] = None
                        st.session_state.selected_appointment = None
                        st.rerun()
                    if st.session_state.selected_appointment is None:
                        col1, col2 = st.columns(2)
                        for index, appointment in enumerate(appointment_details):
                            appointment_id = appointment["appointment_id"]
                            # tool_statuses = appointment["tool_status"].split(", ") if appointment["tool_status"] else []
                            appointment_color = f"#{hash(str(appointment_id)) % 0xFFFFFF:06x}" 
            
                            if all(status.strip() == "Completed" for status in tool_statuses):
                                status_text = "Completed ✅"
                            else:
                                status_text = "Pending forms to fill"

                
                            with col1 if index % 2 == 0 else col2:
                                hasClicked = card(
                                    title=ordinal(len(appointment_details) - index),
                                    text=f"{appointment_id} \",
                                    url=None,
                                    styles={
                                        "card": {
                                            "width": "280px",
                                            "height": "200px",
                                            "border-radius": "30px",
                                            "background": appointment_color,
                                            "color": "white",
                                            "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                                            "border": f"2px solid {appointment_color}",
                                            "text-align": "center",
                                        },
                                        "text": {"font-family": "serif"},
                                    },
                                )

                                if hasClicked:
                                    st.session_state.selected_appointment = appointment
                                    st.rerun()

                    else:
                        if st.button("🔙 Return to Appointments"):
                            st.session_state.selected_appointment = None
                            st.rerun()
                        student_forms_page.main()
                else:
                    st.info("No pending appointments, please wait for updates.")

                





        elif st.session_state["selected_page"] == "SUPPORT":
            st.subheader("Support Page")

        elif st.session_state["selected_page"] == "CHAT ROOM":
            st.subheader("Chats Page")
        
        elif st.session_state["selected_page"] == "CONTENT":
            video_display.main()
           
        elif st.session_state["selected_page"] == "PROFILE":
            st.subheader("Profile Page")
            student_info = fetch_student_record(st.session_state["username"])
            if student_info:
                st.write(student_info)

        else:
            col1, col2 = st.columns(2)
            for index, page in enumerate(pages):
                with col1 if index % 2 == 0 else col2:
                    if card(
                        title=page["title"],
                        text=page['text'],
                        image=page["icon"],
                        key=page["title"],
                        styles={
                            "card": {
                                "width": "300px",
                                "height": "250px",
                                "border-radius": "30px",
                                "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
                                "color": "white",
                                "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                                "border": f"2px solid {page['color']}",
                                "text-align": "center",
                            },
                            "text": {"font-family": "serif", "font-size": "16px"},
                        },
                    ):
                        st.session_state["selected_page"] = page["title"]
                        st.rerun()

if __name__ == "__main__":
    main()

