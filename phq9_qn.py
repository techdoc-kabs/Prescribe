# import streamlit as st
# import mysql.connector
# from datetime import datetime
# import json

# def create_connection():
#     config = {
#         'user': 'root',
#         'password': '',
#         'host': 'localhost',
#         'port': 3306,
#         'database': 'mhpss_db'
#     }
#     return mysql.connector.connect(**config)

# phq9_questions = [
#     "Little interest or pleasure in doing things",
#     "Feeling down, depressed, or hopeless",
#     "Trouble falling asleep, staying asleep, or sleeping too much",
#     "Feeling tired or having little energy",
#     "Poor appetite or overeating",
#     "Feeling bad about yourself - or that you’re a failure or have let yourself or your family down",
#     "Trouble concentrating on things, such as reading the newspaper or watching television",
#     "Moving or speaking so slowly that other people could have noticed. Or, the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
#     "Thoughts that you would be better off dead or of hurting yourself in some way"
# ]

# def create_PHQ_9forms_table(db):
#     cursor = db.cursor()
#     create_query = """
#     CREATE TABLE IF NOT EXISTS PHQ_9forms (
#         assessment_date DATETIME,
#         appointment_id VARCHAR(255),
#         student_id VARCHAR(255),
#         student_name VARCHAR(255),
#         phq_score INTEGER,
#         depression_status TEXT,
#         suicide_response INTEGER,
#         suicide_risk TEXT,
#         responses JSON,
#         assessed_by VARCHAR(255),
#         FOREIGN KEY (appointment_id) REFERENCES screen_appointments(appointment_id)
#     )"""
#     cursor.execute(create_query)
#     db.commit()
#     cursor.close()

# def insert_into_PHQ_9forms(db, appointment_id, student_id, student_name, phq_score, depression_status, suicide_response, suicide_risk, responses_dict, assessed_by):
#     try:
#         cursor = db.cursor()
#         insert_query = """
#         INSERT INTO PHQ_9forms (
#             assessment_date, appointment_id, student_id, student_name, 
#             phq_score, depression_status, suicide_response, suicide_risk, responses, assessed_by
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         assessment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         values = (
#             assessment_date, appointment_id, student_id, student_name, 
#             phq_score, depression_status, suicide_response, suicide_risk, 
#             json.dumps(responses_dict), assessed_by
#         )
#         cursor.execute(insert_query, values)
#         db.commit()
#         st.success(f"PHQ-9 response submitted successfully!")
#     except Exception as e:
#         db.rollback()
#         st.error(f"An error occurred: {e}")
#     finally:
#         cursor.close()

# def check_existing_entry(db, appointment_id):
#     try:
#         cursor = db.cursor()
#         query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = %s"
#         cursor.execute(query, (appointment_id,))
#         return cursor.fetchone()[0] > 0
#     except Exception as e:
#         st.error(f"Error checking for duplicates: {e}")
#         return False
#     finally:
#         cursor.close()

# def calculate_phq_score(responses):
#     response_values = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}
#     return sum(response_values.get(response["response"], 0) for response in responses)

# def interpret_pat_score(score):
#     if score >= 20: return "Severe depression"
#     elif score >= 15: return "Moderately severe depression"
#     elif score >= 10: return "Moderate depression"
#     elif score >= 5: return "Mild depression"
#     elif score >= 1: return "Minimal depression"
#     return 'No depression'

# def generate_responses_dict(responses):
#     response_values = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}
#     return [
#         {"question_id": entry["question"], "question": phq9_questions[int(entry["question"][1:]) - 1], 
#          "response": entry["response"], "response_value": response_values.get(entry["response"], 'N/A')}
#         for entry in responses
#     ]



# def capture_PHQ_9_responses():
#     responses = []
#     answered_questions = set()
    
#     with st.form('PHQ-9'):
#         st.write('PATIENT HEALTH QUESTIONNAIRE-9 (PHQ-9 Form)')
#         for i, question in enumerate(phq9_questions, start=1):
#             st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
#             selected_radio = st.radio(
#                 f'Q{i}', 
#                 ["Not Selected", "Not at all", "Several Days", "More Than Half the Days", "Nearly Every Day"], 
#                 index=0, 
#                 key=f"q{i}_{st.session_state.get('appointment_id', 'default')}_{st.session_state.get('unique_session_key', 'default')}"
#             )
#             responses.append({'question': f'Q{i}', 'response': selected_radio})
#             if selected_radio != "Not Selected":
#                 answered_questions.add(i)
        
#         submit_button = st.form_submit_button('Save responses')
#         if submit_button:
#             if len(answered_questions) != len(phq9_questions):
#                 st.warning('Please complete the entire form before submitting.')
#                 return None
#             return responses



# def main():
#     db = create_connection()
#     create_PHQ_9forms_table(db)
#     if 'appointment_id' not in st.session_state or 'student_id' not in st.session_state:
#         st.error("Appointment ID and Student ID are required.")
#         return
#     appointment_id = st.session_state.appointment_id
#     student_id = st.session_state.student_id
#     student_name = st.session_state.get('student_name', 'Unknown')
#     assessed_by = st.session_state.get('clinician_name', 'Unknown')
#     responses = capture_PHQ_9_responses()
#     if responses:
#         if len(responses) != len(phq9_questions):
#             st.warning('Please complete the entire form')
#             return 

#         if check_existing_entry(db, appointment_id):
#             st.warning("An entry for this appointment ID already exists.")
#             return
#         responses_dict = generate_responses_dict(responses)
#         phq_score = calculate_phq_score(responses_dict)
#         depression_status = interpret_pat_score(phq_score)
#         suicide_response = next((r["response"] for r in responses_dict if r["question_id"] == "Q9"), None)
#         suicide_risk_value = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}.get(suicide_response, -1)
#         suicide_risk = ["Low", "Moderate", "High"][min(suicide_risk_value, 2)] if suicide_risk_value >= 0 else "Unknown"
#         insert_into_PHQ_9forms(db, appointment_id, student_id, student_name, phq_score, depression_status, suicide_risk_value, suicide_risk, responses_dict, assessed_by)

#     db.close()

# if __name__ == "__main__":
#     main()



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

phq9_questions = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling asleep, staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself - or that you’re a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed. Or, the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead or of hurting yourself in some way"
]

def create_PHQ_9forms_table(db):
    cursor = db.cursor()
    create_query = """
    CREATE TABLE IF NOT EXISTS PHQ_9forms (
        assessment_date TEXT,
        appointment_id TEXT,
        student_id TEXT,
        student_name TEXT,
        phq_score INTEGER,
        depression_status TEXT,
        suicide_response INTEGER,
        suicide_risk TEXT,
        responses TEXT,
        assessed_by TEXT,
        FOREIGN KEY (appointment_id) REFERENCES screen_appointments(appointment_id)
    )
    """
    cursor.execute(create_query)
    db.commit()
    cursor.close()

def insert_into_PHQ_9forms(db, appointment_id, student_id, student_name, phq_score, depression_status, suicide_response, suicide_risk, responses_dict, assessed_by):
    try:
        cursor = db.cursor()
        insert_query = """
        INSERT INTO PHQ_9forms (
            assessment_date, appointment_id, student_id, student_name, 
            phq_score, depression_status, suicide_response, suicide_risk, responses, assessed_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        assessment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (
            assessment_date, appointment_id, student_id, student_name, 
            phq_score, depression_status, suicide_response, suicide_risk, 
            json.dumps(responses_dict), assessed_by
        )
        cursor.execute(insert_query, values)
        db.commit()
        st.success(f"PHQ-9 response submitted successfully!")
    except Exception as e:
        db.rollback()
        st.error(f"An error occurred: {e}")
    finally:
        cursor.close()

def check_existing_entry(db, appointment_id):
    try:
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = ?"
        cursor.execute(query, (appointment_id,))
        return cursor.fetchone()[0] > 0
    except Exception as e:
        st.error(f"Error checking for duplicates: {e}")
        return False
    finally:
        cursor.close()

def calculate_phq_score(responses):
    response_values = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}
    return sum(response_values.get(response["response"], 0) for response in responses)

def interpret_pat_score(score):
    if score >= 20: return "Severe depression"
    elif score >= 15: return "Moderately severe depression"
    elif score >= 10: return "Moderate depression"
    elif score >= 5: return "Mild depression"
    elif score >= 1: return "Minimal depression"
    return 'No depression'

def generate_responses_dict(responses):
    response_values = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}
    return [
        {"question_id": entry["question"], "question": phq9_questions[int(entry["question"][1:]) - 1], 
         "response": entry["response"], "response_value": response_values.get(entry["response"], 'N/A')}
        for entry in responses
    ]

def capture_PHQ_9_responses():
    responses = []
    answered_questions = set()
    
    with st.form('PHQ-9'):
        st.write('PATIENT HEALTH QUESTIONNAIRE-9 (PHQ-9 Form)')
        for i, question in enumerate(phq9_questions, start=1):
            st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
            selected_radio = st.radio(
                f'Q{i}', 
                ["Not Selected", "Not at all", "Several Days", "More Than Half the Days", "Nearly Every Day"], 
                index=0, 
                key=f"q{i}_{st.session_state.get('appointment_id', 'default')}_{st.session_state.get('unique_session_key', 'default')}"
            )
            responses.append({'question': f'Q{i}', 'response': selected_radio})
            if selected_radio != "Not Selected":
                answered_questions.add(i)
        
        submit_button = st.form_submit_button('Save responses')
        if submit_button:
            if len(answered_questions) != len(phq9_questions):
                st.warning('Please complete the entire form before submitting.')
                return None
            return responses

def main():
    db = create_connection()
    create_PHQ_9forms_table(db)
    if 'appointment_id' not in st.session_state or 'student_id' not in st.session_state:
        st.error("Appointment ID and Student ID are required.")
        return
    appointment_id = st.session_state.appointment_id
    student_id = st.session_state.student_id
    student_name = st.session_state.get('student_name', 'Unknown')
    assessed_by = st.session_state.get('clinician_name', 'Unknown')
    responses = capture_PHQ_9_responses()
    if responses:
        if len(responses) != len(phq9_questions):
            st.warning('Please complete the entire form')
            return 

        if check_existing_entry(db, appointment_id):
            st.warning("An entry for this appointment ID already exists.")
            return
        responses_dict = generate_responses_dict(responses)
        phq_score = calculate_phq_score(responses_dict)
        depression_status = interpret_pat_score(phq_score)
        suicide_response = next((r["response"] for r in responses_dict if r["question_id"] == "Q9"), None)
        suicide_risk_value = {"Not at all": 0, "Several Days": 1, "More Than Half the Days": 2, "Nearly Every Day": 3}.get(suicide_response, -1)
        suicide_risk = ["Low", "Moderate", "High"][min(suicide_risk_value, 2)] if suicide_risk_value >= 0 else "Unknown"
        insert_into_PHQ_9forms(db, appointment_id, student_id, student_name, phq_score, depression_status, suicide_risk_value, suicide_risk, responses_dict, assessed_by)

    db.close()

if __name__ == "__main__":
    main()
