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
def create_connection():
    try:
        config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': 3306,
            'database': 'mhpss_db'
        }
        return mysql.connector.connect(**config)
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None




def send_email(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    to_emails = [email.strip() for email in to.split(',')]
    msg['to'] = ", ".join(to_emails) 
    
    user = st.secrets['U']
    msg['from'] = user
    password = st.secrets['SECRET']
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"Error sending email: {e}")