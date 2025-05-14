import pandas as pd
import streamlit as st
import pandas as pd
# import mysql.connector
import streamlit as st
import seaborn as sns
import random
import sqlite3
interventions = {
    "Intervention Type": [
        "Cognitive Behavioral Therapy (CBT)",
        "Dialectical Behavior Therapy (DBT)",
        "Psychodynamic Psychotherapy",
        "Supportive Psychotherapy",
        "Family Therapy",
        "Group Therapy",
        "Interpersonal Therapy (IPT)",
        "Mindfulness-Based Stress Reduction (MBSR)",
        "Psychopharmacological Treatment",
        "Crisis Intervention",
        "Motivational Interviewing",
        "Trauma-Focused Cognitive Behavioral Therapy (TF-CBT)",
        "Social Skills Training",
        "Cognitive Remediation Therapy",
        "Psychoeducation",
        "Behavioral Activation",
        "Music Therapy",
        "Art Therapy",
        "Animal-Assisted Therapy",
        "Guided Imagery",
        "Relaxation Training",
        "Occupational Therapy",
        "Case Management",
        "Support Groups",
        "Cognitive Behavioral Therapy for Insomnia (CBT-I)",
        "Alcohol Dependence Therapy",
        "Trauma Therapy for Children",
        "Trauma Therapy for Adults",
        "Grief Therapy",
        "Mindfulness-Based Addiction Recovery (MBAR)",
        "Motivational Enhancement Therapy (MET)"
    ],
    "Description": [
        "A goal-oriented therapy focusing on changing patterns of thinking or behavior.",
        "A form of CBT focused on emotional regulation and interpersonal effectiveness.",
        "A therapy emphasizing unconscious processes and past experiences.",
        "A supportive and empathetic therapy aiming to help patients deal with stress.",
        "Therapy involving the patient’s family in the treatment process.",
        "Therapy that involves a group of people with similar issues, led by a therapist.",
        "Therapy focused on improving interpersonal relationships and social functioning.",
        "Therapy incorporating mindfulness practices to reduce stress and increase well-being.",
        "Medications to treat psychiatric disorders.",
        "Short-term intervention aimed at providing immediate help during crises.",
        "A collaborative approach to help patients resolve ambivalence and increase motivation.",
        "A structured therapy for patients who have experienced trauma.",
        "Therapy to improve social interactions and reduce social anxiety.",
        "A therapy aimed at improving cognitive function, especially in patients with schizophrenia.",
        "Providing education to patients and their families about mental health conditions.",
        "A therapeutic activity to increase engagement and reduce depression.",
        "Therapy using music as a medium for self-expression and emotional processing.",
        "Therapy that uses art as a medium for self-exploration and emotional healing.",
        "Therapy involving animals as part of the therapeutic process.",
        "A relaxation technique that involves visualizing peaceful imagery.",
        "Therapy aimed at reducing stress and promoting relaxation.",
        "Therapy aimed at improving functional and vocational skills.",
        "Coordinating care and services for patients with complex needs.",
        "Group-based emotional support for individuals facing similar challenges.",
        "A specialized CBT approach to help individuals overcome sleep-related issues.",
        "Therapy aimed at helping individuals overcome alcohol dependence through various interventions.",
        "Therapy focused on children who have experienced trauma, incorporating child-friendly interventions.",
        "Trauma therapy for adults, focusing on recovery and emotional healing from traumatic experiences.",
        "Therapy aimed at helping individuals process and cope with grief and loss.",
        "A mindfulness-based program designed to aid in addiction recovery and prevent relapse.",
        "Therapy designed to enhance motivation in individuals undergoing treatment for addiction."
    ]
}

df_interventions = pd.DataFrame(interventions, columns=["Intervention Type",'Description'])
interventions_list = df_interventions["Intervention Type"].tolist()

def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables access by column name
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

import sqlite3
import pandas as pd
import streamlit as st
import random

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
    
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def check_duplicate_intervention(db, appointment_id, intervention):
    cursor = db.cursor()
    query = """
    SELECT COUNT(*) FROM interventions
    WHERE appointment_id = ? AND intervention = ?
    """
    cursor.execute(query, (appointment_id, intervention))
    result = cursor.fetchone()
    return result[0] > 0

def create_interventions_table(db):
    cursor = db.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS interventions (
        intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id TEXT,
        intervention TEXT,
        intervention_details TEXT,
        clinician TEXT, 
        clinician_cadre TEXT,
        intervention_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
    )
    """
    try:
        cursor.execute(query)
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        st.error(f"Error creating intervention table: {e}")

def insert_intervention(db, appointment_id, new_intervention, intervention_details, clinician, clinician_cadre):
    if check_duplicate_intervention(db, appointment_id, new_intervention):
        st.warning(f"Intervention '{new_intervention}' already exists for this appointment.")
        return

    query = """
    INSERT INTO interventions (appointment_id, intervention, intervention_details, clinician, clinician_cadre)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        db.execute(query, (appointment_id, new_intervention, intervention_details, clinician, clinician_cadre))
        db.commit()
        st.success(f"Intervention '{new_intervention}' added for appointment ID {appointment_id}.")
    except sqlite3.Error as e:
        db.rollback()
        st.error(f"Error inserting intervention: {e}")

def fetch_interventions_df(db, appointment_id):
    query = """
    SELECT intervention_id, appointment_id, intervention, intervention_details, clinician, clinician_cadre, intervention_date 
    FROM interventions WHERE appointment_id = ?
    """
    cursor = db.cursor()
    cursor.execute(query, (appointment_id,))
    result = cursor.fetchall()
    if result:
        df = pd.DataFrame(result, columns=['Intervention ID', 'Appointment ID', 'Intervention', 'Details', 'Clinician', 'Cadre', 'Date'])
    else:
        df = pd.DataFrame(columns=['Intervention ID', 'Appointment ID', 'Intervention', 'Details', 'Clinician', 'Cadre', 'Date'])
    return df

def remove_intervention(db, appointment_id, intervention_to_remove):
    query = """
    DELETE FROM interventions 
    WHERE appointment_id = ? AND intervention = ?
    """
    try:
        db.execute(query, (appointment_id, intervention_to_remove))
        db.commit()
        st.success(f"Intervention '{intervention_to_remove}' removed from appointment ID {appointment_id}.")
    except sqlite3.Error as e:
        db.rollback()
        st.error(f"Error removing intervention: {e}")

def highlight_headers(df):
    return df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]}
    ])

def random_color():
    return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'

def fetch_interventions_by_appointment(db, appointment_id):
    cursor = db.cursor()
    query = "SELECT intervention_id, intervention FROM interventions WHERE appointment_id = ?"
    cursor.execute(query, (appointment_id,))
    return cursor.fetchall()

def fetch_intervention_details(db, intervention_id):
    cursor = db.cursor()
    query = "SELECT * FROM interventions WHERE intervention_id = ?"
    cursor.execute(query, (intervention_id,))
    return cursor.fetchone()

def update_intervention(db, intervention_id, new_name, new_date, new_details):
    query = """
    UPDATE interventions
    SET intervention = ?, intervention_date = ?, intervention_details = ?
    WHERE intervention_id = ?
    """
    try:
        db.execute(query, (new_name, new_date, new_details, intervention_id))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        st.error(f"Error updating intervention: {e}")


def edit_intervention_form(db):
    with st.form('edit_intervention'):
        intervention = st.session_state.selected_intervention
        st.write("Raw Intervention Data:", intervention)
        try:
            intervention_date = pd.to_datetime(intervention[2]).date()
        except Exception as e:
            st.error(f"Error parsing date: {e}")
            intervention_date = None 
        new_name = st.text_input('Intervention Name', intervention[1])
        new_date = st.date_input("Intervention Date", value=intervention_date if intervention_date else pd.Timestamp.today().date())
        new_details = st.text_area("Details", intervention[3] if intervention[3] else "")
        update = st.form_submit_button("Update Intervention")
        if update:
            update_intervention(db, intervention[0], new_name, new_date, new_details)
            st.success("Intervention updated successfully!")

def search_and_edit_intervention(db, appointment_id):
    interventions = fetch_interventions_by_appointment(db, appointment_id)
    
    if interventions:
        intervention_options = {f"{i[1]} (ID: {i[0]})": i[0] for i in interventions}
        selected = st.selectbox("Select an intervention to edit:", list(intervention_options.keys()))

        if selected:
            intervention_id = intervention_options[selected]
            st.session_state.selected_intervention = fetch_intervention_details(db, intervention_id)

    if 'selected_intervention' in st.session_state:
        edit_intervention_form(db)
    else:
        st.error("No interventions found for this appointment.")



### DRIVER CODE #########
def main():
    db = create_connection()
    create_interventions_table(db)
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
    if 'student_name' in st.session_state:
        student_name = st.session_state.student_name
    if 'clinician_name' in st.session_state:
        clinician_name = st.session_state.clinician_name
        intervention_df = fetch_interventions_df(db, appointment_id)
        col1, col2 = st.columns(2)
        with col1:
            with st.expander(f':blue[ADD INTERVENTION TO] :orange', expanded=True):
                selected_intervention = st.selectbox(":Select Interventions", interventions_list)
        if selected_intervention:
            with st.expander(f':orange[{selected_intervention}]', expanded=True):
                c1, c2 = st.columns(2)
                clinician = c1.multiselect('Clinician', ['Dr.Paul', 'Dr.Cissy', 'Dr.Dorothy', 'Dr.Josephine'])
                clinician_cadre = c2.multiselect('Select Cadre', ['PCO', 'Psychologist', 'Psychiatrist'])
                details = st.text_area(f":green[Session notes on - ] :blue[{selected_intervention}]",
                                       placeholder=f'Type details of {selected_intervention}, each on a new line')

                if st.button("Save Interventions"):
                    if not selected_intervention:
                        st.warning("Please select at least one intervention.")
                    else:
                        clinician = " & ".join(clinician) if clinician else ""
                        clinician_cadre = " & ".join(clinician_cadre) if clinician_cadre else ""
                        details_list = details.split('\n')
                        colored_details = [
                            f'<span style="color:{random_color()}; border: 1px solid gray; border-radius: 10px; padding: 3px 7px; margin-right: 5px; display: inline-block;">{i+1}. {detail.strip()}</span>'
                            for i, detail in enumerate(details_list) if detail.strip()
                        ]
                        formatted_details = " ".join(colored_details)
                        insert_intervention(db, appointment_id, selected_intervention, formatted_details, clinician, clinician_cadre)
            if not intervention_df.empty:
                all_interventions = set(intervention_df["Intervention"])
                all_details = set(intervention_df["Details"])
                palette = sns.color_palette("Set3", len(all_interventions) + len(all_details))
                color_map = {
                    item: f'background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)}); color: black; border-radius: 5px; padding: 3px;'
                    for item, (r, g, b) in zip(all_interventions.union(all_details), palette)}

                def apply_styles(row):
                    intervention_html = f'<span style="{color_map.get(row["Intervention"], "")}">{row["Intervention"]}</span>'
                    details_html = row["Details"]
                    
                    return pd.Series([intervention_html, details_html, row["Clinician"], row["Cadre"], row["Date"]])
                styled_df = intervention_df.apply(apply_styles, axis=1)
                styled_df.index = styled_df.index + 1
                styled_df.columns = ["INTERVENTION TYPE", "DETAILS OF INTERVENTION", "Clinician", "Cadre", "Date"]
                styled_df = styled_df.drop(["Clinician", "Cadre", "Date"], axis=1)
                styled_df = highlight_headers(styled_df)
                st.markdown(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.warning('No Inteventions')

        with col2.form("intervention_to_remove"):
            intervention_to_remove = st.selectbox("Select intervention to remove", intervention_df['Intervention'].explode().unique())
            remove = st.form_submit_button("Remove Intervention")
            if remove:
                if intervention_to_remove:
                    remove_intervention(db, appointment_id, intervention_to_remove)
                else:
                    st.warning("Please select an intervention to remove.")

    db.close()

if __name__ == "__main__":
    main()
