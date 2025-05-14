import pandas as pd
# import mysql.connector
import streamlit as st
import seaborn as sns
import sqlite3

disorders = [
    "Anxiety Disorder", 
    "Generalized Anxiety Disorder (GAD)", 
    "Panic Disorder", 
    "Social Anxiety Disorder", 
    "Specific Phobias", 
    "Obsessive-Compulsive Disorder (OCD)", 
    "Post-Traumatic Stress Disorder (PTSD)", 
    "Separation Anxiety Disorder", 
    "Agoraphobia", 
    "Mood Disorder", 
    "Major Depressive Disorder (MDD)", 
    "Bipolar Disorder", 
    "Cyclothymic Disorder", 
    "Dysthymia (Persistent Depressive Disorder)", 
    "Premenstrual Dysphoric Disorder", 
    "Schizophrenia and Other Psychotic Disorders", 
    "Schizophrenia", 
    "Delusional Disorder", 
    "Brief Psychotic Disorder", 
    "Schizoaffective Disorder", 
    "Substance-Related and Addictive Disorders", 
    "Alcohol Use Disorder", 
    "Drug Use Disorder", 
    "Gambling Disorder", 
    "Eating Disorder", 
    "Anorexia Nervosa", 
    "Bulimia Nervosa", 
    "Binge Eating Disorder", 
    "Rumination Disorder", 
    "Pica", 
    "Body Dysmorphic Disorder", 
    "Personality Disorder", 
    "Borderline Personality Disorder", 
    "Antisocial Personality Disorder", 
    "Narcissistic Personality Disorder", 
    "Avoidant Personality Disorder", 
    "Dependent Personality Disorder", 
    "Obsessive-Compulsive Personality Disorder", 
    "Histrionic Personality Disorder", 
    "Paranoid Personality Disorder", 
    "Schizoid Personality Disorder", 
    "Somatic Symptom and Related Disorders", 
    "Somatic Symptom Disorder", 
    "Illness Anxiety Disorder", 
    "Conversion Disorder", 
    "Factitious Disorder", 
    "Dissociative Disorders", 
    "Dissociative Identity Disorder", 
    "Dissociative Amnesia", 
    "Depersonalization-Derealization Disorder", 
    "Neurodevelopmental Disorders", 
    "Autism Spectrum Disorder", 
    "Attention-Deficit/Hyperactivity Disorder (ADHD)", 
    "Specific Learning Disorder", 
    "Intellectual Disability", 
    "Communication Disorders", 
    "Motor Disorders", 
    "Tic Disorders", 
    "Developmental Coordination Disorder", 
    "Stereotypic Movement Disorder", 
    "Sleep-Wake Disorders", 
    "Insomnia Disorder", 
    "Hypersomnolence Disorder", 
    "Narcolepsy", 
    "Parasomnias", 
    "Restless Legs Syndrome", 
    "Circadian Rhythm Sleep-Wake Disorders", 
    "Gender Dysphoria", 
    "Obsessive-Compulsive and Related Disorders", 
    "Hoarding Disorder", 
    "Excoriation (Skin-Picking) Disorder", 
    "Trichotillomania (Hair-Pulling) Disorder", 
    "Reactive Attachment Disorder", 
    "Disinhibited Social Engagement Disorder", 
    "Elimination Disorders", 
    "Enuresis", 
    "Encopresis", 
    "Psychotic Spectrum Disorder", 
    "Delirium", 
    "Neurocognitive Disorders", 
    "Alzheimer's Disease", 
    "Vascular Neurocognitive Disorder", 
    "Frontotemporal Neurocognitive Disorder", 
    "Parkinson's Disease", 
    "Huntington's Disease", 
    "Traumatic Brain Injury", 
    "Dementia", 
    "Amnestic Disorder", 
    "Cognitive Disorders Due to Medical Conditions", 
    "Adjustment Disorders", 
    "Acute Stress Disorder", 
    "Reactive Attachment Disorder", 
    "Conversion Disorder"
]

df_disorders = pd.DataFrame(disorders, columns=["Psychological and Psychiatric Disorders"])
disorders_list = df_disorders["Psychological and Psychiatric Disorders"].tolist()

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None
def fetch_appointments(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("APP-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type, clinician_name
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
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type, clinician_name
        FROM appointments
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))
    results = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    return results

def check_duplicate_diagnosis(db, appointment_id, diagnosis):
    cursor = db.cursor()
    query = "SELECT diagnosis FROM diagnoses WHERE appointment_id = ?"
    cursor.execute(query, (appointment_id,))
    result = cursor.fetchone()
    cursor.close()
    if result and result[0]:
        diagnosis_list = result[0].split(", ")
        return diagnosis in diagnosis_list
    return False

def create_diagnoses_table(db):
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS diagnoses (
        diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id TEXT,
        diagnosis TEXT,
        clinician TEXT,
        clinician_cadre TEXT,
        diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
    );
    """
    try:
        cursor.execute(create_table_query)
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        st.error(f"Error creating diagnosis table: {e}")
    finally:
        cursor.close()

def insert_diagnosis(db, appointment_id, new_diagnosis, clinician, clinician_cadre):
    if check_duplicate_diagnosis(db, appointment_id, new_diagnosis):
        st.warning(f"Diagnosis '{new_diagnosis}' already exists for this appointment.")
        return
    cursor = db.cursor()
    select_query = "SELECT diagnosis FROM diagnoses WHERE appointment_id = ?"
    cursor.execute(select_query, (appointment_id,))
    existing_diagnosis = cursor.fetchone()
    if existing_diagnosis and existing_diagnosis[0]:
        diagnosis_list = existing_diagnosis[0].split(", ")
        updated_diagnosis = ", ".join(diagnosis_list + [new_diagnosis])
        update_query = "UPDATE diagnoses SET diagnosis = ? WHERE appointment_id = ?"
        cursor.execute(update_query, (updated_diagnosis, appointment_id))
    else:
        insert_query = """
        INSERT INTO diagnoses (appointment_id, diagnosis, clinician, clinician_cadre)
        VALUES (?, ?, ?, ?);
        """
        cursor.execute(insert_query, (appointment_id, new_diagnosis, clinician, clinician_cadre))
    db.commit()
    st.success(f"Diagnosis '{new_diagnosis}' added for appointment ID {appointment_id}.")
    cursor.close()

def fetch_diagnoses_df(db, appointment_id):
    cursor = db.cursor()
    fetch_query = """
    SELECT diagnosis_id, appointment_id, diagnosis, clinician, clinician_cadre, diagnosis_date 
    FROM diagnoses WHERE appointment_id = ?
    """
    cursor.execute(fetch_query, (appointment_id,))
    result = cursor.fetchall()
    cursor.close()

    if result:
        diagnosis_df = pd.DataFrame(result, columns=['Diagnosis ID', 'Appointment ID', 'Diagnosis', 'Clinician', 'Cadre', 'Date'])
        diagnosis_df['Diagnosis'] = diagnosis_df['Diagnosis'].apply(lambda x: x.split(", ") if x else [])
    else:
        diagnosis_df = pd.DataFrame(columns=['Diagnosis ID', 'Appointment ID', 'Diagnosis', 'Clinician', 'Cadre', 'Date'])
    return diagnosis_df

def remove_diagnosis(db, appointment_id, diagnosis_to_remove):
    cursor = db.cursor()
    query = "SELECT diagnosis FROM diagnoses WHERE appointment_id = ?"
    cursor.execute(query, (appointment_id,))
    existing_diagnosis = cursor.fetchone()

    if existing_diagnosis and existing_diagnosis[0]:
        diagnosis_list = existing_diagnosis[0].split(", ")
        if diagnosis_to_remove in diagnosis_list:
            diagnosis_list.remove(diagnosis_to_remove)
            updated_diagnosis = ", ".join(diagnosis_list)
            if updated_diagnosis:
                update_query = "UPDATE diagnoses SET diagnosis = ? WHERE appointment_id = ?"
                cursor.execute(update_query, (updated_diagnosis, appointment_id))
            else:
                delete_query = "DELETE FROM diagnoses WHERE appointment_id = ?"
                cursor.execute(delete_query, (appointment_id,))
            db.commit()
            st.success(f"Diagnosis '{diagnosis_to_remove}' removed from appointment ID {appointment_id}.")
        else:
            st.warning(f"Diagnosis '{diagnosis_to_remove}' not found in the record.")
    else:
        st.warning(f"No diagnoses found for appointment ID {appointment_id}.")
    cursor.close()

def search_and_add_diagnoses(db, appointment_id):
    selected_diagnoses = st.multiselect("Choose diagnoses", disorders_list)
    clinician_cadre = st.selectbox('Cadre', ['PCO','Psychologist','Psychiatrist'])
    clinician = st.session_state.clinician_name
    if st.button("Add Selected Diagnoses"):
        for diagnosis in selected_diagnoses:
            insert_diagnosis(db, appointment_id, diagnosis, clinician, clinician_cadre)


def main():
    db = create_connection()
    create_diagnoses_table(db)
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
    if 'student_name' in st.session_state:
        student_name = st.session_state.student_name
    
        diagnosis_df = fetch_diagnoses_df(db, appointment_id)
        diagnosis_df.index = diagnosis_df.index + 1
        # diagnosis_df.drop([['Diagnosis ID']])
        st.write(diagnosis_df)
        col1, col2 = st.columns(2)
        with col1:
            with st.expander(f':blue[ADD DIAGNOSIS TO] :orange[{student_name}]', expanded=True):
                search_and_add_diagnoses(db, appointment_id)
                diagnosis_df = fetch_diagnoses_df(db, appointment_id)
        
        with st.expander(f":blue[Added Dx to] :orange[{student_name}]", expanded=True):           
            all_diagnoses = set(diagnosis for sublist in diagnosis_df["Diagnosis"] for diagnosis in sublist)
            palette = sns.color_palette("Set3", len(all_diagnoses))
            color_map = {diagnosis: f'background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)}); color: black; border-radius: 10px; padding: 5px;'
                         for diagnosis, (r, g, b) in zip(all_diagnoses, palette)}
            def format_diagnosis(diagnoses):
                return " ".join([f'<span style="{color_map.get(diag, "")}">{diag}</span>' for diag in diagnoses])
            styled_html = diagnosis_df["Diagnosis"].apply(format_diagnosis)
            st.markdown("<br>".join(styled_html.to_list()), unsafe_allow_html=True)

        with col2.form("diagnosis_to_remove"):
            diagnosis_to_remove = st.selectbox("Select diagnosis to remove", diagnosis_df['Diagnosis'].explode().unique())
            remove = st.form_submit_button("Remove Diagnosis")
            if remove:
                if diagnosis_to_remove:
                    remove_diagnosis(db, appointment_id, diagnosis_to_remove)
                else:
                    st.warning("Please select a diagnosis to remove.")
    db.close()
if __name__ == "__main__":
    main()
