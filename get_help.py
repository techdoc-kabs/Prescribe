import streamlit as st
import json
import pandas as pd
import os
import mysql.connector
import importlib
from datetime import datetime
from streamlit_card import card

def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'mhpss_db'
    }
    return mysql.connector.connect(**config)



def set_background(image_path, width="500px", height="500px", border_color="orange", border_width="5px"):
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
            border: {border_width}{border_color};
            margin: 300;
            border-radius : 100%;
            position: fixed;
            top: 5;
        }}
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="image-container"></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading background image: {e}")






def main():
    db = create_connection()
    if "student_id" in st.session_state:
        student_id = st.session_state.student_id
    if 'username' in st.session_state:
        username = st.session_state.username
    if 'student_name' in st.session_state:
        student_name = st.session_state.student_name
    
    if "appointment_id" in st.session_state:
        appointment_id = st.session_state.appointment_id
        
        if appointment_id:
            st.warning('I NEED ELP')


           
    db.close()

if __name__ == "__main__":
    main()
