import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime
import base64
import os
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import json
import PyPDF2
import io
import docx
from PIL import Image
import pytesseract
import fitz 
import docx2txt
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
from docx2pdf import convert
import tools, follow_ups
import appointments, forms, requested_tools, captured_responses, results_filled
import os
import email_alerts
import submissions
import share_tools
import assessments


config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': 3306,  
    'database':'mhpss_db'
}


### FORMATING TEXTS
def format_text(label, value, value_style='', label_font_size='18px', value_font_size='14px'):
    label_style = f'color: steelblue; font-weight: bold; font-size: {label_font_size};'
    st.markdown(f"<p style='{label_style}'>{label}</p>", unsafe_allow_html=True)
    value_style = f'color: white; {value_style}; font-size: {value_font_size};'
    st.markdown(f"<p style='{value_style}'>{value}</p>", unsafe_allow_html=True)


def format_text_same_line(label, value, label_style='', value_style=''):
    label_style = f'color: #AA4A44; font-size: 18px; {label_style}'
    value_style = f'color: white; font-size: 18px; {value_style}'
    st.markdown(f"<span style='{label_style}'>{label} </span><span style='{value_style}'>{value}</span>", unsafe_allow_html=True)



### CREATING AND SAVING PDF FILES
def save_as_pdf(biodata, results):
    custom_page_size = (400, 500)
    pdf_filename = "student_record.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=custom_page_size)
    styles = getSampleStyleSheet()
    style_heading = styles["Heading3"]
    style_body = styles["BodyText"]
    content = []
    content.append(Paragraph("Biodata", style_heading))
    for key, value in biodata.items():
        content.append(Paragraph(f"<font color='black'>{key}: </font><font color='blue'>{value}</font>", style_body))
    content.append(Spacer(1, 5)) 
    content.append(HRFlowable(width="100%", color="black", thickness=1, lineCap='round', spaceBefore=10, spaceAfter=10, dash=[2, 2]))
    content.append(Paragraph("Results", style_heading))
    for key, value in results.items():
        content.append(Paragraph(f"<font color='black'>{key}: </font><font color='blue'>{value}</font>", style_body))
    doc.build(content)
    return pdf_filename

def get_download_link(file_content, file_name):
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    href = f"<a href='data:application/octet-stream;base64,{encoded_content}' download='{file_name}'>Download {file_name} _summary </a>"
    return href


def create_connection():
    db = mysql.connector.connect(**config)
    return db

def create_database(db):
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS school_db")
    cursor.close()

### REGISTERING STUDENTS #################################
def create_consults_table(db):
    cursor = db.cursor()
    create_students_table_query = """
    CREATE TABLE IF NOT EXISTS students (
    STUDENT_ID  VARCHAR(20) PRIMARY KEY,
    STUDENT_NAME VARCHAR(255) NOT NULL,
    AGE INT,
    GENDER VARCHAR(20), 
    CLASS VARCHAR(255),
    DATE_REGISTERED TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    cursor.execute(create_students_table_query)
    db.commit()
 


def fetch_all_students(db):
    cursor = db.cursor()
    cursor.execute("USE MHPSS_db")
    select_students_query = "SELECT STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, DATE_REGISTERED FROM students"
    cursor.execute(select_students_query)
    students = cursor.fetchall()
    return students

def fetch_student_by_name(db, student_name):
    cursor = db.cursor()
    select_student_query = "SELECT STUDENT_ID, STUDENT_NAME, AGE, GENDER, CLASS, DATE_REGISTERED FROM students WHERE STUDENT_NAME = %s"
    cursor.execute(select_student_query, (student_name,))
    student = cursor.fetchone()
    return student


######## ANALYTICS #######
def convert_pdf_to_images(pdf_content):
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
    images = []
    for page_number in range(pdf_document.page_count):
        pdf_page = pdf_document[page_number]
        image = pdf_page.get_pixmap()
        images.append(Image.frombytes("RGB", [image.width, image.height], image.samples))
    return images


##### Assessement tools ####################
assessment_tools = ['PHQ-9', 'GAD-7', 'SRQ', 'HTQ', 'BDI']

def create_assessment_tools_table(db):
    cursor = db.cursor()
    create_query = """
    CREATE TABLE IF NOT EXISTS assessment_tools (
        id INT AUTO_INCREMENT PRIMARY KEY,
        appointment_id INT,
        assessment_tool VARCHAR(255)
    )
    """
    cursor.execute(create_query)
    db.commit()
    
def insert_requested_assessment_tool(db, appointment_id, assessment_to_add):
    cursor = db.cursor()
    insert_query = """
    INSERT INTO assessment_tools (appointment_id, assessment_tool)
    VALUES (%s, %s)
    """
    for assessment_tool in assessment_to_add:
        values = (appointment_id, assessment_tool)
        cursor.execute(insert_query, values)
    db.commit()
    st.success("Assessment tools added to the appointment!")


def fetch_requested_assessment_tools_df(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT id, appointment_id, assessment_tool 
    FROM assessment_tools
    WHERE appointment_id = %s
    """
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    columns = ["Test ID", "Appointment ID", "Assessment Tool"]
    assessment_tools_df = pd.DataFrame(result, columns=columns)
    return assessment_tools_df


####### 
def main():
    db = create_connection()
    if "appointment_id" in st.session_state:
        appointment_id = st.session_state["appointment_id"]

    if "appointment" in st.session_state:
        appointment = st.session_state.appointment
    share_tools.main()
    assessments.main()
    db.close()

if __name__ == "__main__":
    main()



