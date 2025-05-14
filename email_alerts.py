import streamlit as st
# import pywhatkit
import pyautogui
import json
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage
import pandas as pd
import mysql.connector
import os
CONTACTS_FILE = "contacts.json"
EMAILS_FILE = "emails.json"  


def load_contacts():
    try:
        with open(CONTACTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_contacts(contacts):
    with open(CONTACTS_FILE, "w") as file:
        json.dump(contacts, file, indent=4)


def load_emails():
    try:
        with open(EMAILS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_emails(emails):
    with open(EMAILS_FILE, "w") as file:
        json.dump(emails, file, indent=4)


def send_message_now(selected_contacts, text_msg, contacts):
    for contact in selected_contacts:
        to_phone = contacts[contact]
        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=to_phone,
                message=text_msg,
                wait_time=15
            )
            time.sleep(2)
            if st.checkbox(f'Close WhatsApp Web tab after sending'):
                pyautogui.hotkey('ctrl', 'w')
            st.success(f"Message sent successfully to {contact}!")
        except Exception as e:
            st.error(f"An error occurred while sending message to {contact}: {e}")


def schedule_message(time_hour, time_min, text_msg, contacts, to_phone):
    try:
        pywhatkit.sendwhatmsg(
            phone_no=to_phone,
            message=text_msg,
            time_hour=time_hour,
            time_minute=time_min)
        st.success(f"Message scheduled for {time_hour}:{time_min}!")
    except Exception as e:
        st.error(f"An error occurred while scheduling message: {e}")


EMAIL_LOG_FILE = "email_logs.json"


def send_email_with_attachments(subject, body, to, attachments):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    to_emails = [email.strip() for email in to.split(',')]
    msg['to'] = ", ".join(to_emails) 
    
    user = st.secrets['U']
    msg['from'] = user
    password = st.secrets['SECRET']
    
    for file in attachments:
        file_name = file.name
        msg.add_attachment(file.read(), maintype='application', subtype='octet-stream', filename=file_name)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"Error sending email: {e}")




def save_email_log(subject, message, recipients, email_address, attachments):
    logs = load_email_logs()
    current_time = datetime.now()
    attachment_names = [file.name for file in attachments]
    
    log_entry = {
        "subject": subject,
        "message": message,
        "recipients": ', '.join(recipients),
        'email_address': email_address,
        'attachments': attachment_names,  # Storing only file names
        "time": current_time.strftime("%H:%M:%S"),
        "date": current_time.strftime("%Y-%m-%d")
    }
    logs.append(log_entry)
    with open(EMAIL_LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)



def load_email_logs():
    try:
        with open(EMAIL_LOG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  


def save_email_log(subject, message, recipients, email_address, attachments):
    logs = load_email_logs()
    current_time = datetime.now()

    attachment_names = [file.name for file in attachments]
    
    log_entry = {
        "subject": subject,
        "message": message,
        "recipients": ', '.join(recipients),
        'email_address': email_address,
        'attachments': attachment_names, 
        "time": current_time.strftime("%H:%M:%S"),
        "date": current_time.strftime("%Y-%m-%d")
    }
    logs.append(log_entry)
    with open(EMAIL_LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)



import urllib.parse
FILE_PATH = "submitted.json"

def load_data_as_dataframe():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
            return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["Name", "Age", "Sex", "Gender", "Class", "Message"])

def generate_form_link(name):
    form_url = f"http://10.32.147.131:8510/?name={urllib.parse.quote(name)}"  # Use the correct URL path
    return form_url

def send_email_with_form_link(subject, body, to, attachments, name):
    form_link = generate_form_link(name)
    body_with_link = f"{body}\n\nPlease fill out the form at the following link: {form_link}"
    send_email_with_attachments(subject, body_with_link, to, attachments)



def get_student_select_list(db):
    cursor = db.cursor()
    cursor.execute("SELECT STUDENT_ID, STUDENT_NAME FROM students")
    students = cursor.fetchall()
    select_list = [""] 
    select_list += [f"{student[0]} - {student[1]}" for student in students]
    return select_list


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


def fetch_all_students(db):
    cursor = db.cursor()
    select_students_query = "SELECT STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, STREAM, CONTACT, EMAIL, DATE_REGISTERED FROM students"
    cursor.execute(select_students_query)
    students = cursor.fetchall()
    return students


###### DRIVER CODE #####
# ##### ALL STUDENTS #### 
# def main():
#     db = create_connection()
#     students = fetch_all_students(db)
#     if "receiver_name" not in st.session_state:
#         st.session_state.receiver_name = []

#     st.session_state.students = students

#     st.write(students)
#     t1, t2, t3 = st.tabs(['Watsup', 'Email', 'Text'])
#     with t2:
#         with st.expander('Share form', expanded=True):
#             email_list = [student[7] for student in students]
#             email_to_name = {student[7]: student[1] for student in students}

#             receiver_name = st.multiselect("Select Recipient", email_list, help="Choose one or more recipients")
#             st.session_state.receiver_name = receiver_name

#             if receiver_name:
#                 email_count = len(receiver_name)
#                 st.text(f"No of Recipients: {email_count}")
#                 for email in receiver_name:
#                     name = email_to_name[email]
#                     form_url = f"http://10.32.147.131:8502/?name={urllib.parse.quote(name)}"
#                     st.write(f"{name} _ {email}")
#                 submit_email = st.button("Share")
#                 if submit_email:
#                     for email in receiver_name:
#                         name = email_to_name[email]
#                         form_url = f"http://10.32.147.131:8502/?name={urllib.parse.quote(name)}"
#                         subject = "Please Fill Out the Form"
#                         body = f"Dear {name},\n\nPlease fill out the form using the following link:\n{form_url}\n\nThank you!"
#                         send_email_with_attachments(subject, body, email, attachments=[])
#                     st.success(f"Shared to: {email_count} recipients!")
#                     # Clear session state
#                     st.session_state.receiver_name = []
#             else:
#                 st.warning('Please add at least one email')

#     with t3:
#         st.write("Email Logs")
#         email_logs = load_email_logs()
#         if email_logs:
#             df = pd.DataFrame(email_logs)
#             st.dataframe(df)
#         else:
#             st.info("No email logs available.")

# if __name__ == "__main__":
#     main()



#### APPOINTMENT EMAILS ######
def main():
    # db = create_connection()
    # appointment = st.session_state.get("appointment", None)
    # if appointment:
    #     appointment_id = appointment[0]
    #     student_id = appointment[1]
    #     student_name = appointment[2]
    #     clinician = appointment[5]
    # else:
    #     st.error("No appointment selected.")
    #     return  

    # students = fetch_all_students(db)
    # student_email = next((student[7] for student in students if student[0] == student_id), None)


    student_email = 'kabpol14@gmail.com'
    student_name ='Paul'
    t1, t2, t3 = st.tabs(['Watsup', 'Email', 'Text'])

    with t2:
        with st.expander('Share form', expanded=True):
            if student_email:
                name = student_name
                email = student_email
                form_url = f"http://10.32.147.131:8502/?name={urllib.parse.quote(name)}"
                st.write(f"**Recipient:** {name} - {email}")

                with st.form("email_form"):
                    submit_email = st.form_submit_button("Share")
                    if submit_email:
                        subject = "Please Fill Out the Form"
                        body = f"Dear {name},\n\nPlease fill out the form using the following link:\n{form_url}\n\nThank you!"
                        send_email_with_attachments(subject, body, email, attachments=[])
                        st.success(f"Shared to: {email}!")
            else:
                st.warning("Student email not found")

    with t3:
        st.write("📬 **Email Logs**")
        email_logs = load_email_logs()
        if email_logs:
            df = pd.DataFrame(email_logs)
            st.dataframe(df)
        else:
            st.info("No email logs available.")

if __name__ == "__main__":
    main()


