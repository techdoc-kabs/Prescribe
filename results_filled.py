
import streamlit as st
import json
import pandas as pd
import os
# import mysql.connector
# import appointments
import requested_tools
from datetime import datetime
import captured_responses 
import seaborn as sns
import plotly.express as px
import sqlite3


def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables access by column name
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None
def fetch_student_by_id(db, student_id):
    cursor = db.cursor()
    query = """
    SELECT student_id, student_name, age, gender, class, stream, email, contact, 
           strftime('%Y-%m-%d', date_registered) AS date_registered
    FROM students
    WHERE student_id = ?
    """
    cursor.execute(query, (student_id,))
    return cursor.fetchone()


def fetch_student_by_appointment_id(db, appointment_id):
    cursor = db.cursor()
    query = """
    SELECT student_id, student_name, appointment_id, appointment_date
    FROM screen_appointments
    WHERE appointment_id = ?
    """
    cursor.execute(query, (appointment_id,))
    return cursor.fetchone()


def fetch_appointments_for_student(db, student_id):
    cursor = db.cursor()
    query = """
    SELECT appointment_id, student_id, student_name, appointment_type, appointment_date
    FROM screen_appointments 
    WHERE student_id = ?
    """
    cursor.execute(query, (student_id,))
    appointments = cursor.fetchall()
    return appointments


def fetch_requested_tools_students(db, appointment_id):
    cursor = db.cursor()
    query = """
    SELECT tool_name, tool_status 
    FROM requested_tools_students
    WHERE appointment_id = ?
    """
    cursor.execute(query, (appointment_id,))
    result = cursor.fetchall()
    tools_status = {row[0]: row[1] for row in result}
    cursor.close()
    return tools_status


def update_tool_status(db, appointment_id, tool_name, new_status):
    cursor = db.cursor()
    update_query = """
    UPDATE requested_tools_students
    SET tool_status = ?
    WHERE appointment_id = ? AND tool_name = ?
    """
    cursor.execute(update_query, (new_status, appointment_id, tool_name))
    db.commit()


def check_existing_entry(db, appointment_id):
    try:
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = ?"
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()[0]
        return result > 0
    except Exception as e:
        st.error(f"An error occurred while checking for duplicates: {e}")
        return False
    finally:
        cursor.close()


def fetch_appointments_for_student_and_id(db, student_id, appointment_id):
    cursor = db.cursor()
    query = """
    SELECT * 
    FROM screen_appointments
    WHERE student_id = ? AND appointment_id = ?
    """
    cursor.execute(query, (student_id, appointment_id))
    appointments = cursor.fetchall()
    cursor.close()
    return appointments


def fetch_appointments(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("APP-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type, clinician_name
        FROM screen_appointments
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
        FROM screen_appointments
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))

    return cursor.fetchall()


def fetch_students(db, search_input):
    cursor = db.cursor()
    if search_input.strip().upper().startswith("STUD-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, age, gender, class, stream
        FROM students
        WHERE student_id = ?
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
        SELECT student_id, student_name, age, gender, class, stream
        FROM students
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))

    return cursor.fetchall()

def capture_PHQ_9_responses():
    responses = []
    answered_questions = set()

    with st.form('PHQ-9'):
        st.write('PATIENT HEALTH QUESTIONNAIRE-9 (PHQ-9 Form)')
        for i, question in enumerate(questions, start=1):
            st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
            selected_radio = st.radio(f'', ['Select from options below', 'Not at all', 'Several Days', 'More Than Half the Days', 'Nearly Every Day'], key=f"q{i}")
            if selected_radio != 'Select from options below':
                responses.append({'question': f'Q{i}', 'response': selected_radio})
                answered_questions.add(i)
        submit_button = st.form_submit_button('Submit')
        if submit_button:
            if len(answered_questions) != len(questions):
                st.warning('Please complete the entire form')
    return responses

tool_status = ['Pending','Completed']
tools_template_dict = {
    'PHQ-9': capture_PHQ_9_responses,
    'GAD-7' :'capture_GAD-7_responses',
    'BDI' :'capture_BDI_responses'}

tool_respnse_dict = {
    'PHQ-9': 'PHQ-9_responses',
    'GAD-7': 'GAD-7_responses',
    'BDI':'BDI_responses'
}

def fetch_notes_by_student_id(db, appointment_id):
    cursor = db.cursor(dictionary=True)
    query = """
    SELECT *
    FROM notes
    WHERE appointment_id = ?
    ORDER BY created_at DESC;
    """
    cursor.execute(query, (appointment_id,))
    return cursor.fetchall()

def fetch_latest_phq9(db, appointment_id):
    try:
        cursor = db.cursor()
        query = """
        SELECT 
            phq_score, 
            depression_status,
            suicide_response,
            suicide_risk
        FROM PHQ_9forms 
        WHERE appointment_id = ?
        ORDER BY assessment_date DESC
        LIMIT 1
        """
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        
        if result:
            columns = ["PHQ Score", "Depression Status", "Suicide Response", "Suicide Risk"]
            return pd.DataFrame([result], columns=columns)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching PHQ-9: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def fetch_latest_gad7(db, appointment_id):
    try:
        cursor = db.cursor()
        query = """
        SELECT 
            gad_score,
            anxiety_status 
        FROM gad_7forms 
        WHERE appointment_id = ?
        ORDER BY assessment_date DESC
        LIMIT 1
        """
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        
        if result:
            columns = ["GAD-7 Score", "Anxiety Status"]
            return pd.DataFrame([result], columns=columns)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching GAD-7: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()


def style_gad7_dataframe(df):
    anxiety_colors = {
        "Severe anxiety": "red",
        "Moderate anxiety": "orange",
        "Mild anxiety": "yellow",
        "Minimal anxiety": "green"}

    def highlight_anxiety(val):
        return f"background-color: {anxiety_colors.get(val, '')}; color: black" if val in anxiety_colors else ""
    styled_df = df.style.applymap(highlight_anxiety, subset=["Anxiety Status"]) \
                         .set_table_styles([{
                             'selector': 'thead th',
                             'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
                         }]) \
                         .hide(axis="index")  
    return styled_df



def style_phq9_dataframe(df):
    status_colors = {
        "Severe depression": "red",
        "Moderately severe depression": "orange",
        "Moderate depression": "yellow",
        "Mild depression": "blue",
        "Minimal depression": "green",
    }
    
    suicide_risk_colors = {
        "High": "red",
        "Moderate": "yellow",
        "Low": "green"}

    def highlight_status(val):
        return f"background-color: {status_colors.get(val, '')}; color: white" if val in status_colors else ""
    def highlight_suicide_risk(val):
        return f"background-color: {suicide_risk_colors.get(val, '')}; color: white" if val in suicide_risk_colors else ""
    styled_df = df.style.applymap(highlight_status, subset=["Depression Status"]) \
                         .applymap(highlight_suicide_risk, subset=["Suicide Risk"]) \
                         .set_table_styles([{
                             'selector': 'thead th',
                             'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
                         }]) \
                         .hide(axis="index")  # Hide index

    return styled_df

def highlight_headers(df):
    return df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]}
    ])

def style_summary_dataframe(df):
    status_colors = {
        "Severe depression": "red",
        "Moderately severe depression": "orange",
        "Moderate depression": "yellow",
        "Mild depression": "blue",
        "Minimal depression": "green",
    }
    suicide_risk_colors = {
        "High": "red",
        "Moderate": "yellow",
        "Low": "green"
    }
    anxiety_colors = {
        "Severe anxiety": "red",
        "Moderate anxiety": "orange",
        "Mild anxiety": "yellow",
        "Minimal anxiety": "green"
    }
    functioning_colors = {
        "Extremely difficult": "red",
        "Very difficult": "#CB4154",
        "Somewhat difficult": "yellow",
        "Not difficult at all": "green"
    }

    def highlight_status(val):
        color = status_colors.get(val)
        return f"background-color: {color}; color: black;" if color else ""

    def highlight_suicide_risk(val):
        color = suicide_risk_colors.get(val)
        return f"background-color: {color}; color: black;" if color else ""

    def highlight_anxiety(val):
        color = anxiety_colors.get(val)
        return f"background-color: {color}; color: black;" if color else ""

    def highlight_functioning(val):
        color = functioning_colors.get(val)
        return f"background-color: {color}; color: black;" if color else ""

    styled_df = df.style \
        .applymap(highlight_status, subset=["Depression Status"]) \
        .applymap(highlight_suicide_risk, subset=["Suicide Risk"]) \
        .applymap(highlight_anxiety, subset=["Anxiety Status"]) \
        .applymap(highlight_functioning, subset=["Functioning Status"]) \
        .set_table_styles([{
            'selector': 'thead th',
            'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
        }]) \
        .hide(axis="index")

    return styled_df


def fetch_fxn(db, appointment_id):
    try:
        cursor = db.cursor()
        query = """
        SELECT 
            difficulty_level
        FROM functioning_responses 
        WHERE appointment_id = ?
        LIMIT 1
        """
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        if result:
            columns = ["Functioning Status"]
            return pd.DataFrame([result], columns=columns)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching difficulty level: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def generate_summary_dataframe(db, appointment_id):
    try:
        phq9_df = fetch_latest_phq9(db, appointment_id)
        gad7_df = fetch_latest_gad7(db, appointment_id)
        fxn_df = fetch_fxn(db, appointment_id) 
        
        if not phq9_df.empty and not gad7_df.empty:
            summary_data = {
                "PHQ Score": phq9_df["PHQ Score"].values[0],
                "Depression Status": phq9_df["Depression Status"].values[0],
                'Suicide Score': phq9_df['Suicide Response'].values[0],
                "Suicide Risk": phq9_df["Suicide Risk"].values[0],
                "GAD-7 Score": gad7_df["GAD-7 Score"].values[0],
                "Anxiety Status": gad7_df["Anxiety Status"].values[0],
                "Functioning Status": fxn_df["Functioning Status"].values[0]
            }
            summary_df = pd.DataFrame([summary_data])
            return style_summary_dataframe(summary_df)

        elif not phq9_df.empty:
            summary_data = {
                "PHQ Score": phq9_df["PHQ Score"].values[0],
                "Depression Status": phq9_df["Depression Status"].values[0],
                'Suicide Score': phq9_df['Suicide Response'].values[0],
                "Suicide Risk": phq9_df["Suicide Risk"].values[0],
                "Functioning Status": fxn_df['Functioning Status'].values[0],
                "GAD-7 Score": "N/A",
                "Anxiety Status": "N/A"
            }
            summary_df = pd.DataFrame([summary_data])
            return style_summary_dataframe(summary_df)

        elif not gad7_df.empty:
            summary_data = {
                "PHQ Score": "N/A",
                "Depression Status": "N/A",
                'Suicide Score':'N/A',
                "Suicide Risk": "N/A",
                "GAD-7 Score": gad7_df["GAD-7 Score"].values[0],
                "Anxiety Status": gad7_df["Anxiety Status"].values[0],
                "Functioning Status": fxn_df['Functioning Status'].values[0]
            }
            summary_df = pd.DataFrame([summary_data])
            summary_df = summary_df.reset_index(drop=True)
            summary_df.index = summary_df.index + 1
            return style_summary_dataframe(summary_df)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return pd.DataFrame()


def style_functioning_dataframe(df):
    functioning_colors = {
        "Extremely difficult": "red",
        "Very difficult": "#CB4154",
        "Somewhat difficult": "yellow",
        "Not difficult at all": "green"
    }

    def highlight_status(val):
        color = functioning_colors.get(val, "")
        return f'background-color: {color}; color: blacke;' if color else ''

    styled_df = df.style \
        .applymap(highlight_status, subset=['Functioning Status']) \
        .set_table_styles([{
            'selector': 'thead th',
            'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
        }]) \
        .hide(axis='index')

    return styled_df



from streamlit_javascript import st_javascript
def main():
    db = create_connection()
    screen_width = st_javascript("window.innerWidth", key="screen_width_js") or 1024

    is_mobile = screen_width < 700

    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
        if appointment_id:
            requested_tools_students = fetch_requested_tools_students(db, appointment_id)
            tools_list = list(requested_tools_students.keys()) 
            if not tools_list:
                st.warning("No requested tools found.")
                db.close()
                return
            
            with st.expander(f'📅:red[{appointment_id}]', expanded=False):
                tool_tabs = st.tabs(tools_list + ['FUNCTONING', 'SUMMARY RESULTS'])
                summary_data = {}

                for idx, tool in enumerate(tools_list):
                    with tool_tabs[idx]:
                        tool_status = requested_tools_students[tool]
                        if tool not in tools_template_dict:
                            st.warning(f"No template available for {tool}")
                            continue

                        if tool_status != 'Completed':
                            st.warning(f"**{tool}** is **Pending** ⏳")

                        if tool == "PHQ-9" and tool_status == "Completed":
                            phq9_df = fetch_latest_phq9(db, appointment_id)
                            if not phq9_df.empty:
                                st.table(style_phq9_dataframe(phq9_df))
                                summary_data.update(phq9_df.iloc[0].to_dict())
                            else:
                                st.info("No PHQ-9 data available.")

                        elif tool == "GAD-7" and tool_status == "Completed":
                            gad7_df = fetch_latest_gad7(db, appointment_id)
                            if not gad7_df.empty:
                                st.table(style_gad7_dataframe(gad7_df))
                                summary_data.update(gad7_df.iloc[0].to_dict())
                            else:
                                st.info("No GAD-7 data available.")

                # Functioning Tab
                with tool_tabs[-2]:
                    fxn_df = fetch_fxn(db, appointment_id)
                    if not fxn_df.empty:
                        st.table(style_functioning_dataframe(fxn_df))
                    else:
                        st.info("No Functioning data available.")

                # Summary Tab
                with tool_tabs[-1]:
                    if summary_data:
                        summary_df = generate_summary_dataframe(db, appointment_id)
                        st.table(summary_df)
                    else:
                        st.info("No completed assessments available for summary.")   

    db.close()

if __name__ == "__main__":
    main()
