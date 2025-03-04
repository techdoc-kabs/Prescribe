import streamlit as st
import pandas as pd
from datetime import datetime
import random
import seaborn as sns
import sqlite3
import re, os


st.set_page_config(
    page_title='Prescriptions',
    page_icon='📋',
    layout='wide',
    initial_sidebar_state='expanded'
)

data = {
    'Drug': ['', 'Aspirin', 'Lisinopril', 'Metformin', 'Atorvastatin', 'Ibuprofen', 'Amoxicillin', 'Ciprofloxacin', 'Omeprazole', 'Simvastatin', 'Levothyroxine',
             'Losartan', 'Gabapentin', 'Amlodipine', 'Warfarin', 'Metoprolol', 'Albuterol', 'Pantoprazole', 'Prednisone', 'Hydrochlorothiazide', 'Tramadol'],
    'Formulation': ['', 'Tablet', 'Tablet', 'Tablet', 'Tablet', 'Tablet', 'Capsule', 'Tablet', 'Capsule', 'Tablet', 'Tablet',
                    'Tablet', 'Capsule', 'Tablet', 'Tablet', 'Tablet', 'Inhaler', 'Tablet', 'Tablet', 'Tablet', 'Tablet'],
    'Drug Strength': ['', '500mg', '10mg', '500mg', '20mg', '200mg', '250mg', '500mg', '20mg', '10mg', '100mcg',
                      '50mg', '300mg', '5mg', '2mg', '5mg', '90mcg', '40mg', '20mg', '5mg', '25mg'],
    'Units': ['', 'mg', 'mg', 'mg', 'mg', 'mg', 'mg', 'mg', 'mg', 'mg', 'mcg',
              'mg', 'mg', 'mg', 'mg', 'mg', 'mcg', 'mg', 'mg', 'mg', 'mg'],
    'Dosing (mg/kg)': ['', '0.5-2', 0.5, 10, 2, 10, 20, 15, 0.5, 0.2, 50,
                              1, 10, 0.2, 0.2, 2, 0.8, 0.2, 0.5, 1, 5],
    'Frequency': ['', 'bd', 'bd', 'tds', 'od', 'bd', 'tds', 'od', 'bd', 'tds', 'od',
                  'od', 'bd', 'tds', 'od', 'bd', 'tds', 'prn', 'bd', 'tds', 'q4h'],
    'Major Toxicity': ['', 'Gastrointestinal bleeding', 'Hypotension', 'Lactic acidosis', 'Myopathy', 'Gastrointestinal bleeding', 'Allergic reactions', 'Tendon rupture', 'Osteoporosis-related fractures', 'Myopathy', 'Cardiac arrhythmias',
                       'Hypotension', 'Dizziness', 'Peripheral edema', 'Bleeding', 'Bradycardia', 'Tachycardia', 'Clostridium difficile infection', 'Immunosuppression', 'Electrolyte imbalance', 'Respiratory depression'],
    'Pregnancy Category': ['', 'C', 'D', 'B', 'X', 'C', 'B', 'C', 'C', 'X', 'A',
                           'D', 'C', 'C', 'X', 'C', 'C', 'B', 'B', 'C', 'D']
}

df = pd.DataFrame(data)
def calculate_max_dose(row):
    dose_per_dose = row['Dosing (mg/kg)']
    if pd.notna(dose_per_dose):
        if isinstance(dose_per_dose, str) and '-' in dose_per_dose:
            start, end = map(float, dose_per_dose.split('-'))
            max_dose = max(start, end)
        elif isinstance(dose_per_dose, (float, int)):
            max_dose = dose_per_dose
        if row['Frequency'] == 'od':
            return max_dose
        elif row['Frequency'] == 'bd':
            return max_dose * 2
        elif row['Frequency'] == 'tds':
            return max_dose * 3
        elif row['Frequency'] == 'q4h':
            return max_dose * 6
    return None

def format_drug_info(df):
    drug_list = [f"{row['Formulation']} {row['Drug']} {row['Drug Strength']}" for _, row in df.iterrows()]
    return drug_list

def get_frequency_options():
    frequency_mapping = {
        "Once daily": 1,
        "Twice daily": 2,
        "Thrice a day": 3,
        "4 times daily": 4,
        "2 hourly": 12,
        "4 hourly": 6,
        "6 hourly": 4,
        "12 hourly": 2,
        "24 hourly": 1,
        "Weekly": 1,
        "Every 2 weeks": 1,
        "Every 3 weeks": 1,
        "Monthly": 1,
        "Annually": 1
    }
    return list(frequency_mapping.keys())

drug_format = [f"{row['Formulation']} {row['Drug']} {row['Drug Strength']}" for _, row in df.iterrows()]
drug_format_df= pd.DataFrame(drug_format, columns=['Formated Drug'])
df2 = pd.concat([df, drug_format_df], axis=1)

def extract_numeric_part(s):
    match = re.search(r'(\d+(\.\d+)?)', s)
    return float(match.group(1)) if match else None

def calculate_prescription_dose(drug_strength, frequency):
    try:
        numeric_part = extract_numeric_part(drug_strength)
        if numeric_part is None:
            raise ValueError("Invalid drug strength format")

        frequency_mapping = {'':0,
            "Once daily": 1,
            "Twice daily": 2,
            "Thrice a day": 3,
            "4 times daily": 4,
            "2 hourly": 12,
            "4 hourly": 6,
            "6 hourly": 4,
            "12 hourly": 2,
            "24 hourly": 1,
            "Weekly": 1,
            "Every 2 weeks": 1,
            "Every 3 weeks": 1,
            "Monthly": 1,
            "Annually": 1
        }

        if frequency in frequency_mapping:
            return numeric_part 
        else:
            raise ValueError("Invalid frequency")
    except ValueError as e:
        return f"Error: {e}"

def extract_strength_formualtion(drug_strength):
    strength_value = extract_numeric_part(drug_strength)
    return strength_value

def cal_quant_per_day(frequency, dose_at_a_time, strength_per_formulation):
    dose_value = extract_numeric_part(dose_at_a_time)
    if dose_value is None:
        st.error('Invalid drug_strength')
    total_daily_dose = frequency * dose_value
    quant_per_day = total_daily_dose / strength_per_formulation
    return quant_per_day


def cal_dose_per_day(frequency, dose_at_a_time):
    dose_value = extract_numeric_part(dose_at_a_time)
    if dose_value is None:
        raise ValueError("Invalid drug strength format")
    return frequency * dose_value


def highlight_headers(df):
    return df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]}])

def random_color():
    return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'


def create_connection():
    db_path = "kabs.db" 
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn

def create_prescriptions_table():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id TEXT,
            prescription TEXT,
            prescriber_instructions TEXT,
            dose_freq_per_day TEXT,
            daily_quantity_prescribed TEXT,
            max_dose TEXT,
            max_prescribed_quantity TEXT,
            prescriber TEXT,
            cadre TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as err:
        st.error(f"Error: {err}")


def insert_prescription(appointment_id, prescription, prescriber_instructions, dose_freq_per_day, daily_quantity_prescribed, max_dose, max_prescribed_quantity, prescriber, cadre):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        check_query = """
        SELECT COUNT(*) FROM prescriptions 
        WHERE appointment_id = ? AND prescription = ?
        """
        cursor.execute(check_query, (appointment_id, prescription))
        result = cursor.fetchone()

        if result and result[0] > 0:
            st.error("This medicine has already been prescribed for this appointment. Duplicate entries are not allowed.")
        else:
            insert_query = """
            INSERT INTO prescriptions 
            (appointment_id, prescription, prescriber_instructions, dose_freq_per_day, daily_quantity_prescribed, max_dose, max_prescribed_quantity, prescriber, cadre, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            current_timestamp = datetime.now()
            cursor.execute(insert_query, (
                appointment_id, prescription, prescriber_instructions, dose_freq_per_day, daily_quantity_prescribed, max_dose, 
                max_prescribed_quantity, prescriber, cadre, current_timestamp
            ))
            conn.commit()
            st.success("Prescription inserted successfully.")

        cursor.close()
        conn.close()

    except sqlite3.Error as err:
        st.error(f"Database error: {err}")

def remove_prescription(appointment_id, prescription_to_remove):
    conn = create_connection()
    cursor = conn.cursor()
    check_query = "SELECT prescription FROM prescriptions WHERE appointment_id = ?"
    cursor.execute(check_query, (appointment_id,))
    existing_prescription = cursor.fetchone()
    if existing_prescription and existing_prescription[0]:
        existing_prescription_list = existing_prescription[0].split(", ")
    else:
        st.warning("No prescription found for this appointment.")
    cursor.close()
    conn.close()


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
    results = cursor.fetchall()
    cursor.close()
    return results


def fetch_prescriptions(db, appointment_id):
    try:
        cursor = db.cursor()
        print(f"Fetching prescriptions for: '{appointment_id}' (Type: {type(appointment_id)})")

        query = """
        SELECT 
            appointment_id, prescription, prescriber_instructions, dose_freq_per_day, daily_quantity_prescribed, 
            max_dose, max_prescribed_quantity, prescriber, cadre
        FROM prescriptions
        WHERE appointment_id = ?
        """
        cursor.execute(query, (str(appointment_id).strip(),))
        result = cursor.fetchall()
        if not result:
            print("No prescriptions found.")  # Debugging
            return pd.DataFrame()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        cursor.close()

        return df

    except Exception as e:
        print(f"Error fetching prescriptions: {e}")
        return pd.DataFrame()



##### DRIVER CODE ###### 
def main():
    db = create_connection()
    create_prescriptions_table()
    st.sidebar.subheader(":blue[APPOINTMENT BIODATA]")
    with st.sidebar.expander("🔍SEARCH", expanded=True):
        search_input = st.text_input("ENTER PATIENT NAME", "", placeholder='eg. Paul')
    results = []
    student_data = fetch_appointments(db, search_input)
    if search_input.strip():
        results = fetch_appointments(db, search_input)
    selected_record = None
    if results:
        st.sidebar.write(f":orange[**{len(results)} result(s) found**]")
        results_dicts = [
            {
                'student_id': r[0],
                'student_name': r[1],
                'appointment_id': r[2],
                'appointment_date': r[3],
                'appointment_type': r[4],
                'clinician_name': r[5]
            } 
            for r in results
        ]
        
        options = {f"{r['student_name']} - {r['appointment_id']}": r for r in results_dicts}
        selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
        selected_record = options[selected_option]
    if selected_record:
        with st.sidebar.expander("📄 APPOINTMENT DETAILS", expanded=True):
            student_id = selected_record['student_id']
            student_name = selected_record['student_name']
            appointment_id = selected_record['appointment_id']
            appointment_date = selected_record['appointment_date']
            appointment_type = selected_record['appointment_type']
            clinician_name = selected_record['clinician_name']
            reason = selected_record.get('reason', 'N/A') 
            st.write(f"Student ID: {student_id}")
            st.write(f"Student Name: {student_name}")
            st.write(f"Appointment ID: {appointment_id}")
            st.write(f"Appointment Type: {appointment_type}")
            st.write(f"Appointment reason: {reason}")
            st.write(f"Clinician: {clinician_name}")
            st.write(f'Appointment Date: {appointment_date}')

        st.session_state["appointment_id"] = selected_record["appointment_id"]
        appointment_id = st.session_state.appointment_id
        st.session_state["student_name"] = selected_record["student_name"]
        student_name = st.session_state.student_name
        st.session_state["student_id"] = selected_record["student_id"]
        st.session_state["appointment_date"] = selected_record["appointment_date"]
        st.session_state["clinician_name"] = selected_record["clinician_name"]
        
       

        if appointment_id:
            prescriptions_df = fetch_prescriptions(db, appointment_id)
            drug_list = format_drug_info(df2)
            frequency_options = ["Once daily", "Twice daily", "Thrice a day", "4 times daily", "2 hourly", 
                                 "4 hourly", "6 hourly", "12 hourly", "24 hourly", "Weekly", "Every 2 weeks", 
                                 "Every 3 weeks", "Monthly", "Annually"]

            with st.expander('PRESCRIPTION FORM', expanded=True):
                col1, col2 = st.columns(2)
                medicine = col1.selectbox("Select Medicine", drug_list)
                frequency = col1.selectbox("Frequency", frequency_options)
                duration = col2.number_input("Treatment Duration", min_value = 0)
                duration_units = col2.selectbox("Duration Units", ["days", "week(s)", "month(s)"])
                prescriber_instrctions = col1.text_area('Instructions', placeholder = 'Write special Instructionsa about a drug')
                prescriber = col2.selectbox("Precriber", ['Dr.Paul','Dr. Cissy','Dr.Ocama'])
                prescriber_cadre = col2.selectbox('Cadre', ['PCO','Psychiatrist','Physician'])
                if duration_units == "week(s)":
                    duration *= 7
                    duration_units = 'day(s)'
                elif duration_units == "month(s)":
                    duration *= 30
                    duration_units = 'day(s)'
                cal_frequency_mapping = {
                    "Once daily": 1, "Twice daily": 2, "Thrice a day": 3, "4 times daily": 4,
                    "2 hourly": 12, "4 hourly": 6, "6 hourly": 4, "12 hourly": 2, "24 hourly": 1,
                    "Weekly": 1, "Every 2 weeks": 1, "Every 3 weeks": 1, "Monthly": 1, "Annually": 1
                }
                cal_frequency = cal_frequency_mapping.get(frequency, None)
                if cal_frequency is None:
                    st.error("Invalid frequency selected.")
                else:
                    quantity_prescribed = cal_frequency * duration
                
                if st.button(':green[Add Prescription]'):
                    selected_row_drug = df2[df2["Formated Drug"] == medicine]
                    formulation = str(selected_row_drug["Formulation"].iloc[0])
                    dose_at_a_time = selected_row_drug['Drug Strength'].iloc[0]

                    prescribed_drug_info = {
                        'Medicine': medicine,
                        'Frequency': frequency,
                        'Duration': duration,
                        'Duration Units': duration_units
                    }

                    prescription = f'{medicine} {frequency} for {duration} {duration_units}.'
                    calculated_dose = calculate_prescription_dose(selected_row_drug['Drug Strength'].iloc[0], frequency)
                    max_dose = calculated_dose * cal_frequency * duration
                    st.write(f"Max Dose/{duration}{duration_units}: {max_dose}{selected_row_drug['Units'].iloc[0]}")
                    max_dose = f'{max_dose}{selected_row_drug["Units"].iloc[0]}'

                    dose_per_day = cal_dose_per_day(cal_frequency, dose_at_a_time)
                    st.write(f"Max dose/day: {dose_per_day} {selected_row_drug['Units'].iloc[0]}")
                    dose_per_day = f'{dose_per_day} {selected_row_drug["Units"].iloc[0]}'

                    strength_per_tablet = extract_strength_formualtion(selected_row_drug['Drug Strength'].iloc[0])
                    quant_per_day = cal_quant_per_day(cal_frequency, dose_at_a_time, strength_per_tablet)
                    dose_freq_per_day = f"{quant_per_day} {formulation} X {cal_frequency}"

                    st.write(f"Total prescribed for the {duration} {duration_units}: {quantity_prescribed} {formulation}(s)")
                    quantity_prescribed = f'{quantity_prescribed} {formulation}(s)'
                    insert_prescription(
                        appointment_id, prescription, prescriber_instrctions, dose_freq_per_day, quant_per_day, max_dose,
                        quantity_prescribed, prescriber, prescriber_cadre
                    )
        
        # if st.checkbox('Delete prescription'):
        #     st.write('---')
        #     if not prescriptions_df.empty:
        #         c1, c2 = st.columns([2.5, 1.5])
        #         with c1.form("prescription_to_remove"):
        #             prescription = st.selectbox("Select prescription to remove", prescriptions_df['prescription'].explode().unique())
        #             remove = st.form_submit_button(":red[Delete prescription]")
        #             if remove:
        #                 remove_prescription(db, appointment_id, prescription)
        #             else:
        #                 st.warning("Please select an prescription to remove.")
        #     else:
        #         st.warning('No added prescriptions')

        if st.checkbox('View Prescriptions'):
            st.write('---')
            st.subheader(f'Prescriptions for {student_name}')
            prescriptions_df.index = prescriptions_df.index + 1
            if not prescriptions_df.empty:
                prescriptions_df = prescriptions_df.drop(['appointment_id'], axis=1)
                all_prescriptions = set(prescriptions_df["prescription"])
                palette = sns.color_palette("Set3", len(all_prescriptions))
                color_map = {
                    item: f'background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)}); color: black; border-radius: 5px; padding: 3px;'
                    for item, (r, g, b) in zip(all_prescriptions, palette)
                }
                def random_text_color():
                    return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
                def apply_styles(row):
                    prescription_html = f'<span style="{color_map.get(row["prescription"], "")}">{row["prescription"]}</span>'
                    def style_text(text):
                        text_color = random_text_color()
                        return f'<span style="border: 2px solid {text_color}; color: {text_color}; border-radius: 50px; padding: 3px 8px;">{text}</span>'

                    return pd.Series([
                        prescription_html, 
                        style_text(row["prescriber_instructions"]), 
                        style_text(row["max_prescribed_quantity"])
                    ], index=["PRESCRIPTION", 'PRESCIRIBER INSTRCTIONS', "PRESCRIBED QUANTITY"])

                styled_df = prescriptions_df.apply(apply_styles, axis=1)
                styled_df.index = styled_df.index + 1 
                styled_df = highlight_headers(styled_df)
                st.markdown(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.warning(f'No prescriptions for {student_name}')

    


    db.close()
if __name__ == "__main__":
	main()

