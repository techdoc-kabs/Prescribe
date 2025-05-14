import streamlit as st
# import mysql.connector
import json
import sqlite3
import json
import streamlit as st

# SQLite connection
def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row  # Enables dict-like access to rows
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None


# Generate formatted markdown from responses
def generate_responses_markdown(answered_questions):
    response_values = {
        "Not at all": 0,
        "Several Days": 1,
        "More Than Half the Days": 2,
        "Nearly Every Day": 3
    }
    if not isinstance(answered_questions, list):
        st.error("Invalid data format for responses.")
        return ""

    formatted_responses = "\n".join(
        f"<span style='color:white'>{i + 1}. \"{gad7_questions[i]}\"</span>\n"
        f"<span style='color:#AA4A44'>{entry['response']} ({response_values.get(entry['response'], 'N/A')})</span>\n"
        for i, entry in enumerate(answered_questions)
    )
    return formatted_responses


# Fetch captured responses from gad_7forms
def fetch_captured_responses(db, appointment_id):
    cursor = db.cursor()
    query = "SELECT responses FROM GAD_7forms WHERE appointment_id = ?"
    cursor.execute(query, (appointment_id,))
    row = cursor.fetchone()
    cursor.close()

    if row and row["responses"]:
        try:
            return json.loads(row["responses"])
        except json.JSONDecodeError:
            st.error("Error decoding the responses.")
            return []

    return []

gad7_questions = [
    "Feeling nervous, anxious, or on edge?",
    "Not being able to stop or control worrying?",
    "Worrying too much about different things?",
    "Trouble relaxing?",
    "Being so restless that it is hard to sit still?",
    "Becoming easily annoyed or irritable?",
    "Feeling afraid as if something awful might happen?"
]


##### DRIVER #############
def main():
    db = create_connection()
    if 'appointment_id' in st.session_state:
        appointment_id = st.session_state.appointment_id
        responses = fetch_captured_responses(db, appointment_id)
        if responses:
            with st.expander('GAD-7 RESPONSES', expanded=True):
                formatted_responses = generate_responses_markdown(responses)
                st.markdown(formatted_responses, unsafe_allow_html=True)
        else:
            st.warning("GAD-7 responses not yet filled.")
    db.close()

if __name__ == "__main__":
    main()
