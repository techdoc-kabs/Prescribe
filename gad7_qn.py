import streamlit as st
import sqlite3
from datetime import datetime
import json

def create_connection():
    try:
        conn = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None

gad7_questions = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen"
]

def capture_GAD_7_responses():
    responses = []
    answered_questions = set()
    with st.form('GAD-7'):
        st.write('GENERALIZED ANXIETY DISORDER 7 (GAD-7 Form)')
        for i, question in enumerate(gad7_questions, start=1):
            st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
            selected_radio = st.radio(
                f'Q{i}', 
                ["Not Selected", "Not at all", "Several Days", "More Than Half the Days", "Nearly Every Day"], 
                index=0, 
                key=f"q{i}_{st.session_state.get('appointment_id', 'default')}"
            )
            responses.append({'question': f'Q{i}', 'response': selected_radio})
            if selected_radio != "Not Selected":
                answered_questions.add(i)

        submit_button = st.form_submit_button('Save responses')
        if submit_button:
            if len(answered_questions) != len(gad7_questions):
                st.warning('Please complete the entire form')
                return None
            return responses

def calculate_gad_score(responses):
    response_values = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}
    return sum(response_values.get(response["response"], 0) for response in responses)

def interpret_gad_score(score):
    if score >= 15: return "Severe anxiety"
    elif score >= 10: return "Moderate anxiety"
    elif score >= 5: return "Mild anxiety"
    return "Minimal anxiety"

def generate_responses_dict(responses):
    response_values = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}
    return [
        {
            "question_id": entry["question"],
            "question": gad7_questions[int(entry["question"][1:]) - 1], 
            "response": entry["response"],
            "response_value": response_values.get(entry["response"], 'N/A')
        }
        for entry in responses
    ]

def create_GAD_7forms_table(db):
    cursor = db.cursor()
    create_query = """
    CREATE TABLE IF NOT EXISTS GAD_7forms (
        assessment_date TEXT,
        appointment_id TEXT,
        student_id TEXT,
        student_name TEXT,
        gad_score INTEGER,
        anxiety_status TEXT,
        responses TEXT,
        assessed_by TEXT,
        FOREIGN KEY (appointment_id) REFERENCES screen_appointments(appointment_id)
    );
    """
    cursor.execute(create_query)
    db.commit()
    cursor.close()

def insert_into_GAD_7forms(db, appointment_id, student_id, student_name, gad_score, anxiety_status, responses_dict, assessed_by):
    try:
        cursor = db.cursor()
        insert_query = """
        INSERT INTO GAD_7forms (
            assessment_date, appointment_id, student_id, student_name, 
            gad_score, anxiety_status, responses, assessed_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        assessment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (
            assessment_date, appointment_id, student_id, student_name, 
            gad_score, anxiety_status, json.dumps(responses_dict), assessed_by
        )
        cursor.execute(insert_query, values)
        db.commit()
        st.success(f"GAD-7 response submitted successfully!")
    except Exception as e:
        db.rollback()
        st.error(f"An error occurred: {e}")
    finally:
        cursor.close()

def check_existing_entry(db, appointment_id):
    try:
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM GAD_7forms WHERE appointment_id = ?"
        cursor.execute(query, (appointment_id,))
        return cursor.fetchone()[0] > 0
    except Exception as e:
        st.error(f"Error checking for duplicates: {e}")
        return False
    finally:
        cursor.close()

def main():
    db = create_connection()
    create_GAD_7forms_table(db)

    if 'appointment_id' not in st.session_state or 'student_id' not in st.session_state:
        st.error("Appointment ID and Student ID are required.")
        return

    appointment_id = st.session_state.appointment_id
    student_id = st.session_state.student_id
    student_name = st.session_state.get('student_name', 'Unknown')
    assessed_by = st.session_state.get('clinician_name', 'Unknown')
    responses = capture_GAD_7_responses()
    if responses:
        if len(responses) != len(gad7_questions):
            st.warning('Please complete the entire form')
            return 

        if check_existing_entry(db, appointment_id):
            st.warning("An entry for this appointment ID already exists.")
            return

        responses_dict = generate_responses_dict(responses)
        gad_score = calculate_gad_score(responses_dict)
        anxiety_status = interpret_gad_score(gad_score)
        insert_into_GAD_7forms(db, appointment_id, student_id, student_name, gad_score, anxiety_status, responses_dict, assessed_by)

    db.close()

if __name__ == "__main__":
    main()
