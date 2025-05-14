
import streamlit as st
import mysql.connector
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
from datetime import datetime
# import Queue

def create_connection():
    db = mysql.connector.connect(**config)
    return db

def create_database(db):
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS kabs_db")
    cursor.close()

def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'kabs_db'
    }
    db = mysql.connector.connect(**config)
    return db

def generate_student_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    result = cursor.fetchone()
    count = result[0] if result[0] is not None else 0
    current_year = datetime.now().year
    new_id = f"STUD-{current_year}-{count + 1:04}"
    return new_id


def create_students_table(db):
    cursor = db.cursor()
    create_students_table_query = """
    CREATE TABLE IF NOT EXISTS students (
        STUDENT_ID VARCHAR(20) PRIMARY KEY,
        STUDENT_NAME VARCHAR(255) NOT NULL,
        AGE INT,
        GENDER VARCHAR(20), 
        CLASS VARCHAR(255),
        STREAM VARCHAR(225),
        EMAIL VARCHAR(255),
        CONTACT VARCHAR(20),
        DATE_REGISTERED TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_students_table_query)
    db.commit()


def insert_student_record(db, STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, STREAM, EMAIL, CONTACT, DATE_REGISTERED):
    cursor = db.cursor()
    insert_query = """
    INSERT INTO students (STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, STREAM, EMAIL, CONTACT, DATE_REGISTERED) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (generate_student_id(db), STUDENT_NAME, AGE, GENDER, CLASS, STREAM, EMAIL, CONTACT, DATE_REGISTERED))
    db.commit()


def fetch_all_students(db):
    cursor = db.cursor()
    select_students_query = "SELECT STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, STREAM, EMAIL, CONTACT, DATE_REGISTERED FROM students"
    cursor.execute(select_students_query)
    students = cursor.fetchall()
    return students


def edit_student_record(db, student_id, new_name, new_age, new_gender, new_class, new_stream, new_email, new_contact, new_date_of_registration):
    cursor = db.cursor()
    update_student_query = """
    UPDATE students
    SET STUDENT_NAME = %s, AGE = %s, GENDER = %s, CLASS = %s, STREAM = %s, EMAIL = %s, CONTACT = %s, DATE_REGISTERED = %s
    WHERE STUDENT_ID = %s
    """
    student_data = (new_name, new_age, new_gender, new_class, new_stream, new_email, new_contact, new_date_of_registration, student_id)
    cursor.execute(update_student_query, student_data)
    db.commit()


def fetch_student_by_id(db, student_id):
    cursor = db.cursor()
    select_student_query = """
    SELECT STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, STREAM, EMAIL, CONTACT, DATE_FORMAT(DATE_REGISTERED, '%Y-%m-%d') AS DATE_REGISTERED
    FROM students
    WHERE STUDENT_ID = %s
    """
    cursor.execute(select_student_query, (student_id,))
    student = cursor.fetchone()
    return student


def display_students(db):
    students = fetch_all_students(db)
    if students:
        df = pd.DataFrame(students, columns=['STUDENT_ID', 'STUDENT NAME', 'AGE', 'GENDER', 'CLASS', 'STREAM', 'EMAIL', 'CONTACT', 'DATE OF REGISTRATION'])
        st.write(f'No. OF REGISTERED STUDENTS: {len(df)}')
        st.dataframe(df)
    else:
        st.write("No students found.")


def edit_student(db):
    if 'edit_student' in st.session_state:
        student = st.session_state.edit_student
        with st.form('Edit Student'):
            new_name = st.text_input("Enter new name", value=student[1])
            new_age = st.number_input("Enter new age", value=student[2])
            new_gender = st.selectbox("Select new gender", gender_list, index=gender_list.index(student[3]))
            new_class = st.selectbox("Select new class", class_list, index=class_list.index(student[4]))
            new_stream = st.selectbox("Select new stream", stream_list, index=stream_list.index(student[5]))
            new_email = st.text_input("Enter new email", value=student[6])
            new_contact = st.text_input("Enter new contact", value=student[7])
            new_date_of_registration = st.date_input("Date of Registration", value=pd.to_datetime(student[8]).date())

            update = st.form_submit_button("Update Student")
            if update:
                edit_student_record(db, student[0], new_name, new_age, new_gender, new_class, new_stream, new_email, new_contact, new_date_of_registration)
                st.success("Student record updated successfully.")
                del st.session_state.edit_student



def update_student_record(db, student_id, new_name, new_age, new_gender, new_class, new_stream, new_contact, new_email, new_date_of_registration):
    cursor = db.cursor()
    cursor.execute("USE kabs_db")
    update_student_query = """
    UPDATE students
    SET STUDENT_NAME = %s, AGE = %s, GENDER = %s, CLASS = %s, STREAM = %s, CONTACT = %s, EMAIL = %s, DATE_REGISTERED = %s
    WHERE STUDENT_ID = %s
    """
    student_data = (new_name, new_age, new_gender, new_class, new_stream, new_contact, new_email, new_date_of_registration, student_id)
    cursor.execute(update_student_query, student_data)
    db.commit()
    st.success("Student record updated successfully.")



def get_student_select_list(db):
    cursor = db.cursor()
    cursor.execute("SELECT STUDENT_ID, STUDENT_NAME FROM students")
    students = cursor.fetchall()
    select_list = [""] 
    select_list += [f"{student[0]} - {student[1]}" for student in students]
    return select_list


def search_edit_and_update_student(db):
    student_select_list = get_student_select_list(db)
    selected_student = st.sidebar.selectbox("Search Student", options=student_select_list, key="selected_student", help="Start typing or select a student.")
    
    selected_student_id = selected_student.split(" - ")[0] if selected_student else None
    if selected_student_id:
        if st.sidebar.checkbox('Open Record'):
            st.sidebar.write('---')
            student = fetch_student_by_id(db, selected_student_id)
            if student:
                student_dict = {
                    'STUDENT_ID': student[0],
                    'STUDENT_NAME': student[1],
                    'AGE': student[2],
                    'GENDER': student[3],
                    'CLASS': student[4],
                    'STREAM': student[5],
                    'CONTACT': student[6],
                    'EMAIL': student[7],
                    'DATE_OF_REGISTRATION': student[8]}
                st.sidebar.write(student_dict)
                st.sidebar.write('---')
                st.session_state.edit_student = student
                if 'edit_student' in st.session_state:
                    edit_student(db)
            else:
                st.error("Student record not found in the database.")


class_list = ['','S1', 'S2', 'S3', 'S4', 'S5', 'S6']
stream_list = ['',"EAST", "SOUTH", 'WEST', 'NORTH']
gender_list = ['','MALE','FEMALE']


def main():
    db = create_connection()
    create_students_table(db)


    if "search_edit_and_update_student" not in st.session_state:
        st.session_state.search_edit_and_update_student = search_edit_and_update_student

    


    register_menu = option_menu(
        menu_title='',
        orientation='horizontal',
        menu_icon='',
        options=['Register', 'Update_record', 'Queue', 'Database'],
        icons=['camera', 'person-circle', 'queue', 'database'],
        styles={
            "container": {"padding": "10!important", "background-color": 'black', 'border': '0.01px dotted red'},
            "icon": {"color": "red", "font-size": "12px"},
            "nav-link": {"color": "#d7c4c1", "font-size": "12px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
            "nav-link-selected": {"background-color": "green"},
        },
        key="register_menu")

    if register_menu == 'Register':
        with st.form('vendor'):
            col1, col2 = st.columns(2)
            name = col1.text_input("NAME", key="name")
            gender = col1.selectbox('GENDER', ['', 'MALE', 'FEMALE'])
            age = col1.number_input("AGE", value=None, min_value=0, step=1, format="%d")
            email = col1.text_input("EMAIL", placeholder='Enter a valid email address')  # Added email input
            student_class = col2.selectbox("CLASS", class_list)
            stream = col2.selectbox('STREAM', stream_list)
            contact = col2.text_input('CONTACT', placeholder='Enter phone number (e.g., +256712345678)')
            submit = col2.form_submit_button('Register student')
            if submit:
                generated_id = generate_student_id(db)  
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
                insert_student_record(db, generated_id, name, age, gender, student_class, stream, email, contact, current_date)  # Included email
                st.success(f"{name} : {gender} : {age} : {email} : {student_class} : {stream} : {contact} successfully registered")

    elif register_menu == 'Update_record':
        search_edit_and_update_student(db)
        

    elif register_menu == 'Queue':
        Queue.main()

    elif register_menu == "Database":
        display_students(db)
    db.close()

if __name__ == '__main__':
    main()
