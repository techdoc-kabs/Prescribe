import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_navigation_bar import st_navbar
import appointments
import mysql.connector
import pandas as pd
import datetime
from datetime import datetime
# import submissions, forms_link, share_tools, consultations
# import screening_page, captured_responses, results_filled, requested_tools
# import LogIn, SignUp, profile, entire_file, appoint_screen, appoint_consult
import base64, consultations
from streamlit_card import card
import video_handles,appoint_screen, appoint_consult, entire_file
import sqlite3
st.set_page_config(initial_sidebar_state="expanded")
st.logo('brain.gif')
st.markdown(
    """
    <style>
        .mental-health-container {
            position: fixed;
            top: 5px;
            left: 20px;
            width: 380px;
            background: rgba(255, 255, 255, 0.1);
            padding: 2px;
            border-radius: 80px;
            text-align: center;
            box-shadow: 0px 4px 12px rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            animation: gradientGlow 3s infinite alternate;
        }

        @keyframes gradientGlow {
            from {
                background: linear-gradient(135deg, #4A90E2, rgba(255, 255, 255, 0.2));
            }
            to {
                background: linear-gradient(135deg, #145DA0, rgba(255, 255, 255, 0.2));
            }
        }

        .mental-health-text {
            font-size: 45px;
            font-weight: bold;
            # font-family: 'Courier New', monospace;
            font-family: 'Mistral', monospace;
            font-family: 'Edwardian Script ITC',monospace;
            color: #D4AF37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            line-height: 0.6;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.markdown(
        # '<div class="mental-health-container">'s
        '<div class="mental-health-text">Mental Health  <br> Is <br> Wealth</div>'
        '</div>',
        unsafe_allow_html=True
    )


pages = ['HOME','SCHEDULES','WORKUP', 'ANALYSIS','ARCHIVES','ONLINE_SUPPORT', 'UPDATES','SETTINGS']
styles = {
    "nav":{
    
        'font-family': 'Haettenschweiler, sans-serif',
        'text-align':'center',
        'color':'#D4AF37',
        'background-color': '#4A90E2',
        'border-radius': '5px',
        'font-size': '28px',
                    
    },

    "img": {
        "padding-right": "20px",
    },
    
    "span": {
        "color": "#D4AF37",
        "border-radius": "0.5rem",
        "padding": "0.4375rem 0.625rem",
        "margin": "0 0.125rem",
    },

    "active": {
        "color": "var(--text-color)",
        "background-color": "green",
        "font-weight": "normal",
        "padding": "5px",
    },


    "hover": {
        "background-color": "red",
    },

}


page_menu = st_navbar(pages, options=False, styles=styles)


import sqlite3
import streamlit as st

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables access by column name
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def get_student_appointment_list(db):
    cursor = db.cursor()
    cursor.execute("SELECT appointment_id, appointment_type, student_id, student_name, appointment_date, appointment_time, clinician_name, reason FROM appointments")
    students = cursor.fetchall()
    select_list = [""]
    select_list += [f"{s[0]} - {s[1]} - {s[2]} {s[2]}, {s[3]}, {s[4]}, {s[5]}, {s[6]}" for s in students]
    return select_list

def fetch_appointment_by_id(db, appointment_id):
    cursor = db.cursor()
    select_query = """
        SELECT appointment_id, student_id, student_name, appointment_date, appointment_time, clinician_name, reason, appointment_type
        FROM appointments
        WHERE appointment_id = ?
    """
    cursor.execute(select_query, (appointment_id,))
    return cursor.fetchone()

def get_student_list(db):
    cursor = db.cursor()
    cursor.execute("SELECT student_id, student_name FROM students")
    students = cursor.fetchall()
    select_list = [""]
    select_list += [f"{s[0]} - {s[1]}" for s in students]
    return select_list

def fetch_student_by_id(db, student_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    return cursor.fetchone()

def fetch_all_roles(db):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT role FROM users")
    roles = cursor.fetchall()
    return [r[0] for r in roles]

def fetch_appointments(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("APP-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type
        FROM appointments
        WHERE appointment_id = ?
        """
        cursor.execute(query, (search_input.strip(),))
    else:
        name_parts = search_input.strip().split()
        query_conditions = []
        params = []

        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("student_name LIKE ?")
            query_conditions.append("student_name LIKE ?")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("student_name LIKE ?")
            params.append(f"%{search_input}%")

        query = f"""
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type
        FROM appointments
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))
    return cursor.fetchall()

def fetch_students(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("STUD-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, age, gender, class, stream
        FROM students
        WHERE student_id = ?
        """
        cursor.execute(query, (search_input.strip(),))
    else:
        name_parts = search_input.strip().split()
        query_conditions = []
        params = []

        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("student_name LIKE ?")
            query_conditions.append("student_name LIKE ?")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("student_name LIKE ?")
            params.append(f"%{search_input}%")

        query = f"""
        SELECT student_id, student_name, age, gender, class, stream
        FROM students
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))

    return cursor.fetchall()


@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("image.jpg")
img = get_img_as_base64("IMG.webp")
back_img = get_img_as_base64('backed.jpg')



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




class MultiApp:
    def __init__(self):
        self.apps = []
        
    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func 
        })
    def run(self):
        db = create_connection() 
        set_custom_background(bg_color=" #2c3e50 ", sidebar_img=img)
        if page_menu =='SCHEDULES':
            schedule_menu = option_menu(
                                menu_title='',
                                orientation='horizontal',
                                menu_icon='',
                                options=['SCREENNG', 'CONSULTATION','GROUP SESSION'],
                                icons=['book','hospital', 'people'],
                                styles={
                                    "container": {"padding": "8!important", "background-color": 'black','border': '0.01px dotted red'},
                                    "icon": {"color": "red", "font-size": "15px"},
                                    "nav-link": {"color": "#d7c4c1", "font-size": "15px","font-weight":'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                                    "nav-link-selected": {"background-color": "green"},
                                },
                                key="archives_menu")


            if schedule_menu == 'SCREENNG':
                appoint_screen.main()
            elif schedule_menu == 'CONSULTATION':
                appoint_consult.main()
            elif schedule_menu == 'GROUP SESSION':
                st.write('working on it')

    
        elif page_menu == 'WORKUP':
            consultations.main()

        elif page_menu == 'ARCHIVES':
            with st.sidebar:
                archives_menu = option_menu(
                                menu_title='',
                                orientation='horizontal',
                                menu_icon='',
                                options=['Files', 'Database'],
                                icons=['folder','database'],
                                styles={
                                    "container": {"padding": "8!important", "background-color": 'black','border': '0.01px dotted red'},
                                    "icon": {"color": "red", "font-size": "15px"},
                                    "nav-link": {"color": "#d7c4c1", "font-size": "15px","font-weight":'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                                    "nav-link-selected": {"background-color": "green"},
                                },
                                key="archives_menu")
            if archives_menu =='Files':
                file_menu = option_menu(
                                menu_title='',
                                orientation='horizontal',
                                menu_icon='',
                                options=['View', 'Print', 'Share'],
                                icons=['eye', 'printer','share'],
                                styles={
                                    "container": {"padding": "8!important", "background-color": 'black','border': '0.01px dotted red'},
                                    "icon": {"color": "red", "font-size": "15px"},
                                    "nav-link": {"color": "#d7c4c1", "font-size": "15px","font-weight":'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                                    "nav-link-selected": {"background-color": "green"},
                                },
                                key="file_menu")
                if file_menu  == 'View':
                    entire_file.main()
        
        elif page_menu == 'UPDATES':
            video_handles.main()


app = MultiApp()
app.run()




