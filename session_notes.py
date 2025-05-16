import streamlit as st
from datetime import datetime
import sqlite3
import json
import streamlit as st
from typing import Dict
import pandas as pd
import json
import sqlite3
from typing import List, Dict

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row 
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def create_session_notes_table(db):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS session_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id TEXT,
        appointment_date TEXT,
        appointment_time TEXT,
        current_concerns TEXT,
        case_summary TEXT,
        working_diagnosis TEXT,
        intervention TEXT,
        follow_up TEXT,
        refer TEXT,
        remarks TEXT,
        clinician_name TEXT
    );
    """
    cursor = db.cursor()
    cursor.execute(create_table_sql)
    db.commit()



def insert_session_note(db, appointment_id, note_data: Dict, clinician_name):
    cursor = db.cursor()
    check_sql = "SELECT COUNT(*) FROM session_notes WHERE appointment_id = ?"
    cursor.execute(check_sql, (appointment_id,))
    existing_count = cursor.fetchone()[0]
    if existing_count > 0:
        return {"success": False, "message": f"Session notes already exist for appointment {appointment_id}"}

    appointment_time_str = note_data.get('appointment_time').strftime('%H:%M:%S')
    sql = """
    INSERT INTO session_notes (
        appointment_id,
        appointment_date,
        appointment_time,
        current_concerns,
        case_summary,
        working_diagnosis,
        intervention,
        follow_up,
        refer,
        remarks,
        clinician_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """
    cursor.execute(sql, (
        appointment_id,
        note_data.get('appointment_date'),
        appointment_time_str,
        note_data.get('current_concerns'),
        note_data.get('case_summary'),
        note_data.get('working_diagnosis'),
        note_data.get('intervention'),
        note_data.get('follow_up'),
        note_data.get('refer'),
        note_data.get('remarks'),
        clinician_name
    ))
    db.commit()
    return {"success": True, "message": "Session note successfully saved!", "note_id": cursor.lastrowid}

def fetch_session_notes(db, appointment_id):
    cursor = db.cursor()
    query = """
    SELECT * FROM session_notes WHERE appointment_id = ?
    """
    cursor.execute(query, (appointment_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def display_session_notes(note):
    st.markdown("""
        <style>
            .preview-container {
                background-color: #EAEAEA;
                border: 2px solid #B0B0B0;
                padding: 10px 20px;
                border-radius: 20px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            .line {
                margin-bottom: 8px;
            }
            .label {
                font-family: 'Times New Roman', serif;
                font-size: 18px;
                font-weight: bold;
                color: #0056b3;
                font-style: italic;
                display: inline-block;
                width: 180px;
            }
            .text {
                font-family: 'Times New Roman', serif;
                font-size: 18px;
                color: #333;
                font-style: italic;
                display: inline-block;
                vertical-align: top;
                max-width: calc(100% - 200px);
                word-wrap: break-word;
            }
            .header {
                font-family: 'Times New Roman', serif;
                font-size: 20px;
                font-weight: bold;
                color: #222;
                margin-bottom: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    appointment_date = note.get("appointment_date", "N/A")
    appointment_time = note.get("appointment_time", "N/A")
    try:
        formatted_time = datetime.strptime(appointment_time, "%H:%M:%S").strftime("%H:%M")
    except:
        formatted_time = appointment_time 

    st.markdown(f"""
        <div class="preview-container">
            <div class="header">📌 SESSION NOTE PREVIEW</div>
            <div class="line"><span class="label">🕐 Date & Time:</span><span class="text">{appointment_date} at {formatted_time}</span></div>
            <div class="line"><span class="label">🗨️ Current Concerns:</span><span class="text">{note.get('current_concerns')}</span></div>
            <div class="line"><span class="label">🧾 Case Summary:</span><span class="text">{note.get('case_summary')}</span></div>
            <div class="line"><span class="label">🧠 Working Diagnosis:</span><span class="text">{note.get('working_diagnosis')}</span></div>
            <div class="line"><span class="label">🧩 Intervention:</span><span class="text">{note.get('intervention')}</span></div>
            <div class="line"><span class="label">📅 Follow-Up:</span><span class="text">{note.get('follow_up')}</span></div>
            <div class="line"><span class="label">🔁 Referral Plan:</span><span class="text">{note.get('refer')}</span></div>
            <div class="line"><span class="label">📝 Remarks:</span><span class="text">{note.get('remarks')}</span></div>
            <div class="line"><span class="label">👤 Clinician:</span><span class="text">{note.get('clinician_name')}</span></div>
        </div>
    """, unsafe_allow_html=True)



def update_session_note(conn, appointment_id, updated_note):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE session_notes
            SET
                appointment_date = ?,
                appointment_time = ?,
                current_concerns = ?,
                case_summary = ?,
                working_diagnosis = ?,
                intervention = ?,
                follow_up = ?,
                refer = ?,
                remarks = ?,
                clinician_name = ?
            WHERE appointment_id = ?
        ''', (
            updated_note["appointment_date"],
            updated_note["appointment_time"],
            updated_note["current_concerns"],
            updated_note["case_summary"],
            updated_note["working_diagnosis"],
            updated_note["intervention"],
            updated_note["follow_up"],
            updated_note["refer"],
            updated_note["remarks"],
            updated_note["clinician_name"],
            appointment_id
        ))
        conn.commit()
        return {"success": True, "message": "Note updated"}
    except Exception as e:
        return {"success": False, "message": str(e)}

from streamlit_option_menu import option_menu

def display_session_notes(note):
    st.markdown("""
        <style>
            .preview-container {
                background-color: #EAEAEA;
                border: 2px solid #B0B0B0;
                padding: 15px;
                border-radius: 20px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
                max-width: 100%;
            }
            .header {
                font-family: 'Times New Roman', serif;
                font-size: 22px;
                font-weight: bold;
                color: #222;
                margin-bottom: 15px;
                text-align: center;
            }
            .line {
                display: flex;
                flex-wrap: wrap;
                margin-bottom: 10px;
            }
            .label {
                font-family: 'Times New Roman', serif;
                font-size: 16px;
                font-weight: bold;
                color: #0056b3;
                font-style: italic;
                flex: 0 0 180px;
                margin-right: 10px;
            }
            .text {
                font-family: 'Times New Roman', serif;
                font-size: 16px;
                color: #333;
                font-style: italic;
                flex: 1;
                word-break: break-word;
            }

            @media screen and (max-width: 600px) {
                .label {
                    flex: 0 0 100%;
                    margin-bottom: 5px;
                }
                .text {
                    flex: 0 0 100%;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    appointment_date = note.get("appointment_date", "N/A")
    appointment_time = note.get("appointment_time", "N/A")
    try:
        formatted_time = datetime.strptime(appointment_time, "%H:%M:%S").strftime("%H:%M")
    except:
        formatted_time = appointment_time

    st.markdown(f"""
        <div class="preview-container">
            <div class="header">📌 SESSION NOTE PREVIEW</div>
            <div class="line"><span class="label">🕐 Date & Time:</span><span class="text">{appointment_date} at {formatted_time}</span></div>
            <div class="line"><span class="label">🗨️ Current Concerns:</span><span class="text">{note.get('current_concerns')}</span></div>
            <div class="line"><span class="label">🧾 Case Summary:</span><span class="text">{note.get('case_summary')}</span></div>
            <div class="line"><span class="label">🧠 Working Diagnosis:</span><span class="text">{note.get('working_diagnosis')}</span></div>
            <div class="line"><span class="label">🧩 Intervention:</span><span class="text">{note.get('intervention')}</span></div>
            <div class="line"><span class="label">📅 Follow-Up:</span><span class="text">{note.get('follow_up')}</span></div>
            <div class="line"><span class="label">🔁 Referral Plan:</span><span class="text">{note.get('refer')}</span></div>
            <div class="line"><span class="label">📝 Remarks:</span><span class="text">{note.get('remarks')}</span></div>
            <div class="line"><span class="label">👤 Clinician:</span><span class="text">{note.get('clinician_name')}</span></div>
        </div>
    """, unsafe_allow_html=True)

def main():
    db = create_connection()
    create_session_notes_table(db)

    if "appointment_id" in st.session_state:
        appointment_id = st.session_state["appointment_id"]

    if "username" in st.session_state:
        username = st.session_state["username"]

    if "student_name" in st.session_state:
        student_name = st.session_state["student_name"]
    
    col1, col2 = st.columns([1, 3.5])
    with col1:
        notes_menu = option_menu(
            menu_title='',
            orientation='vertical',
            menu_icon='',
            options=['Add', 'Preview', 'Edit'],
            icons=["book", "eye", "pencil-square"],
            styles={
                "container": {"padding": "8!important", "background-color": '#e0f7fa', 'border': '0.01px dotted red'},
                "icon": {"color": "red", "font-size": "12px"},
                "nav-link": {"color": "#000000", "font-size": "12px", "font-weight": 'bold', "text-align": "left", "--hover-color": "#d32f2f"},
                "nav-link-selected": {"background-color": "#1976d2"},
            },
            key="notes_menu"
        )
    if notes_menu == 'Add':
        with col2.expander("➕ SESSION NOTES FORM", expanded=True):
            appointment_date = datetime.today().date()
            appointment_time = datetime.now().time()
            current_concerns = st.text_area("🗨️ Current Concerns", placeholder="What are the main issues raised today?")
            case_summary = st.text_area("🧾 Case Summary", placeholder="Summarize today's session...")
            working_diagnosis = st.multiselect("🧠 Working Diagnosis", ['Depression', 'Anxiety', 'Acute stress reaction', 'PTSD'])
            intervention = st.multiselect("🧩 Intervention", ['Psychoeducation', 'CBT', 'Group session', 'Indiviual counselling'])
            
            follow_up_required = st.radio("📅 :red[SCHEDULE Follow-Up?]", ["No", "Yes"], horizontal=True)
            if follow_up_required == "Yes":
                next_review_date = st.date_input("Next Review Date")
                follow_up_reason = st.multiselect("Follow-Up Reason", ['CBT', 'Group session', 'Individual counselling'])
                follow_up_person = st.multiselect("By who?", ['Ivan', 'Cissy', 'Shana'])
                follow_up = f"Yes | Date: {next_review_date}, Reason: {', '.join(follow_up_reason)}, By: {', '.join(follow_up_person)}"
            else:
                follow_up = "Not required"

            refer_required = st.radio(":red[🔁 REFER CLIENT?]", ["No", "Yes"], horizontal=True)
            if refer_required == "Yes":
                refer_to = st.selectbox("Refer to", ['Dr.Paul', 'Dr.Dorothy', 'Dr.Josephine'])
                refer_reason = st.selectbox("Reason for Referral", ['Psychiatric consult', 'Psychotherapy', 'Follow-up'])
                refer = f"Yes | To: {refer_to}, Reason: {refer_reason}"
            else:
                refer = "Not required"

            remarks = st.text_area("📝 Remarks", placeholder="Any remarks/comments?")
            clinician_name = st.text_input('Therapist', value = username)
            if st.button("Submit Session Note"):
                session_note = {
                    'appointment_date': appointment_date,
                    'appointment_time': appointment_time,
                    'current_concerns': current_concerns,
                    'case_summary': case_summary,
                    'working_diagnosis': ", ".join(working_diagnosis),
                    'intervention': ", ".join(intervention),
                    'follow_up': follow_up,
                    'refer': refer,
                    'remarks': remarks
                }
                response = insert_session_note(db, appointment_id, session_note, clinician_name)
                if response["success"]:
                    st.success(response["message"])
                else:
                    st.error(response["message"])
                    st.info("You cannot submit more than one form for the same Appointment ID. Please edit the existing notes.")

    elif notes_menu == 'Preview':
        session_note = fetch_session_notes(db, appointment_id)
        if session_note:
            with col2:
                display_session_notes(session_note)
        else:
            st.warning("No session notes found for this appointment.")

    elif notes_menu == 'Edit':
        session_note = fetch_session_notes(db, appointment_id)
        if session_note:
            with col2.expander(f"✏️ Edit Session Note: {appointment_id}", expanded=True):
                appointment_date = st.date_input("Appointment Date", value=datetime.strptime(session_note["appointment_date"], "%Y-%m-%d").date())
                appointment_time = st.time_input("Appointment Time", value=datetime.strptime(session_note["appointment_time"], "%H:%M:%S").time())
                current_concerns = st.text_area("Current Concerns", value=session_note["current_concerns"])
                case_summary = st.text_area("Case Summary", value=session_note["case_summary"])
                working_diagnosis = st.text_area("Working Diagnosis", value=session_note["working_diagnosis"])
                intervention = st.text_area("Intervention", value=session_note["intervention"])
                follow_up = st.text_input("Follow-Up", value=session_note["follow_up"])
                refer = st.text_input("Referral Plan", value=session_note["refer"])
                remarks = st.text_area("Remarks", value=session_note["remarks"])

                if st.button("Update Session Note"):
                    updated_note = {
                        "appointment_date": appointment_date,
                        "appointment_time": appointment_time.strftime("%H:%M:%S"),  # ← convert to string
                        "current_concerns": current_concerns,
                        "case_summary": case_summary,
                        "working_diagnosis": working_diagnosis,
                        "intervention": intervention,
                        "follow_up": follow_up,
                        "refer": refer,
                        "remarks": remarks,
                        "clinician_name": username
                    }
                    response = update_session_note(db, appointment_id, updated_note)
                    if response["success"]:
                        st.success("Session note updated successfully!")
                    else:
                        st.error(f"Failed to update session note: {response['message']}")

        else:
            st.warning("No session notes found to edit.")

    db.close()
if __name__ == "__main__":
    main()
