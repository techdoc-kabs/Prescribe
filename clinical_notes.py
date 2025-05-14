import streamlit as st
from datetime import datetime
import sqlite3
import json
import streamlit as st
from typing import Dict
import pandas as pd
# import datetime


presenting_complaints = ['',
    "Feeling sad", "Loss of interest", "Feeling guilty", "Thoughts of self-harm",
    "Excessive worry", "Restlessness", "Panic attacks", "Hearing voices",
    "Seeing things that aren’t there", "Trouble thinking clearly", "Avoiding people",
    "Mood swings", "Feeling irritable", "Acting impulsively", "Forgetfulness",
    "Trouble concentrating", "Not sleeping well", "Being too active or too tired",
    "Shortness of breath", "Coughing", "Wheezing", "Tightness in chest",
    "Trouble breathing", "Coughing up blood", "Lots of mucus", "Pain when breathing",
    "Chest pain", "Heart racing", "Swelling in legs", "Feeling faint", "Dizziness",
    "Feeling weak", "High blood pressure", "Breathlessness with activity",
    "Bluish lips", "Fast or irregular heartbeat", "Stomach pain", "Nausea",
    "Vomiting", "Diarrhea", "Bloating", "Blood in stool", "Heartburn",
    "Unexplained weight loss", "No appetite", "Trouble swallowing",
    "Yellow skin or eyes", "Change in bowel habits", "Bleeding from the bottom",
    "Indigestion", "Joint pain", "Muscle aches", "Stiff joints", "Swollen joints",
    "Back pain", "Bone pain", "Muscle cramps", "Trouble moving", "Weight changes",
    "Thirsty all the time", "Frequent urination", "Sweating a lot",
    "Feeling too hot or cold", "Losing hair", "Dry skin", "Irregular periods",
    "Feeling very tired", "Trouble sleeping", "Trembling", "Changes in mood",
    "Pain when urinating", "Blood in urine", "Peeing a lot", "Peeing less than usual",
    "Swollen feet", "Dark or smelly pee", "Losing control of pee",
    "Pain in the lower back", "Cloudy pee", "Stomach pain", "Bruising easily",
    "Feeling tired", "Pale skin", "Getting sick often", "Swollen lymph nodes",
    "Blood clots", "Shortness of breath when active", "Feeling dizzy",
    "Symptoms of low blood", "Rash or irritation on skin", "Itching",
    "Dry or flaky skin", "Lumps on skin", "Changes in skin color", "Sweating too much",
    "Losing hair", "Changes in nails", "Scarring", "Blisters", "Blurred vision",
    "Eye pain", "Red eyes", "Sensitivity to light", "Double vision",
    "Losing side vision", "Discharge from eyes", "Sudden vision loss", 
    "Dry or irritated eyes", "Seeing double", "Hearing loss", "Ringing in ears",
    "Ear pain", "Stuffy nose", "Sore throat", "Hoarseness", "Trouble swallowing",
    "Sinus pain", "Nosebleeds", "Feeling dizzy or off-balance", "Swollen neck glands"
]

presenting_complaints_df = pd.DataFrame(presenting_complaints, columns=["Presenting Complaints"])
complaints_list = presenting_complaints_df['Presenting Complaints'].tolist()
import json
import sqlite3
from typing import List, Dict

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables dict-like row access
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def create_clinical_notes_table(db):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS clinical_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id TEXT,
        assessment_date TEXT,
        assessment_time TEXT,
        presenting_complaints TEXT,
        summary_notes TEXT,
        past_psych_history TEXT,
        recent_medical_conditions TEXT,
        chronic_medical_conditions TEXT,
        drug_history TEXT,
        family_history TEXT,
        psychological_factors TEXT, 
        case_summary TEXT,
        clinician_name TEXT
    );
    """
    cursor = db.cursor()
    cursor.execute(create_table_sql)
    db.commit()

# def insert_clinical_note(db, appointment_id, clinical_note: Dict, clinician_name):
#     cursor = db.cursor()
#     check_sql = "SELECT COUNT(*) FROM clinical_notes WHERE appointment_id = ?"
#     cursor.execute(check_sql, (appointment_id,))
#     existing_count = cursor.fetchone()[0]
#     if existing_count > 0:
#         return 

#     sql = """
#     INSERT INTO clinical_notes (
#         appointment_id,
#         assessment_date,
#         assessment_time,
#         presenting_complaints,
#         summary_notes,
#         past_psych_history,
#         recent_medical_conditions,
#         chronic_medical_conditions,
#         drug_history,
#         family_history,
#         psychological_factors,
#         case_summary,
#         clinician_name
#     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """
#     cursor.execute(sql, (
#         appointment_id,
#         clinical_note.get('assessment_date'),
#         clinical_note.get('assessment_time'),
#         ', '.join(clinical_note.get('presenting_complaints', [])),
#         clinical_note.get('summary_notes'),
#         clinical_note.get('past_psych_history'),
#         ', '.join(clinical_note.get('recent_medical_conditions', [])),
#         ', '.join(clinical_note.get('chronic_medical_conditions', [])),
#         ', '.join(clinical_note.get('drug_history', [])),
#         ', '.join(clinical_note.get('family_history', [])),
#         json.dumps(clinical_note.get('psychological_factors', {})),
#         clinical_note.get('case_summary'),
#         clinician_name
#     ))
#     db.commit()
#     return {"success": True, "message": "Clinical note successfully saved!", "note_id": cursor.lastrowid}
def insert_clinical_note(db, appointment_id, clinical_note: Dict, clinician_name):
    cursor = db.cursor()
    check_sql = "SELECT COUNT(*) FROM clinical_notes WHERE appointment_id = ?"
    cursor.execute(check_sql, (appointment_id,))
    existing_count = cursor.fetchone()[0]
    if existing_count > 0:
        return {"success": False, "message": f"Clinical notes already exist for appointment {appointment_id}"}

    # Convert assessment_time to a string (HH:MM:SS)
    assessment_time_str = clinical_note.get('assessment_time').strftime('%H:%M:%S')

    sql = """
    INSERT INTO clinical_notes (
        appointment_id,
        assessment_date,
        assessment_time,
        presenting_complaints,
        summary_notes,
        past_psych_history,
        recent_medical_conditions,
        chronic_medical_conditions,
        drug_history,
        family_history,
        psychological_factors,
        case_summary,
        clinician_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(sql, (
        appointment_id,
        clinical_note.get('assessment_date'),
        assessment_time_str,  # Use the formatted time string
        ', '.join(clinical_note.get('presenting_complaints', [])),
        clinical_note.get('summary_notes'),
        clinical_note.get('past_psych_history'),
        ', '.join(clinical_note.get('recent_medical_conditions', [])),
        ', '.join(clinical_note.get('chronic_medical_conditions', [])),
        ', '.join(clinical_note.get('drug_history', [])),
        ', '.join(clinical_note.get('family_history', [])),
        json.dumps(clinical_note.get('psychological_factors', {})),
        clinical_note.get('case_summary'),
        clinician_name
    ))
    db.commit()
    return {"success": True, "message": "Clinical note successfully saved!", "note_id": cursor.lastrowid}

def fetch_appointment_by_id(db, appointment_id):
    cursor = db.cursor()
    select_appointment_query = """
    SELECT a.appointment_id, a.student_id, a.student_name, a.appointment_type, a.appointment_date, 
           CAST(a.appointment_time AS TEXT) AS appointment_time, a.clinician_name, a.reason
    FROM appointments a
    WHERE a.appointment_id = ?;
    """
    cursor.execute(select_appointment_query, (appointment_id,))
    appointment = cursor.fetchone()
    return appointment

def fetch_clinical_notes(db, appointment_id):
    try:
        cursor = db.cursor()
        query = """
        SELECT appointment_id, assessment_date, assessment_time, presenting_complaints, summary_notes, 
               past_psych_history, recent_medical_conditions, chronic_medical_conditions, 
               drug_history, family_history, psychological_factors, case_summary, clinician_name
        FROM clinical_notes WHERE appointment_id = ?
        """
        cursor.execute(query, (appointment_id,))
        row = cursor.fetchone()

        if row:
            result = dict(row)
            if isinstance(result.get("psychological_factors"), str):
                try:
                    result["psychological_factors"] = json.loads(result["psychological_factors"])
                except json.JSONDecodeError:
                    result["psychological_factors"] = {}
            return result
        return None
    except Exception as e:
        print(f"Error fetching clinical notes: {e}")
        return None

def display_clinical_notes(clinical_note):
    presenting_complaints = clinical_note.get('presenting_complaints', "")
    if isinstance(presenting_complaints, str):
        presenting_complaints_list = [complaint.strip() for complaint in presenting_complaints.split(",")]
    else:
        presenting_complaints_list = presenting_complaints if isinstance(presenting_complaints, list) else []

    summary_notes = clinical_note.get('summary_notes', "")
    past_psych_history = clinical_note.get('past_psych_history', "")
    recent_medical_condition = clinical_note.get('recent_medical_conditions', [])
    chronic_medical_condition = clinical_note.get('chronic_medical_conditions', [])
    drug_history = clinical_note.get('drug_history', [])
    family_history = clinical_note.get('family_history', [])
    case_summary = clinical_note.get('case_summary', "")
    psychological_factors = clinical_note.get('psychological_factors', {})

    def format_list(items):
        """Formats the list items to appear on new lines with additional breaks."""
        return "<br>".join(items) if isinstance(items, list) else str(items)

    def format_psych_factors(factors):
        """Formats psychological factors properly."""
        return "<br>".join([f"{factor}: {', '.join(examples)}" for factor, examples in factors.items()]) if factors else "N/A"

    st.markdown("""
        <style>
            .preview-container {
                background-color: #EAEAEA;
                border: 2px solid #B0B0B0;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            .custom-text {
                font-family: 'Times New Roman', serif;
                font-size: 18px;
                color: #333;
                padding-left: 40px;
            }
            .custom-label {
                font-family: 'Times New Roman', serif;
                font-size: 18px;
                font-weight: bold;
                color: #0056b3;
                font-style: italic;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="preview-container">
            <p class="custom-label">📌 CLINICAL ASSESSMENT PREVIEW</p>
            <p class="custom-label">📝 Presenting Complaints:</p>
            <p class="custom-text">{format_list(presenting_complaints_list) if presenting_complaints_list else "N/A"}</p>
            <p class="custom-label">📄 History of Presenting Complaints:</p>
            <p class="custom-text">{summary_notes if summary_notes else "N/A"}</p>
            <p class="custom-label">🧠 Past Psychiatric History:</p>
            <p class="custom-text">{past_psych_history if past_psych_history else "N/A"}</p>
            <p class="custom-label">🏥 Medical Conditions:</p>
            <p class="custom-text"><b>🛗 Recent illness:</b> {format_list(recent_medical_condition) if recent_medical_condition else "N/A"}</p>
            <p class="custom-text"><b>🛗 Chronic illness:</b> {format_list(chronic_medical_condition) if chronic_medical_condition else "N/A"}</p>
            <p class="custom-label">💊 Drug History:</p>
            <p class="custom-text">{format_list(drug_history) if drug_history else "N/A"}</p>
            <p class="custom-label">👨‍👩‍👧‍👦 Family History of Mental Illness:</p>
            <p class="custom-text">{format_list(family_history) if family_history else "N/A"}</p>
            <p class="custom-label">🎋🧬 Psychological Factors:</p>
            <p class="custom-text">{format_psych_factors(psychological_factors)}</p>
            <p class="custom-label">📝 Case summary:</p>
            <p class="custom-text">{case_summary if case_summary else "N/A"}</p>
        </div>
    """, unsafe_allow_html=True)

### DRIVER CODE #######
def main():
    db = create_connection()
    create_clinical_notes_table(db)
    if "appointment_id" in st.session_state:
        appointment_id = st.session_state['appointment_id']

    if "student_id" in st.session_state:
        student_id = st.session_state['student_id']

    if "student_name" in st.session_state:
        student_name = st.session_state['student_name']

    if "clinician_name" in st.session_state:
        clinician_name = st.session_state['clinician_name']   
                                            
        with st.expander("CLINICAL ASSESSMENT FORM", expanded=True):
            col1, col2 = st.columns(2)
            assessment_date = datetime.today().date()
            assessment_time = datetime.now().time()

            selected_complaints = st.multiselect("Select Presenting Complaints", complaints_list)
            presenting_complaints_list = []
            if selected_complaints:
                st.write("Specify Duration for Each Complaint:")
                for i, complaint in enumerate(selected_complaints):
                    c1, c2 = st.columns([2, 1])
                    duration = c1.number_input(f"Duration for {complaint}", min_value=1, step=1, key=f"duration_{i}")
                    duration_unit = c2.selectbox(f"Unit for {complaint}", ["Days", "Weeks", "Months", "Years"], key=f"unit_{i}")
                    presenting_complaints_list.append(f"{i+1}. {complaint} for {duration} {duration_unit.lower()}")
            summary_notes = st.text_area("History of Presenting Complaints", placeholder="Enter patient notes...", height=20)
            past_psych_history = st.text_area('Past psychiatric history', placeholder='Type any significant psychiatric history')
            recent_medical_condition = st.multiselect('Medical conditions', ['Unknown', 'Heart disease', 'HIV/AIDs', 'Peptic Ulcer disease'], placeholder='Any recently diagnosed medical illness')
            chronic_medical_condition = st.multiselect('Chronic Medical condition', ['Unknown', 'Heart disease', 'HIV/AIDs', 'Peptic Ulcer disease'], placeholder='Any pre-existing long-term medical condition')
            drug_history = st.multiselect('Drug history', ['unknown', 'Panadol', 'Aspirin', 'Diazepam'], placeholder='Ongoing drug treatment or recently taken drugs')
            family_history = st.multiselect('Any mental illness in the family', ['unknown', 'Depression', 'Psychosis', 'Anxiety', 'PTSD'])
            psychological_factors = {}
            factors = st.multiselect('Psychology Factors', ['Precipitating factor(s)', 'Perpetuating factor(s)', 'Predisposing factor(s)', 'Protecting factor(s)'])
            for factor in factors:
                examples = st.text_input(f'Note down examples for {factor} (comma-separated)', key=factor)
                if examples:
                    psychological_factors[factor] = [example.strip() for example in examples.split(',')]

            case_summary = st.text_area('Case summary/Formulation', placeholder='Important highlights from the case')
            st.markdown("""
                <style>
                    .preview-container {
                        background-color: #EAEAEA; /* Soft gray */
                        border: 2px solid #B0B0B0; /* Subtle gray border */
                        padding: 10px;
                        border-radius: 10px;
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                        margin-bottom: 15px;
                    }
                    .custom-text {
                        font-family: 'Times New Roman', serif;
                        font-size: 18px;
                        color: #333; /* Darker gray for better readability */
                        padding-left: 40px; /* Indentation */
                        text-indent: 0; /* Remove any default text indentation */
                    }
                    .custom-label {
                        font-family: 'Times New Roman', serif;
                        font-size: 18px;
                        font-weight: bold;
                        color: #0056b3; /* Dark blue for distinction */
                        font-style: italic;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="preview-container">
                    <p class="custom-label">📌 CLINICAL ASSESSMENT PREVIEW</p>
                    <p class="custom-label">📝 Presenting Complaints:</p>
                    <p class="custom-text">{"<br>".join(presenting_complaints_list) if presenting_complaints_list else ""}</p>
                    <p class="custom-label">📄 History of Presenting Complaints:</p>
                    <p class="custom-text">{summary_notes if summary_notes else ""}</p>
                    <p class="custom-label">🧠 Past Psychiatric History:</p>
                    <p class="custom-text">{past_psych_history if past_psych_history else ""}</p>
                    <p class="custom-label">🏥 Medical Conditions:</p>
                    <p class="custom-text"><b>🛗 Recent illness:</b> {", ".join(recent_medical_condition) if recent_medical_condition else ""}</p>
                    <p class="custom-text"><b>🛗 Chronic illness:</b> {", ".join(chronic_medical_condition) if chronic_medical_condition else ""}</p>
                    <p class="custom-label">💊 Drug History:</p>
                    <p class="custom-text">{", ".join(drug_history) if drug_history else ""}</p>
                    <p class="custom-label">👨‍👩‍👧‍👦 Family History of Mental Illness:</p>
                    <p class="custom-text">{", ".join(family_history) if family_history else ""}</p>
                    <p class="custom-label">🎋🧬 Psychological Factors:</p>
                    <p class="custom-text">{", ".join([f"{factor}: {', '.join(examples)}" for factor, examples in psychological_factors.items()]) if psychological_factors else ""}</p>
                    <p class="custom-label">📝 Case summary:</p>
                    <p class="custom-text">{case_summary if case_summary else ""}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Submit Clinical Data"):
                clinical_note = {
                    'assessment_date': assessment_date,
                    'assessment_time': assessment_time,  # Pass as datetime object for conversion
                    'presenting_complaints': presenting_complaints_list,
                    'summary_notes': summary_notes,
                    'past_psych_history': past_psych_history,
                    'recent_medical_conditions': recent_medical_condition,
                    'chronic_medical_conditions': chronic_medical_condition,
                    'drug_history': drug_history,
                    'family_history': family_history,
                    'psychological_factors': psychological_factors,
                    'case_summary': case_summary
                }
               
                response = insert_clinical_note(db, appointment_id, clinical_note, clinician_name)
                if response['success']:
                    st.success(response['message'])
                else:
                    st.error(response['message'])
                    st.info('You cannot submit more than one form for the same Appointment ID. Please edit the existing notes.')

            # if st.button("Submit Clinical Data"):
            #     clinical_note = {
            #         'assessment_date': assessment_date,
            #         'assessment_time': assessment_time,
            #         'presenting_complaints': presenting_complaints_list,
            #         'summary_notes': summary_notes,
            #         'past_psych_history': past_psych_history,
            #         'recent_medical_conditions': recent_medical_condition,
            #         'chronic_medical_conditions': chronic_medical_condition,
            #         'drug_history': drug_history,
            #         'family_history': family_history,
            #         'psychological_factors': psychological_factors,
            #         'case_summary': case_summary
            #     }
               
            #     inserted_id = insert_clinical_note(db, appointment_id, clinical_note, clinician_name)
            #     if inserted_id:
            #         st.success("Clinical data submitted successfully!")
            #     else:
            #         st.error(f"{appointment_id} already has submitted form")
            #         st.info('Appoitment ID cannot have mone than 1 form, You instead edit the existing notes')


        if st.checkbox('Fetch Notes'):
            clinical_note = fetch_clinical_notes(db, appointment_id)
            if clinical_note:
                display_clinical_notes(clinical_note)
            else:
                st.warning("No clinical notes found for this appointment.")



    db.close()

if __name__ == "__main__":
    main()
