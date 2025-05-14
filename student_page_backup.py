import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_navigation_bar import st_navbar
import mysql.connector
import LogIn, SignUp
import student_forms_page
import video_display
from streamlit_card import card
st.set_page_config(initial_sidebar_state="expanded")
st.logo('brain.gif')

pages = ['ASSESSMENT', 'SUPPORT', 'CHATS', 'UPDATES','PROFIILE']


styles = {
    "nav": {
        'font-family': 'Haettenschweiler, sans-serif',
        "background-color": "#4B5320",
        "justify-content": "center",
        'border-radius': '20px',
        'padding': '15',
        'font-size': '26px',
        'color':'#4B5320',

    },
    
    



    "active": {
        "color": "var(--text-color)",
        "background-color": "green",
        "font-weight": "normal",
        "padding": "10px",
        'border-radius': '20px'
    },


    "hover": {
        "color": "var(--text-color)",
        "background-color": "red",
        "font-weight": "normal",
        "padding": "10px",
        'border-radius': '20'
    },
}


def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'mhpss_db'
    }
    db = mysql.connector.connect(**config)
    return db

if "username" not in st.session_state:
    st.session_state["username"] = None

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


def get_menu():
    if st.session_state["username"]:
        st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
        return st_navbar(pages, options=True, styles=styles)
    
    else:
        user_menu = option_menu(
            menu_title='',
            orientation='horizontal',
            options=['LogIn', 'Register'],
            icons=['key', 'book'],
            styles={
                "container": {"padding": "10!important", "background-color": 'black', 'border': '0.01px dotted red'},
                "icon": {"color": "red", "font-size": "12px"},
                "nav-link": {"color": "#d7c4c1", "font-size": "12px", "font-weight": 'bold', "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "green"},
            },
            key="user_menu"
        )

        if user_menu == 'Register':
            SignUp.main()
        elif user_menu == 'LogIn':
            LogIn.main()
        return None 


def fetch_appointment_details_by_username(username):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)  
            query = """
                SELECT a.appointment_id, a.name, a.appointment_type, a.appointment_date, 
                       a.appointment_time, a.clinician_name, a.reason
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

def fetch_student_details_by_username(username):
    connection = create_connection() 
    student_details = {}
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM student_users WHERE username = %s", (username,))
            student_details = cursor.fetchone() 
        except Error as e:
            st.error(f"Error fetching student details: {e}")
        finally:
            cursor.close()
            connection.close()
    return student_details


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



def set_custom_background_and_theme(bg_color="skyblue", text_color="black", sidebar_img=None, theme_color="#FF6347"):
    
    sidebar_img_base64 = ""
    if sidebar_img:
        try:
            with open(sidebar_img, "rb") as img_file:
                sidebar_img_base64 = base64.b64encode(img_file.read()).decode()
        except FileNotFoundError:
            st.warning("Sidebar image not found. Using default background.")

    page_style = f"""
        <style>
        /* Background color */
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {bg_color};
            background-size: 140%;
            background-position: top left;
            background-repeat: repeat;
            background-attachment: local;
            padding-top: 0px;
        }}
        /* Sidebar Image */
        [data-testid="stSidebar"] > div:first-child {{
            {"background-image: url('data:image/png;base64," + sidebar_img_base64 + "');" if sidebar_img else ""}
            background-position: center; 
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Header Styling */
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
            padding-top: 0px;
            color: {text_color};
        }}
        /* Toolbar Styling */
        [data-testid="stToolbar"] {{
            right: 2rem;
        }}
        /* Set Text color */
        .css-1d391kg {{
            color: {text_color};
        }}
        /* Customize Theme color */
        [data-testid="stSidebar"] {{
            background-color: {theme_color} !important;
        }}
        </style>
    """
    
    # Apply the custom background and theme
    st.markdown(page_style, unsafe_allow_html=True)

    

def main():
    set_custom_background(bg_color="#2c3e50", sidebar_img=None)
    
    st.markdown(
    """
    <style>
        .mental-health-text {
            position: fixed;
            top: 40px;
            left: 5px;
            width: 300px;
            font-size: 40px;
            font-weight: bold;
            # font-family: 'Courier New', monospace;
            font-family: 'Mistral', monospace;
            font-family: 'Edwardian Script ITC',monospace;
            color: #D4AF37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            line-height: 0.9;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)
    st.sidebar.markdown(
    '<div class="mental-health-text">Mental Health  <br> Is <br> Wealth</div>'
    '</div>',
    unsafe_allow_html=True
)

    
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ''

    page_menu = get_menu()
    if st.session_state["username"]:
        student_info = fetch_student_record(st.session_state["username"])
        st.sidebar.write(student_info)
        if st.sidebar.button(":red[Sign Out]"):
            username = st.session_state["username"]
            st.toast(f"👋 :green[Bye] :green[{username}]")    
            st.session_state.clear()  
            st.rerun()    

        if page_menu == 'ASSESSMENT':
            if st.session_state.username:
                student_details = fetch_student_details_by_username(st.session_state.username)
                if student_details:
                    st.session_state.student_id = student_details.get("student_id")
                    st.session_state.name = student_details.get("name")
                    st.session_state.gender = student_details.get("gender")
                    st.session_state.age = student_details.get("age")
                    st.session_state.student_class = student_details.get("student_class")
                    st.session_state.stream = student_details.get("stream")
                    st.session_state.contact = student_details.get("contact")
                    st.session_state.email = student_details.get("email")
                    st.session_state.role = student_details.get("role")

                appointment_details = fetch_appointment_details_by_username(st.session_state.username)
                if appointment_details:
                    latest_appointment = max(appointment_details, key=lambda x: x["appointment_id"])  # Get the latest appointment
                    appointment_id = latest_appointment.get("appointment_id")
                    appointment_date = latest_appointment.get("appointment_date")
                    with st.expander(f'{appointment_id}', expanded=True):
                        st.session_state.appointment_id = latest_appointment.get("appointment_id")
                        st.session_state.appointment_type = latest_appointment.get("appointment_type")
                        st.session_state.appointment_time = latest_appointment.get("appointment_time")
                        st.session_state.clinician_name = latest_appointment.get("clinician_name")
                        st.session_state.appointment_date = latest_appointment.get("appointment_date")
                        st.session_state.reason = latest_appointment.get("reason")
                        student_forms_page.main()
                else:
                    st.info('No pending assessments exercise, plese wait for Updates')
        

        elif page_menu == 'SUPPORT':
            email_alerts.main()
        
        elif page_menu == 'CHATS':
            st.info('Chatroom Content')
        
        elif page_menu == 'UPDATES':
            # set_custom_background_and_theme(bg_color="#FF6347", text_color="black", sidebar_img=None, theme_color="#FF6347")
            video_display.main()


if __name__ == '__main__':
    main()
